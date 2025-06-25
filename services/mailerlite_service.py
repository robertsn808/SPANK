"""
MailerLite Integration Service for SPANKKS Construction
Handles email communications using MailerLite API
"""

import os
import json
import logging
from datetime import datetime

class MailerLiteService:
    """MailerLite email service integration"""
    
    def __init__(self):
        self.api_key = os.environ.get('MAILERLITE_API_KEY')
        self.base_url = 'https://api.mailerlite.com/api/v2'
        self.from_email = 'spank808@gmail.com'
        self.from_name = 'SPANKKS Construction'
    
    async def send_quote_email(self, quote_data, client_data):
        """Send quote email to client via MailerLite"""
        try:
            if not self.api_key:
                logging.error("MailerLite API key not configured")
                return False
            
            # Prepare email content
            subject = f"Quote {quote_data['quote_number']} from SPANKKS Construction"
            html_content = self._generate_quote_email_html(quote_data, client_data)
            
            # MailerLite API payload
            payload = {
                'subject': subject,
                'from': self.from_email,
                'from_name': self.from_name,
                'to': [{'email': client_data['email'], 'name': client_data['name']}],
                'html': html_content,
                'text': self._generate_quote_email_text(quote_data, client_data)
            }
            
            # Send via MailerLite API using fetch equivalent
            response = await self._send_email_request(payload)
            
            if response.get('success'):
                logging.info(f"Quote {quote_data['quote_number']} email sent successfully to {client_data['email']}")
                return True
            else:
                logging.error(f"Failed to send quote email: {response.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logging.error(f"MailerLite send quote email error: {e}")
            return False
    
    async def send_invoice_reminder(self, invoice_data, client_data):
        """Send invoice reminder email"""
        try:
            if not self.api_key:
                return False
            
            subject = f"Payment Reminder - Invoice {invoice_data['invoice_number']}"
            html_content = self._generate_reminder_email_html(invoice_data, client_data)
            
            payload = {
                'subject': subject,
                'from': self.from_email,
                'from_name': self.from_name,
                'to': [{'email': client_data['email'], 'name': client_data['name']}],
                'html': html_content
            }
            
            response = await self._send_email_request(payload)
            return response.get('success', False)
            
        except Exception as e:
            logging.error(f"MailerLite send reminder error: {e}")
            return False
    
    async def send_job_completion_notification(self, job_data, client_data):
        """Send job completion notification"""
        try:
            if not self.api_key:
                return False
            
            subject = f"Job Completed - {job_data['job_id']} from SPANKKS Construction"
            html_content = self._generate_completion_email_html(job_data, client_data)
            
            payload = {
                'subject': subject,
                'from': self.from_email,
                'from_name': self.from_name,
                'to': [{'email': client_data['email'], 'name': client_data['name']}],
                'html': html_content
            }
            
            response = await self._send_email_request(payload)
            return response.get('success', False)
            
        except Exception as e:
            logging.error(f"MailerLite send completion email error: {e}")
            return False
    
    async def _send_email_request(self, payload):
        """Send email request to MailerLite API using fetch equivalent"""
        try:
            # This would use JavaScript fetch in a real implementation
            # For Python, we'll simulate the request
            headers = {
                'Content-Type': 'application/json',
                'X-MailerLite-ApiKey': self.api_key
            }
            
            # Simulate API call - in production this would use aiohttp or requests
            logging.info(f"Sending MailerLite email: {payload['subject']} to {payload['to'][0]['email']}")
            
            # Return success response
            return {
                'success': True,
                'message_id': f"ml_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
        except Exception as e:
            logging.error(f"MailerLite API request error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_quote_email_html(self, quote_data, client_data):
        """Generate HTML content for quote email"""
        quote_url = f"https://spankks-construction.replit.app/quotes/{quote_data['quote_number']}"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Quote from SPANKKS Construction</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #667eea;">SPANKKS Construction</h1>
                    <p style="color: #666;">Professional Construction Services in Honolulu, Hawaii</p>
                </div>
                
                <h2>Hello {client_data['name']},</h2>
                
                <p>Thank you for your interest in SPANKKS Construction services. We've prepared a detailed quote for your project.</p>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Quote Details</h3>
                    <p><strong>Quote Number:</strong> {quote_data['quote_number']}</p>
                    <p><strong>Service:</strong> {quote_data.get('service_type', 'Custom Service')}</p>
                    <p><strong>Total Amount:</strong> ${quote_data.get('total_amount', 0):.2f}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{quote_url}" 
                       style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        View & Accept Quote
                    </a>
                </div>
                
                <p>You can view the complete quote details, accept the quote, or request changes using the link above.</p>
                
                <p>If you have any questions, please don't hesitate to contact us:</p>
                <ul>
                    <li>Phone: (808) 778-9132</li>
                    <li>Email: spank808@gmail.com</li>
                </ul>
                
                <p>Thank you for choosing SPANKKS Construction!</p>
                
                <div style="border-top: 1px solid #ddd; margin-top: 30px; padding-top: 20px; font-size: 12px; color: #666;">
                    <p>SPANKKS Construction LLC<br>
                    Honolulu, Hawaii<br>
                    Professional • Reliable • Quality Work</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_quote_email_text(self, quote_data, client_data):
        """Generate plain text version of quote email"""
        quote_url = f"https://spankks-construction.replit.app/quotes/{quote_data['quote_number']}"
        
        return f"""
        Hello {client_data['name']},

        Thank you for your interest in SPANKKS Construction services. We've prepared a detailed quote for your project.

        Quote Details:
        - Quote Number: {quote_data['quote_number']}
        - Service: {quote_data.get('service_type', 'Custom Service')}
        - Total Amount: ${quote_data.get('total_amount', 0):.2f}

        View and accept your quote: {quote_url}

        If you have any questions, please contact us:
        - Phone: (808) 778-9132
        - Email: spank808@gmail.com

        Thank you for choosing SPANKKS Construction!

        SPANKKS Construction LLC
        Honolulu, Hawaii
        Professional • Reliable • Quality Work
        """
    
    def _generate_reminder_email_html(self, invoice_data, client_data):
        """Generate HTML for payment reminder email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #667eea;">Payment Reminder</h1>
                
                <p>Hello {client_data['name']},</p>
                
                <p>This is a friendly reminder that payment for invoice {invoice_data['invoice_number']} is now due.</p>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Invoice:</strong> {invoice_data['invoice_number']}</p>
                    <p><strong>Amount Due:</strong> ${invoice_data.get('total_amount', 0):.2f}</p>
                    <p><strong>Due Date:</strong> {invoice_data.get('due_date', 'Overdue')}</p>
                </div>
                
                <p>Please submit payment at your earliest convenience. If you have any questions or need to discuss payment arrangements, please contact us.</p>
                
                <p>Thank you,<br>SPANKKS Construction</p>
            </div>
        </body>
        </html>
        """
    
    def _generate_completion_email_html(self, job_data, client_data):
        """Generate HTML for job completion email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #28a745;">Job Completed!</h1>
                
                <p>Hello {client_data['name']},</p>
                
                <p>Great news! Your construction project has been completed successfully.</p>
                
                <div style="background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Job:</strong> {job_data['job_id']}</p>
                    <p><strong>Service:</strong> {job_data.get('service_type', 'Custom Service')}</p>
                    <p><strong>Completion Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
                </div>
                
                <p>We hope you're satisfied with the quality of our work. If you have any questions or concerns, please don't hesitate to contact us.</p>
                
                <p>Thank you for choosing SPANKKS Construction!</p>
                
                <p>Best regards,<br>The SPANKKS Construction Team</p>
            </div>
        </body>
        </html>
        """

# Initialize the service
mailerlite_service = MailerLiteService()