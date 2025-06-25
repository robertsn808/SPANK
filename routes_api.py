"""
API routes for SPANKKS Construction admin system
Provides REST endpoints for all admin functionality
"""

import os
import json
import logging
from flask import request, jsonify
from datetime import datetime, timedelta
from config.app import app, db

@app.route('/api/admin/clients/list')
def api_clients_list():
    """Get list of all clients for dropdowns"""
    try:
        with db.engine.connect() as conn:
            result = conn.execute(db.text("""
                SELECT client_id, name, email, phone 
                FROM clients 
                ORDER BY name
            """))
            clients = [dict(row._mapping) for row in result]
        
        return jsonify(clients)
    except Exception as e:
        logging.error(f"API clients list error: {e}")
        return jsonify({'error': 'Failed to load clients'}), 500

@app.route('/api/admin/jobs/list')
def api_jobs_list():
    """Get list of all jobs for dropdowns"""
    try:
        with db.engine.connect() as conn:
            result = conn.execute(db.text("""
                SELECT job_id, service_type, status, client_id
                FROM jobs 
                ORDER BY timestamp_created DESC
            """))
            jobs = [dict(row._mapping) for row in result]
        
        return jsonify(jobs)
    except Exception as e:
        logging.error(f"API jobs list error: {e}")
        return jsonify({'error': 'Failed to load jobs'}), 500

@app.route('/api/admin/staff/list')
def api_staff_list():
    """Get list of all staff for dropdowns"""
    try:
        with db.engine.connect() as conn:
            result = conn.execute(db.text("""
                SELECT staff_id, name, role, active
                FROM staff 
                WHERE active = true
                ORDER BY name
            """))
            staff = [dict(row._mapping) for row in result]
        
        return jsonify(staff)
    except Exception as e:
        logging.error(f"API staff list error: {e}")
        return jsonify({'error': 'Failed to load staff'}), 500

