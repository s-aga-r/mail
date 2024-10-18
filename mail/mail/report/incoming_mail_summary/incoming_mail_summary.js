// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Incoming Mail Summary"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_days(frappe.datetime.get_today(), -7),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "name",
			label: __("Incoming Mail"),
			fieldtype: "Link",
			options: "Incoming Mail",
			get_query: () => {
				return {
					query: "mail.utils.query.get_outgoing_mails",
				};
			},
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: ["", "Delivered", "Rejected"],
		},
		{
			fieldname: "folder",
			label: __("Folder"),
			fieldtype: "Select",
			options: ["", "Inbox", "Spam", "Trash"],
		},
		{
			fieldname: "agent",
			label: __("Agent"),
			fieldtype: "Data",
		},
		{
			fieldname: "domain_name",
			label: __("Domain Name"),
			fieldtype: "Link",
			options: "Mail Domain",
		},
		{
			fieldname: "from_ip_address",
			label: __("From IP Address"),
			fieldtype: "Data",
		},
		{
			fieldname: "from_host",
			label: __("From Host"),
			fieldtype: "Data",
		},
		{
			fieldname: "sender",
			label: __("Sender"),
			fieldtype: "Data",
		},
		{
			fieldname: "receiver",
			label: __("Receiver"),
			fieldtype: "Link",
			options: "Mailbox",
		},
		{
			fieldname: "message_id",
			label: __("Message ID"),
			fieldtype: "Data",
		},
	],
};
