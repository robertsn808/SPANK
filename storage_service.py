import json
import os
from datetime import datetime
import logging
from typing import List, Optional

class StorageService:
    """Comprehensive storage service for SPANKKS Construction CRM"""

    def __init__(self):
        self.data_dir = "data"
        self.ensure_data_directory()

    def ensure_data_directory(self):
        """Ensure data directory and required files exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logging.info(f"Created data directory: {self.data_dir}")

        # Initialize empty files if they don't exist
        files = ['contacts.json', 'jobs.json', 'quotes.json', 'invoices.json', 
                'service_requests.json', 'contact_messages.json']
        for file in files:
            filepath = os.path.join(self.data_dir, file)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    json.dump([], f)
                logging.info(f"Created empty data file: {file}")

    def load_data(self, filename: str) -> List[dict]:
        """Load data from JSON file with error handling"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    logging.debug(f"Loaded {len(data)} records from {filename}")
                    return data
            return []
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error loading {filename}: {e}")
            return []

    def save_data(self, filename: str, data: List[dict]) -> bool:
        """Save data to JSON file with error handling"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logging.debug(f"Saved {len(data)} records to {filename}")
            return True
        except Exception as e:
            logging.error(f"Error saving {filename}: {e}")
            return False

    def log_payment(self, payment_data: dict) -> bool:
        """Log payment transaction for financial tracking"""
        try:
            payments = self.load_data('payments.json')
            payment_data['logged_at'] = datetime.now().isoformat()
            payment_data['id'] = f"PAY-{len(payments) + 1:04d}"
            payments.append(payment_data)
            return self.save_data('payments.json', payments)
        except Exception as e:
            logging.error(f"Error logging payment: {e}")
            return False

    def get_all_contacts(self) -> List[dict]:
        """Get all contacts from storage"""
        return self.load_data('contacts.json')

    def add_contact(self, contact_data: dict) -> dict:
        """Add new contact to storage"""
        contacts = self.load_data('contacts.json')
        contact_data['id'] = f"CLI{len(contacts) + 1:03d}"
        contact_data['created_at'] = datetime.now().isoformat()
        contacts.append(contact_data)
        self.save_data('contacts.json', contacts)
        return contact_data

    def get_contact_by_id(self, contact_id: str) -> Optional[dict]:
        """Get contact by ID"""
        contacts = self.load_data('contacts.json')
        for contact in contacts:
            if contact.get('id') == contact_id:
                return contact
        return None

    def get_all_quotes(self) -> List[dict]:
        """Get all quotes from storage"""
        return self.load_data('quotes.json')

    def add_quote(self, quote_data: dict) -> dict:
        """Add new quote to storage"""
        quotes = self.load_data('quotes.json')
        quote_data['id'] = f"Q2025-{len(quotes) + 1:03d}"
        quote_data['created_at'] = datetime.now().isoformat()
        quotes.append(quote_data)
        self.save_data('quotes.json', quotes)
        return quote_data

    def get_quotes_by_contact(self, contact_id: str) -> List[dict]:
        """Get all quotes for a specific contact"""
        quotes = self.load_data('quotes.json')
        return [q for q in quotes if q.get('client_id') == contact_id]

    def get_all_invoices(self) -> List[dict]:
        """Get all invoices from storage"""
        return self.load_data('invoices.json')

    def add_invoice(self, invoice_data: dict) -> dict:
        """Add new invoice to storage"""
        invoices = self.load_data('invoices.json')
        invoice_data['id'] = f"I2025-{len(invoices) + 1:03d}"
        invoice_data['created_at'] = datetime.now().isoformat()
        invoices.append(invoice_data)
        self.save_data('invoices.json', invoices)
        return invoice_data

    def get_invoices_by_contact(self, contact_id: str) -> List[dict]:
        """Get all invoices for a specific contact"""
        invoices = self.load_data('invoices.json')
        return [i for i in invoices if i.get('client_id') == contact_id]

    def get_all_jobs(self) -> List[dict]:
        """Get all jobs from storage"""
        return self.load_data('jobs.json')

    def add_job(self, job_data: dict) -> dict:
        """Add new job to storage"""
        jobs = self.load_data('jobs.json')
        job_data['id'] = f"JOB{len(jobs) + 1:03d}"
        job_data['created_at'] = datetime.now().isoformat()
        jobs.append(job_data)
        self.save_data('jobs.json', jobs)
        return job_data

    def get_jobs_by_contact(self, contact_id: str) -> List[dict]:
        """Get all jobs for a specific contact"""
        jobs = self.load_data('jobs.json')
        return [j for j in jobs if j.get('client_id') == contact_id]

    def update_job_status(self, job_id: str, status: str) -> bool:
        """Update job status"""
        jobs = self.load_data('jobs.json')
        for job in jobs:
            if job.get('id') == job_id:
                job['status'] = status
                job['updated_at'] = datetime.now().isoformat()
                return self.save_data('jobs.json', jobs)
        return False

    def add_job_note(self, job_id: str, note: str) -> bool:
        """Add note to job"""
        jobs = self.load_data('jobs.json')
        for job in jobs:
            if job.get('id') == job_id:
                if 'notes' not in job:
                    job['notes'] = []
                job['notes'].append({
                    'note': note,
                    'timestamp': datetime.now().isoformat()
                })
                return self.save_data('jobs.json', jobs)
        return False

    def update_quote_status(self, quote_id: str, status: str) -> bool:
        """Update quote status"""
        quotes = self.load_data('quotes.json')
        for quote in quotes:
            if quote.get('id') == quote_id:
                quote['status'] = status
                quote['updated_at'] = datetime.now().isoformat()
                return self.save_data('quotes.json', quotes)
        return False

# Global storage instance
storage_service = StorageService()