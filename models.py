import uuid
from datetime import datetime, timedelta
import pytz
import logging

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
        
        # CRM components with file persistence
        self.data_dir = 'data'
        self._ensure_data_directory()
        
        # Load existing data from files
        self.contacts = self._load_contacts()
        self.quotes = self._load_quotes()
        self.invoices = self._load_invoices()
        self.jobs = self._load_jobs()
        
        # Counter for IDs
        self._next_contact_id = self._get_next_id(self.contacts)
        self._next_quote_id = self._get_next_id(self.quotes)
        self._next_invoice_id = self._get_next_id(self.invoices)
        self._next_job_id = self._get_next_id(self.jobs)
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        import os
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
    
    def _get_next_id(self, items):
        """Get next available ID for a collection"""
        if not items:
            return 1
        return max(item.id for item in items if hasattr(item, 'id') and item.id) + 1
    
    def _load_contacts(self):
        """Load contacts from file"""
        import json
        import os
        contacts_file = os.path.join(self.data_dir, 'contacts.json')
        if os.path.exists(contacts_file):
            try:
                with open(contacts_file, 'r') as f:
                    data = json.load(f)
                contacts = []
                for item in data:
                    contact = Contact(
                        name=item['name'],
                        email=item['email'],
                        phone=item['phone'],
                        address=item.get('address', ''),
                        notes=item.get('notes', ''),
                        tags=item.get('tags', []),
                        created_date=item.get('created_date')
                    )
                    contact.id = item['id']
                    contact.job_history = item.get('job_history', [])
                    contact.total_spent = item.get('total_spent', 0.0)
                    contact.last_contact = item.get('last_contact')
                    contact.preferred_contact = item.get('preferred_contact', 'email')
                    contact.status = item.get('status', 'active')
                    contacts.append(contact)
                return contacts
            except Exception as e:
                logging.error(f"Error loading contacts: {e}")
        return []
    
    def _save_contacts_to_file(self):
        """Save contacts to file"""
        import json
        import os
        contacts_file = os.path.join(self.data_dir, 'contacts.json')
        try:
            data = []
            for contact in self.contacts:
                data.append({
                    'id': contact.id,
                    'name': contact.name,
                    'email': contact.email,
                    'phone': contact.phone,
                    'address': contact.address,
                    'notes': contact.notes,
                    'tags': contact.tags,
                    'created_date': contact.created_date,
                    'job_history': contact.job_history,
                    'total_spent': contact.total_spent,
                    'last_contact': contact.last_contact,
                    'preferred_contact': contact.preferred_contact,
                    'status': contact.status
                })
            with open(contacts_file, 'w') as f:
                json.dump(data, f, indent=2)
            logging.info(f"Saved {len(data)} contacts to file")
        except Exception as e:
            logging.error(f"Error saving contacts: {e}")
    
    def _load_quotes(self):
        """Load quotes from file"""
        import json
        import os
        quotes_file = os.path.join(self.data_dir, 'quotes.json')
        if os.path.exists(quotes_file):
            try:
                with open(quotes_file, 'r') as f:
                    data = json.load(f)
                quotes = []
                for item in data:
                    quote = Quote(
                        contact_id=item['contact_id'],
                        service_type=item['service_type'],
                        items=[],  # Will be populated below
                        total_amount=item['total_amount'],
                        valid_until=item['valid_until'],
                        notes=item.get('notes', '')
                    )
                    quote.id = item['id']
                    quote.created_date = item.get('created_date')
                    quote.status = item.get('status', 'pending')
                    quote.quote_number = f"Q{quote.id:04d}"
                    
                    # Reconstruct quote items
                    for item_data in item.get('items', []):
                        quote_item = QuoteItem(
                            description=item_data['description'],
                            quantity=item_data['quantity'],
                            unit_price=item_data['unit_price'],
                            unit=item_data.get('unit', 'each')
                        )
                        quote.items.append(quote_item)
                    
                    quotes.append(quote)
                return quotes
            except Exception as e:
                logging.error(f"Error loading quotes: {e}")
        return []
    
    def _save_quotes_to_file(self):
        """Save quotes to file"""
        import json
        import os
        quotes_file = os.path.join(self.data_dir, 'quotes.json')
        try:
            data = []
            for quote in self.quotes:
                quote_data = {
                    'id': quote.id,
                    'contact_id': quote.contact_id,
                    'service_type': quote.service_type,
                    'total_amount': quote.total_amount,
                    'valid_until': quote.valid_until,
                    'notes': quote.notes,
                    'created_date': quote.created_date,
                    'status': getattr(quote, 'status', 'pending'),
                    'items': []
                }
                
                # Save quote items
                for item in quote.items:
                    quote_data['items'].append({
                        'description': item.description,
                        'quantity': item.quantity,
                        'unit_price': item.unit_price,
                        'unit': item.unit
                    })
                
                data.append(quote_data)
            
            with open(quotes_file, 'w') as f:
                json.dump(data, f, indent=2)
            logging.info(f"Saved {len(data)} quotes to file")
        except Exception as e:
            logging.error(f"Error saving quotes: {e}")
    
    def _load_invoices(self):
        """Load invoices from file"""
        # Similar to quotes but for invoices
        return []
    
    def _load_jobs(self):
        """Load jobs from file"""
        # Similar to quotes but for jobs
        return []

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

    # CRM Methods
    def add_contact(self, contact_data):
        """Add a new contact"""
        contact = Contact(
            name=contact_data['name'],
            email=contact_data['email'],
            phone=contact_data['phone'],
            address=contact_data.get('address', ''),
            notes=contact_data.get('notes', ''),
            tags=contact_data.get('tags', [])
        )
        # Assign unique ID
        contact.id = self._next_contact_id
        self._next_contact_id += 1
        
        self.contacts.append(contact)
        self._save_contacts_to_file()
        return contact

    def get_all_contacts(self):
        """Get all contacts"""
        return self.contacts

    def get_contact_by_id(self, contact_id):
        """Get a specific contact by ID"""
        contacts = self.get_all_contacts()
        return next((c for c in contacts if c.id == contact_id), None)

    def update_contact(self, contact_id, updates):
        """Update an existing contact"""
        try:
            contacts = self.get_all_contacts()

            for contact in contacts:
                if contact.id == contact_id:
                    # Update contact attributes
                    for key, value in updates.items():
                        if hasattr(contact, key) and value is not None:
                            setattr(contact, key, value)

                    # Save back to storage
                    self._save_contacts_to_file()
                    logging.info(f"Updated contact {contact_id}")
                    return True

            logging.warning(f"Contact {contact_id} not found for update")
            return False

        except Exception as e:
            logging.error(f"Error updating contact {contact_id}: {e}")
            return False

    def add_quote(self, quote_data):
        """Add new quote"""
        quote = Quote(
            contact_id=quote_data['contact_id'],
            service_type=quote_data['service_type'],
            items=quote_data['items'],
            total_amount=quote_data['total_amount'],
            valid_until=quote_data['valid_until'],
            notes=quote_data.get('notes')
        )
        # Assign unique ID
        quote.id = self._next_quote_id
        self._next_quote_id += 1
        quote.quote_number = f"Q{quote.id:04d}"
        quote.status = 'pending'
        
        self.quotes.append(quote)
        self._save_quotes_to_file()
        return quote

    def _save_invoices(self):
        """Save invoices to JSON file"""
        try:
            import os
            import json
            os.makedirs('data', exist_ok=True)
            
            invoices_data = []
            for invoice in self.invoices:
                invoice_dict = {
                    'id': invoice.id,
                    'contact_id': invoice.contact_id,
                    'quote_id': invoice.quote_id,
                    'subtotal': invoice.subtotal,
                    'tax_rate': invoice.tax_rate,
                    'total_amount': invoice.total_amount,
                    'created_date': invoice.created_date,
                    'due_date': invoice.due_date,
                    'status': invoice.status,
                    'payment_terms': invoice.payment_terms,
                    'items': [{'description': item.description, 'quantity': item.quantity, 
                              'unit_price': item.unit_price, 'unit': item.unit} for item in invoice.items]
                }
                invoices_data.append(invoice_dict)
            
            with open('data/invoices.json', 'w') as f:
                json.dump(invoices_data, f, indent=2)
            logging.info(f"Saved {len(invoices_data)} invoices to file")
            
        except Exception as e:
            logging.error(f"Error saving invoices: {e}")

    def _save_contacts_to_file(self):
        """Save contacts to JSON file"""
        try:
            import os
            import json
            os.makedirs('data', exist_ok=True)
            
            contacts_data = []
            for contact in self.contacts:
                contact_dict = {
                    'id': contact.id,
                    'name': contact.name,
                    'email': contact.email,
                    'phone': contact.phone,
                    'address': contact.address,
                    'notes': contact.notes,
                    'tags': contact.tags,
                    'created_date': contact.created_date,
                    'job_history': contact.job_history,
                    'total_spent': contact.total_spent,
                    'last_contact': contact.last_contact,
                    'preferred_contact': contact.preferred_contact,
                    'status': contact.status
                }
                contacts_data.append(contact_dict)
            
            with open('data/contacts.json', 'w') as f:
                json.dump(contacts_data, f, indent=2)
            logging.info(f"Saved {len(contacts_data)} contacts to file")
            
        except Exception as e:
            logging.error(f"Error saving contacts: {e}")

    def get_all_quotes(self):
        """Get all quotes"""
        return self.quotes

    def get_quotes_by_contact(self, contact_id):
        """Get quotes for specific contact"""
        return [q for q in self.quotes if q.contact_id == contact_id]

    def update_quote_status(self, quote_id, status):
        """Update quote status"""
        for quote in self.quotes:
            if quote.id == quote_id:
                quote.status = status
                return True
        return False

    def add_invoice(self, invoice_data):
        """Add new invoice"""
        invoice = Invoice(
            contact_id=invoice_data['contact_id'],
            quote_id=invoice_data.get('quote_id'),
            items=invoice_data['items'],
            subtotal=invoice_data['subtotal'],
            tax_rate=invoice_data.get('tax_rate', 0.04712),
            payment_terms=invoice_data.get('payment_terms', 'Net 30')
        )
        invoice.id = len(self.invoices) + 1
        self.invoices.append(invoice)
        self._save_invoices()
        return invoice

    def get_all_invoices(self):
        """Get all invoices"""
        return self.invoices

    def get_invoices_by_contact(self, contact_id):
        """Get invoices for specific contact"""
        return [i for i in self.invoices if i.contact_id == contact_id]

    def update_invoice_status(self, invoice_id, status):
        """Update invoice status"""
        for invoice in self.invoices:
            if invoice.id == invoice_id:
                invoice.status = status
                return True
        return False

    def add_job(self, job_data):
        """Add new job"""
        job = Job(
            contact_id=job_data['contact_id'],
            quote_id=job_data.get('quote_id'),
            scheduled_date=job_data['scheduled_date'],
            crew_members=job_data.get('crew_members', []),
            notes=job_data.get('notes')
        )
        job.id = len(self.jobs) + 1
        self.jobs.append(job)
        return job

    def get_all_jobs(self):
        """Get all jobs"""
        return self.jobs

    def get_jobs_by_contact(self, contact_id):
        """Get jobs for specific contact"""
        return [j for j in self.jobs if j.contact_id == contact_id]

    def get_jobs_by_date(self, date):
        """Get jobs scheduled for specific date"""
        return [j for j in self.jobs if j.scheduled_date == date]

    def update_job_status(self, job_id, status):
        """Update job status"""
        for job in self.jobs:
            if job.id == job_id:
                job.status = status
                if status == 'completed':
                    job.completion_date = get_hawaii_time().strftime('%Y-%m-%d')
                return True
        return False

    def add_job_note(self, job_id, note):
        """Add note to job"""
        for job in self.jobs:
            if job.id == job_id:
                if job.notes:
                    job.notes += f"\n\n{get_hawaii_time().strftime('%Y-%m-%d %H:%M')}: {note}"
                else:
                    job.notes = f"{get_hawaii_time().strftime('%Y-%m-%d %H:%M')}: {note}"
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

