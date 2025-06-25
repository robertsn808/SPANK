"""
Real-Time Availability Scheduler for SPANKKS Construction
Provides exact time slot booking with immediate confirmation
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pytz

class RealTimeScheduler:
    """Real-time availability checking and booking system"""
    
    def __init__(self):
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
        self.availability_file = 'data/real_time_availability.json'
        self.bookings_file = 'data/confirmed_bookings.json'
        self.business_hours = {
            'monday': {'start': '07:00', 'end': '17:00', 'lunch': {'start': '12:00', 'end': '13:00'}},
            'tuesday': {'start': '07:00', 'end': '17:00', 'lunch': {'start': '12:00', 'end': '13:00'}},
            'wednesday': {'start': '07:00', 'end': '17:00', 'lunch': {'start': '12:00', 'end': '13:00'}},
            'thursday': {'start': '07:00', 'end': '17:00', 'lunch': {'start': '12:00', 'end': '13:00'}},
            'friday': {'start': '07:00', 'end': '17:00', 'lunch': {'start': '12:00', 'end': '13:00'}},
            'saturday': {'start': '08:00', 'end': '15:00', 'lunch': None},
            'sunday': {'start': None, 'end': None, 'lunch': None}  # Closed
        }
        self.slot_duration = 60  # 60 minutes per appointment
        self.buffer_time = 30   # 30 minutes travel time between appointments
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Ensure data files exist"""
        os.makedirs('data', exist_ok=True)
        
        if not os.path.exists(self.availability_file):
            with open(self.availability_file, 'w') as f:
                json.dump({}, f, indent=2)
        
        if not os.path.exists(self.bookings_file):
            with open(self.bookings_file, 'w') as f:
                json.dump([], f, indent=2)
    
    def _load_bookings(self) -> List[Dict]:
        """Load existing bookings"""
        try:
            with open(self.bookings_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_booking(self, booking: Dict):
        """Save new booking"""
        bookings = self._load_bookings()
        bookings.append(booking)
        with open(self.bookings_file, 'w') as f:
            json.dump(bookings, f, indent=2)
    
    def _get_hawaii_time(self) -> datetime:
        """Get current Hawaii time"""
        return datetime.now(self.hawaii_tz)
    
    def _time_to_minutes(self, time_str: str) -> int:
        """Convert time string to minutes since midnight"""
        hour, minute = map(int, time_str.split(':'))
        return hour * 60 + minute
    
    def _minutes_to_time(self, minutes: int) -> str:
        """Convert minutes since midnight to time string"""
        hour = minutes // 60
        minute = minutes % 60
        return f"{hour:02d}:{minute:02d}"
    
    def get_available_dates(self, days_ahead: int = 14) -> List[str]:
        """Get list of available dates for the next N days"""
        available_dates = []
        current_date = self._get_hawaii_time().date()
        
        for i in range(1, days_ahead + 1):  # Start from tomorrow
            check_date = current_date + timedelta(days=i)
            day_name = check_date.strftime('%A').lower()
            
            # Check if business is open on this day
            if self.business_hours[day_name]['start'] is not None:
                # Check if there are any available slots
                if self._has_available_slots(check_date.strftime('%Y-%m-%d')):
                    available_dates.append(check_date.strftime('%Y-%m-%d'))
        
        return available_dates
    
    def _has_available_slots(self, date_str: str) -> bool:
        """Check if a date has any available time slots"""
        slots = self.get_available_slots(date_str)
        return len(slots) > 0
    
    def get_available_slots(self, date_str: str) -> List[Dict]:
        """Get available time slots for a specific date"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            day_name = date_obj.strftime('%A').lower()
            
            # Check if business is open
            business_hours = self.business_hours[day_name]
            if business_hours['start'] is None:
                return []
            
            # Generate all possible slots
            all_slots = self._generate_slots(business_hours)
            
            # Get existing bookings for this date
            bookings = self._load_bookings()
            booked_slots = [
                booking['time'] for booking in bookings 
                if booking['date'] == date_str and booking['status'] in ['confirmed', 'tentative']
            ]
            
            # Filter out booked slots and add buffer time
            available_slots = []
            for slot in all_slots:
                if self._is_slot_available(slot, booked_slots, date_str):
                    available_slots.append({
                        'time': slot,
                        'display_time': self._format_display_time(slot),
                        'available': True
                    })
            
            return available_slots
            
        except Exception as e:
            logging.error(f"Error getting available slots for {date_str}: {e}")
            return []
    
    def _generate_slots(self, business_hours: Dict) -> List[str]:
        """Generate all possible time slots for a day"""
        slots = []
        start_minutes = self._time_to_minutes(business_hours['start'])
        end_minutes = self._time_to_minutes(business_hours['end'])
        
        current_minutes = start_minutes
        
        while current_minutes + self.slot_duration <= end_minutes:
            slot_time = self._minutes_to_time(current_minutes)
            
            # Skip lunch break if applicable
            if business_hours['lunch']:
                lunch_start = self._time_to_minutes(business_hours['lunch']['start'])
                lunch_end = self._time_to_minutes(business_hours['lunch']['end'])
                
                if not (current_minutes >= lunch_start and current_minutes < lunch_end):
                    slots.append(slot_time)
            else:
                slots.append(slot_time)
            
            current_minutes += self.slot_duration
        
        return slots
    
    def _is_slot_available(self, slot: str, booked_slots: List[str], date_str: str) -> bool:
        """Check if a specific slot is available considering buffer time"""
        slot_minutes = self._time_to_minutes(slot)
        
        for booked_slot in booked_slots:
            booked_minutes = self._time_to_minutes(booked_slot)
            
            # Check if slot conflicts with existing booking + buffer
            if abs(slot_minutes - booked_minutes) < (self.slot_duration + self.buffer_time):
                return False
        
        # Don't allow booking in the past
        current_time = self._get_hawaii_time()
        slot_datetime = datetime.strptime(f"{date_str} {slot}", '%Y-%m-%d %H:%M')
        slot_datetime = self.hawaii_tz.localize(slot_datetime)
        
        if slot_datetime <= current_time + timedelta(hours=2):  # 2-hour minimum notice
            return False
        
        return True
    
    def _format_display_time(self, time_str: str) -> str:
        """Format time for display (12-hour format)"""
        hour, minute = map(int, time_str.split(':'))
        if hour == 0:
            return f"12:{minute:02d} AM"
        elif hour < 12:
            return f"{hour}:{minute:02d} AM"
        elif hour == 12:
            return f"12:{minute:02d} PM"
        else:
            return f"{hour-12}:{minute:02d} PM"
    
    def book_appointment(self, booking_data: Dict) -> Dict:
        """Book an appointment with real-time validation"""
        try:
            date = booking_data.get('date')
            time = booking_data.get('time')
            
            # Validate required fields
            date = booking_data.get('date')
            time = booking_data.get('time')
            
            if not date or not time:
                return {
                    'success': False,
                    'error': 'Date and time are required'
                }
            
            # Validate slot is still available
            available_slots = self.get_available_slots(str(date))
            available_times = [slot['time'] for slot in available_slots]
            
            if str(time) not in available_times:
                return {
                    'success': False,
                    'error': 'Selected time slot is no longer available',
                    'available_slots': available_slots
                }
            
            # Create booking record
            booking = {
                'id': f"RT{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'date': str(date),
                'time': str(time),
                'customer_name': booking_data.get('customer_name', ''),
                'customer_phone': booking_data.get('customer_phone', ''),
                'customer_email': booking_data.get('customer_email', ''),
                'service_type': booking_data.get('service_type', ''),
                'consultation_type': booking_data.get('consultation_type', ''),
                'project_details': booking_data.get('project_details', ''),
                'status': 'confirmed',
                'booking_method': 'real_time',
                'created_at': datetime.now().isoformat(),
                'confirmed_at': datetime.now().isoformat()
            }
            
            # Save booking
            self._save_booking(booking)
            
            return {
                'success': True,
                'booking_id': booking['id'],
                'confirmation': {
                    'date': str(date),
                    'time': str(time),
                    'display_time': self._format_display_time(str(time)),
                    'customer_name': booking['customer_name'],
                    'service_type': booking['service_type']
                }
            }
            
        except Exception as e:
            logging.error(f"Error booking appointment: {e}")
            return {
                'success': False,
                'error': 'System error occurred during booking'
            }
    
    def get_booking_by_id(self, booking_id: str) -> Optional[Dict]:
        """Get booking details by ID"""
        bookings = self._load_bookings()
        for booking in bookings:
            if booking.get('id') == booking_id:
                return booking
        return None
    
    def cancel_booking(self, booking_id: str) -> bool:
        """Cancel a booking and free up the time slot"""
        try:
            bookings = self._load_bookings()
            for booking in bookings:
                if booking.get('id') == booking_id:
                    booking['status'] = 'cancelled'
                    booking['cancelled_at'] = datetime.now().isoformat()
                    
                    with open(self.bookings_file, 'w') as f:
                        json.dump(bookings, f, indent=2)
                    return True
            return False
            
        except Exception as e:
            logging.error(f"Error cancelling booking {booking_id}: {e}")
            return False
    
    def get_daily_schedule(self, date_str: str) -> Dict:
        """Get complete schedule for a specific date"""
        bookings = self._load_bookings()
        day_bookings = [
            booking for booking in bookings 
            if booking['date'] == date_str and booking['status'] == 'confirmed'
        ]
        
        available_slots = self.get_available_slots(date_str)
        
        return {
            'date': date_str,
            'available_slots': len(available_slots),
            'booked_slots': len(day_bookings),
            'bookings': sorted(day_bookings, key=lambda x: x['time']),
            'available_times': available_slots
        }