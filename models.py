from datetime import datetime
import logging

class BookingStorage:
    """Simple in-memory storage for consultation bookings"""
    
    def __init__(self):
        self.bookings = {}
        self.next_id = 1
    
    def add_booking(self, booking_data):
        """Add a new booking and return the booking ID"""
        booking_id = self.next_id
        self.next_id += 1
        
        # Add metadata
        booking_data['id'] = booking_id
        booking_data['created_at'] = datetime.now()
        booking_data['status'] = 'pending'
        
        self.bookings[booking_id] = booking_data
        logging.info(f"Booking {booking_id} created for {booking_data.get('name', 'Unknown')}")
        return booking_id
    
    def get_booking(self, booking_id):
        """Get a specific booking by ID"""
        return self.bookings.get(booking_id)
    
    def get_all_bookings(self):
        """Get all bookings sorted by creation date (newest first)"""
        bookings_list = list(self.bookings.values())
        bookings_list.sort(key=lambda x: x['created_at'], reverse=True)
        return bookings_list
    
    def update_booking_status(self, booking_id, status):
        """Update the status of a booking"""
        if booking_id in self.bookings:
            self.bookings[booking_id]['status'] = status
            self.bookings[booking_id]['updated_at'] = datetime.now()
            logging.info(f"Booking {booking_id} status updated to {status}")
        else:
            raise ValueError(f"Booking {booking_id} not found")
    
    def delete_booking(self, booking_id):
        """Delete a booking"""
        if booking_id in self.bookings:
            deleted_booking = self.bookings.pop(booking_id)
            logging.info(f"Booking {booking_id} deleted for {deleted_booking.get('name', 'Unknown')}")
        else:
            raise ValueError(f"Booking {booking_id} not found")
