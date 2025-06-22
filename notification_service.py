import os
import logging
from datetime import datetime
from models import HandymanStorage

class NotificationService:
    """Service for manual admin dashboard notifications - no external integrations"""
    
    def __init__(self):
        """Initialize notification service for manual admin dashboard notifications only"""
        self.storage = HandymanStorage()
        self.from_email = "spank808@gmail.com"
        logging.info("Notification service initialized for manual admin dashboard notifications")

    def send_spank_buck_reward(self, phone_number, amount, reason, customer_name=None, email=None):
        """Create admin notification for SPANK Buck reward to be manually processed"""
        try:
            # Create admin notification for manual processing
            notification_data = {
                'type': 'spank_buck_reward',
                'customer_name': customer_name or 'Unknown Customer',
                'phone_number': phone_number,
                'email': email or 'Not provided',
                'amount': amount,
                'reason': reason,
                'timestamp': datetime.now(),
                'status': 'pending'
            }
            
            # Add to admin notifications
            self.storage.add_admin_notification(notification_data)
            
            logging.info(f"Admin notification created: ${amount} SPANK Buck reward for {customer_name} - {reason}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to create admin notification: {e}")
            return False

    def send_inquiry_alert(self, inquiry_type, customer_name, phone_number, email, service_type=None):
        """Create admin notification for new inquiry to be manually followed up"""
        try:
            # Create admin notification for manual follow-up
            notification_data = {
                'type': 'new_inquiry',
                'customer_name': customer_name,
                'phone_number': phone_number,
                'email': email,
                'amount': 0,  # No monetary value for inquiries
                'reason': f"New {inquiry_type} inquiry: {service_type or inquiry_type} - manual follow-up required",
                'timestamp': datetime.now(),
                'status': 'pending'
            }
            
            # Add to admin notifications
            self.storage.add_admin_notification(notification_data)
            
            logging.info(f"Admin notification created: New {inquiry_type} inquiry from {customer_name}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to create inquiry notification: {e}")
            return False

    def send_photo_upload_alert(self, job_id, photo_type, uploader_name):
        """Create admin notification for job photo uploads"""
        try:
            notification_data = {
                'type': 'photo_upload',
                'customer_name': uploader_name,
                'phone_number': 'See job details',
                'email': 'See job details', 
                'amount': 0,
                'reason': f"New {photo_type} photos uploaded for Job #{job_id}",
                'timestamp': datetime.now(),
                'status': 'pending'
            }
            
            self.storage.add_admin_notification(notification_data)
            logging.info(f"Admin notification created: Photo upload for Job #{job_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to create photo upload notification: {e}")
            return False

    def _log_reward(self, to_contact, amount, reason, customer_name):
        """Log reward notification for admin dashboard"""
        logging.info(f"MANUAL ACTION REQUIRED: Send ${amount} SPANK Buck reward to {customer_name} ({to_contact}) - {reason}")

    def _notify_admin_of_reward(self, phone_number, amount, reason, customer_name, email):
        """Admin notification already handled in main methods"""
        pass

    # Legacy method compatibility - redirects to manual notification
    def send_twilio_sendgrid_email(self, to_email, amount, reason, customer_name=None):
        """Legacy compatibility - creates admin notification instead"""
        return self.send_spank_buck_reward(
            phone_number='See email',
            amount=amount,
            reason=reason,
            customer_name=customer_name,
            email=to_email
        )

    def send_spank_buck_sms(self, to_phone, amount, reason, customer_name=None):
        """Legacy compatibility - creates admin notification instead"""
        return self.send_spank_buck_reward(
            phone_number=to_phone,
            amount=amount,
            reason=reason,
            customer_name=customer_name
        )

# Global instance
notification_service = NotificationService()