import frappe
import requests
import json
from frappe import _

@frappe.whitelist()
def send_church_sms(send_to, message, sender_id, branch="", members=None):
    """
    Send SMS to church members
    
    Args:
        send_to: "All Members", "Specific Branch", or "Specific Members"
        message: SMS message text
        sender_id: Sender ID to display
        branch: Branch name (if send_to is "Specific Branch")
        members: List of member dicts (if send_to is "Specific Members")
    
    Returns:
        dict: {"success": bool, "message": str}
    """
    try:
        # Get SMS settings
        settings = frappe.get_single("Church SMS Settings")
        api_key = settings.api_key
        api_secret = settings.get_password("api_secret")
        
        if not api_key or not api_secret:
            return {
                "success": False,
                "message": "SMS API credentials not configured in Church SMS Settings"
            }
        
        if not sender_id:
            sender_id = settings.default_sender_id or "KKKT MABIBO"
        
        # Get recipients based on send_to
        phone_numbers = get_recipients(send_to, branch, members)
        
        if not phone_numbers:
            return {
                "success": False,
                "message": f"No recipients found for: {send_to}"
            }
        
        # Remove duplicates
        phone_numbers = list(set(phone_numbers))
        
        # Send SMS via API (Africa's Talking style)
        result = send_sms_via_api(
            api_key=api_key,
            api_secret=api_secret,
            sender_id=sender_id,
            phone_numbers=phone_numbers,
            message=message
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": f"SMS sent successfully to {len(phone_numbers)} recipients. {result.get('details', '')}"
            }
        else:
            return {
                "success": False,
                "message": f"Failed to send SMS: {result.get('error', 'Unknown error')}"
            }
            
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Church SMS Error")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def get_recipients(send_to, branch="", members=None):
    """Get phone numbers based on send_to criteria"""
    phone_numbers = []
    
    if send_to == "All Members":
        # Get all active members
        members_list = frappe.get_all(
            "Church Member",
            filters={"status": "Active"},
            fields=["phone_number"]
        )
        for member in members_list:
            if member.phone_number:
                phone_numbers.append(format_phone(member.phone_number))
                
    elif send_to == "Specific Branch" and branch:
        # Get members from specific branch
        members_list = frappe.get_all(
            "Church Member",
            filters={"status": "Active", "branch": branch},
            fields=["phone_number"]
        )
        for member in members_list:
            if member.phone_number:
                phone_numbers.append(format_phone(member.phone_number))
                
    elif send_to == "Specific Members" and members:
        # Use provided members list
        if isinstance(members, str):
            members = json.loads(members)
        
        for member_data in members:
            phone = member_data.get("phone")
            if phone:
                phone_numbers.append(format_phone(phone))
    
    return [p for p in phone_numbers if p]  # Remove empty values


def format_phone(phone):
    """Format phone number to international format"""
    if not phone:
        return None
    
    # Remove spaces, dashes, parentheses
    phone = str(phone).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Add country code if missing (Tanzania default)
    if phone.startswith("0"):
        phone = "255" + phone[1:]
    elif phone.startswith("+"):
        phone = phone[1:]
    elif not phone.startswith("255") and len(phone) == 9:
        phone = "255" + phone
    
    return phone


def send_sms_via_api(api_key, api_secret, sender_id, phone_numbers, message):
    """
    Send SMS via Africa's Talking or similar API
    
    This is a generic implementation that works with Africa's Talking style APIs.
    Adjust the endpoint and parameters based on your actual SMS provider.
    """
    try:
        # Africa's Talking SMS API endpoint
        # Note: Adjust this URL based on your actual SMS provider
        url = "https://api.africastalking.com/version1/messaging"
        
        # Prepare recipients (comma-separated for bulk)
        recipients = ",".join(phone_numbers)
        
        # Headers
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "apiKey": api_key
        }
        
        # Payload
        payload = {
            "username": api_secret,  # Africa's Talking uses username
            "to": recipients,
            "message": message,
            "from": sender_id
        }
        
        # Make request
        response = requests.post(url, data=payload, headers=headers, timeout=30)
        
        if response.status_code == 201 or response.status_code == 200:
            result = response.json()
            
            # Check if messages were sent
            if "SMSMessageData" in result:
                sms_data = result["SMSMessageData"]
                recipients_data = sms_data.get("Recipients", [])
                
                sent_count = len([r for r in recipients_data if r.get("statusCode") in [100, 101, 102]])
                failed_count = len(recipients_data) - sent_count
                
                return {
                    "success": True,
                    "details": f"Sent: {sent_count}, Failed: {failed_count}",
                    "response": result
                }
            else:
                return {
                    "success": True,
                    "details": "SMS queued successfully",
                    "response": result
                }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "API request timeout"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "API connection error"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def validate_sms(doc, method):
    """Validate Church SMS before save"""
    if not doc.message:
        frappe.throw(_("Please enter a message"))
    
    if len(doc.message) > 160 and not doc.message:
        frappe.msgprint(
            _("Message exceeds 160 characters and will be sent as multiple SMS segments"),
            indicator="orange"
        )
