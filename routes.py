import os
import logging
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app
from models import HandymanStorage
from ai_service import ai_service
from notification_service import notification_service, NotificationService
import pytz

# Initialize handyman storage
handyman_storage = HandymanStorage()

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
        phone = request.form.get('phone', '').strip()
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

            # Send inquiry alert to admin
            notification_service.send_inquiry_alert(
                inquiry_type="consultation",
                customer_name=name,
                phone_number=phone,
                email=email,
                service_type=service
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
        phone = request.form.get('contact_phone', '').strip()
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

            # Send inquiry alert to admin
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

    return render_template('admin_login.html')

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
        appointment_date = datetime.strptime(appointment['date'], '%Y-%m-%d')
        if start_of_week <= appointment_date < start_of_week + timedelta(days=7):
            week_appointments.append(appointment)

    # Business Analytics
    total_revenue_estimate = sum([
        float(req.budget_range.split('-')[0].replace('$', '').replace(',', '')) 
        if req.budget_range and '-' in req.budget_range 
        else 500.0 
        for req in service_requests if req.status == 'completed'
    ])
    
    # Customer satisfaction metrics
    pending_requests = [req for req in service_requests if req.status == 'pending']
    urgent_requests = [req for req in service_requests if getattr(req, 'priority', 'medium') == 'high']
    
    # Monthly trends
    current_month = hawaii_now.month
    monthly_requests = [req for req in service_requests if datetime.strptime(req.preferred_date or hawaii_now.strftime('%Y-%m-%d'), '%Y-%m-%d').month == current_month]
    
    # Lead source analysis
    referral_stats = handyman_storage.get_referral_stats()
    membership_stats = handyman_storage.get_membership_stats()

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
                         # Business analytics
                         total_revenue_estimate=total_revenue_estimate,
                         pending_requests=pending_requests,
                         urgent_requests=urgent_requests,
                         monthly_requests=monthly_requests,
                         referral_stats=referral_stats,
                         membership_stats=membership_stats)

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

@app.route('/twilio-config')
def twilio_config():
    """Twilio SendGrid configuration page"""
    return render_template('twilio_config.html')

@app.route('/api/test-sms', methods=['POST'])
def test_sms():
    """Test SMS functionality with provided credentials"""
    try:
        data = request.get_json()
        
        # Create temporary notification service with test credentials
        from notification_service import NotificationService
        test_service = NotificationService()
        test_service.twilio_sid = data.get('twilio_sid')
        test_service.twilio_token = data.get('twilio_token') 
        test_service.twilio_phone = data.get('twilio_phone')
        
        if test_service.twilio_sid and test_service.twilio_token:
            from twilio.rest import Client
            test_service.twilio_client = Client(test_service.twilio_sid, test_service.twilio_token)
        
        # Send test SMS
        sms_sent = test_service.send_spank_buck_sms(
            to_phone=data.get('phone'),
            amount=5,
            reason='testing Twilio SMS integration',
            customer_name='Test User'
        )
        
        return jsonify({'success': sms_sent})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-sendgrid', methods=['POST'])
def test_sendgrid():
    """Test SendGrid email functionality with provided credentials"""
    try:
        data = request.get_json()
        
        # Create temporary notification service with test credentials
        from notification_service import NotificationService
        test_service = NotificationService()
        test_service.sendgrid_key = data.get('sendgrid_key')
        
        # Send test email
        email_sent = test_service.send_twilio_sendgrid_email(
            to_email=data.get('email'),
            amount=5,
            reason='testing SendGrid email integration',
            customer_name='Test User'
        )
        
        return jsonify({'success': email_sent})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/check-twilio-status')
def check_twilio_status():
    """Check current Twilio and SendGrid configuration status"""
    twilio_configured = bool(os.environ.get('TWILIO_ACCOUNT_SID') and os.environ.get('TWILIO_AUTH_TOKEN'))
    sendgrid_configured = bool(os.environ.get('SENDGRID_API_KEY'))
    
    return jsonify({
        'twilio_configured': twilio_configured,
        'sendgrid_configured': sendgrid_configured,
        'integration_ready': twilio_configured and sendgrid_configured,
        'rewards_enabled': twilio_configured or sendgrid_configured
    })

