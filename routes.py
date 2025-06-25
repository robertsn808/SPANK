import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response, send_file, abort
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import uuid
import pytz
from utils import phone_formatter

# Import fallback services and models
try:
    from models import HandymanStorage, Contact, Job, Quote, Invoice
except ImportError:
    # Create fallback classes if models not available
    class HandymanStorage:
        def __init__(self):
            pass
    class Contact:
        def __init__(self, **kwargs):
            pass

# Initialize services with minimal dependencies
try:
    from services.storage_service import StorageService
    storage_service = StorageService()
    logging.info("Storage service initialized")
except ImportError:
    storage_service = None
    logging.warning("Storage service not available")

# Initialize services with proper fallback handling
reminder_service = None
real_time_scheduler = None
job_tracking_service = None
financial_reporting_service = None
mailerlite_service = None
inventory_service = None
medium_priority_service = None
checklist_service = None
notification_service = None
unified_scheduler = None

# Initialize handyman storage
try:
    handyman_storage = HandymanStorage()
except:
    handyman_storage = None
    logging.warning("HandymanStorage not available")

# Set file storage
file_storage = storage_service

logging.info("All services initialized successfully")

# App is imported directly from config.app at module level

# Additional storage for appointments and staff
appointments = []
staff_members = []
staff_logins = []

# Staff class
class Staff:
    def __init__(self, name, email, phone=None, role=None, hire_date=None, active=True):
        self.id = len(staff_members) + 1
        self.name = name
        self.email = email
        self.phone = phone
        self.role = role or 'Technician'
        self.hire_date = hire_date or datetime.now().strftime('%Y-%m-%d')
        self.active = active

# Staff login class
class StaffLogin:
    def __init__(self, staff_id, username, password):
        self.id = len(staff_logins) + 1
        self.staff_id = staff_id
        self.username = username
        self.password = password
        self.role = 'staff'
        self.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Admin credentials
ADMIN_USERNAME = "spankysadmin808"
ADMIN_PASSWORD = "Money$$"

# Helper function for Hawaii timezone
def get_hawaii_time():
    """Get current time in Hawaii timezone"""
    hawaii_tz = pytz.timezone('Pacific/Honolulu')
    utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    return utc_now.astimezone(hawaii_tz)

# Import app here to register routes
from config.app import app

@app.route('/admin-home')
def admin_home_redirect():
    """Admin homepage - comprehensive dashboard"""
    try:
        # Get dashboard stats
        dashboard_stats = get_dashboard_stats()
        return render_template('admin/dashboard/main.html', stats=dashboard_stats)
    except Exception as e:
        logging.error(f"Admin dashboard error: {e}")
        return render_template('admin/core/login.html')

