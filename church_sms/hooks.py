app_name = "church_sms"
app_title = "Church SMS"
app_publisher = "KODA Systems"
app_description = "Send bulk SMS to church members with personalization, scheduling, and analytics"
app_email = "justinemsengi@gmail.com"
app_license = "MIT"
app_icon = "octicon octicon-broadcast"
app_color = "#3498db"

# Apps
# ------------------

# Include app in home page
app_include_css = "/assets/church_sms/css/church_sms.css"

# Add to apps screen
add_to_apps_screen = [
    {
        "name": "church_sms",
        "logo": "/assets/church_sms/images/church_sms_logo.png",
        "title": "Church SMS",
        "route": "/app/sms-dashboard",
        "has_permission": "church_sms.api.check_app_permission"
    }
]

# Website
# -------

# Generators
# ----------

# DocType Class
# ---------------
# Override standard doctype classes

# Permissions
# -----------
# Permissions evaluated in scripted ways

# Document Events
# ---------------
# Hook on document methods and events

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

# Testing
# -------

# before_tests = "church_sms.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "church_sms.event.get_events"
# }
#
# each overriding function accepts a `data` argument
# that is the data being processed, and should return
# the processed data

# Exceptions
# ----------
# List of exceptions to ignore during hooks

# Override Standard Doctype
# -------------------------

# Fixtures
# --------
# List of fixtures to export

# Jinja
# ----------

# add methods and filters to jinja environment

# Installation
# ------------

# before_install = "church_sms.install.before_install"
# after_install = "church_sms.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# Permissions
# -----------
# Permissions evaluated in scripted ways

# DocType JS
# ---------------
# doctype_js = {"Church SMS": "public/js/church_sms.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "church_sms.utils.jinja_methods",
# 	"filters": "church_sms.utils.jinja_filters"
# }