@app.route('/api/test-inquiry-alert', methods=['POST'])
def test_inquiry_alert():
    """Test the inquiry alert system manually"""
    try:
        data = request.get_json()
        phone = data.get('phone', '+18084529779')
        
        # Test inquiry alert
        alert_sent = notification_service.send_inquiry_alert(
            inquiry_type="contact",
            customer_name="Test Customer",
            phone_number="+18085551234",
            email="test@example.com"
        )
        
        if alert_sent:
            return jsonify({'success': True, 'message': f'Test alert sent to {phone}'})
        else:
            return jsonify({'success': False, 'error': 'Failed to send alert - check Twilio credentials'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/save-twilio-config', methods=['POST'])
def save_twilio_config():
    """Save Twilio configuration (for demo purposes - in production use environment variables)"""
    try:
        data = request.get_json()
        
        # In a real deployment, these would be set as environment variables
        # For testing purposes, we'll validate the credentials work
        test_success = True
        
        if data.get('twilio_sid') and data.get('twilio_token'):
            try:
                from twilio.rest import Client
                client = Client(data.get('twilio_sid'), data.get('twilio_token'))
                # Validate credentials by fetching account info
                account = client.api.accounts(data.get('twilio_sid')).fetch()
                test_success = True
            except Exception as e:
                return jsonify({'success': False, 'error': f'Twilio validation failed: {str(e)}'})
        
        return jsonify({'success': test_success, 'message': 'Configuration validated successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

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

@app.route('/admin/analytics-dashboard')
def analytics_dashboard():
    """Business analytics and performance metrics dashboard"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access analytics.', 'error')
        return redirect(url_for('admin_login'))

    service_requests = handyman_storage.get_all_service_requests()
    contact_messages = handyman_storage.get_all_contact_messages()
    referrals = handyman_storage.get_all_referrals()
    memberships = handyman_storage.get_all_memberships()

    # Lead source analysis
    lead_sources = {}
    for request in service_requests:
        source = getattr(request, 'lead_source', 'Direct Website')
        lead_sources[source] = lead_sources.get(source, 0) + 1

    # Conversion funnel analysis
    total_inquiries = len(contact_messages) + len(service_requests)
    consultation_requests = len(service_requests)
    completed_jobs = len([req for req in service_requests if req.status == 'completed'])
    
    conversion_rate = (completed_jobs / total_inquiries * 100) if total_inquiries > 0 else 0
    
    # Revenue analytics
    total_revenue = sum([
        float(req.budget_range.split('-')[0].replace('$', '').replace(',', '')) 
        if req.budget_range and '-' in req.budget_range 
        else 750.0 
        for req in service_requests if req.status == 'completed'
    ])

    # Service type popularity
    service_popularity = {}
    for request in service_requests:
        service = request.service
        service_popularity[service] = service_popularity.get(service, 0) + 1

    # Monthly performance trends
    hawaii_now = get_hawaii_time()
    monthly_trends = []
    for i in range(6):
        month_date = hawaii_now - timedelta(days=30 * i)
        month_requests = [
            req for req in service_requests 
            if req.preferred_date and datetime.strptime(req.preferred_date, '%Y-%m-%d').month == month_date.month
        ]
        monthly_trends.append({
            'month': month_date.strftime('%B'),
            'requests': len(month_requests),
            'completed': len([req for req in month_requests if req.status == 'completed']),
            'revenue': sum([
                float(req.budget_range.split('-')[0].replace('$', '').replace(',', '')) 
                if req.budget_range and '-' in req.budget_range 
                else 750.0 
                for req in month_requests if req.status == 'completed'
            ])
        })

    return render_template('admin/analytics_dashboard.html',
                         lead_sources=lead_sources,
                         conversion_rate=conversion_rate,
                         total_revenue=total_revenue,
                         service_popularity=service_popularity,
                         monthly_trends=monthly_trends,
                         total_inquiries=total_inquiries,
                         consultation_requests=consultation_requests,
                         completed_jobs=completed_jobs,
                         referrals=referrals,
                         memberships=memberships)

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
            'phone': request.form['phone'],
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
        phone = data.get('phone')
        service_type = data.get('serviceType', '')
        price = float(data.get('price', 0))
        
        # Validate required fields
        if not all([customer, phone, service_type, price]):
            return jsonify({'error': 'Missing required fields'}), 400
        
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
        
        # Create quote items based on service type
        from models import QuoteItem
        
        # Generate appropriate quote items based on service type and price
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
                'phone': '(808) 555-0000',  # Default phone for API invoices
                'address': '',
                'notes': f'Created via API for invoice {job_id}' if job_id else 'Created via API for invoice',
                'tags': ['api_generated', 'invoice_only']
            }
            contact = handyman_storage.add_contact(contact_data)
        
        # Create a basic quote first (required for invoice generation)
        from models import QuoteItem
        
        # Calculate subtotal from total (reverse Hawaii tax calculation)
        hawaii_tax_rate = 0.04712
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