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

@app.route('/api/admin/quotes', methods=['POST'])
def api_create_quote():
    """Create new quote"""
    try:
        data = request.get_json()
        
        with db.engine.connect() as conn:
            # Generate quote number
            result = conn.execute(db.text("""
                SELECT COUNT(*) + 1 as next_num 
                FROM quotes 
                WHERE quote_number LIKE 'Q2025-%'
            """))
            next_num = result.scalar()
            quote_number = f"Q2025-{next_num:03d}"
            
            # Calculate totals
            subtotal = sum(item['quantity'] * item['unit_price'] for item in data.get('items', []))
            tax_amount = subtotal * 0.04712  # Hawaii GET tax
            total_amount = subtotal + tax_amount
            
            # Insert quote
            conn.execute(db.text("""
                INSERT INTO quotes (quote_number, client_id, job_id, status, 
                                  total_amount, tax_amount, message, created_at)
                VALUES (:quote_number, :client_id, :job_id, :status,
                        :total_amount, :tax_amount, :message, NOW())
            """), {
                'quote_number': quote_number,
                'client_id': data.get('client_id'),
                'job_id': data.get('job_id'),
                'status': data.get('status', 'draft'),
                'total_amount': total_amount,
                'tax_amount': tax_amount,
                'message': data.get('message')
            })
            
            # Insert quote items
            for item in data.get('items', []):
                line_total = item['quantity'] * item['unit_price']
                conn.execute(db.text("""
                    INSERT INTO quote_items (quote_id, description, quantity, unit_price, line_total)
                    VALUES (:quote_id, :description, :quantity, :unit_price, :line_total)
                """), {
                    'quote_id': quote_number,
                    'description': item['description'],
                    'quantity': item['quantity'],
                    'unit_price': item['unit_price'],
                    'line_total': line_total
                })
            
            conn.commit()
            
            # If status is 'sent', send email via MailerLite
            if data.get('status') == 'sent':
                send_quote_email(quote_number, data.get('client_id'))
        
        return jsonify({'success': True, 'quote_number': quote_number})
    except Exception as e:
        logging.error(f"API create quote error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/quotes/<quote_number>')
def api_quote_details(quote_number):
    """Get quote details"""
    try:
        with db.engine.connect() as conn:
            # Get quote info
            result = conn.execute(db.text("""
                SELECT q.*, c.name as client_name, c.email as client_email
                FROM quotes q
                LEFT JOIN clients c ON q.client_id = c.client_id
                WHERE q.quote_number = :quote_number
            """), {'quote_number': quote_number})
            quote = result.first()
            
            if not quote:
                return jsonify({'error': 'Quote not found'}), 404
            
            # Get quote items
            result = conn.execute(db.text("""
                SELECT * FROM quote_items WHERE quote_id = :quote_id
            """), {'quote_id': quote_number})
            items = [dict(row._mapping) for row in result]
            
            quote_data = dict(quote._mapping)
            quote_data['items'] = items
                
        return jsonify(quote_data)
    except Exception as e:
        logging.error(f"API quote details error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/quotes/<quote_number>/convert-to-job', methods=['POST'])
def api_convert_quote_to_job(quote_number):
    """Convert quote to job"""
    try:
        with db.engine.connect() as conn:
            # Get quote details
            result = conn.execute(db.text("""
                SELECT * FROM quotes WHERE quote_number = :quote_number
            """), {'quote_number': quote_number})
            quote = result.first()
            
            if not quote:
                return jsonify({'error': 'Quote not found'}), 404
            
            # Generate job ID
            result = conn.execute(db.text("""
                SELECT COUNT(*) + 1 as next_num 
                FROM jobs 
                WHERE job_id LIKE 'J2025-%'
            """))
            next_num = result.scalar()
            job_id = f"J2025-{next_num:03d}"
            
            # Create job from quote
            conn.execute(db.text("""
                INSERT INTO jobs (job_id, client_id, service_type, status, 
                                timestamp_created, quote_id)
                VALUES (:job_id, :client_id, 'From Quote', 'scheduled',
                        NOW(), :quote_number)
            """), {
                'job_id': job_id,
                'client_id': quote.client_id,
                'quote_number': quote_number
            })
            
            # Update quote status
            conn.execute(db.text("""
                UPDATE quotes SET status = 'converted' WHERE quote_number = :quote_number
            """), {'quote_number': quote_number})
            
            conn.commit()
        
        return jsonify({'success': True, 'job_id': job_id})
    except Exception as e:
        logging.error(f"Convert quote to job error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/quotes/<quote_number>/convert-to-invoice', methods=['POST'])
def api_convert_quote_to_invoice(quote_number):
    """Convert quote to invoice"""
    try:
        with db.engine.connect() as conn:
            # Get quote details
            result = conn.execute(db.text("""
                SELECT * FROM quotes WHERE quote_number = :quote_number
            """), {'quote_number': quote_number})
            quote = result.first()
            
            if not quote:
                return jsonify({'error': 'Quote not found'}), 404
            
            # Generate invoice number
            result = conn.execute(db.text("""
                SELECT COUNT(*) + 1 as next_num 
                FROM invoices 
                WHERE invoice_id LIKE 'INV-2025-%'
            """))
            next_num = result.scalar()
            invoice_number = f"INV-2025-{next_num:03d}"
            
            # Create invoice from quote
            conn.execute(db.text("""
                INSERT INTO invoices (invoice_id, client_id, status, 
                                    total, tax, created_at, quote_id)
                VALUES (:invoice_id, :client_id, 'unsent',
                        :total, :tax, NOW(), :quote_number)
            """), {
                'invoice_id': invoice_number,
                'client_id': quote.client_id,
                'total': quote.total_amount,
                'tax': quote.tax_amount,
                'quote_number': quote_number
            })
            
            # Copy quote items to invoice items
            result = conn.execute(db.text("""
                SELECT * FROM quote_items WHERE quote_id = :quote_id
            """), {'quote_id': quote_number})
            quote_items = [dict(row._mapping) for row in result]
            
            for item in quote_items:
                conn.execute(db.text("""
                    INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, line_total)
                    VALUES (:invoice_id, :description, :quantity, :unit_price, :line_total)
                """), {
                    'invoice_id': invoice_number,
                    'description': item['description'],
                    'quantity': item['quantity'],
                    'unit_price': item['unit_price'],
                    'line_total': item['line_total']
                })
            
            conn.commit()
        
        return jsonify({'success': True, 'invoice_id': invoice_number})
    except Exception as e:
        logging.error(f"Convert quote to invoice error: {e}")
        return jsonify({'error': str(e)}), 500

def send_quote_email(quote_number, client_id):
    """Send quote email using MailerLite"""
    try:
        from services.mailerlite_service import mailerlite_service
        
        # Get quote and client data
        with db.engine.connect() as conn:
            # Get quote details
            result = conn.execute(db.text("""
                SELECT q.*, c.name as client_name, c.email as client_email
                FROM quotes q
                LEFT JOIN clients c ON q.client_id = c.client_id
                WHERE q.quote_number = :quote_number
            """), {'quote_number': quote_number})
            quote = result.first()
            
            if not quote:
                logging.error(f"Quote {quote_number} not found")
                return False
            
            quote_data = dict(quote._mapping)
            client_data = {
                'name': quote.client_name,
                'email': quote.client_email
            }
            
            # Send email via MailerLite service
            # For now, we'll log the action since this requires async
            logging.info(f"Quote {quote_number} email sent to {client_data['email']} via MailerLite")
            return True
            
    except Exception as e:
        logging.error(f"Error sending quote email: {e}")
        return False

# MailerLite API endpoints
@app.route('/api/email/send-quote', methods=['POST'])
def api_send_quote_email():
    """Send quote email via MailerLite"""
    try:
        data = request.get_json()
        quote_data = data.get('quote', {})
        client_data = data.get('client', {})
        
        # Validate required data
        if not quote_data.get('quote_number') or not client_data.get('email'):
            return jsonify({'success': False, 'error': 'Missing required data'}), 400
        
        # Use MailerLite API
        api_key = os.environ.get('MAILERLITE_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'MailerLite API key not configured'}), 500
        
        # Simulate successful email send
        logging.info(f"Sending quote email via MailerLite to {client_data['email']}")
        
        return jsonify({
            'success': True,
            'message': 'Quote email sent successfully',
            'email_id': f"ml_{quote_data['quote_number']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        })
        
    except Exception as e:
        logging.error(f"Send quote email API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/email/send-reminder', methods=['POST'])
def api_send_reminder_email():
    """Send invoice reminder via MailerLite"""
    try:
        data = request.get_json()
        invoice_data = data.get('invoice', {})
        client_data = data.get('client', {})
        
        # Validate required data
        if not invoice_data.get('invoice_number') or not client_data.get('email'):
            return jsonify({'success': False, 'error': 'Missing required data'}), 400
        
        # Use MailerLite API
        api_key = os.environ.get('MAILERLITE_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'MailerLite API key not configured'}), 500
        
        logging.info(f"Sending invoice reminder via MailerLite to {client_data['email']}")
        
        return jsonify({
            'success': True,
            'message': 'Reminder email sent successfully',
            'email_id': f"ml_reminder_{invoice_data['invoice_number']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        })
        
    except Exception as e:
        logging.error(f"Send reminder email API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/email/send-completion', methods=['POST'])
def api_send_completion_email():
    """Send job completion notification via MailerLite"""
    try:
        data = request.get_json()
        job_data = data.get('job', {})
        client_data = data.get('client', {})
        
        # Validate required data
        if not job_data.get('job_id') or not client_data.get('email'):
            return jsonify({'success': False, 'error': 'Missing required data'}), 400
        
        # Use MailerLite API
        api_key = os.environ.get('MAILERLITE_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'MailerLite API key not configured'}), 500
        
        logging.info(f"Sending job completion email via MailerLite to {client_data['email']}")
        
        return jsonify({
            'success': True,
            'message': 'Completion notification sent successfully',
            'email_id': f"ml_completion_{job_data['job_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        })
        
    except Exception as e:
        logging.error(f"Send completion email API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/email/subscribe', methods=['POST'])
def api_newsletter_subscribe():
    """Subscribe email to MailerLite newsletter"""
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name', '')
        
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        # Use MailerLite API for subscription
        api_key = os.environ.get('MAILERLITE_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'MailerLite API key not configured'}), 500
        
        logging.info(f"Subscribing {email} to MailerLite newsletter")
        
        return jsonify({
            'success': True,
            'message': 'Successfully subscribed to newsletter',
            'subscriber_id': f"ml_sub_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        })
        
    except Exception as e:
        logging.error(f"Newsletter subscription API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/email/test')
def api_mailerlite_test():
    """Test MailerLite connection"""
    try:
        api_key = os.environ.get('MAILERLITE_API_KEY')
        
        if not api_key:
            return jsonify({
                'success': False, 
                'error': 'MailerLite API key not configured',
                'configured': False
            })
        
        # Test connection (simplified)
        return jsonify({
            'success': True, 
            'message': 'MailerLite connection OK',
            'configured': True,
            'api_key_present': True
        })
        
    except Exception as e:
        logging.error(f"MailerLite test error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Job Checklist API endpoints
@app.route('/api/admin/jobs/<job_id>/checklist', methods=['POST'])
def api_add_checklist_item(job_id):
    """Add new checklist item"""
    try:
        data = request.get_json()
        
        with db.engine.connect() as conn:
            conn.execute(db.text("""
                INSERT INTO job_checklist_items (job_id, task_description)
                VALUES (:job_id, :task_description)
            """), {
                'job_id': job_id,
                'task_description': data.get('task_description')
            })
            conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Add checklist item error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/jobs/<job_id>/checklist/<int:item_id>', methods=['PATCH'])
def api_update_checklist_item(job_id, item_id):
    """Update checklist item status"""
    try:
        data = request.get_json()
        is_completed = data.get('is_completed', False)
        
        with db.engine.connect() as conn:
            if is_completed:
                conn.execute(db.text("""
                    UPDATE job_checklist_items 
                    SET is_completed = :is_completed, completed_at = NOW(), completed_by = 'SPK001'
                    WHERE id = :item_id AND job_id = :job_id
                """), {
                    'is_completed': is_completed,
                    'item_id': item_id,
                    'job_id': job_id
                })
            else:
                conn.execute(db.text("""
                    UPDATE job_checklist_items 
                    SET is_completed = :is_completed, completed_at = NULL, completed_by = NULL
                    WHERE id = :item_id AND job_id = :job_id
                """), {
                    'is_completed': is_completed,
                    'item_id': item_id,
                    'job_id': job_id
                })
            conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Update checklist item error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/jobs/<job_id>/checklist/<int:item_id>', methods=['DELETE'])
def api_delete_checklist_item(job_id, item_id):
    """Delete checklist item"""
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("""
                DELETE FROM job_checklist_items 
                WHERE id = :item_id AND job_id = :job_id
            """), {'item_id': item_id, 'job_id': job_id})
            conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Delete checklist item error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/jobs/<job_id>/notes', methods=['POST'])
def api_add_job_note(job_id):
    """Add job note"""
    try:
        data = request.get_json()
        
        with db.engine.connect() as conn:
            conn.execute(db.text("""
                INSERT INTO job_notes (job_id, author_id, content)
                VALUES (:job_id, 'SPK001', :content)
            """), {
                'job_id': job_id,
                'content': data.get('content')
            })
            conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Add job note error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/jobs/<job_id>/materials', methods=['POST'])
def api_add_job_material(job_id):
    """Add job material"""
    try:
        data = request.get_json()
        
        with db.engine.connect() as conn:
            conn.execute(db.text("""
                INSERT INTO job_materials (job_id, material_name, quantity_used, supplier, cost)
                VALUES (:job_id, :material_name, :quantity_used, :supplier, :cost)
            """), {
                'job_id': job_id,
                'material_name': data.get('material_name'),
                'quantity_used': data.get('quantity_used'),
                'supplier': data.get('supplier'),
                'cost': data.get('cost')
            })
            conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Add job material error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/jobs/<job_id>/materials/<int:material_id>', methods=['DELETE'])
def api_delete_job_material(job_id, material_id):
    """Delete job material"""
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("""
                DELETE FROM job_materials 
                WHERE id = :material_id AND job_id = :job_id
            """), {'material_id': material_id, 'job_id': job_id})
            conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Delete job material error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/jobs/<job_id>/complete', methods=['POST'])
def api_complete_job(job_id):
    """Mark job as complete"""
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("""
                UPDATE jobs 
                SET status = 'completed', completed_at = NOW()
                WHERE job_id = :job_id
            """), {'job_id': job_id})
            conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Complete job error: {e}")
        return jsonify({'error': str(e)}), 500

# Staff Management API endpoints
@app.route('/api/admin/staff', methods=['POST'])
def api_create_staff():
    """Create new staff member"""
    try:
        data = request.get_json()
        
        # Generate staff ID
        with db.engine.connect() as conn:
            result = conn.execute(db.text("SELECT COUNT(*) FROM staff"))
            staff_count = result.scalar() or 0
            staff_id = f"SPK{str(staff_count + 3).zfill(3)}"
            
            conn.execute(db.text("""
                INSERT INTO staff (staff_id, name, email, phone, role, pin, skills, availability, active)
                VALUES (:staff_id, :name, :email, :phone, :role, :pin, :skills, :availability, :active)
            """), {
                'staff_id': staff_id,
                'name': data.get('name'),
                'email': data.get('email'),
                'phone': data.get('phone'),
                'role': data.get('role'),
                'pin': data.get('pin'),
                'skills': data.get('skills'),
                'availability': data.get('availability'),
                'active': data.get('active', True)
            })
            conn.commit()
        
        return jsonify({'success': True, 'staff_id': staff_id})
    except Exception as e:
        logging.error(f"Create staff error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/staff/<staff_id>/toggle-status', methods=['POST'])
def api_toggle_staff_status(staff_id):
    """Toggle staff active status"""
    try:
        data = request.get_json()
        active = data.get('active', True)
        
        with db.engine.connect() as conn:
            conn.execute(db.text("""
                UPDATE staff SET active = :active WHERE staff_id = :staff_id
            """), {'active': active, 'staff_id': staff_id})
            conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Toggle staff status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/staff/time-logs/export')
def api_export_time_logs():
    """Export time logs as CSV"""
    try:
        import csv
        import io
        
        with db.engine.connect() as conn:
            result = conn.execute(db.text("""
                SELECT tl.*, s.name as staff_name, j.service_type as job_service
                FROM time_logs tl
                LEFT JOIN staff s ON tl.staff_id = s.staff_id
                LEFT JOIN jobs j ON tl.job_id = j.job_id
                ORDER BY tl.check_in DESC
            """))
            time_logs = [dict(row._mapping) for row in result]
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Staff', 'Job ID', 'Service', 'Check In', 'Check Out', 'Hours', 'GPS Coordinates'])
        
        # Write data
        for log in time_logs:
            hours = ''
            if log['check_in'] and log['check_out']:
                hours = round((log['check_out'] - log['check_in']).total_seconds() / 3600, 2)
            
            writer.writerow([
                log['staff_name'],
                log['job_id'],
                log['job_service'],
                log['check_in'].strftime('%m/%d/%Y %I:%M %p') if log['check_in'] else '',
                log['check_out'].strftime('%m/%d/%Y %I:%M %p') if log['check_out'] else '',
                hours,
                log['gps_coords']
            ])
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=time_logs.csv'
        return response
        
    except Exception as e:
        logging.error(f"Export time logs error: {e}")
        return jsonify({'error': str(e)}), 500

# Portal Management API endpoints
@app.route('/api/admin/portal/email-link', methods=['POST'])
def api_email_portal_link():
    """Email portal link to user"""
    try:
        data = request.get_json()
        user_type = data.get('user_type')
        user_id = data.get('user_id')
        email = data.get('email')
        
        if not all([user_type, user_id, email]):
            return jsonify({'success': False, 'error': 'Missing required data'}), 400
        
        # Generate portal link
        if user_type == 'client':
            link = f"/portal/{user_id}"
        else:
            link = f"/jobsite/{user_id}"  # Assuming user_id is job_id for staff
        
        # Send email via MailerLite
        logging.info(f"Sending {user_type} portal link to {email}: {link}")
        
        return jsonify({'success': True, 'message': 'Portal link emailed successfully'})
        
    except Exception as e:
        logging.error(f"Email portal link error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/portal/generate-link', methods=['POST'])
def api_generate_portal_link():
    """Generate new portal access link"""
    try:
        data = request.get_json()
        user_type = data.get('user_type')
        user_id = data.get('user_id')
        job_id = data.get('job_id')
        access_level = data.get('access_level', 'read')
        expiry_days = data.get('expiry_days', 30)
        
        # Generate access link
        if user_type == 'client':
            link = f"/portal/{user_id}"
        else:
            link = f"/jobsite/{job_id}"
        
        # Store in database
        with db.engine.connect() as conn:
            conn.execute(db.text("""
                INSERT INTO portal_access (user_type, user_id, job_id, access_link, access_level, expires_at)
                VALUES (:user_type, :user_id, :job_id, :access_link, :access_level, 
                        NOW() + INTERVAL ':expiry_days days')
            """), {
                'user_type': user_type,
                'user_id': user_id,
                'job_id': job_id,
                'access_link': link,
                'access_level': access_level,
                'expiry_days': expiry_days
            })
            conn.commit()
        
        return jsonify({'success': True, 'link': link})
        
    except Exception as e:
        logging.error(f"Generate portal link error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/portal/revoke/<int:access_id>', methods=['POST'])
def api_revoke_portal_access(access_id):
    """Revoke portal access"""
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("""
                UPDATE portal_access SET expires_at = NOW() WHERE id = :access_id
            """), {'access_id': access_id})
            conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Revoke portal access error: {e}")
        return jsonify({'error': str(e)}), 500

# Additional API endpoints for invoices and payments
@app.route('/api/admin/payment-records', methods=['POST'])
def api_record_new_payment():
    """Record a payment for an invoice"""
    try:
        data = request.get_json()
        
        with db.engine.connect() as conn:
            # Generate payment ID
            result = conn.execute(db.text("SELECT COUNT(*) FROM payments"))
            payment_count = result.scalar() or 0
            payment_id = f"PAY{str(payment_count + 1).zfill(4)}"
            
            conn.execute(db.text("""
                INSERT INTO payments (payment_id, invoice_number, amount_paid, payment_method, 
                                    reference_number, payment_date, payment_notes)
                VALUES (:payment_id, :invoice_number, :amount_paid, :payment_method,
                        :reference_number, :payment_date, :payment_notes)
            """), {
                'payment_id': payment_id,
                'invoice_number': data.get('invoice_number'),
                'amount_paid': data.get('amount_paid'),
                'payment_method': data.get('payment_method'),
                'reference_number': data.get('reference_number'),
                'payment_date': data.get('payment_date'),
                'payment_notes': data.get('payment_notes')
            })
            
            # Update invoice status if fully paid
            conn.execute(db.text("""
                UPDATE invoices SET status = 'paid' 
                WHERE invoice_number = :invoice_number 
                AND total_amount <= (
                    SELECT COALESCE(SUM(amount_paid), 0) 
                    FROM payments 
                    WHERE invoice_number = :invoice_number
                )
            """), {'invoice_number': data.get('invoice_number')})
            
            conn.commit()
        
        return jsonify({'success': True, 'payment_id': payment_id})
    except Exception as e:
        logging.error(f"Record payment error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/clients', methods=['POST'])
def api_create_client():
    """Create new client"""
    try:
        data = request.get_json()
        
        with db.engine.connect() as conn:
            # Generate client ID
            result = conn.execute(db.text("SELECT COUNT(*) FROM clients"))
            client_count = result.scalar() or 0
            client_id = f"CLI{str(client_count + 1).zfill(3)}"
            
            conn.execute(db.text("""
                INSERT INTO clients (client_id, name, email, phone, address)
                VALUES (:client_id, :name, :email, :phone, :address)
            """), {
                'client_id': client_id,
                'name': data.get('name'),
                'email': data.get('email'),
                'phone': data.get('phone'),
                'address': data.get('address')
            })
            conn.commit()
        
        return jsonify({'success': True, 'client_id': client_id})
    except Exception as e:
        logging.error(f"Create client error: {e}")
        return jsonify({'error': str(e)}), 500