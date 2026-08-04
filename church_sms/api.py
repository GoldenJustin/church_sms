import frappe
import requests
import json
from frappe import _

@frappe.whitelist()
def send_church_sms(send_to, message, sender_id, branch="", members=None):
    """Send SMS to church members via Africa's Talking API"""
    try:
        # Get SMS settings
        settings = frappe.get_single("Church SMS Settings")
        
        username = settings.api_key
        api_key = settings.get_password("api_secret")
        
        if not username or not api_key:
            return {
                "success": False,
                "message": "❌ SMS API credentials not configured. Go to Church SMS Settings and set API Key and API Secret."
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
        
        # Send SMS
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
                "message": "✅ SMS sent successfully!\n\n" + result.get("details", "") + "\n\nTotal recipients: " + str(len(phone_numbers))
            }
        else:
            error_detail = result.get("error", "Unknown error")
            troubleshooting = get_troubleshooting_tips(error_detail)
            return {
                "success": False,
                "message": "❌ Failed to send SMS\n\nError: " + error_detail + "\n\n" + troubleshooting
            }
            
    except Exception as e:
        error_msg = str(e)
        frappe.log_error(frappe.get_traceback(), "Church SMS Error")
        return {
            "success": False,
            "message": "❌ System Error: " + error_msg + "\n\nCheck Error Log for details."
        }


def get_troubleshooting_tips(error_msg):
    """Provide troubleshooting tips based on error message"""
    error_lower = error_msg.lower()
    
    if "401" in error_msg or "authentication" in error_lower or "invalid" in error_lower:
        return "💡 **Troubleshooting:**\n- Check Church SMS Settings\n- API Key field = your Africa's Talking username (e.g., 'developerbeneth')\n- API Secret field = your Africa's Talking API key (long string)\n- Verify credentials at https://account.africastalking.com"
    
    elif "sender" in error_lower or "alphanumeric" in error_lower:
        return "💡 **Troubleshooting:**\n- Sender ID must be registered with Africa's Talking\n- Go to Church SMS Settings and update Default Sender ID\n- Or leave it blank to use your account's default sender"
    
    elif "insufficient" in error_lower or "balance" in error_lower:
        return "💡 **Troubleshooting:**\n- Your Africa's Talking account has insufficient balance\n- Top up at https://account.africastalking.com"
    
    elif "timeout" in error_lower:
        return "💡 **Troubleshooting:**\n- Network timeout - try again in a moment\n- Check your internet connection"
    
    elif "connection" in error_lower:
        return "💡 **Troubleshooting:**\n- Cannot connect to Africa's Talking API\n- Check internet connection\n- Africa's Talking might be down - try again later"
    
    else:
        return "💡 **Troubleshooting:**\n- Check Error Log for detailed error\n- Verify Africa's Talking account is active\n- Contact support if issue persists"


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
    
    if len(phone) < 11:
        return None
    
    return "+" + phone


