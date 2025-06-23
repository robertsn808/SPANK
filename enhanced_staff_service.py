"""
Enhanced Staff Management Service - Role-based staff management with availability tracking
Handles staff roles, skills, availability, performance metrics, and workload distribution
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pytz

class EnhancedStaffService:
    def __init__(self):
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
        self.staff_file = 'data/enhanced_staff.json'
        self.availability_file = 'data/staff_availability.json'
        self.assignments_file = 'data/staff_assignments.json'
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Ensure staff data files exist"""
        os.makedirs('data', exist_ok=True)
        
        if not os.path.exists(self.staff_file):
            with open(self.staff_file, 'w') as f:
                json.dump([], f, indent=2)
        
        if not os.path.exists(self.availability_file):
            with open(self.availability_file, 'w') as f:
                json.dump({}, f, indent=2)
        
        if not os.path.exists(self.assignments_file):
            with open(self.assignments_file, 'w') as f:
                json.dump([], f, indent=2)
    
    def _load_staff(self) -> List[Dict]:
        """Load staff from JSON file"""
        try:
            with open(self.staff_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_staff(self, staff: List[Dict]):
        """Save staff to JSON file"""
        with open(self.staff_file, 'w') as f:
            json.dump(staff, f, indent=2)
    
    def _load_availability(self) -> Dict:
        """Load availability schedules"""
        try:
            with open(self.availability_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_availability(self, availability: Dict):
        """Save availability schedules"""
        with open(self.availability_file, 'w') as f:
            json.dump(availability, f, indent=2)
    
    def add_staff_member(self, staff_data: Dict) -> Dict:
        """Add new enhanced staff member with role and skills"""
        hawaii_now = datetime.now(self.hawaii_tz)
        staff_list = self._load_staff()
        
        # Generate staff ID
        staff_id = f"STF{len(staff_list) + 1:03d}"
        
        staff_member = {
            'staff_id': staff_id,
            'name': staff_data['name'],
            'email': staff_data.get('email', ''),
            'phone': staff_data.get('phone', ''),
            'role': staff_data.get('role', 'crew_member'),  # admin, supervisor, crew_member, specialist
            'skills': staff_data.get('skills', []),  # drywall, flooring, electrical, plumbing, painting
            'hourly_rate': float(staff_data.get('hourly_rate', 25.00)),
            'hire_date': staff_data.get('hire_date', hawaii_now.strftime('%Y-%m-%d')),
            'employment_status': staff_data.get('employment_status', 'active'),  # active, inactive, terminated
            'certifications': staff_data.get('certifications', []),
            'emergency_contact': staff_data.get('emergency_contact', {}),
            'notes': staff_data.get('notes', ''),
            'performance_rating': 5.0,  # 1-5 scale
            'jobs_completed': 0,
            'total_hours': 0,
            'average_rating': 0,
            'created_at': hawaii_now.isoformat(),
            'updated_at': hawaii_now.isoformat()
        }
        
        staff_list.append(staff_member)
        self._save_staff(staff_list)
        
        # Initialize availability schedule
        self._initialize_staff_availability(staff_id)
        
        logging.info(f"Added enhanced staff member: {staff_id} - {staff_data['name']} ({staff_data.get('role', 'crew_member')})")
        return staff_member
    
    def _initialize_staff_availability(self, staff_id: str):
        """Initialize default availability schedule for staff member"""
        availability = self._load_availability()
        
        # Default schedule: Monday-Friday 7AM-5PM, Saturday 8AM-3PM
        default_schedule = {
            'monday': {'available': True, 'start_time': '07:00', 'end_time': '17:00'},
            'tuesday': {'available': True, 'start_time': '07:00', 'end_time': '17:00'},
            'wednesday': {'available': True, 'start_time': '07:00', 'end_time': '17:00'},
            'thursday': {'available': True, 'start_time': '07:00', 'end_time': '17:00'},
            'friday': {'available': True, 'start_time': '07:00', 'end_time': '17:00'},
            'saturday': {'available': True, 'start_time': '08:00', 'end_time': '15:00'},
            'sunday': {'available': False, 'start_time': '', 'end_time': ''}
        }
        
        availability[staff_id] = {
            'regular_schedule': default_schedule,
            'time_off_requests': [],
            'blocked_dates': [],
            'overtime_approved': False
        }
        
        self._save_availability(availability)
    
    def update_staff_availability(self, staff_id: str, schedule_data: Dict) -> bool:
        """Update staff member availability schedule"""
        try:
            availability = self._load_availability()
            
            if staff_id not in availability:
                self._initialize_staff_availability(staff_id)
                availability = self._load_availability()
            
            # Update regular schedule
            if 'regular_schedule' in schedule_data:
                availability[staff_id]['regular_schedule'].update(schedule_data['regular_schedule'])
            
            # Add time off request
            if 'time_off' in schedule_data:
                time_off = schedule_data['time_off']
                time_off['requested_at'] = datetime.now(self.hawaii_tz).isoformat()
                time_off['status'] = 'pending'
                availability[staff_id]['time_off_requests'].append(time_off)
            
            # Block specific dates
            if 'blocked_dates' in schedule_data:
                availability[staff_id]['blocked_dates'].extend(schedule_data['blocked_dates'])
            
            self._save_availability(availability)
            logging.info(f"Updated availability for staff {staff_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error updating staff availability: {e}")
            return False
    
    def get_available_staff(self, date: str, time_slot: str = None) -> List[Dict]:
        """Get staff members available for specific date/time"""
        staff_list = self._load_staff()
        availability = self._load_availability()
        
        available_staff = []
        
        for staff_member in staff_list:
            if staff_member['employment_status'] != 'active':
                continue
            
            staff_id = staff_member['staff_id']
            staff_availability = availability.get(staff_id, {})
            
            # Check if date is blocked
            blocked_dates = staff_availability.get('blocked_dates', [])
            if date in blocked_dates:
                continue
            
            # Check regular schedule
            try:
                weekday = datetime.strptime(date, '%Y-%m-%d').strftime('%A').lower()
                day_schedule = staff_availability.get('regular_schedule', {}).get(weekday, {})
                
                if not day_schedule.get('available', False):
                    continue
                
                # If time slot specified, check if within working hours
                if time_slot:
                    start_time = day_schedule.get('start_time', '')
                    end_time = day_schedule.get('end_time', '')
                    
                    if start_time and end_time:
                        if not (start_time <= time_slot <= end_time):
                            continue
                
                available_staff.append({
                    **staff_member,
                    'availability_window': f"{day_schedule.get('start_time', '')} - {day_schedule.get('end_time', '')}"
                })
                
            except ValueError:
                continue
        
        return available_staff
    
    def assign_staff_to_job(self, staff_id: str, job_id: str, estimated_hours: float, 
                           start_date: str, notes: str = '') -> bool:
        """Assign staff member to a job"""
        try:
            # Load current assignments
            with open(self.assignments_file, 'r') as f:
                assignments = json.load(f)
            
            # Create assignment record
            assignment = {
                'assignment_id': f"ASG{len(assignments) + 1:04d}",
                'staff_id': staff_id,
                'job_id': job_id,
                'estimated_hours': estimated_hours,
                'actual_hours': 0,
                'start_date': start_date,
                'completion_date': None,
                'status': 'assigned',  # assigned, in_progress, completed, cancelled
                'notes': notes,
                'created_at': datetime.now(self.hawaii_tz).isoformat()
            }
            
            assignments.append(assignment)
            
            with open(self.assignments_file, 'w') as f:
                json.dump(assignments, f, indent=2)
            
            logging.info(f"Assigned staff {staff_id} to job {job_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error assigning staff to job: {e}")
            return False
    
    def get_staff_workload(self, staff_id: str = None) -> Dict:
        """Get workload analysis for staff member(s)"""
        try:
            with open(self.assignments_file, 'r') as f:
                assignments = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            assignments = []
        
        staff_list = self._load_staff()
        
        if staff_id:
            # Single staff member workload
            staff_assignments = [a for a in assignments if a['staff_id'] == staff_id and a['status'] in ['assigned', 'in_progress']]
            total_hours = sum(a['estimated_hours'] for a in staff_assignments)
            
            return {
                'staff_id': staff_id,
                'active_jobs': len(staff_assignments),
                'total_estimated_hours': total_hours,
                'assignments': staff_assignments
            }
        else:
            # All staff workload summary
            workload_summary = {}
            
            for staff_member in staff_list:
                if staff_member['employment_status'] != 'active':
                    continue
                
                sid = staff_member['staff_id']
                staff_assignments = [a for a in assignments if a['staff_id'] == sid and a['status'] in ['assigned', 'in_progress']]
                
                workload_summary[sid] = {
                    'name': staff_member['name'],
                    'role': staff_member['role'],
                    'active_jobs': len(staff_assignments),
                    'total_hours': sum(a['estimated_hours'] for a in staff_assignments),
                    'capacity_status': 'available' if len(staff_assignments) < 3 else 'busy' if len(staff_assignments) < 5 else 'overloaded'
                }
            
            return workload_summary
    
    def update_staff_performance(self, staff_id: str, job_rating: float, hours_worked: float) -> bool:
        """Update staff performance metrics after job completion"""
        try:
            staff_list = self._load_staff()
            
            for staff_member in staff_list:
                if staff_member['staff_id'] == staff_id:
                    # Update job completion stats
                    staff_member['jobs_completed'] += 1
                    staff_member['total_hours'] += hours_worked
                    
                    # Calculate new average rating
                    current_avg = staff_member.get('average_rating', 0)
                    job_count = staff_member['jobs_completed']
                    
                    if job_count == 1:
                        staff_member['average_rating'] = job_rating
                    else:
                        staff_member['average_rating'] = ((current_avg * (job_count - 1)) + job_rating) / job_count
                    
                    staff_member['updated_at'] = datetime.now(self.hawaii_tz).isoformat()
                    break
            
            self._save_staff(staff_list)
            logging.info(f"Updated performance for staff {staff_id}: {job_rating}/5 rating, {hours_worked} hours")
            return True
            
        except Exception as e:
            logging.error(f"Error updating staff performance: {e}")
            return False
    
    def get_staff_by_skills(self, required_skills: List[str]) -> List[Dict]:
        """Get staff members with specific skills"""
        staff_list = self._load_staff()
        
        matching_staff = []
        for staff_member in staff_list:
            if staff_member['employment_status'] != 'active':
                continue
            
            staff_skills = staff_member.get('skills', [])
            if any(skill in staff_skills for skill in required_skills):
                skill_match_count = sum(1 for skill in required_skills if skill in staff_skills)
                staff_member['skill_match_percentage'] = (skill_match_count / len(required_skills)) * 100
                matching_staff.append(staff_member)
        
        # Sort by skill match percentage and performance rating
        matching_staff.sort(key=lambda x: (x['skill_match_percentage'], x.get('average_rating', 0)), reverse=True)
        return matching_staff
    
    def get_staff_summary(self) -> Dict:
        """Get comprehensive staff summary statistics"""
        staff_list = self._load_staff()
        active_staff = [s for s in staff_list if s['employment_status'] == 'active']
        
        # Role distribution
        roles = {}
        for staff in active_staff:
            role = staff.get('role', 'crew_member')
            roles[role] = roles.get(role, 0) + 1
        
        # Skill distribution
        all_skills = []
        for staff in active_staff:
            all_skills.extend(staff.get('skills', []))
        
        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Performance metrics
        total_jobs = sum(s.get('jobs_completed', 0) for s in active_staff)
        total_hours = sum(s.get('total_hours', 0) for s in active_staff)
        avg_performance = sum(s.get('average_rating', 0) for s in active_staff) / len(active_staff) if active_staff else 0
        
        return {
            'total_staff': len(active_staff),
            'role_distribution': roles,
            'skill_distribution': skill_counts,
            'performance_metrics': {
                'total_jobs_completed': total_jobs,
                'total_hours_worked': total_hours,
                'average_rating': round(avg_performance, 2)
            },
            'capacity_status': self.get_staff_workload()
        }