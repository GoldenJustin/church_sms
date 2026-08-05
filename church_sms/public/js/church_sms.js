frappe.ui.form.on('Church SMS', {
    send_to: function(frm) {
        // Show/hide fields based on send_to
        frm.toggle_display('branch', frm.doc.send_to === 'Specific Branch');
        frm.toggle_display('manual_numbers', frm.doc.send_to === 'Manual Numbers');
        frm.toggle_display('members', frm.doc.send_to === 'Specific Members');
        
        // Make fields mandatory
        frm.toggle_reqd('branch', frm.doc.send_to === 'Specific Branch');
        frm.toggle_reqd('manual_numbers', frm.doc.send_to === 'Manual Numbers');
    },
    
    refresh: function(frm) {
        // Trigger send_to on refresh
        frm.trigger('send_to');
        
        // Add Send SMS button
        if (!frm.is_new() && frm.doc.status === 'Draft') {
            frm.add_custom_button(__('Send SMS'), function() {
                frappe.call({
                    method: 'church_sms.api.send_church_sms',
                    args: {
                        send_to: frm.doc.send_to,
                        message: frm.doc.message,
                        sender_id: frm.doc.sender_id,
                        branch: frm.doc.branch || '',
                        members: frm.doc.members || [],
                        manual_numbers: frm.doc.manual_numbers || ''
                    },
                    freeze: true,
                    freeze_message: __('Sending SMS...'),
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            frappe.msgprint({
                                title: __('Success'),
                                indicator: 'green',
                                message: r.message.message
                            });
                            frm.set_value('status', 'Sent');
                            frm.set_value('response', r.message.message);
                            frm.save();
                        } else {
                            frappe.msgprint({
                                title: __('Failed'),
                                indicator: 'red',
                                message: r.message ? r.message.message : __('Unknown error')
                            });
                            frm.set_value('status', 'Failed');
                            frm.set_value('response', r.message ? r.message.message : 'Failed');
                            frm.save();
                        }
                    }
                });
            }).addClass('btn-primary');
        }
    }
});
