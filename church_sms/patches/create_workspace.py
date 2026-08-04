import frappe

def execute():
    """Create Church SMS workspace programmatically"""
    
    # Check if workspace already exists
    if frappe.db.exists("Workspace", "Church SMS"):
        return
    
    # Create the workspace
    workspace = frappe.new_doc("Workspace")
    workspace.label = "Church SMS"
    workspace.name = "Church SMS"
    workspace.icon = "broadcast"
    workspace.module = "ChurchSMS"
    workspace.public = 1
    workspace.is_default = 0
    workspace.sequence_id = 1
    
    # Add content blocks
    workspace.content = """[
        {"id": "header_1", "type": "header", "data": {"text": "<span class=\"h4\"><b>Church SMS</b></span>", "col": 12}},
        {"id": "paragraph_1", "type": "paragraph", "data": {"text": "Send bulk SMS to church members, manage contacts and track delivery.", "col": 12}},
        {"id": "shortcut_1", "type": "shortcut", "data": {"shortcut_name": "New SMS", "col": 3}},
        {"id": "shortcut_2", "type": "shortcut", "data": {"shortcut_name": "Church Members", "col": 3}},
        {"id": "shortcut_3", "type": "shortcut", "data": {"shortcut_name": "SMS Settings", "col": 3}},
        {"id": "shortcut_4", "type": "shortcut", "data": {"shortcut_name": "Import Members", "col": 3}},
        {"id": "spacer_1", "type": "spacer", "data": {"col": 12}},
        {"id": "shortcut_5", "type": "shortcut", "data": {"shortcut_name": "All SMS History", "col": 4}},
        {"id": "shortcut_6", "type": "shortcut", "data": {"shortcut_name": "Church Branches", "col": 4}},
        {"id": "shortcut_7", "type": "shortcut", "data": {"shortcut_name": "Data Import", "col": 4}}
    ]"""
    
    # Add shortcuts
    workspace.append("shortcuts", {
        "label": "New SMS",
        "link_to": "Church SMS",
        "type": "DocType",
        "doc_view": "New",
        "color": "Blue"
    })
    workspace.append("shortcuts", {
        "label": "Church Members",
        "link_to": "Church Member",
        "type": "DocType",
        "doc_view": "List",
        "color": "Green",
        "stats_filter": '[["Church Member","status","=","Active"]]',
        "format": "{} Active"
    })
    workspace.append("shortcuts", {
        "label": "SMS Settings",
        "link_to": "Church SMS Settings",
        "type": "DocType",
        "doc_view": ""
    })
    workspace.append("shortcuts", {
        "label": "Import Members",
        "link_to": "import-members",
        "type": "Page"
    })
    workspace.append("shortcuts", {
        "label": "All SMS History",
        "link_to": "Church SMS",
        "type": "DocType",
        "doc_view": "List",
        "color": "Grey"
    })
    workspace.append("shortcuts", {
        "label": "Church Branches",
        "link_to": "Church Branch",
        "type": "DocType",
        "doc_view": "List"
    })
    workspace.append("shortcuts", {
        "label": "Data Import",
        "link_to": "Data Import",
        "type": "DocType",
        "doc_view": "List"
    })
    
    # Add links (sidebar items)
    workspace.append("links", {
        "label": "SMS Campaigns",
        "link_to": "Church SMS",
        "link_type": "DocType",
        "type": "Link",
        "onboard": 1
    })
    workspace.append("links", {
        "label": "Church Members",
        "link_to": "Church Member",
        "link_type": "DocType",
        "type": "Link",
        "onboard": 1
    })
    workspace.append("links", {
        "label": "Church Branches",
        "link_to": "Church Branch",
        "link_type": "DocType",
        "type": "Link",
        "onboard": 1
    })
    workspace.append("links", {
        "label": "SMS Settings",
        "link_to": "Church SMS Settings",
        "link_type": "DocType",
        "type": "Link",
        "onboard": 1
    })
    
    workspace.insert(ignore_permissions=True, ignore_if_duplicate=True)
    frappe.db.commit()
    
    print("Church SMS workspace created successfully!")
