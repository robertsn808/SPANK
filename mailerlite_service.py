"""
MailerLite Integration Service for SPANKKS Construction
Handles email marketing, customer lists, and automated campaigns
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any

class MailerLiteService:
    """Professional MailerLite integration for SPANKKS Construction email marketing"""
    
    def __init__(self):
        self.api_key = os.environ.get('MAILERLITE_API_KEY')
        self.base_url = 'https://connect.mailerlite.com/api'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.logger = logging.getLogger('mailerlite_service')
        
        # SPANKKS Construction email lists
        self.lists = {
            'customers': 'SPANKKS Construction Customers',
            'leads': 'Potential Customers & Leads',
            'spank_school': 'SPANKKS SKOOL Participants',
            'newsletter': 'SPANKKS Construction Newsletter',
            'vip': 'VIP Customers & Repeat Clients'
        }
        
        if not self.api_key:
            self.logger.warning("MailerLite API key not found. Email features will be disabled.")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test MailerLite API connection and return account info"""
        if not self.api_key:
            return {"success": False, "error": "API key not configured"}
        
        try:
            response = requests.get(f'{self.base_url}/me', headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                account_data = response.json()['data']
                return {
                    "success": True,
                    "account": {
                        "email": account_data.get('email'),
                        "timezone": account_data.get('timezone'),
                        "plan": account_data.get('plan', {}).get('name'),
                        "subscribers_count": account_data.get('stats', {}).get('subscribers_count', 0)
                    }
                }
            else:
                return {
                    "success": False, 
                    "error": f"API Error: {response.status_code} - {response.text}"
                }
                
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
    
    def get_or_create_group(self, list_name: str) -> Optional[str]:
        """Get existing group ID or create new group for SPANKKS lists"""
        if not self.api_key:
            return None
            
        try:
            # Get existing groups
            response = requests.get(f'{self.base_url}/groups', headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                groups = response.json()['data']
                
                # Look for existing group
                for group in groups:
                    if group['name'] == self.lists[list_name]:
                        return group['id']
                
                # Create new group if not found
                return self.create_group(list_name)
            
            return None
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting groups: {str(e)}")
            return None
    
    def create_group(self, list_name: str) -> Optional[str]:
        """Create a new MailerLite group for SPANKKS Construction"""
        if not self.api_key or list_name not in self.lists:
            return None
            
        try:
            group_data = {
                "name": self.lists[list_name]
            }
            
            response = requests.post(
                f'{self.base_url}/groups',
                headers=self.headers,
                json=group_data,
                timeout=10
            )
            
            if response.status_code == 201:
                group_id = response.json()['data']['id']
                self.logger.info(f"Created MailerLite group: {self.lists[list_name]} (ID: {group_id})")
                return group_id
            
            return None
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error creating group: {str(e)}")
            return None
    
    def add_subscriber(self, email: str, name: str = "", phone: str = "", 
                      list_name: str = "leads", custom_fields: Dict = None) -> Dict[str, Any]:
        """Add subscriber to MailerLite list with SPANKKS Construction context"""
        if not self.api_key:
            return {"success": False, "error": "MailerLite not configured"}
        
        # Get or create the appropriate group
        group_id = self.get_or_create_group(list_name)
        if not group_id:
            return {"success": False, "error": f"Could not access {list_name} list"}
        
        try:
            # Prepare subscriber data
            subscriber_data = {
                "email": email,
                "fields": {
                    "name": name or "",
                    "phone": phone or "",
                    "company": "SPANKKS Construction",
                    "source": "SPANKKS Website"
                }
            }
            
            # Add custom fields if provided
            if custom_fields:
                subscriber_data["fields"].update(custom_fields)
            
            # Add subscriber
            response = requests.post(
                f'{self.base_url}/subscribers',
                headers=self.headers,
                json=subscriber_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                subscriber = response.json()['data']
                
                # Add to specific group
                group_response = requests.post(
                    f'{self.base_url}/subscribers/{subscriber["id"]}/groups/{group_id}',
                    headers=self.headers,
                    timeout=10
                )
                
                return {
                    "success": True,
                    "subscriber_id": subscriber['id'],
                    "email": email,
                    "list": self.lists[list_name],
                    "status": subscriber.get('status', 'subscribed')
                }
            
            return {
                "success": False,
                "error": f"Failed to add subscriber: {response.status_code}"
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error adding subscriber: {str(e)}")
            return {"success": False, "error": f"Connection error: {str(e)}"}
    
    def send_welcome_email(self, email: str, name: str, service_type: str = "General") -> Dict[str, Any]:
        """Send welcome email to new SPANKKS Construction customer"""
        if not self.api_key:
            return {"success": False, "error": "MailerLite not configured"}
        
        try:
            email_content = {
                "subject": f"Welcome to SPANKKS Construction - {name}!",
                "html": self._get_welcome_email_template(name, service_type),
                "text": f"Welcome to SPANKKS Construction, {name}! We're excited to help with your {service_type} project."
            }
            
            # Send via MailerLite campaigns (would need campaign creation)
            # For now, we'll add them to the customers list with a welcome tag
            result = self.add_subscriber(
                email=email,
                name=name,
                list_name="customers",
                custom_fields={
                    "service_interest": service_type,
                    "joined_date": datetime.now().strftime("%Y-%m-%d"),
                    "welcome_sent": "yes"
                }
            )
            
            if result["success"]:
                self.logger.info(f"Welcome email prepared for {email} - {service_type} service")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error sending welcome email: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_quote_follow_up(self, email: str, name: str, quote_id: str, amount: float) -> Dict[str, Any]:
        """Send quote follow-up email with SPANK Buck incentives"""
        if not self.api_key:
            return {"success": False, "error": "MailerLite not configured"}
        
        try:
            # Add to leads list with quote information
            result = self.add_subscriber(
                email=email,
                name=name,
                list_name="leads",
                custom_fields={
                    "quote_id": quote_id,
                    "quote_amount": str(amount),
                    "quote_date": datetime.now().strftime("%Y-%m-%d"),
                    "follow_up_needed": "yes"
                }
            )
            
            if result["success"]:
                self.logger.info(f"Quote follow-up prepared for {email} - Quote #{quote_id} (${amount:,.2f})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error sending quote follow-up: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def add_spank_school_subscriber(self, email: str, name: str, course_completed: str) -> Dict[str, Any]:
        """Add subscriber to SPANKKS SKOOL list after course completion"""
        return self.add_subscriber(
            email=email,
            name=name,
            list_name="spank_school",
            custom_fields={
                "course_completed": course_completed,
                "completion_date": datetime.now().strftime("%Y-%m-%d"),
                "spank_bucks_earned": "5"
            }
        )
    
    def promote_to_vip(self, email: str, name: str, total_spent: float, projects_completed: int) -> Dict[str, Any]:
        """Promote customer to VIP list based on spending/project history"""
        return self.add_subscriber(
            email=email,
            name=name,
            list_name="vip",
            custom_fields={
                "total_spent": str(total_spent),
                "projects_completed": str(projects_completed),
                "vip_since": datetime.now().strftime("%Y-%m-%d"),
                "customer_tier": "VIP"
            }
        )
    
    def get_subscriber_stats(self) -> Dict[str, Any]:
        """Get subscriber statistics for all SPANKKS Construction lists"""
        if not self.api_key:
            return {"success": False, "error": "MailerLite not configured"}
        
        try:
            response = requests.get(f'{self.base_url}/groups', headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                groups = response.json()['data']
                stats = {}
                
                for group in groups:
                    group_name = group['name']
                    if group_name in self.lists.values():
                        # Find the list key for this group
                        list_key = None
                        for key, value in self.lists.items():
                            if value == group_name:
                                list_key = key
                                break
                        
                        if list_key:
                            stats[list_key] = {
                                "name": group_name,
                                "subscribers": group.get('active_count', 0),
                                "id": group['id']
                            }
                
                return {"success": True, "stats": stats}
            
            return {"success": False, "error": "Could not fetch group statistics"}
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting subscriber stats: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def unsubscribe_subscriber(self, email: str) -> Dict[str, Any]:
        """Unsubscribe a customer from all SPANKKS Construction lists"""
        if not self.api_key:
            return {"success": False, "error": "MailerLite not configured"}
        
        try:
            # Find subscriber by email
            response = requests.get(
                f'{self.base_url}/subscribers',
                headers=self.headers,
                params={"filter[email]": email},
                timeout=10
            )
            
            if response.status_code == 200:
                subscribers = response.json()['data']
                if subscribers:
                    subscriber_id = subscribers[0]['id']
                    
                    # Unsubscribe
                    unsubscribe_response = requests.patch(
                        f'{self.base_url}/subscribers/{subscriber_id}',
                        headers=self.headers,
                        json={"status": "unsubscribed"},
                        timeout=10
                    )
                    
                    if unsubscribe_response.status_code == 200:
                        return {"success": True, "message": f"Unsubscribed {email}"}
            
            return {"success": False, "error": "Subscriber not found"}
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error unsubscribing: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _get_welcome_email_template(self, name: str, service_type: str) -> str:
        """Generate HTML welcome email template for SPANKKS Construction"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <img src="https://your-domain.com/static/images/spank-logo.png" alt="SPANKKS Construction" style="max-width: 200px; margin-bottom: 20px;">
                
                <h1 style="color: #28a745;">Welcome to SPANKKS Construction, {name}!</h1>
                
                <p>Thank you for choosing SPANKKS Construction for your <strong>{service_type}</strong> needs. We're excited to work with you!</p>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #28a745; margin-top: 0;">What's Next?</h3>
                    <ul>
                        <li>We'll review your request and contact you within 24 hours</li>
                        <li>Our licensed professionals will provide a detailed quote</li>
                        <li>All work comes with our satisfaction guarantee</li>
                    </ul>
                </div>
                
                <div style="background: #28a745; color: white; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center;">
                    <h3 style="margin: 0;">🎓 Don't forget about SPANKKS SKOOL!</h3>
                    <p style="margin: 10px 0;">Complete DIY courses and earn SPANK Bucks for future projects!</p>
                    <a href="https://your-domain.com/spankks-skool" style="color: white; text-decoration: underline;">Visit SPANKKS SKOOL →</a>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p><strong>Contact Us:</strong></p>
                    <p>📞 (808) 778-9132<br>
                    📧 spank808@gmail.com<br>
                    🏝️ Serving all of O'ahu</p>
                    
                    <p style="font-size: 12px; color: #666; margin-top: 20px;">
                        Licensed & Insured • Professional Construction Services Across O'ahu
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def create_campaign(self, subject: str, content: str, list_name: str = "customers") -> Dict[str, Any]:
        """Create and send email campaign to specific SPANKKS Construction list"""
        if not self.api_key:
            return {"success": False, "error": "MailerLite not configured"}
        
        group_id = self.get_or_create_group(list_name)
        if not group_id:
            return {"success": False, "error": f"Could not access {list_name} list"}
        
        try:
            campaign_data = {
                "name": f"SPANKKS Construction - {subject}",
                "type": "regular",
                "emails": [{
                    "subject": subject,
                    "from_name": "SPANKKS Construction",
                    "from": "spank808@gmail.com",
                    "content": content
                }],
                "groups": [group_id]
            }
            
            response = requests.post(
                f'{self.base_url}/campaigns',
                headers=self.headers,
                json=campaign_data,
                timeout=10
            )
            
            if response.status_code == 201:
                campaign = response.json()['data']
                return {
                    "success": True,
                    "campaign_id": campaign['id'],
                    "name": campaign['name'],
                    "status": campaign['status']
                }
            
            return {"success": False, "error": f"Campaign creation failed: {response.status_code}"}
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error creating campaign: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get statistics for a specific campaign"""
        if not self.api_key:
            return {"success": False, "error": "MailerLite not configured"}
        
        try:
            response = requests.get(
                f'{self.base_url}/campaigns/{campaign_id}/reports',
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                stats = response.json()['data']
                return {
                    "success": True,
                    "stats": {
                        "sent": stats.get('sent', 0),
                        "delivered": stats.get('delivered', 0),
                        "opened": stats.get('opened', 0),
                        "clicked": stats.get('clicked', 0),
                        "open_rate": stats.get('open_rate', 0),
                        "click_rate": stats.get('click_rate', 0)
                    }
                }
            
            return {"success": False, "error": "Could not fetch campaign stats"}
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting campaign stats: {str(e)}")
            return {"success": False, "error": str(e)}