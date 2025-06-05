from flask import render_template, request, redirect, url_for, session, flash
from app import app
from models import BookingStorage
import logging

# Initialize booking storage
booking_storage = BookingStorage()

# Admin credentials
ADMIN_USERNAME = "tccadmin808"
ADMIN_PASSWORD = "Money$$"

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
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            logging.info("Admin login successful")
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
            logging.warning(f"Failed admin login attempt for username: {username}")
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard showing all bookings and contact messages"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access the admin dashboard.', 'error')
        return redirect(url_for('admin_login'))
    
    bookings = booking_storage.get_all_bookings()
    contact_messages = booking_storage.get_all_contact_messages()
    return render_template('admin_dashboard.html', bookings=bookings, contact_messages=contact_messages)

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