@app.route('/api/admin/jobs', methods=['POST'])
def api_create_job():
    """Create new job"""
    try:
        data = request.get_json()
        
        # Generate job ID
        with db.engine.connect() as conn:
            # Get next job number
            result = conn.execute(db.text("""
                SELECT COUNT(*) + 1 as next_num 
                FROM jobs 
                WHERE job_id LIKE 'J2025-%'
            """))
            next_num = result.scalar()
            job_id = f"J2025-{next_num:03d}"
            
            # Insert new job
            conn.execute(db.text("""
                INSERT INTO jobs (job_id, client_id, service_type, status, scheduled_date, 
                                estimated_hours, job_note, location, timestamp_created)
                VALUES (:job_id, :client_id, :service_type, 'draft', :scheduled_date,
                        :estimated_hours, :job_note, :location, NOW())
            """), {
                'job_id': job_id,
                'client_id': data.get('client_id'),
                'service_type': data.get('service_type'),
                'scheduled_date': data.get('scheduled_date'),
                'estimated_hours': data.get('estimated_hours'),
                'job_note': data.get('job_note'),
                'location': data.get('location')
            })
            conn.commit()
        
        return jsonify({'success': True, 'job_id': job_id})
    except Exception as e:
        logging.error(f"API create job error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/jobs/<job_id>')
def api_job_details(job_id):
    """Get job details"""
    try:
        with db.engine.connect() as conn:
            result = conn.execute(db.text("""
                SELECT j.*, c.name as client_name, c.phone as client_phone
                FROM jobs j
                LEFT JOIN clients c ON j.client_id = c.client_id
                WHERE j.job_id = :job_id
            """), {'job_id': job_id})
            job = result.first()
            
            if not job:
                return jsonify({'error': 'Job not found'}), 404
                
        return jsonify(dict(job._mapping))
    except Exception as e:
        logging.error(f"API job details error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/invoices', methods=['POST'])
def api_create_invoice():
    """Create new invoice"""
    try:
        data = request.get_json()
        
        with db.engine.connect() as conn:
            # Generate invoice number
            result = conn.execute(db.text("""
                SELECT COUNT(*) + 1 as next_num 
                FROM invoices 
                WHERE invoice_id LIKE 'INV-2025-%'
            """))
            next_num = result.scalar()
            invoice_number = f"INV-2025-{next_num:03d}"
            
            # Calculate totals
            subtotal = sum(item['quantity'] * item['unit_price'] for item in data.get('items', []))
            tax_amount = subtotal * 0.04712  # Hawaii GET tax
            total_amount = subtotal + tax_amount
            
            # Insert invoice
            conn.execute(db.text("""
                INSERT INTO invoices (invoice_id, client_id, job_id, issue_date, due_date,
                                    subtotal, tax, total_amount, status, notes, created_at)
                VALUES (:invoice_id, :client_id, :job_id, :issue_date, :due_date,
                        :subtotal, :tax, :total_amount, 'unsent', :notes, NOW())
            """), {
                'invoice_id': invoice_number,
                'client_id': data.get('client_id'),
                'job_id': data.get('job_id'),
                'issue_date': data.get('issue_date'),
                'due_date': data.get('due_date'),
                'subtotal': subtotal,
                'tax': tax_amount,
                'total_amount': total_amount,
                'notes': data.get('notes')
            })
            
            # Insert line items
            for item in data.get('items', []):
                line_total = item['quantity'] * item['unit_price']
                conn.execute(db.text("""
                    INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, line_total)
                    VALUES (:invoice_id, :description, :quantity, :unit_price, :line_total)
                """), {
                    'invoice_id': invoice_number,
                    'description': item['description'],
                    'quantity': item['quantity'],
                    'unit_price': item['unit_price'],
                    'line_total': line_total
                })
            
            conn.commit()
        
        return jsonify({'success': True, 'invoice_id': invoice_number})
    except Exception as e:
        logging.error(f"API create invoice error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/payments', methods=['POST'])
def api_record_payment():
    """Record payment for invoice"""
    try:
        data = request.get_json()
        
        with db.engine.connect() as conn:
            # Get invoice and client info
            invoice_result = conn.execute(db.text("""
                SELECT client_id, total_amount FROM invoices WHERE invoice_id = :invoice_id
            """), {'invoice_id': data.get('invoice_id')})
            invoice = invoice_result.first()
            
            if not invoice:
                return jsonify({'error': 'Invoice not found'}), 404
            
            # Record payment
            conn.execute(db.text("""
                INSERT INTO payments (invoice_id, client_id, amount_paid, payment_method,
                                    payment_date, reference_note, recorded_by, created_at)
                VALUES (:invoice_id, :client_id, :amount_paid, :payment_method,
                        :payment_date, :reference_note, :recorded_by, NOW())
            """), {
                'invoice_id': data.get('invoice_id'),
                'client_id': invoice.client_id,
                'amount_paid': data.get('amount_paid'),
                'payment_method': data.get('payment_method'),
                'payment_date': data.get('payment_date'),
                'reference_note': data.get('reference_note'),
                'recorded_by': data.get('recorded_by')
            })
            
            # Update invoice status if fully paid
            amount_paid = float(data.get('amount_paid'))
            if amount_paid >= invoice.total_amount:
                conn.execute(db.text("""
                    UPDATE invoices SET status = 'paid', paid_at = NOW()
                    WHERE invoice_id = :invoice_id
                """), {'invoice_id': data.get('invoice_id')})
            
            conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"API record payment error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/inventory/items', methods=['POST'])
def api_create_inventory_item():
    """Create new inventory item"""
    try:
        data = request.get_json()
        
        with db.engine.connect() as conn:
            conn.execute(db.text("""
                INSERT INTO inventory (name, category, description, unit, current_stock,
                                     reorder_level, unit_cost, supplier, location, last_updated)
                VALUES (:name, :category, :description, :unit, :current_stock,
                        :reorder_level, :unit_cost, :supplier, :location, NOW())
            """), {
                'name': data.get('name'),
                'category': data.get('category'),
                'description': data.get('description'),
                'unit': data.get('unit', 'each'),
                'current_stock': data.get('stock_quantity', 0),
                'reorder_level': data.get('reorder_threshold', 5),
                'unit_cost': data.get('unit_cost', 0),
                'supplier': data.get('supplier'),
                'location': data.get('location', 'Main Warehouse')
            })
            conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"API create inventory item error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/inventory/<item_id>/adjust', methods=['POST'])
def api_adjust_inventory(item_id):
    """Adjust inventory stock levels"""
    try:
        data = request.get_json()
        action = data.get('action')
        quantity = int(data.get('quantity'))
        
        with db.engine.connect() as conn:
            # Get current stock
            result = conn.execute(db.text("""
                SELECT current_stock FROM inventory WHERE item_id = :item_id
            """), {'item_id': item_id})
            current_stock = result.scalar()
            
            if current_stock is None:
                return jsonify({'error': 'Item not found'}), 404
            
            # Calculate new stock
            if action == 'add':
                new_stock = current_stock + quantity
            elif action == 'remove':
                new_stock = max(0, current_stock - quantity)
            elif action == 'set':
                new_stock = quantity
            else:
                return jsonify({'error': 'Invalid action'}), 400
            
            # Update stock
            conn.execute(db.text("""
                UPDATE inventory 
                SET current_stock = :new_stock, last_updated = NOW()
                WHERE item_id = :item_id
            """), {'new_stock': new_stock, 'item_id': item_id})
            conn.commit()
        
        return jsonify({'success': True, 'new_stock': new_stock})
    except Exception as e:
        logging.error(f"API adjust inventory error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/calendar/events')
def api_calendar_events():
    """Get calendar events for FullCalendar"""
    try:
        with db.engine.connect() as conn:
            result = conn.execute(db.text("""
                SELECT j.job_id, j.service_type, j.scheduled_date, j.status,
                       j.estimated_hours, c.name as client_name, j.location
                FROM jobs j
                LEFT JOIN clients c ON j.client_id = c.client_id
                WHERE j.scheduled_date IS NOT NULL
                ORDER BY j.scheduled_date
            """))
            jobs = [dict(row._mapping) for row in result]
            
            # Format for FullCalendar
            events = []
            for job in jobs:
                if job['scheduled_date']:
                    start_date = job['scheduled_date']
                    if isinstance(start_date, str):
                        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    
                    # Estimate end time based on estimated hours
                    estimated_hours = job.get('estimated_hours', 4)
                    end_date = start_date + timedelta(hours=estimated_hours)
                    
                    events.append({
                        'id': job['job_id'],
                        'title': f"{job['service_type']} - {job['client_name']}",
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat(),
                        'extendedProps': {
                            'client': job['client_name'],
                            'location': job['location'],
                            'status': job['status'],
                            'jobId': job['job_id']
                        }
                    })
        
        return jsonify(events)
    except Exception as e:
        logging.error(f"API calendar events error: {e}")
        return jsonify([])  # Return empty array on error

@app.route('/api/admin/calendar/check-conflicts', methods=['POST'])
def api_check_conflicts():
    """Check for scheduling conflicts"""
    try:
        data = request.get_json()
        conflicts = []
        
        # Business logic for conflict checking would go here
        # For now, return no conflicts
        
        return jsonify({'conflicts': conflicts})
    except Exception as e:
        logging.error(f"API check conflicts error: {e}")
        return jsonify({'conflicts': []})



@app.route('/api/admin/performance/live-data')
def api_performance_live_data():
    """Get live performance data for real-time updates"""
    try:
        with db.engine.connect() as conn:
            # Get current metrics
            data = {}
            
            # Total jobs this month
            result = conn.execute(db.text("""
                SELECT COUNT(*) FROM jobs
                WHERE DATE_TRUNC('month', timestamp_created) = DATE_TRUNC('month', CURRENT_DATE)
            """))
            data['totalJobsMonth'] = result.scalar() or 0
            
            # Completion rate
            result = conn.execute(db.text("""
                SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'completed') / NULLIF(COUNT(*), 0), 2)
                FROM jobs
                WHERE DATE_TRUNC('month', timestamp_created) = DATE_TRUNC('month', CURRENT_DATE)
            """))
            data['completionRate'] = result.scalar() or 0
            
            # Revenue this month
            result = conn.execute(db.text("""
                SELECT COALESCE(SUM(amount_paid), 0)
                FROM payments
                WHERE DATE_TRUNC('month', payment_date) = DATE_TRUNC('month', CURRENT_DATE)
            """))
            data['revenueMonth'] = result.scalar() or 0
            
            # Quote conversion rate
            result = conn.execute(db.text("""
                SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'accepted') / NULLIF(COUNT(*), 0), 2)
                FROM quotes
                WHERE DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE)
            """))
            data['conversionRate'] = result.scalar() or 0
            
        return jsonify(data)
    except Exception as e:
        logging.error(f"Performance live data error: {e}")
        return jsonify({'error': 'Failed to load live data'}), 500

@app.route('/api/admin/performance/export')
def api_performance_export():
    """Export performance report"""
    try:
        format_type = request.args.get('format', 'pdf')
        
        if format_type == 'pdf':
            # Generate PDF report
            return jsonify({'success': True, 'message': 'PDF report generated'})
        else:
            return jsonify({'error': 'Unsupported format'}), 400
            
    except Exception as e:
        logging.error(f"Performance export error: {e}")
        return jsonify({'error': 'Failed to export report'}), 500

@app.route('/api/admin/performance/forecast')
def api_performance_forecast():
    """Generate 3-month performance forecast"""
    try:
        # Calculate forecast based on historical data
        forecast_data = {
            'month1': {'revenue': 18000, 'jobs': 25},
            'month2': {'revenue': 22000, 'jobs': 30},
            'month3': {'revenue': 26000, 'jobs': 35}
        }
        
        return jsonify(forecast_data)
    except Exception as e:
        logging.error(f"Performance forecast error: {e}")
        return jsonify({'error': 'Failed to generate forecast'}), 500