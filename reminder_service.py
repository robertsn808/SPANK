"""
Automated Reminder Service for SPANKKS Construction
Handles email and SMS reminders for appointments, invoices, and follow-ups
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pytz
from notification_service import NotificationService

class ReminderService:
    """Manages automated reminders for appointments, payments, and follow-ups"""
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
        self.reminder_file = 'data/reminders.json'
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Ensure reminder data files exist"""
        os.makedirs('data', exist_ok=True)
        
        if not os.path.exists(self.reminder_file):
            with open(self.reminder_file, 'w') as f:
                json.dump([], f, indent=2)
    
    def schedule_appointment_reminder(self, appointment_data: Dict) -> bool:
        """Schedule appointment reminders (24h email, 2h SMS)"""
        try:
            appointment_time = datetime.fromisoformat(appointment_data.get('scheduled_datetime'))
            customer_phone = appointment_data.get('customer_phone')
            customer_email = appointment_data.get('customer_email')
            
            # Schedule 24-hour email reminder
            email_reminder_time = appointment_time - timedelta(hours=24)
            self._schedule_reminder({
                'id': f"email_appt_{appointment_data.get('id')}_{int(datetime.now().timestamp())}",
                'type': 'appointment_email',
                'scheduled_time': email_reminder_time.isoformat(),
                'recipient_email': customer_email,
                'recipient_phone': customer_phone,
                'appointment_data': appointment_data,
                'status': 'pending'
            })
            
            # Schedule 2-hour SMS reminder
            sms_reminder_time = appointment_time - timedelta(hours=2)
            self._schedule_reminder({
                'id': f"sms_appt_{appointment_data.get('id')}_{int(datetime.now().timestamp())}",
                'type': 'appointment_sms',
                'scheduled_time': sms_reminder_time.isoformat(),
                'recipient_email': customer_email,
                'recipient_phone': customer_phone,
                'appointment_data': appointment_data,
                'status': 'pending'
            })
            
            logging.info(f"Scheduled appointment reminders for {appointment_data.get('id')}")
            return True
            
        except Exception as e:
            logging.error(f"Error scheduling appointment reminder: {e}")
            return False
    
    def schedule_invoice_reminder(self, invoice_data: Dict) -> bool:
        """Schedule invoice payment reminders"""
        try:
            due_date = datetime.fromisoformat(invoice_data.get('due_date'))
            customer_phone = invoice_data.get('customer_phone')
            customer_email = invoice_data.get('customer_email')
            
            # Schedule 7-day before due date reminder
            early_reminder = due_date - timedelta(days=7)
            self._schedule_reminder({
                'id': f"invoice_early_{invoice_data.get('id')}_{int(datetime.now().timestamp())}",
                'type': 'invoice_early',
                'scheduled_time': early_reminder.isoformat(),
                'recipient_email': customer_email,
                'recipient_phone': customer_phone,
                'invoice_data': invoice_data,
                'status': 'pending'
            })
            
            # Schedule due date reminder
            due_reminder = due_date
            self._schedule_reminder({
                'id': f"invoice_due_{invoice_data.get('id')}_{int(datetime.now().timestamp())}",
                'type': 'invoice_due',
                'scheduled_time': due_reminder.isoformat(),
                'recipient_email': customer_email,
                'recipient_phone': customer_phone,
                'invoice_data': invoice_data,
                'status': 'pending'
            })
            
            # Schedule overdue reminder (3 days after due date)
            overdue_reminder = due_date + timedelta(days=3)
            self._schedule_reminder({
                'id': f"invoice_overdue_{invoice_data.get('id')}_{int(datetime.now().timestamp())}",
                'type': 'invoice_overdue',
                'scheduled_time': overdue_reminder.isoformat(),
                'recipient_email': customer_email,
                'recipient_phone': customer_phone,
                'invoice_data': invoice_data,
                'status': 'pending'
            })
            
            logging.info(f"Scheduled invoice reminders for {invoice_data.get('id')}")
            return True
            
        except Exception as e:
            logging.error(f"Error scheduling invoice reminder: {e}")
            return False
    
    def schedule_follow_up_reminder(self, contact_data: Dict, days_ahead: int = 3) -> bool:
        """Schedule follow-up reminders for quotes and inquiries"""
        try:
            follow_up_time = datetime.now() + timedelta(days=days_ahead)
            
            self._schedule_reminder({
                'id': f"followup_{contact_data.get('id')}_{int(datetime.now().timestamp())}",
                'type': 'follow_up',
                'scheduled_time': follow_up_time.isoformat(),
                'recipient_email': contact_data.get('email'),
                'recipient_phone': contact_data.get('phone'),
                'contact_data': contact_data,
                'status': 'pending'
            })
            
            logging.info(f"Scheduled follow-up reminder for {contact_data.get('id')}")
            return True
            
        except Exception as e:
            logging.error(f"Error scheduling follow-up reminder: {e}")
            return False
    
    def _schedule_reminder(self, reminder_data: Dict):
        """Add reminder to schedule"""
        reminders = []
        if os.path.exists(self.reminder_file):
            with open(self.reminder_file, 'r') as f:
                reminders = json.load(f)
        
        reminders.append(reminder_data)
        
        with open(self.reminder_file, 'w') as f:
            json.dump(reminders, f, indent=2)
    
    def process_pending_reminders(self) -> List[Dict]:
        """Process all pending reminders that are due"""
        processed_reminders = []
        
        try:
            if not os.path.exists(self.reminder_file):
                return processed_reminders
            
            with open(self.reminder_file, 'r') as f:
                reminders = json.load(f)
            
            now = datetime.now()
            updated_reminders = []
            
            for reminder in reminders:
                if reminder.get('status') != 'pending':
                    updated_reminders.append(reminder)
                    continue
                
                scheduled_time = datetime.fromisoformat(reminder.get('scheduled_time'))
                
                if now >= scheduled_time:
                    # Process the reminder
                    success = self._send_reminder(reminder)
                    
                    if success:
                        reminder['status'] = 'sent'
                        reminder['sent_time'] = now.isoformat()
                        processed_reminders.append(reminder)
                    else:
                        reminder['status'] = 'failed'
                        reminder['failed_time'] = now.isoformat()
                
                updated_reminders.append(reminder)
            
            # Save updated reminders
            with open(self.reminder_file, 'w') as f:
                json.dump(updated_reminders, f, indent=2)
            
            return processed_reminders
            
        except Exception as e:
            logging.error(f"Error processing reminders: {e}")
            return []
    
    def _send_reminder(self, reminder: Dict) -> bool:
        """Send individual reminder based on type"""
        try:
            reminder_type = reminder.get('type')
            
            if reminder_type == 'appointment_email':
                return self._send_appointment_email_reminder(reminder)
            elif reminder_type == 'appointment_sms':
                return self._send_appointment_sms_reminder(reminder)
            elif reminder_type in ['invoice_early', 'invoice_due', 'invoice_overdue']:
                return self._send_invoice_reminder(reminder)
            elif reminder_type == 'follow_up':
                return self._send_follow_up_reminder(reminder)
            
            return False
            
        except Exception as e:
            logging.error(f"Error sending reminder: {e}")
            return False
    
    def _send_appointment_email_reminder(self, reminder: Dict) -> bool:
        """Send appointment email reminder"""
        appointment = reminder.get('appointment_data', {})
        email = reminder.get('recipient_email')
        
        if not email:
            return False
        
        subject = "Appointment Reminder - SPANKKS Construction"
        
        # Format appointment time
        appt_time = datetime.fromisoformat(appointment.get('scheduled_datetime', ''))
        formatted_time = appt_time.strftime('%A, %B %d, %Y at %I:%M %p')
        
        message = f"""
Dear {appointment.get('customer_name', 'Valued Customer')},

This is a friendly reminder about your upcoming appointment with SPANKKS Construction.

Appointment Details:
• Date & Time: {formatted_time}
• Service: {appointment.get('service_type', 'Construction Services')}
• Location: {appointment.get('address', 'To be confirmed')}

If you need to reschedule or have any questions, please contact us at (808) 778-9132.

We look forward to working with you!

Best regards,
SPANKKS Construction Team
(808) 778-9132
spank808@gmail.com

Licensed & Insured • Serving O'ahu with Pride
"""
        
        return self.notification_service.send_email(email, subject, message)
    
    def _send_appointment_sms_reminder(self, reminder: Dict) -> bool:
        """Send appointment SMS reminder"""
        appointment = reminder.get('appointment_data', {})
        phone = reminder.get('recipient_phone')
        
        if not phone:
            return False
        
        # Format appointment time
        appt_time = datetime.fromisoformat(appointment.get('scheduled_datetime', ''))
        formatted_time = appt_time.strftime('%m/%d at %I:%M %p')
        
        message = f"SPANKKS Construction: Your appointment is scheduled for {formatted_time}. Please call (808) 778-9132 if you need to reschedule. Thank you!"
        
        return self.notification_service.send_sms(phone, message)
    
    def _send_invoice_reminder(self, reminder: Dict) -> bool:
        """Send invoice payment reminder"""
        invoice = reminder.get('invoice_data', {})
        email = reminder.get('recipient_email')
        phone = reminder.get('recipient_phone')
        reminder_type = reminder.get('type')
        
        # Determine message based on reminder type
        if reminder_type == 'invoice_early':
            subject = "Payment Due Soon - SPANKKS Construction"
            urgency = "in 7 days"
        elif reminder_type == 'invoice_due':
            subject = "Payment Due Today - SPANKKS Construction"
            urgency = "today"
        else:  # overdue
            subject = "Overdue Payment - SPANKKS Construction"
            urgency = "is now overdue"
        
        if email:
            message = f"""
Dear {invoice.get('customer_name', 'Valued Customer')},

Your invoice {invoice.get('id')} {urgency}.

Invoice Details:
• Invoice #: {invoice.get('id')}
• Amount Due: ${invoice.get('total_amount', '0.00')}
• Service: {invoice.get('service_type', 'Construction Services')}
• Due Date: {invoice.get('due_date', 'N/A')}

Please remit payment at your earliest convenience. You can pay by cash, check, Venmo, or Zelle.

For questions about your invoice, please contact us at (808) 778-9132.

Thank you for choosing SPANKKS Construction!

Best regards,
SPANKKS Construction Team
(808) 778-9132
spank808@gmail.com
"""
            self.notification_service.send_email(email, subject, message)
        
        # Also send SMS for overdue invoices
        if reminder_type == 'invoice_overdue' and phone:
            sms_message = f"SPANKKS Construction: Invoice {invoice.get('id')} for ${invoice.get('total_amount', '0.00')} is overdue. Please call (808) 778-9132 to arrange payment."
            self.notification_service.send_sms(phone, sms_message)
        
        return True
    
    def _send_follow_up_reminder(self, reminder: Dict) -> bool:
        """Send follow-up reminder for quotes and inquiries"""
        contact = reminder.get('contact_data', {})
        email = contact.get('email')
        
        if not email:
            return False
        
        subject = "Follow-up on Your SPANKKS Construction Inquiry"
        
        message = f"""
Dear {contact.get('name', 'Valued Customer')},

We wanted to follow up on your recent inquiry with SPANKKS Construction.

We're here to help with your construction and home improvement needs. Our team is ready to provide you with:
• Professional consultation
• Detailed quotes
• Quality workmanship
• Licensed & insured services

If you're ready to move forward or have any questions, please don't hesitate to contact us:
• Phone: (808) 778-9132
• Email: spank808@gmail.com

We look forward to working with you on your project!

Best regards,
SPANKKS Construction Team

Licensed & Insured • Serving O'ahu with Pride
"""
        
        return self.notification_service.send_email(email, subject, message)
    
    def get_reminder_statistics(self) -> Dict:
        """Get reminder statistics for admin dashboard"""
        try:
            if not os.path.exists(self.reminder_file):
                return {
                    'total_scheduled': 0,
                    'sent_today': 0,
                    'pending': 0,
                    'failed': 0
                }
            
            with open(self.reminder_file, 'r') as f:
                reminders = json.load(f)
            
            today = datetime.now().date()
            stats = {
                'total_scheduled': len(reminders),
                'sent_today': 0,
                'pending': 0,
                'failed': 0
            }
            
            for reminder in reminders:
                if reminder.get('status') == 'pending':
                    stats['pending'] += 1
                elif reminder.get('status') == 'failed':
                    stats['failed'] += 1
                elif reminder.get('status') == 'sent':
                    sent_date = datetime.fromisoformat(reminder.get('sent_time', '')).date()
                    if sent_date == today:
                        stats['sent_today'] += 1
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting reminder statistics: {e}")
            return {
                'total_scheduled': 0,
                'sent_today': 0,
                'pending': 0,
                'failed': 0
            }
    
    def cancel_reminders_for_appointment(self, appointment_id: str) -> bool:
        """Cancel all reminders for a specific appointment"""
        try:
            if not os.path.exists(self.reminder_file):
                return True
            
            with open(self.reminder_file, 'r') as f:
                reminders = json.load(f)
            
            updated_reminders = []
            for reminder in reminders:
                if (reminder.get('type', '').startswith('appointment_') and 
                    reminder.get('appointment_data', {}).get('id') == appointment_id):
                    reminder['status'] = 'cancelled'
                    reminder['cancelled_time'] = datetime.now().isoformat()
                
                updated_reminders.append(reminder)
            
            with open(self.reminder_file, 'w') as f:
                json.dump(updated_reminders, f, indent=2)
            
            return True
            
        except Exception as e:
            logging.error(f"Error cancelling reminders: {e}")
            return False
    
    def cancel_reminders_for_invoice(self, invoice_id: str) -> bool:
        """Cancel all reminders for a specific invoice (when paid)"""
        try:
            if not os.path.exists(self.reminder_file):
                return True
            
            with open(self.reminder_file, 'r') as f:
                reminders = json.load(f)
            
            updated_reminders = []
            for reminder in reminders:
                if (reminder.get('type', '').startswith('invoice_') and 
                    reminder.get('invoice_data', {}).get('id') == invoice_id):
                    reminder['status'] = 'cancelled'
                    reminder['cancelled_time'] = datetime.now().isoformat()
                
                updated_reminders.append(reminder)
            
            with open(self.reminder_file, 'w') as f:
                json.dump(updated_reminders, f, indent=2)
            
            return True
            
        except Exception as e:
            logging.error(f"Error cancelling invoice reminders: {e}")
            return False