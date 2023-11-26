// Copyright (c) 2023, Oymom and contributors
// For license information, please see license.txt

frappe.ui.form.on("Doctor Registration", {
	refresh(frm) {
        if (!cur_frm.is_new()){

            cur_frm.page.set_primary_action(__('Approve'), function() {
                cur_frm.save("Submit")
            }).addClass('btn-primary');
        }
	},
});
