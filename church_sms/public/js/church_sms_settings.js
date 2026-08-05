frappe.ui.form.on("Church SMS Settings", {
    refresh: function(frm) {
        // Test Connection button
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
                            message: frappe.utils.md_to_html(r.message.message)
                        });
                    }
                }
            });
        }, __("Actions")).addClass("btn-primary");

        // Diagnose button
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
        }, __("Actions"));

        // Quick status info
        frappe.call({
            method: "frappe.client.get_count",
            args: { doctype: "Church Member", filters: { status: "Active" } },
            callback: function(r) {
                if (r.message !== undefined) {
                    frm.dashboard.set_headline(
                        '<span class="indicator-pill green">👥 ' + r.message + ' Active Members</span> &nbsp; ' +
                        '<span class="indicator-pill blue">📱 Sender ID: ' + (frm.doc.default_sender_id || 'Not Set') + '</span>'
                    );
                }
            }
        });
    }
});
