import os, json
from modules.log import Log

class App:
	instance = None
	data = dict()
	data_folder_name = ".data"

	def __new__(cls, local_path):
		if not cls.instance:
			cls.instance = super(App, cls).__new__(cls)
			cls.local_path = local_path
			cls.file_path = f"{local_path}/{cls.data_folder_name}/settings.json"

		return cls.instance

	def __init__(self, local_path):
		self.changes_made = False

		# Create settings file (and log file) if it doesn't exist
		if not os.path.exists(self.file_path):
			self.data = {
				"database_path": ""
			}

			os.makedirs(f"{self.local_path}/{self.data_folder_name}", exist_ok=True)

			with open(self.file_path, "w", encoding="UTF-8") as file:
				file.write(json.dumps(self.data, indent=2).replace("  ", "\t"))

			with open(f"{self.local_path}/{self.data_folder_name}/log.txt".replace("\\", "/"), "w") as file:
				file.write("...")

		# Or load the settings file
		else:
			with open(self.file_path, "r", encoding="UTF-8") as file:
				self.data = json.loads(file.read())

		# Load the log writer for the first time
		self.log = Log(f"{self.local_path}/{self.data_folder_name}/log.txt")

		# Create local database if there is no path to one
		if (self.data["database_path"] == ""):
			self.log.write_line(
				"No path to database file found, assuming local...\nIf you wish to use a custom database location, edit the settings.json file.")
			self.data["database_path"] = f"{self.local_path}/{self.data_folder_name}/data.sqlite3".replace("\\", "/")
			self.changes_made = True

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		# Rewrite the settings file if there were changes made
		if self.changes_made:
			self.log.write_line(
				"Updating settings.json...")
			with open(self.file_path, "w", encoding="UTF-8") as file:
				file.write(json.dumps(self.data, indent=2).replace("  ", "\t"))

	def get_database_path(self):
		return self.data["database_path"]