app_name = "church_sms"
app_title = "Church SMS"
app_publisher = "KODA Systems"
app_description = "Church SMS Management - Send bulk SMS to church members via Kilakona"
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
    "Church SMS": "public/js/church_sms.js",
    "Church SMS Settings": "public/js/church_sms_settings.js"
}

# DocType List JS
doctype_list_js = {
    "Church Member": "public/js/church_member_list.js"
}
