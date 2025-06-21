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
        self.twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')
        self.from_email = "noreply@spankhandyman.com"
        
    def send_spank_buck_email(self, to_email, amount, reason, customer_name=None):
        """Send SPANK Buck reward email using available service"""
        try:
            if self.rapidapi_key:
                return self._send_via_rapidapi(to_email, amount, reason, customer_name)
            elif self.sendgrid_key:
                return self._send_via_sendgrid(to_email, amount, reason, customer_name)
            else:
                logging.warning("No email service configured - logging reward instead")
                return self._log_reward(to_email, amount, reason, customer_name)
        except Exception as e:
            logging.error(f"Failed to send SPANK Buck email: {e}")
            return False
    
    def send_spank_buck_sms(self, to_phone, amount, reason, customer_name=None):
        """Send SPANK Buck reward SMS via Twilio"""
        try:
            if not all([self.twilio_sid, self.twilio_token, self.twilio_phone]):
                logging.warning("Twilio not configured - skipping SMS")
                return False
                
            client = Client(self.twilio_sid, self.twilio_token)
            
            message_body = f"🎉 Congratulations {customer_name or 'there'}! You've earned ${amount} SPANK Bucks for {reason}. Use them on your next handyman service! - SPANK Team"
            
            message = client.messages.create(
                body=message_body,
                from_=self.twilio_phone,
                to=to_phone
            )
            
            logging.info(f"SPANK Buck SMS sent to {to_phone}: ${amount} for {reason}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send SPANK Buck SMS: {e}")
            return False
    
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
                            <li>Call us at (808) 599-0908 and mention your SPANK Bucks</li>
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
                    <p>📞 (808) 599-0908 | 🌐 Licensed & Insured</p>
                    
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
    
    def _log_reward(self, to_email, amount, reason, customer_name):
        """Log reward when no email service is available"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] SPANK Buck Reward: ${amount} to {to_email} ({customer_name}) for {reason}"
        logging.info(log_message)
        
        # Store in a simple log file for manual processing
        try:
            with open('spank_buck_rewards.log', 'a') as f:
                f.write(log_message + '\n')
        except Exception as e:
            logging.error(f"Failed to write reward log: {e}")
        
        return True

# Global notification service instance
notification_service = NotificationService()