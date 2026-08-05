frappe.pages['sms-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'SMS Dashboard',
        single_column: true
    });
    
    $(page.body).html(`
        <div class="container-fluid">
            <div class="row mb-4">
                <div class="col-md-12">
                    <h2><i class="fa fa-bar-chart"></i> SMS Dashboard</h2>
                </div>
            </div>
            <div class="row">
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body">
                            <h5 class="card-title">Total SMS</h5>
                            <h2 id="stat-total">Loading...</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body">
                            <h5 class="card-title">Sent</h5>
                            <h2 id="stat-sent">Loading...</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-danger text-white">
                        <div class="card-body">
                            <h5 class="card-title">Failed</h5>
                            <h2 id="stat-failed">Loading...</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body">
                            <h5 class="card-title">Members</h5>
                            <h2 id="stat-members">Loading...</h2>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row mt-4">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-body">
                            <h5>Recent Campaigns</h5>
                            <div id="recent-campaigns">Loading...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `);
    
    // Load statistics
    frappe.call({
        method: 'church_sms.api.get_sms_statistics',
        callback: function(r) {
            if (r.message && r.message.success) {
                var stats = r.message.stats;
                $('#stat-total').text(stats.total_sms || 0);
                $('#stat-sent').text(stats.sent || 0);
                $('#stat-failed').text(stats.failed || 0);
                $('#stat-members').text(stats.total_members || 0);
                
                var campaigns = r.message.recent_campaigns || [];
                var html = '<table class="table table-striped"><thead><tr><th>Name</th><th>Status</th><th>Created</th></tr></thead><tbody>';
                campaigns.forEach(function(c) {
                    html += '<tr><td><a href="/app/church-sms/' + c.name + '">' + c.name + '</a></td>';
                    html += '<td><span class="badge badge-' + (c.status === 'Sent' ? 'success' : 'warning') + '">' + c.status + '</span></td>';
                    html += '<td>' + frappe.datetime.str_to_user(c.creation) + '</td></tr>';
                });
                html += '</tbody></table>';
                $('#recent-campaigns').html(html);
            }
        }
    });
}
