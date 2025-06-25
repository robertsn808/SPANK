"""
Admin-specific routes for SPANKKS Construction
All admin functionality using PostgreSQL database
"""

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
        clients = db.session.query(Client).order_by(Client.created_date.desc()).all()
        
        # Get client statistics
        client_stats = []
        for client in clients:
            jobs_count = db.session.query(Job).filter(Job.client_id == client.id).count()
            quotes_count = db.session.query(Quote).filter(Quote.client_id == client.id).count()
            total_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
                Invoice.client_id == client.id, 
                Invoice.status == 'paid'
            ).scalar() or 0
            
            client_stats.append({
                'client': client,
                'jobs_count': jobs_count,
                'quotes_count': quotes_count,
                'total_revenue': float(total_revenue)
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
        jobs = db.session.query(Job).order_by(Job.created_date.desc()).all()
        
        # Group jobs by status
        job_stats = {
            'scheduled': db.session.query(Job).filter(Job.status == 'scheduled').count(),
            'in_progress': db.session.query(Job).filter(Job.status == 'in_progress').count(),
            'completed': db.session.query(Job).filter(Job.status == 'completed').count(),
            'cancelled': db.session.query(Job).filter(Job.status == 'cancelled').count()
        }
        
        return render_template('admin/sections/jobs_section.html', 
                             jobs=jobs, 
                             job_stats=job_stats)
    except Exception as e:
        logging.error(f"Jobs page error: {e}")
        flash('Error loading jobs data', 'error')
        return redirect('/admin-home')

@app.route('/admin/financial')
def admin_financial():
    """Financial reports page with PostgreSQL data"""
    try:
        # Get financial metrics
        total_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
            Invoice.status == 'paid'
        ).scalar() or 0
        
        pending_invoices = db.session.query(func.sum(Invoice.total_amount)).filter(
            Invoice.status == 'pending'
        ).scalar() or 0
        
        overdue_invoices = db.session.query(func.sum(Invoice.total_amount)).filter(
            Invoice.status == 'overdue'
        ).scalar() or 0
        
        # Recent invoices
        recent_invoices = db.session.query(Invoice).order_by(Invoice.created_date.desc()).limit(10).all()
        
        financial_data = {
            'total_revenue': float(total_revenue),
            'pending_amount': float(pending_invoices),
            'overdue_amount': float(overdue_invoices),
            'recent_invoices': recent_invoices
        }
        
        return render_template('admin/sections/financial_section.html', 
                             financial_data=financial_data)
    except Exception as e:
        logging.error(f"Financial page error: {e}")
        flash('Error loading financial data', 'error')
        return redirect('/admin-home')

@app.route('/admin/staff')
def admin_staff():
    """Staff management page with PostgreSQL data"""
    try:
        staff_members = db.session.query(Staff).all()
        
        # Get staff statistics
        staff_stats = []
        for staff in staff_members:
            assigned_jobs = db.session.query(Job).filter(Job.assigned_staff_id == staff.id).count()
            completed_jobs = db.session.query(Job).filter(
                Job.assigned_staff_id == staff.id, 
                Job.status == 'completed'
            ).count()
            
            staff_stats.append({
                'staff': staff,
                'assigned_jobs': assigned_jobs,
                'completed_jobs': completed_jobs,
                'completion_rate': (completed_jobs / assigned_jobs * 100) if assigned_jobs > 0 else 0
            })
        
        return render_template('admin/sections/staff_crm_section.html', 
                             staff_stats=staff_stats,
                             total_staff=len(staff_members))
    except Exception as e:
        logging.error(f"Staff page error: {e}")
        flash('Error loading staff data', 'error')
        return redirect('/admin-home')

@app.route('/admin/inventory')
def admin_inventory():
    """Inventory management page with PostgreSQL data"""
    try:
        # Get materials usage data
        materials = db.session.query(MaterialsUsed).all()
        
        # Group by material type and calculate totals
        material_summary = {}
        for material in materials:
            if material.material_name not in material_summary:
                material_summary[material.material_name] = {
                    'total_quantity': 0,
                    'total_cost': 0,
                    'supplier': material.supplier,
                    'unit': material.unit
                }
            material_summary[material.material_name]['total_quantity'] += material.quantity_used
            material_summary[material.material_name]['total_cost'] += float(material.cost_per_unit or 0) * material.quantity_used
        
        return render_template('admin/sections/inventory_section.html', 
                             material_summary=material_summary)
    except Exception as e:
        logging.error(f"Inventory page error: {e}")
        flash('Error loading inventory data', 'error')
        return redirect('/admin-home')

@app.route('/admin/analytics')
def admin_analytics():
    """Business analytics page with PostgreSQL data"""
    try:
        from analytics.business_intelligence import BusinessIntelligence
        
        bi_service = BusinessIntelligence()
        analytics_data = bi_service.generate_business_insights(storage_service)
        
        return render_template('admin/sections/business_intelligence_section.html', 
                             analytics=analytics_data)
    except Exception as e:
        logging.error(f"Analytics page error: {e}")
        flash('Error loading analytics data', 'error')
        return redirect('/admin-home')

@app.route('/admin/service-management')
def admin_service_management():
    """Service management page with PostgreSQL data"""
    try:
        service_types = db.session.query(ServiceType).all()
        
        # Get service statistics
        service_stats = []
        for service in service_types:
            jobs_count = db.session.query(Job).filter(Job.service_type == service.name).count()
            quotes_count = db.session.query(Quote).filter(Quote.service_type == service.name).count()
            
            service_stats.append({
                'service': service,
                'jobs_count': jobs_count,
                'quotes_count': quotes_count
            })
        
        return render_template('admin/sections/service_management_section.html', 
                             service_stats=service_stats)
    except Exception as e:
        logging.error(f"Service management page error: {e}")
        flash('Error loading service data', 'error')
        return redirect('/admin-home')

@app.route('/admin/calendar')
def admin_calendar():
    """Calendar and scheduling page"""
    try:
        # Get scheduled jobs for calendar
        scheduled_jobs = db.session.query(Job).filter(Job.status.in_(['scheduled', 'in_progress'])).all()
        
        # Format for FullCalendar
        calendar_events = []
        for job in scheduled_jobs:
            calendar_events.append({
                'id': job.id,
                'title': f"{job.service_type} - {job.client.name if job.client else 'Unknown'}",
                'start': job.scheduled_date.isoformat() if job.scheduled_date else None,
                'backgroundColor': '#007bff' if job.status == 'scheduled' else '#28a745',
                'borderColor': '#007bff' if job.status == 'scheduled' else '#28a745'
            })
        
        return render_template('admin/sections/advanced_schedule_section.html', 
                             calendar_events=calendar_events)
    except Exception as e:
        logging.error(f"Calendar page error: {e}")
        flash('Error loading calendar data', 'error')
        return redirect('/admin-home')

# API endpoints for AJAX requests
@app.route('/api/admin/dashboard-stats')
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    try:
        stats = get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        logging.error(f"Dashboard stats API error: {e}")
        return jsonify({'error': 'Failed to load dashboard stats'}), 500

@app.route('/api/admin/client/<int:client_id>')
def api_client_details(client_id):
    """API endpoint for client details"""
    try:
        client = db.session.query(Client).get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # Get client's jobs and quotes
        jobs = db.session.query(Job).filter(Job.client_id == client_id).all()
        quotes = db.session.query(Quote).filter(Quote.client_id == client_id).all()
        
        return jsonify({
            'client': {
                'id': client.id,
                'name': client.name,
                'email': client.email,
                'phone': client.phone,
                'address': client.address
            },
            'jobs': [{'id': j.id, 'service_type': j.service_type, 'status': j.status} for j in jobs],
            'quotes': [{'id': q.id, 'quote_id': q.quote_id, 'status': q.status, 'total_amount': float(q.total_amount or 0)} for q in quotes]
        })
    except Exception as e:
        logging.error(f"Client details API error: {e}")
        return jsonify({'error': 'Failed to load client details'}), 500

# Import the dashboard stats function from routes.py
from routes import get_dashboard_stats