class AdminNotification:
    def __init__(self, type, customer_name, phone_number, email, amount, reason, timestamp, status="unread"):
        self.id = str(uuid.uuid4())
        self.type = type  # spank_buck_reward
        self.customer_name = customer_name
        self.phone_number = phone_number
        self.email = email
        self.amount = amount
        self.reason = reason
        self.timestamp = timestamp
        self.status = status  # unread, read

class Contact:
    def __init__(self, name, email, phone, address=None, notes=None, tags=None, created_date=None):
        self.id = 0  # Will be set by storage
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address or ""
        self.notes = notes or ""
        self.tags = tags or []
        self.created_date = created_date or get_hawaii_time().strftime('%Y-%m-%d')
        self.job_history = []
        self.total_spent = 0.0
        self.last_contact = None
        self.preferred_contact = "email"
        self.status = "active"

class Quote:
    def __init__(self, contact_id, service_type, items, total_amount, valid_until, notes=None):
        self.id = 0  # Will be set by storage
        self.quote_number = ""  # Will be set by storage
        self.contact_id = contact_id
        self.service_type = service_type  # 'drywall', 'flooring', 'fencing', 'general'
        self.items = items  # List of quote items
        self.total_amount = total_amount
        self.valid_until = valid_until
        self.notes = notes or ""
        self.created_date = get_hawaii_time().strftime('%Y-%m-%d')
        self.status = "pending"  # pending, accepted, declined, expired
        self.pdf_path = None

