"""
Quote Acceptance and Workflow Automation Service for SPANKKS Construction
Handles digital quote acceptance, automatic job creation, and workflow progression
"""

import json
import os
import logging
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional, Any

class QuoteAcceptanceService:
    """Service for handling quote acceptance and automatic workflow progression"""
    
    def __init__(self):
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
        self.logger = logging.getLogger(__name__)
        self.data_dir = 'data'
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
    
    def _get_hawaii_time(self):
        """Get current Hawaii time"""
        return datetime.now(self.hawaii_tz)
    
    def _load_json_file(self, filename: str) -> List[Dict]:
        """Load data from JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def _save_json_file(self, filename: str, data: List[Dict]) -> bool:
        """Save data to JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving {filename}: {e}")
            return False
    
    def accept_quote(self, quote_id: int, client_signature: str, acceptance_method: str = 'digital') -> Dict[str, Any]:
        """
        Accept a quote and trigger automatic workflow progression
        
        Args:
            quote_id: ID of the quote to accept
            client_signature: Client's digital signature or name
            acceptance_method: Method of acceptance (digital, phone, email)
        
        Returns:
            Dictionary with acceptance status and created job details
        """
        current_time = self._get_hawaii_time()
        
        # Load quotes and find the target quote
        quotes = self._load_json_file('quotes.json')
        quote = None
        quote_index = None
        
        for i, q in enumerate(quotes):
            if q.get('id') == quote_id:
                quote = q
                quote_index = i
                break
        
        if not quote:
            return {
                'success': False,
                'error': 'Quote not found',
                'quote_id': quote_id
            }
        
        if quote.get('status') == 'accepted':
            return {
                'success': False,
                'error': 'Quote already accepted',
                'quote_id': quote_id
            }
        
        # Update quote status to accepted
        quote['status'] = 'accepted'
        quote['accepted_date'] = current_time.strftime('%Y-%m-%d')
        quote['accepted_time'] = current_time.strftime('%H:%M:%S')
        quote['client_signature'] = client_signature
        quote['acceptance_method'] = acceptance_method
        
        quotes[quote_index] = quote
        self._save_json_file('quotes.json', quotes)
        
        # Create automatic job from accepted quote
        job_details = self._create_job_from_quote(quote)
        
        # Create automatic invoice
        invoice_details = self._create_invoice_from_quote(quote)
        
        # Schedule follow-up reminders
        self._schedule_job_reminders(job_details['job_id'], quote['contact_id'])
        
        # Log acceptance activity
        self._log_quote_acceptance(quote_id, client_signature, acceptance_method)
        
        return {
            'success': True,
            'quote_id': quote_id,
            'acceptance_date': quote['accepted_date'],
            'acceptance_time': quote['accepted_time'],
            'job_created': job_details,
            'invoice_created': invoice_details,
            'workflow_status': 'Quote accepted → Job created → Invoice generated → Reminders scheduled'
        }
    
    def _create_job_from_quote(self, quote: Dict) -> Dict[str, Any]:
        """Create a job automatically from an accepted quote"""
        current_time = self._get_hawaii_time()
        
        # Load existing jobs to get next ID
        jobs = self._load_json_file('jobs.json')
        next_job_id = max([j.get('id', 0) for j in jobs], default=0) + 1
        
        # Create job record
        job = {
            'id': next_job_id,
            'contact_id': quote['contact_id'],
            'quote_id': quote['id'],
            'service_type': quote['service_type'],
            'total_amount': quote['total_amount'],
            'status': 'scheduled',
            'priority': 'normal',
            'created_date': current_time.strftime('%Y-%m-%d'),
            'scheduled_date': (current_time + timedelta(days=7)).strftime('%Y-%m-%d'),  # Default 1 week out
            'estimated_hours': self._estimate_job_hours(quote['service_type']),
            'items': quote.get('items', []),
            'notes': f"Job created automatically from accepted quote Q{quote['id']:04d}",
            'materials_needed': self._generate_materials_list(quote),
            'crew_assigned': [],
            'progress': {
                'quote_accepted': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'job_created': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'scheduled': None,
                'in_progress': None,
                'completed': None
            }
        }
        
        jobs.append(job)
        self._save_json_file('jobs.json', jobs)
        
        # Update contact job history
        self._update_contact_job_history(quote['contact_id'], next_job_id)
        
        return {
            'job_id': next_job_id,
            'status': 'scheduled',
            'scheduled_date': job['scheduled_date'],
            'estimated_hours': job['estimated_hours']
        }
    
    def _create_invoice_from_quote(self, quote: Dict) -> Dict[str, Any]:
        """Create an invoice automatically from an accepted quote"""
        current_time = self._get_hawaii_time()
        
        # Load existing invoices to get next ID
        invoices = self._load_json_file('invoices.json')
        next_invoice_id = max([i.get('id', 0) for i in invoices], default=0) + 1
        
        # Calculate Hawaii GET tax (4.712%)
        subtotal = quote['total_amount']
        tax_rate = 0.04712
        tax_amount = subtotal * tax_rate
        total_with_tax = subtotal + tax_amount
        
        # Create invoice record
        invoice = {
            'id': next_invoice_id,
            'contact_id': quote['contact_id'],
            'quote_id': quote['id'],
            'subtotal': subtotal,
            'tax_rate': tax_rate,
            'tax_amount': tax_amount,
            'total_amount': total_with_tax,
            'created_date': current_time.strftime('%Y-%m-%d'),
            'due_date': (current_time + timedelta(days=30)).strftime('%Y-%m-%d'),
            'status': 'pending',
            'payment_terms': 'Net 30',
            'items': quote.get('items', []),
            'notes': f"Invoice generated automatically from accepted quote Q{quote['id']:04d}",
            'payment_history': []
        }
        
        invoices.append(invoice)
        self._save_json_file('invoices.json', invoices)
        
        return {
            'invoice_id': next_invoice_id,
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total_amount': total_with_tax,
            'due_date': invoice['due_date']
        }
    
    def _estimate_job_hours(self, service_type: str) -> int:
        """Estimate hours required for different service types"""
        hour_estimates = {
            'drywall_services': 8,
            'flooring_installation': 12,
            'electrical_work': 6,
            'plumbing_services': 4,
            'general_handyman': 6,
            'fence_installation': 16,
            'painting_services': 10,
            'appliance_installation': 3,
            'cabinet_installation': 14,
            'bathroom_renovation': 40,
            'kitchen_renovation': 60
        }
        return hour_estimates.get(service_type, 8)  # Default 8 hours
    
    def _generate_materials_list(self, quote: Dict) -> List[str]:
        """Generate basic materials list based on service type"""
        service_type = quote.get('service_type', '')
        
        materials_by_service = {
            'drywall_services': ['Drywall sheets', 'Joint compound', 'Drywall screws', 'Tape', 'Primer', 'Paint'],
            'flooring_installation': ['Flooring material', 'Underlayment', 'Adhesive/nails', 'Trim/molding', 'Transition strips'],
            'electrical_work': ['Wire', 'Outlets/switches', 'Wire nuts', 'Electrical boxes', 'Circuit breakers'],
            'plumbing_services': ['Pipes/fittings', 'Shut-off valves', 'Pipe sealant', 'Fixtures'],
            'fence_installation': ['Fence panels', 'Posts', 'Hardware', 'Concrete', 'Stain/sealant'],
            'general_handyman': ['Basic hardware', 'Fasteners', 'Caulk', 'Touch-up paint']
        }
        
        return materials_by_service.get(service_type, ['Materials as specified in quote'])
    
    def _update_contact_job_history(self, contact_id: int, job_id: int):
        """Update contact's job history with new job"""
        contacts = self._load_json_file('contacts.json')
        
        for contact in contacts:
            if contact.get('id') == contact_id:
                if 'job_history' not in contact:
                    contact['job_history'] = []
                contact['job_history'].append(job_id)
                contact['last_contact'] = self._get_hawaii_time().strftime('%Y-%m-%d')
                break
        
        self._save_json_file('contacts.json', contacts)
    
    def _schedule_job_reminders(self, job_id: int, contact_id: int):
        """Schedule automatic reminders for job follow-up"""
        current_time = self._get_hawaii_time()
        reminders = self._load_json_file('reminders.json')
        
        # Schedule reminders at different intervals
        reminder_schedule = [
            {'days': 1, 'type': 'job_confirmation', 'message': 'Confirm job scheduling and materials'},
            {'days': 7, 'type': 'job_preparation', 'message': 'Job scheduled for next week - confirm timing'},
            {'days': 14, 'type': 'job_follow_up', 'message': 'Follow up on job completion and satisfaction'}
        ]
        
        for reminder_config in reminder_schedule:
            reminder_date = current_time + timedelta(days=reminder_config['days'])
            
            reminder = {
                'id': len(reminders) + 1,
                'job_id': job_id,
                'contact_id': contact_id,
                'type': reminder_config['type'],
                'message': reminder_config['message'],
                'scheduled_date': reminder_date.strftime('%Y-%m-%d'),
                'scheduled_time': '09:00:00',  # 9 AM Hawaii time
                'status': 'pending',
                'created_date': current_time.strftime('%Y-%m-%d')
            }
            
            reminders.append(reminder)
        
        self._save_json_file('reminders.json', reminders)
    
    def _log_quote_acceptance(self, quote_id: int, client_signature: str, acceptance_method: str):
        """Log quote acceptance activity for audit trail"""
        current_time = self._get_hawaii_time()
        
        # Load or create activity log
        log_file = 'quote_acceptance_log.json'
        activity_log = self._load_json_file(log_file)
        
        log_entry = {
            'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'quote_id': quote_id,
            'action': 'quote_accepted',
            'client_signature': client_signature,
            'acceptance_method': acceptance_method,
            'ip_address': 'internal',  # Could be enhanced with actual IP tracking
            'user_agent': 'SPANKKS Construction System'
        }
        
        activity_log.append(log_entry)
        self._save_json_file(log_file, activity_log)
        
        self.logger.info(f"Quote {quote_id} accepted by {client_signature} via {acceptance_method}")
    
    def get_pending_quotes(self) -> List[Dict]:
        """Get all pending quotes that can be accepted"""
        quotes = self._load_json_file('quotes.json')
        current_date = self._get_hawaii_time().strftime('%Y-%m-%d')
        
        pending_quotes = []
        for quote in quotes:
            if (quote.get('status') == 'pending' and 
                quote.get('valid_until', '9999-12-31') >= current_date):
                
                # Add contact information
                contacts = self._load_json_file('contacts.json')
                contact = next((c for c in contacts if c.get('id') == quote.get('contact_id')), {})
                
                quote_with_contact = quote.copy()
                quote_with_contact['contact_name'] = contact.get('name', 'Unknown')
                quote_with_contact['contact_phone'] = contact.get('phone', '')
                quote_with_contact['contact_email'] = contact.get('email', '')
                
                pending_quotes.append(quote_with_contact)
        
        return pending_quotes
    
    def get_acceptance_statistics(self) -> Dict[str, Any]:
        """Get quote acceptance statistics for analytics"""
        quotes = self._load_json_file('quotes.json')
        current_time = self._get_hawaii_time()
        
        total_quotes = len(quotes)
        accepted_quotes = len([q for q in quotes if q.get('status') == 'accepted'])
        pending_quotes = len([q for q in quotes if q.get('status') == 'pending'])
        expired_quotes = len([q for q in quotes if q.get('valid_until', '9999-12-31') < current_time.strftime('%Y-%m-%d')])
        
        # Calculate conversion rate
        conversion_rate = (accepted_quotes / total_quotes * 100) if total_quotes > 0 else 0
        
        # Get acceptance methods breakdown
        acceptance_methods = {}
        for quote in quotes:
            if quote.get('status') == 'accepted':
                method = quote.get('acceptance_method', 'unknown')
                acceptance_methods[method] = acceptance_methods.get(method, 0) + 1
        
        return {
            'total_quotes': total_quotes,
            'accepted_quotes': accepted_quotes,
            'pending_quotes': pending_quotes,
            'expired_quotes': expired_quotes,
            'conversion_rate': round(conversion_rate, 2),
            'acceptance_methods': acceptance_methods,
            'last_updated': current_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def process_bulk_quote_acceptance(self, quote_acceptances: List[Dict]) -> Dict[str, Any]:
        """Process multiple quote acceptances in bulk"""
        results = {
            'successful': [],
            'failed': [],
            'total_processed': len(quote_acceptances)
        }
        
        for acceptance in quote_acceptances:
            try:
                result = self.accept_quote(
                    quote_id=acceptance['quote_id'],
                    client_signature=acceptance['client_signature'],
                    acceptance_method=acceptance.get('acceptance_method', 'bulk_import')
                )
                
                if result['success']:
                    results['successful'].append(result)
                else:
                    results['failed'].append({
                        'quote_id': acceptance['quote_id'],
                        'error': result['error']
                    })
                    
            except Exception as e:
                results['failed'].append({
                    'quote_id': acceptance.get('quote_id', 'unknown'),
                    'error': str(e)
                })
        
        return results