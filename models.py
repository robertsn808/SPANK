
import uuid
from datetime import datetime
import pytz

def get_hawaii_time():
    """Get current time in Hawaii timezone"""
    hawaii_tz = pytz.timezone('Pacific/Honolulu')
    return datetime.now(hawaii_tz)

class ContactMessage:
    def __init__(self, name, email, phone=None, subject=None, message=None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.email = email
        self.phone = phone
        self.subject = subject
        self.message = message
        self.status = 'unread'
        self.created_at = datetime.now()
        self.ai_analysis = None
        self.priority_score = 0

class ServiceRequest:
    def __init__(self, name, email, phone, service, priority=None, preferred_date=None, 
                 preferred_time=None, location=None, description=None, budget_range=None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.email = email
        self.phone = phone
        self.service = service
        self.priority = priority or 'medium'
        self.preferred_date = preferred_date
        self.preferred_time = preferred_time
        self.location = location
        self.description = description
        self.budget_range = budget_range
        self.status = 'pending'
        self.submitted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.ai_recommendations = None
        self.estimated_duration = None
        self.estimated_cost = None

class Lead:
    def __init__(self, name, email, phone, source, interest_level=None, notes=None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.email = email
        self.phone = phone
        self.source = source  # website, referral, social_media, etc.
        self.interest_level = interest_level or 'medium'
        self.notes = notes
        self.status = 'new'  # new, contacted, qualified, converted, closed
        self.created_at = datetime.now()
        self.ai_score = 0
        self.follow_up_suggestions = None

class HandymanStorage:
    def __init__(self):
        self.service_requests = []
        self.contact_messages = []
        self.leads = []
        self.referrals = []
        self.memberships = []
        self.admin_notifications = []
    
    def add_service_request(self, request_data):
        request = ServiceRequest(**request_data)
        self.service_requests.append(request)
        return request.id
    
    def get_all_service_requests(self):
        return self.service_requests
    
    def update_service_request_status(self, request_id, status):
        for request in self.service_requests:
            if request.id == request_id:
                request.status = status
                return True
        return False
    
    def delete_service_request(self, request_id):
        self.service_requests = [r for r in self.service_requests if r.id != request_id]
        return True
    
    def add_contact_message(self, message_data):
        message = ContactMessage(**message_data)
        self.contact_messages.append(message)
        return message.id
    
    def get_all_contact_messages(self):
        return self.contact_messages
    
    def update_message_status(self, message_id, status):
        for message in self.contact_messages:
            if message.id == message_id:
                message.status = status
                return True
        return False
    
    def delete_contact_message(self, message_id):
        self.contact_messages = [m for m in self.contact_messages if m.id != message_id]
        return True
    
    def add_lead(self, lead_data):
        lead = Lead(**lead_data)
        self.leads.append(lead)
        return lead.id
    
    def get_all_leads(self):
        return self.leads
    
    def update_lead_status(self, lead_id, status):
        for lead in self.leads:
            if lead.id == lead_id:
                lead.status = status
                return True
        return False
    
    def delete_lead(self, lead_id):
        self.leads = [l for l in self.leads if l.id != lead_id]
        return True
    
    def get_high_priority_leads(self):
        return [lead for lead in self.leads if lead.ai_score > 7 or lead.interest_level == 'high']
    
    # Referral management methods
    def add_referral(self, referral_data):
        referral = Referral(
            referrer_code=referral_data['referrer_code'],
            referred_email=referral_data['referred_email'],
            status=referral_data.get('status', 'pending'),
            reward_amount=referral_data.get('reward_amount', 25)
        )
        self.referrals.append(referral)
        return referral.id
    
    def get_all_referrals(self):
        return self.referrals
    
    def get_referrals_by_code(self, referrer_code):
        return [ref for ref in self.referrals if ref.referrer_code == referrer_code]
    
    def update_referral_status(self, referral_id, status):
        for referral in self.referrals:
            if referral.id == referral_id:
                referral.status = status
                if status == 'completed':
                    referral.completed_date = get_hawaii_time()
                return True
        return False
    
    # Membership management methods
    def add_membership(self, membership_data):
        membership = Membership(
            customer_email=membership_data['customer_email'],
            plan_type=membership_data['plan_type'],
            status=membership_data.get('status', 'active')
        )
        self.memberships.append(membership)
        return membership.id
    
    def get_all_memberships(self):
        return self.memberships
    
    def get_membership_by_email(self, email):
        for membership in self.memberships:
            if membership.customer_email == email:
                return membership
        return None
    
    def update_membership_status(self, membership_id, status):
        for membership in self.memberships:
            if membership.id == membership_id:
                membership.status = status
                return True
        return False
    
    def get_referral_stats(self):
        total_referrals = len(self.referrals)
        completed_referrals = len([r for r in self.referrals if r.status == 'completed'])
        total_rewards = sum(r.reward_amount for r in self.referrals if r.status == 'rewarded')
        return {
            'total': total_referrals,
            'completed': completed_referrals,
            'pending': total_referrals - completed_referrals,
            'total_rewards': total_rewards
        }
    
    def get_membership_stats(self):
        active_memberships = len([m for m in self.memberships if m.status == 'active'])
        revenue_by_plan = {}
        for membership in self.memberships:
            if membership.status == 'active':
                revenue_by_plan[membership.plan_type] = revenue_by_plan.get(membership.plan_type, 0) + membership.monthly_fee
        
        return {
            'active_members': active_memberships,
            'monthly_revenue': sum(revenue_by_plan.values()),
            'revenue_by_plan': revenue_by_plan
        }
    
    def add_admin_notification(self, notification_data):
        """Add admin notification for SPANK Buck rewards"""
        notification = AdminNotification(**notification_data)
        self.admin_notifications.append(notification)
        return notification.id
    
    def get_admin_notifications(self):
        """Get all admin notifications"""
        return sorted(self.admin_notifications, key=lambda x: x.timestamp, reverse=True)
    
    def mark_notification_read(self, notification_id):
        """Mark notification as read"""
        for notification in self.admin_notifications:
            if notification.id == notification_id:
                notification.status = 'read'
                return True
        return False

class Admin:
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

class Referral:
    def __init__(self, referrer_code, referred_email, status="pending", reward_amount=25, created_date=None):
        self.id = str(uuid.uuid4())
        self.referrer_code = referrer_code
        self.referred_email = referred_email
        self.status = status  # pending, completed, rewarded
        self.reward_amount = reward_amount
        self.created_date = created_date or get_hawaii_time()
        self.completed_date = None

class Membership:
    def __init__(self, customer_email, plan_type, start_date=None, status="active"):
        self.id = str(uuid.uuid4())
        self.customer_email = customer_email
        self.plan_type = plan_type  # essential, premium, elite
        self.start_date = start_date or get_hawaii_time()
        self.status = status  # active, cancelled, suspended
        self.monthly_fee = {"essential": 29, "premium": 59, "elite": 99}.get(plan_type, 0)
        self.benefits_used = 0
        self.next_billing_date = None
