frappe.pages['sms-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'SMS Dashboard',
        single_column: true
    });
    
    $(page.body).html(`
        <div class="container-fluid">
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body">
                            <h5 class="card-title">Total SMS Sent</h5>
                            <h2 id="total-sms">0</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body">
                            <h5 class="card-title">Delivered</h5>
                            <h2 id="delivered-sms">0</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-danger text-white">
                        <div class="card-body">
                            <h5 class="card-title">Failed</h5>
                            <h2 id="failed-sms">0</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body">
                            <h5 class="card-title">Active Members</h5>
                            <h2 id="total-members">0</h2>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>SMS Balance</h5>
                        </div>
                        <div class="card-body">
                            <h2 id="sms-balance">Loading...</h2>
                            <button class="btn btn-sm btn-primary" onclick="refresh_balance()">
                                <i class="fa fa-refresh"></i> Refresh
                            </button>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Quick Actions</h5>
                        </div>
                        <div class="card-body">
                            <a href="/app/church-sms/new" class="btn btn-primary btn-block mb-2">
                                <i class="fa fa-plus"></i> Send New SMS
                            </a>
                            <a href="/app/church-member" class="btn btn-secondary btn-block mb-2">
                                <i class="fa fa-users"></i> Manage Members
                            </a>
                            <a href="/app/scheduled-sms" class="btn btn-info btn-block">
                                <i class="fa fa-clock-o"></i> Scheduled Messages
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <h5>Recent Campaigns</h5>
                        </div>
                        <div class="card-body">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Name</th>
                                        <th>Send To</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody id="recent-campaigns">
                                    <tr><td colspan="4">Loading...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `);
    
    load_dashboard_data();
};

function load_dashboard_data() {
    frappe.call({
        method: 'church_sms.api.get_sms_statistics',
        callback: function(r) {
            if (r.message && r.message.success) {
                var stats = r.message.stats;
                $('#total-sms').text(stats.total_sms || 0);
                $('#delivered-sms').text(stats.sent || 0);
                $('#failed-sms').text(stats.failed || 0);
                $('#total-members').text(stats.total_members || 0);
                
                var campaigns = r.message.recent_campaigns || [];
                var tbody = $('#recent-campaigns');
                tbody.empty();
                
                if (campaigns.length === 0) {
                    tbody.append('<tr><td colspan="4">No campaigns yet</td></tr>');
                } else {
                    campaigns.forEach(function(c) {
                        tbody.append(`
                            <tr>
                                <td>${frappe.datetime.str_to_user(c.creation)}</td>
                                <td><a href="/app/church-sms/${c.name}">${c.name}</a></td>
                                <td>${c.send_to}</td>
                                <td><span class="badge badge-${c.status === 'Sent' ? 'success' : 'warning'}">${c.status}</span></td>
                            </tr>
                        `);
                    });
                }
            }
        }
    });
    
    refresh_balance();
}

function refresh_balance() {
    $('#sms-balance').text('Loading...');
    frappe.call({
        method: 'church_sms.api.get_sms_balance',
        callback: function(r) {
            if (r.message && r.message.success) {
                $('#sms-balance').text(r.message.balance + ' SMS');
            } else {
                $('#sms-balance').text('N/A');
            }
        }
    });
}
