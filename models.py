
import uuid
from datetime import datetime

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
