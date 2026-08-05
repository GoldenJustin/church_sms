import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_fields = {
        "Church SMS": [
            {
                "fieldname": "manual_numbers",
                "label": "Manual Phone Numbers",
                "fieldtype": "Small Text",
                "insert_after": "branch",
                "description": "Enter phone numbers separated by commas or new lines (e.g., 0748121608, 0712345678)",
                "depends_on": 'eval:doc.send_to=="Manual Numbers"',
                "mandatory_depends_on": 'eval:doc.send_to=="Manual Numbers"'
            }
        ]
    }
    
    create_custom_fields(custom_fields)
    
    # Update send_to options
    docfield = frappe.get_doc("DocField", {
        "parent": "Church SMS",
        "fieldname": "send_to"
    })
    
    if docfield:
        docfield.options = "\nAll Members\nSpecific Branch\nSpecific Members\nManual Numbers"
        docfield.save()
    
    frappe.db.commit()
    print("✅ Added manual_numbers field to Church SMS")
