app_name = "church_sms"
app_title = "Church SMS"
app_publisher = "KODA Systems"
app_description = "Send bulk SMS to church members with personalization, scheduling, and analytics"
app_email = "justinemsengi@gmail.com"
app_license = "MIT"
app_icon = "fa fa-bullhorn"
app_color = "#3498db"

# Apps
# ------------------

# Add to apps screen
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
# ---------------
doc_events = {
    "Church SMS": {
        "validate": "church_sms.api.validate_sms"
    }
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "all": [
        "church_sms.churchsms.doctype.scheduled_sms.scheduled_sms.process_scheduled_sms"
    ]
}

# DocType JS
# ---------------
doctype_js = {
    "Church SMS": "public/js/church_sms.js"
}
