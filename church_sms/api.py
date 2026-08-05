import frappe
import requests
import json
from frappe import _

@frappe.whitelist()
def send_church_sms(send_to, message, sender_id, branch="", members=None):
    """Send SMS to church members via Kilakona API"""
    try:
        # Get SMS settings
        settings = frappe.get_single("Church SMS Settings")
        
        login_id = settings.api_key  # developerbeneth
        password = settings.get_password("api_secret")  # Kilakona@2025#%
        
        if not login_id or not password:
            return {
                "success": False,
                "message": "❌ SMS credentials not configured. Go to Church SMS Settings and set API Key (login ID) and API Secret (password)."
            }
        
        if not sender_id:
            sender_id = settings.default_sender_id or "KKKT MABIBO"
        
        # Get recipients
        phone_numbers = get_recipients(send_to, branch, members)
        
        if not phone_numbers:
            return {
                "success": False,
                "message": "❌ No recipients found for: " + str(send_to) + ". Make sure members have phone numbers and are Active."
            }
        
        # Remove duplicates
        phone_numbers = list(set(phone_numbers))
        
        # Login to get JWT token
        token = get_kilakona_token(login_id, password)
        if not token:
            return {
                "success": False,
                "message": "❌ Failed to authenticate with Kilakona. Check your API Key and API Secret in Church SMS Settings."
            }
        
        # Send SMS
        result = send_sms_via_kilakona(
            token=token,
            sender_id=sender_id,
            phone_numbers=phone_numbers,
            message=message
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": "✅ SMS sent successfully!\n\n" + result.get("details", "") + "\n\nTotal recipients: " + str(len(phone_numbers))
            }
        else:
            return {
                "success": False,
                "message": "❌ Failed to send SMS\n\nError: " + result.get("error", "Unknown error")
            }
            
    except Exception as e:
        error_msg = str(e)
        frappe.log_error(frappe.get_traceback(), "Church SMS Error")
        return {
            "success": False,
            "message": "❌ System Error: " + error_msg + "\n\nCheck Error Log for details."
        }


def get_kilakona_token(login_id, password):
    """Login to Kilakona and get JWT token"""
    try:
        url = "https://messaging.kilakona.co.tz/api/v1/auth/login"
        payload = {
            "loginId": login_id,
            "password": password
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data", {}).get("token"):
                return data["data"]["token"]
        
        return None
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Kilakona Login Error")
        return None


def get_recipients(send_to, branch="", members=None):
    """Get phone numbers based on send_to criteria"""
    phone_numbers = []
    
    if send_to == "All Members":
        members_list = frappe.get_all(
            "Church Member",
            filters={"status": "Active"},
            fields=["full_name", "phone_number"]
        )
        for member in members_list:
            if member.phone_number:
                formatted = format_phone(member.phone_number)
                if formatted:
                    phone_numbers.append(formatted)
                
    elif send_to == "Specific Branch" and branch:
        members_list = frappe.get_all(
            "Church Member",
            filters={"status": "Active", "branch": branch},
            fields=["full_name", "phone_number"]
        )
        for member in members_list:
            if member.phone_number:
                formatted = format_phone(member.phone_number)
                if formatted:
                    phone_numbers.append(formatted)
                
    elif send_to == "Specific Members" and members:
        if isinstance(members, str):
            members = json.loads(members)
        
        for member_data in members:
            phone = member_data.get("phone")
            if phone:
                formatted = format_phone(phone)
                if formatted:
                    phone_numbers.append(formatted)
    
    return [p for p in phone_numbers if p]


def format_phone(phone):
    """Format phone number for Kilakona (keep as-is, they handle formatting)"""
    if not phone:
        return None
    
    phone = str(phone).strip()
    phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Remove + if present
    if phone.startswith("+"):
        phone = phone[1:]
    
    # Validate minimum length
    if len(phone) < 9:
        return None
    
    return phone


def send_sms_via_kilakona(token, sender_id, phone_numbers, message):
    """Send SMS via Kilakona API"""
    try:
        url = "https://messaging.kilakona.co.tz/api/v1/users/message/send"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Format contacts as comma-separated string
        contacts = ",".join(phone_numbers)
        
        payload = {
            "senderId": sender_id,
            "messageType": "text",
            "message": message,
            "contacts": contacts
        }
        
        # Log the request
        frappe.logger().info(f"Church SMS: Sending to {len(phone_numbers)} recipients via Kilakona")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                data = result.get("data", {})
                valid = data.get("validContacts", 0)
                invalid = data.get("invalidContacts", 0)
                shoot_id = data.get("shootId", "")
                
                details = f"✅ Sent: {valid}"
                if invalid > 0:
                    details += f"\n❌ Invalid numbers: {invalid}"
                if shoot_id:
                    details += f"\n📋 Message ID: {shoot_id}"
                
                return {
                    "success": True,
                    "details": details,
                    "response": result
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error from Kilakona")
                }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text[:200]}"
            }
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timeout (30 seconds)"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to Kilakona API"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Kilakona SMS Error")
        return {"success": False, "error": str(e)}


def validate_sms(doc, method):
    """Validate Church SMS before save"""
    if not doc.message:
        frappe.throw(_("Please enter a message"))


def check_app_permission():
    """Check if user has permission to see the app"""
    return True
