"""
Workflow Automation Service for SPANKKS Construction
Handles automatic status changes based on quote → invoice → payment progression
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

class WorkflowAutomation:
    """Manages automatic job status progression and business workflow automation"""
    
    def __init__(self):
        self.data_dir = "data"
        self.workflow_rules_file = os.path.join(self.data_dir, "workflow_rules.json")
        self.automation_log_file = os.path.join(self.data_dir, "automation_log.json")
        self._ensure_data_files()
        
    def _ensure_data_files(self):
        """Ensure workflow automation data files exist"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize workflow rules if not exists
        if not os.path.exists(self.workflow_rules_file):
            default_rules = {
                "status_progression": {
                    "inquiry": {
                        "next_status": "quote_sent",
                        "trigger": "quote_generated",
                        "auto_advance": True,
                        "notification": True
                    },
                    "quote_sent": {
                        "next_status": "quote_approved",
                        "trigger": "manual_approval",
                        "auto_advance": False,
                        "notification": True
                    },
                    "quote_approved": {
                        "next_status": "job_scheduled",
                        "trigger": "appointment_created",
                        "auto_advance": True,
                        "notification": True
                    },
                    "job_scheduled": {
                        "next_status": "job_in_progress",
                        "trigger": "job_started",
                        "auto_advance": True,
                        "notification": True
                    },
                    "job_in_progress": {
                        "next_status": "invoice_generated",
                        "trigger": "invoice_created",
                        "auto_advance": True,
                        "notification": True
                    },
                    "invoice_generated": {
                        "next_status": "payment_received",
                        "trigger": "payment_recorded",
                        "auto_advance": True,
                        "notification": True
                    },
                    "payment_received": {
                        "next_status": "job_completed",
                        "trigger": "final_review",
                        "auto_advance": True,
                        "notification": True
                    }
                },
                "automation_settings": {
                    "enable_auto_progression": True,
                    "send_notifications": True,
                    "log_all_changes": True,
                    "reminder_intervals": {
                        "quote_follow_up_days": 3,
                        "payment_reminder_days": 7,
                        "overdue_payment_days": 30
                    }
                },
                "notification_templates": {
                    "quote_sent": "Quote {quote_id} has been sent to {customer_name}",
                    "quote_approved": "Quote {quote_id} approved by {customer_name}",
                    "job_scheduled": "Job {job_id} scheduled for {date}",
                    "job_started": "Work has begun on job {job_id}",
                    "invoice_generated": "Invoice {invoice_id} generated for job {job_id}",
                    "payment_received": "Payment received for invoice {invoice_id}",
                    "job_completed": "Job {job_id} completed successfully"
                }
            }
            
            with open(self.workflow_rules_file, 'w') as f:
                json.dump(default_rules, f, indent=2)
        
        # Initialize automation log if not exists
        if not os.path.exists(self.automation_log_file):
            with open(self.automation_log_file, 'w') as f:
                json.dump([], f)
    
    def get_workflow_rules(self) -> Dict:
        """Get current workflow rules"""
        try:
            with open(self.workflow_rules_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading workflow rules: {e}")
            return {}
    
    def log_automation_event(self, event_type: str, details: Dict):
        """Log automation events for audit trail"""
        try:
            with open(self.automation_log_file, 'r') as f:
                log_entries = json.load(f)
        except:
            log_entries = []
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details,
            "automated": True
        }
        
        log_entries.append(log_entry)
        
        # Keep only last 1000 entries
        if len(log_entries) > 1000:
            log_entries = log_entries[-1000:]
        
        try:
            with open(self.automation_log_file, 'w') as f:
                json.dump(log_entries, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving automation log: {e}")
    
    def process_quote_generation(self, quote_data: Dict) -> Dict:
        """Process quote generation and advance status"""
        rules = self.get_workflow_rules()
        
        if not rules.get("automation_settings", {}).get("enable_auto_progression", False):
            return {"status_changed": False, "message": "Auto-progression disabled"}
        
        quote_id = quote_data.get("id")
        customer_name = quote_data.get("customer_name")
        
        # Log the event
        self.log_automation_event("quote_generated", {
            "quote_id": quote_id,
            "customer_name": customer_name,
            "amount": quote_data.get("total_amount")
        })
        
        # Auto-advance status from inquiry to quote_sent
        status_update = {
            "previous_status": "inquiry",
            "new_status": "quote_sent",
            "trigger": "quote_generated",
            "automated": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate notification
        notification_template = rules.get("notification_templates", {}).get("quote_sent", "")
        notification_message = notification_template.format(
            quote_id=quote_id,
            customer_name=customer_name
        )
        
        return {
            "status_changed": True,
            "status_update": status_update,
            "notification": notification_message,
            "next_actions": ["await_customer_approval", "schedule_follow_up"]
        }
    
    def process_invoice_generation(self, invoice_data: Dict) -> Dict:
        """Process invoice generation and advance status"""
        rules = self.get_workflow_rules()
        
        if not rules.get("automation_settings", {}).get("enable_auto_progression", False):
            return {"status_changed": False, "message": "Auto-progression disabled"}
        
        invoice_id = invoice_data.get("id")
        job_id = invoice_data.get("job_id")
        customer_name = invoice_data.get("customer_name")
        
        # Log the event
        self.log_automation_event("invoice_generated", {
            "invoice_id": invoice_id,
            "job_id": job_id,
            "customer_name": customer_name,
            "amount": invoice_data.get("total_amount")
        })
        
        # Auto-advance status
        status_update = {
            "previous_status": "job_in_progress",
            "new_status": "invoice_generated",
            "trigger": "invoice_created",
            "automated": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate notification
        notification_template = rules.get("notification_templates", {}).get("invoice_generated", "")
        notification_message = notification_template.format(
            invoice_id=invoice_id,
            job_id=job_id
        )
        
        return {
            "status_changed": True,
            "status_update": status_update,
            "notification": notification_message,
            "next_actions": ["send_invoice_to_customer", "schedule_payment_reminder"]
        }
    
    def process_payment_received(self, payment_data: Dict) -> Dict:
        """Process payment and advance status to completion"""
        rules = self.get_workflow_rules()
        
        if not rules.get("automation_settings", {}).get("enable_auto_progression", False):
            return {"status_changed": False, "message": "Auto-progression disabled"}
        
        invoice_id = payment_data.get("invoice_id")
        amount = payment_data.get("amount")
        payment_method = payment_data.get("payment_method", "Unknown")
        
        # Log the event
        self.log_automation_event("payment_received", {
            "invoice_id": invoice_id,
            "amount": amount,
            "payment_method": payment_method
        })
        
        # Auto-advance status
        status_update = {
            "previous_status": "invoice_generated",
            "new_status": "payment_received",
            "trigger": "payment_recorded",
            "automated": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate notification
        notification_template = rules.get("notification_templates", {}).get("payment_received", "")
        notification_message = notification_template.format(
            invoice_id=invoice_id
        )
        
        return {
            "status_changed": True,
            "status_update": status_update,
            "notification": notification_message,
            "next_actions": ["finalize_job", "generate_completion_certificate"]
        }
    
    def process_job_start(self, job_data: Dict) -> Dict:
        """Process job start and update status"""
        rules = self.get_workflow_rules()
        
        job_id = job_data.get("id")
        customer_name = job_data.get("customer_name")
        staff_assigned = job_data.get("staff_assigned", [])
        
        # Log the event
        self.log_automation_event("job_started", {
            "job_id": job_id,
            "customer_name": customer_name,
            "staff_assigned": staff_assigned
        })
        
        # Auto-advance status
        status_update = {
            "previous_status": "job_scheduled",
            "new_status": "job_in_progress",
            "trigger": "job_started",
            "automated": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate notification
        notification_template = rules.get("notification_templates", {}).get("job_started", "")
        notification_message = notification_template.format(
            job_id=job_id
        )
        
        return {
            "status_changed": True,
            "status_update": status_update,
            "notification": notification_message,
            "next_actions": ["track_progress", "document_work"]
        }
    
    def check_pending_reminders(self) -> List[Dict]:
        """Check for pending reminders and generate them"""
        rules = self.get_workflow_rules()
        reminder_settings = rules.get("automation_settings", {}).get("reminder_intervals", {})
        
        pending_reminders = []
        
        # This would integrate with your storage system to check:
        # - Quotes sent X days ago without response
        # - Invoices due for payment
        # - Overdue payments
        
        # Example reminder logic (would need integration with your data)
        today = datetime.now()
        
        # Quote follow-up reminders
        quote_follow_up_days = reminder_settings.get("quote_follow_up_days", 3)
        
        # Payment reminders
        payment_reminder_days = reminder_settings.get("payment_reminder_days", 7)
        
        # Overdue payment alerts
        overdue_payment_days = reminder_settings.get("overdue_payment_days", 30)
        
        return pending_reminders
    
    def get_automation_statistics(self) -> Dict:
        """Get automation performance statistics"""
        try:
            with open(self.automation_log_file, 'r') as f:
                log_entries = json.load(f)
        except:
            log_entries = []
        
        # Calculate statistics
        total_events = len(log_entries)
        event_types = {}
        recent_events = []
        
        # Count events by type
        for entry in log_entries:
            event_type = entry.get("event_type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            # Get recent events (last 7 days)
            event_date = datetime.fromisoformat(entry["timestamp"])
            if (datetime.now() - event_date).days <= 7:
                recent_events.append(entry)
        
        return {
            "total_automation_events": total_events,
            "events_by_type": event_types,
            "recent_events_count": len(recent_events),
            "automation_enabled": self.get_workflow_rules().get("automation_settings", {}).get("enable_auto_progression", False),
            "last_updated": datetime.now().isoformat()
        }
    
    def update_workflow_rules(self, new_rules: Dict) -> bool:
        """Update workflow automation rules"""
        try:
            with open(self.workflow_rules_file, 'w') as f:
                json.dump(new_rules, f, indent=2)
            
            self.log_automation_event("rules_updated", {
                "updated_by": "admin",
                "changes": "Workflow rules configuration updated"
            })
            
            return True
        except Exception as e:
            logging.error(f"Error updating workflow rules: {e}")
            return False
    
    def get_status_progression_map(self) -> Dict:
        """Get the complete status progression mapping"""
        rules = self.get_workflow_rules()
        return rules.get("status_progression", {})
    
    def get_next_status(self, current_status: str, trigger: str) -> Optional[str]:
        """Get the next status based on current status and trigger"""
        progression_map = self.get_status_progression_map()
        
        if current_status in progression_map:
            status_config = progression_map[current_status]
            if status_config.get("trigger") == trigger and status_config.get("auto_advance", False):
                return status_config.get("next_status")
        
        return None
    
    def process_workflow_trigger(self, trigger: str, data: Dict) -> Dict:
        """Process any workflow trigger and determine actions"""
        
        trigger_processors = {
            "quote_generated": self.process_quote_generation,
            "invoice_created": self.process_invoice_generation,
            "payment_recorded": self.process_payment_received,
            "job_started": self.process_job_start
        }
        
        if trigger in trigger_processors:
            return trigger_processors[trigger](data)
        
        # Generic trigger processing
        self.log_automation_event("workflow_trigger", {
            "trigger": trigger,
            "data": data
        })
        
        return {
            "status_changed": False,
            "message": f"Trigger '{trigger}' processed but no automation rules matched"
        }