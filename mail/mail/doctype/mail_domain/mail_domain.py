# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from mail.mail_server import MailServerDomain
from mail.mail.doctype.mailbox.mailbox import create_postmaster_mailbox


class MailDomain(Document):
	def autoname(self) -> None:
		self.domain_name = self.domain_name.strip().lower()
		self.name = self.domain_name

	def validate(self) -> None:
		self.validate_newsletter_retention()

		if self.is_new():
			self.add_or_update_domain_in_mail_server()

		if not self.enabled:
			self.is_verified = 0

	def after_insert(self) -> None:
		create_postmaster_mailbox(self.domain_name)

	def validate_newsletter_retention(self) -> None:
		"""Validates the Newsletter Retention."""

		if self.newsletter_retention:
			if self.newsletter_retention < 1:
				frappe.throw(_("Newsletter Retention must be greater than 0."))

			max_newsletter_retention = frappe.db.get_single_value(
				"Mail Settings", "max_newsletter_retention", cache=True
			)
			if self.newsletter_retention > max_newsletter_retention:
				frappe.throw(
					_("Newsletter Retention must be less than or equal to {0}.").format(
						frappe.bold(max_newsletter_retention)
					)
				)
		else:
			self.newsletter_retention = frappe.db.get_single_value(
				"Mail Settings", "default_newsletter_retention", cache=True
			)

	def add_or_update_domain_in_mail_server(self) -> None:
		"""Adds or Updates the Domain in the Mail Server."""

		mail_settings = frappe.get_cached_doc("Mail Settings")
		ms_domain = MailServerDomain(
			mail_settings.mail_server_host,
			mail_settings.mail_server_api_key,
			mail_settings.get_password("mail_server_api_secret"),
		)
		response = ms_domain.add_or_update_domain(self.domain_name)

		for record in response["dns_records"]:
			self.append("dns_records", record)

		self.dkim_selector = response["dkim_selector"]
		self.dkim_private_key = response["dkim_private_key"]

	@frappe.whitelist()
	def refresh_dns_records(self) -> None:
		"""Refreshes the DNS Records."""

		self.is_verified = 0
		self.dns_records.clear()

		mail_settings = frappe.get_cached_doc("Mail Settings")
		ms_domain = MailServerDomain(
			mail_settings.mail_server_host,
			mail_settings.mail_server_api_key,
			mail_settings.get_password("mail_server_api_secret"),
		)
		dns_records = ms_domain.get_dns_records(self.domain_name)

		for record in dns_records:
			self.append("dns_records", record)

		self.save()

	@frappe.whitelist()
	def verify_dns_records(self, save: bool = True) -> None:
		"""Verifies the DNS Records."""

		mail_settings = frappe.get_cached_doc("Mail Settings")
		ms_domain = MailServerDomain(
			mail_settings.mail_server_host,
			mail_settings.mail_server_api_key,
			mail_settings.get_password("mail_server_api_secret"),
		)
		errors = ms_domain.verify_dns_records(self.domain_name)

		if not errors:
			self.is_verified = 1
			frappe.msgprint(
				_("DNS Records verified successfully."), indicator="green", alert=True
			)
		else:
			self.is_verified = 0
			frappe.msgprint(
				errors, title="DNS Verification Failed", indicator="red", as_list=True
			)

		if save:
			self.save()
