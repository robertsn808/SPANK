from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app
from models import HandymanStorage
from ai_service import ai_service
from datetime import datetime, timedelta
import pytz
import logging

# Initialize handyman storage
handyman_storage = HandymanStorage()

# Additional storage for contact messages, appointments, and staff
contact_messages = []
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
ADMIN_USERNAME = "tccadmin808"
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

@app.route('/gallery')
def gallery():
    """Gallery page showcasing work samples"""
    return render_template('gallery.html')

@app.route('/reviews')
def reviews():
    """Reviews page with customer testimonials"""
    return render_template('reviews.html')

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
            booking_id = booking_storage.add_booking({
                'name': name,
                'email': email,
                'phone': phone,
                'service': service,
                'project_type': project_type,
                'consultation_type': consultation_type,
                'preferred_date': preferred_date,
                'preferred_time': preferred_time,
                'message': message,
                'square_footage': square_footage
            })
            
            flash('Thank you! Your consultation request has been submitted. We will contact you within 24 hours.', 'success')
            logging.info(f"New booking created with ID: {booking_id}")
            return redirect(url_for('consultation'))
            
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
            message_id = booking_storage.add_contact_message({
                'name': name,
                'email': email,
                'phone': phone,
                'subject': subject,
                'message': message
            })
            
            flash('Thank you! Your message has been sent. We will respond within 24 hours.', 'success')
            logging.info(f"New contact message created with ID: {message_id}")
            return redirect(url_for('contact'))
            
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

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard showing all bookings, contact messages, and weekly calendar"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access the admin dashboard.', 'error')
        return redirect(url_for('admin_login'))
    
    bookings = booking_storage.get_all_bookings()
    contact_messages = booking_storage.get_all_contact_messages()
    
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
    
    return render_template('admin_dashboard.html', 
                         bookings=bookings, 
                         contact_messages=contact_messages,
                         week_dates=week_dates,
                         week_appointments=week_appointments,
                         staff_members=staff_members,
                         staff_logins=staff_logins,
                         today=hawaii_now.strftime('%Y-%m-%d'),
                         user_role=session.get('user_role', 'admin'),
                         user_name=session.get('user_name', 'Admin'))

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
        success = booking_storage.update_booking_status(booking_id, 'completed')
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
            booking_storage.update_booking_status(booking_id, status)
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
        booking_exists = any(b.id == booking_id for b in booking_storage.get_all_bookings())
        if booking_exists:
            booking_storage.delete_booking(booking_id)
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
        success = booking_storage.update_message_status(message_id, 'read')
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
        message_exists = any(m.id == message_id for m in booking_storage.get_all_contact_messages())
        if message_exists:
            booking_storage.delete_contact_message(message_id)
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
        for b in booking_storage.get_all_bookings():
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
        
        # Update booking status
        booking_storage.update_booking_status(booking_id, "scheduled")
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

