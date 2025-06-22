"""
Reminder Service for SPANKKS Construction
Handles automated email and SMS reminders for appointments and payments
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pytz

class ReminderService:
    """Automated reminder system for appointments and payments"""
    
    def __init__(self):
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
        self.reminders_file = 'data/reminders.json'
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Ensure reminder data files exist"""
        os.makedirs('data', exist_ok=True)
        
        if not os.path.exists(self.reminders_file):
            with open(self.reminders_file, 'w') as f:
                json.dump([], f, indent=2)
    
    def schedule_appointment_reminders(self, appointment_data: Dict) -> Dict:
        """Schedule automated reminders for an appointment"""
        try:
            appointment_date = datetime.fromisoformat(appointment_data.get('date', ''))
            client_name = appointment_data.get('client_name', '')
            client_email = appointment_data.get('client_email', '')
            client_phone = appointment_data.get('client_phone', '')
            service_type = appointment_data.get('service_type', '')
            
            reminders = []
            
            # 24-hour email reminder
            email_reminder_time = appointment_date - timedelta(hours=24)
            if email_reminder_time > datetime.now():
                email_reminder = {
                    'id': f"reminder_email_{int(datetime.now().timestamp())}",
                    'type': 'appointment_email',
                    'scheduled_time': email_reminder_time.isoformat(),
                    'recipient_name': client_name,
                    'recipient_email': client_email,
                    'appointment_date': appointment_data.get('date'),
                    'service_type': service_type,
                    'status': 'scheduled',
                    'created_date': datetime.now().isoformat()
                }
                reminders.append(email_reminder)
            
            # 2-hour SMS reminder
            sms_reminder_time = appointment_date - timedelta(hours=2)
            if sms_reminder_time > datetime.now() and client_phone:
                sms_reminder = {
                    'id': f"reminder_sms_{int(datetime.now().timestamp())}",
                    'type': 'appointment_sms',
                    'scheduled_time': sms_reminder_time.isoformat(),
                    'recipient_name': client_name,
                    'recipient_phone': client_phone,
                    'appointment_date': appointment_data.get('date'),
                    'service_type': service_type,
                    'status': 'scheduled',
                    'created_date': datetime.now().isoformat()
                }
                reminders.append(sms_reminder)
            
            # Save reminders
            self._save_reminders(reminders)
            
            logging.info(f"Scheduled {len(reminders)} reminders for appointment on {appointment_date}")
            
            return {
                'success': True,
                'reminders_scheduled': len(reminders),
                'reminder_ids': [r['id'] for r in reminders]
            }
            
        except Exception as e:
            logging.error(f"Error scheduling appointment reminders: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def schedule_payment_reminders(self, invoice_data: Dict) -> Dict:
        """Schedule automated payment reminders for an invoice"""
        try:
            due_date = datetime.fromisoformat(invoice_data.get('due_date', ''))
            client_name = invoice_data.get('client_name', '')
            client_email = invoice_data.get('client_email', '')
            client_phone = invoice_data.get('client_phone', '')
            invoice_number = invoice_data.get('invoice_number', '')
            amount = invoice_data.get('amount', 0)
            
            reminders = []
            
            # 3-day email reminder before due date
            email_reminder_time = due_date - timedelta(days=3)
            if email_reminder_time > datetime.now():
                email_reminder = {
                    'id': f"payment_email_{int(datetime.now().timestamp())}",
                    'type': 'payment_email',
                    'scheduled_time': email_reminder_time.isoformat(),
                    'recipient_name': client_name,
                    'recipient_email': client_email,
                    'invoice_number': invoice_number,
                    'amount': amount,
                    'due_date': invoice_data.get('due_date'),
                    'status': 'scheduled',
                    'created_date': datetime.now().isoformat()
                }
                reminders.append(email_reminder)
            
            # Day-of SMS reminder
            sms_reminder_time = due_date.replace(hour=10, minute=0, second=0, microsecond=0)
            if sms_reminder_time > datetime.now() and client_phone:
                sms_reminder = {
                    'id': f"payment_sms_{int(datetime.now().timestamp())}",
                    'type': 'payment_sms',
                    'scheduled_time': sms_reminder_time.isoformat(),
                    'recipient_name': client_name,
                    'recipient_phone': client_phone,
                    'invoice_number': invoice_number,
                    'amount': amount,
                    'due_date': invoice_data.get('due_date'),
                    'status': 'scheduled',
                    'created_date': datetime.now().isoformat()
                }
                reminders.append(sms_reminder)
            
            # Save reminders
            self._save_reminders(reminders)
            
            logging.info(f"Scheduled {len(reminders)} payment reminders for invoice {invoice_number}")
            
            return {
                'success': True,
                'reminders_scheduled': len(reminders),
                'reminder_ids': [r['id'] for r in reminders]
            }
            
        except Exception as e:
            logging.error(f"Error scheduling payment reminders: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_pending_reminders(self) -> List[Dict]:
        """Get all pending reminders that should be sent"""
        try:
            reminders = self._load_reminders()
            pending = []
            current_time = datetime.now()
            
            for reminder in reminders:
                if reminder.get('status') == 'scheduled':
                    scheduled_time = datetime.fromisoformat(reminder.get('scheduled_time', ''))
                    if scheduled_time <= current_time:
                        pending.append(reminder)
            
            return pending
            
        except Exception as e:
            logging.error(f"Error getting pending reminders: {e}")
            return []
    
    def mark_reminder_sent(self, reminder_id: str) -> bool:
        """Mark a reminder as sent"""
        try:
            reminders = self._load_reminders()
            
            for reminder in reminders:
                if reminder['id'] == reminder_id:
                    reminder['status'] = 'sent'
                    reminder['sent_date'] = datetime.now().isoformat()
                    break
            
            with open(self.reminders_file, 'w') as f:
                json.dump(reminders, f, indent=2)
            
            return True
            
        except Exception as e:
            logging.error(f"Error marking reminder as sent: {e}")
            return False
    
    def get_reminder_statistics(self) -> Dict:
        """Get reminder system statistics"""
        try:
            reminders = self._load_reminders()
            
            stats = {
                'total_reminders': len(reminders),
                'scheduled': 0,
                'sent': 0,
                'failed': 0,
                'by_type': {
                    'appointment_email': 0,
                    'appointment_sms': 0,
                    'payment_email': 0,
                    'payment_sms': 0
                }
            }
            
            for reminder in reminders:
                status = reminder.get('status', 'unknown')
                reminder_type = reminder.get('type', 'unknown')
                
                if status in stats:
                    stats[status] += 1
                
                if reminder_type in stats['by_type']:
                    stats['by_type'][reminder_type] += 1
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting reminder statistics: {e}")
            return {
                'total_reminders': 0,
                'scheduled': 0,
                'sent': 0,
                'failed': 0,
                'by_type': {}
            }
    
    def generate_email_content(self, reminder: Dict) -> Dict:
        """Generate email content for a reminder"""
        try:
            if reminder['type'] == 'appointment_email':
                subject = f"Reminder: Your SPANKKS Construction appointment tomorrow"
                
                # Format appointment date
                appointment_date = datetime.fromisoformat(reminder['appointment_date'])
                formatted_date = appointment_date.strftime('%A, %B %d, %Y at %I:%M %p')
                
                body = f"""
Dear {reminder['recipient_name']},

This is a friendly reminder about your upcoming appointment with SPANKKS Construction.

Appointment Details:
• Service: {reminder['service_type']}
• Date & Time: {formatted_date}
• Location: Your property

What to expect:
• Our team will arrive promptly at the scheduled time
• We'll review the project scope and answer any questions
• All necessary materials and tools will be provided

Need to reschedule or have questions?
Call us at (808) 778-9132 or email spank808@gmail.com

Thank you for choosing SPANKKS Construction!

Best regards,
The SPANKKS Construction Team
Licensed & Insured in Hawaii
"""
                
            elif reminder['type'] == 'payment_email':
                subject = f"Payment Reminder: Invoice {reminder['invoice_number']} due soon"
                
                # Format due date
                due_date = datetime.fromisoformat(reminder['due_date'])
                formatted_due = due_date.strftime('%A, %B %d, %Y')
                
                body = f"""
Dear {reminder['recipient_name']},

This is a friendly reminder that payment for Invoice {reminder['invoice_number']} is due on {formatted_due}.

Invoice Details:
• Invoice Number: {reminder['invoice_number']}
• Amount Due: ${reminder['amount']:.2f}
• Due Date: {formatted_due}

Payment Options:
• Venmo: @SPANKKS-Construction
• Zelle: spank808@gmail.com
• Check or Cash
• Call us to arrange payment: (808) 778-9132

Thank you for your prompt payment. We appreciate your business!

Questions about this invoice?
Contact us at (808) 778-9132 or spank808@gmail.com

Best regards,
SPANKKS Construction LLC
Licensed & Insured in Hawaii
"""
            
            else:
                raise ValueError(f"Unknown reminder type: {reminder['type']}")
            
            return {
                'subject': subject,
                'body': body.strip(),
                'recipient_email': reminder['recipient_email']
            }
            
        except Exception as e:
            logging.error(f"Error generating email content: {e}")
            return {
                'subject': 'Reminder from SPANKKS Construction',
                'body': 'Please contact us at (808) 778-9132 for details.',
                'recipient_email': reminder.get('recipient_email', '')
            }
    
    def generate_sms_content(self, reminder: Dict) -> Dict:
        """Generate SMS content for a reminder"""
        try:
            if reminder['type'] == 'appointment_sms':
                appointment_date = datetime.fromisoformat(reminder['appointment_date'])
                time_str = appointment_date.strftime('%I:%M %p')
                
                message = f"SPANKKS Construction reminder: Your {reminder['service_type']} appointment is in 2 hours at {time_str}. Questions? Call (808) 778-9132"
                
            elif reminder['type'] == 'payment_sms':
                message = f"SPANKKS Construction: Invoice {reminder['invoice_number']} for ${reminder['amount']:.2f} is due today. Pay via Venmo @SPANKKS-Construction or call (808) 778-9132"
                
            else:
                raise ValueError(f"Unknown reminder type: {reminder['type']}")
            
            return {
                'message': message,
                'recipient_phone': reminder['recipient_phone']
            }
            
        except Exception as e:
            logging.error(f"Error generating SMS content: {e}")
            return {
                'message': 'SPANKKS Construction reminder. Call (808) 778-9132 for details.',
                'recipient_phone': reminder.get('recipient_phone', '')
            }
    
    def _load_reminders(self) -> List[Dict]:
        """Load reminders from JSON file"""
        try:
            with open(self.reminders_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_reminders(self, new_reminders: List[Dict]):
        """Save new reminders to JSON file"""
        existing_reminders = self._load_reminders()
        existing_reminders.extend(new_reminders)
        
        # Keep only last 1000 reminders to prevent file bloat
        if len(existing_reminders) > 1000:
            existing_reminders = existing_reminders[-1000:]
        
        with open(self.reminders_file, 'w') as f:
            json.dump(existing_reminders, f, indent=2)

# Initialize global reminder service
reminder_service = ReminderService()