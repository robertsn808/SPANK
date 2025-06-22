"""
Photo upload service for job documentation
Handles before/after photos for construction jobs with metadata tracking
"""

import os
import json
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import uuid

# Configure allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heic', 'heif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size

class PhotoUploadService:
    """Service for handling job photo uploads with metadata"""
    
    def __init__(self, base_upload_dir="uploads"):
        self.base_upload_dir = base_upload_dir
        self.ensure_upload_directory()
        
    def ensure_upload_directory(self):
        """Ensure the base upload directory exists"""
        if not os.path.exists(self.base_upload_dir):
            os.makedirs(self.base_upload_dir, exist_ok=True)
            
    def allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def get_job_directory(self, job_id, photo_type):
        """Get the directory path for a specific job and photo type"""
        return os.path.join(self.base_upload_dir, "jobs", str(job_id), photo_type)
    
    def ensure_job_directory(self, job_id, photo_type):
        """Ensure job directory exists"""
        directory = self.get_job_directory(job_id, photo_type)
        os.makedirs(directory, exist_ok=True)
        return directory
    
    def save_photo(self, file, job_id, photo_type, metadata=None):
        """
        Save uploaded photo with metadata
        
        Args:
            file: FileStorage object from Flask request
            job_id: Job identifier
            photo_type: 'before' or 'after'
            metadata: Optional metadata dict
            
        Returns:
            dict: Upload result with file info
        """
        try:
            if not file or file.filename == '':
                return {'error': 'No file provided'}
                
            if not self.allowed_file(file.filename):
                return {'error': 'File type not allowed'}
                
            # Check file size
            file.seek(0, 2)  # Seek to end
            size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if size > MAX_FILE_SIZE:
                return {'error': 'File too large (max 16MB)'}
            
            # Generate secure filename
            original_filename = secure_filename(file.filename)
            file_extension = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{file_extension}"
            
            # Ensure directory exists
            directory = self.ensure_job_directory(job_id, photo_type)
            file_path = os.path.join(directory, unique_filename)
            
            # Save file
            file.save(file_path)
            
            # Prepare metadata
            file_metadata = {
                'original_filename': original_filename,
                'saved_filename': unique_filename,
                'file_path': file_path,
                'file_size': size,
                'upload_date': datetime.now().isoformat(),
                'job_id': str(job_id),
                'photo_type': photo_type,
                'file_extension': file_extension
            }
            
            # Add custom metadata if provided
            if metadata:
                file_metadata.update(metadata)
            
            # Save metadata
            self.save_metadata(job_id, photo_type, unique_filename, file_metadata)
            
            return {
                'success': True,
                'filename': unique_filename,
                'file_path': file_path,
                'file_size': size,
                'metadata': file_metadata
            }
            
        except Exception as e:
            logging.error(f"Error saving photo: {e}")
            return {'error': f'Upload failed: {str(e)}'}
    
    def save_metadata(self, job_id, photo_type, filename, metadata):
        """Save photo metadata to JSON file"""
        try:
            metadata_dir = self.get_job_directory(job_id, photo_type)
            metadata_file = os.path.join(metadata_dir, 'metadata.json')
            
            # Load existing metadata
            existing_metadata = {}
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    existing_metadata = json.load(f)
            
            # Add new metadata
            existing_metadata[filename] = metadata
            
            # Save updated metadata
            with open(metadata_file, 'w') as f:
                json.dump(existing_metadata, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error saving metadata: {e}")
    
    def get_job_photos(self, job_id, photo_type=None):
        """Get all photos for a job"""
        try:
            if photo_type:
                photo_types = [photo_type]
            else:
                photo_types = ['before', 'after']
            
            result = {}
            
            for ptype in photo_types:
                result[ptype] = []
                metadata_file = os.path.join(self.get_job_directory(job_id, ptype), 'metadata.json')
                
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        result[ptype] = list(metadata.values())
            
            return result
            
        except Exception as e:
            logging.error(f"Error getting job photos: {e}")
            return {}
    
    def delete_photo(self, job_id, photo_type, filename):
        """Delete a specific photo and its metadata"""
        try:
            # Delete file
            file_path = os.path.join(self.get_job_directory(job_id, photo_type), filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Remove from metadata
            metadata_file = os.path.join(self.get_job_directory(job_id, photo_type), 'metadata.json')
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                if filename in metadata:
                    del metadata[filename]
                
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            return {'success': True}
            
        except Exception as e:
            logging.error(f"Error deleting photo: {e}")
            return {'error': f'Delete failed: {str(e)}'}

# Global instance
photo_service = PhotoUploadService()