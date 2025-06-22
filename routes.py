import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file, abort
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import uuid
import pytz

# Import services after Flask setup to avoid circular imports
try:
    from models import HandymanStorage
    from ai_service import ai_service
    from notification_service import NotificationService
    from auth_service import auth_service
    from phone_formatter import phone_formatter
    from unified_scheduler import unified_scheduler
    logging.info("All required modules imported successfully")
except ImportError as e:
    logging.error(f"Critical import error in routes.py: {e}")
    logging.error("This may cause application functionality issues")
    # Create fallback objects to prevent crashes
    class FallbackService:
        def __getattr__(self, name):
            logging.warning(f"Fallback service called for missing method: {name}")
            return lambda *args, **kwargs: None
    
    HandymanStorage = FallbackService
    ai_service = FallbackService()
    NotificationService = FallbackService
    auth_service = FallbackService()
    phone_formatter = FallbackService()

# Initialize services with proper error handling
try:
    handyman_storage = HandymanStorage()
    notification_service = NotificationService()
    
    # Initialize file storage service
    from file_storage_service import FileStorageService
    file_storage = FileStorageService()
    
    # Initialize all required services
    from storage_service import StorageService
    from reminder_service import ReminderService
    from job_tracking_service import JobTrackingService
    from financial_reporting_service import FinancialReportingService
    from inventory_service import InventoryService
    from checklist_service import ChecklistService
    
    storage_service = StorageService()
    reminder_service = ReminderService()
    job_tracking_service = JobTrackingService()
    financial_reporting_service = FinancialReportingService()
    inventory_service = InventoryService()
    checklist_service = ChecklistService()
    
    logging.info("All services initialized successfully")
except Exception as e:
    logging.error(f"Service initialization error: {e}")
    # Ensure required services are always available, even as fallbacks
    if 'handyman_storage' not in locals():
        try:
            handyman_storage = HandymanStorage()
        except:
            handyman_storage = None
    if 'notification_service' not in locals():
        notification_service = None
    if 'storage_service' not in locals():
        storage_service = None
    if 'reminder_service' not in locals():
        reminder_service = None
    if 'job_tracking_service' not in locals():
        job_tracking_service = None
    if 'financial_reporting_service' not in locals():
        financial_reporting_service = None
    if 'inventory_service' not in locals():
        inventory_service = None
    if 'checklist_service' not in locals():
        checklist_service = None

# Get app instance after imports to avoid circular import
def get_app():
    from app import app
    return app

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
from app import app

@app.route('/')
def index():
    """Homepage with hero section and services overview"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page with company information"""
    return render_template('about.html')

@app.route('/services')
def services():
    """Services page with comprehensive handyman service listings"""
    return render_template('services.html')

@app.route('/pricing')
def pricing():
    """Pricing page with service rates and packages"""
    return render_template('pricing.html')

@app.route('/spank-school')
def spank_school():
    """Spank School - Educational DIY learning platform"""
    return render_template('spank_school.html')

@app.route('/reviews')
def reviews():
    """Customer reviews and testimonials page"""
    return render_template('reviews.html')

@app.route('/admin')
def admin_redirect():
    """Redirect to admin login"""
    return redirect(url_for('admin_login'))

@app.route('/staff-portal')
def staff_portal_redirect():
    """Redirect to staff portal login"""
    return redirect(url_for('portal_login'))

@app.route('/test-email-interface')
def test_email_interface():
    """Email testing interface for SPANK Buck rewards"""
    return render_template('test_email.html')

