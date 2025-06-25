"""
Enhanced Authentication Service for SPANKKS Construction
Handles dual-level authentication, session management, and portal access control
"""

import json
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import session, request

class EnhancedAuthService:
    def __init__(self, storage_service):
        self.storage_service = storage_service
        self.session_timeout = 3600  # 1 hour
        self.max_login_attempts = 5
        self.lockout_duration = 300  # 5 minutes
    
    def authenticate_client_portal(self, client_id: str, job_id: str) -> Dict:
        """Authenticate client for read-only portal access"""
        try:
            # Load client data
            clients = self.storage_service.load_data('clients.json')
            
            # Find matching client
            client = None
            for c in clients:
                if (c.get('client_id', '').upper() == client_id.upper() and 
                    c.get('job_id', '').upper() == job_id.upper()):
                    client = c
                    break
            
            if not client:
                # Try alternative lookup in contacts/appointments
                contacts = self.storage_service.get_all_contacts()
                appointments = self.storage_service.load_data('unified_appointments.json')
                
                # Check appointments for matching IDs
                for apt in appointments:
                    if (apt.get('client_id', '').upper() == client_id.upper() and 
                        apt.get('job_id', '').upper() == job_id.upper()):
                        # Find associated contact
                        contact = next((c for c in contacts if c.get('id') == apt.get('client_id')), None)
                        if contact:
                            client = {
                                'client_id': client_id,
                                'job_id': job_id,
                                'client_name': contact.get('name'),
                                'client_phone': contact.get('phone'),
                                'client_email': contact.get('email'),
                                'access_level': 'client',
                                'status': 'active'
                            }
                            break
            
            if not client:
                self._log_login_attempt(client_id, 'client_portal', False, 'Invalid credentials')
                return {
                    'success': False,
                    'error': 'Invalid client ID or job ID'
                }
            
            # Create client session
            session_data = {
                'client_id': client_id,
                'job_id': job_id,
                'access_level': 'client',
                'client_name': client.get('client_name', 'Unknown'),
                'login_time': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(seconds=self.session_timeout)).isoformat()
            }
            
            self._log_login_attempt(client_id, 'client_portal', True)
            
            return {
                'success': True,
                'session_data': session_data,
                'access_level': 'client'
            }
            
        except Exception as e:
            logging.error(f"Client portal authentication error: {e}")
            return {
                'success': False,
                'error': 'Authentication system error'
            }
    
    def authenticate_staff_portal(self, client_id: str, job_id: str, pin: str) -> Dict:
        """Authenticate staff for full portal access with PIN"""
        try:
            # First validate client/job combination
            client_auth = self.authenticate_client_portal(client_id, job_id)
            if not client_auth['success']:
                return client_auth
            
            # Validate PIN for staff access
            if not self._validate_staff_pin(pin):
                self._log_login_attempt(f"{client_id}+PIN", 'staff_portal', False, 'Invalid PIN')
                return {
                    'success': False,
                    'error': 'Invalid staff PIN'
                }
            
            # Get staff member by PIN
            staff_member = self._get_staff_by_pin(pin)
            
            # Create staff session with full access
            session_data = {
                'client_id': client_id,
                'job_id': job_id,
                'access_level': 'staff',
                'staff_id': staff_member['id'] if staff_member else 'STF001',
                'staff_name': staff_member['full_name'] if staff_member else 'SPANKKS Staff',
                'client_name': client_auth['session_data']['client_name'],
                'login_time': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(seconds=self.session_timeout * 2)).isoformat(),
                'permissions': staff_member.get('permissions', ['all']) if staff_member else ['all']
            }
            
            self._log_login_attempt(f"{client_id}+PIN", 'staff_portal', True)
            
            return {
                'success': True,
                'session_data': session_data,
                'access_level': 'staff'
            }
            
        except Exception as e:
            logging.error(f"Staff portal authentication error: {e}")
            return {
                'success': False,
                'error': 'Authentication system error'
            }
    
    def _validate_staff_pin(self, pin: str) -> bool:
        """Validate staff PIN"""
        # For SPANKKS Construction, using secure PIN
        valid_pins = ['Money$$', 'SPANKKS123', 'Admin2025']
        return pin in valid_pins
    
    def _get_staff_by_pin(self, pin: str) -> Optional[Dict]:
        """Get staff member associated with PIN"""
        try:
            staff = self.storage_service.load_data('staff.json')
            # For now, return admin user for valid PINs
            if self._validate_staff_pin(pin):
                return {
                    'id': 'STF001',
                    'full_name': 'SPANKKS Admin',
                    'role': 'admin',
                    'permissions': ['all']
                }
        except:
            pass
        return None
    
    def validate_session(self, session_data: Dict) -> bool:
        """Validate if session is still active"""
        try:
            expires_at = datetime.fromisoformat(session_data.get('expires_at', ''))
            return datetime.now() < expires_at
        except:
            return False
    
    def extend_session(self, session_data: Dict) -> Dict:
        """Extend session expiration"""
        extension_time = self.session_timeout
        if session_data.get('access_level') == 'staff':
            extension_time *= 2  # Staff sessions last longer
        
        session_data['expires_at'] = (datetime.now() + timedelta(seconds=extension_time)).isoformat()
        return session_data
    
    def logout_session(self, session_data: Dict) -> Dict:
        """Logout and invalidate session"""
        try:
            self._log_logout(session_data)
            return {'success': True}
        except Exception as e:
            logging.error(f"Logout error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_portal_access_data(self, client_id: str, job_id: str, access_level: str) -> Dict:
        """Get data accessible to portal user based on access level"""
        try:
            data = {
                'client_info': self._get_client_info(client_id),
                'job_info': self._get_job_info(job_id),
                'quotes': self._get_client_quotes(client_id),
                'invoices': self._get_client_invoices(client_id),
                'photos': self._get_job_photos(job_id, access_level),
                'messages': self._get_client_messages(client_id)
            }
            
            # Staff get additional access
            if access_level == 'staff':
                data.update({
                    'staff_tools': True,
                    'job_management': self._get_job_management_data(job_id),
                    'materials_tracking': self._get_materials_data(job_id),
                    'time_tracking': self._get_time_tracking_data(),
                    'all_jobs': self._get_all_jobs_summary()
                })
            
            return data
            
        except Exception as e:
            logging.error(f"Error getting portal data: {e}")
            return {}
    
    def _get_client_info(self, client_id: str) -> Dict:
        """Get client information"""
        try:
            contacts = self.storage_service.get_all_contacts()
            client = next((c for c in contacts if c.get('id') == client_id), None)
            return client or {}
        except:
            return {}
    
    def _get_job_info(self, job_id: str) -> Dict:
        """Get job information"""
        try:
            appointments = self.storage_service.load_data('unified_appointments.json')
            job = next((a for a in appointments if a.get('job_id') == job_id), None)
            return job or {}
        except:
            return {}
    
    def _get_client_quotes(self, client_id: str) -> List[Dict]:
        """Get quotes for client"""
        try:
            quotes = self.storage_service.get_all_quotes()
            # Match by client name or ID
            client_info = self._get_client_info(client_id)
            client_name = client_info.get('name', '')
            
            client_quotes = []
            for quote in quotes:
                if (quote.get('client_name') == client_name or 
                    quote.get('client_id') == client_id):
                    client_quotes.append(quote)
            
            return client_quotes
        except:
            return []
    
    def _get_client_invoices(self, client_id: str) -> List[Dict]:
        """Get invoices for client"""
        try:
            invoices = self.storage_service.load_data('invoices.json')
            client_info = self._get_client_info(client_id)
            client_name = client_info.get('name', '')
            
            client_invoices = []
            for invoice in invoices:
                if (invoice.get('client_name') == client_name or 
                    invoice.get('client_id') == client_id):
                    client_invoices.append(invoice)
            
            return client_invoices
        except:
            return []
    
    def _get_job_photos(self, job_id: str, access_level: str) -> List[Dict]:
        """Get job photos based on access level"""
        try:
            photos = self.storage_service.load_data('job_photos.json')
            job_photos = [p for p in photos if p.get('job_id') == job_id]
            
            # Filter sensitive metadata for client access
            if access_level == 'client':
                for photo in job_photos:
                    # Remove staff-only metadata
                    photo.pop('uploaded_by', None)
                    photo.pop('file_path', None)
                    photo.pop('device_info', None)
            
            return job_photos
        except:
            return []
    
    def _get_client_messages(self, client_id: str) -> List[Dict]:
        """Get messages for client"""
        try:
            contacts = self.storage_service.get_all_contacts()
            client = next((c for c in contacts if c.get('id') == client_id), None)
            if client:
                return [client]  # Return contact as message
            return []
        except:
            return []
    
    def _get_job_management_data(self, job_id: str) -> Dict:
        """Get job management data for staff"""
        return {
            'checklists': [],
            'materials': [],
            'time_entries': [],
            'notes': []
        }
    
    def _get_materials_data(self, job_id: str) -> List[Dict]:
        """Get materials data for job"""
        return []
    
    def _get_time_tracking_data(self) -> Dict:
        """Get time tracking data"""
        return {
            'current_entries': [],
            'today_total': 0.0
        }
    
    def _get_all_jobs_summary(self) -> List[Dict]:
        """Get summary of all jobs for staff"""
        try:
            appointments = self.storage_service.load_data('unified_appointments.json')
            return appointments[:10]  # Return recent 10 jobs
        except:
            return []
    
    def _log_login_attempt(self, user_id: str, portal_type: str, success: bool, error: str = None):
        """Log login attempts for security"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'portal_type': portal_type,
                'success': success,
                'error': error,
                'ip_address': request.remote_addr if request else None,
                'user_agent': request.headers.get('User-Agent') if request else None
            }
            
            logs = self.storage_service.load_data('auth_log.json')
            logs.append(log_entry)
            
            # Keep only last 1000 entries
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            self.storage_service.save_data('auth_log.json', logs)
            
        except Exception as e:
            logging.error(f"Error logging login attempt: {e}")
    
    def _log_logout(self, session_data: Dict):
        """Log logout events"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'user_id': session_data.get('client_id', 'unknown'),
                'access_level': session_data.get('access_level', 'unknown'),
                'session_duration': self._calculate_session_duration(session_data),
                'ip_address': request.remote_addr if request else None
            }
            
            logs = self.storage_service.load_data('logout_log.json')
            logs.append(log_entry)
            self.storage_service.save_data('logout_log.json', logs)
            
        except Exception as e:
            logging.error(f"Error logging logout: {e}")
    
    def _calculate_session_duration(self, session_data: Dict) -> float:
        """Calculate session duration in minutes"""
        try:
            login_time = datetime.fromisoformat(session_data.get('login_time', ''))
            duration = (datetime.now() - login_time).total_seconds() / 60
            return round(duration, 2)
        except:
            return 0.0
    
    def get_security_stats(self) -> Dict:
        """Get security and access statistics"""
        try:
            auth_logs = self.storage_service.load_data('auth_log.json')
            
            today = datetime.now().date()
            today_logs = [log for log in auth_logs 
                         if datetime.fromisoformat(log['timestamp']).date() == today]
            
            return {
                'total_logins_today': len(today_logs),
                'successful_logins': len([log for log in today_logs if log['success']]),
                'failed_logins': len([log for log in today_logs if not log['success']]),
                'client_logins': len([log for log in today_logs if log['portal_type'] == 'client_portal']),
                'staff_logins': len([log for log in today_logs if log['portal_type'] == 'staff_portal']),
                'unique_users': len(set(log['user_id'] for log in today_logs))
            }
            
        except Exception as e:
            logging.error(f"Error getting security stats: {e}")
            return {
                'total_logins_today': 0,
                'successful_logins': 0,
                'failed_logins': 0,
                'client_logins': 0,
                'staff_logins': 0,
                'unique_users': 0
            }