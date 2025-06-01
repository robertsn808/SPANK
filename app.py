import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "triton-concrete-coating-secret-key-2025")

# In-memory storage for bookings and admin credentials
bookings = []
admin_credentials = {
    'username': 'tccadmin808',
    'password_hash': generate_password_hash('Money$$')
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/reviews')
def reviews():
    return render_template('reviews.html')

@app.route('/consultation', methods=['GET', 'POST'])
def consultation():
    if request.method == 'POST':
        booking = {
            'id': len(bookings) + 1,
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'service': request.form.get('service'),
            'property_type': request.form.get('property_type'),
            'square_footage': request.form.get('square_footage'),
            'preferred_date': request.form.get('preferred_date'),
            'preferred_time': request.form.get('preferred_time'),
            'consultation_type': request.form.get('consultation_type'),
            'message': request.form.get('message'),
            'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'pending'
        }
        bookings.append(booking)
        flash('Your consultation request has been submitted successfully! We will contact you within 24 hours.', 'success')
        return redirect(url_for('consultation'))
    
    return render_template('consultation.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if (username == admin_credentials['username'] and 
            check_password_hash(admin_credentials['password_hash'], password)):
            session['admin_logged_in'] = True
            flash('Successfully logged in!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Please log in to access the admin dashboard.', 'error')
        return redirect(url_for('admin_login'))
    
    return render_template('admin_dashboard.html', bookings=bookings)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Successfully logged out!', 'success')
    return redirect(url_for('index'))

@app.route('/admin/update_booking/<int:booking_id>', methods=['POST'])
def update_booking(booking_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    status = request.form.get('status')
    for booking in bookings:
        if booking['id'] == booking_id:
            booking['status'] = status
            flash(f'Booking #{booking_id} status updated to {status}', 'success')
            break
    
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
