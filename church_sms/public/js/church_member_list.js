frappe.listview_settings['Church Member'] = {
    onload: function(listview) {
        // Add bulk delete button
        listview.page.add_action_item(__('Delete Selected'), function() {
            var selected = listview.get_checked_items();
            if (selected.length === 0) {
                frappe.msgprint('Please select members to delete');
                return;
            }
            
            var names = selected.map(function(d) { return d.name; });
            
            frappe.confirm(
                'Are you sure you want to delete ' + names.length + ' member(s)? This cannot be undone.',
                function() {
                    frappe.call({
                        method: 'church_sms.api.bulk_delete_members',
                        args: { member_names: names },
                        freeze: true,
                        callback: function(r) {
                            if (r.message) {
                                frappe.msgprint(r.message.message);
                                listview.refresh();
                            }
                        }
                    });
                }
            );
        });

        // Add bulk update status button
        listview.page.add_action_item(__('Set as Active'), function() {
            var selected = listview.get_checked_items();
            if (selected.length === 0) {
                frappe.msgprint('Please select members');
                return;
            }
            
            var names = selected.map(function(d) { return d.name; });
            frappe.call({
                method: 'church_sms.api.bulk_update_members',
                args: { member_names: names, field: 'status', value: 'Active' },
                freeze: true,
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert({message: r.message.message, indicator: 'green'});
                        listview.refresh();
                    }
                }
            });
        });

        listview.page.add_action_item(__('Set as Inactive'), function() {
            var selected = listview.get_checked_items();
            if (selected.length === 0) {
                frappe.msgprint('Please select members');
                return;
            }
            
            var names = selected.map(function(d) { return d.name; });
            frappe.call({
                method: 'church_sms.api.bulk_update_members',
                args: { member_names: names, field: 'status', value: 'Inactive' },
                freeze: true,
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert({message: r.message.message, indicator: 'green'});
                        listview.refresh();
                    }
                }
            });
        });

        // Add bulk change branch
        listview.page.add_action_item(__('Change Branch'), function() {
            var selected = listview.get_checked_items();
            if (selected.length === 0) {
                frappe.msgprint('Please select members');
                return;
            }
            
            var names = selected.map(function(d) { return d.name; });
            
            frappe.prompt({
                fieldtype: 'Link',
                label: 'New Branch',
                fieldname: 'branch',
                options: 'Church Branch',
                reqd: 1
            }, function(values) {
                frappe.call({
                    method: 'church_sms.api.bulk_update_members',
                    args: { member_names: names, field: 'branch', value: values.branch },
                    freeze: true,
                    callback: function(r) {
                        if (r.message) {
                            frappe.show_alert({message: r.message.message, indicator: 'green'});
                            listview.refresh();
                        }
                    }
                });
            }, 'Change Branch for ' + names.length + ' Members');
        });
    },

    get_indicator: function(doc) {
        if (doc.status === 'Active') {
            return [__('Active'), 'green', 'status,=,Active'];
        } else {
            return [__('Inactive'), 'grey', 'status,=,Inactive'];
        }
    }
};
