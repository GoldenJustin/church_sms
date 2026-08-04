frappe.pages['import-members'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Import Church Members',
        single_column: true
    });
    
    // Build the page content
    $(page.body).html(`
        <div class="container-fluid" style="max-width: 900px; margin: 20px auto;">
            <div class="card">
                <div class="card-header">
                    <h4><i class="fa fa-upload"></i> Bulk Import Church Members</h4>
                </div>
                <div class="card-body">
                    <div class="alert alert-info">
                        <strong><i class="fa fa-info-circle"></i> How to Import:</strong>
                        <ol style="margin-top: 10px;">
                            <li>Download the template CSV file below</li>
                            <li>Fill in your church members' details</li>
                            <li>Upload the filled CSV file</li>
                            <li>Click "Import Members"</li>
                        </ol>
                    </div>
                    
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="card bg-light">
                                <div class="card-body text-center">
                                    <h5><i class="fa fa-download text-primary"></i> Step 1: Download Template</h5>
                                    <p class="text-muted">Get the CSV template with all required fields</p>
                                    <button class="btn btn-primary" id="download-template">
                                        <i class="fa fa-download"></i> Download CSV Template
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card bg-light">
                                <div class="card-body text-center">
                                    <h5><i class="fa fa-file-excel text-success"></i> Or Use Data Import</h5>
                                    <p class="text-muted">Use Frappe's built-in Data Import tool</p>
                                    <button class="btn btn-success" id="use-data-import">
                                        <i class="fa fa-arrow-right"></i> Open Data Import
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <hr>
                    
                    <h5><i class="fa fa-upload"></i> Step 2: Upload Your CSV</h5>
                    <div class="form-group">
                        <label>Select CSV File:</label>
                        <input type="file" id="csv-file" class="form-control" accept=".csv">
                        <small class="form-text text-muted">
                            Required columns: full_name, phone_number, branch, status (Active/Inactive)
                        </small>
                    </div>
                    
                    <div id="preview-section" style="display: none;" class="mt-3">
                        <h6>Preview:</h6>
                        <div id="csv-preview" class="table-responsive" style="max-height: 300px; overflow-y: auto;"></div>
                        <p id="row-count" class="text-muted"></p>
                    </div>
                    
                    <div class="mt-4">
                        <button class="btn btn-primary btn-lg" id="import-btn" disabled>
                            <i class="fa fa-upload"></i> Import Members
                        </button>
                    </div>
                    
                    <div id="progress-section" style="display: none;" class="mt-4">
                        <div class="progress" style="height: 25px;">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                 id="progress-bar" style="width: 0%"></div>
                        </div>
                        <p id="progress-text" class="text-center mt-2"></p>
                    </div>
                    
                    <div id="results-section" style="display: none;" class="mt-4">
                        <div class="alert" id="results-alert">
                            <h5 id="results-title"></h5>
                            <div id="results-details"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card mt-4">
                <div class="card-header">
                    <h5><i class="fa fa-info-circle"></i> CSV Format Guide</h5>
                </div>
                <div class="card-body">
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Column</th>
                                <th>Required</th>
                                <th>Example</th>
                                <th>Notes</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><code>full_name</code></td>
                                <td><span class="badge badge-danger">Required</span></td>
                                <td>John Doe</td>
                                <td>Full name of the member</td>
                            </tr>
                            <tr>
                                <td><code>phone_number</code></td>
                                <td><span class="badge badge-danger">Required</span></td>
                                <td>0712345678</td>
                                <td>Phone number (will be auto-formatted to +255...)</td>
                            </tr>
                            <tr>
                                <td><code>branch</code></td>
                                <td><span class="badge badge-warning">Optional</span></td>
                                <td>Mabibo Jeshini</td>
                                <td>Must match an existing Church Branch</td>
                            </tr>
                            <tr>
                                <td><code>status</code></td>
                                <td><span class="badge badge-warning">Optional</span></td>
                                <td>Active</td>
                                <td>Active or Inactive (default: Active)</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `);
    
    // Download template
    $('#download-template').on('click', function() {
        var csv = 'full_name,phone_number,branch,status\nJohn Doe,0712345678,Mabibo Jeshini,Active\nJane Smith,0787654321,Mabibo Farasi,Active\nPeter Johnson,0756789012,,Active';
        var blob = new Blob([csv], { type: 'text/csv' });
        var url = window.URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'church_members_template.csv';
        a.click();
        window.URL.revokeObjectURL(url);
        frappe.show_alert({message: 'Template downloaded!', indicator: 'green'});
    });
    
    // Open Data Import
    $('#use-data-import').on('click', function() {
        frappe.set_route('Form', 'Data Import', 'new-data-import', {
            reference_doctype: 'Church Member'
        });
    });
    
    // CSV file upload
    $('#csv-file').on('change', function(e) {
        var file = e.target.files[0];
        if (!file) return;
        
        var reader = new FileReader();
        reader.onload = function(event) {
            var text = event.target.result;
            var lines = text.split('\n').filter(l => l.trim());
            
            if (lines.length < 2) {
                frappe.msgprint('CSV file is empty or has no data rows');
                return;
            }
            
            var headers = lines[0].split(',').map(h => h.trim());
            var required = ['full_name', 'phone_number'];
            var missing = required.filter(r => !headers.includes(r));
            
            if (missing.length > 0) {
                frappe.msgprint('Missing required columns: ' + missing.join(', '));
                return;
            }
            
            // Preview
            var tableHtml = '<table class="table table-sm table-bordered">';
            tableHtml += '<thead><tr>' + headers.map(h => '<th>' + h + '</th>').join('') + '</tr></thead>';
            tableHtml += '<tbody>';
            
            var maxPreview = Math.min(lines.length - 1, 10);
            for (var i = 1; i <= maxPreview; i++) {
                var cols = lines[i].split(',').map(c => c.trim());
                tableHtml += '<tr>' + cols.map(c => '<td>' + c + '</td>').join('') + '</tr>';
            }
            
            if (lines.length - 1 > 10) {
                tableHtml += '<tr><td colspan="' + headers.length + '" class="text-center text-muted">... and ' + (lines.length - 11) + ' more rows</td></tr>';
            }
            
            tableHtml += '</tbody></table>';
            
            $('#csv-preview').html(tableHtml);
            $('#row-count').text((lines.length - 1) + ' members to import');
            $('#preview-section').show();
            $('#import-btn').prop('disabled', false);
        };
        reader.readAsText(file);
    });
    
    // Import button
    $('#import-btn').on('click', function() {
        var file = $('#csv-file')[0].files[0];
        if (!file) return;
        
        var reader = new FileReader();
        reader.onload = function(event) {
            var text = event.target.result;
            var lines = text.split('\n').filter(l => l.trim());
            var headers = lines[0].split(',').map(h => h.trim());
            
            var rows = [];
            for (var i = 1; i < lines.length; i++) {
                var cols = lines[i].split(',');
                var row = {};
                headers.forEach(function(h, idx) {
                    row[h] = (cols[idx] || '').trim();
                });
                if (row.full_name && row.phone_number) {
                    rows.push(row);
                }
            }
            
            if (rows.length === 0) {
                frappe.msgprint('No valid rows found in CSV');
                return;
            }
            
            // Start import
            $('#import-btn').prop('disabled', true);
            $('#progress-section').show();
            $('#results-section').hide();
            
            import_members(rows, 0, 0, 0);
        };
        reader.readAsText(file);
    });
    
    function import_members(rows, index, success_count, fail_count) {
        if (index >= rows.length) {
            // Done
            var percent = 100;
            $('#progress-bar').css('width', percent + '%').text('Complete!');
            $('#progress-text').text('Import complete!');
            
            var alertClass = fail_count === 0 ? 'alert-success' : 'alert-warning';
            $('#results-alert').removeClass().addClass('alert ' + alertClass);
            $('#results-title').text(fail_count === 0 ? '✅ Import Successful!' : '⚠️ Import Completed with Errors');
            $('#results-details').html(
                '<p><strong>Total:</strong> ' + rows.length + ' members</p>' +
                '<p><strong>Imported:</strong> ' + success_count + '</p>' +
                '<p><strong>Failed:</strong> ' + fail_count + '</p>' +
                '<br><a href="/app/church-member" class="btn btn-primary">View Members</a>'
            );
            $('#results-section').show();
            return;
        }
        
        var row = rows[index];
        var percent = Math.round(((index + 1) / rows.length) * 100);
        $('#progress-bar').css('width', percent + '%').text(percent + '%');
        $('#progress-text').text('Importing ' + (index + 1) + ' of ' + rows.length + ': ' + row.full_name);
        
        frappe.call({
            method: 'church_sms.api.import_member',
            args: {
                full_name: row.full_name,
                phone_number: row.phone_number,
                branch: row.branch || '',
                status: row.status || 'Active'
            },
            callback: function(r) {
                if (r.message && r.message.success) {
                    success_count++;
                } else {
                    fail_count++;
                    console.error('Failed to import:', row.full_name, r.message);
                }
                import_members(rows, index + 1, success_count, fail_count);
            },
            error: function() {
                fail_count++;
                import_members(rows, index + 1, success_count, fail_count);
            }
        });
    }
};
