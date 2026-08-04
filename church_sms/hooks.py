app_name = "church_sms"
app_title = "Church SMS"
app_publisher = "KODA Systems"
app_description = "Church SMS Management - Send bulk SMS to church members"
app_email = "justinemsengi@gmail.com"
app_license = "MIT"
required_apps = ["frappe"]

# Document Events
doc_events = {
    "Church SMS": {
        "validate": "church_sms.api.validate_sms",
    }
}

# DocType JS
doctype_js = {
    "Church SMS": "public/js/church_sms.js"
}

# Fixtures - export workspace
fixtures = [
    {
        "dt": "Workspace",
        "filters": [["name", "=", "Church SMS"]]
    }
]
