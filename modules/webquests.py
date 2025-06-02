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

# Get points generated
def get_curseforge_transactions(cookies: dict, range_start: int, range_end: int) -> list:
	data = curseforge_api_get(cookies, f"transactions?filter=%7B%7D&range=%5B{range_start}%2C{range_end}%5D&sort=%5B%22DateCreated%22%2C%22DESC%22%5D", None)
	output = list()
	for trans in data:
		ttype = "income" if (trans["type"] == 1) else 0
		if (ttype == 0):
			if (trans["type"] == 8):
				ttype = "withdrawal"
			elif (trans["type"] == 5):
				continue
			else:
				ttype = "unknown"
		output.append({
			"change": trans["pointChange"] * 0.05 if (ttype != "withdrawal") else trans["pointChange"] * -0.05,
			"date": trans["dateCreated"][:10],
			"time": trans["dateCreated"][11:16],
			"type": ttype
		})
	return output


# Helper function for interacting with the CurseForge authors API
def curseforge_api_get(cookies: dict, url: str, value_path: list = None) -> any:
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
		if value_path is not None:
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


# Gets user information from provided cookies
# https://docs.modrinth.com/api/operations/getuserfromauth/
def get_modrinth_user_info(cookies: dict):
	response = requests.get(
		url = "https://api.modrinth.com/v2/user",
		cookies = cookies,
		headers = {
			"user-agent": RequestData.UserAgent,
			"Authorization": cookies["auth-token"]
		}
	)
	return response.json()


# Gets all projects of a Modrinth user
# https://docs.modrinth.com/api/operations/getuserprojects/
def get_modrinth_user_projects(user: str):
	response = requests.get(
		url = f"https://api.modrinth.com/v2/user/{user}/projects",
		headers = {
			"user-agent": RequestData.UserAgent
		}
	)
	return response.json()


# Gets the download count of a project
# https://docs.modrinth.com/api/operations/getproject/
def get_modrinth_project_downloads(project: str) -> int:
	response = requests.get(
		url = f"https://api.modrinth.com/v2/project/{project}",
		headers = {
			"user-agent": RequestData.UserAgent
		}
	)
	return response.json()["downloads"]


# Gets the total download count of all Modrinth user's projects
def get_modrinth_downloads_total(cookies: dict) -> int:
	user_info = get_modrinth_user_info(cookies)
	projects = get_modrinth_user_projects(user_info["id"])

	count: int = 0
	for project in projects:
		count += get_modrinth_project_downloads(project["id"])

	return count


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
