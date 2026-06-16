# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from uuid import uuid7

import frappe
from frappe.model.document import Document

from mail.jmap import parse_account


class TrustedSender(Document):
	_DOCTYPE_NAME = "Trusted Sender"

	def autoname(self) -> None:
		self.name = str(uuid7())

	def before_insert(self) -> None:
		self.user = parse_account(self.account)[0]

	def validate(self) -> None:
		self.validate_duplicate_sender()
		self.sender = self.sender.lower()

	def validate_duplicate_sender(self) -> None:
		"""Validates that the same sender is not trusted multiple times for the same account."""

		if frappe.db.exists(
			"Trusted Sender",
			{"account": self.account, "sender": self.sender, "name": ["!=", self.name]},
		):
			frappe.throw(
				frappe._("The sender {0} is already trusted for account {1}.").format(
					self.sender, self.account
				)
			)


def is_sender_trusted(account: str, sender: str) -> bool:
	"""Returns True if the sender is trusted for the given account, False otherwise."""

	sender = sender.lower()
	return frappe.db.exists("Trusted Sender", {"account": account, "sender": sender}) is not None


def get_trusted_senders(account: str) -> list[str]:
	"""Returns a list of trusted senders for the given account."""

	return frappe.db.get_all("Trusted Sender", filters={"account": account}, pluck="sender")


def on_doctype_update() -> None:
	frappe.db.add_unique(
		"Trusted Sender",
		["account", "sender"],
		constraint_name="unique_account_trusted_sender",
	)
