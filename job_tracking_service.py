"""
Job Records and Payment Tracking System for SPANKKS Construction
Comprehensive tracking for quotes, estimates, materials, labor, and manual payments
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid
from phone_formatter import PhoneFormatter

class JobTrackingService:
    """Comprehensive job records and payment tracking system"""
    
    def __init__(self):
        self.phone_formatter = PhoneFormatter()
        self.data_dir = 'data'
        self.jobs_file = os.path.join(self.data_dir, 'job_records.json')
        self.quotes_file = os.path.join(self.data_dir, 'quote_history.json')
        self.payments_file = os.path.join(self.data_dir, 'payment_logs.json')
        self.materials_file = os.path.join(self.data_dir, 'material_logs.json')
        self.labor_file = os.path.join(self.data_dir, 'labor_logs.json')
        
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Ensure all data files exist with proper structure"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize job records
        if not os.path.exists(self.jobs_file):
            with open(self.jobs_file, 'w') as f:
                json.dump([], f, indent=2)
        
        # Initialize quote history
        if not os.path.exists(self.quotes_file):
            with open(self.quotes_file, 'w') as f:
                json.dump([], f, indent=2)
        
        # Initialize payment logs
        if not os.path.exists(self.payments_file):
            with open(self.payments_file, 'w') as f:
                json.dump([], f, indent=2)
        
        # Initialize material logs
        if not os.path.exists(self.materials_file):
            with open(self.materials_file, 'w') as f:
                json.dump([], f, indent=2)
        
        # Initialize labor logs
        if not os.path.exists(self.labor_file):
            with open(self.labor_file, 'w') as f:
                json.dump([], f, indent=2)
    
    def generate_job_id(self) -> str:
        """Generate unique job ID in format J2025-XXXX"""
        jobs = self._load_jobs()
        year = datetime.now().year
        
        # Find the highest job number for current year
        job_numbers = []
        for job in jobs:
            job_id = job.get('job_id', '')
            if job_id.startswith(f'J{year}-'):
                try:
                    num = int(job_id.split('-')[1])
                    job_numbers.append(num)
                except (IndexError, ValueError):
                    continue
        
        next_number = max(job_numbers, default=0) + 1
        return f'J{year}-{next_number:04d}'
    
    def generate_quote_id(self) -> str:
        """Generate unique quote ID in format Q2025-XXXX"""
        quotes = self._load_quotes()
        year = datetime.now().year
        
        # Find the highest quote number for current year
        quote_numbers = []
        for quote in quotes:
            quote_id = quote.get('quote_id', '')
            if quote_id.startswith(f'Q{year}-'):
                try:
                    num = int(quote_id.split('-')[1])
                    quote_numbers.append(num)
                except (IndexError, ValueError):
                    continue
        
        next_number = max(quote_numbers, default=0) + 1
        return f'Q{year}-{next_number:04d}'
    
    def create_job_record(self, job_data: Dict) -> Dict:
        """Create comprehensive job record"""
        try:
            jobs = self._load_jobs()
            
            job_id = self.generate_job_id()
            
            job_record = {
                'job_id': job_id,
                'client_name': job_data.get('client_name', ''),
                'client_phone': self.phone_formatter.format_phone(job_data.get('client_phone', '')),
                'client_email': job_data.get('client_email', ''),
                'client_address': job_data.get('client_address', ''),
                'service_type': job_data.get('service_type', ''),
                'project_description': job_data.get('project_description', ''),
                'estimated_cost': float(job_data.get('estimated_cost', 0)),
                'estimated_labor_hours': float(job_data.get('estimated_labor_hours', 0)),
                'estimated_material_cost': float(job_data.get('estimated_material_cost', 0)),
                'job_start_date': job_data.get('job_start_date', ''),
                'job_end_date': job_data.get('job_end_date', ''),
                'status': job_data.get('status', 'estimate'),
                'priority': job_data.get('priority', 'normal'),
                'assigned_staff': job_data.get('assigned_staff', []),
                'notes': job_data.get('notes', ''),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'payment_terms': job_data.get('payment_terms', ''),
                'deposit_required': job_data.get('deposit_required', False),
                'deposit_amount': float(job_data.get('deposit_amount', 0)),
                'total_payments_received': 0.0,
                'outstanding_balance': float(job_data.get('estimated_cost', 0)),
                'profit_margin': 0.0,  # Will be calculated after completion
                'actual_cost': 0.0,    # Will be updated as materials/labor are logged
                'completion_percentage': 0
            }
            
            jobs.append(job_record)
            self._save_jobs(jobs)
            
            logging.info(f"Created job record: {job_id}")
            return {'success': True, 'job_id': job_id, 'job': job_record}
            
        except Exception as e:
            logging.error(f"Error creating job record: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_quote_record(self, quote_data: Dict) -> Dict:
        """Create comprehensive quote record"""
        try:
            quotes = self._load_quotes()
            
            quote_id = self.generate_quote_id()
            
            quote_record = {
                'quote_id': quote_id,
                'job_id': quote_data.get('job_id', ''),
                'client_name': quote_data.get('client_name', ''),
                'client_phone': self.phone_formatter.format_phone(quote_data.get('client_phone', '')),
                'client_email': quote_data.get('client_email', ''),
                'service_type': quote_data.get('service_type', ''),
                'items_services': quote_data.get('items_services', []),
                'subtotal': float(quote_data.get('subtotal', 0)),
                'tax_amount': float(quote_data.get('tax_amount', 0)),
                'total_amount': float(quote_data.get('total_amount', 0)),
                'date_sent': quote_data.get('date_sent', datetime.now().isoformat()),
                'quote_status': quote_data.get('quote_status', 'sent'),  # sent, pending, accepted, declined, expired
                'payment_terms': quote_data.get('payment_terms', 'Net 30'),
                'valid_until': quote_data.get('valid_until', ''),
                'deposit_required': quote_data.get('deposit_required', False),
                'deposit_percentage': float(quote_data.get('deposit_percentage', 0)),
                'notes': quote_data.get('notes', ''),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'follow_up_date': quote_data.get('follow_up_date', ''),
                'conversion_probability': quote_data.get('conversion_probability', 'medium')
            }
            
            quotes.append(quote_record)
            self._save_quotes(quotes)
            
            logging.info(f"Created quote record: {quote_id}")
            return {'success': True, 'quote_id': quote_id, 'quote': quote_record}
            
        except Exception as e:
            logging.error(f"Error creating quote record: {e}")
            return {'success': False, 'error': str(e)}
    
    def log_payment(self, payment_data: Dict) -> Dict:
        """Log manual payment received"""
        try:
            payments = self._load_payments()
            
            payment_id = f"PAY-{datetime.now().strftime('%Y%m%d')}-{len(payments) + 1:03d}"
            
            payment_record = {
                'payment_id': payment_id,
                'job_id': payment_data.get('job_id', ''),
                'quote_id': payment_data.get('quote_id', ''),
                'client_name': payment_data.get('client_name', ''),
                'payment_amount': float(payment_data.get('payment_amount', 0)),
                'payment_method': payment_data.get('payment_method', ''),  # cash, check, venmo, zelle, etc.
                'date_received': payment_data.get('date_received', datetime.now().isoformat()),
                'reference_number': payment_data.get('reference_number', ''),  # check number, venmo ID, etc.
                'notes': payment_data.get('notes', ''),
                'recorded_by': payment_data.get('recorded_by', 'admin'),
                'created_at': datetime.now().isoformat()
            }
            
            payments.append(payment_record)
            self._save_payments(payments)
            
            # Update job outstanding balance
            job_id = payment_data.get('job_id')
            if job_id:
                self._update_job_payment_status(job_id, payment_record['payment_amount'])
            
            logging.info(f"Logged payment: {payment_id}")
            return {'success': True, 'payment_id': payment_id, 'payment': payment_record}
            
        except Exception as e:
            logging.error(f"Error logging payment: {e}")
            return {'success': False, 'error': str(e)}
    
    def log_materials(self, material_data: Dict) -> Dict:
        """Log materials used for job"""
        try:
            materials = self._load_materials()
            
            material_id = f"MAT-{datetime.now().strftime('%Y%m%d')}-{len(materials) + 1:03d}"
            
            material_record = {
                'material_id': material_id,
                'job_id': material_data.get('job_id', ''),
                'supplier_name': material_data.get('supplier_name', ''),
                'items': material_data.get('items', []),  # [{'name': '', 'quantity': 0, 'unit_cost': 0, 'total_cost': 0}]
                'total_cost': float(material_data.get('total_cost', 0)),
                'purchase_date': material_data.get('purchase_date', datetime.now().isoformat()),
                'receipt_number': material_data.get('receipt_number', ''),
                'delivery_date': material_data.get('delivery_date', ''),
                'notes': material_data.get('notes', ''),
                'recorded_by': material_data.get('recorded_by', 'admin'),
                'created_at': datetime.now().isoformat()
            }
            
            materials.append(material_record)
            self._save_materials(materials)
            
            # Update job actual cost
            job_id = material_data.get('job_id')
            if job_id:
                self._update_job_actual_cost(job_id, material_record['total_cost'], 'material')
            
            logging.info(f"Logged materials: {material_id}")
            return {'success': True, 'material_id': material_id, 'material': material_record}
            
        except Exception as e:
            logging.error(f"Error logging materials: {e}")
            return {'success': False, 'error': str(e)}
    
    def log_labor(self, labor_data: Dict) -> Dict:
        """Log labor hours for job"""
        try:
            labor_logs = self._load_labor()
            
            labor_id = f"LAB-{datetime.now().strftime('%Y%m%d')}-{len(labor_logs) + 1:03d}"
            
            labor_record = {
                'labor_id': labor_id,
                'job_id': labor_data.get('job_id', ''),
                'staff_name': labor_data.get('staff_name', ''),
                'work_date': labor_data.get('work_date', datetime.now().date().isoformat()),
                'start_time': labor_data.get('start_time', ''),
                'end_time': labor_data.get('end_time', ''),
                'hours_worked': float(labor_data.get('hours_worked', 0)),
                'hourly_rate': float(labor_data.get('hourly_rate', 0)),
                'labor_cost': float(labor_data.get('hours_worked', 0)) * float(labor_data.get('hourly_rate', 0)),
                'work_description': labor_data.get('work_description', ''),
                'overtime_hours': float(labor_data.get('overtime_hours', 0)),
                'overtime_rate': float(labor_data.get('overtime_rate', 0)),
                'notes': labor_data.get('notes', ''),
                'recorded_by': labor_data.get('recorded_by', 'admin'),
                'created_at': datetime.now().isoformat()
            }
            
            labor_logs.append(labor_record)
            self._save_labor(labor_logs)
            
            # Update job actual cost
            job_id = labor_data.get('job_id')
            if job_id:
                total_labor_cost = labor_record['labor_cost'] + (labor_record['overtime_hours'] * labor_record['overtime_rate'])
                self._update_job_actual_cost(job_id, total_labor_cost, 'labor')
            
            logging.info(f"Logged labor: {labor_id}")
            return {'success': True, 'labor_id': labor_id, 'labor': labor_record}
            
        except Exception as e:
            logging.error(f"Error logging labor: {e}")
            return {'success': False, 'error': str(e)}
    
    def _update_job_payment_status(self, job_id: str, payment_amount: float):
        """Update job payment status after payment received"""
        jobs = self._load_jobs()
        
        for job in jobs:
            if job['job_id'] == job_id:
                job['total_payments_received'] += payment_amount
                job['outstanding_balance'] = max(0, job['estimated_cost'] - job['total_payments_received'])
                job['updated_at'] = datetime.now().isoformat()
                
                # Update status if fully paid
                if job['outstanding_balance'] <= 0:
                    job['status'] = 'paid'
                
                break
        
        self._save_jobs(jobs)
    
    def _update_job_actual_cost(self, job_id: str, cost: float, cost_type: str):
        """Update job actual cost as materials/labor are logged"""
        jobs = self._load_jobs()
        
        for job in jobs:
            if job['job_id'] == job_id:
                job['actual_cost'] += cost
                job['updated_at'] = datetime.now().isoformat()
                
                # Calculate profit margin if job is completed
                if job['status'] == 'completed' and job['total_payments_received'] > 0:
                    job['profit_margin'] = ((job['total_payments_received'] - job['actual_cost']) / job['total_payments_received']) * 100
                
                break
        
        self._save_jobs(jobs)
    
    def get_job_records(self, status: str = None) -> List[Dict]:
        """Get job records, optionally filtered by status"""
        jobs = self._load_jobs()
        
        if status:
            return [job for job in jobs if job.get('status') == status]
        
        return jobs
    
    def get_quote_history(self, status: str = None) -> List[Dict]:
        """Get quote history, optionally filtered by status"""
        quotes = self._load_quotes()
        
        if status:
            return [quote for quote in quotes if quote.get('quote_status') == status]
        
        return quotes
    
    def get_payment_logs(self, job_id: str = None) -> List[Dict]:
        """Get payment logs, optionally filtered by job ID"""
        payments = self._load_payments()
        
        if job_id:
            return [payment for payment in payments if payment.get('job_id') == job_id]
        
        return payments
    
    def get_job_summary(self, job_id: str) -> Dict:
        """Get comprehensive job summary including all related records"""
        try:
            jobs = self._load_jobs()
            job = next((j for j in jobs if j['job_id'] == job_id), None)
            
            if not job:
                return {'success': False, 'error': 'Job not found'}
            
            # Get related records
            quotes = [q for q in self._load_quotes() if q.get('job_id') == job_id]
            payments = [p for p in self._load_payments() if p.get('job_id') == job_id]
            materials = [m for m in self._load_materials() if m.get('job_id') == job_id]
            labor = [l for l in self._load_labor() if l.get('job_id') == job_id]
            
            return {
                'success': True,
                'job': job,
                'quotes': quotes,
                'payments': payments,
                'materials': materials,
                'labor': labor,
                'summary': {
                    'total_quotes': len(quotes),
                    'total_payments': sum(p['payment_amount'] for p in payments),
                    'material_costs': sum(m['total_cost'] for m in materials),
                    'labor_costs': sum(l['labor_cost'] for l in labor),
                    'total_actual_cost': job['actual_cost'],
                    'profit_margin': job['profit_margin'],
                    'outstanding_balance': job['outstanding_balance']
                }
            }
            
        except Exception as e:
            logging.error(f"Error getting job summary: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_reporting_data(self) -> Dict:
        """Get comprehensive reporting data"""
        try:
            jobs = self._load_jobs()
            quotes = self._load_quotes()
            payments = self._load_payments()
            
            # Calculate key metrics
            total_jobs = len(jobs)
            completed_jobs = len([j for j in jobs if j['status'] == 'completed'])
            total_estimated_value = sum(j['estimated_cost'] for j in jobs)
            total_actual_revenue = sum(j['total_payments_received'] for j in jobs)
            total_actual_costs = sum(j['actual_cost'] for j in jobs)
            
            quote_conversion_rate = 0
            if quotes:
                accepted_quotes = len([q for q in quotes if q['quote_status'] == 'accepted'])
                quote_conversion_rate = (accepted_quotes / len(quotes)) * 100
            
            # Status breakdown
            status_breakdown = {}
            for job in jobs:
                status = job.get('status', 'unknown')
                status_breakdown[status] = status_breakdown.get(status, 0) + 1
            
            # Payment method breakdown
            payment_method_breakdown = {}
            for payment in payments:
                method = payment.get('payment_method', 'unknown')
                payment_method_breakdown[method] = payment_method_breakdown.get(method, 0) + 1
            
            return {
                'total_jobs': total_jobs,
                'completed_jobs': completed_jobs,
                'completion_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
                'total_estimated_value': total_estimated_value,
                'total_actual_revenue': total_actual_revenue,
                'total_actual_costs': total_actual_costs,
                'profit_margin': ((total_actual_revenue - total_actual_costs) / total_actual_revenue * 100) if total_actual_revenue > 0 else 0,
                'quote_conversion_rate': quote_conversion_rate,
                'status_breakdown': status_breakdown,
                'payment_method_breakdown': payment_method_breakdown,
                'average_job_value': total_estimated_value / total_jobs if total_jobs > 0 else 0,
                'outstanding_balances': sum(j['outstanding_balance'] for j in jobs)
            }
            
        except Exception as e:
            logging.error(f"Error getting reporting data: {e}")
            return {}
    
    # Data persistence methods
    def _load_jobs(self) -> List[Dict]:
        """Load job records from file"""
        try:
            with open(self.jobs_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_jobs(self, jobs: List[Dict]):
        """Save job records to file"""
        with open(self.jobs_file, 'w') as f:
            json.dump(jobs, f, indent=2)
    
    def _load_quotes(self) -> List[Dict]:
        """Load quote history from file"""
        try:
            with open(self.quotes_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_quotes(self, quotes: List[Dict]):
        """Save quote history to file"""
        with open(self.quotes_file, 'w') as f:
            json.dump(quotes, f, indent=2)
    
    def _load_payments(self) -> List[Dict]:
        """Load payment logs from file"""
        try:
            with open(self.payments_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_payments(self, payments: List[Dict]):
        """Save payment logs to file"""
        with open(self.payments_file, 'w') as f:
            json.dump(payments, f, indent=2)
    
    def _load_materials(self) -> List[Dict]:
        """Load material logs from file"""
        try:
            with open(self.materials_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_materials(self, materials: List[Dict]):
        """Save material logs to file"""
        with open(self.materials_file, 'w') as f:
            json.dump(materials, f, indent=2)
    
    def _load_labor(self) -> List[Dict]:
        """Load labor logs from file"""
        try:
            with open(self.labor_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_labor(self, labor: List[Dict]):
        """Save labor logs to file"""
        with open(self.labor_file, 'w') as f:
            json.dump(labor, f, indent=2)

# Global instance
job_tracking_service = JobTrackingService()