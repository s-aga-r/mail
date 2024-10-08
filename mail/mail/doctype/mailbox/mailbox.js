// Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Mailbox", {
	setup(frm) {
        frm.trigger("set_queries");
    },

    refresh(frm) {
        frm.trigger("add_actions");
	},

	set_queries(frm) {
		frm.set_query("domain_name", () => ({
            query: "mail.mail.doctype.mailbox.mailbox.get_domain",
        }));

		frm.set_query("user", () => ({
            query: "mail.mail.doctype.mailbox.mailbox.get_user",
        }));
    },

    add_actions(frm) {
        if (frm.doc.__islocal || !has_common(frappe.user_roles, ["Administrator", "System Manager"])) return;

        frm.add_custom_button(__("Delete Incoming Mails"), () => {
            frappe.confirm(
                __("Are you certain you wish to proceed?"),
                () => frm.trigger("delete_incoming_mails")
            )
        }, __("Actions"));

        frm.add_custom_button(__("Delete Outgoing Mails"), () => {
            frappe.confirm(
                __("Are you certain you wish to proceed?"),
                () => frm.trigger("delete_outgoing_mails")
            )
        }, __("Actions"));
    },

    delete_incoming_mails(frm) {
        frappe.call({
			method: "mail.mail.doctype.incoming_mail.incoming_mail.delete_incoming_mails",
			args: {
				mailbox: frm.doc.name,
			},
			freeze: true,
			freeze_message: __("Deleting Incoming Mails..."),
		});
    },

    delete_outgoing_mails(frm) {
        frappe.call({
			method: "mail.mail.doctype.outgoing_mail.outgoing_mail.delete_outgoing_mails",
			args: {
				mailbox: frm.doc.name,
			},
			freeze: true,
			freeze_message: __("Deleting Outgoing Mails..."),
		});
    },
});
