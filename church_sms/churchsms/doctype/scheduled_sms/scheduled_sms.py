# Copyright (c) 2026, KODA Systems and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta

class ScheduledSMS(Document):
    def validate(self):
        # Parse date and time strings to datetime objects
        if self.start_date and self.start_time:
            try:
                # Convert string date to date object
                if isinstance(self.start_date, str):
                    start_date_obj = datetime.strptime(self.start_date, '%Y-%m-%d').date()
                else:
                    start_date_obj = self.start_date
                
                # Convert string time to time object
                if isinstance(self.start_time, str):
                    start_time_obj = datetime.strptime(self.start_time, '%H:%M:%S').time()
                else:
                    start_time_obj = self.start_time
                
                # Combine date and time
                start_datetime = datetime.combine(start_date_obj, start_time_obj)
                
                # Validate not in past for one-time schedules
                if self.schedule_type == "Once" and start_datetime < datetime.now():
                    frappe.throw("Start date and time cannot be in the past")
                
                # Update next_scheduled
                self.update_next_scheduled()
                
            except ValueError as e:
                frappe.throw(f"Invalid date or time format: {str(e)}")
    
    def update_next_scheduled(self):
        if not self.start_date or not self.start_time:
            return
        
        # Parse date and time
        if isinstance(self.start_date, str):
            start_date_obj = datetime.strptime(self.start_date, '%Y-%m-%d').date()
        else:
            start_date_obj = self.start_date
        
        if isinstance(self.start_time, str):
            start_time_obj = datetime.strptime(self.start_time, '%H:%M:%S').time()
        else:
            start_time_obj = self.start_time
        
        next_dt = datetime.combine(start_date_obj, start_time_obj)
        now = datetime.now()
        
        # If it's a one-time schedule and time has passed, set status to Completed
        if self.schedule_type == "Once":
            if next_dt < now:
                self.status = "Completed"
                self.next_scheduled = None
            else:
                self.next_scheduled = next_dt
        else:
            # For recurring schedules, calculate next occurrence
            if next_dt > now:
                self.next_scheduled = next_dt
            else:
                # Calculate next occurrence based on schedule type
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
                        # Add months
                        month = next_dt.month - 1 + months_to_add
                        year = next_dt.year + month // 12
                        month = month % 12 + 1
                        # Handle day overflow
                        import calendar
                        max_day = calendar.monthrange(year, month)[1]
                        day = min(next_dt.day, max_day)
                        next_dt = next_dt.replace(year=year, month=month, day=day)
                
                # Check end date
                if self.end_date:
                    if isinstance(self.end_date, str):
                        end_date_obj = datetime.strptime(self.end_date, '%Y-%m-%d').date()
                    else:
                        end_date_obj = self.end_date
                    
                    if next_dt.date() > end_date_obj:
                        self.status = "Completed"
                        self.next_scheduled = None
                    else:
                        self.next_scheduled = next_dt
                else:
                    self.next_scheduled = next_dt
