
from datetime import datetime

class Booking:
    def __init__(self, name, email, phone, service, project_type=None, preferred_date=None, 
                 preferred_time=None, consultation_type=None, message=None, square_footage=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.service = service
        self.project_type = project_type
        self.preferred_date = preferred_date
        self.preferred_time = preferred_time
        self.consultation_type = consultation_type
        self.message = message
        self.square_footage = square_footage
        self.status = 'pending'
        self.submitted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

class BookingStorage:
    def __init__(self):
        self.bookings = []
        self.next_id = 1
    
    def add_booking(self, booking_data):
        booking = Booking(**booking_data)
        booking.id = self.next_id
        self.bookings.append(booking)
        self.next_id += 1
        return booking.id
    
    def get_all_bookings(self):
        return self.bookings
    
    def update_booking_status(self, booking_id, status):
        for booking in self.bookings:
            if booking.id == booking_id:
                booking.status = status
                return True
        return False
    
    def delete_booking(self, booking_id):
        self.bookings = [b for b in self.bookings if b.id != booking_id]
        return True

class Admin:
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash
