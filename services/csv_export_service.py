"""
CSV Export Service for SPANKKS Construction
Generates CSV templates and exports for bulk data operations
"""

import csv
import io
import zipfile
import os
from datetime import datetime
from typing import Dict, List, Any

class CSVExportService:
    """Service for generating CSV templates and data exports"""
    
    def __init__(self):
        self.templates_dir = "csv_templates"
        
    def get_available_templates(self) -> List[Dict[str, str]]:
        """Get list of available CSV templates"""
        templates = [
            {
                "name": "clients_template.csv",
                "title": "Client Database Template",
                "description": "Upload client contact information and preferences",
                "fields": "name, phone, email, address, city, state, zip_code, client_type, notes, preferred_contact_method"
            },
            {
                "name": "jobs_template.csv", 
                "title": "Jobs Database Template",
                "description": "Upload job records with service details and scheduling",
                "fields": "client_name, client_email, job_title, service_type, description, location, priority, status, estimated_hours, hourly_rate, materials_cost, scheduled_date, scheduled_time, completion_date, notes"
            },
            {
                "name": "schedule_template.csv",
                "title": "Schedule/Appointments Template", 
                "description": "Upload appointment and scheduling data",
                "fields": "client_name, client_phone, client_email, appointment_date, appointment_time, duration_minutes, service_type, description, location, priority, status, assigned_staff, notes"
            },
            {
                "name": "service_types_template.csv",
                "title": "Service Types & Pricing Template",
                "description": "Upload service categories with pricing and specifications", 
                "fields": "service_name, category, base_hourly_rate, unit_type, unit_price, estimated_hours, description, materials_included, equipment_required, skill_level"
            },
            {
                "name": "staff_template.csv",
                "title": "Staff Database Template",
                "description": "Upload employee information and availability",
                "fields": "name, phone, email, role, hourly_rate, skills, availability, hire_date, status, emergency_contact, emergency_phone, notes"
            },
            {
                "name": "quotes_template.csv",
                "title": "Quotes Database Template", 
                "description": "Upload quote records with Hawaii tax calculations",
                "fields": "client_name, client_email, quote_title, service_type, description, quantity, unit, unit_price, line_total, total_before_tax, hawaii_tax_rate, hawaii_tax_amount, total_amount, status, valid_until, notes"
            },
            {
                "name": "invoices_template.csv",
                "title": "Invoices Database Template",
                "description": "Upload invoice records with payment tracking", 
                "fields": "client_name, client_email, invoice_title, service_type, description, quantity, unit, unit_price, line_total, total_before_tax, hawaii_tax_rate, hawaii_tax_amount, total_amount, payment_status, payment_method, payment_date, due_date, notes"
            }
        ]
        return templates
    
    def get_template_content(self, template_name: str) -> str:
        """Get CSV template file content"""
        try:
            template_path = os.path.join(self.templates_dir, template_name)
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return self._generate_empty_template(template_name)
        except Exception as e:
            return f"Error loading template: {str(e)}"
    
    def generate_all_templates_zip(self) -> bytes:
        """Generate ZIP file containing all CSV templates"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add all template files
            for template in self.get_available_templates():
                template_name = template['name']
                content = self.get_template_content(template_name)
                zip_file.writestr(template_name, content)
            
            # Add README file
            readme_path = os.path.join(self.templates_dir, "README.md")
            if os.path.exists(readme_path):
                with open(readme_path, 'r', encoding='utf-8') as f:
                    zip_file.writestr("README.md", f.read())
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    def export_current_data_csv(self, data_type: str, storage_service) -> str:
        """Export current database data to CSV format"""
        try:
            if data_type == "clients":
                return self._export_clients_data(storage_service)
            elif data_type == "jobs": 
                return self._export_jobs_data(storage_service)
            elif data_type == "schedule":
                return self._export_schedule_data(storage_service)
            elif data_type == "staff":
                return self._export_staff_data(storage_service)
            elif data_type == "quotes":
                return self._export_quotes_data(storage_service)
            elif data_type == "invoices":
                return self._export_invoices_data(storage_service)
            else:
                return "Error: Invalid data type"
        except Exception as e:
            return f"Error exporting data: {str(e)}"
    
    def _export_clients_data(self, storage_service) -> str:
        """Export current clients to CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['name', 'phone', 'email', 'address', 'city', 'state', 'zip_code', 'client_type', 'notes', 'preferred_contact_method'])
        
        # Get current clients
        try:
            contacts = storage_service.get_all_contacts() if storage_service else []
            for contact in contacts:
                writer.writerow([
                    getattr(contact, 'name', ''),
                    getattr(contact, 'phone', ''),
                    getattr(contact, 'email', ''),
                    getattr(contact, 'address', ''),
                    getattr(contact, 'city', 'Honolulu'),
                    getattr(contact, 'state', 'HI'),
                    getattr(contact, 'zip_code', '96814'),
                    getattr(contact, 'client_type', 'residential'),
                    getattr(contact, 'notes', ''),
                    getattr(contact, 'preferred_contact_method', 'email')
                ])
        except Exception as e:
            writer.writerow(['# Error loading clients:', str(e)])
        
        return output.getvalue()
    
    def _export_jobs_data(self, storage_service) -> str:
        """Export current jobs to CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['client_name', 'client_email', 'job_title', 'service_type', 'description', 'location', 'priority', 'status', 'estimated_hours', 'hourly_rate', 'materials_cost', 'scheduled_date', 'scheduled_time', 'completion_date', 'notes'])
        
        # Get current jobs
        try:
            jobs = storage_service.get_all_jobs() if storage_service else []
            for job in jobs:
                writer.writerow([
                    getattr(job, 'client_name', ''),
                    getattr(job, 'client_email', ''),
                    getattr(job, 'title', ''),
                    getattr(job, 'service_type', ''),
                    getattr(job, 'description', ''),
                    getattr(job, 'location', ''),
                    getattr(job, 'priority', 'medium'),
                    getattr(job, 'status', 'pending'),
                    getattr(job, 'estimated_hours', ''),
                    getattr(job, 'hourly_rate', '95.00'),
                    getattr(job, 'materials_cost', ''),
                    getattr(job, 'scheduled_date', ''),
                    getattr(job, 'scheduled_time', ''),
                    getattr(job, 'completion_date', ''),
                    getattr(job, 'notes', '')
                ])
        except Exception as e:
            writer.writerow(['# Error loading jobs:', str(e)])
        
        return output.getvalue()
    
    def _export_quotes_data(self, storage_service) -> str:
        """Export current quotes to CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header  
        writer.writerow(['client_name', 'client_email', 'quote_title', 'service_type', 'description', 'quantity', 'unit', 'unit_price', 'line_total', 'total_before_tax', 'hawaii_tax_rate', 'hawaii_tax_amount', 'total_amount', 'status', 'valid_until', 'notes'])
        
        # Get current quotes
        try:
            quotes = storage_service.get_all_quotes() if storage_service else []
            for quote in quotes:
                writer.writerow([
                    getattr(quote, 'client_name', ''),
                    getattr(quote, 'client_email', ''),
                    getattr(quote, 'title', ''),
                    getattr(quote, 'service_type', ''),
                    getattr(quote, 'description', ''),
                    getattr(quote, 'quantity', '1'),
                    getattr(quote, 'unit', 'service'),
                    getattr(quote, 'unit_price', ''),
                    getattr(quote, 'line_total', ''),
                    getattr(quote, 'subtotal', ''),
                    '0.04712',
                    getattr(quote, 'tax_amount', ''),
                    getattr(quote, 'total', ''),
                    getattr(quote, 'status', 'pending'),
                    getattr(quote, 'valid_until', ''),
                    getattr(quote, 'notes', '')
                ])
        except Exception as e:
            writer.writerow(['# Error loading quotes:', str(e)])
        
        return output.getvalue()
    
    def _export_schedule_data(self, storage_service) -> str:
        """Export current schedule to CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['client_name', 'client_phone', 'client_email', 'appointment_date', 'appointment_time', 'duration_minutes', 'service_type', 'description', 'location', 'priority', 'status', 'assigned_staff', 'notes'])
        
        # Get current appointments/schedule
        try:
            # This would connect to the real scheduler data
            writer.writerow(['# No appointments currently scheduled'])
        except Exception as e:
            writer.writerow(['# Error loading schedule:', str(e)])
        
        return output.getvalue()
    
    def _export_staff_data(self, storage_service) -> str:
        """Export current staff to CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['name', 'phone', 'email', 'role', 'hourly_rate', 'skills', 'availability', 'hire_date', 'status', 'emergency_contact', 'emergency_phone', 'notes'])
        
        # Get current staff 
        try:
            # This would connect to the real staff data
            writer.writerow(['# No staff records currently in system'])
        except Exception as e:
            writer.writerow(['# Error loading staff:', str(e)])
        
        return output.getvalue()
    
    def _export_invoices_data(self, storage_service) -> str:
        """Export current invoices to CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['client_name', 'client_email', 'invoice_title', 'service_type', 'description', 'quantity', 'unit', 'unit_price', 'line_total', 'total_before_tax', 'hawaii_tax_rate', 'hawaii_tax_amount', 'total_amount', 'payment_status', 'payment_method', 'payment_date', 'due_date', 'notes'])
        
        # Get current invoices
        try:
            invoices = storage_service.get_all_invoices() if storage_service else []
            for invoice in invoices:
                writer.writerow([
                    getattr(invoice, 'client_name', ''),
                    getattr(invoice, 'client_email', ''),
                    getattr(invoice, 'title', ''),
                    getattr(invoice, 'service_type', ''),
                    getattr(invoice, 'description', ''),
                    getattr(invoice, 'quantity', '1'),
                    getattr(invoice, 'unit', 'service'),
                    getattr(invoice, 'unit_price', ''),
                    getattr(invoice, 'line_total', ''),
                    getattr(invoice, 'subtotal', ''),
                    '0.04712',
                    getattr(invoice, 'tax_amount', ''),
                    getattr(invoice, 'total', ''),
                    getattr(invoice, 'payment_status', 'pending'),
                    getattr(invoice, 'payment_method', ''),
                    getattr(invoice, 'payment_date', ''),
                    getattr(invoice, 'due_date', ''),
                    getattr(invoice, 'notes', '')
                ])
        except Exception as e:
            writer.writerow(['# Error loading invoices:', str(e)])
        
        return output.getvalue()
    
    def _generate_empty_template(self, template_name: str) -> str:
        """Generate empty template if file doesn't exist"""
        templates = {
            "clients_template.csv": "name,phone,email,address,city,state,zip_code,client_type,notes,preferred_contact_method\n",
            "jobs_template.csv": "client_name,client_email,job_title,service_type,description,location,priority,status,estimated_hours,hourly_rate,materials_cost,scheduled_date,scheduled_time,completion_date,notes\n",
            "schedule_template.csv": "client_name,client_phone,client_email,appointment_date,appointment_time,duration_minutes,service_type,description,location,priority,status,assigned_staff,notes\n",
            "service_types_template.csv": "service_name,category,base_hourly_rate,unit_type,unit_price,estimated_hours,description,materials_included,equipment_required,skill_level\n",
            "staff_template.csv": "name,phone,email,role,hourly_rate,skills,availability,hire_date,status,emergency_contact,emergency_phone,notes\n", 
            "quotes_template.csv": "client_name,client_email,quote_title,service_type,description,quantity,unit,unit_price,line_total,total_before_tax,hawaii_tax_rate,hawaii_tax_amount,total_amount,status,valid_until,notes\n",
            "invoices_template.csv": "client_name,client_email,invoice_title,service_type,description,quantity,unit,unit_price,line_total,total_before_tax,hawaii_tax_rate,hawaii_tax_amount,total_amount,payment_status,payment_method,payment_date,due_date,notes\n"
        }
        return templates.get(template_name, "# Template not found\n")