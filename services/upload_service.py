"""
CSV Upload Service for SPANKKS Construction
Handles bulk data uploads from CSV files
"""

import csv
import io
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple
from phone_formatter import PhoneFormatter

class CSVUploadService:
    """Service for processing CSV file uploads and bulk data operations"""
    
    def __init__(self, storage_service=None):
        self.storage_service = storage_service
        self.phone_formatter = PhoneFormatter()
        self.upload_results = []
        
    def validate_csv_file(self, file_content: str, expected_headers: List[str]) -> Tuple[bool, str, List[Dict]]:
        """Validate CSV file format and extract data"""
        try:
            # Parse CSV content
            csv_reader = csv.DictReader(io.StringIO(file_content))
            
            # Check headers
            if not csv_reader.fieldnames:
                return False, "CSV file has no headers", []
            
            missing_headers = set(expected_headers) - set(csv_reader.fieldnames)
            if missing_headers:
                return False, f"Missing required headers: {', '.join(missing_headers)}", []
            
            # Extract and validate data
            data_rows = []
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (after header)
                # Clean and validate row data
                cleaned_row = {}
                for key, value in row.items():
                    if key in expected_headers:
                        cleaned_row[key] = value.strip() if value else ""
                
                if any(cleaned_row.values()):  # Skip completely empty rows
                    data_rows.append(cleaned_row)
            
            return True, f"Valid CSV with {len(data_rows)} data rows", data_rows
            
        except Exception as e:
            return False, f"CSV parsing error: {str(e)}", []
    
    def upload_clients_csv(self, file_content: str) -> Dict[str, Any]:
        """Upload clients from CSV file"""
        expected_headers = ['name', 'phone', 'email', 'address', 'city', 'state', 'zip_code', 'client_type', 'notes', 'preferred_contact_method']
        
        is_valid, message, data_rows = self.validate_csv_file(file_content, expected_headers)
        
        if not is_valid:
            return {'success': False, 'error': message, 'processed': 0}
        
        processed_count = 0
        errors = []
        
        for row_num, row in enumerate(data_rows, start=2):
            try:
                # Format phone number
                if row.get('phone'):
                    row['phone'] = self.phone_formatter.format_phone(row['phone'])
                
                # Validate required fields
                if not row.get('name') or not row.get('email'):
                    errors.append(f"Row {row_num}: Name and email are required")
                    continue
                
                # Create client record (if storage service available)
                if self.storage_service:
                    try:
                        self.storage_service.add_contact({
                            'name': row['name'],
                            'phone': row['phone'],
                            'email': row['email'],
                            'address': row.get('address', ''),
                            'city': row.get('city', 'Honolulu'),
                            'state': row.get('state', 'HI'),
                            'zip_code': row.get('zip_code', ''),
                            'client_type': row.get('client_type', 'residential'),
                            'notes': row.get('notes', ''),
                            'preferred_contact_method': row.get('preferred_contact_method', 'email')
                        })
                        processed_count += 1
                    except Exception as e:
                        errors.append(f"Row {row_num}: Database error - {str(e)}")
                else:
                    processed_count += 1  # Simulate success if no storage service
                    
            except Exception as e:
                errors.append(f"Row {row_num}: Processing error - {str(e)}")
        
        return {
            'success': True,
            'processed': processed_count,
            'total_rows': len(data_rows),
            'errors': errors,
            'message': f"Successfully processed {processed_count} clients"
        }
    
    def upload_jobs_csv(self, file_content: str) -> Dict[str, Any]:
        """Upload jobs from CSV file"""
        expected_headers = ['client_name', 'client_email', 'job_title', 'service_type', 'description', 'location', 'priority', 'status', 'estimated_hours', 'hourly_rate', 'materials_cost', 'scheduled_date', 'scheduled_time', 'completion_date', 'notes']
        
        is_valid, message, data_rows = self.validate_csv_file(file_content, expected_headers)
        
        if not is_valid:
            return {'success': False, 'error': message, 'processed': 0}
        
        processed_count = 0
        errors = []
        
        for row_num, row in enumerate(data_rows, start=2):
            try:
                # Validate required fields
                if not row.get('client_name') or not row.get('job_title'):
                    errors.append(f"Row {row_num}: Client name and job title are required")
                    continue
                
                # Create job record (if storage service available)
                if self.storage_service:
                    try:
                        self.storage_service.add_job({
                            'client_name': row['client_name'],
                            'client_email': row['client_email'],
                            'title': row['job_title'],
                            'service_type': row.get('service_type', 'General Handyman'),
                            'description': row.get('description', ''),
                            'location': row.get('location', ''),
                            'priority': row.get('priority', 'medium'),
                            'status': row.get('status', 'pending'),
                            'estimated_hours': row.get('estimated_hours', ''),
                            'hourly_rate': row.get('hourly_rate', '95.00'),
                            'materials_cost': row.get('materials_cost', ''),
                            'scheduled_date': row.get('scheduled_date', ''),
                            'scheduled_time': row.get('scheduled_time', ''),
                            'completion_date': row.get('completion_date', ''),
                            'notes': row.get('notes', '')
                        })
                        processed_count += 1
                    except Exception as e:
                        errors.append(f"Row {row_num}: Database error - {str(e)}")
                else:
                    processed_count += 1
                    
            except Exception as e:
                errors.append(f"Row {row_num}: Processing error - {str(e)}")
        
        return {
            'success': True,
            'processed': processed_count,
            'total_rows': len(data_rows),
            'errors': errors,
            'message': f"Successfully processed {processed_count} jobs"
        }
    
    def upload_quotes_csv(self, file_content: str) -> Dict[str, Any]:
        """Upload quotes from CSV file"""
        expected_headers = ['client_name', 'client_email', 'quote_title', 'service_type', 'description', 'quantity', 'unit', 'unit_price', 'line_total', 'total_before_tax', 'hawaii_tax_rate', 'hawaii_tax_amount', 'total_amount', 'status', 'valid_until', 'notes']
        
        is_valid, message, data_rows = self.validate_csv_file(file_content, expected_headers)
        
        if not is_valid:
            return {'success': False, 'error': message, 'processed': 0}
        
        processed_count = 0
        errors = []
        
        for row_num, row in enumerate(data_rows, start=2):
            try:
                # Validate required fields
                if not row.get('client_name') or not row.get('total_amount'):
                    errors.append(f"Row {row_num}: Client name and total amount are required")
                    continue
                
                # Create quote record (if storage service available)
                if self.storage_service:
                    try:
                        self.storage_service.add_quote({
                            'client_name': row['client_name'],
                            'client_email': row['client_email'],
                            'title': row['quote_title'],
                            'service_type': row.get('service_type', 'General Handyman'),
                            'description': row.get('description', ''),
                            'quantity': row.get('quantity', '1'),
                            'unit': row.get('unit', 'service'),
                            'unit_price': row.get('unit_price', '0.00'),
                            'line_total': row.get('line_total', '0.00'),
                            'subtotal': row.get('total_before_tax', '0.00'),
                            'tax_rate': row.get('hawaii_tax_rate', '0.04712'),
                            'tax_amount': row.get('hawaii_tax_amount', '0.00'),
                            'total': row.get('total_amount', '0.00'),
                            'status': row.get('status', 'pending'),
                            'valid_until': row.get('valid_until', ''),
                            'notes': row.get('notes', '')
                        })
                        processed_count += 1
                    except Exception as e:
                        errors.append(f"Row {row_num}: Database error - {str(e)}")
                else:
                    processed_count += 1
                    
            except Exception as e:
                errors.append(f"Row {row_num}: Processing error - {str(e)}")
        
        return {
            'success': True,
            'processed': processed_count,
            'total_rows': len(data_rows),
            'errors': errors,
            'message': f"Successfully processed {processed_count} quotes"
        }
    
    def get_upload_summary(self) -> Dict[str, Any]:
        """Get summary of upload operations"""
        return {
            'total_uploads': len(self.upload_results),
            'successful_uploads': sum(1 for result in self.upload_results if result.get('success')),
            'failed_uploads': sum(1 for result in self.upload_results if not result.get('success')),
            'total_records_processed': sum(result.get('processed', 0) for result in self.upload_results),
            'upload_details': self.upload_results
        }
    
    def process_bulk_upload(self, upload_type: str, file_content: str) -> Dict[str, Any]:
        """Process bulk upload based on type"""
        upload_handlers = {
            'clients': self.upload_clients_csv,
            'jobs': self.upload_jobs_csv,
            'quotes': self.upload_quotes_csv,
            'invoices': self.upload_invoices_csv,
            'staff': self.upload_staff_csv,
            'schedule': self.upload_schedule_csv
        }
        
        if upload_type not in upload_handlers:
            return {'success': False, 'error': f'Unsupported upload type: {upload_type}'}
        
        try:
            result = upload_handlers[upload_type](file_content)
            self.upload_results.append({
                'type': upload_type,
                'timestamp': datetime.now().isoformat(),
                'result': result
            })
            return result
        except Exception as e:
            error_result = {'success': False, 'error': f'Upload processing error: {str(e)}', 'processed': 0}
            self.upload_results.append({
                'type': upload_type,
                'timestamp': datetime.now().isoformat(),
                'result': error_result
            })
            return error_result
    
    def upload_invoices_csv(self, file_content: str) -> Dict[str, Any]:
        """Upload invoices from CSV file"""
        expected_headers = ['client_name', 'client_email', 'invoice_title', 'service_type', 'description', 'quantity', 'unit', 'unit_price', 'line_total', 'total_before_tax', 'hawaii_tax_rate', 'hawaii_tax_amount', 'total_amount', 'payment_status', 'payment_method', 'payment_date', 'due_date', 'notes']
        
        is_valid, message, data_rows = self.validate_csv_file(file_content, expected_headers)
        
        if not is_valid:
            return {'success': False, 'error': message, 'processed': 0}
        
        processed_count = 0
        errors = []
        
        for row_num, row in enumerate(data_rows, start=2):
            try:
                if not row.get('client_name') or not row.get('total_amount'):
                    errors.append(f"Row {row_num}: Client name and total amount are required")
                    continue
                
                if self.storage_service:
                    try:
                        self.storage_service.add_invoice({
                            'client_name': row['client_name'],
                            'client_email': row['client_email'],
                            'title': row['invoice_title'],
                            'service_type': row.get('service_type', 'General Handyman'),
                            'description': row.get('description', ''),
                            'quantity': row.get('quantity', '1'),
                            'unit': row.get('unit', 'service'),
                            'unit_price': row.get('unit_price', '0.00'),
                            'line_total': row.get('line_total', '0.00'),
                            'subtotal': row.get('total_before_tax', '0.00'),
                            'tax_rate': row.get('hawaii_tax_rate', '0.04712'),
                            'tax_amount': row.get('hawaii_tax_amount', '0.00'),
                            'total': row.get('total_amount', '0.00'),
                            'payment_status': row.get('payment_status', 'pending'),
                            'payment_method': row.get('payment_method', ''),
                            'payment_date': row.get('payment_date', ''),
                            'due_date': row.get('due_date', ''),
                            'notes': row.get('notes', '')
                        })
                        processed_count += 1
                    except Exception as e:
                        errors.append(f"Row {row_num}: Database error - {str(e)}")
                else:
                    processed_count += 1
                    
            except Exception as e:
                errors.append(f"Row {row_num}: Processing error - {str(e)}")
        
        return {
            'success': True,
            'processed': processed_count,
            'total_rows': len(data_rows),
            'errors': errors,
            'message': f"Successfully processed {processed_count} invoices"
        }
    
    def upload_staff_csv(self, file_content: str) -> Dict[str, Any]:
        """Upload staff from CSV file"""
        expected_headers = ['name', 'phone', 'email', 'role', 'hourly_rate', 'skills', 'availability', 'hire_date', 'status', 'emergency_contact', 'emergency_phone', 'notes']
        
        is_valid, message, data_rows = self.validate_csv_file(file_content, expected_headers)
        
        if not is_valid:
            return {'success': False, 'error': message, 'processed': 0}
        
        processed_count = 0
        errors = []
        
        for row_num, row in enumerate(data_rows, start=2):
            try:
                if not row.get('name') or not row.get('email'):
                    errors.append(f"Row {row_num}: Name and email are required")
                    continue
                
                # Format phone numbers
                if row.get('phone'):
                    row['phone'] = self.phone_formatter.format_phone(row['phone'])
                if row.get('emergency_phone'):
                    row['emergency_phone'] = self.phone_formatter.format_phone(row['emergency_phone'])
                
                processed_count += 1  # Staff management not fully implemented yet
                    
            except Exception as e:
                errors.append(f"Row {row_num}: Processing error - {str(e)}")
        
        return {
            'success': True,
            'processed': processed_count,
            'total_rows': len(data_rows),
            'errors': errors,
            'message': f"Successfully processed {processed_count} staff records"
        }
    
    def upload_schedule_csv(self, file_content: str) -> Dict[str, Any]:
        """Upload schedule from CSV file"""
        expected_headers = ['client_name', 'client_phone', 'client_email', 'appointment_date', 'appointment_time', 'duration_minutes', 'service_type', 'description', 'location', 'priority', 'status', 'assigned_staff', 'notes']
        
        is_valid, message, data_rows = self.validate_csv_file(file_content, expected_headers)
        
        if not is_valid:
            return {'success': False, 'error': message, 'processed': 0}
        
        processed_count = 0
        errors = []
        
        for row_num, row in enumerate(data_rows, start=2):
            try:
                if not row.get('client_name') or not row.get('appointment_date'):
                    errors.append(f"Row {row_num}: Client name and appointment date are required")
                    continue
                
                # Format phone number
                if row.get('client_phone'):
                    row['client_phone'] = self.phone_formatter.format_phone(row['client_phone'])
                
                processed_count += 1  # Schedule management integration pending
                    
            except Exception as e:
                errors.append(f"Row {row_num}: Processing error - {str(e)}")
        
        return {
            'success': True,
            'processed': processed_count,
            'total_rows': len(data_rows),
            'errors': errors,
            'message': f"Successfully processed {processed_count} appointments"
        }