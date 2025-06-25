"""
Enhanced Staff Management Service for SPANKKS Construction
Handles staff portals, time tracking, job assignments, and availability management
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pytz

class EnhancedStaffService:
    def __init__(self, storage_service):
        self.storage_service = storage_service
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
        
    def get_hawaii_time(self) -> datetime:
        """Get current Hawaii time"""
        return datetime.now(self.hawaii_tz)
    
    def get_all_staff(self) -> List[Dict]:
        """Get all staff members with enhanced data"""
        try:
            staff = self.storage_service.load_data('staff.json')
            # Enhance with real-time data
            for member in staff:
                member['current_status'] = self._get_current_status(member['id'])
                member['today_hours'] = self._get_today_hours(member['id'])
                member['current_jobs'] = self._get_current_jobs(member['id'])
            return staff
        except Exception as e:
            logging.error(f"Error loading staff: {e}")
            return []  # Return empty list instead of mock data
    
    # Removed mock staff data - only use authentic database records
    
    def _get_current_status(self, staff_id: str) -> str:
        """Get current status of staff member"""
        time_entries = self._get_time_entries(staff_id)
        hawaii_time = self.get_hawaii_time()
        today = hawaii_time.date()
        
        # Check if clocked in today
        for entry in time_entries:
            entry_date = datetime.fromisoformat(entry['clock_in']).date()
            if entry_date == today and not entry.get('clock_out'):
                return 'on_job'
        
        return 'available'
    
    def _get_today_hours(self, staff_id: str) -> float:
        """Calculate hours worked today"""
        time_entries = self._get_time_entries(staff_id)
        hawaii_time = self.get_hawaii_time()
        today = hawaii_time.date()
        total_hours = 0.0
        
        for entry in time_entries:
            entry_date = datetime.fromisoformat(entry['clock_in']).date()
            if entry_date == today:
                clock_in = datetime.fromisoformat(entry['clock_in'])
                if entry.get('clock_out'):
                    clock_out = datetime.fromisoformat(entry['clock_out'])
                    hours = (clock_out - clock_in).total_seconds() / 3600
                    total_hours += hours
                else:
                    # Currently clocked in
                    hours = (hawaii_time.replace(tzinfo=None) - clock_in).total_seconds() / 3600
                    total_hours += hours
        
        return round(total_hours, 1)
    
    def _get_current_jobs(self, staff_id: str) -> List[str]:
        """Get current job assignments for staff member"""
        try:
            assignments = self.storage_service.load_data('job_assignments.json')
            current_jobs = []
            for assignment in assignments:
                if (assignment.get('staff_id') == staff_id and 
                    assignment.get('status') in ['assigned', 'in_progress']):
                    current_jobs.append(assignment.get('job_id'))
            return current_jobs
        except:
            return []
    
    def _get_time_entries(self, staff_id: str) -> List[Dict]:
        """Get time entries for staff member"""
        try:
            entries = self.storage_service.load_data('time_entries.json')
            return [e for e in entries if e.get('staff_id') == staff_id]
        except:
            return []
    
    def clock_in(self, staff_id: str, job_id: str = None, location: Dict = None) -> Dict:
        """Clock in staff member with GPS location"""
        hawaii_time = self.get_hawaii_time()
        
        entry = {
            'id': f"TIME{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'staff_id': staff_id,
            'job_id': job_id,
            'clock_in': hawaii_time.isoformat(),
            'clock_out': None,
            'location': location or {},
            'notes': '',
            'break_minutes': 0,
            'overtime_hours': 0.0
        }
        
        try:
            entries = self.storage_service.load_data('time_entries.json')
            entries.append(entry)
            self.storage_service.save_data('time_entries.json', entries)
            return {'success': True, 'entry_id': entry['id']}
        except Exception as e:
            logging.error(f"Error clocking in: {e}")
            return {'success': False, 'error': str(e)}
    
    def clock_out(self, staff_id: str, notes: str = '') -> Dict:
        """Clock out staff member"""
        hawaii_time = self.get_hawaii_time()
        
        try:
            entries = self.storage_service.load_data('time_entries.json')
            
            # Find most recent open entry
            for entry in reversed(entries):
                if (entry.get('staff_id') == staff_id and 
                    not entry.get('clock_out')):
                    entry['clock_out'] = hawaii_time.isoformat()
                    entry['notes'] = notes
                    
                    # Calculate hours and overtime
                    clock_in = datetime.fromisoformat(entry['clock_in'])
                    total_hours = (hawaii_time.replace(tzinfo=None) - clock_in).total_seconds() / 3600
                    if total_hours > 8:
                        entry['overtime_hours'] = total_hours - 8
                    
                    self.storage_service.save_data('time_entries.json', entries)
                    return {'success': True, 'total_hours': round(total_hours, 2)}
            
            return {'success': False, 'error': 'No open time entry found'}
            
        except Exception as e:
            logging.error(f"Error clocking out: {e}")
            return {'success': False, 'error': str(e)}
    
    def assign_job(self, staff_id: str, job_id: str, role: str = 'worker', priority: str = 'normal') -> Dict:
        """Assign job to staff member"""
        assignment = {
            'id': f"ASSIGN{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'staff_id': staff_id,
            'job_id': job_id,
            'role': role,
            'priority': priority,
            'status': 'assigned',
            'assigned_date': self.get_hawaii_time().isoformat(),
            'start_date': None,
            'completion_date': None,
            'notes': ''
        }
        
        try:
            assignments = self.storage_service.load_data('job_assignments.json')
            assignments.append(assignment)
            self.storage_service.save_data('job_assignments.json', assignments)
            return {'success': True, 'assignment_id': assignment['id']}
        except Exception as e:
            logging.error(f"Error assigning job: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_workload_analysis(self) -> Dict:
        """Analyze staff workload and capacity"""
        staff = self.get_all_staff()
        analysis = {
            'total_staff': len(staff),
            'available_staff': len([s for s in staff if s['availability'] == 'available']),
            'busy_staff': len([s for s in staff if s['availability'] == 'busy']),
            'total_capacity_hours': sum(8 for s in staff if s['status'] == 'active'),
            'utilized_hours': sum(s['today_hours'] for s in staff),
            'capacity_utilization': 0.0,
            'staff_details': []
        }
        
        if analysis['total_capacity_hours'] > 0:
            analysis['capacity_utilization'] = (analysis['utilized_hours'] / analysis['total_capacity_hours']) * 100
        
        for member in staff:
            analysis['staff_details'].append({
                'staff_id': member['id'],
                'name': member['full_name'],
                'today_hours': member['today_hours'],
                'utilization': (member['today_hours'] / 8) * 100 if member['today_hours'] <= 8 else 100,
                'current_jobs': len(member['current_jobs']),
                'availability': member['availability']
            })
        
        return analysis
    
    def get_payroll_summary(self, week_start: str = None) -> Dict:
        """Generate payroll summary for specified week"""
        if not week_start:
            hawaii_time = self.get_hawaii_time()
            week_start = (hawaii_time - timedelta(days=hawaii_time.weekday())).strftime('%Y-%m-%d')
        
        staff = self.get_all_staff()
        summary = {
            'week_start': week_start,
            'total_hours': 0.0,
            'total_regular_pay': 0.0,
            'total_overtime_pay': 0.0,
            'total_payroll': 0.0,
            'staff_payroll': []
        }
        
        for member in staff:
            # Calculate weekly hours (simplified for demo)
            weekly_hours = member['today_hours'] * 5  # Simulate 5-day week
            overtime_hours = max(0, weekly_hours - 40)
            regular_hours = min(weekly_hours, 40)
            
            regular_pay = regular_hours * member['hourly_rate']
            overtime_pay = overtime_hours * member['hourly_rate'] * 1.5
            total_pay = regular_pay + overtime_pay
            
            staff_payroll = {
                'staff_id': member['id'],
                'name': member['full_name'],
                'regular_hours': regular_hours,
                'overtime_hours': overtime_hours,
                'hourly_rate': member['hourly_rate'],
                'regular_pay': regular_pay,
                'overtime_pay': overtime_pay,
                'total_pay': total_pay
            }
            
            summary['staff_payroll'].append(staff_payroll)
            summary['total_hours'] += weekly_hours
            summary['total_regular_pay'] += regular_pay
            summary['total_overtime_pay'] += overtime_pay
            summary['total_payroll'] += total_pay
        
        return summary