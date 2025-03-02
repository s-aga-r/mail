# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import random_string


class MailAgentGroup(Document):
	def autoname(self) -> None:
		self.agent_group = self.agent_group.lower()
		self.name = self.agent_group

	def validate(self) -> None:
		self.validate_enabled()
		self.validate_agent_group()
		self.validate_priority()
		self.validate_admin_password()
		self.validate_cluster_encryption_key()

	def validate_enabled(self) -> None:
		"""Validates the enabled status of the agent group."""

		if self.enabled and not self.inbound and not self.outbound:
			self.enabled = 0

		if self.enabled:
			return

		if agent := frappe.db.exists("Mail Agent", {"enabled": 1, "agent_group": self.name}):
			frappe.throw(_("Mail Agent {0} is enabled. Please disable it first.").format(frappe.bold(agent)))

	def validate_agent_group(self) -> None:
		"""Validates the agent group."""

		if self.is_new() and frappe.db.exists("Mail Agent Group", self.agent_group):
			frappe.throw(_("Mail Agent Group {0} already exists.").format(frappe.bold(self.agent_group)))

	def validate_priority(self) -> None:
		"""Validates the priority of the agent group."""

		if frappe.db.exists(
			"Mail Agent Group",
			{"enabled": 1, "inbound": 1, "priority": self.priority, "name": ["!=", self.name]},
		):
			frappe.throw(
				_("Mail Agent Group with priority {0} already exists.").format(frappe.bold(self.priority))
			)

	def validate_admin_password(self) -> None:
		if self.admin_password:
			if len(self.admin_password) < 16:
				frappe.throw(_("Password must be at least 16 characters long."))
		else:
			self.admin_password = random_string(length=20)

	def validate_cluster_encryption_key(self) -> None:
		"""Validates the encryption key of the agent group."""

		if not self.cluster_encryption_key:
			self.cluster_encryption_key = random_string(length=64)
