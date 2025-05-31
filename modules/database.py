import sqlite3, os, datetime
import modules.webquests as webquests
from modules.log import Log

class DatabaseHandler:
	instance = None

	def __new__(cls, db_path):
		if cls.instance is None:
			cls.instance = super(DatabaseHandler, cls).__new__(cls)
		return cls.instance

	def __init__(self, db_path):
		if not os.path.exists(db_path):
			print("Creating database...")

		# Connect to db
		self.db = sqlite3.connect(db_path, autocommit=True)
		self.cursor = self.db.cursor()
		self.log = Log()

		# Create accounts table if it doesn't exist
		if not self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accounts';").fetchall():
			print("Creating accounts table...")
			self.cursor.execute(f"CREATE TABLE accounts (id TEXT, name TEXT, type TEXT, access_method TEXT, token TEXT)") #SQL-QUERY

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.log.write_line("Database connections have been ended properly.")
		self.cursor.close(); self.db.close()

	def __enter__(self):
		return self

	# GETTERS
	def get_accounts(self) -> list:
		return [x[0] for x in self.cursor.execute("SELECT id FROM accounts;").fetchall()] #SQL-QUERY

	def get_account_id_from_name(self, account_name: str) -> str | None:
		result = self.cursor.execute(f"SELECT * FROM accounts WHERE name='{account_name}';").fetchall() #SQL-QUERY
		if result: return result[0][0]
		else: return None

	def get_account_info(self, account_id: str) -> list | None:
		result = self.cursor.execute(f"SELECT * FROM accounts WHERE id='{account_id}';").fetchall() #SQL-QUERY
		if result: return result[0]
		else: return None

	def get_account_name(self, account_id: str) -> str | None:
		result = self.cursor.execute(f"SELECT * FROM accounts WHERE id='{account_id}';").fetchall() #SQL-QUERY
		if result: return result[0][1]
		else: return None

	# SETTERS
	def add_account(self, account_name: str, account_type: str, account_id: str = None):
		account_name = account_name.strip(); account_type = account_type.strip().lower()

		if (account_name == ""):
			raise ValueError("Account name cannot be empty!")

		if (account_id is None):
			account_id = account_name.replace(" ", "").lower()
			while (account_id, ) in self.cursor.execute(f"SELECT id FROM accounts;").fetchall(): #SQL-QUERY
				account_id = f"{account_id}-1"
		else: account_id = account_id.strip()

		if (account_type not in ["curseforge", "cf", "modrinth"]):
			raise ValueError("Unknown account type!")

		elif (account_type == "cf"):
			account_type = "curseforge"

		self.cursor.execute(f"INSERT INTO accounts (id, name, type, access_method, token) VALUES ('{account_id}', '{account_name}', '{account_type}', 'none', 'none');") #SQL-QUERY
		self.cursor.execute(f"CREATE TABLE account_{account_id} (datetime TEXT, balance REAL)") #SQL-QUERY
		self.db.commit()
		self.log.write_line(f"Added account '{account_name}' to accounts.")

	def collect_account(self, account_id: str, timestamp_overwrite: str = None) -> float:
		info = self.get_account_info(account_id)
		if info is None:
			raise ValueError(f"Account '{account_id}' doesn't exist, can't collect data.")

		if timestamp_overwrite is not None: timestamp = timestamp_overwrite
		else: timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M")

		self.log.write_line(f"Collecting data for '{account_id}'...")

		balance: float | None = None; tries: int = 3
		if info[3] == "website" and info[2] in ["curseforge", "cf", "modrinth"]:
			while balance is None and tries > 0:
				self.log.write_line(f"Trying to get data... tries left: {tries}")
				tries -= 1
				cookies = webquests.load_cookies_from_file(info[4])
				if info[2] == "cf" or info[2] == "curseforge":
					balance = webquests.get_curseforge_dollar_balance(cookies)
				elif info[2] == "modrinth":
					balance = webquests.get_modrinth_dollar_balance(cookies)
		else:
			raise ValueError("Unknown account type or access method?")

		if balance is not None and isinstance(balance, float):
			self.cursor.execute(f"INSERT INTO account_{account_id} VALUES ('{timestamp}', {balance});") #SQL-QUERY
			self.db.commit()
			self.log.write_line(f"Success! Got balance for '{account_id}'.")
			return balance
		else:
			self.log.write_line(f"Failed to collect account balance for '{account_id}'.")
			raise ValueError("Failed")

	def add_website_cookie(self, account_id: str, path: str):
		self.cursor.execute(
			f"UPDATE accounts SET access_method = 'website', token = '{path}' WHERE id='{account_id}';") #SQL-QUERY
		self.log.write_line(f"Added website cookies to account '{self.get_account_name(account_id)}'.")

	def remove_access_method(self, account_id: str):
		self.cursor.execute(
			f"UPDATE accounts SET access_method = 'none', token = 'none' WHERE id='{account_id}';")  # SQL-QUERY
		self.log.write_line(f"Removed website cookies from account '{self.get_account_name(account_id)}'.")

	def collect_accounts(self):
		timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M")
		for acc_id in self.get_accounts():
			self.collect_account(acc_id, timestamp)

	def export_csv(self, directory: str):
		import csv

		print(f"Getting data for CSV export...")
		accounts = self.cursor.execute("SELECT * FROM accounts;").fetchall() #SQL-QUERY
		accounts = [{"id": x[0], "name": x[1], "type": x[2], "data": list()} for x in accounts]

		# Get data from accounts
		for account in accounts:
			account_data = self.cursor.execute(f"SELECT * FROM account_{account['id']};").fetchall() #SQL-QUERY
			account["data"] = account_data

		# Get timestamps from all added accounts
		all_timestamps = set()
		account_timestamps = dict()
		for account in accounts:
			acnt = []
			for entry in account["data"]:
				all_timestamps.add(entry[0])
				acnt.append(entry[0])
			account_timestamps[account['id']] = acnt
		all_timestamps = list(all_timestamps); all_timestamps.sort()

		# Add balance entries to each timestamp
		header = ["Date and time"] + [f"{x['name']} balance" for x in accounts]
		rows = []
		for time_entry in all_timestamps:
			row = [time_entry]
			for account in accounts:
				if time_entry in account_timestamps[account['id']]:
					row.append(account["data"][account_timestamps[account['id']].index(time_entry)][1])
				else:
					row.append("-")
			rows.append(row)

		print(f"Writing CSV to {directory}...")
		with open(f"{directory}/exported_data.csv", "w", newline="") as file:
			writer = csv.writer(file)
			writer.writerow(header)
			writer.writerows(rows)
