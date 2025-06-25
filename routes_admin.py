"""
Admin-specific routes for SPANKKS Construction
All admin functionality using PostgreSQL database
"""

import os
import json
import logging
from flask import render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, timedelta
from config.app import app, db
# Import what's available from database models
try:
    from models.models_db import ServiceType
    from config.app import db
    database_available = True
except ImportError:
    database_available = False
from services.storage_service import StorageService
from sqlalchemy import func, desc

# Initialize services
storage_service = StorageService()

@app.route('/admin/crm')
def admin_crm():
    """Customer CRM page with PostgreSQL data"""
    try:
        # Get clients with comprehensive data using direct SQL
        with db.engine.connect() as conn:
            # Get all clients
            clients_result = conn.execute(db.text("""
                SELECT client_id, name, email, phone, address, billing_address, 
                       preferred_contact_method, created_at, notes
                FROM clients 
                ORDER BY created_at DESC
            """))
            clients = [dict(row._mapping) for row in clients_result]
            
            # Get client statistics
            client_stats = []
            for client in clients:
                client_id = client['client_id']
                
                # Get jobs count
                jobs_result = conn.execute(db.text("""
                    SELECT COUNT(*) as count FROM jobs WHERE client_id = :client_id
                """), {'client_id': client_id})
                jobs_count = jobs_result.scalar()
                
                # Get quotes count
                quotes_result = conn.execute(db.text("""
                    SELECT COUNT(*) as count FROM quotes WHERE client_id = :client_id
                """), {'client_id': client_id})
                quotes_count = quotes_result.scalar()
                
                # Get total revenue
                revenue_result = conn.execute(db.text("""
                    SELECT COALESCE(SUM(total_paid), 0) as total
                    FROM invoices 
                    WHERE client_id = :client_id AND status = 'paid'
                """), {'client_id': client_id})
                total_revenue = float(revenue_result.scalar() or 0)
                
                # Get recent job
                recent_job_result = conn.execute(db.text("""
                    SELECT service_type, status, scheduled_date 
                    FROM jobs 
                    WHERE client_id = :client_id 
                    ORDER BY timestamp_created DESC 
                    LIMIT 1
                """), {'client_id': client_id})
                recent_job = recent_job_result.first()
                
                client_stats.append({
                    'client': client,
                    'jobs_count': jobs_count,
                    'quotes_count': quotes_count,
                    'total_revenue': total_revenue,
                    'recent_job': dict(recent_job._mapping) if recent_job else None
                })
        
        return render_template('admin/sections/crm_section.html', 
                             clients=client_stats, 
                             total_clients=len(clients))
    except Exception as e:
        logging.error(f"CRM page error: {e}")
        flash('Error loading CRM data', 'error')
        return redirect('/admin-home')

@app.route('/admin/jobs')
def admin_jobs():
    """Job management page with PostgreSQL data"""
    try:
        with db.engine.connect() as conn:
            # Get all jobs with client information
            jobs_result = conn.execute(db.text("""
                SELECT j.job_id, j.service_type, j.status, j.scheduled_date, 
                       j.estimated_hours, j.actual_hours, j.location,
                       c.name as client_name, c.phone as client_phone
                FROM jobs j
                LEFT JOIN clients c ON j.client_id = c.client_id
                ORDER BY j.timestamp_created DESC
            """))
            jobs = [dict(row._mapping) for row in jobs_result]
        
        return render_template('admin/sections/jobs_section.html', jobs=jobs)
    except Exception as e:
        logging.error(f"Jobs page error: {e}")
        flash('Error loading jobs data', 'error')
        return redirect('/admin-home')

@app.route('/admin/financial')
def admin_financial():
    """Financial reports page with PostgreSQL data"""
    try:
        with db.engine.connect() as conn:
            # Get financial overview
            revenue_result = conn.execute(db.text("""
                SELECT COALESCE(SUM(total_paid), 0) as total_revenue
                FROM invoices WHERE status = 'paid'
            """))
            total_revenue = float(revenue_result.scalar() or 0)
            
            # Get pending invoices
            pending_result = conn.execute(db.text("""
                SELECT COUNT(*) as count, COALESCE(SUM(amount_due), 0) as amount
                FROM invoices WHERE status = 'pending'
            """))
            pending_data = pending_result.first()
            
            financial_data = {
                'total_revenue': total_revenue,
                'pending_invoices': pending_data.count,
                'pending_amount': float(pending_data.amount)
            }
        
        return render_template('admin/sections/financial_section.html', 
                             financial=financial_data)
    except Exception as e:
        logging.error(f"Financial page error: {e}")
        flash('Error loading financial data', 'error')
        return redirect('/admin-home')

