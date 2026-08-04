// Church SMS - Additional client-side functionality
// Note: Main form logic is in the "Church SMS-Form" Client Script

// Add Test Connection button to Church SMS Settings
frappe.ui.form.on("Church SMS Settings", {
    refresh: function(frm) {
        frm.add_custom_button(__("Test Connection"), function() {
            frappe.call({
                method: "church_sms.api.test_sms_connection",
                freeze: true,
                freeze_message: "Testing connection...",
                callback: function(r) {
                    if (r.message) {
                        if (r.message.success) {
                            frappe.msgprint({
                                title: "Connection Test",
                                indicator: "green",
                                message: r.message.message
                            });
                        } else {
                            frappe.msgprint({
                                title: "Connection Test Failed",
                                indicator: "red",
                                message: r.message.message
                            });
                        }
                    }
                }
            });
        }).addClass("btn-primary");
    }
});
