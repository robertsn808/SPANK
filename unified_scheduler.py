"""
Unified Appointment Scheduling System for SPANKKS Construction
Consolidates legacy appointments and CRM jobs into a single, persistent system
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pytz
import logging

class UnifiedScheduler:
    """Unified scheduling system that replaces fragmented appointment management"""
    
    def __init__(self):
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
        self.appointments_file = 'data/unified_appointments.json'
        self.client_sequence_file = 'data/client_sequence.json'
        self.job_sequence_file = 'data/job_sequence.json'
        
        # Initialize data files
        self._ensure_data_files()
        
    def _ensure_data_files(self):
        """Ensure all required data files exist"""
        import os
        os.makedirs('data', exist_ok=True)
        
        # Initialize appointments file
        if not os.path.exists(self.appointments_file):
            with open(self.appointments_file, 'w') as f:
                json.dump([], f, indent=2)
        
        # Initialize sequence files
        if not os.path.exists(self.client_sequence_file):
            with open(self.client_sequence_file, 'w') as f:
                json.dump({'next_id': 1, 'prefix': 'CLI'}, f, indent=2)
                
        if not os.path.exists(self.job_sequence_file):
            with open(self.job_sequence_file, 'w') as f:
                json.dump({'next_id': 1, 'prefix': 'JOB'}, f, indent=2)
    
    def generate_client_id(self) -> str:
        """Generate standardized client ID: CLI001, CLI002, etc."""
        with open(self.client_sequence_file, 'r') as f:
            data = json.load(f)
        
        client_id = f"{data['prefix']}{data['next_id']:03d}"
        data['next_id'] += 1
        
        with open(self.client_sequence_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        return client_id
    
    def generate_job_id(self) -> str:
        """Generate standardized job ID: JOB001, JOB002, etc."""
        with open(self.job_sequence_file, 'r') as f:
            data = json.load(f)
        
        job_id = f"{data['prefix']}{data['next_id']:03d}"
        data['next_id'] += 1
        
        with open(self.job_sequence_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        return job_id
    
    def create_appointment(self, appointment_data: Dict) -> Dict:
        """Create new appointment with standardized IDs and data structure"""
        hawaii_now = datetime.now(self.hawaii_tz)
        
        # Generate IDs if not provided
        client_id = appointment_data.get('client_id') or self.generate_client_id()
        job_id = appointment_data.get('job_id') or self.generate_job_id()
        
        appointment = {
            'appointment_id': str(uuid.uuid4()),
            'client_id': client_id,
            'job_id': job_id,
            'client_name': appointment_data['client_name'],
            'client_phone': appointment_data.get('client_phone', ''),
            'client_email': appointment_data.get('client_email', ''),
            'service_type': appointment_data['service_type'],
            'scheduled_date': appointment_data['scheduled_date'],
            'scheduled_time': appointment_data.get('scheduled_time', '09:00'),
            'estimated_duration': appointment_data.get('estimated_duration', 120),  # minutes
            'status': appointment_data.get('status', 'scheduled'),
            'priority': appointment_data.get('priority', 'normal'),
            'assigned_staff': appointment_data.get('assigned_staff', []),
            'location': appointment_data.get('location', ''),
            'notes': appointment_data.get('notes', ''),
            'quote_id': appointment_data.get('quote_id'),
            'booking_reference': appointment_data.get('booking_reference'),
            'created_at': hawaii_now.isoformat(),
            'created_by': appointment_data.get('created_by', 'system'),
            'updated_at': hawaii_now.isoformat(),
            'tags': appointment_data.get('tags', []),
            'materials_needed': appointment_data.get('materials_needed', []),
            'special_instructions': appointment_data.get('special_instructions', ''),
            'customer_portal_access': True,
            'staff_portal_access': True
        }
        
        # Save appointment
        appointments = self._load_appointments()
        appointments.append(appointment)
        self._save_appointments(appointments)
        
        logging.info(f"Created unified appointment: {client_id}/{job_id}")
        return appointment
    
    def get_appointment_by_ids(self, client_id: str, job_id: str) -> Optional[Dict]:
        """Get appointment by client and job ID combination"""
        appointments = self._load_appointments()
        for appointment in appointments:
            if appointment['client_id'] == client_id and appointment['job_id'] == job_id:
                return appointment
        return None
    
    def get_appointments_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get appointments within date range"""
        appointments = self._load_appointments()
        filtered = []
        
        for appointment in appointments:
            if start_date <= appointment['scheduled_date'] <= end_date:
                filtered.append(appointment)
        
        return sorted(filtered, key=lambda x: (x['scheduled_date'], x['scheduled_time']))
    
    def get_weekly_schedule(self, week_offset: int = 0) -> Dict:
        """Get weekly schedule with organized data"""
        hawaii_now = datetime.now(self.hawaii_tz)
        start_of_week = hawaii_now - timedelta(days=hawaii_now.weekday()) + timedelta(weeks=week_offset)
        end_of_week = start_of_week + timedelta(days=6)
        
        start_date = start_of_week.strftime('%Y-%m-%d')
        end_date = end_of_week.strftime('%Y-%m-%d')
        
        appointments = self.get_appointments_by_date_range(start_date, end_date)
        
        # Organize by day
        week_schedule = {}
        for i in range(7):
            day_date = (start_of_week + timedelta(days=i)).strftime('%Y-%m-%d')
            week_schedule[day_date] = []
        
        for appointment in appointments:
            date = appointment['scheduled_date']
            if date in week_schedule:
                week_schedule[date].append(appointment)
        
        return {
            'week_dates': [(start_of_week + timedelta(days=i)).date() for i in range(7)],
            'schedule': week_schedule,
            'total_appointments': len(appointments),
            'week_start': start_date,
            'week_end': end_date
        }
    
    def update_appointment_status(self, appointment_id: str, status: str, updated_by: str = 'system') -> bool:
        """Update appointment status with audit trail"""
        appointments = self._load_appointments()
        
        for appointment in appointments:
            if appointment['appointment_id'] == appointment_id:
                old_status = appointment['status']
                appointment['status'] = status
                appointment['updated_at'] = datetime.now(self.hawaii_tz).isoformat()
                appointment['updated_by'] = updated_by
                
                # Add status change to notes
                status_note = f"Status changed from {old_status} to {status} by {updated_by}"
                if appointment.get('status_history'):
                    appointment['status_history'].append(status_note)
                else:
                    appointment['status_history'] = [status_note]
                
                self._save_appointments(appointments)
                logging.info(f"Updated appointment {appointment_id}: {old_status} → {status}")
                return True
        
        return False
    
    def add_appointment_note(self, appointment_id: str, note: str, added_by: str = 'system') -> bool:
        """Add note to appointment"""
        appointments = self._load_appointments()
        
        for appointment in appointments:
            if appointment['appointment_id'] == appointment_id:
                hawaii_now = datetime.now(self.hawaii_tz)
                note_entry = {
                    'note': note,
                    'added_by': added_by,
                    'timestamp': hawaii_now.isoformat()
                }
                
                if appointment.get('notes_history'):
                    appointment['notes_history'].append(note_entry)
                else:
                    appointment['notes_history'] = [note_entry]
                
                appointment['updated_at'] = hawaii_now.isoformat()
                self._save_appointments(appointments)
                
                logging.info(f"Added note to appointment {appointment_id}")
                return True
        
        return False
    
    def get_staff_schedule(self, staff_id: str, date: str = None) -> List[Dict]:
        """Get appointments assigned to specific staff member"""
        appointments = self._load_appointments()
        
        if date:
            # Filter by specific date
            staff_appointments = [
                apt for apt in appointments 
                if staff_id in apt.get('assigned_staff', []) and apt['scheduled_date'] == date
            ]
        else:
            # All appointments for staff
            staff_appointments = [
                apt for apt in appointments 
                if staff_id in apt.get('assigned_staff', [])
            ]
        
        return sorted(staff_appointments, key=lambda x: (x['scheduled_date'], x['scheduled_time']))
    
    def migrate_legacy_appointments(self, legacy_appointments: List[Dict]) -> int:
        """Migrate data from legacy appointment system"""
        migrated_count = 0
        
        for legacy_apt in legacy_appointments:
            try:
                # Convert legacy format to unified format
                unified_data = {
                    'client_name': legacy_apt.get('client_name', 'Unknown'),
                    'client_phone': legacy_apt.get('client_phone', ''),
                    'client_email': legacy_apt.get('client_email', ''),
                    'service_type': legacy_apt.get('service', 'General Service'),
                    'scheduled_date': legacy_apt.get('date', ''),
                    'scheduled_time': legacy_apt.get('time', '09:00'),
                    'status': legacy_apt.get('status', 'scheduled'),
                    'notes': legacy_apt.get('notes', ''),
                    'assigned_staff': [legacy_apt.get('staff_id')] if legacy_apt.get('staff_id') else [],
                    'booking_reference': legacy_apt.get('booking_id'),
                    'created_by': legacy_apt.get('created_by', 'migration'),
                    'tags': ['migrated']
                }
                
                self.create_appointment(unified_data)
                migrated_count += 1
                
            except Exception as e:
                logging.error(f"Failed to migrate appointment: {e}")
        
        logging.info(f"Migrated {migrated_count} legacy appointments")
        return migrated_count
    
    def get_calendar_events(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Get appointments formatted for calendar display"""
        if not start_date or not end_date:
            # Default to current month
            hawaii_now = datetime.now(self.hawaii_tz)
            start_date = hawaii_now.replace(day=1).strftime('%Y-%m-%d')
            next_month = hawaii_now.replace(day=28) + timedelta(days=4)
            end_date = (next_month - timedelta(days=next_month.day)).strftime('%Y-%m-%d')
        
        appointments = self.get_appointments_by_date_range(start_date, end_date)
        
        events = []
        for apt in appointments:
            # Color coding by status
            color_map = {
                'scheduled': '#007bff',
                'in_progress': '#28a745',
                'completed': '#6c757d',
                'cancelled': '#dc3545',
                'tentative': '#ffc107'
            }
            
            event = {
                'id': apt['appointment_id'],
                'title': f"{apt['service_type']} - {apt['client_name']}",
                'start': f"{apt['scheduled_date']}T{apt['scheduled_time']}",
                'backgroundColor': color_map.get(apt['status'], '#007bff'),
                'borderColor': color_map.get(apt['status'], '#007bff'),
                'textColor': '#ffffff',
                'extendedProps': {
                    'client_id': apt['client_id'],
                    'job_id': apt['job_id'],
                    'status': apt['status'],
                    'staff': apt.get('assigned_staff', []),
                    'phone': apt['client_phone'],
                    'notes': apt['notes']
                }
            }
            events.append(event)
        
        return events
    
    def _load_appointments(self) -> List[Dict]:
        """Load appointments from JSON file"""
        try:
            with open(self.appointments_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_appointments(self, appointments: List[Dict]):
        """Save appointments to JSON file"""
        with open(self.appointments_file, 'w') as f:
            json.dump(appointments, f, indent=2, default=str)

# Global instance
unified_scheduler = UnifiedScheduler()