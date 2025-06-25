"""
Portal Service for SPANKKS Construction
Handles client and staff portal functionality with comprehensive job management
"""

import json
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import os

class PortalService:
    """Professional portal management system for clients and staff"""
    
    def __init__(self):
        self.db_url = os.environ.get('DATABASE_URL')
        
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
    
    # Client Portal Methods
    def get_client_portal_overview(self, client_id: str) -> Dict[str, Any]:
        """Get comprehensive client portal overview"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get client information
                    cursor.execute("""
                        SELECT client_id, name, email, phone, address
                        FROM clients WHERE client_id = %s
                    """, (client_id,))
                    client = cursor.fetchone()
                    
                    if not client:
                        return {'success': False, 'message': 'Client not found'}
                    
                    # Get jobs
                    cursor.execute("""
                        SELECT job_id, service_type, status, scheduled_date, 
                               crew_assigned, completion_date, total_cost
                        FROM jobs WHERE client_id = %s 
                        ORDER BY scheduled_date DESC
                    """, (client_id,))
                    jobs = [dict(job) for job in cursor.fetchall()]
                    
                    # Get quotes
                    cursor.execute("""
                        SELECT quote_number, total_amount, tax_amount, status, 
                               created_at, message
                        FROM quotes WHERE client_id = %s 
                        ORDER BY created_at DESC
                    """, (client_id,))
                    quotes = [dict(quote) for quote in cursor.fetchall()]
                    
                    # Get invoices
                    cursor.execute("""
                        SELECT invoice_number, total_amount, amount_paid, 
                               due_date, status, created_at
                        FROM invoices WHERE client_id = %s 
                        ORDER BY created_at DESC
                    """, (client_id,))
                    invoices = [dict(invoice) for invoice in cursor.fetchall()]
                    
                    return {
                        'success': True,
                        'client': dict(client),
                        'jobs': jobs,
                        'quotes': quotes,
                        'invoices': invoices,
                        'summary': {
                            'total_jobs': len(jobs),
                            'active_jobs': len([j for j in jobs if j['status'] in ['scheduled', 'in_progress']]),
                            'pending_quotes': len([q for q in quotes if q['status'] == 'pending']),
                            'outstanding_invoices': len([i for i in invoices if i['status'] != 'paid'])
                        }
                    }
                    
        except Exception as e:
            logging.error(f"Error getting client portal overview: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_client_job_photos(self, client_id: str, job_id: str = None) -> List[Dict]:
        """Get job photos for client portal"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    if job_id:
                        cursor.execute("""
                            SELECT jp.id, jp.job_id, jp.photo_url, jp.label, 
                                   jp.stage, jp.uploaded_at, j.service_type
                            FROM job_photos jp
                            JOIN jobs j ON j.job_id = jp.job_id
                            WHERE j.client_id = %s AND jp.job_id = %s
                            ORDER BY jp.uploaded_at DESC
                        """, (client_id, job_id))
                    else:
                        cursor.execute("""
                            SELECT jp.id, jp.job_id, jp.photo_url, jp.label, 
                                   jp.stage, jp.uploaded_at, j.service_type
                            FROM job_photos jp
                            JOIN jobs j ON j.job_id = jp.job_id
                            WHERE j.client_id = %s
                            ORDER BY jp.uploaded_at DESC
                        """, (client_id,))
                    
                    return [dict(photo) for photo in cursor.fetchall()]
                    
        except Exception as e:
            logging.error(f"Error getting client job photos: {e}")
            return []
    
    def get_client_job_notes(self, client_id: str, job_id: str) -> List[Dict]:
        """Get client-facing job notes"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT jn.note, jn.created_by, jn.created_at
                        FROM job_notes jn
                        JOIN jobs j ON j.job_id = jn.job_id
                        WHERE j.client_id = %s AND jn.job_id = %s 
                        AND jn.note_type = 'client_facing'
                        ORDER BY jn.created_at DESC
                    """, (client_id, job_id))
                    
                    return [dict(note) for note in cursor.fetchall()]
                    
        except Exception as e:
            logging.error(f"Error getting client job notes: {e}")
            return []
    
    # Staff Portal Methods
    def get_staff_job_details(self, job_id: str) -> Dict[str, Any]:
        """Get comprehensive job details for staff portal"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get job information
                    cursor.execute("""
                        SELECT j.*, c.name as client_name, c.email as client_email, 
                               c.phone as client_phone, c.address as client_address
                        FROM jobs j
                        JOIN clients c ON c.client_id = j.client_id
                        WHERE j.job_id = %s
                    """, (job_id,))
                    job = cursor.fetchone()
                    
                    if not job:
                        return {'success': False, 'message': 'Job not found'}
                    
                    # Get checklist
                    cursor.execute("""
                        SELECT id, task, is_completed, completed_at, created_by
                        FROM job_checklists WHERE job_id = %s ORDER BY id
                    """, (job_id,))
                    checklist = [dict(item) for item in cursor.fetchall()]
                    
                    # Get photos
                    cursor.execute("""
                        SELECT id, photo_url, label, stage, uploaded_at, uploaded_by
                        FROM job_photos WHERE job_id = %s ORDER BY uploaded_at DESC
                    """, (job_id,))
                    photos = [dict(photo) for photo in cursor.fetchall()]
                    
                    # Get notes
                    cursor.execute("""
                        SELECT id, note, note_type, created_by, created_at
                        FROM job_notes WHERE job_id = %s ORDER BY created_at DESC
                    """, (job_id,))
                    notes = [dict(note) for note in cursor.fetchall()]
                    
                    # Get materials
                    cursor.execute("""
                        SELECT id, material_name, quantity_used, cost_per_unit, 
                               unit_type, added_by, added_at
                        FROM materials_used WHERE job_id = %s ORDER BY added_at DESC
                    """, (job_id,))
                    materials = [dict(material) for material in cursor.fetchall()]
                    
                    # Get timeclock records
                    cursor.execute("""
                        SELECT id, staff_name, clock_in, clock_out, total_hours, 
                               hourly_rate, notes
                        FROM staff_timeclock WHERE job_id = %s ORDER BY clock_in DESC
                    """, (job_id,))
                    timeclock = [dict(record) for record in cursor.fetchall()]
                    
                    return {
                        'success': True,
                        'job': dict(job),
                        'checklist': checklist,
                        'photos': photos,
                        'notes': notes,
                        'materials': materials,
                        'timeclock': timeclock
                    }
                    
        except Exception as e:
            logging.error(f"Error getting staff job details: {e}")
            return {'success': False, 'message': str(e)}
    
    def add_checklist_item(self, job_id: str, task: str, created_by: str) -> Dict[str, Any]:
        """Add new checklist item to job"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO job_checklists (job_id, task, created_by)
                        VALUES (%s, %s, %s) RETURNING id
                    """, (job_id, task, created_by))
                    
                    item_id = cursor.fetchone()['id']
                    conn.commit()
                    
                    return {
                        'success': True,
                        'message': 'Checklist item added successfully',
                        'item_id': item_id
                    }
                    
        except Exception as e:
            logging.error(f"Error adding checklist item: {e}")
            return {'success': False, 'message': str(e)}
    
    def update_checklist_item(self, item_id: int, is_completed: bool, completed_by: str = None) -> Dict[str, Any]:
        """Update checklist item completion status"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    if is_completed:
                        cursor.execute("""
                            UPDATE job_checklists 
                            SET is_completed = %s, completed_at = CURRENT_TIMESTAMP
                            WHERE id = %s
                        """, (is_completed, item_id))
                    else:
                        cursor.execute("""
                            UPDATE job_checklists 
                            SET is_completed = %s, completed_at = NULL
                            WHERE id = %s
                        """, (is_completed, item_id))
                    
                    conn.commit()
                    
                    return {
                        'success': True,
                        'message': 'Checklist item updated successfully'
                    }
                    
        except Exception as e:
            logging.error(f"Error updating checklist item: {e}")
            return {'success': False, 'message': str(e)}
    
    def add_job_note(self, job_id: str, note: str, note_type: str, created_by: str) -> Dict[str, Any]:
        """Add job note"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO job_notes (job_id, note, note_type, created_by)
                        VALUES (%s, %s, %s, %s) RETURNING id
                    """, (job_id, note, note_type, created_by))
                    
                    note_id = cursor.fetchone()['id']
                    conn.commit()
                    
                    return {
                        'success': True,
                        'message': 'Job note added successfully',
                        'note_id': note_id
                    }
                    
        except Exception as e:
            logging.error(f"Error adding job note: {e}")
            return {'success': False, 'message': str(e)}
    
    def add_material_used(self, job_id: str, material_name: str, quantity: float, 
                         cost_per_unit: float, unit_type: str, added_by: str) -> Dict[str, Any]:
        """Add material usage record"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO materials_used 
                        (job_id, material_name, quantity_used, cost_per_unit, unit_type, added_by)
                        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                    """, (job_id, material_name, quantity, cost_per_unit, unit_type, added_by))
                    
                    material_id = cursor.fetchone()['id']
                    conn.commit()
                    
                    return {
                        'success': True,
                        'message': 'Material usage recorded successfully',
                        'material_id': material_id
                    }
                    
        except Exception as e:
            logging.error(f"Error adding material usage: {e}")
            return {'success': False, 'message': str(e)}
    
    def clock_staff_time(self, job_id: str, staff_id: str, staff_name: str, 
                        action: str, hourly_rate: float = None, notes: str = None) -> Dict[str, Any]:
        """Handle staff clock in/out"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    if action == 'clock_in':
                        cursor.execute("""
                            INSERT INTO staff_timeclock (job_id, staff_id, staff_name, clock_in, hourly_rate, notes)
                            VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s) RETURNING id
                        """, (job_id, staff_id, staff_name, hourly_rate, notes))
                        
                        record_id = cursor.fetchone()['id']
                        
                    elif action == 'clock_out':
                        # Find the most recent unclosed clock-in record
                        cursor.execute("""
                            SELECT id, clock_in, hourly_rate FROM staff_timeclock 
                            WHERE job_id = %s AND staff_id = %s AND clock_out IS NULL
                            ORDER BY clock_in DESC LIMIT 1
                        """, (job_id, staff_id))
                        
                        record = cursor.fetchone()
                        if not record:
                            return {'success': False, 'message': 'No open clock-in record found'}
                        
                        # Calculate total hours
                        cursor.execute("""
                            UPDATE staff_timeclock 
                            SET clock_out = CURRENT_TIMESTAMP,
                                total_hours = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - clock_in)) / 3600
                            WHERE id = %s
                        """, (record['id'],))
                        
                        record_id = record['id']
                    
                    conn.commit()
                    
                    return {
                        'success': True,
                        'message': f'Successfully {action.replace("_", " ")}',
                        'record_id': record_id
                    }
                    
        except Exception as e:
            logging.error(f"Error with staff timeclock: {e}")
            return {'success': False, 'message': str(e)}
    
    def generate_portal_access_token(self, client_id: str, access_type: str, 
                                   expires_days: int = 30) -> Dict[str, Any]:
        """Generate secure portal access token"""
        try:
            # Generate secure token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(days=expires_days)
            
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO portal_access (client_id, access_type, access_token, expires_at)
                        VALUES (%s, %s, %s, %s) RETURNING id
                    """, (client_id, access_type, token, expires_at))
                    
                    access_id = cursor.fetchone()['id']
                    conn.commit()
                    
                    return {
                        'success': True,
                        'access_token': token,
                        'expires_at': expires_at.isoformat(),
                        'access_id': access_id
                    }
                    
        except Exception as e:
            logging.error(f"Error generating portal access token: {e}")
            return {'success': False, 'message': str(e)}
    
    def validate_portal_access(self, token: str) -> Dict[str, Any]:
        """Validate portal access token"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT client_id, access_type, expires_at, is_active
                        FROM portal_access 
                        WHERE access_token = %s
                    """, (token,))
                    
                    access = cursor.fetchone()
                    
                    if not access:
                        return {'success': False, 'message': 'Invalid access token'}
                    
                    if not access['is_active']:
                        return {'success': False, 'message': 'Access token has been revoked'}
                    
                    if access['expires_at'] and access['expires_at'] < datetime.now():
                        return {'success': False, 'message': 'Access token has expired'}
                    
                    # Update last accessed
                    cursor.execute("""
                        UPDATE portal_access 
                        SET last_accessed = CURRENT_TIMESTAMP
                        WHERE access_token = %s
                    """, (token,))
                    conn.commit()
                    
                    return {
                        'success': True,
                        'client_id': access['client_id'],
                        'access_type': access['access_type']
                    }
                    
        except Exception as e:
            logging.error(f"Error validating portal access: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_job_progress_summary(self, job_id: str) -> Dict[str, Any]:
        """Get job progress summary for client portal"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get checklist completion
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_tasks,
                            COUNT(CASE WHEN is_completed THEN 1 END) as completed_tasks
                        FROM job_checklists WHERE job_id = %s
                    """, (job_id,))
                    
                    checklist_data = cursor.fetchone()
                    
                    # Get photo counts
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_photos,
                            COUNT(CASE WHEN stage = 'before' THEN 1 END) as before_photos,
                            COUNT(CASE WHEN stage = 'after' THEN 1 END) as after_photos
                        FROM job_photos WHERE job_id = %s
                    """, (job_id,))
                    
                    photo_data = cursor.fetchone()
                    
                    # Calculate progress percentage
                    total_tasks = checklist_data['total_tasks'] or 0
                    completed_tasks = checklist_data['completed_tasks'] or 0
                    progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                    
                    return {
                        'success': True,
                        'progress_percentage': round(progress_percentage, 1),
                        'checklist': {
                            'total_tasks': total_tasks,
                            'completed_tasks': completed_tasks
                        },
                        'photos': {
                            'total_photos': photo_data['total_photos'] or 0,
                            'before_photos': photo_data['before_photos'] or 0,
                            'after_photos': photo_data['after_photos'] or 0
                        }
                    }
                    
        except Exception as e:
            logging.error(f"Error getting job progress summary: {e}")
            return {'success': False, 'message': str(e)}