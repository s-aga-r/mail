# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint
from mail.utils.cache import delete_cache
from frappe.model.document import Document
from frappe.core.api.file import get_max_file_size


class MailSettings(Document):
	def validate(self) -> None:
		self.validate_postmaster()
		self.validate_outgoing_max_attachment_size()
		self.validate_outgoing_total_attachments_size()

	def on_update(self) -> None:
		delete_cache("postmaster")

	def validate_postmaster(self) -> None:
		"""Validates the Postmaster."""

		if not self.postmaster:
			return

		if not frappe.db.exists("User", self.postmaster):
			frappe.throw(_("User {0} does not exist.").format(frappe.bold(self.postmaster)))
		elif not frappe.db.get_value("User", self.postmaster, "enabled"):
			frappe.throw(_("User {0} is disabled.").format(frappe.bold(self.postmaster)))
		elif not frappe.db.exists(
			"Has Role", {"parent": self.postmaster, "role": "Postmaster", "parenttype": "User"}
		):
			frappe.throw(
				_("User {0} does not have the Postmaster role.").format(
					frappe.bold(self.postmaster)
				)
			)

	def validate_outgoing_max_attachment_size(self) -> None:
		"""Validates the Outgoing Max Attachment Size."""

		max_file_size = cint(get_max_file_size() / 1024 / 1024)

		if self.outgoing_max_attachment_size > max_file_size:
			frappe.throw(
				_("{0} should be less than or equal to {1} MB.").format(
					frappe.bold("Max Attachment Size"), frappe.bold(max_file_size)
				)
			)

	def validate_outgoing_total_attachments_size(self) -> None:
		"""Validates the Outgoing Total Attachments Size."""

		if self.outgoing_max_attachment_size > self.outgoing_total_attachments_size:
			frappe.throw(
				_("{0} should be greater than or equal to {1}.").format(
					frappe.bold("Total Attachments Size"), frappe.bold("Max Attachment Size")
				)
			)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_postmaster(
	doctype: str | None = None,
	txt: str | None = None,
	searchfield: str | None = None,
	start: int = 0,
	page_len: int = 20,
	filters: dict | None = None,
) -> list:
	"""Returns the Postmaster."""

	USER = frappe.qb.DocType("User")
	HAS_ROLE = frappe.qb.DocType("Has Role")
	return (
		frappe.qb.from_(USER)
		.left_join(HAS_ROLE)
		.on(USER.name == HAS_ROLE.parent)
		.select(USER.name)
		.where(
			(USER.enabled == 1)
			& (USER.name.like(f"%{txt}%"))
			& (HAS_ROLE.role == "Postmaster")
			& (HAS_ROLE.parenttype == "User")
		)
	).run(as_dict=False)
