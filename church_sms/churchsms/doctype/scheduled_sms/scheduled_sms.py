# Copyright (c) 2026, KODA Systems and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta

class ScheduledSMS(Document):
    def validate(self):
        if self.schedule_type == "Once" and self.start_date:
            start_datetime = datetime.combine(self.start_date, self.start_time or datetime.now().time())
            if start_datetime < datetime.now():
                frappe.throw("Start date and time cannot be in the past")
        
        self.update_next_scheduled()
    
    def update_next_scheduled(self):
        if self.status == "Active" and self.start_date and self.start_time:
            next_dt = datetime.combine(self.start_date, self.start_time)
            if next_dt > datetime.now():
                self.next_scheduled = next_dt
            elif self.schedule_type != "Once":
                # Calculate next occurrence
                self.next_scheduled = self.calculate_next_occurrence(next_dt)
    
    def calculate_next_occurrence(self, from_datetime):
        now = datetime.now()
        next_dt = from_datetime
        
        if self.schedule_type == "Daily":
            days_to_add = self.repeat_every or 1
            while next_dt <= now:
                next_dt += timedelta(days=days_to_add)
        
        elif self.schedule_type == "Weekly":
            weeks_to_add = self.repeat_every or 1
            while next_dt <= now:
                next_dt += timedelta(weeks=weeks_to_add)
        
        elif self.schedule_type == "Monthly":
            months_to_add = self.repeat_every or 1
            while next_dt <= now:
                month = next_dt.month - 1 + months_to_add
                year = next_dt.year + month // 12
                month = month % 12 + 1
                day = min(next_dt.day, [31,29 if year%4==0 and (year%100!=0 or year%400==0) else 28,31,30,31,30,31,31,30,31,30,31][month-1])
                next_dt = next_dt.replace(year=year, month=month, day=day)
        
        # Check end date
        if self.end_date and next_dt.date() > self.end_date:
            return None
        
        return next_dt
    
    def should_send_now(self):
        if self.status != "Active":
            return False
        
        if not self.next_scheduled:
            return False
        
        now = datetime.now()
        if now >= self.next_scheduled:
            return True
        
        return False
    
    def send_now(self):
        from church_sms.api import send_church_sms
        
        result = send_church_sms(
            send_to=self.send_to,
            message=self.message,
            sender_id=self.sender_id,
            branch=self.branch
        )
        
        if result.get("success"):
            self.last_sent = datetime.now()
            self.times_sent = (self.times_sent or 0) + 1
            
            if self.schedule_type == "Once":
                self.status = "Completed"
            else:
                self.update_next_scheduled()
            
            self.save(ignore_permissions=True)
        
        return result

def process_scheduled_sms():
    """Called by scheduler to process due scheduled SMS"""
    scheduled_list = frappe.get_all(
        "Scheduled SMS",
        filters={"status": "Active"},
        fields=["name"]
    )
    
    for item in scheduled_list:
        doc = frappe.get_doc("Scheduled SMS", item.name)
        if doc.should_send_now():
            try:
                doc.send_now()
                frappe.db.commit()
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), f"Scheduled SMS Error: {item.name}")
                frappe.db.rollback()