@app.route('/consultation', methods=['GET', 'POST'])
def consultation():
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

        # Basic validation
        if not all([name, email, phone, service]):
            flash('Please fill in all required fields.', 'error')
            return render_template('consultation.html')

        # Store booking
        try:
            request_id = handyman_storage.add_service_request({
                'name': name,
                'email': email,
                'phone': phone,
                'service': service,
                'preferred_date': preferred_date,
                'preferred_time': preferred_time,
                'location': f"{consultation_type} consultation" if consultation_type else None,
                'description': f"{message}. Project type: {project_type}. Square footage: {square_footage}" if message else f"Project type: {project_type}. Square footage: {square_footage}",
                'budget_range': None
            })

            # Automatically create unified appointment with client/job IDs
            appointment_data = {
                'client_name': name,
                'client_phone': phone_formatter.format_phone(phone),
                'client_email': email,
                'service_type': service,
                'scheduled_date': preferred_date if preferred_date else (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'scheduled_time': preferred_time if preferred_time else '09:00',
                'status': 'tentative',
                'priority': 'normal',
                'location': f"{consultation_type} consultation" if consultation_type else '',
                'notes': f"Auto-created from consultation request. {message}. Project: {project_type}. Sq ft: {square_footage}",
                'booking_reference': request_id,
                'created_by': 'system_auto',
                'tags': ['consultation', 'auto_created']
            }
            
            appointment = unified_scheduler.create_appointment(appointment_data)
            
            # Send inquiry alert to admin with appointment details
            notification_service.send_inquiry_alert(
                inquiry_type="consultation",
                customer_name=name,
                phone_number=phone,
                email=email,
                service_type=service,
                additional_info=f"Auto-scheduled: {appointment['client_id']}/{appointment['job_id']} for {preferred_date or 'next day'}"
            )
            
            logging.info(f"New service request created with ID: {request_id}")
            return redirect(url_for('form_confirmation', 
                                  form_type='consultation',
                                  customer_name=name,
                                  customer_phone=phone,
                                  customer_email=email,
                                  service_type=service,
                                  confirmation_id=request_id))

        except Exception as e:
            logging.error(f"Error creating booking: {e}")
            flash('There was an error submitting your request. Please try again or call us directly.', 'error')

    return render_template('consultation.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with business information and form handling"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('contact_name', '').strip()
        email = request.form.get('contact_email', '').strip()
        phone = phone_formatter.format_phone(request.form.get('contact_phone', '').strip())
        subject = request.form.get('contact_subject', '').strip()
        message = request.form.get('contact_message', '').strip()

        # Basic validation
        if not all([name, email, message]):
            flash('Please fill in all required fields.', 'error')
            return render_template('contact.html')

        # Store contact message
        try:
            message_id = handyman_storage.add_contact_message({
                'name': name,
                'email': email,
                'phone': phone,
                'subject': subject,
                'message': message
            })

            # Auto-create appointment for service-related inquiries
            service_keywords = ['drywall', 'floor', 'fence', 'plumb', 'electric', 'paint', 'repair', 'renovation', 'handyman']
            is_service_inquiry = any(keyword in (subject + ' ' + message).lower() for keyword in service_keywords)
            
            if is_service_inquiry:
                # Determine service type from keywords
                service_type = 'General Handyman'
                if 'drywall' in (subject + ' ' + message).lower():
                    service_type = 'Drywall Services'
                elif 'floor' in (subject + ' ' + message).lower():
                    service_type = 'Flooring Installation'
                elif 'fence' in (subject + ' ' + message).lower():
                    service_type = 'Fence Building'
                elif 'plumb' in (subject + ' ' + message).lower():
                    service_type = 'Plumbing Repair'
                elif 'electric' in (subject + ' ' + message).lower():
                    service_type = 'Electrical Work'
                elif 'paint' in (subject + ' ' + message).lower():
                    service_type = 'Painting'
                elif 'renovation' in (subject + ' ' + message).lower():
                    service_type = 'Home Renovation'
                
                appointment_data = {
                    'client_name': name,
                    'client_phone': phone,
                    'client_email': email,
                    'service_type': service_type,
                    'scheduled_date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                    'scheduled_time': '10:00',
                    'status': 'tentative',
                    'priority': 'normal',
                    'location': '',
                    'notes': f"Auto-created from contact form. Subject: {subject}. Message: {message}",
                    'booking_reference': message_id,
                    'created_by': 'system_auto',
                    'tags': ['contact_form', 'auto_created']
                }
                
                appointment = unified_scheduler.create_appointment(appointment_data)
                
                # Send enhanced notification with appointment details
                notification_service.send_inquiry_alert(
                    inquiry_type="contact",
                    customer_name=name,
                    phone_number=phone,
                    email=email,
                    service_type=service_type,
                    additional_info=f"Service inquiry auto-scheduled: {appointment['client_id']}/{appointment['job_id']} for {appointment['scheduled_date']}"
                )
            else:
                # Send standard notification for general inquiries
                notification_service.send_inquiry_alert(
                    inquiry_type="contact",
                    customer_name=name,
                    phone_number=phone,
                    email=email
                )
            
            logging.info(f"New contact message created with ID: {message_id}")
            return redirect(url_for('form_confirmation', 
                                  form_type='contact',
                                  customer_name=name,
                                  customer_phone=phone,
                                  customer_email=email,
                                  confirmation_id=message_id))

        except Exception as e:
            logging.error(f"Error creating contact message: {e}")
            flash('There was an error sending your message. Please try again or call us directly.', 'error')

    return render_template('contact.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin and staff login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Check admin credentials
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['user_role'] = 'admin'
            session['user_name'] = 'Admin'
            logging.info("Admin login successful")
            return redirect(url_for('admin_dashboard'))

        # Check staff credentials
        for staff_login in staff_logins:
            if staff_login.username == username and staff_login.password == password:
                # Find staff member details
                staff_member = None
                for staff in staff_members:
                    if staff.id == staff_login.staff_id and staff.active:
                        staff_member = staff
                        break

                if staff_member:
                    session['admin_logged_in'] = True
                    session['user_role'] = 'staff'
                    session['user_name'] = staff_member.name
                    session['staff_id'] = staff_member.id
                    logging.info(f"Staff login successful: {staff_member.name}")
                    return redirect(url_for('admin_dashboard'))

        flash('Invalid credentials. Please try again.', 'error')
        logging.warning(f"Failed login attempt for username: {username}")

    return render_template('admin_login_clean.html')

@app.route('/admin/ai-leads')
def ai_leads():
    """AI Lead Generator page for analyzing and managing leads"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access the AI lead generator.', 'error')
        return redirect(url_for('admin_login'))

    # Get all leads and analyze them with AI
    leads = handyman_storage.get_all_leads()
    contact_messages = handyman_storage.get_all_contact_messages()
    service_requests = handyman_storage.get_all_service_requests()

    # Analyze unanalyzed contact messages with AI
    for message in contact_messages:
        if not message.ai_analysis:
            try:
                analysis = ai_service.analyze_contact_message(message)
                message.ai_analysis = analysis
                message.priority_score = analysis.get('urgency_score', 0)
            except Exception as e:
                logging.error(f"AI analysis failed for message {message.id}: {e}")

    # Generate service recommendations for pending requests
    for request in service_requests:
        if not request.ai_recommendations and request.status == 'pending':
            try:
                recommendations = ai_service.generate_service_recommendations(request)
                request.ai_recommendations = recommendations
                request.estimated_duration = recommendations.get('estimated_project_duration', 'TBD')
                request.estimated_cost = recommendations.get('material_considerations', 'TBD')
            except Exception as e:
                logging.error(f"AI recommendations failed for request {request.id}: {e}")

    # Score existing leads
    for lead in leads:
        if lead.ai_score == 0:
            try:
                scoring = ai_service.score_lead_quality(lead)
                lead.ai_score = scoring.get('conversion_score', 0)
                lead.follow_up_suggestions = scoring.get('recommended_approach', '')
            except Exception as e:
                logging.error(f"AI scoring failed for lead {lead.id}: {e}")

    # Get high priority items
    high_priority_messages = [m for m in contact_messages if m.priority_score >= 7]
    high_value_leads = handyman_storage.get_high_priority_leads()
    urgent_requests = [r for r in service_requests if r.priority == 'high' or (r.ai_recommendations and 'urgent' in str(r.ai_recommendations).lower())]

    return render_template('admin/ai_leads.html',
                         leads=leads,
                         contact_messages=contact_messages,
                         service_requests=service_requests,
                         high_priority_messages=high_priority_messages,
                         high_value_leads=high_value_leads,
                         urgent_requests=urgent_requests)

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard showing all bookings, contact messages, and weekly calendar"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access the admin dashboard.', 'error')
        return redirect(url_for('admin_login'))

    try:
        service_requests = handyman_storage.get_all_service_requests()
        contact_messages = handyman_storage.get_all_contact_messages()

        # Generate current week dates for calendar using Hawaii timezone
        hawaii_now = get_hawaii_time()

        # Get the start of the week (Monday) in Hawaii time
        start_of_week = hawaii_now - timedelta(days=hawaii_now.weekday())
        week_dates = [(start_of_week + timedelta(days=i)) for i in range(7)]

        # Get appointments for current week
        week_appointments = []
        for appointment in appointments:
            try:
                appointment_date = datetime.strptime(appointment['date'], '%Y-%m-%d')
                if start_of_week <= appointment_date < start_of_week + timedelta(days=7):
                    week_appointments.append(appointment)
            except (KeyError, ValueError, TypeError) as e:
                logging.warning(f"Invalid appointment data: {appointment} - {e}")
                continue

        # Only show authentic data - actual contact messages and service requests
        pending_requests = [req for req in service_requests if hasattr(req, 'status') and req.status == 'pending']
        urgent_requests = [req for req in service_requests if getattr(req, 'priority', 'medium') == 'high']
        
        # Get admin notifications for manual processing
        try:
            admin_notifications = handyman_storage.get_admin_notifications()
        except Exception as e:
            logging.warning(f"Error getting admin notifications: {e}")
            admin_notifications = []

        return render_template('admin_dashboard.html',
                             bookings=service_requests,
                             service_requests=service_requests, 
                             contact_messages=contact_messages,
                             week_dates=week_dates,
                             week_appointments=week_appointments,
                             staff_members=staff_members,
                             staff_logins=staff_logins,
                             today=hawaii_now.strftime('%Y-%m-%d'),
                             user_role=session.get('user_role', 'admin'),
                             user_name=session.get('user_name', 'Admin'),
                             # Only authentic data
                             pending_requests=pending_requests,
                             urgent_requests=urgent_requests,
                             admin_notifications=admin_notifications)
    
    except Exception as e:
        logging.error(f"Error loading admin dashboard: {e}")
        flash('Dashboard temporarily unavailable. Please try again.', 'error')
        return render_template('admin_login.html')

@app.route('/admin/notifications/<int:notification_id>/complete', methods=['POST'])
def mark_notification_complete(notification_id):
    """Mark a notification as complete"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401

    try:
        success = handyman_storage.mark_notification_read(notification_id)
        if success:
            return jsonify({'success': True, 'message': 'Notification marked as complete'})
        else:
            return jsonify({'success': False, 'error': 'Notification not found'}), 404
    except Exception as e:
        logging.error(f"Error marking notification {notification_id} as complete: {e}")
        return jsonify({'success': False, 'error': 'Internal error'}), 500

@app.route('/admin/twilio-config')
def twilio_config():
    """Legacy Twilio configuration page - now shows manual notification system info"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access configuration.', 'error')
        return redirect(url_for('admin_login'))
    
    return render_template('twilio_config.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/booking/<int:booking_id>/complete')
def complete_booking(booking_id):
    """Mark a booking as completed"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    try:
        success = handyman_storage.update_service_request_status(booking_id, 'completed')
        if success:
            flash('Booking marked as completed.', 'success')
        else:
            flash('Booking not found.', 'error')
    except Exception as e:
        logging.error(f"Error updating booking {booking_id}: {e}")
        flash('Error updating booking status.', 'error')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/booking/<int:booking_id>/update', methods=['POST'])
def update_booking(booking_id):
    """Update booking status"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    status = request.form.get('status')
    if status in ['pending', 'confirmed', 'completed', 'cancelled']:
        try:
            handyman_storage.update_service_request_status(booking_id, status)
            flash(f'Booking status updated to {status}.', 'success')
        except Exception as e:
            logging.error(f"Error updating booking {booking_id}: {e}")
            flash('Error updating booking status.', 'error')
    else:
        flash('Invalid status.', 'error')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/booking/<int:booking_id>/delete')
def delete_booking(booking_id):
    """Delete a booking"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    try:
        # Check if booking exists before deletion
        request_exists = any(r.id == booking_id for r in handyman_storage.get_all_service_requests())
        if request_exists:
            handyman_storage.delete_service_request(booking_id)
            flash('Booking deleted successfully.', 'success')
        else:
            flash('Booking not found.', 'error')
    except Exception as e:
        logging.error(f"Error deleting booking {booking_id}: {e}")
        flash('Error deleting booking.', 'error')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/message/<int:message_id>/read')
def mark_message_read(message_id):
    """Mark a contact message as read"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    try:
        success = handyman_storage.update_message_status(message_id, 'read')
        if success:
            flash('Message marked as read.', 'success')
        else:
            flash('Message not found.', 'error')
    except Exception as e:
        logging.error(f"Error updating message {message_id}: {e}")
        flash('Error updating message status.', 'error')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/message/<int:message_id>/delete')
def delete_contact_message(message_id):
    """Delete a contact message"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    try:
        # Check if message exists before deletion
        message_exists = any(m.id == message_id for m in handyman_storage.get_all_contact_messages())
        if message_exists:
            handyman_storage.delete_contact_message(message_id)
            flash('Contact message deleted successfully.', 'success')
        else:
            flash('Message not found.', 'error')
    except Exception as e:
        logging.error(f"Error deleting message {message_id}: {e}")
        flash('Error deleting message.', 'error')

    return redirect(url_for('admin_dashboard'))

# Appointment scheduling routes
@app.route("/admin/appointment/add", methods=["POST"])
def add_appointment():
    """Add a new appointment"""
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    try:
        appointment = {
            "id": len(appointments) + 1,
            "date": request.form.get("appointment_date"),
            "time": request.form.get("appointment_time"),
            "client_name": request.form.get("client_name"),
            "client_phone": request.form.get("client_phone"),
            "client_email": request.form.get("client_email"),
            "service": request.form.get("service"),
            "notes": request.form.get("notes", ""),
            "staff_id": request.form.get("staff_id"),
            "status": "scheduled",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "created_by": session.get('user_name', 'Admin')
        }
        appointments.append(appointment)
        flash("Appointment scheduled successfully!", "success")
    except Exception as e:
        logging.error(f"Error adding appointment: {e}")
        flash("Error scheduling appointment.", "error")

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/appointment/from_booking/<int:booking_id>", methods=["POST"])
def schedule_from_booking(booking_id):
    """Schedule appointment from consultation booking"""
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    try:
        # Find the booking
        booking = None
        for b in handyman_storage.get_all_service_requests():
            if b.id == booking_id:
                booking = b
                break

        if not booking:
            flash("Booking not found.", "error")
            return redirect(url_for("admin_dashboard"))

        appointment = {
            "id": len(appointments) + 1,
            "date": request.form.get("appointment_date"),
            "time": request.form.get("appointment_time"),
            "client_name": booking.name,
            "client_phone": booking.phone,
            "client_email": booking.email,
            "service": booking.service,
            "notes": f"From consultation: {booking.consultation_type}. {booking.message or ''}",
            "staff_id": request.form.get("staff_id"),
            "status": "scheduled",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "booking_id": booking_id,
            "created_by": session.get('user_name', 'Admin')
        }
        appointments.append(appointment)

        # Update service request status
        handyman_storage.update_service_request_status(booking_id, "scheduled")
        flash("Appointment scheduled from consultation request!", "success")
    except Exception as e:
        logging.error(f"Error scheduling appointment from booking {booking_id}: {e}")
        flash("Error scheduling appointment.", "error")

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/appointment/<int:appointment_id>/update", methods=["POST"])
def update_appointment(appointment_id):
    """Update appointment status"""
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    try:
        status = request.form.get("status")
        for appointment in appointments:
            if appointment["id"] == appointment_id:
                appointment["status"] = status
                flash(f"Appointment status updated to {status}", "success")
                break
        else:
            flash("Appointment not found.", "error")
    except Exception as e:
        logging.error(f"Error updating appointment {appointment_id}: {e}")
        flash("Error updating appointment.", "error")

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/appointment/<int:appointment_id>/delete", methods=["POST"])
def delete_appointment(appointment_id):
    """Delete appointment"""
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    try:
        global appointments
        appointments = [a for a in appointments if a["id"] != appointment_id]
        flash("Appointment deleted successfully.", "success")
    except Exception as e:
        logging.error(f"Error deleting appointment {appointment_id}: {e}")
        flash("Error deleting appointment.", "error")

    return redirect(url_for("admin_dashboard"))


# Staff management routes
@app.route("/admin/staff/add", methods=["POST"])
def add_staff():
    """Add a new staff member"""
    if not session.get("admin_logged_in") or session.get("user_role") != "admin":
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        staff = Staff(
            name=request.form.get("staff_name"),
            email=request.form.get("staff_email"),
            phone=request.form.get("staff_phone"),
            role=request.form.get("staff_role")
        )
        staff_members.append(staff)
        flash(f"Staff member {staff.name} added successfully!", "success")
    except Exception as e:
        logging.error(f"Error adding staff: {e}")
        flash("Error adding staff member.", "error")

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/staff/<int:staff_id>/create_login", methods=["POST"])
def create_staff_login(staff_id):
    """Create login credentials for staff member"""
    if not session.get("admin_logged_in") or session.get("user_role") != "admin":
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("admin_dashboard"))
    try:
        # Check if staff member exists
        staff_member = None
        for staff in staff_members:
            if staff.id == staff_id:
                staff_member = staff
                break

        if not staff_member:
            flash("Staff member not found.", "error")
            return redirect(url_for("admin_dashboard"))

        # Check if login already exists
        existing_login = None
        for login in staff_logins:
            if login.staff_id == staff_id:
                existing_login = login
                break

        if existing_login:
            flash("Login already exists for this staff member.", "warning")
            return redirect(url_for("admin_dashboard"))

        username = request.form.get("username")
        password = request.form.get("password")

        # Check if username is already taken
        for login in staff_logins:
            if login.username == username:
                flash("Username already taken.", "error")
                return redirect(url_for("admin_dashboard"))

        if username == ADMIN_USERNAME:
            flash("Username conflicts with admin account.", "error")
            return redirect(url_for("admin_dashboard"))

        staff_login = StaffLogin(staff_id, username, password)
        staff_logins.append(staff_login)
        flash(f"Login created for {staff_member.name}!", "success")
    except Exception as e:
        logging.error(f"Error creating staff login: {e}")
        flash("Error creating staff login.", "error")

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/staff/<int:staff_id>/toggle_status", methods=["POST"])
def toggle_staff_status(staff_id):
    """Toggle staff member active status"""
    if not session.get("admin_logged_in") or session.get("user_role") != "admin":
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("admin_dashboard"))
    try:
        for staff in staff_members:
            if staff.id == staff_id:
                staff.active = not staff.active
                status = "activated" if staff.active else "deactivated"
                flash(f"Staff member {staff.name} {status}.", "success")
                break
        else:
            flash("Staff member not found.", "error")
    except Exception as e:
        logging.error(f"Error toggling staff status: {e}")
        flash("Error updating staff status.", "error")

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/appointment/<int:appointment_id>/add_note", methods=["POST"])
def add_appointment_note(appointment_id):
    """Add or update notes for an appointment"""
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    try:
        note = request.form.get("note", "").strip()
        for appointment in appointments:
            if appointment["id"] == appointment_id:
                appointment["notes"] = note
                appointment["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                appointment["updated_by"] = session.get("user_name", "Unknown")
                flash("Appointment note updated successfully.", "success")
                break
        else:
            flash("Appointment not found.", "error")
    except Exception as e:
        logging.error(f"Error updating appointment note: {e}")
        flash("Error updating appointment note.", "error")

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/appointment/<int:appointment_id>/assign_staff", methods=["POST"])
def assign_staff_to_appointment(appointment_id):
    """Assign staff member to appointment"""
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    try:
        staff_id = request.form.get("staff_id")
        for appointment in appointments:
            if appointment["id"] == appointment_id:
                appointment["staff_id"] = staff_id
                appointment["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                appointment["updated_by"] = session.get("user_name", "Unknown")

                # Get staff name for confirmation
                staff_name = "Unassigned"
                if staff_id:
                    for staff in staff_members:
                        if staff.id == int(staff_id):
                            staff_name = staff.name
                            break

                flash(f"Appointment assigned to {staff_name}.", "success")
                break
        else:
            flash("Appointment not found.", "error")
    except Exception as e:
        logging.error(f"Error assigning staff to appointment: {e}")
        flash("Error assigning staff to appointment.", "error")

    return redirect(url_for("admin_dashboard"))

@app.route('/api/send-spank-bucks', methods=['POST'])
def send_spank_bucks():
    """API endpoint to send SPANK Buck rewards"""
    try:
        data = request.get_json()
        
        email = data.get('email')
        amount = data.get('amount', 5)
        reason = data.get('reason', 'completing a course')
        name = data.get('name', 'Valued Customer')
        phone = data.get('phone')
        
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        # Send SMS notification only
        sms_sent = notification_service.send_spank_buck_reward(
            phone_number=phone,
            amount=amount,
            reason=reason,
            customer_name=name,
            email=email
        )
        
        # SMS already sent via send_spank_buck_reward above
        
        logging.info(f"SPANK Buck reward processed: ${amount} to {email} for {reason}")
        
        return jsonify({
            'success': sms_sent,
            'sms_sent': sms_sent,
            'message': f'${amount} SPANK Bucks sent to {phone or email}'
        })
        
    except Exception as e:
        logging.error(f"Error sending SPANK Bucks: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/complete-course', methods=['POST'])
def complete_course():
    """Handle course completion and send SPANK Buck reward"""
    try:
        data = request.get_json()
        
        email = data.get('email')
        phone = data.get('phone')
        course_name = data.get('course_name')
        student_name = data.get('student_name', 'Student')
        
        if not phone or not course_name:
            return jsonify({'success': False, 'error': 'Phone number and course name are required'}), 400
        
        # Send $5 SPANK Buck reward for course completion via SMS
        reward_sent = notification_service.send_spank_buck_reward(
            phone_number=phone,
            amount=5,
            reason=f'completing the "{course_name}" course at SPANK School',
            customer_name=student_name,
            email=email
        )
        
        logging.info(f"Course completion reward sent: {email} completed {course_name}")
        
        return jsonify({
            'success': True,
            'reward_sent': reward_sent,
            'message': f'Congratulations! $5 SPANK Bucks sent to {email}'
        })
        
    except Exception as e:
        logging.error(f"Error processing course completion: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/form-confirmation')
def form_confirmation():
    """Form confirmation page"""
    form_type = request.args.get('form_type', 'contact')
    customer_name = request.args.get('customer_name', '')
    customer_phone = request.args.get('customer_phone', '')
    customer_email = request.args.get('customer_email', '')
    service_type = request.args.get('service_type', '')
    confirmation_id = request.args.get('confirmation_id', '')
    
    return render_template('form_confirmation.html',
                         form_type=form_type,
                         customer_name=customer_name,
                         customer_phone=customer_phone,
                         customer_email=customer_email,
                         service_type=service_type,
                         confirmation_id=confirmation_id)

# Legacy Twilio routes removed - now using manual notification system

# Legacy Twilio testing routes removed - now using manual notification system

@app.route('/api/process-referral', methods=['POST'])
def process_referral():
    """Handle referral and send SPANK Buck reward"""
    try:
        data = request.get_json()
        
        referrer_email = data.get('referrer_email')
        referrer_phone = data.get('referrer_phone')
        referred_email = data.get('referred_email')
        referrer_name = data.get('referrer_name', 'Valued Customer')
        
        if not referrer_email or not referred_email:
            return jsonify({'success': False, 'error': 'Both emails are required'}), 400
        
        # Send $25 SPANK Buck reward for successful referral via SMS and email
        reward_sent = notification_service.send_spank_buck_reward(
            phone_number=referrer_phone,
            amount=25,
            reason=f'referring {referred_email} to SPANK services',
            customer_name=referrer_name,
            email=referrer_email
        )
        
        # Store referral record
        referral_data = {
            'referrer_code': referrer_email,
            'referred_email': referred_email,
            'status': 'completed',
            'reward_amount': 25
        }
        
        handyman_storage.add_referral(referral_data)
        
        logging.info(f"Referral reward sent: {referrer_email} referred {referred_email}")
        
        return jsonify({
            'success': True,
            'reward_sent': reward_sent,
            'message': f'$25 SPANK Bucks sent to {referrer_email} for successful referral'
        })
        
    except Exception as e:
        logging.error(f"Error processing referral: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/project-tracking')
def project_tracking():
    """Project timeline and tracking dashboard"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access project tracking.', 'error')
        return redirect(url_for('admin_login'))

    service_requests = handyman_storage.get_all_service_requests()
    
    # Organize projects by status
    active_projects = [req for req in service_requests if req.status in ['confirmed', 'in_progress']]
    pending_projects = [req for req in service_requests if req.status == 'pending']
    completed_projects = [req for req in service_requests if req.status == 'completed']
    
    # Calculate project metrics
    total_active_value = sum([
        float(req.budget_range.split('-')[0].replace('$', '').replace(',', '')) 
        if req.budget_range and '-' in req.budget_range 
        else 750.0 
        for req in active_projects
    ])
    
    # Timeline analysis
    hawaii_now = get_hawaii_time()
    upcoming_deadlines = []
    for project in active_projects:
        if project.preferred_date:
            project_date = datetime.strptime(project.preferred_date, '%Y-%m-%d')
            days_until = (project_date - hawaii_now.replace(tzinfo=None)).days
            if days_until <= 7:  # Projects due within a week
                upcoming_deadlines.append({
                    'project': project,
                    'days_until': days_until
                })
    
    return render_template('admin/project_tracking.html',
                         active_projects=active_projects,
                         pending_projects=pending_projects,
                         completed_projects=completed_projects,
                         total_active_value=total_active_value,
                         upcoming_deadlines=upcoming_deadlines)

# Additional imports for advanced features
try:
    from models import Contact, Job, Quote, Invoice
    from pdf_service import generate_quote_pdf, generate_invoice_pdf
    from upload_service import photo_service
    from analytics_service import analytics_service
    from performance_monitor import performance_monitor
    from business_intelligence import business_intelligence
    from ml_analytics import ml_analytics
except ImportError as e:
    logging.warning(f"Advanced feature import failed: {e}")
    # Continue with basic functionality

@app.route('/admin/business-intelligence')
def business_intelligence_dashboard():
    """Comprehensive business intelligence and strategic insights"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access business intelligence.', 'error')
        return redirect(url_for('admin_login'))

    from business_intelligence import business_intelligence
    from ml_analytics import ml_analytics
    
    # Generate comprehensive business intelligence
    executive_briefing = business_intelligence.generate_executive_briefing(handyman_storage)
    market_insights = business_intelligence.generate_market_insights(handyman_storage)
    strategic_recommendations = business_intelligence.generate_strategic_recommendations(handyman_storage)
    roi_projections = business_intelligence.calculate_roi_projections(handyman_storage, strategic_recommendations)
    
    # Generate ML-powered insights
    ml_insights = ml_analytics.generate_ml_insights(handyman_storage)
    
    return render_template('admin/business_intelligence.html',
                         executive_briefing=executive_briefing,
                         market_insights=market_insights,
                         strategic_recommendations=strategic_recommendations,
                         roi_projections=roi_projections,
                         ml_insights=ml_insights)

@app.route('/admin/ml-insights')
def ml_insights_dashboard():
    """Machine Learning powered business insights and predictions"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access ML insights.', 'error')
        return redirect(url_for('admin_login'))

    from analytics_manager import analytics_manager
    
    try:
        # Get business insights through centralized manager
        business_insights = analytics_manager.get_business_insights(handyman_storage)
        
        # Get comprehensive analytics for additional context
        analytics_data = analytics_manager.get_comprehensive_analytics(handyman_storage)
        
        return render_template('admin/ml_insights.html',
                             ml_insights=analytics_data['ml_insights'],
                             business_insights=business_insights,
                             confidence_level=business_insights.get('confidence_level', 'Developing'))
                             
    except Exception as e:
        logging.error(f"Error in ML insights: {e}")
        flash('ML insights temporarily unavailable. Please try again.', 'warning')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/performance-monitor')
def performance_monitor_dashboard():
    """Real-time performance monitoring and automated alerts"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access performance monitoring.', 'error')
        return redirect(url_for('admin_login'))

    from analytics_manager import analytics_manager
    
    try:
        # Get real-time performance data through centralized manager
        real_time_metrics = analytics_manager.get_real_time_metrics(handyman_storage)
        performance_alerts = analytics_manager.get_performance_alerts(handyman_storage)
        
        # Get cache status for system monitoring
        cache_status = analytics_manager.get_cache_status()
        
        return render_template('admin/performance_monitor.html',
                             real_time_metrics=real_time_metrics,
                             performance_alerts=performance_alerts,
                             cache_status=cache_status,
                             system_health=real_time_metrics.get('health_score', {}))
                             
    except Exception as e:
        logging.error(f"Error in performance monitoring: {e}")
        flash('Performance monitoring temporarily unavailable. Please try again.', 'warning')
        return redirect(url_for('admin_dashboard'))

# Analytics API Endpoints
@app.route('/api/analytics/comprehensive')
def api_comprehensive_analytics():
    """API endpoint for comprehensive analytics data"""
    try:
        from analytics_manager import analytics_manager
        analytics_data = analytics_manager.get_comprehensive_analytics(storage_service)
        return jsonify(analytics_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/real-time')
def api_real_time_metrics():
    """API endpoint for real-time metrics"""
    try:
        from analytics_manager import analytics_manager
        metrics = analytics_manager.get_real_time_metrics(storage_service)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/alerts')
def api_performance_alerts():
    """API endpoint for performance alerts"""
    try:
        from analytics_manager import analytics_manager
        alerts = analytics_manager.get_performance_alerts(storage_service)
        return jsonify(alerts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/executive-summary')
def api_executive_summary():
    """API endpoint for executive summary"""
    try:
        from analytics_manager import analytics_manager
        summary = analytics_manager.get_executive_summary(storage_service)
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workflow/advance/<int:quote_id>/<string:stage>', methods=['POST'])
def api_advance_workflow(quote_id, stage):
    """API endpoint to advance workflow stage"""
    try:
        from workflow_automation_service import WorkflowAutomationService
        workflow_service = WorkflowAutomationService()
        
        result = workflow_service.advance_workflow_stage(quote_id, stage, manual=True)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/workflow/analytics')
def api_workflow_analytics():
    """API endpoint for workflow analytics"""
    try:
        from workflow_automation_service import WorkflowAutomationService
        workflow_service = WorkflowAutomationService()
        
        analytics = workflow_service.get_workflow_analytics()
        return jsonify(analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workflow/process-actions', methods=['POST'])
def api_process_workflow_actions():
    """API endpoint to process pending automated actions"""
    try:
        from workflow_automation_service import WorkflowAutomationService
        workflow_service = WorkflowAutomationService()
        
        results = workflow_service.process_automated_actions()
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customer-engagement/track', methods=['POST'])
def api_track_customer_interaction():
    """API endpoint to track customer interactions"""
    try:
        from customer_engagement_service import CustomerEngagementService
        engagement_service = CustomerEngagementService()
        
        data = request.get_json()
        contact_id = data.get('contact_id')
        interaction_type = data.get('interaction_type')
        details = data.get('details', '')
        
        if not contact_id or not interaction_type:
            return jsonify({'error': 'contact_id and interaction_type required'}), 400
        
        result = engagement_service.track_customer_interaction(contact_id, interaction_type, details)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customer-engagement/analytics')
def api_customer_engagement_analytics():
    """API endpoint for customer engagement analytics"""
    try:
        from customer_engagement_service import CustomerEngagementService
        engagement_service = CustomerEngagementService()
        
        analytics = engagement_service.get_engagement_analytics()
        return jsonify(analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customer-engagement/customers-for-engagement')
def api_customers_for_engagement():
    """API endpoint to get customers needing engagement"""
    try:
        from customer_engagement_service import CustomerEngagementService
        engagement_service = CustomerEngagementService()
        
        engagement_type = request.args.get('type', 'all')
        customers = engagement_service.get_customers_for_engagement(engagement_type)
        return jsonify({'customers': customers, 'count': len(customers)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customer-engagement/generate-campaign', methods=['POST'])
def api_generate_engagement_campaign():
    """API endpoint to generate engagement campaign"""
    try:
        from customer_engagement_service import CustomerEngagementService
        engagement_service = CustomerEngagementService()
        
        data = request.get_json()
        target_audience = data.get('target_audience', 'all')
        
        campaign = engagement_service.generate_engagement_campaign(target_audience)
        return jsonify(campaign)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/cache/clear', methods=['POST'])
def api_clear_analytics_cache():
    """API endpoint to clear analytics cache"""
    try:
        from analytics_manager import analytics_manager
        analytics_manager.clear_cache()
        return jsonify({'success': True, 'message': 'Analytics cache cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/client/<client_id>/<job_id>/update', methods=['POST'])
def update_client_info(client_id, job_id):
    """Update client information in the database"""
    if not session.get('portal_authenticated'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Only allow staff to update client information
    if session.get('access_level') != 'staff':
        return jsonify({'error': 'Staff access required'}), 403
    
    try:
        data = request.get_json()
        
        # Update client in auth_service
        success = auth_service.update_client(client_id, job_id, {
            'name': data.get('name'),
            'phone': data.get('phone'),
            'email': data.get('email'),
            'address': data.get('address')
        })
        
        if success:
            # Also update in CRM system if contact exists
            try:
                # Find existing contact in CRM by multiple criteria
                contacts = handyman_storage.get_all_contacts()
                contact_to_update = None
                
                # Normalize phone number for comparison
                def normalize_phone(phone):
                    if not phone:
                        return ""
                    return ''.join(filter(str.isdigit, str(phone)))
                
                new_phone_normalized = normalize_phone(data.get('phone'))
                new_email = data.get('email', '').lower().strip()
                new_name = data.get('name', '').lower().strip()
                
                logging.info(f"Searching for existing contact: phone={new_phone_normalized}, email={new_email}, name={new_name}")
                
                for contact in contacts:
                    contact_phone_normalized = normalize_phone(contact.phone)
                    contact_email = (contact.email or '').lower().strip()
                    contact_name = (contact.name or '').lower().strip()
                    
                    # Check for matches by phone, email, or exact name
                    if (new_phone_normalized and contact_phone_normalized and new_phone_normalized == contact_phone_normalized) or \
                       (new_email and contact_email and new_email == contact_email) or \
                       (new_name and contact_name and new_name == contact_name):
                        contact_to_update = contact
                        logging.info(f"Found matching contact: {contact.id} - {contact.name}")
                        break
                
                # Check for portal sync tags to find previously synced contacts
                if not contact_to_update:
                    for contact in contacts:
                        if (hasattr(contact, 'tags') and contact.tags and 'portal_sync' in contact.tags) or \
                           (hasattr(contact, 'notes') and contact.notes and f'portal client {client_id}/{job_id}' in contact.notes):
                            contact_to_update = contact
                            logging.info(f"Found portal-synced contact: {contact.id} - {contact.name}")
                            break
                
                # If contact exists in CRM, update it
                if contact_to_update:
                    handyman_storage.update_contact(contact_to_update.id, {
                        'name': data.get('name'),
                        'phone': data.get('phone'),
                        'email': data.get('email'),
                        'address': data.get('address')
                    })
                    logging.info(f"Updated existing CRM contact {contact_to_update.id}: {data.get('name')}")
                    
                    # Update any related quotes, invoices, and jobs with new contact info
                    try:
                        # Update quotes
                        quotes = handyman_storage.get_quotes_by_contact(contact_to_update.id)
                        for quote in quotes:
                            if hasattr(quote, 'contact_name'):
                                quote.contact_name = data.get('name')
                        
                        # Update invoices  
                        invoices = handyman_storage.get_invoices_by_contact(contact_to_update.id)
                        for invoice in invoices:
                            if hasattr(invoice, 'contact_name'):
                                invoice.contact_name = data.get('name')
                        
                        # Update jobs
                        jobs = handyman_storage.get_jobs_by_contact(contact_to_update.id)
                        for job in jobs:
                            if hasattr(job, 'contact_name'):
                                job.contact_name = data.get('name')
                                
                        logging.info(f"Updated related records for contact {contact_to_update.id}")
                    except Exception as e:
                        logging.warning(f"Could not update related records: {e}")
                        
                else:
                    # Create new contact in CRM if it doesn't exist
                    contact_data = {
                        'name': data.get('name'),
                        'email': data.get('email'),
                        'phone': data.get('phone'),
                        'address': data.get('address'),
                        'notes': f'Auto-synced from portal client {client_id}/{job_id}',
                        'tags': ['portal_sync', 'auto_created']
                    }
                    new_contact = handyman_storage.add_contact(contact_data)
                    logging.info(f"Created new CRM contact {new_contact.id}: {data.get('name')}")
                    
            except Exception as e:
                logging.warning(f"Could not sync client update to CRM: {e}")
                # Don't fail the update if CRM sync fails
            
            return jsonify({'success': True, 'message': 'Client information updated successfully'})
        else:
            return jsonify({'error': 'Client not found'}), 404
            
    except Exception as e:
        logging.error(f"Error updating client info: {e}")
        return jsonify({'error': 'Failed to update client information'}), 500

@app.route('/api/client/<client_id>/<job_id>/info')
def get_client_info(client_id, job_id):
    """Get current client information"""
    if not session.get('portal_authenticated'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Allow access if:
    # 1. User is authenticated for this specific client/job combination, OR
    # 2. User has staff access level (can view any client info)
    user_client_id = session.get('client_id')
    user_job_id = session.get('job_id')
    access_level = session.get('access_level')
    
    if not ((user_client_id == client_id and user_job_id == job_id) or access_level == 'staff'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get fresh client data from auth_service
        client_data = auth_service.find_client(client_id, job_id)
        
        if client_data:
            return jsonify({
                'success': True,
                'client': client_data,
                'message': 'Client information retrieved successfully'
            })
        else:
            return jsonify({'error': 'Client not found'}), 404
            
    except Exception as e:
        logging.error(f"Error getting client info: {e}")
        return jsonify({'error': 'Failed to retrieve client information'}), 500

@app.route('/admin/integrated-analytics')
def integrated_analytics():
    """Comprehensive integrated analytics dashboard"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access integrated analytics.', 'error')
        return redirect(url_for('admin_login'))

    from analytics_manager import analytics_manager
    
    try:
        # Get comprehensive analytics through centralized manager
        analytics_data = analytics_manager.get_comprehensive_analytics(handyman_storage)
        
        # Get real-time performance data
        real_time_metrics = analytics_manager.get_real_time_metrics(handyman_storage)
        
        # Get executive summary for quick overview
        executive_summary = analytics_manager.get_executive_summary(handyman_storage)
        
        return render_template('admin/integrated_analytics.html',
                             business_report=analytics_data['business_report'],
                             executive_briefing=analytics_data['executive_briefing'],
                             ml_insights=analytics_data['ml_insights'],
                             performance_data=analytics_data['performance_data'],
                             daily_insights=analytics_data['daily_insights'],
                             real_time_metrics=real_time_metrics,
                             executive_summary=executive_summary,
                             system_status=analytics_data['system_status'])
                             
    except Exception as e:
        logging.error(f"Error in integrated analytics: {e}")
        flash('Analytics temporarily unavailable. Please try again.', 'warning')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/executive-summary')
def executive_summary():
    """Executive dashboard with key business metrics"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access executive summary.', 'error')
        return redirect(url_for('admin_login'))

    from analytics_manager import analytics_manager
    
    try:
        # Get executive summary through centralized manager
        executive_data = analytics_manager.get_executive_summary(handyman_storage)
        
        # Get real-time metrics for current status
        real_time_metrics = analytics_manager.get_real_time_metrics(handyman_storage)
        
        # Get performance alerts
        performance_alerts = analytics_manager.get_performance_alerts(handyman_storage)
        
        return render_template('admin/executive_summary.html',
                             executive_metrics=executive_data['key_metrics'],
                             business_status=executive_data['business_status'],
                             health_score=executive_data['health_score'],
                             top_priorities=executive_data['top_priorities'],
                             growth_outlook=executive_data['growth_outlook'],
                             recommendations=executive_data['recommendations'],
                             real_time_metrics=real_time_metrics,
                             performance_alerts=performance_alerts['alerts'][:3])
                             
    except Exception as e:
        logging.error(f"Error in executive summary: {e}")
        flash('Executive summary temporarily unavailable. Please try again.', 'warning')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/analytics-dashboard')
def analytics_dashboard():
    """Enhanced business analytics with comprehensive CRM insights"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access analytics.', 'error')
        return redirect(url_for('admin_login'))

    from analytics_manager import analytics_manager
    
    # Get comprehensive analytics through centralized manager
    analytics_data = analytics_manager.get_comprehensive_analytics(handyman_storage)
    real_time_metrics = analytics_manager.get_real_time_metrics(handyman_storage)
    performance_alerts = analytics_manager.get_performance_alerts(handyman_storage)
    
    return render_template('admin/enhanced_analytics.html',
                         business_report=analytics_data['business_report'],
                         performance_alerts=performance_alerts['alerts'],
                         cash_flow_forecast=analytics_data['business_report']['revenue'],
                         predictive_insights=analytics_data['ml_insights'],
                         real_time_metrics=real_time_metrics)

@app.route('/admin/customer-feedback')
def customer_feedback():
    """Customer satisfaction and feedback management"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access customer feedback.', 'error')
        return redirect(url_for('admin_login'))

    service_requests = handyman_storage.get_all_service_requests()
    contact_messages = handyman_storage.get_all_contact_messages()
    
    # Recently completed jobs needing follow-up
    hawaii_now = get_hawaii_time()
    recent_completions = []
    follow_up_needed = []
    
    for request in service_requests:
        if request.status == 'completed' and request.preferred_date:
            completion_date = datetime.strptime(request.preferred_date, '%Y-%m-%d')
            days_since = (hawaii_now.replace(tzinfo=None) - completion_date).days
            
            if days_since <= 7:  # Completed within last week
                recent_completions.append({
                    'request': request,
                    'days_since': days_since
                })
            elif 7 < days_since <= 30:  # Needs satisfaction follow-up
                follow_up_needed.append({
                    'request': request,
                    'days_since': days_since
                })

    # Customer communication priorities
    urgent_messages = [msg for msg in contact_messages if msg.status == 'unread' and 
                      hasattr(msg, 'priority_score') and msg.priority_score >= 7]
    
    # Calculate satisfaction metrics
    total_completed = len([req for req in service_requests if req.status == 'completed'])
    
    return render_template('admin/customer_feedback.html',
                         recent_completions=recent_completions,
                         follow_up_needed=follow_up_needed,
                         urgent_messages=urgent_messages,
                         total_completed=total_completed,
                         contact_messages=contact_messages)

@app.route('/admin/send-followup/<int:request_id>', methods=['POST'])
def send_followup(request_id):
    """Send automated follow-up message to customer"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        service_requests = handyman_storage.get_all_service_requests()
        request_obj = next((req for req in service_requests if req.id == request_id), None)
        
        if not request_obj:
            flash('Service request not found.', 'error')
            return redirect(url_for('customer_feedback'))
        
        # Send follow-up notification
        follow_up_message = f"""
        Thank you for choosing SPANKKS Construction for your {request_obj.service} project!
        
        We hope you're satisfied with our work. Your feedback helps us improve our services.
        
        As a token of appreciation, here's $5 SPANK Bucks for completing our quick satisfaction survey!
        
        Rate your experience: [Survey Link]
        
        Need additional work? Contact us for a 10% returning customer discount!
        
        Best regards,
        SPANKKS Construction Team
        """
        
        # Send via notification service
        notification_service.send_inquiry_alert(
            'Follow-up', 
            request_obj.name, 
            request_obj.phone, 
            request_obj.email, 
            f"Satisfaction follow-up for {request_obj.service}"
        )
        
        # Send SPANK Buck reward
        notification_service.send_spank_buck_reward(
            request_obj.phone, 
            5, 
            "Customer satisfaction survey completion", 
            request_obj.name, 
            request_obj.email
        )
        
        flash(f'Follow-up sent to {request_obj.name} with $5 SPANK Buck reward!', 'success')
        
    except Exception as e:
        logging.error(f"Error sending follow-up: {e}")
        flash('Error sending follow-up message.', 'error')
    
    return redirect(url_for('customer_feedback'))

@app.route('/admin/bulk-communications')
def bulk_communications():
    """Bulk customer communication management"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access bulk communications.', 'error')
        return redirect(url_for('admin_login'))

    service_requests = handyman_storage.get_all_service_requests()
    memberships = handyman_storage.get_all_memberships()
    referrals = handyman_storage.get_all_referrals()
    
    # Segment customers for targeted campaigns
    recent_customers = [req for req in service_requests if req.status == 'completed']
    pending_customers = [req for req in service_requests if req.status == 'pending']
    repeat_customers = []  # Would track based on email matching
    
    # SPANK Buck campaigns
    seasonal_promotions = [
        {
            'name': 'Summer Home Prep',
            'description': 'Get ready for summer with deck repairs and outdoor projects',
            'reward': 15,
            'target': 'recent_customers'
        },
        {
            'name': 'Holiday Home Safety',
            'description': 'Electrical safety checks and holiday lighting installation',
            'reward': 20,
            'target': 'all_customers'
        },
        {
            'name': 'Spring Cleaning Specials',
            'description': 'Pressure washing, fence maintenance, and exterior touch-ups',
            'reward': 10,
            'target': 'members'
        }
    ]
    
    return render_template('admin/bulk_communications.html',
                         recent_customers=recent_customers,
                         pending_customers=pending_customers,
                         repeat_customers=repeat_customers,
                         seasonal_promotions=seasonal_promotions,
                         memberships=memberships,
                         referrals=referrals)

# CRM Routes
@app.route('/admin/crm')
def crm_dashboard():
    """CRM Dashboard with contacts, quotes, invoices, and jobs"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Ensure storage is available
    global handyman_storage
    if handyman_storage is None:
        from models import HandymanStorage
        handyman_storage = HandymanStorage()
    
    contacts = handyman_storage.get_all_contacts()
    quotes = handyman_storage.get_all_quotes()
    invoices = handyman_storage.get_all_invoices()
    jobs = handyman_storage.get_all_jobs()
    
    # CRM metrics
    total_revenue = sum(i.total_amount for i in invoices if i.status == 'paid')
    pending_invoices = sum(i.total_amount for i in invoices if i.status == 'pending')
    active_jobs = len([j for j in jobs if j.status in ['scheduled', 'in_progress']])
    pending_quotes = len([q for q in quotes if q.status == 'pending'])
    
    return render_template('admin/crm_dashboard.html',
                         contacts=contacts,
                         quotes=quotes,
                         invoices=invoices,
                         jobs=jobs,
                         total_revenue=total_revenue,
                         pending_invoices=pending_invoices,
                         active_jobs=active_jobs,
                         pending_quotes=pending_quotes)

@app.route('/admin/crm/contacts')
def contact_list():
    """Contact database management"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    contacts = handyman_storage.get_all_contacts()
    return render_template('admin/contacts.html', contacts=contacts)

@app.route('/admin/crm/contacts/add', methods=['GET', 'POST'])
def add_contact():
    """Add new contact"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        contact_data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'phone': phone_formatter.format_phone(request.form['phone']),
            'address': request.form.get('address', ''),
            'notes': request.form.get('notes', ''),
            'tags': request.form.get('tags', '').split(',') if request.form.get('tags') else []
        }
        handyman_storage.add_contact(contact_data)
        flash('Contact added successfully!', 'success')
        return redirect(url_for('contact_list'))
    
    return render_template('admin/add_contact.html')

@app.route('/admin/crm/contacts/<int:contact_id>')
def contact_detail(contact_id):
    """Contact detail view with job history"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    contact = handyman_storage.get_contact_by_id(contact_id)
    if not contact:
        flash('Contact not found.', 'error')
        return redirect(url_for('contact_list'))
    
    quotes = handyman_storage.get_quotes_by_contact(contact_id)
    invoices = handyman_storage.get_invoices_by_contact(contact_id)
    jobs = handyman_storage.get_jobs_by_contact(contact_id)
    
    return render_template('admin/contact_detail.html',
                         contact=contact,
                         quotes=quotes,
                         invoices=invoices,
                         jobs=jobs)

@app.route('/admin/crm/quotes')
def quote_list():
    """Quote management"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    quotes = handyman_storage.get_all_quotes()
    contacts = handyman_storage.get_all_contacts()
    
    return render_template('admin/quotes.html', quotes=quotes, contacts=contacts)

@app.route('/admin/crm/quotes/builder')
def quote_builder():
    """Interactive quote builder"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    contacts = handyman_storage.get_all_contacts()
    
    # Service templates for quick quote building
    service_templates = {
        'drywall': [
            {'description': 'Small patch (under 12")', 'unit_price': 155, 'unit': 'patch'},
            {'description': 'Medium patch (12"-24")', 'unit_price': 275, 'unit': 'patch'},
            {'description': 'Large patch (24"+)', 'unit_price': 425, 'unit': 'patch'},
            {'description': 'Texture matching', 'unit_price': 125, 'unit': 'sq ft'},
            {'description': 'Prime and paint', 'unit_price': 85, 'unit': 'sq ft'}
        ],
        'flooring': [
            {'description': 'Vinyl plank installation', 'unit_price': 4.50, 'unit': 'sq ft'},
            {'description': 'Tile installation', 'unit_price': 6.75, 'unit': 'sq ft'},
            {'description': 'Hardwood installation', 'unit_price': 8.25, 'unit': 'sq ft'},
            {'description': 'Subfloor repair', 'unit_price': 125, 'unit': 'sq ft'},
            {'description': 'Transition strips', 'unit_price': 35, 'unit': 'linear ft'}
        ],
        'fencing': [
            {'description': 'Wood fence installation', 'unit_price': 45, 'unit': 'linear ft'},
            {'description': 'Vinyl fence installation', 'unit_price': 55, 'unit': 'linear ft'},
            {'description': 'Chain link fence', 'unit_price': 35, 'unit': 'linear ft'},
            {'description': 'Gate installation', 'unit_price': 325, 'unit': 'each'},
            {'description': 'Post replacement', 'unit_price': 85, 'unit': 'each'}
        ],
        'general': [
            {'description': 'General repair (per hour)', 'unit_price': 95, 'unit': 'hour'},
            {'description': 'Emergency service', 'unit_price': 125, 'unit': 'hour'},
            {'description': 'Material markup', 'unit_price': 0.15, 'unit': 'percentage'},
            {'description': 'Travel charge', 'unit_price': 45, 'unit': 'trip'},
            {'description': 'Disposal fee', 'unit_price': 65, 'unit': 'load'}
        ]
    }
    
    return render_template('admin/quote_builder.html', 
                         contacts=contacts, 
                         service_templates=service_templates)

@app.route('/admin/crm/quotes/create', methods=['POST'])
def create_quote():
    """Create new quote from builder"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    from models import QuoteItem
    
    # Parse quote items from form
    items = []
    item_count = int(request.form.get('item_count', 0))
    
    for i in range(item_count):
        if request.form.get(f'item_{i}_description'):
            item = QuoteItem(
                description=request.form[f'item_{i}_description'],
                quantity=float(request.form[f'item_{i}_quantity']),
                unit_price=float(request.form[f'item_{i}_unit_price']),
                unit=request.form[f'item_{i}_unit']
            )
            items.append(item)
    
    total_amount = sum(item.total for item in items)
    
    quote_data = {
        'contact_id': int(request.form['contact_id']),
        'service_type': request.form['service_type'],
        'items': items,
        'total_amount': total_amount,
        'valid_until': request.form['valid_until'],
        'notes': request.form.get('notes', '')
    }
    
    quote = handyman_storage.add_quote(quote_data)
    flash('Quote created successfully!', 'success')
    return redirect(url_for('quote_detail', quote_id=quote.id))

@app.route('/admin/crm/quotes/<int:quote_id>')
def quote_detail(quote_id):
    """Quote detail view"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    quotes = handyman_storage.get_all_quotes()
    quote = next((q for q in quotes if q.id == quote_id), None)
    
    if not quote:
        flash('Quote not found.', 'error')
        return redirect(url_for('quote_list'))
    
    contact = handyman_storage.get_contact_by_id(quote.contact_id)
    
    return render_template('admin/quote_detail.html', quote=quote, contact=contact)

@app.route('/admin/crm/invoices')
def invoice_list():
    """Invoice management"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    invoices = handyman_storage.get_all_invoices()
    contacts = handyman_storage.get_all_contacts()
    
    return render_template('admin/invoices.html', invoices=invoices, contacts=contacts)

@app.route('/admin/crm/invoices/create/<int:quote_id>')
def create_invoice_from_quote(quote_id):
    """Create invoice from accepted quote"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    quotes = handyman_storage.get_all_quotes()
    quote = next((q for q in quotes if q.id == quote_id), None)
    
    if not quote:
        flash('Quote not found.', 'error')
        return redirect(url_for('quote_list'))
    
    invoice_data = {
        'contact_id': quote.contact_id,
        'quote_id': quote.id,
        'items': quote.items,
        'subtotal': quote.total_amount
    }
    
    invoice = handyman_storage.add_invoice(invoice_data)
    handyman_storage.update_quote_status(quote_id, 'accepted')
    
    flash('Invoice created from quote successfully!', 'success')
    return redirect(url_for('invoice_detail', invoice_id=invoice.id))

@app.route('/admin/crm/invoices/<int:invoice_id>')
def invoice_detail(invoice_id):
    """Invoice detail view"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    invoices = handyman_storage.get_all_invoices()
    invoice = next((i for i in invoices if i.id == invoice_id), None)
    
    if not invoice:
        flash('Invoice not found.', 'error')
        return redirect(url_for('invoice_list'))
    
    contact = handyman_storage.get_contact_by_id(invoice.contact_id)
    
    return render_template('admin/invoice_detail.html', invoice=invoice, contact=contact)

@app.route('/admin/crm/schedule')
def job_schedule():
    """Job scheduling calendar"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    jobs = handyman_storage.get_all_jobs()
    contacts = handyman_storage.get_all_contacts()
    
    # Organize jobs by date for calendar view
    jobs_by_date = {}
    for job in jobs:
        date = job.scheduled_date
        if date not in jobs_by_date:
            jobs_by_date[date] = []
        jobs_by_date[date].append(job)
    
    return render_template('admin/schedule.html', 
                         jobs=jobs, 
                         contacts=contacts, 
                         jobs_by_date=jobs_by_date)

@app.route('/admin/crm/jobs/create', methods=['GET', 'POST'])
def create_job():
    """Create new job"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        job_data = {
            'contact_id': int(request.form['contact_id']),
            'quote_id': int(request.form['quote_id']) if request.form.get('quote_id') else None,
            'scheduled_date': request.form['scheduled_date'],
            'crew_members': request.form.get('crew_members', '').split(',') if request.form.get('crew_members') else [],
            'notes': request.form.get('notes', '')
        }
        
        job = handyman_storage.add_job(job_data)
        flash('Job created successfully!', 'success')
        return redirect(url_for('job_detail', job_id=job.id))
    
    contacts = handyman_storage.get_all_contacts()
    quotes = handyman_storage.get_all_quotes()
    
    return render_template('admin/create_job.html', contacts=contacts, quotes=quotes)

@app.route('/admin/crm/jobs/<int:job_id>')
def job_detail(job_id):
    """Job detail view with mobile crew access"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    jobs = handyman_storage.get_all_jobs()
    job = next((j for j in jobs if j.id == job_id), None)
    
    if not job:
        flash('Job not found.', 'error')
        return redirect(url_for('job_schedule'))
    
    contact = handyman_storage.get_contact_by_id(job.contact_id)
    
    return render_template('admin/job_detail.html', job=job, contact=contact)

@app.route('/admin/crm/jobs/<int:job_id>/update_status', methods=['POST'])
def update_job_status(job_id):
    """Update job status"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    status = request.form['status']
    handyman_storage.update_job_status(job_id, status)
    
    flash(f'Job status updated to {status}!', 'success')
    return redirect(url_for('job_detail', job_id=job_id))

@app.route('/admin/crm/jobs/<int:job_id>/add_note', methods=['POST'])
def add_job_note_route(job_id):
    """Add note to job"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    note = request.form['note']
    handyman_storage.add_job_note(job_id, note)
    
    flash('Note added successfully!', 'success')
    return redirect(url_for('job_detail', job_id=job_id))

# PDF Generation Routes
@app.route('/admin/crm/quotes/<int:quote_id>/pdf')
def download_quote_pdf(quote_id):
    """Generate and download quote PDF"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        from pdf_service import generate_quote_pdf
        
        quotes = handyman_storage.get_all_quotes()
        quote = next((q for q in quotes if q.id == quote_id), None)
        
        if not quote:
            flash('Quote not found.', 'error')
            return redirect(url_for('quote_list'))
        
        contact = handyman_storage.get_contact_by_id(quote.contact_id)
        if not contact:
            flash('Contact information not found.', 'error')
            return redirect(url_for('quote_list'))
        
        # Generate PDF
        filename = generate_quote_pdf(quote, contact)
        
        # Update quote with PDF path
        quote.pdf_path = f"static/pdfs/{filename}"
        
        # Send file to user
        from flask import send_file
        return send_file(f"static/pdfs/{filename}", as_attachment=True, download_name=filename)
        
    except Exception as e:
        logging.error(f"Error generating quote PDF: {e}")
        flash('Error generating PDF. Please try again.', 'error')
        return redirect(url_for('quote_detail', quote_id=quote_id))

@app.route('/admin/crm/invoices/<int:invoice_id>/pdf')
def download_invoice_pdf(invoice_id):
    """Generate and download invoice PDF"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        from pdf_service import generate_invoice_pdf
        
        invoices = handyman_storage.get_all_invoices()
        invoice = next((i for i in invoices if i.id == invoice_id), None)
        
        if not invoice:
            flash('Invoice not found.', 'error')
            return redirect(url_for('invoice_list'))
        
        contact = handyman_storage.get_contact_by_id(invoice.contact_id)
        if not contact:
            flash('Contact information not found.', 'error')
            return redirect(url_for('invoice_list'))
        
        # Generate PDF
        filename = generate_invoice_pdf(invoice, contact)
        
        # Update invoice with PDF path
        invoice.pdf_path = f"static/pdfs/{filename}"
        
        # Send file to user
        from flask import send_file
        return send_file(f"static/pdfs/{filename}", as_attachment=True, download_name=filename)
        
    except Exception as e:
        logging.error(f"Error generating invoice PDF: {e}")
        flash('Error generating PDF. Please try again.', 'error')
        return redirect(url_for('invoice_detail', invoice_id=invoice_id))

@app.route('/admin/crm/quotes/<int:quote_id>/email')
def email_quote_pdf(quote_id):
    """Email quote PDF to customer"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        from pdf_service import generate_quote_pdf
        
        quotes = handyman_storage.get_all_quotes()
        quote = next((q for q in quotes if q.id == quote_id), None)
        
        if not quote:
            flash('Quote not found.', 'error')
            return redirect(url_for('quote_list'))
        
        contact = handyman_storage.get_contact_by_id(quote.contact_id)
        if not contact:
            flash('Contact information not found.', 'error')
            return redirect(url_for('quote_list'))
        
        # Generate PDF
        filename = generate_quote_pdf(quote, contact)
        
        # Send quote via notification service
        notification_service.send_inquiry_alert(
            'Quote Delivery',
            contact.name,
            contact.phone,
            contact.email,
            f"Professional quote Q{quote.id:04d} for {quote.service_type} services - ${quote.total_amount:.2f}"
        )
        
        flash(f'Quote emailed to {contact.name} at {contact.email}!', 'success')
        return redirect(url_for('quote_detail', quote_id=quote_id))
        
    except Exception as e:
        logging.error(f"Error emailing quote: {e}")
        flash('Error sending quote email. Please try again.', 'error')
        return redirect(url_for('quote_detail', quote_id=quote_id))

@app.route('/admin/crm/invoices/<int:invoice_id>/email')
def email_invoice_pdf(invoice_id):
    """Email invoice PDF to customer"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        from pdf_service import generate_invoice_pdf
        
        invoices = handyman_storage.get_all_invoices()
        invoice = next((i for i in invoices if i.id == invoice_id), None)
        
        if not invoice:
            flash('Invoice not found.', 'error')
            return redirect(url_for('invoice_list'))
        
        contact = handyman_storage.get_contact_by_id(invoice.contact_id)
        if not contact:
            flash('Contact information not found.', 'error')
            return redirect(url_for('invoice_list'))
        
        # Generate PDF
        filename = generate_invoice_pdf(invoice, contact)
        
        # Send invoice via notification service
        notification_service.send_inquiry_alert(
            'Invoice Delivery',
            contact.name,
            contact.phone,
            contact.email,
            f"Invoice INV{invoice.id:04d} - Amount Due: ${invoice.total_amount:.2f} - Due: {invoice.due_date}"
        )
        
        flash(f'Invoice emailed to {contact.name} at {contact.email}!', 'success')
        return redirect(url_for('invoice_detail', invoice_id=invoice_id))
        
    except Exception as e:
        logging.error(f"Error emailing invoice: {e}")
        flash('Error sending invoice email. Please try again.', 'error')
        return redirect(url_for('invoice_detail', invoice_id=invoice_id))

@app.route('/api/generate-quote', methods=['POST'])
def generate_quote_api():
    """API endpoint for generating quotes - compatible with external integrations"""
    try:
        # Parse request data
        data = request.get_json() if request.is_json else request.form
        
        client_id = data.get('clientId')
        job_id = data.get('jobId')
        customer = data.get('customer')
        phone = phone_formatter.format_phone(data.get('phone') or data.get('customer_phone'))
        service_type = data.get('serviceType', '')
        price = float(data.get('price', 0))
        
        # Check if this is a multi-line quote with items array
        has_items = 'items' in data and isinstance(data['items'], list) and len(data['items']) > 0
        
        # Validate required fields based on quote type
        if has_items:
            # Multi-line quote validation
            if not all([customer, phone]):
                return jsonify({'error': 'Missing required fields: customer and phone'}), 400
        else:
            # Legacy single-item quote validation
            if not all([customer, phone, service_type, price]):
                return jsonify({'error': 'Missing required fields: customer, phone, serviceType, price'}), 400
        
        # Check if contact exists or create new one
        contacts = handyman_storage.get_all_contacts()
        contact = next((c for c in contacts if c.phone == phone), None)
        
        if not contact:
            # Create new contact
            # Generate safe email from customer name
            safe_email = 'customer'
            if customer and isinstance(customer, str):
                safe_email = customer.lower().replace(' ', '.')
            contact_data = {
                'name': customer,
                'email': f"{safe_email}@tempmail.com",  # Temporary email
                'phone': phone,
                'address': '',
                'notes': f'Created via API for job {job_id}' if job_id else 'Created via API',
                'tags': ['api_generated']
            }
            contact = handyman_storage.add_contact(contact_data)
        
        # Handle multi-line quote items from req.body.items[] array
        from models import QuoteItem
        quote_items = []
        
        if 'items' in data and isinstance(data['items'], list) and len(data['items']) > 0:
            # Multi-line quote with itemized descriptions
            total_amount = 0
            for item in data['items']:
                if isinstance(item, dict):
                    item_obj = QuoteItem(
                        description=item.get('description', 'Service Item'),
                        quantity=float(item.get('quantity', 1)),
                        unit_price=float(item.get('unit_price', 0)),
                        unit="each"
                    )
                    quote_items.append(item_obj)
                    total_amount += item.get('line_total', item_obj.quantity * item_obj.unit_price)
            
            # Use calculated total from items or fallback to provided total
            price = data.get('total', total_amount) if total_amount > 0 else float(data.get('price', 0))
        else:
            # Legacy single-item quote for backward compatibility
            service_lower = service_type.lower() if service_type else 'general'
            
            if service_lower in ['drywall', 'drywall repair']:
                quote_items = [QuoteItem(
                    description=f"{service_type} Service",
                    quantity=1.0,
                    unit_price=price,
                    unit="job"
                )]
            elif service_lower in ['flooring', 'flooring installation']:
                quote_items = [QuoteItem(
                    description=f"{service_type} Service",
                    quantity=1.0,
                    unit_price=price,
                    unit="sq ft"
                )]
            elif service_lower in ['fence', 'fencing']:
                quote_items = [QuoteItem(
                    description=f"{service_type} Service",
                    quantity=1.0,
                    unit_price=price,
                    unit="linear ft"
                )]
            else:
                quote_items = [QuoteItem(
                    description=f"{service_type} Service",
                    quantity=1.0,
                    unit_price=price,
                    unit="job"
                )]
        
        # Create quote
        hawaii_time = get_hawaii_time()
        valid_until = (hawaii_time + timedelta(days=30)).strftime('%Y-%m-%d')
        
        quote_data = {
            'contact_id': contact.id,
            'service_type': service_type.lower().replace(' ', '_'),
            'items': quote_items,
            'total_amount': price,
            'valid_until': valid_until,
            'notes': f'Generated via API for job {job_id}' if job_id else 'Generated via API'
        }
        
        quote = handyman_storage.add_quote(quote_data)
        
        # Initialize automated workflow tracking for quote follow-up
        try:
            from workflow_automation_service import WorkflowAutomationService
            workflow_service = WorkflowAutomationService()
            workflow_result = workflow_service.initialize_quote_workflow(quote.id)
            logging.info(f"Workflow automation initialized for quote {quote.id}")
        except Exception as e:
            logging.warning(f"Workflow automation failed for quote {quote.id}: {e}")
        
        # Generate PDF
        from pdf_service import generate_quote_pdf
        filename = generate_quote_pdf(quote, contact)
        pdf_path = f"/admin/crm/quotes/{quote.id}/pdf"
        
        # Send notification if configured
        try:
            notification_service.send_inquiry_alert(
                'API Quote Generated',
                contact.name,
                contact.phone,
                contact.email,
                f"Quote Q{quote.id:04d} for {service_type} - ${price:.2f}"
            )
        except Exception as e:
            logging.warning(f"Could not send notification: {e}")
        
        return jsonify({
            'message': 'Quote generated successfully',
            'quoteId': f"Q{quote.id:04d}",
            'jobId': job_id,
            'customer': contact.name,
            'phone': contact.phone,
            'serviceType': service_type,
            'price': price,
            'total': quote.total_amount * 1.04712,  # Include Hawaii tax
            'path': pdf_path,
            'downloadUrl': url_for('download_quote_pdf', quote_id=quote.id, _external=True),
            'viewUrl': url_for('quote_detail', quote_id=quote.id, _external=True),
            'date': hawaii_time.strftime('%m/%d/%Y')
        }), 201
        
    except Exception as e:
        logging.error(f"Error generating quote via API: {e}")
        return jsonify({'error': 'Failed to generate quote', 'details': str(e)}), 500

@app.route('/api/download-quote/<quote_id>')
def download_quote_api(quote_id):
    """API endpoint for downloading quote PDFs"""
    try:
        # Handle both numeric and formatted quote IDs
        if quote_id.startswith('Q'):
            numeric_id = int(quote_id[1:])
        else:
            numeric_id = int(quote_id)
        
        quotes = handyman_storage.get_all_quotes()
        quote = next((q for q in quotes if q.id == numeric_id), None)
        
        if not quote:
            return jsonify({'error': 'Quote not found'}), 404
        
        contact = handyman_storage.get_contact_by_id(quote.contact_id)
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        # Generate PDF if it doesn't exist
        from pdf_service import generate_quote_pdf
        filename = generate_quote_pdf(quote, contact)
        
        from flask import send_file
        return send_file(f"static/pdfs/{filename}", as_attachment=True, download_name=filename)
        
    except Exception as e:
        logging.error(f"Error downloading quote via API: {e}")
        return jsonify({'error': 'Failed to download quote', 'details': str(e)}), 500

@app.route('/api/generate-invoice', methods=['POST'])
def generate_invoice_api():
    """API endpoint for generating invoices - compatible with external integrations"""
    try:
        # Parse request data
        data = request.get_json() if request.is_json else request.form
        
        client_id = data.get('clientId')
        job_id = data.get('jobId')
        customer = data.get('customer')
        total = float(data.get('total', 0))
        
        # Validate required fields
        if not all([customer, total]):
            return jsonify({'error': 'Missing required fields: customer and total are required'}), 400
        
        # Check if contact exists or create new one
        contacts = handyman_storage.get_all_contacts()
        contact = next((c for c in contacts if c.name and customer and c.name.lower() == customer.lower()), None)
        
        if not contact:
            # Create new contact for invoice
            safe_email = 'customer'
            if customer and isinstance(customer, str):
                safe_email = customer.lower().replace(' ', '.')
            contact_data = {
                'name': customer,
                'email': f"{safe_email}@tempmail.com",
                'phone': phone_formatter.format_phone('8085550000'),  # Default formatted phone for API invoices
                'address': '',
                'notes': f'Created via API for invoice {job_id}' if job_id else 'Created via API for invoice',
                'tags': ['api_generated', 'invoice_only']
            }
            contact = handyman_storage.add_contact(contact_data)
        
        # Create a basic quote first (required for invoice generation)
        from models import QuoteItem
        
        # Calculate subtotal from total (reverse Hawaii tax calculation)
        hawaii_tax_rate = 0.04712  # Hawaii GET tax (4.712% O'ahu rate)
        subtotal = total / (1 + hawaii_tax_rate)
        
        quote_items = [QuoteItem(
            description="Services Rendered",
            quantity=1.0,
            unit_price=subtotal,
            unit="job"
        )]
        
        # Create quote
        hawaii_time = get_hawaii_time()
        valid_until = (hawaii_time + timedelta(days=30)).strftime('%Y-%m-%d')
        
        quote_data = {
            'contact_id': contact.id,
            'service_type': 'api_generated',
            'items': quote_items,
            'total_amount': subtotal,
            'valid_until': valid_until,
            'notes': f'Auto-generated quote for invoice {job_id}' if job_id else 'Auto-generated quote for API invoice'
        }
        
        quote = handyman_storage.add_quote(quote_data)
        
        # Create invoice from quote
        from models import Invoice
        
        invoice_data = {
            'contact_id': contact.id,
            'quote_id': quote.id,
            'items': quote_items,
            'subtotal': subtotal,
            'tax_rate': hawaii_tax_rate,
            'payment_terms': 'Net 30'
        }
        
        invoice = handyman_storage.add_invoice(invoice_data)
        
        # Generate PDF
        from pdf_service import generate_invoice_pdf
        filename = generate_invoice_pdf(invoice, contact)
        pdf_path = f"/admin/crm/invoices/{invoice.id}/pdf"
        
        # Send notification if configured
        try:
            notification_service.send_inquiry_alert(
                'API Invoice Generated',
                contact.name,
                contact.phone,
                contact.email,
                f"Invoice I{invoice.id:04d} for ${total:.2f}"
            )
        except Exception as e:
            logging.warning(f"Could not send notification: {e}")
        
        return jsonify({
            'message': 'Invoice generated successfully',
            'invoiceId': f"I{invoice.id:04d}",
            'jobId': job_id,
            'customer': contact.name,
            'total': total,
            'subtotal': subtotal,
            'tax': total - subtotal,
            'path': pdf_path,
            'downloadUrl': url_for('download_invoice_pdf', invoice_id=invoice.id, _external=True),
            'viewUrl': url_for('invoice_detail', invoice_id=invoice.id, _external=True),
            'date': hawaii_time.strftime('%m/%d/%Y')
        }), 201
        
    except Exception as e:
        logging.error(f"Error generating invoice via API: {e}")
        return jsonify({'error': 'Failed to generate invoice', 'details': str(e)}), 500

@app.route('/api/download-invoice/<invoice_id>')
def download_invoice_api(invoice_id):
    """API endpoint for downloading invoice PDFs"""
    try:
        # Handle both numeric and formatted invoice IDs
        if invoice_id.startswith('I'):
            numeric_id = int(invoice_id[1:])
        else:
            numeric_id = int(invoice_id)
        
        invoices = handyman_storage.get_all_invoices()
        invoice = next((i for i in invoices if i.id == numeric_id), None)
        
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        contact = handyman_storage.get_contact_by_id(invoice.contact_id)
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        # Generate PDF if it doesn't exist
        from pdf_service import generate_invoice_pdf
        filename = generate_invoice_pdf(invoice, contact)
        
        from flask import send_file
        return send_file(f"static/pdfs/{filename}", as_attachment=True, download_name=filename)
        
    except Exception as e:
        logging.error(f"Error downloading invoice via API: {e}")
        return jsonify({'error': 'Failed to download invoice', 'details': str(e)}), 500

@app.route('/quote-invoice-generator')
def quote_invoice_generator():
    """Professional quote and invoice generation form"""
    return render_template('quote_invoice_generator.html')

@app.route('/quote-generator')
def quote_generator():
    """Dedicated quote generator form"""
    return render_template('quote_generator.html')

@app.route('/invoice-generator')
def invoice_generator():
    """Dedicated invoice generator form"""
    return render_template('invoice_generator.html')

@app.route('/admin/invoice-management')
def admin_invoice_management():
    """Invoice management dashboard"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin/invoice_management.html')

@app.route('/api/invoices/mark-paid', methods=['POST'])
def mark_invoice_paid():
    """Mark an invoice as paid with payment details"""
    try:
        invoice_id = request.form.get('invoice_id')
        payment_method = request.form.get('payment_method')
        payment_amount = float(request.form.get('payment_amount', 0))
        payment_date = request.form.get('payment_date')
        payment_notes = request.form.get('payment_notes', '')
        
        if not all([invoice_id, payment_method, payment_amount, payment_date]):
            return jsonify({'error': 'Missing required payment information'}), 400
        
        # Load invoices
        invoices = []
        if os.path.exists('data/invoices.json'):
            with open('data/invoices.json', 'r') as f:
                invoices = json.load(f)
        
        # Find the invoice
        invoice_found = False
        for invoice in invoices:
            if invoice['id'] == invoice_id:
                invoice['status'] = 'paid'
                invoice['payment_method'] = payment_method
                invoice['payment_amount'] = payment_amount
                invoice['payment_date'] = payment_date
                invoice['payment_notes'] = payment_notes
                invoice['paid_date'] = datetime.now().isoformat()
                invoice_found = True
                break
        
        if not invoice_found:
            return jsonify({'error': 'Invoice not found'}), 404
        
        # Save updated invoices
        with open('data/invoices.json', 'w') as f:
            json.dump(invoices, f, indent=2)
        
        # Log the payment in job tracking system
        if storage_service and hasattr(storage_service, 'log_payment'):
            storage_service.log_payment({
                'invoice_id': invoice_id,
                'amount': payment_amount,
                'method': payment_method,
                'date': payment_date,
                'notes': payment_notes,
                'recorded_date': datetime.now().isoformat()
            })
        
        return jsonify({
            'success': True,
            'message': f'Invoice {invoice_id} marked as paid',
            'payment_details': {
                'method': payment_method,
                'amount': payment_amount,
                'date': payment_date
            }
        })
        
    except Exception as e:
        logging.error(f"Error marking invoice as paid: {e}")
        return jsonify({'error': f'Failed to mark invoice as paid: {str(e)}'}), 500

@app.route('/api/convert-quote-to-invoice', methods=['POST'])
def convert_quote_to_invoice():
    """Convert a quote to an invoice with workflow automation"""
    try:
        data = request.get_json()
        quote_id = data.get('quote_id')
        
        if not quote_id:
            return jsonify({'error': 'Quote ID is required'}), 400
        
        # Load quotes
        quotes = []
        if os.path.exists('data/quotes.json'):
            with open('data/quotes.json', 'r') as f:
                quotes = json.load(f)
        
        # Find the quote
        quote = None
        for q in quotes:
            if q['id'] == quote_id:
                quote = q
                break
        
        if not quote:
            return jsonify({'error': f'Quote {quote_id} not found'}), 404
        
        if quote.get('status') != 'pending':
            return jsonify({'error': f'Quote {quote_id} is not in pending status'}), 400
        
        # Generate invoice ID
        existing_invoices = []
        if os.path.exists('data/invoices.json'):
            with open('data/invoices.json', 'r') as f:
                existing_invoices = json.load(f)
        
        invoice_id = f"I{datetime.now().strftime('%Y')}-{len(existing_invoices) + 1:04d}"
        
        # Create invoice from quote
        invoice_data = {
            'id': invoice_id,
            'quote_id': quote_id,
            'contact_id': quote.get('contact_id'),
            'customer_name': quote.get('customer_name'),
            'customer_phone': quote.get('customer_phone'),
            'customer_address': quote.get('customer_address'),
            'service_type': quote.get('service_type'),
            'items': quote.get('items', []),
            'subtotal': quote.get('subtotal'),
            'total_discount': quote.get('total_discount', 0),
            'total_tax': quote.get('total_tax'),
            'total_amount': quote.get('total_amount'),
            'status': 'pending',
            'payment_terms': 'Net 30',
            'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'created_by': 'Admin',
            'notes': f'Generated from quote {quote_id}'
        }
        
        # Load and update invoices
        invoices = []
        if os.path.exists('data/invoices.json'):
            with open('data/invoices.json', 'r') as f:
                invoices = json.load(f)
        
        invoices.append(invoice_data)
        
        # Save invoices
        os.makedirs('data', exist_ok=True)
        with open('data/invoices.json', 'w') as f:
            json.dump(invoices, f, indent=2)
        
        # Update quote status
        quote['status'] = 'converted'
        quote['converted_to_invoice'] = invoice_id
        quote['converted_date'] = datetime.now().isoformat()
        
        # Save updated quotes
        with open('data/quotes.json', 'w') as f:
            json.dump(quotes, f, indent=2)
        
        # Trigger workflow automation
        try:
            from workflow_automation import WorkflowAutomation
            workflow = WorkflowAutomation()
            
            workflow_result = workflow.process_invoice_generation(invoice_data)
            
        except Exception as workflow_error:
            logging.warning(f"Workflow automation error: {workflow_error}")
            workflow_result = {'status_changed': False, 'message': 'Workflow automation unavailable'}
        
        return jsonify({
            'success': True,
            'invoice_id': invoice_id,
            'quote_id': quote_id,
            'message': f'Quote {quote_id} successfully converted to invoice {invoice_id}',
            'workflow_update': workflow_result
        })
        
    except Exception as e:
        logging.error(f"Error converting quote to invoice: {e}")
        return jsonify({'error': f'Failed to convert quote: {str(e)}'}), 500

@app.route('/api/reminders/process', methods=['POST'])
def process_reminders():
    """Process all pending reminders"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from reminder_service import ReminderService
        reminder_service = ReminderService()
        
        processed = reminder_service.process_pending_reminders()
        stats = reminder_service.get_reminder_statistics()
        
        return jsonify({
            'success': True,
            'processed_count': len(processed),
            'processed_reminders': processed,
            'statistics': stats
        })
        
    except Exception as e:
        logging.error(f"Error processing reminders: {e}")
        return jsonify({'error': f'Failed to process reminders: {str(e)}'}), 500

@app.route('/api/reminders/schedule/appointment', methods=['POST'])
def schedule_appointment_reminder():
    """Schedule reminders for an appointment"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from reminder_service import ReminderService
        reminder_service = ReminderService()
        
        appointment_data = request.get_json()
        
        success = reminder_service.schedule_appointment_reminder(appointment_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Reminders scheduled for appointment {appointment_data.get("id")}'
            })
        else:
            return jsonify({'error': 'Failed to schedule reminders'}), 500
            
    except Exception as e:
        logging.error(f"Error scheduling appointment reminder: {e}")
        return jsonify({'error': f'Failed to schedule reminder: {str(e)}'}), 500

@app.route('/api/reminders/schedule/invoice', methods=['POST'])
def schedule_invoice_reminder():
    """Schedule reminders for an invoice"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from reminder_service import ReminderService
        reminder_service = ReminderService()
        
        invoice_data = request.get_json()
        
        success = reminder_service.schedule_invoice_reminder(invoice_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Payment reminders scheduled for invoice {invoice_data.get("id")}'
            })
        else:
            return jsonify({'error': 'Failed to schedule reminders'}), 500
            
    except Exception as e:
        logging.error(f"Error scheduling invoice reminder: {e}")
        return jsonify({'error': f'Failed to schedule reminder: {str(e)}'}), 500

@app.route('/api/messaging/send-client-message', methods=['POST'])
def send_client_message():
    """Send message to client via email or SMS"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        client_id = data.get('client_id')
        message_type = data.get('message_type')  # email, sms, both
        subject = data.get('subject', '')
        message = data.get('message')
        
        if not all([client_id, message_type, message]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Load client data
        contacts = []
        if os.path.exists('data/contacts.json'):
            with open('data/contacts.json', 'r') as f:
                contacts = json.load(f)
        
        client = None
        for contact in contacts:
            if contact['id'] == client_id:
                client = contact
                break
        
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # Send message
        from notification_service import NotificationService
        notification_service = NotificationService()
        
        results = {}
        
        if message_type in ['email', 'both'] and client.get('email'):
            email_success = notification_service.send_email(
                client['email'], 
                subject or 'Message from SPANKKS Construction',
                message
            )
            results['email'] = 'sent' if email_success else 'failed'
        
        if message_type in ['sms', 'both'] and client.get('phone'):
            sms_success = notification_service.send_sms(
                client['phone'], 
                message
            )
            results['sms'] = 'sent' if sms_success else 'failed'
        
        # Log the communication
        communication_log = {
            'id': f"msg_{int(datetime.now().timestamp())}",
            'client_id': client_id,
            'client_name': client['name'],
            'message_type': message_type,
            'subject': subject,
            'message': message,
            'sent_date': datetime.now().isoformat(),
            'sent_by': 'Admin',
            'results': results
        }
        
        # Save communication log
        os.makedirs('data', exist_ok=True)
        communications = []
        if os.path.exists('data/communications.json'):
            with open('data/communications.json', 'r') as f:
                communications = json.load(f)
        
        communications.append(communication_log)
        
        with open('data/communications.json', 'w') as f:
            json.dump(communications, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Message sent to {client["name"]}',
            'results': results,
            'communication_id': communication_log['id']
        })
        
    except Exception as e:
        logging.error(f"Error sending client message: {e}")
        return jsonify({'error': f'Failed to send message: {str(e)}'}), 500

@app.route('/api/messaging/communication-history/<client_id>')
def get_communication_history(client_id):
    """Get communication history for a client"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        communications = []
        if os.path.exists('data/communications.json'):
            with open('data/communications.json', 'r') as f:
                all_communications = json.load(f)
                communications = [c for c in all_communications if c.get('client_id') == client_id]
        
        # Sort by date, most recent first
        communications.sort(key=lambda x: x.get('sent_date', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'communications': communications,
            'total': len(communications)
        })
        
    except Exception as e:
        logging.error(f"Error getting communication history: {e}")
        return jsonify({'error': f'Failed to get history: {str(e)}'}), 500

@app.route('/admin/client-messaging')
def client_messaging_dashboard():
    """Client messaging and communication dashboard"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # Get all clients
        contacts = []
        if os.path.exists('data/contacts.json'):
            with open('data/contacts.json', 'r') as f:
                contacts = json.load(f)
        
        # Get recent communications
        recent_communications = []
        if os.path.exists('data/communications.json'):
            with open('data/communications.json', 'r') as f:
                all_communications = json.load(f)
                recent_communications = sorted(
                    all_communications, 
                    key=lambda x: x.get('sent_date', ''), 
                    reverse=True
                )[:10]  # Last 10 communications
        
        # Get reminder statistics
        try:
            from reminder_service import ReminderService
            reminder_service = ReminderService()
            reminder_stats = reminder_service.get_reminder_statistics()
        except:
            reminder_stats = {
                'total_scheduled': 0,
                'sent_today': 0,
                'pending': 0,
                'failed': 0
            }
        
        return render_template('admin/client_messaging.html',
                             contacts=contacts,
                             recent_communications=recent_communications,
                             reminder_stats=reminder_stats)
        
    except Exception as e:
        logging.error(f"Error loading client messaging dashboard: {e}")
        flash('Error loading messaging dashboard.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/api/invoices')
def api_invoices():
    """API endpoint to get all invoices with payment status"""
    try:
        invoices = []
        if os.path.exists('data/invoices.json'):
            with open('data/invoices.json', 'r') as f:
                invoices = json.load(f)
        
        # Ensure each invoice has required fields for the management dashboard
        for invoice in invoices:
            if 'status' not in invoice:
                invoice['status'] = 'pending'
            if 'created_date' not in invoice:
                invoice['created_date'] = datetime.now().isoformat()
            
            # Format total_amount as float
            if isinstance(invoice.get('total_amount'), str):
                try:
                    invoice['total_amount'] = float(invoice['total_amount'].replace('$', '').replace(',', ''))
                except (ValueError, AttributeError):
                    invoice['total_amount'] = 0.0
        
        return jsonify(invoices)
        
    except Exception as e:
        logging.error(f"Error retrieving invoices: {e}")
        return jsonify({'error': f'Failed to retrieve invoices: {str(e)}'}), 500

@app.route('/admin/enhanced-staff-management')
def enhanced_staff_management():
    """Enhanced staff management dashboard"""
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin/enhanced_staff_management.html')

@app.route('/api/staff/enhanced')
def api_staff_enhanced():
    """API endpoint to get enhanced staff data with skills and performance"""
    try:
        staff_data = []
        
        # Load existing staff data
        if os.path.exists('data/staff.json'):
            with open('data/staff.json', 'r') as f:
                staff_data = json.load(f)
        
        # Enhance staff data with additional fields if not present
        for staff in staff_data:
            if 'skills' not in staff:
                staff['skills'] = ['General Handyman', 'Basic Tools']
            if 'performance_score' not in staff:
                staff['performance_score'] = 95
            if 'availability_status' not in staff:
                staff['availability_status'] = 'available'
            if 'hourly_rate' not in staff:
                staff['hourly_rate'] = 25.00
            if 'hire_date' not in staff:
                staff['hire_date'] = datetime.now().strftime('%Y-%m-%d')
            if 'working_days' not in staff:
                staff['working_days'] = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
            if 'start_time' not in staff:
                staff['start_time'] = '07:00'
            if 'end_time' not in staff:
                staff['end_time'] = '17:00'
        
        return jsonify(staff_data)
        
    except Exception as e:
        logging.error(f"Error retrieving enhanced staff data: {e}")
        return jsonify({'error': f'Failed to retrieve staff data: {str(e)}'}), 500

@app.route('/api/staff/save', methods=['POST'])
def api_staff_save():
    """API endpoint to save staff member with enhanced data"""
    try:
        staff_id = request.form.get('staff_id')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')
        hourly_rate = float(request.form.get('hourly_rate', 25.00))
        hire_date = request.form.get('hire_date')
        skills = json.loads(request.form.get('skills', '[]'))
        working_days = json.loads(request.form.get('working_days', '[]'))
        start_time = request.form.get('start_time', '07:00')
        end_time = request.form.get('end_time', '17:00')
        notes = request.form.get('notes', '')
        
        # Validate required fields
        if not all([name, email, phone, role]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Format phone number
        formatted_phone = phone_formatter.format_phone(phone)
        
        # Load existing staff data
        staff_data = []
        if os.path.exists('data/staff.json'):
            with open('data/staff.json', 'r') as f:
                staff_data = json.load(f)
        
        # Create new staff record
        new_staff = {
            'id': staff_id if staff_id else f"STF{len(staff_data) + 1:03d}",
            'name': name,
            'email': email,
            'phone': formatted_phone,
            'role': role,
            'hourly_rate': hourly_rate,
            'hire_date': hire_date,
            'skills': skills,
            'working_days': working_days,
            'start_time': start_time,
            'end_time': end_time,
            'notes': notes,
            'performance_score': 95,  # Default performance score
            'availability_status': 'available',
            'active': True,
            'created_date': datetime.now().isoformat()
        }
        
        # Update existing or add new
        if staff_id:
            # Update existing staff
            for i, staff in enumerate(staff_data):
                if staff['id'] == staff_id:
                    staff_data[i] = new_staff
                    break
        else:
            # Add new staff
            staff_data.append(new_staff)
        
        # Save updated staff data
        os.makedirs('data', exist_ok=True)
        with open('data/staff.json', 'w') as f:
            json.dump(staff_data, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Staff member saved successfully',
            'staff_id': new_staff['id']
        })
        
    except Exception as e:
        logging.error(f"Error saving staff member: {e}")
        return jsonify({'error': f'Failed to save staff member: {str(e)}'}), 500

@app.route('/upload/<job_id>/<photo_type>', methods=['POST'])
def upload_job_photos(job_id, photo_type):
    """Upload job photos (before/after) with metadata tracking"""
    
    # Validate photo type
    if photo_type not in ['before', 'after']:
        return jsonify({'error': 'Invalid photo type. Must be "before" or "after"'}), 400
    
    try:
        # Get uploaded files
        uploaded_files = request.files.getlist('photos')
        
        if not uploaded_files or all(file.filename == '' for file in uploaded_files):
            return jsonify({'error': 'No files provided'}), 400
        
        results = []
        errors = []
        
        # Process each uploaded file
        for file in uploaded_files:
            if file.filename != '':
                # Add metadata
                metadata = {
                    'uploader_ip': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', ''),
                    'photo_type': photo_type,
                    'job_id': job_id
                }
                
                result = photo_service.save_photo(file, job_id, photo_type, metadata)
                
                if result.get('success'):
                    results.append({
                        'filename': result['filename'],
                        'file_size': result['file_size'],
                        'upload_date': datetime.now().isoformat()
                    })
                else:
                    errors.append(f"{file.filename}: {result.get('error')}")
        
        # Send inquiry alert for photo uploads
        try:
            from notification_service import NotificationService
            notification_service = NotificationService()
            notification_service.send_inquiry_alert(
                inquiry_type='photo_upload',
                customer_name=f'Job {job_id}',
                phone_number='(808) 452-9779',  # Admin phone
                email='spank808@gmail.com',
                service_type=f'{photo_type} photos uploaded'
            )
        except Exception as e:
            logging.warning(f"Could not send photo upload notification: {e}")
        
        response_data = {
            'message': f'Upload completed for job {job_id}',
            'job_id': job_id,
            'photo_type': photo_type,
            'uploaded_files': results,
            'success_count': len(results),
            'error_count': len(errors)
        }
        
        if errors:
            response_data['errors'] = errors
        
        return jsonify(response_data), 201 if results else 400
        
    except Exception as e:
        logging.error(f"Error uploading photos: {e}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/photos/<job_id>')
@app.route('/photos/<job_id>/<photo_type>')
def get_job_photos(job_id, photo_type=None):
    """Get all photos for a job"""
    
    try:
        photos = photo_service.get_job_photos(job_id, photo_type)
        return jsonify({
            'job_id': job_id,
            'photos': photos
        })
        
    except Exception as e:
        logging.error(f"Error getting job photos: {e}")
        return jsonify({'error': f'Failed to get photos: {str(e)}'}), 500

@app.route('/photo/<job_id>/<photo_type>/<filename>')
def serve_photo(job_id, photo_type, filename):
    """Serve uploaded photo files"""
    import os
    from flask import send_file
    
    try:
        file_path = os.path.join(photo_service.get_job_directory(job_id, photo_type), filename)
        
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return jsonify({'error': 'Photo not found'}), 404
            
    except Exception as e:
        logging.error(f"Error serving photo: {e}")
        return jsonify({'error': f'Failed to serve photo: {str(e)}'}), 500

@app.route('/photo/<job_id>/<photo_type>/<filename>', methods=['DELETE'])
def delete_job_photo(job_id, photo_type, filename):
    """Delete a specific job photo"""
    
    try:
        result = photo_service.delete_photo(job_id, photo_type, filename)
        
        if result.get('success'):
            return jsonify({'message': 'Photo deleted successfully'})
        else:
            return jsonify({'error': result.get('error', 'Delete failed')}), 400
            
    except Exception as e:
        logging.error(f"Error deleting photo: {e}")
        return jsonify({'error': f'Failed to delete photo: {str(e)}'}), 500

@app.route('/job-photos/<job_id>')
def job_photos_interface(job_id):
    """Job photo upload and management interface"""
    
    # Get existing photos
    existing_photos = photo_service.get_job_photos(job_id)
    
    return render_template('job_photos.html', 
                         job_id=job_id, 
                         existing_photos=existing_photos)

# ===============================
# JOB SITE PORTAL AUTHENTICATION
# ===============================

@app.route('/login')
def portal_login_page():
    """Job Site Portal login page"""
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def portal_login():
    """Handle portal login authentication"""
    client_id = request.form.get('clientId', '').strip()
    job_id = request.form.get('jobId', '').strip()
    staff_pin = request.form.get('staffPin', '').strip() or None
    
    if not client_id or not job_id:
        flash('Please enter both Client ID and Job ID', 'error')
        return render_template('login.html')
    
    # Authenticate user
    success, client_data, access_level = auth_service.authenticate(client_id, job_id, staff_pin)
    
    if not success:
        flash('Invalid credentials. Please check your Client ID, Job ID, and PIN (if provided).', 'error')
        return render_template('login.html')
    
    # Store session data
    session['portal_authenticated'] = True
    session['client_id'] = client_id
    session['job_id'] = job_id
    session['access_level'] = access_level
    session['client_data'] = client_data
    
    # Redirect based on access level
    if access_level == 'staff':
        flash(f'Welcome back! Staff access granted for Job #{job_id}', 'success')
        return redirect(url_for('staff_portal', job_id=job_id))
    else:
        name = client_data.get("name", "User") if client_data else "User"
        flash(f'Welcome {name}! Client portal access granted.', 'success')
        return redirect(url_for('client_portal', client_id=client_id, job_id=job_id))

@app.route('/portal/<client_id>/<job_id>')
def client_portal(client_id, job_id):
    """Client portal - read-only access"""
    if not session.get('portal_authenticated') or session.get('client_id') != client_id or session.get('job_id') != job_id:
        flash('Please log in to access the portal', 'error')
        return redirect(url_for('portal_login_page'))
    
    # Get fresh client data from auth service database
    client_data = auth_service.find_client(client_id, job_id)
    if not client_data:
        flash('Client data not found. Please contact support.', 'error')
        return redirect(url_for('portal_login_page'))
    
    # Update session with fresh data
    session['client_data'] = client_data
    
    return render_template('client_portal.html', client=client_data)

@app.route('/job/<job_id>')
def staff_portal(job_id):
    """Staff portal - full access"""
    if (not session.get('portal_authenticated') or 
        session.get('access_level') != 'staff' or 
        session.get('job_id') != job_id):
        flash('Staff access required. Please log in with your PIN.', 'error')
        return redirect(url_for('portal_login_page'))
    
    # Get fresh client data from auth service database
    client_id = session.get('client_id')
    client_data = auth_service.find_client(client_id, job_id)
    if not client_data:
        flash('Client data not found. Please contact support.', 'error')
        return redirect(url_for('portal_login_page'))
    
    # Update session with fresh data
    session['client_data'] = client_data
    
    return render_template('staff_portal.html', client=client_data)

@app.route('/portal/logout')
def portal_logout():
    """Logout from portal"""
    session.pop('portal_authenticated', None)
    session.pop('client_id', None)
    session.pop('job_id', None)
    session.pop('access_level', None)
    session.pop('client_data', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('portal_login_page'))

# ===============================
# PORTAL API ENDPOINTS
# ===============================

@app.route('/api/client/<client_id>/quotes')
def get_client_quotes(client_id):
    """Get quotes for a specific client"""
    if not session.get('portal_authenticated') or session.get('client_id') != client_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get client data to find their name for contact lookup
    client_data = session.get('client_data', {})
    client_name = client_data.get('name', '')
    
    if not client_name:
        return jsonify({'error': 'Client name not found'}), 400
    
    # Find the contact by name
    all_contacts = handyman_storage.get_all_contacts()
    client_contact = None
    for contact in all_contacts:
        if contact.name == client_name:
            client_contact = contact
            break
    
    if not client_contact:
        return jsonify({'quotes': [], 'count': 0})
    
    # Get quotes for this contact
    all_quotes = handyman_storage.get_all_quotes()
    client_quotes = []
    for quote in all_quotes:
        if quote.contact_id == client_contact.id:
            quote_dict = {
                'id': quote.id,
                'service_type': quote.service_type,
                'total_amount': quote.total_amount,
                'status': quote.status,
                'created_date': quote.created_date,
                'valid_until': quote.valid_until,
                'notes': quote.notes
            }
            client_quotes.append(quote_dict)
    
    return jsonify({
        'quotes': client_quotes,
        'count': len(client_quotes)
    })

@app.route('/api/client/<client_id>/invoices')
def get_client_invoices(client_id):
    """Get invoices for a specific client"""
    if not session.get('portal_authenticated') or session.get('client_id') != client_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get client data to find their name for contact lookup
    client_data = session.get('client_data', {})
    client_name = client_data.get('name', '')
    
    if not client_name:
        return jsonify({'error': 'Client name not found'}), 400
    
    # Find the contact by name
    all_contacts = handyman_storage.get_all_contacts()
    client_contact = None
    for contact in all_contacts:
        if contact.name == client_name:
            client_contact = contact
            break
    
    if not client_contact:
        return jsonify({'invoices': [], 'count': 0})
    
    # Get invoices for this contact
    all_invoices = handyman_storage.get_all_invoices()
    client_invoices = []
    for invoice in all_invoices:
        if invoice.contact_id == client_contact.id:
            invoice_dict = {
                'id': invoice.id,
                'invoice_number': getattr(invoice, 'invoice_number', f'I{invoice.id:04d}'),
                'total_amount': invoice.total_amount,
                'status': invoice.status,
                'created_date': invoice.created_date,
                'due_date': getattr(invoice, 'due_date', ''),
                'notes': getattr(invoice, 'notes', '')
            }
            client_invoices.append(invoice_dict)
    
    return jsonify({
        'invoices': client_invoices,
        'count': len(client_invoices)
    })

@app.route('/api/job/<job_id>/notes')
def get_job_notes(job_id):
    """Get notes for a specific job"""
    if not session.get('portal_authenticated') or session.get('job_id') != job_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get job notes from CRM
    all_jobs = handyman_storage.get_all_jobs()
    job = next((j for j in all_jobs if j.get('job_id') == job_id), None)
    
    if job:
        notes = job.get('notes', [])
        return jsonify({
            'notes': notes,
            'count': len(notes)
        })
    
    return jsonify({'notes': [], 'count': 0})

# ===============================
# LEGAL AND SUPPORT PAGES
# ===============================

@app.route('/terms-of-service')
def terms_of_service():
    """Terms of Service page"""
    return render_template('terms_of_service.html')

@app.route('/privacy-policy')
def privacy_policy():
    """Privacy Policy page"""
    return render_template('privacy_policy.html')

@app.route('/help-faq')
def help_faq():
    """Help & FAQ page"""
    return render_template('help_faq.html')

# Note: send_client_message route exists elsewhere in file - duplicate removed

# ===============================
# FILE STORAGE MANAGEMENT
# ===============================

@app.route('/admin/file-storage')
def file_storage_dashboard():
    """File storage management dashboard"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Get storage statistics
    stats = file_storage.get_storage_statistics()
    
    # Get recent files
    recent_files = []
    for category in ['invoice', 'quote', 'photo_before', 'photo_after', 'contract']:
        category_files = file_storage.get_files_by_category(category, limit=10)
        recent_files.extend(category_files)
    
    # Sort by upload date
    recent_files.sort(key=lambda x: x.get('upload_date', ''), reverse=True)
    recent_files = recent_files[:20]
    
    return render_template('admin/file_storage.html',
                         storage_stats=stats,
                         recent_files=recent_files)

@app.route('/admin/create-backup', methods=['POST'])
def create_backup():
    """Create a system backup"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    backup_type = data.get('type', 'manual')
    
    try:
        result = file_storage.create_backup(backup_type)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Backup created successfully',
                'backup_info': result['backup_info']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            })
            
    except Exception as e:
        logging.error(f"Error creating backup: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ===============================
# SCHEDULER & CALENDAR SYSTEM
# ===============================

@app.route('/admin/scheduler')
def scheduler_dashboard():
    """Comprehensive scheduler with daily/weekly/monthly views"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Load data from JSON files
    with open('data/inquiries.json', 'r') as f:
        inquiries = json.load(f)
    
    with open('data/staff.json', 'r') as f:
        staff = json.load(f)
    
    # Get CRM jobs
    all_jobs = handyman_storage.get_all_jobs()
    
    return render_template('scheduler.html', 
                         inquiries=inquiries,
                         staff=staff,
                         jobs=all_jobs)

@app.route('/admin/inquiries')
def inquiry_management():
    """Inquiry management dashboard with CRM workflow"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    with open('data/inquiries.json', 'r') as f:
        inquiries = json.load(f)
    
    # Sort by status priority and date
    status_priority = {'received': 1, 'review': 2, 'tentative': 3, 'quoted': 4, 'booked': 5}
    inquiries.sort(key=lambda x: (status_priority.get(x['status'], 99), x['created_date']))
    
    return render_template('inquiry_management.html', inquiries=inquiries)

@app.route('/admin/inquiry/<inquiry_id>/status', methods=['POST'])
def update_inquiry_status(inquiry_id):
    """Update inquiry status in workflow"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    new_status = request.form.get('status')
    notes = request.form.get('notes', '')
    
    with open('data/inquiries.json', 'r') as f:
        inquiries = json.load(f)
    
    # Find and update inquiry
    for inquiry in inquiries:
        if inquiry['inquiry_id'] == inquiry_id:
            inquiry['status'] = new_status
            inquiry['last_updated'] = get_hawaii_time().isoformat()
            if notes:
                if 'notes' not in inquiry:
                    inquiry['notes'] = []
                inquiry['notes'].append({
                    'note': notes,
                    'timestamp': get_hawaii_time().isoformat(),
                    'user': 'Admin'
                })
            break
    
    # Save back to file
    with open('data/inquiries.json', 'w') as f:
        json.dump(inquiries, f, indent=2)
    
    flash(f'Inquiry {inquiry_id} status updated to {new_status}', 'success')
    return redirect(url_for('inquiry_management'))

@app.route('/admin/inquiry/<inquiry_id>/convert-quote', methods=['POST'])
def convert_inquiry_to_quote(inquiry_id):
    """Convert inquiry to quote in CRM system"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    with open('data/inquiries.json', 'r') as f:
        inquiries = json.load(f)
    
    # Find inquiry
    inquiry = next((i for i in inquiries if i['inquiry_id'] == inquiry_id), None)
    if not inquiry:
        flash('Inquiry not found', 'error')
        return redirect(url_for('inquiry_management'))
    
    # Create contact in CRM if doesn't exist
    existing_contacts = handyman_storage.get_all_contacts()
    contact = next((c for c in existing_contacts if c['email'] == inquiry['email']), None)
    
    if not contact:
        contact_data = {
            'name': inquiry['name'],
            'email': inquiry['email'],
            'phone': inquiry['phone'],
            'address': inquiry.get('address', ''),
            'notes': f"Converted from inquiry {inquiry_id}",
            'tags': ['inquiry_conversion']
        }
        contact_id = handyman_storage.add_contact(contact_data)
    else:
        contact_id = contact['contact_id']
    
    # Create quote with inquiry details
    quote_data = {
        'contact_id': contact_id,
        'service_type': inquiry['service_type'],
        'items': [{
            'description': inquiry['description'],
            'quantity': 1,
            'unit_price': 0,  # To be filled by admin
            'unit': 'project'
        }],
        'total_amount': 0,  # To be calculated
        'valid_until': (get_hawaii_time() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'notes': f"Generated from inquiry {inquiry_id}",
        'inquiry_id': inquiry_id
    }
    
    quote_id = handyman_storage.add_quote(quote_data)
    
    # Update inquiry status
    for inq in inquiries:
        if inq['inquiry_id'] == inquiry_id:
            inq['status'] = 'quoted'
            inq['quote_id'] = quote_id
            inq['last_updated'] = get_hawaii_time().isoformat()
            break
    
    with open('data/inquiries.json', 'w') as f:
        json.dump(inquiries, f, indent=2)
    
    flash(f'Inquiry converted to quote {quote_id}', 'success')
    return redirect(url_for('quote_detail', quote_id=quote_id))

@app.route('/admin/inquiry/<inquiry_id>/schedule', methods=['POST'])
def schedule_inquiry_tentative(inquiry_id):
    """Place inquiry as tentative hold on calendar"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    tentative_date = request.form.get('tentative_date')
    tentative_time = request.form.get('tentative_time', '09:00')
    
    with open('data/inquiries.json', 'r') as f:
        inquiries = json.load(f)
    
    # Update inquiry with tentative scheduling
    for inquiry in inquiries:
        if inquiry['inquiry_id'] == inquiry_id:
            inquiry['status'] = 'tentative'
            inquiry['tentative_date'] = tentative_date
            inquiry['tentative_time'] = tentative_time
            inquiry['last_updated'] = get_hawaii_time().isoformat()
            break
    
    with open('data/inquiries.json', 'w') as f:
        json.dump(inquiries, f, indent=2)
    
    flash(f'Inquiry {inquiry_id} placed as tentative on {tentative_date}', 'success')
    return redirect(url_for('scheduler_dashboard'))

# ===============================
# STAFF MANAGEMENT SYSTEM
# ===============================

@app.route('/admin/staff')
def staff_management():
    """Staff management dashboard"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    with open('data/staff.json', 'r') as f:
        staff = json.load(f)
    
    # Get job assignments
    all_jobs = handyman_storage.get_all_jobs()
    
    return render_template('staff_management.html', staff=staff, jobs=all_jobs)

@app.route('/admin/staff/add', methods=['POST'])
def add_staff_member():
    """Add new staff member"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    with open('data/staff.json', 'r') as f:
        staff = json.load(f)
    
    # Generate new staff ID
    existing_ids = [int(s['staff_id'][3:]) for s in staff]
    new_id = max(existing_ids) + 1 if existing_ids else 1
    
    new_staff = {
        'staff_id': f'STF{new_id:03d}',
        'name': request.form.get('name'),
        'role': request.form.get('role'),
        'phone': request.form.get('phone'),
        'email': request.form.get('email'),
        'pin': request.form.get('pin'),
        'status': 'active',
        'hire_date': get_hawaii_time().strftime('%Y-%m-%d'),
        'skills': request.form.get('skills', '').split(','),
        'hourly_rate': float(request.form.get('hourly_rate', 20)),
        'assigned_jobs': [],
        'availability': {
            'monday': 'monday' in request.form,
            'tuesday': 'tuesday' in request.form,
            'wednesday': 'wednesday' in request.form,
            'thursday': 'thursday' in request.form,
            'friday': 'friday' in request.form,
            'saturday': 'saturday' in request.form,
            'sunday': 'sunday' in request.form
        }
    }
    
    staff.append(new_staff)
    
    with open('data/staff.json', 'w') as f:
        json.dump(staff, f, indent=2)
    
    flash(f'Staff member {new_staff["name"]} added successfully', 'success')
    return redirect(url_for('staff_management'))

@app.route('/admin/staff/<staff_id>/assign', methods=['POST'])
def assign_staff_to_job(staff_id):
    """Assign staff member to job"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    job_id = request.form.get('job_id')
    
    with open('data/staff.json', 'r') as f:
        staff = json.load(f)
    
    # Add job to staff assignments
    for member in staff:
        if member['staff_id'] == staff_id:
            if job_id not in member['assigned_jobs']:
                member['assigned_jobs'].append(job_id)
            break
    
    with open('data/staff.json', 'w') as f:
        json.dump(staff, f, indent=2)
    
    # Update job with assigned staff
    all_jobs = handyman_storage.get_all_jobs()
    for job in all_jobs:
        if job.get('job_id') == job_id:
            if 'assigned_staff' not in job:
                job['assigned_staff'] = []
            if staff_id not in job['assigned_staff']:
                job['assigned_staff'].append(staff_id)
                handyman_storage.add_job_note(job_id, f'Staff {staff_id} assigned to job')
            break
    
    flash(f'Staff {staff_id} assigned to job {job_id}', 'success')
    return redirect(url_for('staff_management'))

@app.route('/staff/<staff_id>/portal')
def staff_member_portal(staff_id):
    """Individual staff member portal"""
    # Basic authentication check (could be enhanced)
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    with open('data/staff.json', 'r') as f:
        staff = json.load(f)
    
    staff_member = next((s for s in staff if s['staff_id'] == staff_id), None)
    if not staff_member:
        flash('Staff member not found', 'error')
        return redirect(url_for('staff_management'))
    
    # Get assigned jobs
    all_jobs = handyman_storage.get_all_jobs()
    assigned_jobs = [job for job in all_jobs if job.get('job_id') in staff_member['assigned_jobs']]
    
    return render_template('staff_portal_individual.html', 
                         staff=staff_member, 
                         assigned_jobs=assigned_jobs)

@app.route('/staff/<staff_id>/checkin/<job_id>', methods=['POST'])
def staff_checkin(staff_id, job_id):
    """Staff check-in to job site"""
    timestamp = get_hawaii_time().isoformat()
    
    # Log check-in
    checkin_data = {
        'staff_id': staff_id,
        'job_id': job_id,
        'checkin_time': timestamp,
        'location': request.form.get('location', 'Job Site')
    }
    
    # Add note to job
    handyman_storage.add_job_note(job_id, f'Staff {staff_id} checked in at {timestamp}')
    
    flash('Successfully checked in to job site', 'success')
    return redirect(url_for('staff_member_portal', staff_id=staff_id))

# ===============================
# INVENTORY MANAGEMENT SYSTEM
# ===============================

@app.route('/admin/inventory')
def inventory_dashboard():
    """Comprehensive inventory management dashboard"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    from inventory_service import inventory_service
    
    inventory_items = inventory_service.get_all_inventory()
    inventory_summary = inventory_service.get_inventory_summary()
    low_stock_items = inventory_service.get_low_stock_items()
    
    return render_template('admin/inventory_dashboard.html',
                         inventory_items=inventory_items,
                         inventory_summary=inventory_summary,
                         low_stock_items=low_stock_items)

@app.route('/admin/inventory/add', methods=['POST'])
def add_inventory_item():
    """Add new inventory item"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    from inventory_service import inventory_service
    
    try:
        item_data = {
            'name': request.form.get('name'),
            'category': request.form.get('category', 'General'),
            'description': request.form.get('description', ''),
            'unit': request.form.get('unit', 'each'),
            'current_stock': request.form.get('current_stock', 0),
            'minimum_stock': request.form.get('minimum_stock', 5),
            'unit_cost': request.form.get('unit_cost', 0.0),
            'supplier': request.form.get('supplier', ''),
            'location': request.form.get('location', 'Main Storage')
        }
        
        new_item = inventory_service.add_inventory_item(item_data)
        flash(f'Inventory item "{new_item["name"]}" added successfully!', 'success')
        
    except Exception as e:
        flash(f'Error adding inventory item: {str(e)}', 'error')
    
    return redirect(url_for('inventory_dashboard'))

@app.route('/admin/inventory/update', methods=['POST'])
def update_inventory_item():
    """Update inventory item"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    from inventory_service import inventory_service
    
    try:
        item_id = request.form.get('item_id')
        updates = {
            'name': request.form.get('name'),
            'category': request.form.get('category'),
            'description': request.form.get('description'),
            'unit': request.form.get('unit'),
            'current_stock': int(request.form.get('current_stock', 0)),
            'minimum_stock': int(request.form.get('minimum_stock', 5)),
            'unit_cost': float(request.form.get('unit_cost', 0.0)),
            'supplier': request.form.get('supplier'),
            'location': request.form.get('location'),
            'status': request.form.get('status', 'active')
        }
        
        inventory_service.update_inventory_item(item_id, updates)
        flash('Inventory item updated successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating inventory item: {str(e)}', 'error')
    
    return redirect(url_for('inventory_dashboard'))

@app.route('/api/materials/log/<job_id>', methods=['POST'])
def log_job_materials(job_id):
    """Log materials used for a job"""
    if not session.get('portal_authenticated'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    from inventory_service import inventory_service
    
    try:
        data = request.get_json()
        materials_used = data.get('materials', [])
        
        if not materials_used:
            return jsonify({'error': 'No materials provided'}), 400
        
        usage_record = inventory_service.log_material_usage(job_id, materials_used)
        
        # Add note to job about materials logged
        handyman_storage.add_job_note(job_id, f'Materials logged: {len(materials_used)} items, Total cost: ${usage_record["total_cost"]:.2f}')
        
        return jsonify({
            'success': True,
            'usage_id': usage_record['usage_id'],
            'total_cost': usage_record['total_cost'],
            'message': 'Materials logged successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/job/<job_id>/materials')
def get_job_materials():
    """Get materials used for specific job"""
    if not session.get('portal_authenticated') and not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    from inventory_service import inventory_service
    
    try:
        materials = inventory_service.get_materials_by_job(job_id)
        cost_analysis = inventory_service.get_job_cost_analysis(job_id)
        
        return jsonify({
            'materials': materials,
            'cost_analysis': cost_analysis
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===============================
# CHECKLIST MANAGEMENT SYSTEM
# ===============================

@app.route('/admin/checklists')
def checklist_management():
    """Checklist management dashboard"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    from checklist_service import checklist_service
    
    all_checklists = checklist_service.get_all_checklists()
    templates = checklist_service.get_checklist_templates()
    completion_status = checklist_service.get_jobs_by_completion_status()
    
    return render_template('admin/checklist_management.html',
                         checklists=all_checklists,
                         templates=templates,
                         completion_status=completion_status)

@app.route('/admin/checklist/create/<job_id>', methods=['POST'])
def create_job_checklist(job_id):
    """Create checklist for a job"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    from checklist_service import checklist_service
    
    try:
        service_type = request.form.get('service_type', 'General')
        custom_tasks = request.form.getlist('custom_tasks')
        
        # Filter out empty custom tasks
        custom_tasks = [task.strip() for task in custom_tasks if task.strip()]
        
        checklist = checklist_service.create_job_checklist(job_id, service_type, custom_tasks)
        
        flash(f'Checklist created for job {job_id}', 'success')
        return jsonify({'success': True, 'checklist_id': checklist['checklist_id']})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/checklist/<checklist_id>/task/<task_id>/update', methods=['POST'])
def update_checklist_task(checklist_id, task_id):
    """Update checklist task status"""
    if not session.get('portal_authenticated') and not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    from checklist_service import checklist_service
    
    try:
        data = request.get_json()
        completed = data.get('completed', False)
        completed_by = data.get('completed_by', 'Staff')
        notes = data.get('notes', '')
        
        checklist_service.update_task_status(checklist_id, task_id, completed, completed_by, notes)
        
        return jsonify({'success': True, 'message': 'Task updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/checklist/<checklist_id>/add-task', methods=['POST'])
def add_custom_checklist_task(checklist_id):
    """Add custom task to checklist"""
    if not session.get('portal_authenticated') and not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    from checklist_service import checklist_service
    
    try:
        data = request.get_json()
        task_description = data.get('task_description', '').strip()
        required = data.get('required', False)
        
        if not task_description:
            return jsonify({'error': 'Task description is required'}), 400
        
        checklist_service.add_custom_task(checklist_id, task_description, required)
        
        return jsonify({'success': True, 'message': 'Custom task added successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/job/<job_id>/checklist')
def get_job_checklist():
    """Get checklist for specific job"""
    if not session.get('portal_authenticated') and not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    from checklist_service import checklist_service
    
    try:
        checklist = checklist_service.get_checklist_by_job(job_id)
        completion_summary = checklist_service.get_completion_summary(job_id)
        
        return jsonify({
            'checklist': checklist,
            'completion_summary': completion_summary
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===============================
# JOB COMPLETION WORKFLOW
# ===============================

@app.route('/api/job/<job_id>/complete', methods=['POST'])
def complete_job(job_id):
    """Mark job as completed with full workflow"""
    if not session.get('portal_authenticated') and not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    from checklist_service import checklist_service
    from inventory_service import inventory_service
    
    try:
        # Get completion data
        completion_summary = checklist_service.get_completion_summary(job_id)
        cost_analysis = inventory_service.get_job_cost_analysis(job_id)
        
        # Check if all required tasks are completed
        if completion_summary['required_remaining'] > 0:
            return jsonify({
                'error': f'Cannot complete job. {completion_summary["required_remaining"]} required tasks remaining.',
                'required_remaining': completion_summary['required_remaining']
            }), 400
        
        # Update job status in CRM
        handyman_storage.update_job_status(job_id, 'completed')
        
        # Add completion note
        completion_note = f'Job completed. Checklist: {completion_summary["completion_percentage"]}% complete. Material cost: ${cost_analysis["total_material_cost"]}'
        handyman_storage.add_job_note(job_id, completion_note)
        
        return jsonify({
            'success': True,
            'message': 'Job marked as completed successfully',
            'completion_summary': completion_summary,
            'cost_analysis': cost_analysis
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===============================
# CALENDAR API ENDPOINTS
# ===============================

@app.route('/api/calendar/events')
def get_calendar_events():
    """Get calendar events for scheduler"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    events = []
    
    # Add confirmed jobs
    all_jobs = handyman_storage.get_all_jobs()
    for job in all_jobs:
        if job.get('scheduled_date'):
            events.append({
                'id': f"job_{job['job_id']}",
                'title': f"Job: {job.get('service_type', 'Service')}",
                'start': job['scheduled_date'],
                'className': f"job-{job.get('status', 'scheduled')}",
                'backgroundColor': '#28a745' if job.get('status') == 'completed' else '#007bff',
                'borderColor': '#28a745' if job.get('status') == 'completed' else '#007bff',
                'url': f"/crm/job/{job['job_id']}"
            })
    
    # Add tentative inquiries
    with open('data/inquiries.json', 'r') as f:
        inquiries = json.load(f)
    
    for inquiry in inquiries:
        if inquiry['status'] == 'tentative' and inquiry.get('tentative_date'):
            events.append({
                'id': f"inquiry_{inquiry['inquiry_id']}",
                'title': f"Tentative: {inquiry['service_type']}",
                'start': inquiry['tentative_date'],
                'className': 'inquiry-tentative',
                'backgroundColor': '#ffc107',
                'borderColor': '#ffc107',
                'opacity': 0.7,
                'url': f"/admin/inquiries"
            })
    
    return jsonify(events)

@app.route('/api/staff/availability')
def get_staff_availability():
    """Get staff availability for scheduling"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    with open('data/staff.json', 'r') as f:
        staff = json.load(f)
    
    availability = {}
    for member in staff:
        if member['status'] == 'active':
            availability[member['staff_id']] = {
                'name': member['name'],
                'role': member['role'],
                'availability': member['availability'],
                'assigned_jobs': member['assigned_jobs']
            }
    
    return jsonify(availability)

# ===============================
# UNIFIED SCHEDULER ENDPOINTS
# ===============================

@app.route('/admin/scheduler/unified')
def unified_scheduler_dashboard():
    """Unified scheduler dashboard with consolidated appointment management"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # Get weekly schedule from unified scheduler
        week_data = unified_scheduler.get_weekly_schedule()
        
        # Get available staff for assignment
        staff_members = [
            {'id': 'mike_spankks', 'name': 'Mike Spankks', 'role': 'Lead Contractor'},
            {'id': 'crew_member_1', 'name': 'Crew Member 1', 'role': 'Assistant'},
            {'id': 'crew_member_2', 'name': 'Crew Member 2', 'role': 'Specialist'}
        ]
        
        # Migration status - check if legacy appointments exist
        legacy_appointments_count = len(appointments) if appointments else 0
        
        return render_template('admin/unified_scheduler.html',
                             week_data=week_data,
                             staff_members=staff_members,
                             legacy_count=legacy_appointments_count)
                             
    except Exception as e:
        logging.error(f"Error loading unified scheduler: {e}")
        flash('Error loading scheduler dashboard.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/scheduler/appointments/create', methods=['POST'])
def create_unified_appointment():
    """Create new appointment using unified scheduler"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        appointment_data = {
            'client_name': request.form['client_name'],
            'client_phone': phone_formatter.format_phone(request.form.get('client_phone', '')),
            'client_email': request.form.get('client_email', ''),
            'service_type': request.form['service_type'],
            'scheduled_date': request.form['scheduled_date'],
            'scheduled_time': request.form.get('scheduled_time', '09:00'),
            'estimated_duration': int(request.form.get('estimated_duration', 120)),
            'assigned_staff': request.form.getlist('assigned_staff'),
            'priority': request.form.get('priority', 'normal'),
            'location': request.form.get('location', ''),
            'notes': request.form.get('notes', ''),
            'created_by': session.get('user_name', 'Admin')
        }
        
        appointment = unified_scheduler.create_appointment(appointment_data)
        
        # Send notification if notification service is available
        if notification_service:
            try:
                notification_service.send_inquiry_alert(
                    f"New appointment scheduled: {appointment['service_type']} for {appointment['client_name']} on {appointment['scheduled_date']}"
                )
            except Exception as e:
                logging.warning(f"Failed to send appointment notification: {e}")
        
        return jsonify({
            'success': True,
            'appointment': appointment,
            'message': f'Appointment created: {appointment["client_id"]}/{appointment["job_id"]}'
        })
        
    except Exception as e:
        logging.error(f"Error creating unified appointment: {e}")
        return jsonify({'error': 'Failed to create appointment'}), 500

@app.route('/admin/scheduler/appointments/<appointment_id>/update', methods=['POST'])
def update_unified_appointment(appointment_id):
    """Update unified appointment status"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        status = request.form.get('status')
        notes = request.form.get('notes')
        
        # Update status
        if status:
            success = unified_scheduler.update_appointment_status(
                appointment_id, status, session.get('user_name', 'Admin')
            )
            if not success:
                return jsonify({'error': 'Appointment not found'}), 404
        
        # Add notes if provided
        if notes:
            unified_scheduler.add_appointment_note(
                appointment_id, notes, session.get('user_name', 'Admin')
            )
        
        return jsonify({'success': True, 'message': 'Appointment updated successfully'})
        
    except Exception as e:
        logging.error(f"Error updating appointment {appointment_id}: {e}")
        return jsonify({'error': 'Failed to update appointment'}), 500

@app.route('/admin/scheduler/migrate', methods=['POST'])
def migrate_legacy_appointments():
    """Migrate legacy appointments to unified system"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Migrate existing legacy appointments
        migrated_count = unified_scheduler.migrate_legacy_appointments(appointments)
        
        # Clear legacy appointments after successful migration
        if migrated_count > 0:
            appointments.clear()
            logging.info(f"Cleared {migrated_count} legacy appointments after migration")
        
        return jsonify({
            'success': True,
            'migrated_count': migrated_count,
            'message': f'Successfully migrated {migrated_count} appointments to unified system'
        })
        
    except Exception as e:
        logging.error(f"Error migrating appointments: {e}")
        return jsonify({'error': 'Failed to migrate appointments'}), 500

@app.route('/api/unified/calendar/events')
def get_unified_calendar_events():
    """Get calendar events from unified scheduler"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        
        # Get events from unified scheduler
        events = unified_scheduler.get_calendar_events(start_date, end_date)
        
        return jsonify(events)
        
    except Exception as e:
        logging.error(f"Error getting unified calendar events: {e}")
        return jsonify({'error': 'Failed to load calendar events'}), 500

@app.route('/admin/scheduler/business-hours')
def business_hours_management():
    """Business hours configuration"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    business_hours = unified_scheduler.get_business_hours()
    return render_template('admin/business_hours.html', business_hours=business_hours)

@app.route('/admin/scheduler/business-hours/update', methods=['POST'])
def update_business_hours():
    """Update business hours configuration"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get form data and build hours configuration
        hours_data = {
            'monday': {
                'start': request.form.get('monday_start', '07:00'),
                'end': request.form.get('monday_end', '17:00'),
                'enabled': request.form.get('monday_enabled') == 'on'
            },
            'tuesday': {
                'start': request.form.get('tuesday_start', '07:00'),
                'end': request.form.get('tuesday_end', '17:00'),
                'enabled': request.form.get('tuesday_enabled') == 'on'
            },
            'wednesday': {
                'start': request.form.get('wednesday_start', '07:00'),
                'end': request.form.get('wednesday_end', '17:00'),
                'enabled': request.form.get('wednesday_enabled') == 'on'
            },
            'thursday': {
                'start': request.form.get('thursday_start', '07:00'),
                'end': request.form.get('thursday_end', '17:00'),
                'enabled': request.form.get('thursday_enabled') == 'on'
            },
            'friday': {
                'start': request.form.get('friday_start', '07:00'),
                'end': request.form.get('friday_end', '17:00'),
                'enabled': request.form.get('friday_enabled') == 'on'
            },
            'saturday': {
                'start': request.form.get('saturday_start', '08:00'),
                'end': request.form.get('saturday_end', '15:00'),
                'enabled': request.form.get('saturday_enabled') == 'on'
            },
            'sunday': {
                'start': request.form.get('sunday_start', '08:00'),
                'end': request.form.get('sunday_end', '15:00'),
                'enabled': request.form.get('sunday_enabled') == 'on'
            },
            'lunch_break': {
                'start': request.form.get('lunch_start', '12:00'),
                'end': request.form.get('lunch_end', '13:00'),
                'enabled': request.form.get('lunch_enabled') == 'on'
            },
            'timezone': 'Pacific/Honolulu',
            'buffer_minutes': int(request.form.get('buffer_minutes', 30))
        }
        
        success = unified_scheduler.update_business_hours(hours_data)
        
        if success:
            flash('Business hours updated successfully!', 'success')
        else:
            flash('Error updating business hours.', 'error')
            
        return redirect(url_for('business_hours_management'))
        
    except Exception as e:
        logging.error(f"Error updating business hours: {e}")
        flash('Error updating business hours.', 'error')
        return redirect(url_for('business_hours_management'))

@app.route('/api/scheduler/validate-time', methods=['POST'])
def validate_appointment_time():
    """API endpoint to validate appointment time for conflicts and business hours"""
    try:
        data = request.get_json()
        date_str = data.get('date')
        time_str = data.get('time')
        duration = int(data.get('duration', 120))
        exclude_id = data.get('exclude_appointment_id')
        
        validation = unified_scheduler.validate_appointment_time(
            date_str, time_str, duration, exclude_id
        )
        
        return jsonify(validation)
        
    except Exception as e:
        logging.error(f"Error validating appointment time: {e}")
        return jsonify({
            'valid': False,
            'reason': f'Validation error: {str(e)}',
            'type': 'system_error'
        }), 500

@app.route('/api/scheduler/available-times/<date>')
def get_available_times(date):
    """Get available appointment times for a specific date"""
    try:
        duration = int(request.args.get('duration', 120))
        available_times = unified_scheduler._get_available_times(date, duration)
        
        return jsonify({
            'date': date,
            'available_times': available_times,
            'business_hours': unified_scheduler.get_business_hours()
        })
        
    except Exception as e:
        logging.error(f"Error getting available times: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/reschedule/<appointment_id>', methods=['POST'])
def reschedule_appointment_api(appointment_id):
    """Reschedule appointment via API"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        new_date = data.get('new_date')
        new_time = data.get('new_time')
        reason = data.get('reason', '')
        
        result = unified_scheduler.reschedule_appointment(
            appointment_id, new_date, new_time, reason
        )
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error rescheduling appointment: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/recurring', methods=['POST'])
def create_recurring_appointment():
    """Create recurring appointments"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        base_appointment = data.get('base_appointment')
        recurring_config = data.get('recurring_config')
        
        # Create the base appointment first
        appointment = unified_scheduler.create_appointment(base_appointment)
        
        # Create recurring appointments
        recurring_appointments = unified_scheduler.create_recurring_appointments(
            appointment, recurring_config
        )
        
        return jsonify({
            'success': True,
            'base_appointment': appointment,
            'recurring_appointments': recurring_appointments,
            'total_created': len(recurring_appointments) + 1
        })
        
    except Exception as e:
        logging.error(f"Error creating recurring appointments: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/reminders/<int:hours_ahead>')
def get_appointment_reminders_api(hours_ahead):
    """Get appointments needing reminders"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        reminders = unified_scheduler.get_appointment_reminders(hours_ahead)
        return jsonify(reminders)
        
    except Exception as e:
        logging.error(f"Error getting reminders: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/reminder-sent/<appointment_id>', methods=['POST'])
def mark_reminder_sent_api(appointment_id):
    """Mark reminder as sent"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        reminder_type = data.get('reminder_type')
        hours_ahead = data.get('hours_ahead')
        
        unified_scheduler.mark_reminder_sent(appointment_id, reminder_type, hours_ahead)
        
        return jsonify({'success': True})
        
    except Exception as e:
        logging.error(f"Error marking reminder sent: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/staff-workload')
def get_staff_workload_api():
    """Get staff workload analysis"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        days = int(request.args.get('days', 7))
        workload = unified_scheduler.get_staff_workload(days)
        
        return jsonify(workload)
        
    except Exception as e:
        logging.error(f"Error getting staff workload: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/scheduler/advanced')
def advanced_scheduler_dashboard():
    """Advanced scheduler with drag-and-drop and workload management"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # Get upcoming appointments
        week_data = unified_scheduler.get_weekly_schedule()
        
        # Get staff workload
        staff_workload = unified_scheduler.get_staff_workload(14)  # 2 weeks
        
        # Get pending reminders
        reminders_24h = unified_scheduler.get_appointment_reminders(24)
        reminders_2h = unified_scheduler.get_appointment_reminders(2)
        
        # Get business hours for validation
        business_hours = unified_scheduler.get_business_hours()
        
        return render_template('admin/advanced_scheduler.html',
                             week_data=week_data,
                             staff_workload=staff_workload,
                             reminders_24h=reminders_24h,
                             reminders_2h=reminders_2h,
                             business_hours=business_hours)
                             
    except Exception as e:
        logging.error(f"Error loading advanced scheduler: {e}")
        flash('Error loading advanced scheduler.', 'error')
        return redirect(url_for('admin_dashboard'))

# ===============================
# MULTI-PROJECT CLIENT MANAGEMENT
# ===============================

@app.route('/admin/multi_project_clients')
def admin_multi_project_clients():
    """Admin view for managing clients with multiple projects"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # Get clients with multiple projects
        multi_project_clients = unified_scheduler.get_clients_with_multiple_projects()
        
        return render_template('admin/multi_project_clients.html',
                             clients=multi_project_clients)
        
    except Exception as e:
        logging.error(f"Error loading multi-project clients: {e}")
        flash('Error loading client data.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/client/<client_id>/projects')
def admin_client_project_history(client_id):
    """View detailed project history for a specific client"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # Get client project history
        project_history = unified_scheduler.get_client_project_history(client_id)
        
        if not project_history:
            flash('No projects found for this client.', 'warning')
            return redirect(url_for('admin_multi_project_clients'))
        
        # Get client basic info from first project
        client_info = {
            'client_id': client_id,
            'client_name': project_history[0].get('client_name', 'Unknown'),
            'project_count': len(project_history)
        }
        
        return render_template('admin/client_project_history.html',
                             client=client_info,
                             projects=project_history)
        
    except Exception as e:
        logging.error(f"Error loading client project history: {e}")
        flash('Error loading project history.', 'error')
        return redirect(url_for('admin_multi_project_clients'))

@app.route('/api/client/<client_id>/project_history')
def get_client_project_history_api(client_id):
    """API endpoint to get client project history"""
    if not session.get('portal_authenticated'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Verify client can access this data
    session_client_id = session.get('client_id')
    if session_client_id != client_id and session.get('access_level') != 'staff':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get project history for this client
        project_history = unified_scheduler.get_client_project_history(client_id)
        
        # Format for API response
        formatted_projects = []
        for project in project_history:
            formatted_projects.append({
                'job_id': project['job_id'],
                'project_name': project['project_name'],
                'service_type': project['service_type'],
                'status': project['status'],
                'scheduled_date': project['scheduled_date'],
                'scheduled_time': project['scheduled_time'],
                'created_at': project['created_at'],
                'notes': project['notes'],
                'project_phase': project['project_phase']
            })
        
        return jsonify({
            'client_id': client_id,
            'projects': formatted_projects,
            'total_projects': len(formatted_projects)
        })
        
    except Exception as e:
        logging.error(f"Error getting client project history: {e}")
        return jsonify({'error': 'Failed to load project history'}), 500

# Advanced Scheduling API Routes
@app.route('/api/scheduler/assign-staff/<appointment_id>', methods=['POST'])
def assign_staff_to_job_api(appointment_id):
    """Assign staff to specific job"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        staff_ids = data.get('staff_ids', [])
        team_name = data.get('team_name', '')
        
        result = unified_scheduler.assign_job_to_staff(appointment_id, staff_ids, team_name)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error assigning staff to job: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/block-availability', methods=['POST'])
def block_staff_availability_api():
    """Block staff availability for time off or sick days"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        staff_id = data.get('staff_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        reason = data.get('reason', 'Time off')
        
        result = unified_scheduler.block_staff_availability(staff_id, start_date, end_date, reason)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error blocking staff availability: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/staff-schedule/<staff_id>')
def get_staff_schedule_api(staff_id):
    """Get schedule for specific staff member"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        days = int(request.args.get('days', 7))
        schedule = unified_scheduler.get_staff_schedule(staff_id, days)
        return jsonify(schedule)
        
    except Exception as e:
        logging.error(f"Error getting staff schedule: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/update-status/<appointment_id>', methods=['POST'])
def update_job_status_api(appointment_id):
    """Update job status with workflow tracking"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        status = data.get('status')
        notes = data.get('notes', '')
        
        result = unified_scheduler.update_job_status(appointment_id, status, notes)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error updating job status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/add-checklist/<appointment_id>', methods=['POST'])
def add_job_checklist_api(appointment_id):
    """Add materials or prep task checklist to job"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        checklist_items = data.get('checklist_items', [])
        
        result = unified_scheduler.add_job_checklist(appointment_id, checklist_items)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error adding job checklist: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/reporting')
def get_job_reporting_api():
    """Get comprehensive job reporting data"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        reporting_data = unified_scheduler.get_job_reporting_data(start_date, end_date)
        return jsonify(reporting_data)
        
    except Exception as e:
        logging.error(f"Error getting job reporting data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/color-coded-events')
def get_color_coded_events_api():
    """Get calendar events with color coding by job type"""
    try:
        events = unified_scheduler.get_color_coded_events()
        return jsonify(events)
        
    except Exception as e:
        logging.error(f"Error getting color-coded events: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/workflow-dashboard')
def workflow_management_dashboard():
    """Comprehensive workflow management dashboard"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # Get current week appointments
        week_data = unified_scheduler.get_weekly_schedule()
        
        # Get job reporting data for last 30 days
        reporting_data = unified_scheduler.get_job_reporting_data()
        
        # Get staff workload
        staff_workload = unified_scheduler.get_staff_workload(14)
        
        # Get pending reminders
        reminders_24h = unified_scheduler.get_appointment_reminders(24)
        reminders_2h = unified_scheduler.get_appointment_reminders(2)
        
        # Get overdue jobs
        appointments = unified_scheduler._load_appointments()
        hawaii_now = datetime.now(unified_scheduler.hawaii_tz)
        overdue_jobs = []
        
        for appointment in appointments:
            if appointment.get('status') in ['work_in_progress', 'estimate_sent']:
                appointment_date = datetime.strptime(appointment['scheduled_date'], '%Y-%m-%d')
                appointment_date = unified_scheduler.hawaii_tz.localize(appointment_date)
                
                # Jobs are overdue if they're past due date and not completed
                if appointment_date < hawaii_now:
                    overdue_jobs.append(appointment)
        
        return render_template('admin/workflow_dashboard.html',
                             week_data=week_data,
                             reporting_data=reporting_data,
                             staff_workload=staff_workload,
                             reminders_24h=reminders_24h,
                             reminders_2h=reminders_2h,
                             overdue_jobs=overdue_jobs)
                             
    except Exception as e:
        logging.error(f"Error loading workflow dashboard: {e}")
        flash('Error loading workflow dashboard.', 'error')
        return redirect(url_for('admin_dashboard'))

# Job Tracking API Routes
@app.route('/admin/workflow-automation')
def workflow_automation_dashboard():
    """Comprehensive workflow automation and business process management"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access workflow automation.', 'error')
        return redirect(url_for('admin_login'))
    
    try:
        from workflow_automation_service import WorkflowAutomationService
        workflow_service = WorkflowAutomationService()
        
        # Get workflow analytics
        analytics = workflow_service.get_workflow_analytics()
        
        # Process any pending automated actions
        automation_results = workflow_service.process_automated_actions()
        
        # Get active workflows
        workflows = workflow_service._load_json_file('workflow_tracking.json')
        active_workflows = [w for w in workflows if w.get('status') == 'active']
        
        # Get pending actions
        scheduled_actions = workflow_service._load_json_file('scheduled_actions.json')
        pending_actions = [a for a in scheduled_actions if a.get('status') == 'pending']
        
        return render_template('admin/workflow_automation.html',
                             analytics=analytics,
                             automation_results=automation_results,
                             active_workflows=active_workflows,
                             pending_actions=pending_actions,
                             workflow_stages=workflow_service.workflow_stages)
                             
    except Exception as e:
        logging.error(f"Error in workflow automation dashboard: {e}")
        flash('Workflow automation temporarily unavailable. Please try again.', 'warning')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/job-tracking')
def job_tracking_dashboard():
    """Job tracking and payment management dashboard"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        from job_tracking_service import job_tracking_service
        
        # Get comprehensive data
        job_records = job_tracking_service.get_job_records()
        quote_history = job_tracking_service.get_quote_history()
        payment_logs = job_tracking_service.get_payment_logs()
        reporting_data = job_tracking_service.get_reporting_data()
        
        return render_template('admin/job_tracking_dashboard.html',
                             job_records=job_records,
                             quote_history=quote_history,
                             payment_logs=payment_logs,
                             reporting_data=reporting_data)
                             
    except Exception as e:
        logging.error(f"Error loading job tracking dashboard: {e}")
        flash('Error loading job tracking dashboard.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/api/job-tracking/create-job', methods=['POST'])
def create_job_record_api():
    """Create new job record"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from job_tracking_service import job_tracking_service
        
        data = request.get_json()
        result = job_tracking_service.create_job_record(data)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error creating job record: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/job-tracking/create-quote', methods=['POST'])
def create_quote_record_api():
    """Create new quote record"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from job_tracking_service import job_tracking_service
        
        data = request.get_json()
        result = job_tracking_service.create_quote_record(data)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error creating quote record: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/job-tracking/log-payment', methods=['POST'])
def log_payment_api():
    """Log manual payment received"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from job_tracking_service import job_tracking_service
        
        data = request.get_json()
        result = job_tracking_service.log_payment(data)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error logging payment: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/job-tracking/log-materials', methods=['POST'])
def log_materials_api():
    """Log materials used for job"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from job_tracking_service import job_tracking_service
        
        data = request.get_json()
        result = job_tracking_service.log_materials(data)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error logging materials: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/job-tracking/log-labor', methods=['POST'])
def log_labor_api():
    """Log labor hours for job"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from job_tracking_service import job_tracking_service
        
        data = request.get_json()
        result = job_tracking_service.log_labor(data)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error logging labor: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/job-tracking/job-summary/<job_id>')
def get_job_summary_api(job_id):
    """Get comprehensive job summary"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from job_tracking_service import job_tracking_service
        
        result = job_tracking_service.get_job_summary(job_id)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error getting job summary: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/job-tracking/reporting')
def get_job_tracking_reporting():
    """Get job tracking reporting data"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from job_tracking_service import job_tracking_service
        
        reporting_data = job_tracking_service.get_reporting_data()
        return jsonify(reporting_data)
        
    except Exception as e:
        logging.error(f"Error getting reporting data: {e}")
        return jsonify({'error': str(e)}), 500

# Financial Reporting API Routes
@app.route('/admin/financial-reports')
def financial_reports_dashboard():
    """Financial reporting dashboard with P&L, job costing, and tax reports"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        from financial_reporting_service import financial_reporting_service
        
        # Get current year data for overview
        current_year = datetime.now().year
        start_date = f"{current_year}-01-01"
        end_date = f"{current_year}-12-31"
        
        # Generate key reports
        profit_loss = financial_reporting_service.generate_profit_loss_statement(start_date, end_date)
        invoice_report = financial_reporting_service.generate_invoice_report()
        client_summary = financial_reporting_service.generate_client_payment_summary()
        tax_summary = financial_reporting_service.generate_tax_summary_report(current_year)
        
        return render_template('admin/financial_reports_dashboard.html',
                             profit_loss=profit_loss,
                             invoice_report=invoice_report,
                             client_summary=client_summary,
                             tax_summary=tax_summary,
                             current_year=current_year)
                             
    except Exception as e:
        logging.error(f"Error loading financial reports dashboard: {e}")
        flash('Error loading financial reports dashboard.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/api/financial-reports/profit-loss')
def generate_profit_loss_api():
    """Generate profit and loss statement"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from financial_reporting_service import financial_reporting_service
        
        start_date = request.args.get('start_date', f"{datetime.now().year}-01-01")
        end_date = request.args.get('end_date', f"{datetime.now().year}-12-31")
        
        result = financial_reporting_service.generate_profit_loss_statement(start_date, end_date)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error generating P&L statement: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/financial-reports/job-costing')
def generate_job_costing_api():
    """Generate job costing report"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from financial_reporting_service import financial_reporting_service
        
        job_id = request.args.get('job_id')
        result = financial_reporting_service.generate_job_costing_report(job_id)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error generating job costing report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/financial-reports/invoice-report')
def generate_invoice_report_api():
    """Generate invoice status and payment tracking report"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from financial_reporting_service import financial_reporting_service
        
        status_filter = request.args.get('status')
        result = financial_reporting_service.generate_invoice_report(status_filter)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error generating invoice report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/financial-reports/client-payments')
def generate_client_payment_summary_api():
    """Generate client payment summary report"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from financial_reporting_service import financial_reporting_service
        
        client_filter = request.args.get('client')
        result = financial_reporting_service.generate_client_payment_summary(client_filter)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error generating client payment summary: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/financial-reports/materials')
def generate_materials_report_api():
    """Generate materials and supplies report"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from financial_reporting_service import financial_reporting_service
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        date_range = (start_date, end_date) if start_date and end_date else None
        result = financial_reporting_service.generate_materials_report(date_range)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error generating materials report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/financial-reports/tax-summary')
def generate_tax_summary_api():
    """Generate tax summary report"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from financial_reporting_service import financial_reporting_service
        
        tax_year = int(request.args.get('year', datetime.now().year))
        result = financial_reporting_service.generate_tax_summary_report(tax_year)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error generating tax summary report: {e}")
        return jsonify({'error': str(e)}), 500