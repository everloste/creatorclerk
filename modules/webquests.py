import requests, json, re

class RequestData:
	UserAgent = "everloste/creatorclerk/0.25.5.31"


# Load cookies from file path
# Right now only supports JSON files as exported by the cookie-editor extension
def load_cookies_from_file(path: str) -> dict:
	cookies = dict()

	try:
		with open(path, "r") as file:
			source = json.loads(file.read())

	except ValueError:
		raise ValueError("The cookie file is either not a JSON file or is invalid")

	except OSError:
		raise FileNotFoundError("The cookie file either doesn't exist or cannot be read")

	if isinstance(source, list):
		for item in source:
			if isinstance(item, dict):
				try:
					cookies[item["name"]] = item["value"]
				except KeyError:
					pass

	if len(cookies) != 0:
		return cookies
	else:
		raise ValueError("The cookie file was read, but contains no valid cookie values")


#################### CURSEFORGE ####################

# Get CurseForge points balance
def get_curseforge_points_balance(cookies: dict) -> int:
	return curseforge_api_get(cookies, "reward-store/user-points", ["userPoints"])

# Get CurseForge dollar balance
def get_curseforge_dollar_balance(cookies: dict) -> float:
	points = get_curseforge_points_balance(cookies)
	return points * 0.05

# Get CurseForge total download count
def get_curseforge_downloads_total(cookies: dict) -> int:
	return curseforge_api_get(cookies, "statistics/queries/downloadsTotal", ["queryResult", "data", 0, "total"])

# Helper function for interacting with the CurseForge authors API
def curseforge_api_get(cookies: dict, url: str, value_path: list) -> any:
	response = requests.get(
		url = f"https://authors.curseforge.com/_api/{url}",
		cookies = cookies,
		headers = {
			"user-agent": RequestData.UserAgent,
			"host": "authors.curseforge.com",
			"referer": "https://authors.curseforge.com/"
		}
	)

	if response.status_code != 200:
		raise ConnectionError(f"Request to CurseForge API returned {response.status_code}; cookies might be invalid")

	try:
		response_data = response.json()
		for key in value_path:
			response_data = response_data[key]
		return response_data

	except KeyError or ValueError:
		raise ValueError(f"Request response from CurseForge API wasn't as expected: {response.text}")


#################### MODRINTH ####################

# Get Modrinth balance
# This Modrinth page is static, which means we can just request it and search for the numbers
def get_modrinth_dollar_balance(cookies: dict) -> float:
	response = requests.get(
		url = "https://modrinth.com/dashboard/revenue",
		cookies = cookies,
		headers = {
			"user-agent": RequestData.UserAgent
		}
	)
	result = __get_modrinth_balance_from_page__(response.text)
	if result is None:
		raise ConnectionError("The Modrinth webpage didn't contain balance values. Are your cookies valid?")

	return result

# Helper function to search the revenue page for the amount
# Uses regex to search for the dollar amount
def __get_modrinth_balance_from_page__(html: str) -> float | None:
	try:
		a = re.findall(
			pattern="""Available now.*?\\$(.*?)<\\/div>""",
			string=html,
			flags=re.DOTALL)[0].strip().replace(",", "")

		b = re.findall(
			pattern="""Total pending.*?\\$(.*?)<\\/div>""",
			string=html,
			flags=re.DOTALL)[0].strip().replace(",", "")

		return float(a) + float(b)

	except IndexError:
		return None