@app.route('/admin/staff')
def admin_staff():
    """Staff management page with PostgreSQL data"""
    try:
        with db.engine.connect() as conn:
            # Get staff information
            staff_result = conn.execute(db.text("""
                SELECT staff_id, name, email, phone, role, hourly_rate, 
                       skills, availability, active, created_at
                FROM staff
                ORDER BY created_at DESC
            """))
            staff = [dict(row._mapping) for row in staff_result]
        
        return render_template('admin/sections/staff_section.html', staff=staff)
    except Exception as e:
        logging.error(f"Staff page error: {e}")
        flash('Error loading staff data', 'error')
        return redirect('/admin-home')

@app.route('/admin/inventory')
def admin_inventory():
    """Inventory management page with PostgreSQL data"""
    try:
        with db.engine.connect() as conn:
            # Get inventory information
            inventory_result = conn.execute(db.text("""
                SELECT item_id, name, category, current_stock, 
                       reorder_level, unit_cost, supplier
                FROM inventory
                ORDER BY name
            """))
            inventory = [dict(row._mapping) for row in inventory_result]
        
        return render_template('admin/sections/inventory_section.html', 
                             inventory=inventory)
    except Exception as e:
        logging.error(f"Inventory page error: {e}")
        flash('Error loading inventory data', 'error')
        return redirect('/admin-home')

@app.route('/admin/analytics')
def admin_analytics():
    """Business analytics page with PostgreSQL data"""
    try:
        # Use analytics service for comprehensive data
        from analytics.analytics_manager import AnalyticsManager
        analytics_manager = AnalyticsManager()
        analytics_data = analytics_manager.get_comprehensive_analytics(storage_service)
        
        return render_template('admin/sections/analytics_section.html', 
                             analytics=analytics_data)
    except Exception as e:
        logging.error(f"Analytics page error: {e}")
        flash('Error loading analytics data', 'error')
        return redirect('/admin-home')

@app.route('/admin/service-management')
def admin_service_management():
    """Service management page"""
    try:
        if database_available:
            service_types = db.session.query(ServiceType).all()
        else:
            service_types = []
        
        return render_template('admin/sections/service_management_section.html', 
                             service_types=service_types)
    except Exception as e:
        logging.error(f"Service management page error: {e}")
        flash('Error loading service management data', 'error')
        return redirect('/admin-home')

@app.route('/admin/calendar')
def admin_calendar():
    """Calendar and scheduling page"""
    try:
        with db.engine.connect() as conn:
            # Get scheduled jobs for calendar
            calendar_result = conn.execute(db.text("""
                SELECT j.job_id, j.service_type, j.scheduled_date,
                       c.name as client_name
                FROM jobs j
                LEFT JOIN clients c ON j.client_id = c.client_id
                WHERE j.status = 'scheduled'
                ORDER BY j.scheduled_date
            """))
            calendar_events = [dict(row._mapping) for row in calendar_result]
        
        return render_template('admin/sections/calendar_section.html', 
                             events=calendar_events)
    except Exception as e:
        logging.error(f"Calendar page error: {e}")
        flash('Error loading calendar data', 'error')
        return redirect('/admin-home')

# API Endpoints
@app.route('/api/dashboard/stats')
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    try:
        from routes import get_dashboard_stats
        stats = get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        logging.error(f"Dashboard API error: {e}")
        return jsonify({'error': 'Failed to load dashboard stats'}), 500

@app.route('/api/admin/client/<client_id>')
def api_client_details(client_id):
    """API endpoint for client details"""
    try:
        with db.engine.connect() as conn:
            # Get client details
            client_result = conn.execute(db.text("""
                SELECT * FROM clients WHERE client_id = :client_id
            """), {'client_id': client_id})
            client = client_result.first()
            
            if not client:
                return jsonify({'error': 'Client not found'}), 404
            
            # Get client jobs
            jobs_result = conn.execute(db.text("""
                SELECT * FROM jobs WHERE client_id = :client_id
                ORDER BY timestamp_created DESC
            """), {'client_id': client_id})
            jobs = [dict(row._mapping) for row in jobs_result]
            
            # Get client quotes
            quotes_result = conn.execute(db.text("""
                SELECT * FROM quotes WHERE client_id = :client_id
                ORDER BY created_at DESC
            """), {'client_id': client_id})
            quotes = [dict(row._mapping) for row in quotes_result]
            
            return jsonify({
                'client': dict(client._mapping),
                'jobs': jobs,
                'quotes': quotes
            })
    except Exception as e:
        logging.error(f"Client details API error: {e}")
        return jsonify({'error': 'Failed to load client details'}), 500