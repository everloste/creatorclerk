import datetime

class Log:
	instance = None
	log_path = None

	def __new__(cls, *args, **kwargs):
		if not cls.instance:
			cls.instance = super(Log, cls).__new__(cls)
			cls.log_path = args[0]

			with open(file=cls.log_path, mode="a", encoding="UTF-8") as file:
				timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
				file.write(f"\n-------------------- {timestamp} --------------------")

		return cls.instance

	def write_line(self, text):
		print(text)
		with open(file=self.log_path, mode="a", encoding="UTF-8") as file:
			timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S")
			file.write(f"\n[{timestamp}] {text}")