frappe.ui.form.on('Church SMS', {
    refresh: function(frm) {
        // Show/hide fields based on send_to
        frm.toggle_display('branch', frm.doc.send_to === 'Specific Branch');
        frm.toggle_display('manual_numbers', frm.doc.send_to === 'Manual Numbers');
        
        // Add Send SMS button for saved documents
        if (!frm.is_new() && frm.doc.status !== 'Sent') {
            frm.add_custom_button(__('Send SMS Now'), function() {
                frappe.call({
                    method: 'church_sms.api.send_church_sms',
                    args: {
                        send_to: frm.doc.send_to,
                        message: frm.doc.message,
                        sender_id: frm.doc.sender_id || 'KKKT MABIBO',
                        branch: frm.doc.branch || '',
                        manual_numbers: frm.doc.manual_numbers || ''
                    },
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
                                
                                // Reload to see updated status
                                frm.reload_doc();
                            } else {
                                frappe.msgprint({
                                    title: __('Failed'),
                                    indicator: 'red',
                                    message: r.message.message
                                });
                            }
                        }
                    }
                });
            }).addClass('btn-primary');
        }
        
        // Show info for background jobs
        if (frm.doc.status === 'Draft' && frm.doc.response && frm.doc.response.includes('background')) {
            frm.dashboard.add_comment(
                __('SMS is being sent in background. Check SMS Log for progress.'),
                'blue',
                true
            );
        }
    },
    
    send_to: function(frm) {
        frm.trigger('refresh');
    }
});
