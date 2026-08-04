from frappe import _

def get_data():
    return [
        {
            "module_name": "Church SMS",
            "color": "blue",
            "icon": "octicon octicon-broadcast",
            "type": "module",
            "label": _("Church SMS"),
            "description": _("Send bulk SMS to church members")
        }
    ]
