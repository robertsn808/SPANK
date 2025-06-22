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
        self.business_hours_file = 'data/business_hours.json'
        
        # Default business hours
        self.default_business_hours = {
            'monday': {'start': '07:00', 'end': '17:00', 'enabled': True},
            'tuesday': {'start': '07:00', 'end': '17:00', 'enabled': True},
            'wednesday': {'start': '07:00', 'end': '17:00', 'enabled': True},
            'thursday': {'start': '07:00', 'end': '17:00', 'enabled': True},
            'friday': {'start': '07:00', 'end': '17:00', 'enabled': True},
            'saturday': {'start': '08:00', 'end': '15:00', 'enabled': True},
            'sunday': {'start': '08:00', 'end': '15:00', 'enabled': False},
            'lunch_break': {'start': '12:00', 'end': '13:00', 'enabled': True},
            'timezone': 'Pacific/Honolulu',
            'buffer_minutes': 30  # Buffer time between appointments
        }
        
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
        
        # Initialize business hours file
        if not os.path.exists(self.business_hours_file):
            with open(self.business_hours_file, 'w') as f:
                json.dump(self.default_business_hours, f, indent=2)
    
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
        
        # Check for existing client by email/phone to maintain project continuity
        existing_client_id = self._find_existing_client(
            appointment_data.get('client_email'),
            appointment_data.get('client_phone'),
            appointment_data['client_name']
        )
        
        # Use existing client ID or generate new one
        client_id = existing_client_id or appointment_data.get('client_id') or self.generate_client_id()
        job_id = appointment_data.get('job_id') or self.generate_job_id()
        
        appointment = {
            'appointment_id': str(uuid.uuid4()),
            'client_id': client_id,
            'job_id': job_id,
            'project_name': appointment_data.get('project_name', f"{appointment_data['service_type']} Project"),
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
            'staff_portal_access': True,
            'is_returning_client': existing_client_id is not None,
            'project_phase': appointment_data.get('project_phase', 'initial'),
            'related_jobs': []  # Will be populated with other jobs for this client
        }
        
        # Save appointment
        appointments = self._load_appointments()
        appointments.append(appointment)
        self._save_appointments(appointments)
        
        # Update related jobs for client continuity
        self._update_client_project_history(client_id, job_id)
        
        logging.info(f"Created unified appointment: {client_id}/{job_id} {'(returning client)' if existing_client_id else '(new client)'}")
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
    
    def get_business_hours(self) -> Dict:
        """Get current business hours configuration"""
        try:
            with open(self.business_hours_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.default_business_hours
    
    def update_business_hours(self, hours_data: Dict) -> bool:
        """Update business hours configuration"""
        try:
            with open(self.business_hours_file, 'w') as f:
                json.dump(hours_data, f, indent=2)
            logging.info("Business hours updated successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to update business hours: {e}")
            return False
    
    def is_within_business_hours(self, date_str: str, time_str: str) -> Dict:
        """Check if appointment time is within business hours"""
        try:
            business_hours = self.get_business_hours()
            
            # Parse the date and get day of week
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d')
            day_name = appointment_date.strftime('%A').lower()
            
            # Check if business is open on this day
            day_config = business_hours.get(day_name, {})
            if not day_config.get('enabled', False):
                return {
                    'valid': False,
                    'reason': f'Business is closed on {day_name.title()}s',
                    'suggested_times': self._get_next_available_day(date_str)
                }
            
            # Parse appointment time
            appointment_time = datetime.strptime(time_str, '%H:%M').time()
            start_time = datetime.strptime(day_config['start'], '%H:%M').time()
            end_time = datetime.strptime(day_config['end'], '%H:%M').time()
            
            # Check if within business hours
            if not (start_time <= appointment_time <= end_time):
                return {
                    'valid': False,
                    'reason': f'Outside business hours. {day_name.title()} hours: {day_config["start"]} - {day_config["end"]}',
                    'business_hours': day_config,
                    'suggested_times': self._get_available_times(date_str)
                }
            
            # Check lunch break if enabled
            if business_hours.get('lunch_break', {}).get('enabled', False):
                lunch_start = datetime.strptime(business_hours['lunch_break']['start'], '%H:%M').time()
                lunch_end = datetime.strptime(business_hours['lunch_break']['end'], '%H:%M').time()
                
                if lunch_start <= appointment_time <= lunch_end:
                    return {
                        'valid': False,
                        'reason': f'During lunch break ({business_hours["lunch_break"]["start"]} - {business_hours["lunch_break"]["end"]})',
                        'suggested_times': self._get_available_times(date_str)
                    }
            
            return {'valid': True, 'reason': 'Within business hours'}
            
        except Exception as e:
            logging.error(f"Error checking business hours: {e}")
            return {'valid': False, 'reason': 'Error validating business hours'}
    
    def check_scheduling_conflicts(self, date_str: str, time_str: str, duration_minutes: int, exclude_appointment_id: str = None) -> Dict:
        """Check for scheduling conflicts with existing appointments"""
        try:
            business_hours = self.get_business_hours()
            buffer_minutes = business_hours.get('buffer_minutes', 30)
            
            # Parse new appointment time
            new_start = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
            new_end = new_start + timedelta(minutes=duration_minutes)
            
            # Get all appointments for the date
            existing_appointments = self.get_appointments_by_date_range(date_str, date_str)
            
            conflicts = []
            for apt in existing_appointments:
                # Skip if this is the same appointment (for updates)
                if exclude_appointment_id and apt['appointment_id'] == exclude_appointment_id:
                    continue
                
                # Skip cancelled appointments
                if apt.get('status') == 'cancelled':
                    continue
                
                # Parse existing appointment time
                existing_start = datetime.strptime(f"{apt['scheduled_date']} {apt['scheduled_time']}", '%Y-%m-%d %H:%M')
                existing_end = existing_start + timedelta(minutes=apt.get('estimated_duration', 120))
                
                # Add buffer time
                existing_start_with_buffer = existing_start - timedelta(minutes=buffer_minutes)
                existing_end_with_buffer = existing_end + timedelta(minutes=buffer_minutes)
                
                # Check for overlap
                if (new_start < existing_end_with_buffer and new_end > existing_start_with_buffer):
                    conflicts.append({
                        'appointment_id': apt['appointment_id'],
                        'client_name': apt['client_name'],
                        'service_type': apt['service_type'],
                        'time': apt['scheduled_time'],
                        'duration': apt.get('estimated_duration', 120),
                        'conflict_type': 'time_overlap'
                    })
            
            if conflicts:
                return {
                    'has_conflicts': True,
                    'conflicts': conflicts,
                    'suggested_times': self._get_available_times(date_str, duration_minutes),
                    'message': f'Found {len(conflicts)} scheduling conflict(s)'
                }
            
            return {
                'has_conflicts': False,
                'message': 'No scheduling conflicts found'
            }
            
        except Exception as e:
            logging.error(f"Error checking scheduling conflicts: {e}")
            return {
                'has_conflicts': True,
                'message': f'Error checking conflicts: {str(e)}'
            }
    
    def _get_available_times(self, date_str: str, duration_minutes: int = 120) -> List[str]:
        """Get list of available appointment times for a given date"""
        try:
            business_hours = self.get_business_hours()
            
            # Get day configuration
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d')
            day_name = appointment_date.strftime('%A').lower()
            day_config = business_hours.get(day_name, {})
            
            if not day_config.get('enabled', False):
                return []
            
            # Generate time slots
            start_time = datetime.strptime(day_config['start'], '%H:%M').time()
            end_time = datetime.strptime(day_config['end'], '%H:%M').time()
            
            available_times = []
            current_time = datetime.combine(appointment_date.date(), start_time)
            end_datetime = datetime.combine(appointment_date.date(), end_time)
            
            while current_time + timedelta(minutes=duration_minutes) <= end_datetime:
                time_str = current_time.strftime('%H:%M')
                
                # Check if this time conflicts with existing appointments
                conflict_check = self.check_scheduling_conflicts(date_str, time_str, duration_minutes)
                if not conflict_check['has_conflicts']:
                    # Check lunch break
                    if business_hours.get('lunch_break', {}).get('enabled', False):
                        lunch_start = datetime.strptime(business_hours['lunch_break']['start'], '%H:%M').time()
                        lunch_end = datetime.strptime(business_hours['lunch_break']['end'], '%H:%M').time()
                        
                        if not (lunch_start <= current_time.time() <= lunch_end):
                            available_times.append(time_str)
                    else:
                        available_times.append(time_str)
                
                # Move to next 30-minute slot
                current_time += timedelta(minutes=30)
            
            return available_times[:10]  # Limit to 10 suggestions
            
        except Exception as e:
            logging.error(f"Error getting available times: {e}")
            return []
    
    def _get_next_available_day(self, date_str: str) -> List[Dict]:
        """Find next available business days"""
        try:
            business_hours = self.get_business_hours()
            current_date = datetime.strptime(date_str, '%Y-%m-%d')
            available_days = []
            
            for i in range(1, 8):  # Check next 7 days
                next_date = current_date + timedelta(days=i)
                day_name = next_date.strftime('%A').lower()
                day_config = business_hours.get(day_name, {})
                
                if day_config.get('enabled', False):
                    available_days.append({
                        'date': next_date.strftime('%Y-%m-%d'),
                        'day_name': day_name.title(),
                        'hours': f"{day_config['start']} - {day_config['end']}"
                    })
                
                if len(available_days) >= 3:  # Limit to 3 suggestions
                    break
            
            return available_days
            
        except Exception as e:
            logging.error(f"Error getting next available days: {e}")
            return []
    
    def validate_appointment_time(self, date_str: str, time_str: str, duration_minutes: int = 120, exclude_appointment_id: str = None) -> Dict:
        """Comprehensive validation of appointment time"""
        # Check business hours
        hours_check = self.is_within_business_hours(date_str, time_str)
        if not hours_check['valid']:
            return {
                'valid': False,
                'reason': hours_check['reason'],
                'type': 'business_hours',
                'suggestions': hours_check.get('suggested_times', [])
            }
        
        # Check conflicts
        conflict_check = self.check_scheduling_conflicts(date_str, time_str, duration_minutes, exclude_appointment_id)
        if conflict_check['has_conflicts']:
            return {
                'valid': False,
                'reason': conflict_check['message'],
                'type': 'scheduling_conflict',
                'conflicts': conflict_check['conflicts'],
                'suggestions': conflict_check.get('suggested_times', [])
            }
        
        return {
            'valid': True,
            'reason': 'Appointment time is available'
        }
    
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
    
    def _find_existing_client(self, email: str, phone: str, name: str) -> Optional[str]:
        """Find existing client by email, phone, or name to maintain project continuity"""
        if not email and not phone:
            return None
            
        appointments = self._load_appointments()
        
        # Search by email first (most reliable)
        if email:
            for appointment in appointments:
                if appointment.get('client_email', '').lower() == email.lower():
                    return appointment['client_id']
        
        # Search by phone number
        if phone:
            for appointment in appointments:
                if appointment.get('client_phone', '') == phone:
                    return appointment['client_id']
        
        # Search by name (less reliable, only for exact matches)
        for appointment in appointments:
            if appointment.get('client_name', '').lower() == name.lower():
                return appointment['client_id']
        
        return None
    
    def _update_client_project_history(self, client_id: str, new_job_id: str):
        """Update related jobs for client project continuity"""
        appointments = self._load_appointments()
        client_jobs = []
        
        # Find all jobs for this client
        for appointment in appointments:
            if appointment['client_id'] == client_id:
                client_jobs.append({
                    'job_id': appointment['job_id'],
                    'project_name': appointment.get('project_name', 'Unnamed Project'),
                    'service_type': appointment['service_type'],
                    'status': appointment['status'],
                    'scheduled_date': appointment['scheduled_date']
                })
        
        # Update related_jobs for all appointments of this client
        for appointment in appointments:
            if appointment['client_id'] == client_id:
                appointment['related_jobs'] = [job for job in client_jobs if job['job_id'] != appointment['job_id']]
        
        self._save_appointments(appointments)
    
    def get_client_project_history(self, client_id: str) -> List[Dict]:
        """Get complete project history for a client"""
        appointments = self._load_appointments()
        client_projects = []
        
        for appointment in appointments:
            if appointment['client_id'] == client_id:
                project = {
                    'job_id': appointment['job_id'],
                    'project_name': appointment.get('project_name', 'Unnamed Project'),
                    'service_type': appointment['service_type'],
                    'status': appointment['status'],
                    'scheduled_date': appointment['scheduled_date'],
                    'scheduled_time': appointment.get('scheduled_time', ''),
                    'created_at': appointment['created_at'],
                    'notes': appointment.get('notes', ''),
                    'quote_id': appointment.get('quote_id'),
                    'project_phase': appointment.get('project_phase', 'initial')
                }
                client_projects.append(project)
        
        # Sort by creation date (newest first)
        client_projects.sort(key=lambda x: x['created_at'], reverse=True)
        return client_projects
    
    def get_clients_with_multiple_projects(self) -> List[Dict]:
        """Get clients who have multiple projects for better management"""
        appointments = self._load_appointments()
        client_project_count = {}
        client_info = {}
        
        # Count projects per client
        for appointment in appointments:
            client_id = appointment['client_id']
            if client_id not in client_project_count:
                client_project_count[client_id] = 0
                client_info[client_id] = {
                    'client_id': client_id,
                    'client_name': appointment['client_name'],
                    'client_email': appointment.get('client_email', ''),
                    'client_phone': appointment.get('client_phone', ''),
                    'projects': []
                }
            
            client_project_count[client_id] += 1
            client_info[client_id]['projects'].append({
                'job_id': appointment['job_id'],
                'project_name': appointment.get('project_name', 'Unnamed Project'),
                'service_type': appointment['service_type'],
                'status': appointment['status'],
                'scheduled_date': appointment['scheduled_date']
            })
        
        # Return only clients with multiple projects
        multi_project_clients = []
        for client_id, count in client_project_count.items():
            if count > 1:
                client_data = client_info[client_id]
                client_data['project_count'] = count
                client_data['total_value'] = self._calculate_client_total_value(client_id)
                multi_project_clients.append(client_data)
        
        # Sort by project count (most projects first)
        multi_project_clients.sort(key=lambda x: x['project_count'], reverse=True)
        return multi_project_clients
    
    def _calculate_client_total_value(self, client_id: str) -> float:
        """Calculate total project value for a client (placeholder for future quote integration)"""
        # This would integrate with the quote system to calculate actual values
        # For now, return 0 as placeholder
        return 0.0

# Global instance
unified_scheduler = UnifiedScheduler()