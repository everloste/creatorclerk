import os, sys
from modules.app import App
from modules.database import DatabaseHandler


def parse_system_arguments(args_, flags = None):
	try:
		if args_[0] == "add":
			database.add_account(
				account_type = args_[1],
				account_name = args_[2]
			)
		elif args_[0] == "collect":
			database.collect_accounts()

		elif args_[0] == "export":
			database.export_csv(
				directory = args_[1]
			)
		elif args_[0] == "cookies":
			if args_[1] == "add":
				database.add_website_cookie(
					account_id=database.get_account_id_from_name(args_[2]),
					path=args_[3]
				)
			elif args_[1] == "remove":
				database.remove_access_method(database.get_account_id_from_name(args_[2]))

		elif args_[0] == "list":
			app.log.write_line(
				f"Account list: {database.get_accounts()}"
			)

		elif args_[0] == "connect":
			print("Connecting...")
			print(f"Account balance: ${database.collect_account(
				database.get_account_id_from_name(args_[1])
			)}")
			print("For your privacy the balance is not written to the log.")

		else:
			raise ValueError("Command cannot be recognized")

	except IndexError:
		raise IndexError("Command is missing arguments")


if __name__ == '__main__':
	raw_args = sys.argv[1:]

	args = [x.strip() for x in raw_args if x[0] != "-"]
	flags = [x.strip()[1:] for x in raw_args if x[0] == "-"]

	if len(args) > 0:
		with App(os.path.realpath(os.path.dirname(__file__))) as app:
			with DatabaseHandler(app.get_database_path()) as database:
				try:
					parse_system_arguments(args, flags)
				except:
					app.log.write_line(f"Failed to execute command:\n\tArguments: {raw_args}\n\tError: {sys.exc_info()[1]}")

	if "wait" in flags:
		input("Press any key to exit... ")