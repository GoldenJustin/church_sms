import frappe
import requests
import json
from frappe import _
from datetime import datetime, timedelta

@frappe.whitelist()
def send_church_sms(send_to, message, sender_id, branch="", members=None):
    """Send SMS to church members via Kilakona API with personalization"""
    try:
        settings = frappe.get_single("Church SMS Settings")
        
        login_id = settings.api_key
        password = settings.get_password("api_secret")
        
        if not login_id or not password:
            return {
                "success": False,
                "message": "❌ SMS credentials not configured in Church SMS Settings."
            }
        
        if not sender_id:
            sender_id = settings.default_sender_id or "KKKT MABIBO"
        
        # Get recipients with their details for personalization
        recipients = get_recipients_with_details(send_to, branch, members)
        
        if not recipients:
            return {
                "success": False,
                "message": "❌ No recipients found."
            }
        
        # Login to get JWT token
        token = get_kilakona_token(login_id, password)
        if not token:
            return {
                "success": False,
                "message": "❌ Failed to authenticate with Kilakona."
            }
        
        # Send personalized SMS to each recipient
        total_sent = 0
        total_failed = 0
        errors = []
        
        for recipient in recipients:
            # Personalize message
            personalized_message = personalize_message(message, recipient)
            
            result = send_single_sms(
                token=token,
                sender_id=sender_id,
                phone=recipient["phone"],
                message=personalized_message
            )
            
            if result.get("success"):
                total_sent += 1
            else:
                total_failed += 1
                errors.append(f"{recipient['name']}: {result.get('error', 'Unknown')}")
        
        details = f"✅ Sent: {total_sent}"
        if total_failed > 0:
            details += f"\n❌ Failed: {total_failed}"
            if errors:
                details += f"\n\nErrors:\n" + "\n".join(errors[:5])
        
        return {
            "success": total_sent > 0,
            "message": details
        }
            
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Church SMS Error")
        return {
            "success": False,
            "message": "❌ Error: " + str(e)
        }


def personalize_message(message, recipient):
    """Replace template variables with recipient details"""
    personalized = message
    
    # Replace {{name}} or {{member_name}} with full name
    if "{{name}}" in personalized or "{{member_name}}" in personalized:
        name = recipient.get("name", "")
        personalized = personalized.replace("{{name}}", name)
        personalized = personalized.replace("{{member_name}}", name)
    
    # Replace {{phone}} with phone number
    if "{{phone}}" in personalized:
        personalized = personalized.replace("{{phone}}", recipient.get("phone", ""))
    
    # Replace {{branch}} with branch name
    if "{{branch}}" in personalized:
        personalized = personalized.replace("{{branch}}", recipient.get("branch", ""))
    
    return personalized


def get_recipients_with_details(send_to, branch="", members=None):
    """Get recipients with full details for personalization"""
    recipients = []
    
    if send_to == "All Members":
        members_list = frappe.get_all(
            "Church Member",
            filters={"status": "Active"},
            fields=["name", "full_name", "phone_number", "branch"]
        )
        for member in members_list:
            if member.phone_number:
                phone = format_phone(member.phone_number)
                if phone:
                    recipients.append({
                        "name": member.full_name or member.name,
                        "phone": phone,
                        "branch": member.branch or ""
                    })
                
    elif send_to == "Specific Branch" and branch:
        members_list = frappe.get_all(
            "Church Member",
            filters={"status": "Active", "branch": branch},
            fields=["name", "full_name", "phone_number", "branch"]
        )
        for member in members_list:
            if member.phone_number:
                phone = format_phone(member.phone_number)
                if phone:
                    recipients.append({
                        "name": member.full_name or member.name,
                        "phone": phone,
                        "branch": member.branch or ""
                    })
                
    elif send_to == "Specific Members" and members:
        if isinstance(members, str):
            members = json.loads(members)
        
        for member_data in members:
            phone = member_data.get("phone")
            if phone:
                phone = format_phone(phone)
                if phone:
                    recipients.append({
                        "name": member_data.get("member_name", ""),
                        "phone": phone,
                        "branch": ""
                    })
    
    return recipients


def get_kilakona_token(login_id, password):
    """Login to Kilakona and get JWT token"""
    try:
        url = "https://messaging.kilakona.co.tz/api/v1/auth/login"
        payload = {"loginId": login_id, "password": password}
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data", {}).get("token"):
                return data["data"]["token"]
        return None
    except:
        return None


def send_single_sms(token, sender_id, phone, message):
    """Send single SMS via Kilakona API"""
    try:
        url = "https://messaging.kilakona.co.tz/api/v1/users/message/send"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "senderId": sender_id,
            "messageType": "text",
            "message": message,
            "contacts": phone
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return {"success": True, "shoot_id": result.get("data", {}).get("shootId")}
            else:
                return {"success": False, "error": result.get("message", "Failed")}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def format_phone(phone):
    """Format phone number"""
    if not phone:
        return None
    phone = str(phone).strip().replace(" ", "").replace("-", "")
    if phone.startswith("+"):
        phone = phone[1:]
    return phone if len(phone) >= 9 else None


@frappe.whitelist()
def get_sms_balance():
    """Get SMS balance from Kilakona"""
    try:
        settings = frappe.get_single("Church SMS Settings")
        login_id = settings.api_key
        password = settings.get_password("api_secret")
        
        token = get_kilakona_token(login_id, password)
        if not token:
            return {"success": False, "error": "Authentication failed"}
        
        # Try to get balance (endpoint might vary)
        url = "https://messaging.kilakona.co.tz/api/v1/users/balance"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {"success": True, "balance": data.get("data", {}).get("balance", "N/A")}
        
        return {"success": False, "error": "Could not fetch balance"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_sms_statistics():
    """Get SMS statistics for dashboard"""
    try:
        # Get total SMS sent
        total_sms = frappe.db.count("Church SMS")
        
        # Get by status
        sent = frappe.db.count("Church SMS", {"status": "Sent"})
        failed = frappe.db.count("Church SMS", {"status": "Failed"})
        draft = frappe.db.count("Church SMS", {"status": "Draft"})
        
        # Get recent campaigns
        recent = frappe.get_all(
            "Church SMS",
            fields=["name", "creation", "status", "send_to"],
            order_by="creation desc",
            limit=5
        )
        
        # Get member count
        total_members = frappe.db.count("Church Member", {"status": "Active"})
        
        return {
            "success": True,
            "stats": {
                "total_sms": total_sms,
                "sent": sent,
                "failed": failed,
                "draft": draft,
                "total_members": total_members
            },
            "recent_campaigns": recent
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def validate_sms(doc, method):
    """Validate Church SMS before save"""
    if not doc.message:
        frappe.throw(_("Please enter a message"))


def check_app_permission():
    """Check if user has permission to see the app"""
    return True
