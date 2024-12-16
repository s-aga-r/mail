from typing import Any
from urllib.parse import urljoin

import requests


class JMAPClient:
	def __init__(self, base_url: str, username: str, password: str) -> None:
		"""
		Initialize the JMAP Client.
		:param base_url: Base URL of the JMAP server.
		:param username: Username for authentication.
		:param password: Password for authentication.
		"""
		self.__base_url = base_url
		self.__username = username
		self.__password = password
		self.__session = None
		self.__mailboxes = None

		self.authenticate()

	def authenticate(self) -> None:
		"""
		Authenticate and fetch session details.
		"""
		url = urljoin(self.__base_url, ".well-known/jmap")
		response = requests.get(url, auth=(self.__username, self.__password))
		if response.status_code == 200:
			self.__session = response.json()
		else:
			raise Exception(f"Authentication failed: {response.status_code}, {response.text}")

	def load_mailboxes(self) -> None:
		"""
		Load mailboxes for the account.
		"""
		response = self.make_request(
			["urn:ietf:params:jmap:mail"], [["Mailbox/get", {"accountId": self.account_id}, "0"]]
		)
		self.__mailboxes = response["methodResponses"][0][1]["list"]

	@property
	def session(self) -> dict | None:
		"""
		Return the session details.
		"""
		return self.__session

	@property
	def api_url(self) -> str | None:
		"""
		Return the API URL.
		"""
		return self.__session["apiUrl"]

	@property
	def upload_url(self) -> str | None:
		"""
		Return the Upload URL.
		"""
		return self.__session["uploadUrl"]

	@property
	def download_url(self) -> str | None:
		"""
		Return the Download URL.
		"""
		return self.__session["downloadUrl"]

	@property
	def event_source_url(self) -> str | None:
		"""
		Return the Event Source URL.
		"""
		return self.__session["eventSourceUrl"]

	@property
	def account_id(self) -> str | None:
		"""
		Return the account ID.
		"""
		return list(self.__session["accounts"].keys())[0]

	@property
	def capabilities(self) -> list[str] | None:
		"""
		Return the capabilities.
		"""
		return self.__session["capabilities"]

	@property
	def mailboxes(self) -> list[dict] | None:
		"""
		Return the mailboxes.
		"""
		return self.__mailboxes

	def __validate_capabilities(self, capabilities: list[str]) -> None:
		"""
		Validate the capabilities.
		:param using: List of capabilities.
		"""
		for capability in capabilities:
			if capability not in self.capabilities:
				raise Exception(f"Capability {capability} not supported by the server.")

	def __validate_method_calls(self, method_calls: list[list]) -> None:
		"""
		Validate the method calls.
		:param method_calls: List of method calls.
		"""
		call_ids = []
		for method_call in method_calls:
			if not isinstance(method_call, list) or len(method_call) != 3:
				raise Exception("Method call should be a list of 3 elements.")

			if (
				not isinstance(method_call[0], str)
				or not isinstance(method_call[1], dict)
				or not isinstance(method_call[2], str)
			):
				raise Exception("Method call should be a list of [string, dict, string].")

			if method_call[2] in call_ids:
				raise Exception("Call ID should be unique.")

			call_ids.append(method_call[2])

	def _get_mailbox_id(self, role: str) -> str | None:
		"""
		Get the mailbox ID for the given role.
		:param role: Role of the mailbox.
		"""
		for mailbox in self.mailboxes:
			if mailbox["role"] == role:
				return mailbox["id"]

	def make_request(self, using: list[str], method_calls: list[list]) -> Any:
		"""
		Make a JMAP API call.
		:param using: List of capabilities to use (e.g., ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"]).
		:param method_calls: List of method calls (e.g., [["Email/query", {"accountId": "your-account-id"}, "0"]]).
		:return: JSON response.
		"""
		if not self.api_url:
			raise Exception("Client not authenticated. Call authenticate() first.")

		self.__validate_capabilities(using)
		self.__validate_method_calls(method_calls)

		request_body = {"using": using, "methodCalls": method_calls}
		response = requests.post(self.api_url, json=request_body, auth=(self.__username, self.__password))
		if response.status_code == 200:
			return response.json()
		else:
			raise Exception(f"JMAP API call failed: {response.status_code}, {response.text}")

	def fetch_emails(
		self,
		filter: dict | None = None,
		sort: list[dict] | None = None,
		position: int = 0,
		limit: int = 10,
		calculate_total: bool = True,
		properties: list[str] | None = None,
	) -> tuple[int, list]:
		email_query_args = {
			"accountId": self.account_id,
			"position": position,
			"limit": limit,
			"calculateTotal": calculate_total,
		}
		if filter:
			email_query_args["filter"] = filter
		if sort:
			email_query_args["sort"] = sort

		email_get_args = {
			"accountId": self.account_id,
			"#ids": {"name": "Email/query", "path": "/ids", "resultOf": "0"},
		}
		if properties:
			email_get_args["properties"] = properties

		method_calls = [["Email/query", email_query_args, "0"], ["Email/get", email_get_args, "1"]]
		response = self.make_request(["urn:ietf:params:jmap:mail"], method_calls)
		total = response["methodResponses"][0][1].get("total", 0)
		emails = response["methodResponses"][1][1]["list"]

		return total, emails

	def download_blob(self, blob_id: str) -> str:
		"""
		Download a blob using the download URL.
		:param blob_id: Blob ID to download.
		:return: Blob content as a string.
		"""
		download_url = self.download_url.format(
			accountId=self.account_id, blobId=blob_id, name="blob", type="application/octet-stream"
		)
		response = requests.get(download_url, auth=(self.__username, self.__password))
		if response.status_code != 200:
			raise Exception(f"Blob download failed: {response.status_code} {response.text}")
		return response.text


def get_client():
	BASE_URL = "https://a1-blr.mail.frappemail.com"
	USERNAME = "u1@s-aga-r.dev"
	PASSWORD = "u1@s-aga-r.dev"
	return JMAPClient(BASE_URL, USERNAME, PASSWORD)


def process():
	emails = []
	client = get_client()
	client.authenticate()
	for email_id in client.query_emails(limit=1_00_000):
		matadata = client.fetch_email(email_id)
		email = client.download_blob(matadata["blobId"])
		emails.append(email)

	return emails
