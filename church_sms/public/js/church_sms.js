frappe.ui.form.on('Church SMS', {
    send_to: function(frm) {
        // Show/hide fields based on send_to
        frm.toggle_display('branch', frm.doc.send_to === 'Specific Branch');
        frm.toggle_display('manual_numbers', frm.doc.send_to === 'Manual Numbers');
        
        // Make fields mandatory
        frm.toggle_reqd('branch', frm.doc.send_to === 'Specific Branch');
        frm.toggle_reqd('manual_numbers', frm.doc.send_to === 'Manual Numbers');
    },
    
    refresh: function(frm) {
        // Trigger send_to on refresh
        frm.trigger('send_to');
        
        // Add Send SMS button
        if (!frm.is_new() && frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Send SMS'), function() {
                // Prepare arguments
                var args = {
                    send_to: frm.doc.send_to,
                    message: frm.doc.message,
                    sender_id: frm.doc.sender_id || 'KKKT MABIBO',
                    branch: frm.doc.branch || '',
                    members: frm.doc.members || []
                };
                
                // Add manual_numbers if applicable
                if (frm.doc.send_to === 'Manual Numbers') {
                    args.manual_numbers = frm.doc.manual_numbers || '';
                }
                
                frappe.call({
                    method: 'church_sms.api.send_church_sms',
                    args: args,
                    freeze: true,
                    freeze_message: __('Sending SMS...'),
                    callback: function(r) {
                        if (r.message) {
                            if (r.message.success) {
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
                                    message: r.message.message
                                });
                                frm.set_value('status', 'Failed');
                                frm.set_value('response', r.message.message);
                                frm.save();
                            }
                        }
                    }
                });
            }).addClass('btn-primary');
        }
    }
});
