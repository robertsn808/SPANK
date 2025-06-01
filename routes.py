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
                'message': message
            })
            
            flash('Thank you! Your consultation request has been submitted. We will contact you within 24 hours.', 'success')
            logging.info(f"New booking created with ID: {booking_id}")
            return redirect(url_for('consultation'))
            
        except Exception as e:
            logging.error(f"Error creating booking: {e}")
            flash('There was an error submitting your request. Please try again or call us directly.', 'error')
    
    return render_template('consultation.html')

@app.route('/contact')
def contact():
    """Contact page with business information"""
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
    
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard showing all bookings"""
    if not session.get('admin_logged_in'):
        flash('Please log in to access the admin dashboard.', 'error')
        return redirect(url_for('admin_login'))
    
    bookings = booking_storage.get_all_bookings()
    return render_template('admin/dashboard.html', bookings=bookings)

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
        booking_storage.update_booking_status(booking_id, 'completed')
        flash('Booking marked as completed.', 'success')
    except Exception as e:
        logging.error(f"Error updating booking {booking_id}: {e}")
        flash('Error updating booking status.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/booking/<int:booking_id>/delete')
def delete_booking(booking_id):
    """Delete a booking"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        booking_storage.delete_booking(booking_id)
        flash('Booking deleted successfully.', 'success')
    except Exception as e:
        logging.error(f"Error deleting booking {booking_id}: {e}")
        flash('Error deleting booking.', 'error')
    
    return redirect(url_for('admin_dashboard'))
