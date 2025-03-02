// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mail Agent Store', {
	refresh(frm) {
		frm.trigger('set_defaults')
	},

	set_defaults(frm) {
		if (!frm.doc.__islocal || !frm.doc.type) return

		if (frm.doc.type === 'RocksDB') {
			frm.set_value('store_id', 'rocksdb')
			frm.set_value('compression', 'LZ4')
			frm.set_value('min_blob_size_bytes', '16834')
			frm.set_value('write_buffer_size_mb', '128')
			frm.set_value('purge_frequency_cron', '0 3 * * *')
		}
	},
})
