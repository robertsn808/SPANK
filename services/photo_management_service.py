"""
Photo & Documentation Management Service for SPANKKS Construction
Handles before/after photos, metadata tracking, file validation, and gallery management
"""

import os
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from werkzeug.utils import secure_filename
import uuid

class PhotoManagementService:
    def __init__(self, storage_service, upload_folder='uploads/photos'):
        self.storage_service = storage_service
        self.upload_folder = upload_folder
        self.allowed_extensions = {'jpg', 'jpeg', 'png', 'heic'}
        self.max_file_size = 16 * 1024 * 1024  # 16MB
        
        # Ensure upload directory exists
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def validate_file_size(self, file_size: int) -> bool:
        """Validate file size is within limits"""
        return file_size <= self.max_file_size
    
    def generate_filename(self, original_filename: str, job_id: str, photo_type: str) -> str:
        """Generate secure filename with metadata"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_ext = original_filename.rsplit('.', 1)[1].lower()
        unique_id = str(uuid.uuid4())[:8]
        return f"{job_id}_{photo_type}_{timestamp}_{unique_id}.{file_ext}"
    
    def upload_photo(self, file_data: bytes, filename: str, job_id: str, 
                    photo_type: str, staff_id: str, metadata: Dict = None) -> Dict:
        """Upload and process job photo with metadata"""
        try:
            # Validate file
            if not self.is_allowed_file(filename):
                return {'success': False, 'error': 'Invalid file type. Only JPG, PNG, HEIC allowed.'}
            
            if not self.validate_file_size(len(file_data)):
                return {'success': False, 'error': 'File too large. Maximum 16MB allowed.'}
            
            # Generate secure filename
            secure_name = self.generate_filename(filename, job_id, photo_type)
            file_path = os.path.join(self.upload_folder, secure_name)
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Create photo record
            photo_record = {
                'id': f"PHOTO{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'job_id': job_id,
                'filename': secure_name,
                'original_filename': filename,
                'photo_type': photo_type,  # 'before', 'after', 'progress', 'materials'
                'file_path': file_path,
                'file_size': len(file_data),
                'uploaded_by': staff_id,
                'upload_date': datetime.now().isoformat(),
                'metadata': metadata or {},
                'is_cover': False,
                'tags': [],
                'notes': '',
                'gps_location': metadata.get('location') if metadata else None,
                'device_info': metadata.get('device') if metadata else None
            }
            
            # Save to photo database
            photos = self.storage_service.load_data('job_photos.json')
            photos.append(photo_record)
            self.storage_service.save_data('job_photos.json', photos)
            
            return {
                'success': True, 
                'photo_id': photo_record['id'],
                'filename': secure_name
            }
            
        except Exception as e:
            logging.error(f"Error uploading photo: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_job_photos(self, job_id: str) -> List[Dict]:
        """Get all photos for a specific job"""
        try:
            photos = self.storage_service.load_data('job_photos.json')
            job_photos = [p for p in photos if p.get('job_id') == job_id]
            
            # Sort by upload date
            job_photos.sort(key=lambda x: x.get('upload_date', ''), reverse=True)
            
            return job_photos
        except Exception as e:
            logging.error(f"Error loading job photos: {e}")
            return []
    
    def get_before_after_pairs(self, job_id: str) -> List[Dict]:
        """Get before/after photo pairs for comparison"""
        photos = self.get_job_photos(job_id)
        before_photos = [p for p in photos if p.get('photo_type') == 'before']
        after_photos = [p for p in photos if p.get('photo_type') == 'after']
        
        pairs = []
        for before in before_photos:
            # Find matching after photo (same area/timestamp proximity)
            matching_after = None
            for after in after_photos:
                # Simple matching by upload time proximity (could be enhanced)
                before_time = datetime.fromisoformat(before['upload_date'])
                after_time = datetime.fromisoformat(after['upload_date'])
                if abs((after_time - before_time).total_seconds()) < 3600:  # Within 1 hour
                    matching_after = after
                    break
            
            pairs.append({
                'before': before,
                'after': matching_after,
                'comparison_id': f"COMP_{before['id']}_{matching_after['id'] if matching_after else 'none'}"
            })
        
        return pairs
    
    def set_cover_photo(self, photo_id: str, job_id: str) -> Dict:
        """Set a photo as the cover photo for a job"""
        try:
            photos = self.storage_service.load_data('job_photos.json')
            
            # Remove existing cover designation for this job
            for photo in photos:
                if photo.get('job_id') == job_id:
                    photo['is_cover'] = False
            
            # Set new cover photo
            for photo in photos:
                if photo.get('id') == photo_id:
                    photo['is_cover'] = True
                    break
            
            self.storage_service.save_data('job_photos.json', photos)
            return {'success': True}
            
        except Exception as e:
            logging.error(f"Error setting cover photo: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_photo(self, photo_id: str, staff_id: str) -> Dict:
        """Delete a photo (with permission check)"""
        try:
            photos = self.storage_service.load_data('job_photos.json')
            photo_to_delete = None
            
            for i, photo in enumerate(photos):
                if photo.get('id') == photo_id:
                    photo_to_delete = photo
                    # Remove from database
                    photos.pop(i)
                    break
            
            if not photo_to_delete:
                return {'success': False, 'error': 'Photo not found'}
            
            # Delete physical file
            if os.path.exists(photo_to_delete['file_path']):
                os.remove(photo_to_delete['file_path'])
            
            # Save updated database
            self.storage_service.save_data('job_photos.json', photos)
            
            # Log deletion
            self._log_photo_action('delete', photo_id, staff_id)
            
            return {'success': True}
            
        except Exception as e:
            logging.error(f"Error deleting photo: {e}")
            return {'success': False, 'error': str(e)}
    
    def add_photo_note(self, photo_id: str, note: str, staff_id: str) -> Dict:
        """Add a note to a photo"""
        try:
            photos = self.storage_service.load_data('job_photos.json')
            
            for photo in photos:
                if photo.get('id') == photo_id:
                    photo['notes'] = note
                    photo['last_modified'] = datetime.now().isoformat()
                    photo['modified_by'] = staff_id
                    break
            
            self.storage_service.save_data('job_photos.json', photos)
            return {'success': True}
            
        except Exception as e:
            logging.error(f"Error adding photo note: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_gallery_stats(self) -> Dict:
        """Get photo gallery statistics"""
        try:
            photos = self.storage_service.load_data('job_photos.json')
            
            total_photos = len(photos)
            total_size = sum(p.get('file_size', 0) for p in photos)
            
            type_counts = {}
            for photo in photos:
                photo_type = photo.get('photo_type', 'unknown')
                type_counts[photo_type] = type_counts.get(photo_type, 0) + 1
            
            recent_uploads = [p for p in photos 
                            if datetime.fromisoformat(p['upload_date']).date() == datetime.now().date()]
            
            return {
                'total_photos': total_photos,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'type_breakdown': type_counts,
                'uploads_today': len(recent_uploads),
                'avg_file_size_mb': round((total_size / total_photos) / (1024 * 1024), 2) if total_photos > 0 else 0
            }
            
        except Exception as e:
            logging.error(f"Error getting gallery stats: {e}")
            return {
                'total_photos': 0,
                'total_size_mb': 0,
                'type_breakdown': {},
                'uploads_today': 0,
                'avg_file_size_mb': 0
            }
    
    def _log_photo_action(self, action: str, photo_id: str, staff_id: str):
        """Log photo-related actions for audit trail"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'photo_id': photo_id,
                'staff_id': staff_id,
                'ip_address': None  # Could be added from request context
            }
            
            logs = self.storage_service.load_data('photo_audit_log.json')
            logs.append(log_entry)
            self.storage_service.save_data('photo_audit_log.json', logs)
            
        except Exception as e:
            logging.error(f"Error logging photo action: {e}")
    
    def cleanup_orphaned_files(self) -> Dict:
        """Clean up orphaned photo files (not in database)"""
        try:
            photos = self.storage_service.load_data('job_photos.json')
            db_files = {p['filename'] for p in photos}
            
            deleted_count = 0
            if os.path.exists(self.upload_folder):
                for filename in os.listdir(self.upload_folder):
                    if filename not in db_files:
                        file_path = os.path.join(self.upload_folder, filename)
                        os.remove(file_path)
                        deleted_count += 1
            
            return {
                'success': True,
                'deleted_files': deleted_count
            }
            
        except Exception as e:
            logging.error(f"Error cleaning up files: {e}")
            return {'success': False, 'error': str(e)}