class QuoteItem:
    def __init__(self, description, quantity, unit_price, unit="each"):
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.unit = unit
        self.total = quantity * unit_price

class Invoice:
    def __init__(self, contact_id, quote_id, items, subtotal, tax_rate=0.04712, payment_terms="Net 30"):
        self.id = 0  # Will be set by storage
        self.contact_id = contact_id
        self.quote_id = quote_id
        self.items = items
        self.subtotal = subtotal
        self.tax_rate = tax_rate  # Hawaii GET tax
        self.tax_amount = subtotal * tax_rate
        self.total_amount = subtotal + self.tax_amount
        self.payment_terms = payment_terms
        self.created_date = get_hawaii_time().strftime('%Y-%m-%d')
        hawaii_time = get_hawaii_time()
        due_date = hawaii_time + timedelta(days=30)
        self.due_date = due_date.strftime('%Y-%m-%d')
        self.status = "pending"  # pending, paid, overdue, cancelled
        self.payment_link = None
        self.pdf_path = None

class Job:
    def __init__(self, contact_id, quote_id, scheduled_date, crew_members=None, notes=None):
        self.id = 0  # Will be set by storage
        self.contact_id = contact_id
        self.quote_id = quote_id
        self.scheduled_date = scheduled_date
        self.scheduled_time = None
        self.crew_members = crew_members or []
        self.notes = notes or ""
        self.status = "scheduled"  # scheduled, in_progress, completed, cancelled
        self.created_date = get_hawaii_time().strftime('%Y-%m-%d')
        self.completion_date = None
        self.photos = []
        self.materials_used = []
        self.time_spent = 0
        self.customer_signature = None