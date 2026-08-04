import frappe
import requests
import json
from frappe import _

@frappe.whitelist()
def send_church_sms(send_to, message, sender_id, branch="", members=None):
    """
    Send SMS to church members via Africa's Talking API
    
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
        
        # In Church SMS Settings:
        # api_key = username (e.g. "developerbeneth")
        # api_secret = actual API key (e.g. "VBGBW1HNk3tBYT0nSqu0")
        username = settings.api_key  # "developerbeneth"
        api_key = settings.get_password("api_secret")  # "VBGBW1HNk3tBYT0nSqu0"
        
        if not username or not api_key:
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
                "message": "No recipients found for: " + str(send_to)
            }
        
        # Remove duplicates
        phone_numbers = list(set(phone_numbers))
        
        # Send SMS via Africa's Talking API
        result = send_sms_via_at(
            username=username,
            api_key=api_key,
            sender_id=sender_id,
            phone_numbers=phone_numbers,
            message=message
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": "SMS sent successfully to " + str(len(phone_numbers)) + " recipients. " + result.get("details", "")
            }
        else:
            return {
                "success": False,
                "message": "Failed to send SMS: " + result.get("error", "Unknown error")
            }
            
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Church SMS Error")
        return {
            "success": False,
            "message": "Error: " + str(e)
        }


def get_recipients(send_to, branch="", members=None):
    """Get phone numbers based on send_to criteria"""
    phone_numbers = []
    
    if send_to == "All Members":
        members_list = frappe.get_all(
            "Church Member",
            filters={"status": "Active"},
            fields=["phone_number"]
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
            fields=["phone_number"]
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
    """Format phone number to international format (+255...)"""
    if not phone:
        return None
    
    phone = str(phone).strip()
    phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    if phone.startswith("+"):
        phone = phone[1:]
    
    if phone.startswith("0"):
        phone = "255" + phone[1:]
    elif not phone.startswith("255") and len(phone) >= 9:
        phone = "255" + phone
    
    # Validate - should be 12 digits for Tanzania
    if len(phone) < 11:
        return None
    
    return "+" + phone


def send_sms_via_at(username, api_key, sender_id, phone_numbers, message):
    """
    Send SMS via Africa's Talking API
    
    Africa's Talking SMS API:
    - Endpoint: https://api.africastalking.com/version1/messaging
    - Header: apiKey = your API key
    - Body: username = your account username
    - Body: to = comma-separated phone numbers
    - Body: message = SMS text
    - Body: from = sender ID (optional, must be registered)
    """
    try:
        url = "https://api.africastalking.com/version1/messaging"
        
        # Format recipients
        recipients = ",".join(phone_numbers)
        
        # Headers - apiKey goes here
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "apiKey": api_key  # This is the actual API key from api_secret field
        }
        
        # Payload
        payload = {
            "username": username,  # This is the username from api_key field
            "to": recipients,
            "message": message,
        }
        
        # Only add sender ID if provided (must be registered with Africa's Talking)
        if sender_id:
            payload["from"] = sender_id
        
        # Log for debugging
        frappe.logger().info(f"Church SMS: Sending to {len(phone_numbers)} recipients via Africa's Talking")
        frappe.logger().info(f"Church SMS: Username={username}, Recipients={recipients}")
        
        # Make request
        response = requests.post(url, data=payload, headers=headers, timeout=30)
        
        # Log response
        frappe.logger().info(f"Church SMS: Response {response.status_code}: {response.text}")
        
        if response.status_code in [200, 201]:
            try:
                result = response.json()
            except:
                result = {"raw": response.text}
            
            # Parse Africa's Talking response
            if "SMSMessageData" in result:
                sms_data = result["SMSMessageData"]
                recipients_data = sms_data.get("Recipients", [])
                
                sent_count = 0
                failed_count = 0
                
                for r in recipients_data:
                    status_code = r.get("statusCode")
                    if status_code in [100, 101, 102]:
                        sent_count += 1
                    else:
                        failed_count += 1
                
                details = "Sent: " + str(sent_count)
                if failed_count > 0:
                    details += ", Failed: " + str(failed_count)
                
                # Include any error messages from failed recipients
                for r in recipients_data:
                    if r.get("statusCode") not in [100, 101, 102]:
                        err = r.get("status", "")
                        if err:
                            details += " | Error: " + str(err)
                            break
                
                return {
                    "success": sent_count > 0,
                    "details": details,
                    "response": result
                }
            else:
                return {
                    "success": True,
                    "details": "SMS queued. Response: " + str(result)[:200],
                    "response": result
                }
        else:
            return {
                "success": False,
                "error": "HTTP " + str(response.status_code) + ": " + response.text[:300]
            }
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "API request timeout (30s)"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to Africa's Talking API"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Church SMS API Error")
        return {"success": False, "error": str(e)}


def validate_sms(doc, method):
    """Validate Church SMS before save"""
    if not doc.message:
        frappe.throw(_("Please enter a message"))