def send_sms_via_at(username, api_key, sender_id, phone_numbers, message):
    """Send SMS via Africa's Talking API with detailed logging"""
    try:
        url = "https://api.africastalking.com/version1/messaging"
        
        recipients = ",".join(phone_numbers)
        
        # Headers
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "apiKey": api_key
        }
        
        # Payload
        payload = {
            "username": username,
            "to": recipients,
            "message": message,
        }
        
        if sender_id and sender_id.strip():
            payload["from"] = sender_id.strip()
        
        # Log request (for debugging)
        log_data = {
            "username": username,
            "recipients_count": len(phone_numbers),
            "recipients": recipients[:100] + "..." if len(recipients) > 100 else recipients,
            "sender_id": sender_id,
            "message": message[:100]
        }
        frappe.logger().info(f"Church SMS Request: {json.dumps(log_data)}")
        
        # Make request
        response = requests.post(url, data=payload, headers=headers, timeout=30)
        
        # Log response
        frappe.logger().info(f"Church SMS Response {response.status_code}: {response.text}")
        
        if response.status_code in [200, 201]:
            try:
                result = response.json()
            except:
                return {
                    "success": True,
                    "details": "SMS sent (response not JSON): " + response.text[:200]
                }
            
            # Parse response
            if "SMSMessageData" in result:
                sms_data = result["SMSMessageData"]
                recipients_data = sms_data.get("Recipients", [])
                
                sent_count = 0
                failed_count = 0
                errors = []
                
                for r in recipients_data:
                    status_code = r.get("statusCode")
                    if status_code in [100, 101, 102]:
                        sent_count += 1
                    else:
                        failed_count += 1
                        error = r.get("status", "Unknown error")
                        if error and error not in errors:
                            errors.append(error)
                
                details = f"✅ Sent: {sent_count}"
                if failed_count > 0:
                    details += f"\n❌ Failed: {failed_count}"
                    if errors:
                        details += f"\n\nErrors: {'; '.join(errors[:3])}"
                
                # Add cost info if available
                if "totalCost" in sms_data:
                    cost = sms_data.get("totalCost")
                    currency = sms_data.get("cost", "").split()[0] if "cost" in sms_data else ""
                    if cost:
                        details += f"\n\n💰 Cost: {currency} {cost}"
                
                return {
                    "success": sent_count > 0,
                    "details": details,
                    "response": result
                }
            else:
                return {
                    "success": True,
                    "details": "SMS queued successfully",
                    "response": result
                }
        else:
            # HTTP error
            try:
                error_data = response.json()
                error_msg = error_data.get("ErrorMessage", response.text)
            except:
                error_msg = response.text
            
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {error_msg}"
            }
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timeout (30 seconds). Africa's Talking API might be slow or unreachable."}
    except requests.exceptions.ConnectionError as e:
        return {"success": False, "error": f"Connection error: Cannot reach Africa's Talking API. {str(e)}"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Church SMS API Error")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@frappe.whitelist()
def test_sms_connection():
    """Test SMS API connection without sending"""
    try:
        settings = frappe.get_single("Church SMS Settings")
        
        username = settings.api_key
        api_key = settings.get_password("api_secret")
        
        if not username or not api_key:
            return {"success": False, "message": "❌ API credentials not configured"}
        
        # Try to get user info (lightweight API call)
        url = "https://api.africastalking.com/version1/user"
        headers = {
            "Accept": "application/json",
            "apiKey": api_key
        }
        params = {"username": username}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            user_data = data.get("UserData", {})
            balance = user_data.get("balance", "Unknown")
            
            return {
                "success": True,
                "message": f"✅ Connection successful!\n\nUsername: {username}\nBalance: {balance}"
            }
        else:
            return {
                "success": False,
                "message": f"❌ Connection failed (HTTP {response.status_code})\n\n{response.text}"
            }
            
    except Exception as e:
        return {"success": False, "message": f"❌ Error: {str(e)}"}


def validate_sms(doc, method):
    """Validate Church SMS before save"""
    if not doc.message:
        frappe.throw(_("Please enter a message"))
    
    if len(doc.message) > 160:
        segments = (len(doc.message) + 159) // 160
        frappe.msgprint(
            _("Message is {0} characters and will be sent as {1} SMS segments").format(len(doc.message), segments),
            indicator="orange"
        )


@frappe.whitelist()
def import_member(full_name, phone_number, branch="", status="Active"):
    """Import a single church member"""
    try:
        if not full_name or not phone_number:
            return {"success": False, "message": "full_name and phone_number are required"}
        
        # Check if member already exists
        existing = frappe.db.exists("Church Member", {"full_name": full_name})
        if existing:
            return {"success": False, "message": "Member already exists: " + full_name}
        
        # Format phone number
        formatted_phone = format_phone(phone_number)
        
        # Create member
        member = frappe.get_doc({
            "doctype": "Church Member",
            "full_name": full_name,
            "phone_number": phone_number,
            "branch": branch if branch else None,
            "status": status or "Active"
        })
        member.insert(ignore_permissions=True)
        
        return {
            "success": True,
            "message": "Imported: " + full_name,
            "name": member.name
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def bulk_import_members(csv_data):
    """Bulk import members from CSV data (JSON string)"""
    import json
    
    if isinstance(csv_data, str):
        csv_data = json.loads(csv_data)
    
    results = {"imported": 0, "failed": 0, "errors": []}
    
    for row in csv_data:
        result = import_member(
            full_name=row.get("full_name", ""),
            phone_number=row.get("phone_number", ""),
            branch=row.get("branch", ""),
            status=row.get("status", "Active")
        )
        
        if result.get("success"):
            results["imported"] += 1
        else:
            results["failed"] += 1
            results["errors"].append(f"{row.get('full_name', 'Unknown')}: {result.get('message', 'Unknown error')}")
    
    return results


@frappe.whitelist()
def diagnose_sms_setup():
    """Diagnose SMS setup and show detailed information"""
    result = []
    
    try:
        # Get settings
        settings = frappe.get_single("Church SMS Settings")
        
        result.append("📋 **Church SMS Settings:**")
        result.append(f"- API Key (username): `{settings.api_key}`")
        result.append(f"- API Secret (API key): `{'*' * 8}...{settings.get_password('api_secret')[-4:] if settings.get_password('api_secret') else 'NOT SET'}`")
        result.append(f"- Default Sender ID: `{settings.default_sender_id or 'NOT SET'}`")
        result.append("")
        
        username = settings.api_key
        api_key = settings.get_password("api_secret")
        
        if not username or not api_key:
            result.append("❌ **Missing credentials**")
            result.append("Please set both API Key and API Secret in Church SMS Settings")
            return "\n".join(result)
        
        # Test 1: Try Africa's Talking with current mapping
        result.append("🧪 **Test 1: Africa's Talking API (Current Mapping)**")
        result.append(f"- Username: `{username}`")
        result.append(f"- API Key: `{api_key[:8]}...{api_key[-4:]}`")
        
        try:
            url = "https://api.africastalking.com/version1/user"
            headers = {
                "Accept": "application/json",
                "apiKey": api_key
            }
            params = {"username": username}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get("UserData", {})
                balance = user_data.get("balance", "Unknown")
                result.append(f"✅ **SUCCESS!**")
                result.append(f"- Balance: {balance}")
                result.append(f"- Your credentials are correct!")
                return "\n".join(result)
            else:
                result.append(f"❌ Failed: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    result.append(f"- Error: {error_data.get('ErrorMessage', response.text)}")
                except:
                    result.append(f"- Response: {response.text[:200]}")
        except Exception as e:
            result.append(f"❌ Error: {str(e)}")
        
        result.append("")
        
        # Test 2: Try with swapped credentials
        result.append("🧪 **Test 2: Africa's Talking (Swapped Mapping)**")
        result.append(f"- Username: `{api_key[:20]}...`")
        result.append(f"- API Key: `{username}`")
        
        try:
            headers = {
                "Accept": "application/json",
                "apiKey": username  # Swapped
            }
            params = {"username": api_key}  # Swapped
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get("UserData", {})
                balance = user_data.get("balance", "Unknown")
                result.append(f"✅ **SUCCESS with swapped credentials!**")
                result.append(f"- Balance: {balance}")
                result.append(f"")
                result.append(f"⚠️ **Your credentials are swapped in Church SMS Settings!**")
                result.append(f"Please swap them:")
                result.append(f"- API Key field should be: `{api_key}`")
                result.append(f"- API Secret field should be: `{username}`")
                return "\n".join(result)
            else:
                result.append(f"❌ Failed: HTTP {response.status_code}")
        except Exception as e:
            result.append(f"❌ Error: {str(e)}")
        
        result.append("")
        
        # Test 3: Check if it's a sandbox account
        result.append("🧪 **Test 3: Africa's Talking Sandbox**")
        try:
            sandbox_url = "https://api.sandbox.africastalking.com/version1/user"
            headers = {
                "Accept": "application/json",
                "apiKey": api_key
            }
            params = {"username": "sandbox"}
            
            response = requests.get(sandbox_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                result.append("✅ Sandbox API is accessible")
                result.append("If you're using sandbox, your username should be 'sandbox'")
            else:
                result.append(f"❌ Sandbox test failed: HTTP {response.status_code}")
        except Exception as e:
            result.append(f"❌ Error: {str(e)}")
        
        result.append("")
        result.append("💡 **Next Steps:**")
        result.append("1. Verify your Africa's Talking credentials at https://account.africastalking.com")
        result.append("2. Check if you're using sandbox or production")
        result.append("3. Ensure your API key has SMS permissions")
        result.append("4. If using a different SMS provider, let me know which one")
        
    except Exception as e:
        result.append(f"❌ **Error:** {str(e)}")
        frappe.log_error(frappe.get_traceback(), "SMS Diagnosis Error")
    
    return "\n".join(result)
