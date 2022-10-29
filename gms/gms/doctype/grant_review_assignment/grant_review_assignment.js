// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt


//Navari 25/03/2021
//selecting and adding grant application in child table and Reviewers
frappe.ui.form.on('Grant Review Assignment', {

	get_grant_applications: function (frm) {
		frappe.call({
			method: "get_submitted_grant_applications",
			doc: frm.doc,
			callback: function (r) {
				refresh_field("grant_applications");
			}
		});
	},
	get_reviewers: function (frm) {
		frappe.call({
			method: "get_current_discipline_reviewers",
			doc: frm.doc,
			callback: function (r) {
				refresh_field("reviewers");
			}
		});
	},
	send_emails_to_reviewers: function (frm) {
		frappe.call({
			method: "send_emails_to_reviewers",
			doc: frm.doc,
			callback: function (r) {
				refresh_field("reviewers");
			}
		});
	}
});
