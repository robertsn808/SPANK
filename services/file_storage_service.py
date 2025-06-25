"""
File Storage Service for SPANKKS Construction
Handles secure file storage for invoices, photos, and documents with backup capabilities
"""

import json
import logging
import os
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

class FileStorageService:
    """Manages file storage, organization, and backups for business documents"""
    
    def __init__(self):
        self.base_storage_path = Path('storage')
        self.backup_path = Path('backups')
        self.metadata_file = 'data/file_metadata.json'
        self._ensure_storage_structure()
    
    def _ensure_storage_structure(self):
        """Create storage directory structure"""
        storage_dirs = [
            'storage/invoices',
            'storage/quotes',
            'storage/photos/before',
            'storage/photos/after',
            'storage/photos/progress',
            'storage/documents/contracts',
            'storage/documents/permits',
            'storage/documents/receipts',
            'storage/temp',
            'backups/daily',
            'backups/weekly',
            'backups/monthly',
            'data'
        ]
        
        for directory in storage_dirs:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Ensure metadata file exists
        if not os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'w') as f:
                json.dump([], f, indent=2)
    
    def store_file(self, file_path: str, category: str, metadata: Dict) -> Dict:
        """Store file with metadata and return storage information"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Source file not found: {file_path}")
            
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_hash = self._calculate_file_hash(file_path)
            safe_filename = self._sanitize_filename(file_path.name)
            
            unique_filename = f"{timestamp}_{file_hash[:8]}_{safe_filename}"
            
            # Determine storage location based on category
            storage_location = self._get_storage_location(category, unique_filename)
            
            # Copy file to storage
            shutil.copy2(file_path, storage_location)
            
            # Create metadata record
            file_record = {
                'id': f"file_{int(datetime.now().timestamp())}",
                'original_name': file_path.name,
                'stored_name': unique_filename,
                'storage_path': str(storage_location),
                'category': category,
                'file_hash': file_hash,
                'file_size': file_path.stat().st_size,
                'upload_date': datetime.now().isoformat(),
                'metadata': metadata
            }
            
            # Save metadata
            self._save_file_metadata(file_record)
            
            logging.info(f"File stored: {unique_filename} in category {category}")
            
            return {
                'success': True,
                'file_id': file_record['id'],
                'storage_path': str(storage_location),
                'file_url': f"/storage/{category}/{unique_filename}"
            }
            
        except Exception as e:
            logging.error(f"Error storing file: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_file_info(self, file_id: str) -> Optional[Dict]:
        """Get file information by ID"""
        try:
            metadata = self._load_file_metadata()
            for record in metadata:
                if record['id'] == file_id:
                    return record
            return None
            
        except Exception as e:
            logging.error(f"Error getting file info: {e}")
            return None
    
    def get_files_by_category(self, category: str, limit: Optional[int] = None) -> List[Dict]:
        """Get files by category with optional limit"""
        try:
            metadata = self._load_file_metadata()
            category_files = [record for record in metadata if record['category'] == category]
            
            # Sort by upload date, most recent first
            category_files.sort(key=lambda x: x['upload_date'], reverse=True)
            
            if limit:
                category_files = category_files[:limit]
            
            return category_files
            
        except Exception as e:
            logging.error(f"Error getting files by category: {e}")
            return []
    
    def get_files_by_job(self, job_id: str) -> List[Dict]:
        """Get all files related to a specific job"""
        try:
            metadata = self._load_file_metadata()
            job_files = []
            
            for record in metadata:
                if record['metadata'].get('job_id') == job_id:
                    job_files.append(record)
            
            # Sort by upload date, most recent first
            job_files.sort(key=lambda x: x['upload_date'], reverse=True)
            
            return job_files
            
        except Exception as e:
            logging.error(f"Error getting files by job: {e}")
            return []
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file and its metadata"""
        try:
            metadata = self._load_file_metadata()
            file_record = None
            
            for i, record in enumerate(metadata):
                if record['id'] == file_id:
                    file_record = record
                    metadata.pop(i)
                    break
            
            if not file_record:
                return False
            
            # Delete physical file
            file_path = Path(file_record['storage_path'])
            if file_path.exists():
                file_path.unlink()
            
            # Save updated metadata
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logging.info(f"File deleted: {file_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error deleting file: {e}")
            return False
    
    def create_backup(self, backup_type: str = 'daily') -> Dict:
        """Create backup of all business data"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"spankks_backup_{backup_type}_{timestamp}.zip"
            backup_path = self.backup_path / backup_type / backup_filename
            
            # Ensure backup directory exists
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create zip file with all important data
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Backup JSON data files
                data_files = [
                    'data/contacts.json',
                    'data/quotes.json',
                    'data/invoices.json',
                    'data/jobs.json',
                    'data/staff.json',
                    'data/inventory.json',
                    'data/checklists.json',
                    'data/appointments.json',
                    'data/communications.json',
                    'data/reminders.json',
                    'data/file_metadata.json'
                ]
                
                for data_file in data_files:
                    if os.path.exists(data_file):
                        zipf.write(data_file)
                
                # Backup storage files
                storage_path = Path('storage')
                if storage_path.exists():
                    for file_path in storage_path.rglob('*'):
                        if file_path.is_file():
                            # Create archive path relative to storage
                            archive_path = file_path.relative_to(storage_path.parent)
                            zipf.write(file_path, archive_path)
            
            # Create backup metadata
            backup_info = {
                'backup_id': f"backup_{int(datetime.now().timestamp())}",
                'backup_type': backup_type,
                'backup_date': datetime.now().isoformat(),
                'backup_file': str(backup_path),
                'file_size': backup_path.stat().st_size,
                'file_count': len(zipf.namelist()) if 'zipf' in locals() else 0
            }
            
            # Save backup metadata
            self._save_backup_metadata(backup_info)
            
            # Clean old backups based on retention policy
            self._cleanup_old_backups(backup_type)
            
            logging.info(f"Backup created: {backup_filename}")
            
            return {
                'success': True,
                'backup_info': backup_info
            }
            
        except Exception as e:
            logging.error(f"Error creating backup: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_storage_statistics(self) -> Dict:
        """Get storage usage statistics"""
        try:
            stats = {
                'total_files': 0,
                'total_size': 0,
                'categories': {},
                'recent_uploads': 0
            }
            
            metadata = self._load_file_metadata()
            week_ago = datetime.now() - timedelta(days=7)
            
            for record in metadata:
                stats['total_files'] += 1
                stats['total_size'] += record.get('file_size', 0)
                
                category = record['category']
                if category not in stats['categories']:
                    stats['categories'][category] = {'count': 0, 'size': 0}
                
                stats['categories'][category]['count'] += 1
                stats['categories'][category]['size'] += record.get('file_size', 0)
                
                # Count recent uploads
                upload_date = datetime.fromisoformat(record['upload_date'])
                if upload_date >= week_ago:
                    stats['recent_uploads'] += 1
            
            # Format sizes for display
            stats['total_size_formatted'] = self._format_file_size(stats['total_size'])
            for category in stats['categories']:
                stats['categories'][category]['size_formatted'] = self._format_file_size(
                    stats['categories'][category]['size']
                )
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting storage statistics: {e}")
            return {
                'total_files': 0,
                'total_size': 0,
                'categories': {},
                'recent_uploads': 0
            }
    
    def _get_storage_location(self, category: str, filename: str) -> Path:
        """Get appropriate storage location for file category"""
        category_paths = {
            'invoice': 'storage/invoices',
            'quote': 'storage/quotes',
            'photo_before': 'storage/photos/before',
            'photo_after': 'storage/photos/after',
            'photo_progress': 'storage/photos/progress',
            'contract': 'storage/documents/contracts',
            'permit': 'storage/documents/permits',
            'receipt': 'storage/documents/receipts'
        }
        
        storage_dir = category_paths.get(category, 'storage/temp')
        return Path(storage_dir) / filename
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file for integrity checking"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 100:
            name, ext = os.path.splitext(filename)
            filename = name[:96] + ext
        
        return filename
    
    def _load_file_metadata(self) -> List[Dict]:
        """Load file metadata from JSON"""
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_file_metadata(self, file_record: Dict):
        """Save file metadata to JSON"""
        metadata = self._load_file_metadata()
        metadata.append(file_record)
        
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _save_backup_metadata(self, backup_info: Dict):
        """Save backup metadata"""
        backup_metadata_file = 'data/backup_metadata.json'
        
        # Load existing backup metadata
        if os.path.exists(backup_metadata_file):
            with open(backup_metadata_file, 'r') as f:
                backup_metadata = json.load(f)
        else:
            backup_metadata = []
        
        backup_metadata.append(backup_info)
        
        with open(backup_metadata_file, 'w') as f:
            json.dump(backup_metadata, f, indent=2)
    
    def _cleanup_old_backups(self, backup_type: str):
        """Clean up old backups based on retention policy"""
        retention_days = {
            'daily': 30,    # Keep 30 days of daily backups
            'weekly': 90,   # Keep 90 days of weekly backups
            'monthly': 365  # Keep 1 year of monthly backups
        }
        
        cutoff_date = datetime.now() - timedelta(days=retention_days.get(backup_type, 30))
        backup_dir = self.backup_path / backup_type
        
        if backup_dir.exists():
            for backup_file in backup_dir.iterdir():
                if backup_file.is_file() and backup_file.stat().st_mtime < cutoff_date.timestamp():
                    try:
                        backup_file.unlink()
                        logging.info(f"Deleted old backup: {backup_file.name}")
                    except Exception as e:
                        logging.error(f"Error deleting old backup {backup_file.name}: {e}")
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f} {size_names[i]}"