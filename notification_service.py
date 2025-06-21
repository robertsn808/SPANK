import os
import requests
import logging
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from twilio.rest import Client

class NotificationService:
    """Service for sending SPANK Buck rewards via email and SMS"""
    
    def __init__(self):
        self.rapidapi_key = os.environ.get('RAPIDAPI_KEY')
        self.sendgrid_key = os.environ.get('SENDGRID_API_KEY')
        # Use provided Twilio credentials as fallback
        self.twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID') or "US56bbfe10c643f708191c41349097faa4"
        self.twilio_token = os.environ.get('TWILIO_AUTH_TOKEN') or "4cd27b48274be507ac9163775722ad8e"
        self.twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER') or "+18778102726"
        self.from_email = "spank808@gmail.com"
        
        # Initialize Twilio client with SendGrid integration
        if self.twilio_sid and self.twilio_token:
            try:
                self.twilio_client = Client(self.twilio_sid, self.twilio_token)
                # Test credentials by fetching account info
                account = self.twilio_client.api.accounts(self.twilio_sid).fetch()
                logging.info(f"Twilio client initialized successfully for account: {account.friendly_name}")
            except Exception as e:
                logging.error(f"Twilio initialization failed: {e}")
                self.twilio_client = None
        else:
            self.twilio_client = None
        
    def send_spank_buck_reward(self, phone_number, amount, reason, customer_name=None, email=None):
        """Send SPANK Buck reward via SMS and email through Twilio SendGrid integration"""
        try:
            # Send SMS notification
            sms_sent = self.send_spank_buck_sms(phone_number, amount, reason, customer_name)
            
            # Send email if available through Twilio SendGrid integration
            email_sent = False
            if email and self.sendgrid_key:
                email_sent = self.send_twilio_sendgrid_email(email, amount, reason, customer_name)
            
            # Log the reward
            self._log_reward(email or phone_number, amount, reason, customer_name)
            
            # Notify admin of reward sent
            self._notify_admin_of_reward(phone_number, amount, reason, customer_name, email)
            
            return sms_sent or email_sent
        except Exception as e:
            logging.error(f"Failed to send SPANK Buck reward: {e}")
            return False
    
    def send_twilio_sendgrid_email(self, to_email, amount, reason, customer_name=None):
        """Send SPANK Buck reward email via Twilio SendGrid integration"""
        try:
            if not self.sendgrid_key:
                logging.warning("SendGrid not configured - skipping email")
                return False
                
            sg = SendGridAPIClient(self.sendgrid_key)
            
            # Create email content
            subject = f"🎉 You've Earned ${amount} SPANK Bucks!"
            
            if "referral" in reason.lower():
                html_content = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #007bff, #28a745); padding: 30px; border-radius: 15px; color: white;">
                    <h1 style="text-align: center; margin-bottom: 30px;">🎉 SPANK Buck Reward!</h1>
                    <div style="background: rgba(255,255,255,0.9); padding: 30px; border-radius: 10px; color: #333; text-align: center;">
                        <h2 style="color: #007bff; margin-bottom: 20px;">Congratulations {customer_name or 'there'}!</h2>
                        <p style="font-size: 18px; margin-bottom: 20px;">You've earned <strong style="color: #28a745; font-size: 24px;">${amount} SPANK Bucks</strong> for {reason}.</p>
                        <p style="margin-bottom: 20px;">Our SPANK team will reach out to your referred guest soon to help them with their home improvement needs!</p>
                        <p style="margin-bottom: 30px;">Use your SPANK Bucks on your next service and save money while getting quality work done!</p>
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <p style="margin: 0; font-weight: bold; color: #007bff;">Contact SPANK Team:</p>
                            <p style="margin: 5px 0;">📞 (808) 778-9132</p>
                            <p style="margin: 5px 0;">📧 spank808@gmail.com</p>
                        </div>
                        <p style="font-size: 14px; color: #666; margin-top: 20px;">Thank you for choosing SPANK Handyman Services!</p>
                    </div>
                </div>
                """
            else:
                html_content = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #007bff, #28a745); padding: 30px; border-radius: 15px; color: white;">
                    <h1 style="text-align: center; margin-bottom: 30px;">🎉 SPANK Buck Reward!</h1>
                    <div style="background: rgba(255,255,255,0.9); padding: 30px; border-radius: 10px; color: #333; text-align: center;">
                        <h2 style="color: #007bff; margin-bottom: 20px;">Congratulations {customer_name or 'there'}!</h2>
                        <p style="font-size: 18px; margin-bottom: 20px;">You've earned <strong style="color: #28a745; font-size: 24px;">${amount} SPANK Bucks</strong> for {reason}.</p>
                        <p style="margin-bottom: 20px;">A SPANK team member will follow up to see how we can help with your next project!</p>
                        <p style="margin-bottom: 30px;">Use your SPANK Bucks on any service and get quality work done for less!</p>
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <p style="margin: 0; font-weight: bold; color: #007bff;">Contact SPANK Team:</p>
                            <p style="margin: 5px 0;">📞 (808) 778-9132</p>
                            <p style="margin: 5px 0;">📧 spank808@gmail.com</p>
                        </div>
                        <p style="font-size: 14px; color: #666; margin-top: 20px;">Thank you for choosing SPANK Handyman Services!</p>
                    </div>
                </div>
                """
            
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            response = sg.send(message)
            logging.info(f"SendGrid email sent successfully to {to_email}: {response.status_code}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send SendGrid email: {e}")
            return False

    def send_spank_buck_sms(self, to_phone, amount, reason, customer_name=None):
        """Send SPANK Buck reward SMS via Twilio"""
        try:
            if not self.twilio_client:
                logging.warning("Twilio not configured - skipping SMS")
                return False
            
            if "referral" in reason.lower():
                message_body = f"🎉 Congratulations {customer_name or 'there'}! You've earned ${amount} SPANK Bucks for {reason}. Our SPANK team will reach out to your referred guest soon. Use your SPANK Bucks on your next service! - SPANK Team"
            elif "course" in reason.lower() or "lesson" in reason.lower():
                message_body = f"🎉 Congratulations {customer_name or 'there'}! You've earned ${amount} SPANK Bucks for {reason}. A SPANK team member will follow up to see how we can help with your project! Use your SPANK Bucks on any service! - SPANK Team"
            else:
                message_body = f"🎉 Congratulations {customer_name or 'there'}! You've earned ${amount} SPANK Bucks for {reason}. Our SPANK team will be in touch soon. Use your SPANK Bucks on your next service! - SPANK Team"
            
            message = self.twilio_client.messages.create(
                body=message_body,
                from_=self.twilio_phone,
                to=to_phone
            )
            
            logging.info(f"SPANK Buck SMS sent to {to_phone}: ${amount} for {reason}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send SPANK Buck SMS: {e}")
            return False

    def send_inquiry_alert(self, inquiry_type, customer_name, phone_number, email, service_type=None):
        """Send SMS alert to admin when new inquiries come in"""
        admin_phone = "+18084529779"
        
        try:
            if not self.twilio_client:
                # Log the inquiry for manual follow-up
                self._log_inquiry_for_admin(inquiry_type, customer_name, phone_number, email, service_type)
                logging.warning("Twilio not configured - inquiry logged for manual follow-up")
                return True  # Return True so the form still works
            
            if inquiry_type == "contact":
                message_body = f"🔔 New Contact Inquiry!\n\nCustomer: {customer_name}\nPhone: {phone_number}\nEmail: {email}\n\nPlease follow up promptly.\n- SPANK Team"
            elif inquiry_type == "consultation":
                message_body = f"🔔 New Consultation Request!\n\nCustomer: {customer_name}\nPhone: {phone_number}\nEmail: {email}\nService: {service_type or 'General'}\n\nPlease schedule consultation.\n- SPANK Team"
            else:
                message_body = f"🔔 New Inquiry!\n\nCustomer: {customer_name}\nPhone: {phone_number}\nEmail: {email}\n\nPlease follow up.\n- SPANK Team"
            
            message = self.twilio_client.messages.create(
                body=message_body,
                from_=self.twilio_phone,
                to=admin_phone
            )
            
            logging.info(f"Inquiry alert sent to admin for {customer_name}")
            return True
            
        except Exception as e:
            # Log the inquiry for manual follow-up even if SMS fails
            self._log_inquiry_for_admin(inquiry_type, customer_name, phone_number, email, service_type)
            logging.error(f"Failed to send inquiry alert: {e} - inquiry logged for manual follow-up")
            return True  # Return True so the form still works

    def _log_inquiry_for_admin(self, inquiry_type, customer_name, phone_number, email, service_type=None):
        """Log inquiry details for admin manual follow-up"""
        notification_data = {
            'type': 'new_inquiry',
            'inquiry_type': inquiry_type,
            'customer_name': customer_name,
            'phone_number': phone_number,
            'email': email,
            'service_type': service_type,
            'timestamp': datetime.now(),
            'status': 'unread'
        }
        
        # Import locally to avoid circular import
        from models import HandymanStorage
        storage = HandymanStorage()
        storage.add_admin_notification(notification_data)
        logging.info(f"Inquiry logged for admin follow-up: {customer_name} - {inquiry_type}")
    
    def _send_via_rapidapi(self, to_email, amount, reason, customer_name):
        """Send email via RapidAPI SendGrid service"""
        url = "https://rapidprod-sendgrid-v1.p.rapidapi.com/mail/send"
        
        html_content = self._generate_email_template(amount, reason, customer_name)
        
        payload = {
            "personalizations": [
                {
                    "to": [{"email": to_email}],
                    "subject": f"🎉 You've Earned ${amount} SPANK Bucks!"
                }
            ],
            "from": {"email": self.from_email, "name": "SPANK Handyman Services"},
            "content": [
                {
                    "type": "text/html",
                    "value": html_content
                }
            ]
        }
        
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "rapidprod-sendgrid-v1.p.rapidapi.com"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 202:
            logging.info(f"SPANK Buck email sent via RapidAPI to {to_email}: ${amount} for {reason}")
            return True
        else:
            logging.error(f"RapidAPI email failed: {response.status_code} - {response.text}")
            return False
    
    def _send_via_sendgrid(self, to_email, amount, reason, customer_name):
        """Send email via direct SendGrid API using dynamic templates"""
        sg = SendGridAPIClient(self.sendgrid_key)
        
        # Generate unique reward code
        import uuid
        reward_code = f"SPANK-{str(uuid.uuid4())[:8].upper()}"
        
        # Determine template ID based on amount
        template_id = os.environ.get('SENDGRID_TEMPLATE_5') if amount == 5 else os.environ.get('SENDGRID_TEMPLATE_25')
        
        # If no dynamic template, fall back to HTML content
        if not template_id:
            html_content = self._generate_email_template(amount, reason, customer_name)
            
            message = Mail(
                from_email=Email(self.from_email, "SPANK Handyman Services"),
                to_emails=To(to_email),
                subject=f"🎉 You've Earned ${amount} SPANK Bucks!",
                html_content=Content("text/html", html_content)
            )
        else:
            # Use dynamic template
            message = Mail(
                from_email=Email(self.from_email, "SPANK Handyman Services"),
                to_emails=To(to_email)
            )
            
            message.template_id = template_id
            message.dynamic_template_data = {
                'first_name': customer_name or to_email.split('@')[0],
                'lesson_title': reason,
                'reward_code': reward_code,
                'amount': amount,
                'spank_buck_image_url': f"https://your-domain.com/static/images/spank-buck-{amount}.png",
                'booking_link': "https://your-domain.com/consultation"
            }
        
        response = sg.send(message)
        
        if response.status_code == 202:
            logging.info(f"SPANK Buck email sent via SendGrid to {to_email}: ${amount} for {reason} (Code: {reward_code})")
            return True
        else:
            logging.error(f"SendGrid email failed: {response.status_code}")
            return False
    
    def _generate_email_template(self, amount, reason, customer_name):
        """Generate HTML email template for SPANK Buck rewards"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SPANK Bucks Reward</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 0; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%); padding: 30px; text-align: center; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; }}
                .logo {{ max-width: 120px; margin-bottom: 20px; }}
                .content {{ padding: 40px 30px; }}
                .reward-amount {{ text-align: center; margin: 30px 0; }}
                .spank-buck {{ width: 100px; height: auto; }}
                .amount {{ font-size: 36px; font-weight: bold; color: #ff6b35; margin: 20px 0; }}
                .reason {{ font-size: 18px; color: #333; margin-bottom: 30px; }}
                .cta-button {{ display: inline-block; background: #ff6b35; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; margin: 20px 0; }}
                .footer {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; font-size: 14px; }}
                .social-icons {{ margin-top: 15px; }}
                .social-icons a {{ color: white; margin: 0 10px; font-size: 18px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Congratulations!</h1>
                    <p style="color: white; font-size: 18px; margin: 10px 0 0 0;">You've earned SPANK Bucks!</p>
                </div>
                
                <div class="content">
                    <p style="font-size: 18px; color: #333;">Hi {customer_name or 'there'},</p>
                    
                    <div class="reward-amount">
                        <img src="https://your-domain.com/static/images/spank-buck-{amount}.png" alt="${amount} SPANK Buck" class="spank-buck">
                        <div class="amount">${amount} SPANK Bucks</div>
                        <div class="reason">Earned for: {reason}</div>
                    </div>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #555;">
                        Thank you for being part of the SPANK community! Your SPANK Bucks can be used toward any of our handyman services across O'ahu.
                    </p>
                    
                    <div style="text-align: center;">
                        <a href="https://your-domain.com/services" class="cta-button">Book Your Next Service</a>
                    </div>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; margin: 30px 0; border-radius: 10px;">
                        <h3 style="color: #ff6b35; margin-top: 0;">How to Use Your SPANK Bucks:</h3>
                        <ul style="color: #555; line-height: 1.6;">
                            <li>Each SPANK Buck = $1 credit toward services</li>
                            <li>Call us at (808) 778-9132 and mention your SPANK Bucks</li>
                            <li>No expiration date - use them anytime!</li>
                            <li>Combine with other offers and discounts</li>
                        </ul>
                    </div>
                    
                    <p style="font-size: 16px; color: #555;">
                        Keep learning at <strong>SPANK School</strong> to earn more rewards, or refer friends to earn $25 SPANK Bucks per successful referral!
                    </p>
                </div>
                
                <div class="footer">
                    <p><strong>SPANK Handyman Services</strong></p>
                    <p>Professional home repairs across O'ahu</p>
                    <p>📞 (808) 778-9132 | 🌐 Licensed & Insured</p>
                    
                    <div class="social-icons">
                        <a href="#" title="Facebook">📘</a>
                        <a href="#" title="Instagram">📷</a>
                        <a href="#" title="YouTube">🎥</a>
                    </div>
                    
                    <p style="font-size: 12px; margin-top: 20px; opacity: 0.8;">
                        This email was sent because you earned SPANK Bucks. 
                        Questions? Reply to this email or call us directly.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _log_reward(self, to_contact, amount, reason, customer_name):
        """Log reward when no email service is available"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] SPANK Buck Reward: ${amount} to {to_contact} ({customer_name}) for {reason}"
        logging.info(log_message)
        
        # Store in a simple log file for manual processing
        try:
            with open('spank_buck_rewards.log', 'a') as f:
                f.write(log_message + '\n')
        except Exception as e:
            logging.error(f"Failed to write reward log: {e}")
        
        return True
    
    def _notify_admin_of_reward(self, phone_number, amount, reason, customer_name, email):
        """Add reward notification to admin panel"""
        from models import HandymanStorage
        storage = HandymanStorage()
        
        # Create admin notification
        notification_data = {
            'type': 'spank_buck_reward',
            'customer_name': customer_name or 'Unknown Customer',
            'phone_number': phone_number,
            'email': email,
            'amount': amount,
            'reason': reason,
            'timestamp': datetime.now(),
            'status': 'sent'
        }
        
        # Add to storage
        try:
            storage.add_admin_notification(notification_data)
            logging.info(f"Admin notified of ${amount} SPANK Buck reward to {customer_name}")
        except Exception as e:
            logging.error(f"Failed to notify admin of reward: {e}")

# Global notification service instance
notification_service = NotificationService()