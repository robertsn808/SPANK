"""
Calendar Enhancement Service - Status filtering and color-coding for appointments
Handles calendar event styling, status management, and visual organization
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pytz

class CalendarEnhancementService:
    def __init__(self):
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
        self.calendar_config_file = 'data/calendar_config.json'
        self._ensure_config_file()
        
        # Status color mapping
        self.status_colors = {
            'pending': '#ffc107',      # Yellow - awaiting confirmation
            'confirmed': '#28a745',    # Green - confirmed appointment
            'in_progress': '#007bff',  # Blue - work in progress
            'completed': '#6c757d',    # Gray - completed job
            'cancelled': '#dc3545',    # Red - cancelled
            'rescheduled': '#fd7e14',  # Orange - needs rescheduling
            'tentative': '#17a2b8',    # Teal - tentative booking
            'quoted': '#6f42c1'       # Purple - quote sent
        }
        
        # Service type colors
        self.service_colors = {
            'drywall': '#e83e8c',      # Pink
            'flooring': '#8B4513',     # Brown
            'electrical': '#FFD700',   # Gold
            'plumbing': '#4682B4',     # Steel Blue
            'painting': '#FF6347',     # Tomato
            'renovation': '#9370DB',   # Medium Purple
            'fence': '#228B22',        # Forest Green
            'general': '#708090'       # Slate Gray
        }
    
    def _ensure_config_file(self):
        """Ensure calendar configuration file exists"""
        os.makedirs('data', exist_ok=True)
        
        if not os.path.exists(self.calendar_config_file):
            default_config = {
                'view_preferences': {
                    'default_view': 'timeGridWeek',
                    'show_weekends': True,
                    'business_hours': {
                        'start': '07:00',
                        'end': '17:00'
                    }
                },
                'status_filters': {
                    'show_pending': True,
                    'show_confirmed': True,
                    'show_in_progress': True,
                    'show_completed': False,
                    'show_cancelled': False,
                    'show_rescheduled': True,
                    'show_tentative': True,
                    'show_quoted': True
                },
                'color_coding': {
                    'by_status': True,
                    'by_service_type': False,
                    'by_priority': False
                }
            }
            
            with open(self.calendar_config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
    
    def get_calendar_config(self) -> Dict:
        """Get current calendar configuration"""
        try:
            with open(self.calendar_config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._ensure_config_file()
            return self.get_calendar_config()
    
    def update_calendar_config(self, config_updates: Dict) -> bool:
        """Update calendar configuration"""
        try:
            config = self.get_calendar_config()
            
            # Deep update configuration
            for key, value in config_updates.items():
                if isinstance(value, dict) and key in config:
                    config[key].update(value)
                else:
                    config[key] = value
            
            with open(self.calendar_config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logging.info("Calendar configuration updated")
            return True
            
        except Exception as e:
            logging.error(f"Error updating calendar config: {e}")
            return False
    
    def get_enhanced_calendar_events(self, appointments: List[Dict], 
                                   start_date: str = None, end_date: str = None) -> List[Dict]:
        """Convert appointments to enhanced FullCalendar events with color coding"""
        config = self.get_calendar_config()
        status_filters = config.get('status_filters', {})
        color_mode = config.get('color_coding', {})
        
        events = []
        
        for appointment in appointments:
            # Check status filter
            status = appointment.get('status', 'pending').lower()
            if not status_filters.get(f'show_{status}', True):
                continue
            
            # Date filtering
            appointment_date = appointment.get('scheduled_date', '')
            if start_date and appointment_date < start_date:
                continue
            if end_date and appointment_date > end_date:
                continue
            
            # Determine color based on mode
            event_color = self._get_event_color(appointment, color_mode)
            
            # Create FullCalendar event
            event = {
                'id': appointment.get('appointment_id', ''),
                'title': self._format_event_title(appointment),
                'start': f"{appointment_date}T{appointment.get('scheduled_time', '09:00')}",
                'end': self._calculate_end_time(appointment),
                'backgroundColor': event_color,
                'borderColor': event_color,
                'textColor': self._get_text_color(event_color),
                'extendedProps': {
                    'client_id': appointment.get('client_id', ''),
                    'job_id': appointment.get('job_id', ''),
                    'client_name': appointment.get('client_name', ''),
                    'client_phone': appointment.get('client_phone', ''),
                    'service_type': appointment.get('service_type', ''),
                    'status': status,
                    'priority': appointment.get('priority', 'normal'),
                    'notes': appointment.get('notes', ''),
                    'estimated_duration': appointment.get('estimated_duration', 120),
                    'assigned_staff': appointment.get('assigned_staff', []),
                    'location': appointment.get('location', '')
                }
            }
            
            # Add status-specific properties
            if status == 'tentative':
                event['display'] = 'background'
                event['className'] = 'tentative-event'
            elif status == 'cancelled':
                event['className'] = 'cancelled-event'
                event['textColor'] = '#ffffff'
            
            events.append(event)
        
        return events
    
    def _get_event_color(self, appointment: Dict, color_mode: Dict) -> str:
        """Determine event color based on color mode settings"""
        if color_mode.get('by_status', True):
            status = appointment.get('status', 'pending').lower()
            return self.status_colors.get(status, '#6c757d')
        
        elif color_mode.get('by_service_type', False):
            service_type = appointment.get('service_type', 'general').lower()
            for key, color in self.service_colors.items():
                if key in service_type:
                    return color
            return self.service_colors['general']
        
        elif color_mode.get('by_priority', False):
            priority = appointment.get('priority', 'normal').lower()
            priority_colors = {
                'low': '#28a745',
                'normal': '#007bff',
                'high': '#ffc107',
                'urgent': '#dc3545'
            }
            return priority_colors.get(priority, '#007bff')
        
        return '#007bff'  # Default blue
    
    def _get_text_color(self, background_color: str) -> str:
        """Calculate appropriate text color based on background"""
        # Simple contrast calculation
        if background_color.lower() in ['#ffc107', '#FFD700', '#FF6347']:
            return '#000000'  # Dark text for light backgrounds
        return '#ffffff'  # White text for dark backgrounds
    
    def _format_event_title(self, appointment: Dict) -> str:
        """Format event title with relevant information"""
        client_name = appointment.get('client_name', 'Unknown Client')
        service_type = appointment.get('service_type', 'Service')
        
        # Truncate for calendar display
        if len(client_name) > 15:
            client_name = client_name[:12] + '...'
        
        if len(service_type) > 20:
            service_type = service_type[:17] + '...'
        
        return f"{client_name} - {service_type}"
    
    def _calculate_end_time(self, appointment: Dict) -> str:
        """Calculate event end time based on duration"""
        start_date = appointment.get('scheduled_date', '')
        start_time = appointment.get('scheduled_time', '09:00')
        duration_minutes = appointment.get('estimated_duration', 120)
        
        try:
            # Parse start datetime
            start_datetime = datetime.strptime(f"{start_date} {start_time}", '%Y-%m-%d %H:%M')
            
            # Add duration
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)
            
            return end_datetime.strftime('%Y-%m-%dT%H:%M')
            
        except ValueError:
            # Fallback to 2-hour default
            fallback_end = datetime.strptime(f"{start_date} {start_time}", '%Y-%m-%d %H:%M')
            fallback_end += timedelta(hours=2)
            return fallback_end.strftime('%Y-%m-%dT%H:%M')
    
    def get_status_summary(self, appointments: List[Dict]) -> Dict:
        """Get summary of appointments by status"""
        summary = {}
        
        for appointment in appointments:
            status = appointment.get('status', 'pending').lower()
            summary[status] = summary.get(status, 0) + 1
        
        return summary
    
    def update_appointment_status(self, appointment_id: str, new_status: str, 
                                 updated_by: str = 'admin') -> bool:
        """Update appointment status with logging"""
        try:
            from unified_scheduler import UnifiedScheduler
            scheduler = UnifiedScheduler()
            
            # Update status in unified scheduler
            success = scheduler.update_appointment_status(appointment_id, new_status, updated_by)
            
            if success:
                logging.info(f"Updated appointment {appointment_id} status to {new_status}")
            
            return success
            
        except Exception as e:
            logging.error(f"Error updating appointment status: {e}")
            return False
    
    def bulk_status_update(self, appointment_ids: List[str], new_status: str, 
                          updated_by: str = 'admin') -> Dict:
        """Update multiple appointments to same status"""
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for appointment_id in appointment_ids:
            if self.update_appointment_status(appointment_id, new_status, updated_by):
                results['success'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"Failed to update {appointment_id}")
        
        logging.info(f"Bulk status update: {results['success']} success, {results['failed']} failed")
        return results
    
    def get_calendar_legend(self) -> Dict:
        """Get calendar legend for status colors"""
        config = self.get_calendar_config()
        color_mode = config.get('color_coding', {})
        
        if color_mode.get('by_status', True):
            return {
                'title': 'Status Legend',
                'items': [
                    {'label': 'Pending', 'color': self.status_colors['pending']},
                    {'label': 'Confirmed', 'color': self.status_colors['confirmed']},
                    {'label': 'In Progress', 'color': self.status_colors['in_progress']},
                    {'label': 'Completed', 'color': self.status_colors['completed']},
                    {'label': 'Cancelled', 'color': self.status_colors['cancelled']},
                    {'label': 'Rescheduled', 'color': self.status_colors['rescheduled']},
                    {'label': 'Tentative', 'color': self.status_colors['tentative']},
                    {'label': 'Quoted', 'color': self.status_colors['quoted']}
                ]
            }
        
        elif color_mode.get('by_service_type', False):
            return {
                'title': 'Service Type Legend',
                'items': [
                    {'label': 'Drywall', 'color': self.service_colors['drywall']},
                    {'label': 'Flooring', 'color': self.service_colors['flooring']},
                    {'label': 'Electrical', 'color': self.service_colors['electrical']},
                    {'label': 'Plumbing', 'color': self.service_colors['plumbing']},
                    {'label': 'Painting', 'color': self.service_colors['painting']},
                    {'label': 'Renovation', 'color': self.service_colors['renovation']},
                    {'label': 'Fence', 'color': self.service_colors['fence']},
                    {'label': 'General', 'color': self.service_colors['general']}
                ]
            }
        
        return {'title': 'Calendar Legend', 'items': []}
    
    def export_calendar_data(self, start_date: str, end_date: str, 
                           format_type: str = 'ics') -> Optional[str]:
        """Export calendar data in specified format"""
        try:
            from unified_scheduler import UnifiedScheduler
            scheduler = UnifiedScheduler()
            
            appointments = scheduler.get_appointments_by_date_range(start_date, end_date)
            
            if format_type == 'ics':
                return self._generate_ics_calendar(appointments)
            elif format_type == 'csv':
                return self._generate_csv_calendar(appointments)
            
            return None
            
        except Exception as e:
            logging.error(f"Error exporting calendar data: {e}")
            return None
    
    def _generate_ics_calendar(self, appointments: List[Dict]) -> str:
        """Generate ICS calendar file content"""
        ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//SPANKKS Construction//Calendar//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
"""
        
        for appointment in appointments:
            ics_content += f"""BEGIN:VEVENT
UID:{appointment.get('appointment_id', '')}@spankks.com
DTSTART:{self._format_ics_datetime(appointment.get('scheduled_date', ''), appointment.get('scheduled_time', '09:00'))}
DTEND:{self._format_ics_datetime(appointment.get('scheduled_date', ''), appointment.get('scheduled_time', '09:00'), appointment.get('estimated_duration', 120))}
SUMMARY:{appointment.get('client_name', '')} - {appointment.get('service_type', '')}
DESCRIPTION:Status: {appointment.get('status', '')}\\nPhone: {appointment.get('client_phone', '')}\\nNotes: {appointment.get('notes', '')}
LOCATION:{appointment.get('location', '')}
STATUS:CONFIRMED
END:VEVENT
"""
        
        ics_content += "END:VCALENDAR"
        return ics_content
    
    def _format_ics_datetime(self, date: str, time: str, duration_minutes: int = 0) -> str:
        """Format datetime for ICS format"""
        try:
            dt = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M')
            if duration_minutes > 0:
                dt += timedelta(minutes=duration_minutes)
            return dt.strftime('%Y%m%dT%H%M%S')
        except ValueError:
            return datetime.now().strftime('%Y%m%dT%H%M%S')
    
    def _generate_csv_calendar(self, appointments: List[Dict]) -> str:
        """Generate CSV calendar export"""
        csv_content = "Date,Time,Client,Service,Status,Phone,Location,Notes\n"
        
        for appointment in appointments:
            csv_content += f'"{appointment.get("scheduled_date", "")}","{appointment.get("scheduled_time", "")}","{appointment.get("client_name", "")}","{appointment.get("service_type", "")}","{appointment.get("status", "")}","{appointment.get("client_phone", "")}","{appointment.get("location", "")}","{appointment.get("notes", "")}"\n'
        
        return csv_content