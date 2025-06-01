# Simple data models for the application
# Since we're using in-memory storage, this file defines the structure

class Booking:
    def __init__(self, name, email, phone, service, property_type, square_footage, 
                 preferred_date, preferred_time, consultation_type, message):
        self.name = name
        self.email = email
        self.phone = phone
        self.service = service
        self.property_type = property_type
        self.square_footage = square_footage
        self.preferred_date = preferred_date
        self.preferred_time = preferred_time
        self.consultation_type = consultation_type
        self.message = message
        self.status = 'pending'
        self.submitted_at = None

class Admin:
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash
