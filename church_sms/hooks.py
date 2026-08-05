app_name = "church_sms"
app_title = "Church SMS"
app_publisher = "KODA Systems"
app_description = "Church SMS Management - Send bulk SMS to church members"
app_email = "justinemsengi@gmail.com"
app_license = "MIT"
required_apps = ["frappe"]

# Apps page / home
add_to_apps_screen = [
    {
        "name": "church_sms",
        "logo": "/assets/church_sms/images/church_sms_logo.png",
        "title": "Church SMS",
        "route": "/app/church-sms",
        "has_permission": "church_sms.api.check_app_permission"
    }
]

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
