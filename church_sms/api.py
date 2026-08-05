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
        
        username = settings.api_key  # developerbeneth
        password = settings.get_password("api_secret")  # Should be: Kilakona@2025#%
        
        if not username or not password:
            return {
                "success": False,
                "message": "❌ SMS API credentials not configured. Go to Church SMS Settings and set API Key (username) and API Secret (password)."
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
        
        # Send SMS via Kilakona (try multiple methods)
        result = send_sms_via_kilakona(
            username=username,
            password=password,
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
            error_detail = result.get("error", "Unknown error")
            return {
                "success": False,
                "message": "❌ Failed to send SMS\n\nError: " + error_detail
            }
            
    except Exception as e:
        error_msg = str(e)
        frappe.log_error(frappe.get_traceback(), "Church SMS Error")
        return {
            "success": False,
            "message": "❌ System Error: " + error_msg + "\n\nCheck Error Log for details."
        }


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
    """Format phone number - keep as-is for Kilakona (they handle formatting)"""
    if not phone:
        return None
    
    phone = str(phone).strip()
    phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Remove + if present (most SMS gateways don't need it)
    if phone.startswith("+"):
        phone = phone[1:]
    
    # Keep the number as-is (let Kilakona handle country codes)
    if len(phone) < 9:
        return None
    
    return phone


def send_sms_via_kilakona(username, password, sender_id, phone_numbers, message):
    """
    Send SMS via Kilakona API
    Try multiple common authentication and request patterns
    """
    
    # Log the attempt
    frappe.log_error(
        title="Church SMS - Kilakona Attempt",
        message=f"Username: {username}\nRecipients: {len(phone_numbers)}\nSender: {sender_id}\nMessage: {message[:100]}"
    )
    
    # Try Method 1: Basic Auth with JSON
    result = try_kilakona_method1(username, password, sender_id, phone_numbers, message)
    if result.get("success"):
        return result
    
    # Try Method 2: Form POST with credentials in body
    result = try_kilakona_method2(username, password, sender_id, phone_numbers, message)
    if result.get("success"):
        return result
    
    # Try Method 3: GET request with query params
    result = try_kilakona_method3(username, password, sender_id, phone_numbers, message)
    if result.get("success"):
        return result
    
    # All methods failed
    return {
        "success": False,
        "error": "All authentication methods failed. Please verify:\n1. Username is correct\n2. Password is correct\n3. Account has SMS credits\n4. Sender ID is registered\n\nCheck Error Log for detailed responses."
    }


def try_kilakona_method1(username, password, sender_id, phone_numbers, message):
    """Method 1: Basic Auth with JSON POST"""
    try:
        import base64
        url = "http://sms.kilakona.co.tz/api/sendsms"
        
        auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_string}"
        }
        
        payload = {
            "username": username,
            "password": password,
            "sender": sender_id,
            "message": message,
            "phones": ",".join(phone_numbers)
        }
        
        frappe.log_error(
            title="Church SMS - Method 1 (Basic Auth JSON)",
            message=f"URL: {url}\nPayload: {json.dumps(payload)}"
        )
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        frappe.log_error(
            title="Church SMS - Method 1 Response",
            message=f"Status: {response.status_code}\nResponse: {response.text}"
        )
        
        if response.status_code in [200, 201]:
            return {
                "success": True,
                "details": f"Sent to {len(phone_numbers)} recipients via Kilakona (Method 1)",
                "response": response.text
            }
        
        return {"success": False, "error": f"Method 1 failed: HTTP {response.status_code}"}
        
    except Exception as e:
        frappe.log_error(title="Church SMS - Method 1 Error", message=str(e))
        return {"success": False, "error": f"Method 1 error: {str(e)}"}


def try_kilakona_method2(username, password, sender_id, phone_numbers, message):
    """Method 2: Form POST with credentials in body"""
    try:
        url = "http://sms.kilakona.co.tz/api/sendsms"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        payload = {
            "username": username,
            "password": password,
            "sender": sender_id,
            "message": message,
            "numbers": ",".join(phone_numbers)
        }
        
        frappe.log_error(
            title="Church SMS - Method 2 (Form POST)",
            message=f"URL: {url}\nPayload: {payload}"
        )
        
        response = requests.post(url, data=payload, headers=headers, timeout=30)
        
        frappe.log_error(
            title="Church SMS - Method 2 Response",
            message=f"Status: {response.status_code}\nResponse: {response.text}"
        )
        
        if response.status_code in [200, 201]:
            return {
                "success": True,
                "details": f"Sent to {len(phone_numbers)} recipients via Kilakona (Method 2)",
                "response": response.text
            }
        
        return {"success": False, "error": f"Method 2 failed: HTTP {response.status_code}"}
        
    except Exception as e:
        frappe.log_error(title="Church SMS - Method 2 Error", message=str(e))
        return {"success": False, "error": f"Method 2 error: {str(e)}"}


def try_kilakona_method3(username, password, sender_id, phone_numbers, message):
    """Method 3: GET request with query parameters"""
    try:
        url = "http://sms.kilakona.co.tz/api/sendsms"
        
        params = {
            "username": username,
            "password": password,
            "sender": sender_id,
            "message": message,
            "mobiles": ",".join(phone_numbers)
        }
        
        frappe.log_error(
            title="Church SMS - Method 3 (GET)",
            message=f"URL: {url}\nParams: {params}"
        )
        
        response = requests.get(url, params=params, timeout=30)
        
        frappe.log_error(
            title="Church SMS - Method 3 Response",
            message=f"Status: {response.status_code}\nResponse: {response.text}"
        )
        
        if response.status_code in [200, 201]:
            return {
                "success": True,
                "details": f"Sent to {len(phone_numbers)} recipients via Kilakona (Method 3)",
                "response": response.text
            }
        
        return {"success": False, "error": f"Method 3 failed: HTTP {response.status_code}"}
        
    except Exception as e:
        frappe.log_error(title="Church SMS - Method 3 Error", message=str(e))
        return {"success": False, "error": f"Method 3 error: {str(e)}"}


def validate_sms(doc, method):
    """Validate Church SMS before save"""
    if not doc.message:
        frappe.throw(_("Please enter a message"))


def check_app_permission():
    """Check if user has permission to see the app"""
    return True


@frappe.whitelist()
def update_sms_password(new_password):
    """Update the API Secret (password) in Church SMS Settings"""
    settings = frappe.get_single("Church SMS Settings")
    settings.api_secret = new_password
    settings.save(ignore_permissions=True)
    return {"success": True, "message": "Password updated successfully"}


@frappe.whitelist()
def bulk_delete_members(member_names):
    """Bulk delete church members"""
    if isinstance(member_names, str):
        member_names = json.loads(member_names)
    
    deleted = 0
    errors = []
    
    for name in member_names:
        try:
            frappe.delete_doc("Church Member", name, ignore_permissions=True)
            deleted += 1
        except Exception as e:
            errors.append(f"{name}: {str(e)}")
    
    return {
        "deleted": deleted,
        "errors": errors,
        "message": f"Deleted {deleted} members. {len(errors)} errors." if errors else f"Successfully deleted {deleted} members."
    }


@frappe.whitelist()
def bulk_update_members(member_names, field, value):
    """Bulk update a field for multiple church members"""
    if isinstance(member_names, str):
        member_names = json.loads(member_names)
    
    updated = 0
    errors = []
    
    for name in member_names:
        try:
            frappe.db.set_value("Church Member", name, field, value)
            updated += 1
        except Exception as e:
            errors.append(f"{name}: {str(e)}")
    
    frappe.db.commit()
    
    return {
        "updated": updated,
        "errors": errors,
        "message": f"Updated {updated} members." + (f" {len(errors)} errors." if errors else "")
    }


@frappe.whitelist()
def test_kilakona_connection():
    """Test Kilakona API connection with detailed logging"""
    settings = frappe.get_single("Church SMS Settings")
    username = settings.api_key
    password = settings.get_password("api_secret")
    
    result = []
    result.append(f"**Settings:**")
    result.append(f"- Username: `{username}`")
    result.append(f"- Password: `{'*' * (len(password) - 4)}{password[-4:] if password else 'NOT SET'}`")
    result.append(f"- Sender ID: `{settings.default_sender_id}`")
    result.append("")
    
    if not username or not password:
        return {"success": False, "message": "❌ Credentials not set"}
    
    # Try to connect
    try:
        # Test with a simple request
        url = "http://sms.kilakona.co.tz/api/sendsms"
        
        import base64
        auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
        
        # Test with minimal params
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_string}"
        }
        
        # Try balance check or auth check
        test_url = "http://sms.kilakona.co.tz/api/balance"
        response = requests.get(test_url, headers=headers, timeout=10)
        
        result.append(f"**Balance Check:**")
        result.append(f"- Status: {response.status_code}")
        result.append(f"- Response: {response.text[:300]}")
        
        if response.status_code == 200:
            result.append("✅ **Connection successful!**")
            return {"success": True, "message": "\n".join(result)}
        
        # Try alternative endpoints
        test_urls = [
            "http://sms.kilakona.co.tz/api/getbalance",
            "http://sms.kilakona.co.tz/api/checkbalance",
            "http://sms.kilakona.co.tz/api/auth",
            "http://sms.kilakona.co.tz/api/userinfo",
            "http://sms.kilakona.co.tz/app/api/balance",
        ]
        
        for test_url in test_urls:
            try:
                resp = requests.get(test_url, headers=headers, timeout=5)
                result.append(f"- {test_url}: HTTP {resp.status_code} - {resp.text[:100]}")
                if resp.status_code == 200:
                    result.append(f"✅ **Found working endpoint: {test_url}**")
                    return {"success": True, "message": "\n".join(result)}
            except:
                result.append(f"- {test_url}: Connection failed")
        
        result.append("")
        result.append("❌ All connection tests failed")
        result.append("Please verify credentials at sms.kilakona.co.tz")
        
    except Exception as e:
        result.append(f"❌ Error: {str(e)}")
    
    return {"success": False, "message": "\n".join(result)}