def get_dashboard_stats():
    """Get comprehensive dashboard statistics using existing services"""
    try:
        # Import database models
        from models.models_db import Client, Job, Quote, Invoice
        from sqlalchemy import func
        from config.app import db
        
        # Initialize base stats structure
        stats = {
            'overview': {
                'total_revenue': 0,
                'active_jobs': 0,
                'pending_quotes': 0,
                'overdue_invoices': 0
            },
            'recent_activity': [],
            'upcoming_jobs': [],
            'kpis': {
                'conversion_rate': 0,
                'avg_job_value': 0,
                'customer_satisfaction': 0,
                'staff_utilization': 0
            },
            'quick_actions': [
                {'title': 'Generate Quote', 'url': '/generate-quote', 'icon': 'fas fa-file-invoice'},
                {'title': 'View Calendar', 'url': '/admin/calendar', 'icon': 'fas fa-calendar-plus'},
                {'title': 'Customer CRM', 'url': '/admin/crm', 'icon': 'fas fa-user-plus'},
                {'title': 'Staff Management', 'url': '/admin/staff', 'icon': 'fas fa-users'},
                {'title': 'Financial Reports', 'url': '/admin/financial', 'icon': 'fas fa-chart-line'},
                {'title': 'Job Tracking', 'url': '/admin/jobs', 'icon': 'fas fa-tasks'},
                {'title': 'Inventory', 'url': '/admin/inventory', 'icon': 'fas fa-boxes'},
                {'title': 'Analytics', 'url': '/admin/analytics', 'icon': 'fas fa-analytics'}
            ]
        }
        
        # Get real data from PostgreSQL database
        try:
            # Calculate overview metrics from database
            paid_invoices = db.session.query(Invoice).filter(Invoice.status == 'paid').all()
            stats['overview']['total_revenue'] = sum(float(invoice.total_amount or 0) for invoice in paid_invoices)
            
            active_jobs = db.session.query(Job).filter(Job.status.in_(['scheduled', 'in_progress'])).count()
            stats['overview']['active_jobs'] = active_jobs
            
            pending_quotes = db.session.query(Quote).filter(Quote.status == 'pending').count()
            stats['overview']['pending_quotes'] = pending_quotes
            
            overdue_invoices = db.session.query(Invoice).filter(Invoice.status == 'overdue').count()
            stats['overview']['overdue_invoices'] = overdue_invoices
            
            # Recent activity from database
            recent_activity = []
            
            # Get recent quotes
            recent_quotes = db.session.query(Quote).order_by(Quote.created_date.desc()).limit(3).all()
            for quote in recent_quotes:
                client_name = quote.client.name if quote.client else 'Unknown Client'
                recent_activity.append({
                    'action': f"Quote {quote.quote_id} generated for {client_name}",
                    'time': quote.created_date.strftime('%m/%d') if quote.created_date else 'Recently',
                    'type': 'quote'
                })
            
            # Get recent payments
            recent_payments = db.session.query(Invoice).filter(Invoice.status == 'paid').order_by(Invoice.payment_date.desc()).limit(2).all()
            for payment in recent_payments:
                recent_activity.append({
                    'action': f"Payment received ${payment.total_amount} - {payment.invoice_id}",
                    'time': payment.payment_date.strftime('%m/%d') if payment.payment_date else 'Recently',
                    'type': 'payment'
                })
            
            stats['recent_activity'] = recent_activity[:5]
            
            # Calculate KPIs from database
            total_quotes = db.session.query(Quote).count()
            paid_quotes = db.session.query(Invoice).filter(Invoice.status == 'paid').count()
            
            if total_quotes > 0:
                conversion_rate = (paid_quotes / total_quotes) * 100
                stats['kpis']['conversion_rate'] = round(conversion_rate, 1)
            
            if paid_invoices:
                avg_value = sum(float(invoice.total_amount or 0) for invoice in paid_invoices) / len(paid_invoices)
                stats['kpis']['avg_job_value'] = round(avg_value, 2)
            
            # Get upcoming jobs
            upcoming_jobs = db.session.query(Job).filter(Job.status == 'scheduled').order_by(Job.scheduled_date).limit(3).all()
            stats['upcoming_jobs'] = [{
                'client': job.client.name if job.client else 'Unknown',
                'service': job.service_type,
                'date': job.scheduled_date.strftime('%m/%d') if job.scheduled_date else 'TBD',
                'status': job.status
            } for job in upcoming_jobs]
            
        except Exception as e:
            logging.error(f"Database query error: {e}")
            # Fallback to JSON data if database fails
            if storage_service:
                try:
                    invoices = storage_service.load_data('invoices.json') or []
                    quotes = storage_service.load_data('quotes.json') or []
                    jobs = storage_service.load_data('jobs.json') or []
                    
                    paid_invoices = [i for i in invoices if i.get('status') == 'paid']
                    stats['overview']['total_revenue'] = sum(float(i.get('total_amount', 0)) for i in paid_invoices)
                    stats['overview']['active_jobs'] = len([j for j in jobs if j.get('status') in ['scheduled', 'in_progress']])
                    stats['overview']['pending_quotes'] = len([q for q in quotes if q.get('status') == 'pending'])
                    stats['overview']['overdue_invoices'] = len([i for i in invoices if i.get('status') == 'overdue'])
                except Exception as fallback_error:
                    logging.error(f"Fallback data loading error: {fallback_error}")
        
        return stats
    except Exception as e:
        logging.error(f"Dashboard stats error: {e}")
        return {
            'overview': {'total_revenue': 0, 'active_jobs': 0, 'pending_quotes': 0, 'overdue_invoices': 0},
            'recent_activity': [],
            'upcoming_jobs': [],
            'kpis': {'conversion_rate': 0, 'avg_job_value': 0, 'customer_satisfaction': 0, 'staff_utilization': 0},
            'quick_actions': [
                {'title': 'Generate Quote', 'url': '/generate-quote', 'icon': 'fas fa-file-invoice'},
                {'title': 'View Calendar', 'url': '/admin/calendar', 'icon': 'fas fa-calendar-plus'},
                {'title': 'Customer CRM', 'url': '/admin/crm', 'icon': 'fas fa-user-plus'},
                {'title': 'Staff Management', 'url': '/admin/staff', 'icon': 'fas fa-users'}
            ]
        }

# Legacy admin routes - public routes handled by routes_public.py

@app.route('/admin')
def admin_redirect():
    """Redirect to admin login"""
    return redirect('/admin-home')

@app.route('/staff-portal')
def staff_portal_redirect():
    """Staff portal login page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>SPANKKS Construction - Staff Portal</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <h4 class="mb-0">SPANKKS Construction Staff Portal</h4>
                        </div>
                        <div class="card-body">
                            <p>Welcome to the SPANKKS Construction staff portal.</p>
                            <div class="d-grid gap-2">
                                <a href="/" class="btn btn-secondary">Return to Website</a>
                                <a href="/consultation" class="btn btn-success">View Jobs</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/test-email-interface')
def test_email_interface():
    """Email testing interface for SPANK Buck rewards"""
    return render_template('test_email.html')

@app.route('/admin-consultation', methods=['GET', 'POST'])
def admin_consultation():
    """Consultation booking page"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = phone_formatter.format_phone(request.form.get('phone', '').strip())
        service = request.form.get('service', '').strip()
        project_type = request.form.get('project_type', '').strip()
        consultation_type = request.form.get('consultation_type', '').strip()
        preferred_date = request.form.get('preferred_date', '').strip()
        preferred_time = request.form.get('preferred_time', '').strip()
        message = request.form.get('message', '').strip()
        square_footage = request.form.get('square_footage', '').strip()

        # Ensure all consultation requests default to "Consultation" service type
        if not service or service.strip() == '':
            service = 'Consultation'
        
        # Basic validation
        if not all([name, email, phone, service]):
            flash('Please fill in all required fields.', 'error')
            return render_template('consultation.html')

        # Check if client already exists in database (by phone number as unique identifier)
