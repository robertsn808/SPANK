"""
Enhanced Client Portal Service - PIN security, payment history, and digital quote acceptance
Handles secure client authentication, invoice tracking, and quote approval workflows
"""

import json
import os
import logging
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pytz

class EnhancedClientPortalService:
    def __init__(self):
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
        self.portal_auth_file = 'data/portal_auth.json'
        self.quote_approvals_file = 'data/quote_approvals.json'
        self.portal_sessions_file = 'data/portal_sessions.json'
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Ensure portal data files exist"""
        os.makedirs('data', exist_ok=True)
        
        for file_path in [self.portal_auth_file, self.quote_approvals_file, self.portal_sessions_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f, indent=2)
    
    def generate_client_pin(self, client_id: str, job_id: str) -> str:
        """Generate secure PIN for client portal access"""
        # Generate 6-digit PIN
        pin = ''.join(secrets.choice(string.digits) for _ in range(6))
        
        # Store in authentication file
        auth_data = self._load_portal_auth()
        
        portal_key = f"{client_id}/{job_id}"
        auth_data[portal_key] = {
            'pin': pin,
            'client_id': client_id,
            'job_id': job_id,
            'created_at': datetime.now(self.hawaii_tz).isoformat(),
            'expires_at': (datetime.now(self.hawaii_tz) + timedelta(days=90)).isoformat(),
            'access_count': 0,
            'last_access': None,
            'status': 'active'
        }
        
        self._save_portal_auth(auth_data)
        
        logging.info(f"Generated PIN for client portal: {client_id}/{job_id}")
        return pin
    
    def _load_portal_auth(self) -> Dict:
        """Load portal authentication data"""
        try:
            with open(self.portal_auth_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_portal_auth(self, auth_data: Dict):
        """Save portal authentication data"""
        with open(self.portal_auth_file, 'w') as f:
            json.dump(auth_data, f, indent=2)
    
    def authenticate_client(self, client_id: str, job_id: str, pin: str) -> Dict:
        """Authenticate client with PIN"""
        auth_data = self._load_portal_auth()
        portal_key = f"{client_id}/{job_id}"
        
        if portal_key not in auth_data:
            return {'success': False, 'error': 'Invalid client ID or job ID'}
        
        auth_record = auth_data[portal_key]
        
        # Check PIN
        if auth_record['pin'] != pin:
            return {'success': False, 'error': 'Invalid PIN'}
        
        # Check expiration
        expires_at = datetime.fromisoformat(auth_record['expires_at'])
        if datetime.now(self.hawaii_tz) > expires_at:
            return {'success': False, 'error': 'Access expired. Please contact SPANKKS Construction.'}
        
        # Check status
        if auth_record['status'] != 'active':
            return {'success': False, 'error': 'Access deactivated. Please contact SPANKKS Construction.'}
        
        # Update access tracking
        auth_record['access_count'] += 1
        auth_record['last_access'] = datetime.now(self.hawaii_tz).isoformat()
        auth_data[portal_key] = auth_record
        self._save_portal_auth(auth_data)
        
        # Create session
        session_token = self._create_portal_session(client_id, job_id)
        
        return {
            'success': True,
            'session_token': session_token,
            'client_id': client_id,
            'job_id': job_id,
            'access_level': 'client'
        }
    
    def _create_portal_session(self, client_id: str, job_id: str) -> str:
        """Create portal session token"""
        session_token = secrets.token_urlsafe(32)
        
        # Load sessions
        try:
            with open(self.portal_sessions_file, 'r') as f:
                sessions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            sessions = {}
        
        # Store session
        sessions[session_token] = {
            'client_id': client_id,
            'job_id': job_id,
            'access_level': 'client',
            'created_at': datetime.now(self.hawaii_tz).isoformat(),
            'expires_at': (datetime.now(self.hawaii_tz) + timedelta(hours=8)).isoformat(),
            'active': True
        }
        
        with open(self.portal_sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)
        
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """Validate portal session"""
        try:
            with open(self.portal_sessions_file, 'r') as f:
                sessions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
        
        if session_token not in sessions:
            return None
        
        session = sessions[session_token]
        
        # Check expiration
        expires_at = datetime.fromisoformat(session['expires_at'])
        if datetime.now(self.hawaii_tz) > expires_at:
            # Mark session as expired
            session['active'] = False
            with open(self.portal_sessions_file, 'w') as f:
                json.dump(sessions, f, indent=2)
            return None
        
        return session
    
    def get_client_payment_history(self, client_id: str, job_id: str) -> List[Dict]:
        """Get payment history for client"""
        try:
            from payment_tracking_service import PaymentTrackingService
            payment_service = PaymentTrackingService()
            
            # Get all payments and filter by client
            payments = payment_service._load_payments()
            
            # Get client's invoices to match payments
            from models import HandymanStorage
            storage = HandymanStorage()
            invoices = storage.get_all_invoices() or []
            
            client_invoices = []
            for invoice in invoices:
                # Match by job ID or client info
                if (invoice.get('job_id') == job_id or 
                    client_id.lower() in invoice.get('customer_name', '').lower()):
                    client_invoices.append(invoice)
            
            # Match payments to invoices
            payment_history = []
            for invoice in client_invoices:
                invoice_id = invoice.get('id') or invoice.get('invoice_number', '')
                invoice_payments = [p for p in payments if p.get('invoice_id') == str(invoice_id)]
                
                payment_history.append({
                    'invoice_id': invoice_id,
                    'invoice_number': invoice.get('invoice_number', ''),
                    'amount': invoice.get('total_amount', 0),
                    'issue_date': invoice.get('created_at', ''),
                    'due_date': invoice.get('due_date', ''),
                    'status': invoice.get('payment_status', 'pending'),
                    'payments': invoice_payments,
                    'balance_due': self._calculate_balance_due(invoice, invoice_payments)
                })
            
            return sorted(payment_history, key=lambda x: x['issue_date'], reverse=True)
            
        except Exception as e:
            logging.error(f"Error getting payment history: {e}")
            return []
    
    def _calculate_balance_due(self, invoice: Dict, payments: List[Dict]) -> float:
        """Calculate remaining balance on invoice"""
        total_amount = float(invoice.get('total_amount', 0))
        total_paid = sum(float(p.get('amount', 0)) for p in payments)
        return max(0, total_amount - total_paid)
    
    def approve_quote(self, client_id: str, job_id: str, quote_id: str, 
                     approval_method: str = 'digital_signature') -> Dict:
        """Process digital quote approval"""
        try:
            # Load quote approvals
            with open(self.quote_approvals_file, 'r') as f:
                approvals = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            approvals = {}
        
        # Get quote details
        from models import HandymanStorage
        storage = HandymanStorage()
        quotes = storage.get_all_quotes() or []
        
        quote = next((q for q in quotes if q.get('id') == quote_id), None)
        if not quote:
            return {'success': False, 'error': 'Quote not found'}
        
        # Create approval record
        approval_id = f"APP{len(approvals) + 1:04d}"
        hawaii_now = datetime.now(self.hawaii_tz)
        
        approval_record = {
            'approval_id': approval_id,
            'quote_id': quote_id,
            'client_id': client_id,
            'job_id': job_id,
            'approval_method': approval_method,
            'approved_at': hawaii_now.isoformat(),
            'approved_by': quote.get('customer_name', 'Client'),
            'quote_amount': quote.get('total_amount', 0),
            'terms_accepted': True,
            'ip_address': self._get_client_ip(),
            'user_agent': 'Portal Client',
            'status': 'approved'
        }
        
        approvals[approval_id] = approval_record
        
        with open(self.quote_approvals_file, 'w') as f:
            json.dump(approvals, f, indent=2)
        
        # Update quote status
        quote['status'] = 'approved'
        quote['approved_at'] = hawaii_now.isoformat()
        quote['approval_id'] = approval_id
        
        # Save updated quotes
        for i, q in enumerate(quotes):
            if q.get('id') == quote_id:
                quotes[i] = quote
                break
        
        storage._save_quotes_to_file(quotes)
        
        # Trigger workflow automation
        self._trigger_quote_approval_workflow(quote, approval_record)
        
        logging.info(f"Quote {quote_id} approved by client {client_id}")
        
        return {
            'success': True,
            'approval_id': approval_id,
            'message': 'Quote approved successfully!',
            'next_steps': [
                'Your quote has been approved and SPANKKS Construction has been notified.',
                'We will contact you within 24 hours to schedule the work.',
                'An invoice will be generated and sent to you shortly.'
            ]
        }
        
    except Exception as e:
        logging.error(f"Error approving quote: {e}")
        return {'success': False, 'error': 'Failed to process approval'}
    
    def _get_client_ip(self) -> str:
        """Get client IP address (simplified for demo)"""
        return "127.0.0.1"  # Would be extracted from request in real implementation
    
    def _trigger_quote_approval_workflow(self, quote: Dict, approval: Dict):
        """Trigger automated workflow after quote approval"""
        try:
            # Create automatic invoice
            from models import HandymanStorage
            storage = HandymanStorage()
            
            invoice_data = {
                'customer_name': quote.get('customer_name', ''),
                'customer_phone': quote.get('customer_phone', ''),
                'customer_email': quote.get('customer_email', ''),
                'service_type': quote.get('service_type', ''),
                'items': quote.get('items', []),
                'subtotal': quote.get('subtotal', 0),
                'tax_amount': quote.get('tax_amount', 0),
                'total_amount': quote.get('total_amount', 0),
                'quote_reference': quote.get('quote_number', ''),
                'due_date': (datetime.now(self.hawaii_tz) + timedelta(days=30)).strftime('%Y-%m-%d'),
                'payment_terms': 'Net 30 days',
                'created_from_quote': True,
                'auto_generated': True
            }
            
            invoice = storage.add_invoice(invoice_data)
            
            # Schedule appointment if not already scheduled
            from unified_scheduler import UnifiedScheduler
            scheduler = UnifiedScheduler()
            
            appointment_data = {
                'client_name': quote.get('customer_name', ''),
                'client_phone': quote.get('customer_phone', ''),
                'client_email': quote.get('customer_email', ''),
                'service_type': quote.get('service_type', ''),
                'scheduled_date': (datetime.now(self.hawaii_tz) + timedelta(days=7)).strftime('%Y-%m-%d'),
                'scheduled_time': '09:00',
                'status': 'scheduled',
                'quote_id': quote.get('id'),
                'notes': f"Auto-scheduled from approved quote {quote.get('quote_number', '')}"
            }
            
            scheduler.create_appointment(appointment_data)
            
            logging.info(f"Automated workflow triggered for approved quote {quote.get('id')}")
            
        except Exception as e:
            logging.error(f"Error in quote approval workflow: {e}")
    
    def get_client_quotes(self, client_id: str, job_id: str) -> List[Dict]:
        """Get quotes for specific client"""
        try:
            from models import HandymanStorage
            storage = HandymanStorage()
            quotes = storage.get_all_quotes() or []
            
            # Filter quotes for this client
            client_quotes = []
            for quote in quotes:
                if (client_id.lower() in quote.get('customer_name', '').lower() or
                    job_id in quote.get('job_reference', '')):
                    
                    # Add approval status
                    approval_status = self._get_quote_approval_status(quote.get('id'))
                    quote['approval_status'] = approval_status
                    
                    client_quotes.append(quote)
            
            return sorted(client_quotes, key=lambda x: x.get('created_at', ''), reverse=True)
            
        except Exception as e:
            logging.error(f"Error getting client quotes: {e}")
            return []
    
    def _get_quote_approval_status(self, quote_id: str) -> Dict:
        """Get approval status for quote"""
        try:
            with open(self.quote_approvals_file, 'r') as f:
                approvals = json.load(f)
            
            for approval_id, approval in approvals.items():
                if approval.get('quote_id') == quote_id:
                    return {
                        'approved': True,
                        'approved_at': approval.get('approved_at'),
                        'approval_id': approval_id,
                        'method': approval.get('approval_method')
                    }
            
            return {'approved': False}
            
        except Exception:
            return {'approved': False}
    
    def get_client_portal_data(self, client_id: str, job_id: str) -> Dict:
        """Get comprehensive portal data for client"""
        try:
            # Get client info
            from models import HandymanStorage
            storage = HandymanStorage()
            
            # Get job details
            jobs = storage.get_all_jobs() or []
            job = next((j for j in jobs if j.get('id') == job_id), None)
            
            # Get contact info
            contacts = storage.get_all_contacts() or []
            contact = next((c for c in contacts if c.get('id') == client_id), None)
            
            # Compile portal data
            portal_data = {
                'client_info': {
                    'name': contact.get('name', 'Valued Customer') if contact else 'Valued Customer',
                    'phone': contact.get('phone', '') if contact else '',
                    'email': contact.get('email', '') if contact else '',
                    'address': contact.get('address', '') if contact else ''
                },
                'job_info': {
                    'job_id': job_id,
                    'project_name': job.get('title', 'Project') if job else 'Project',
                    'status': job.get('status', 'scheduled') if job else 'scheduled',
                    'description': job.get('description', '') if job else ''
                },
                'quotes': self.get_client_quotes(client_id, job_id),
                'invoices': self.get_client_payment_history(client_id, job_id),
                'photos': self._get_job_photos(job_id),
                'timeline': self._get_project_timeline(client_id, job_id),
                'next_steps': self._get_next_steps(client_id, job_id)
            }
            
            return portal_data
            
        except Exception as e:
            logging.error(f"Error getting portal data: {e}")
            return {}
    
    def _get_job_photos(self, job_id: str) -> Dict:
        """Get before/after photos for job"""
        try:
            from upload_service import JobPhotoUploadService
            photo_service = JobPhotoUploadService()
            
            return {
                'before': photo_service.get_job_photos(job_id, 'before'),
                'progress': photo_service.get_job_photos(job_id, 'progress'),
                'after': photo_service.get_job_photos(job_id, 'after')
            }
        except Exception:
            return {'before': [], 'progress': [], 'after': []}
    
    def _get_project_timeline(self, client_id: str, job_id: str) -> List[Dict]:
        """Get project timeline events"""
        timeline = []
        
        try:
            # Add quote events
            quotes = self.get_client_quotes(client_id, job_id)
            for quote in quotes:
                timeline.append({
                    'date': quote.get('created_at', ''),
                    'event': 'Quote Generated',
                    'description': f"Quote {quote.get('quote_number', '')} for ${quote.get('total_amount', 0):.2f}",
                    'status': 'completed'
                })
                
                if quote.get('approval_status', {}).get('approved'):
                    timeline.append({
                        'date': quote['approval_status'].get('approved_at', ''),
                        'event': 'Quote Approved',
                        'description': 'Client approved the quote digitally',
                        'status': 'completed'
                    })
            
            # Add appointment events
            from unified_scheduler import UnifiedScheduler
            scheduler = UnifiedScheduler()
            appointments = scheduler.get_appointments_by_client(client_id)
            
            for appointment in appointments:
                if appointment.get('job_id') == job_id:
                    timeline.append({
                        'date': appointment.get('scheduled_date', ''),
                        'event': 'Work Scheduled',
                        'description': f"Appointment scheduled for {appointment.get('service_type', '')}",
                        'status': 'scheduled' if appointment.get('status') == 'scheduled' else 'completed'
                    })
            
            # Sort by date
            timeline.sort(key=lambda x: x.get('date', ''), reverse=True)
            
        except Exception as e:
            logging.error(f"Error getting timeline: {e}")
        
        return timeline
    
    def _get_next_steps(self, client_id: str, job_id: str) -> List[str]:
        """Get next steps for client"""
        next_steps = []
        
        try:
            # Check for pending quotes
            quotes = self.get_client_quotes(client_id, job_id)
            pending_quotes = [q for q in quotes if not q.get('approval_status', {}).get('approved')]
            
            if pending_quotes:
                next_steps.append("Review and approve pending quotes to proceed with scheduling")
            
            # Check for outstanding invoices
            payment_history = self.get_client_payment_history(client_id, job_id)
            outstanding_invoices = [p for p in payment_history if p.get('balance_due', 0) > 0]
            
            if outstanding_invoices:
                next_steps.append("Review outstanding invoices and payment options")
            
            # Check for scheduled work
            from unified_scheduler import UnifiedScheduler
            scheduler = UnifiedScheduler()
            appointments = scheduler.get_appointments_by_client(client_id)
            
            upcoming_appointments = [a for a in appointments 
                                   if a.get('job_id') == job_id and 
                                   a.get('status') == 'scheduled']
            
            if upcoming_appointments:
                next_steps.append("Prepare for upcoming scheduled work")
            else:
                next_steps.append("Work scheduling will be coordinated after quote approval")
            
            if not next_steps:
                next_steps.append("All current items are up to date. Thank you for choosing SPANKKS Construction!")
                
        except Exception as e:
            logging.error(f"Error getting next steps: {e}")
            next_steps.append("Contact SPANKKS Construction for current project status")
        
        return next_steps