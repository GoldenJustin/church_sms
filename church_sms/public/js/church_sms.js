// Church SMS Settings - Add Test and Diagnose buttons
frappe.ui.form.on("Church SMS Settings", {
    refresh: function(frm) {
        frm.add_custom_button(__("Test Connection"), function() {
            frappe.call({
                method: "church_sms.api.test_sms_connection",
                freeze: true,
                freeze_message: "Testing...",
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint({
                            title: r.message.success ? "✅ Connection OK" : "❌ Connection Failed",
                            indicator: r.message.success ? "green" : "red",
                            message: r.message.message
                        });
                    }
                }
            });
        }).addClass("btn-primary");

        frm.add_custom_button(__("🔍 Diagnose"), function() {
            frappe.call({
                method: "church_sms.api.diagnose_sms_setup",
                freeze: true,
                freeze_message: "Running diagnosis...",
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint({
                            title: "🔍 SMS Diagnosis Report",
                            indicator: "blue",
                            message: frappe.utils.md_to_html(r.message),
                            wide: true
                        });
                    }
                }
            });
        });
    }
});
