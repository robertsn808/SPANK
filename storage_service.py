
import json
import os
from datetime import datetime
from models import Contact, Job, Quote, Invoice
from typing import List, Optional

class StorageService:
    """Simple JSON-based storage service for SPANKKS Construction CRM"""
    
    def __init__(self):
        self.data_dir = "data"
        self.ensure_data_directory()
        
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # Initialize empty files if they don't exist
        files = ['contacts.json', 'jobs.json', 'quotes.json', 'invoices.json']
        for file in files:
            filepath = os.path.join(self.data_dir, file)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    json.dump([], f)
    
    def _load_data(self, filename: str) -> List[dict]:
        """Load data from JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_data(self, filename: str, data: List[dict]):
        """Save data to JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    # Contact methods
    def get_all_contacts(self) -> List[Contact]:
        """Get all contacts"""
        data = self._load_data('contacts.json')
        return [Contact(**item) for item in data]
    
    def save_contact(self, contact: Contact) -> Contact:
        """Save a contact"""
        contacts = self._load_data('contacts.json')
        contact_dict = contact.__dict__.copy()
        
        # Add or update contact
        if hasattr(contact, 'id') and contact.id:
            # Update existing
            for i, c in enumerate(contacts):
                if c.get('id') == contact.id:
                    contacts[i] = contact_dict
                    break
        else:
            # Add new
            contact.id = len(contacts) + 1
            contact_dict['id'] = contact.id
            contacts.append(contact_dict)
        
        self._save_data('contacts.json', contacts)
        return contact
    
    # Job methods
    def get_all_jobs(self) -> List[Job]:
        """Get all jobs"""
        data = self._load_data('jobs.json')
        return [Job(**item) for item in data]
    
    def save_job(self, job: Job) -> Job:
        """Save a job"""
        jobs = self._load_data('jobs.json')
        job_dict = job.__dict__.copy()
        
        if hasattr(job, 'id') and job.id:
            for i, j in enumerate(jobs):
                if j.get('id') == job.id:
                    jobs[i] = job_dict
                    break
        else:
            job.id = len(jobs) + 1
            job_dict['id'] = job.id
            jobs.append(job_dict)
        
        self._save_data('jobs.json', jobs)
        return job
    
    # Quote methods
    def get_all_quotes(self) -> List[Quote]:
        """Get all quotes"""
        data = self._load_data('quotes.json')
        return [Quote(**item) for item in data]
    
    def save_quote(self, quote: Quote) -> Quote:
        """Save a quote"""
        quotes = self._load_data('quotes.json')
        quote_dict = quote.__dict__.copy()
        
        if hasattr(quote, 'id') and quote.id:
            for i, q in enumerate(quotes):
                if q.get('id') == quote.id:
                    quotes[i] = quote_dict
                    break
        else:
            quote.id = len(quotes) + 1
            quote_dict['id'] = quote.id
            quotes.append(quote_dict)
        
        self._save_data('quotes.json', quotes)
        return quote
    
    # Invoice methods
    def get_all_invoices(self) -> List[Invoice]:
        """Get all invoices"""
        data = self._load_data('invoices.json')
        return [Invoice(**item) for item in data]
    
    def save_invoice(self, invoice: Invoice) -> Invoice:
        """Save an invoice"""
        invoices = self._load_data('invoices.json')
        invoice_dict = invoice.__dict__.copy()
        
        if hasattr(invoice, 'id') and invoice.id:
            for i, inv in enumerate(invoices):
                if inv.get('id') == invoice.id:
                    invoices[i] = invoice_dict
                    break
        else:
            invoice.id = len(invoices) + 1
            invoice_dict['id'] = invoice.id
            invoices.append(invoice_dict)
        
        self._save_data('invoices.json', invoices)
        return invoice

# Global storage instance
storage = StorageService()
