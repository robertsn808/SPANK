"""
Job Checklist Management Service for SPANKKS Construction
Handles job checklists, task templates, and completion tracking
"""

import json
import os
from datetime import datetime
import pytz
from models import get_hawaii_time

class ChecklistService:
    """Comprehensive job checklist management system"""
    
    def __init__(self):
        self.checklist_file = 'data/job_checklists.json'
        self.templates_file = 'data/checklist_templates.json'
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Ensure checklist data files exist"""
        if not os.path.exists('data'):
            os.makedirs('data')
            
        if not os.path.exists(self.checklist_file):
            with open(self.checklist_file, 'w') as f:
                json.dump([], f, indent=2)
                
        if not os.path.exists(self.templates_file):
            # Create default templates
            default_templates = [
                {
                    "template_id": "TEMP001",
                    "name": "Standard Job Checklist",
                    "service_type": "General",
                    "tasks": [
                        {"task": "Site assessment completed", "required": True, "order": 1},
                        {"task": "Materials ordered", "required": True, "order": 2},
                        {"task": "Before photos taken", "required": True, "order": 3},
                        {"task": "Work started", "required": True, "order": 4},
                        {"task": "Quality check completed", "required": True, "order": 5},
                        {"task": "After photos taken", "required": True, "order": 6},
                        {"task": "Client walkthrough", "required": True, "order": 7},
                        {"task": "Final cleanup", "required": True, "order": 8}
                    ]
                },
                {
                    "template_id": "TEMP002",
                    "name": "Drywall Services Checklist",
                    "service_type": "Drywall Services",
                    "tasks": [
                        {"task": "Site assessment and measurements", "required": True, "order": 1},
                        {"task": "Materials delivered (drywall, joint compound, tape)", "required": True, "order": 2},
                        {"task": "Before photos taken", "required": True, "order": 3},
                        {"task": "Old drywall removal (if applicable)", "required": False, "order": 4},
                        {"task": "Electrical/plumbing rough-in complete", "required": False, "order": 5},
                        {"task": "Drywall installation", "required": True, "order": 6},
                        {"task": "Joint taping and mudding - First coat", "required": True, "order": 7},
                        {"task": "Joint taping and mudding - Second coat", "required": True, "order": 8},
                        {"task": "Sanding and smoothing", "required": True, "order": 9},
                        {"task": "Primer application", "required": True, "order": 10},
                        {"task": "Quality inspection", "required": True, "order": 11},
                        {"task": "After photos taken", "required": True, "order": 12},
                        {"task": "Client walkthrough and approval", "required": True, "order": 13},
                        {"task": "Cleanup and debris removal", "required": True, "order": 14}
                    ]
                },
                {
                    "template_id": "TEMP003",
                    "name": "Flooring Installation Checklist",
                    "service_type": "Flooring Installation",
                    "tasks": [
                        {"task": "Site measurement and assessment", "required": True, "order": 1},
                        {"task": "Flooring materials delivered", "required": True, "order": 2},
                        {"task": "Before photos taken", "required": True, "order": 3},
                        {"task": "Subfloor preparation and leveling", "required": True, "order": 4},
                        {"task": "Underlayment installation (if required)", "required": False, "order": 5},
                        {"task": "Flooring installation started", "required": True, "order": 6},
                        {"task": "Pattern/layout verification", "required": True, "order": 7},
                        {"task": "Transition strips and molding installed", "required": True, "order": 8},
                        {"task": "Quality check and adjustments", "required": True, "order": 9},
                        {"task": "After photos taken", "required": True, "order": 10},
                        {"task": "Client walkthrough", "required": True, "order": 11},
                        {"task": "Cleanup and debris removal", "required": True, "order": 12}
                    ]
                }
            ]
            with open(self.templates_file, 'w') as f:
                json.dump(default_templates, f, indent=2)
    
    def get_all_checklists(self):
        """Get all job checklists"""
        try:
            with open(self.checklist_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def get_checklist_templates(self):
        """Get all checklist templates"""
        try:
            with open(self.templates_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def create_job_checklist(self, job_id, service_type, custom_tasks=None):
        """Create a new checklist for a job"""
        checklists = self.get_all_checklists()
        templates = self.get_checklist_templates()
        
        # Find appropriate template
        template = None
        for temp in templates:
            if temp['service_type'] == service_type:
                template = temp
                break
        
        # Use general template if specific not found
        if not template:
            template = next((t for t in templates if t['service_type'] == 'General'), None)
        
        # Create checklist from template
        tasks = []
        if template:
            for task_template in template['tasks']:
                tasks.append({
                    'task_id': f"T{len(tasks) + 1:03d}",
                    'description': task_template['task'],
                    'required': task_template['required'],
                    'completed': False,
                    'completed_by': None,
                    'completed_date': None,
                    'order': task_template['order'],
                    'notes': ''
                })
        
        # Add custom tasks if provided
        if custom_tasks:
            for custom_task in custom_tasks:
                tasks.append({
                    'task_id': f"T{len(tasks) + 1:03d}",
                    'description': custom_task,
                    'required': False,
                    'completed': False,
                    'completed_by': None,
                    'completed_date': None,
                    'order': len(tasks) + 1,
                    'notes': ''
                })
        
        # Create new checklist
        new_checklist = {
            'checklist_id': f"CHK{len(checklists) + 1:05d}",
            'job_id': job_id,
            'service_type': service_type,
            'template_used': template['template_id'] if template else None,
            'created_date': get_hawaii_time().isoformat(),
            'last_updated': get_hawaii_time().isoformat(),
            'completion_percentage': 0,
            'status': 'active',
            'tasks': tasks
        }
        
        checklists.append(new_checklist)
        
        with open(self.checklist_file, 'w') as f:
            json.dump(checklists, f, indent=2)
            
        return new_checklist
    
    def get_checklist_by_job(self, job_id):
        """Get checklist for specific job"""
        checklists = self.get_all_checklists()
        return next((c for c in checklists if c['job_id'] == job_id), None)
    
    def update_task_status(self, checklist_id, task_id, completed, completed_by=None, notes=None):
        """Update task completion status"""
        checklists = self.get_all_checklists()
        
        for checklist in checklists:
            if checklist['checklist_id'] == checklist_id:
                for task in checklist['tasks']:
                    if task['task_id'] == task_id:
                        task['completed'] = completed
                        task['completed_by'] = completed_by if completed else None
                        task['completed_date'] = get_hawaii_time().isoformat() if completed else None
                        if notes:
                            task['notes'] = notes
                        break
                
                # Update completion percentage
                total_tasks = len(checklist['tasks'])
                completed_tasks = sum(1 for task in checklist['tasks'] if task['completed'])
                checklist['completion_percentage'] = round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0
                checklist['last_updated'] = get_hawaii_time().isoformat()
                
                # Update status based on completion
                if checklist['completion_percentage'] == 100:
                    checklist['status'] = 'completed'
                elif checklist['completion_percentage'] > 0:
                    checklist['status'] = 'in_progress'
                
                break
        
        with open(self.checklist_file, 'w') as f:
            json.dump(checklists, f, indent=2)
            
        return True
    
    def add_custom_task(self, checklist_id, task_description, required=False):
        """Add custom task to existing checklist"""
        checklists = self.get_all_checklists()
        
        for checklist in checklists:
            if checklist['checklist_id'] == checklist_id:
                new_task = {
                    'task_id': f"T{len(checklist['tasks']) + 1:03d}",
                    'description': task_description,
                    'required': required,
                    'completed': False,
                    'completed_by': None,
                    'completed_date': None,
                    'order': len(checklist['tasks']) + 1,
                    'notes': ''
                }
                
                checklist['tasks'].append(new_task)
                checklist['last_updated'] = get_hawaii_time().isoformat()
                
                # Recalculate completion percentage
                total_tasks = len(checklist['tasks'])
                completed_tasks = sum(1 for task in checklist['tasks'] if task['completed'])
                checklist['completion_percentage'] = round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0
                
                break
        
        with open(self.checklist_file, 'w') as f:
            json.dump(checklists, f, indent=2)
            
        return True
    
    def get_completion_summary(self, job_id):
        """Get completion summary for a job"""
        checklist = self.get_checklist_by_job(job_id)
        
        if not checklist:
            return {
                'checklist_exists': False,
                'completion_percentage': 0,
                'completed_tasks': 0,
                'total_tasks': 0,
                'required_remaining': 0,
                'status': 'not_started'
            }
        
        total_tasks = len(checklist['tasks'])
        completed_tasks = sum(1 for task in checklist['tasks'] if task['completed'])
        required_tasks = [task for task in checklist['tasks'] if task['required']]
        required_remaining = sum(1 for task in required_tasks if not task['completed'])
        
        return {
            'checklist_exists': True,
            'checklist_id': checklist['checklist_id'],
            'completion_percentage': checklist['completion_percentage'],
            'completed_tasks': completed_tasks,
            'total_tasks': total_tasks,
            'required_remaining': required_remaining,
            'status': checklist['status'],
            'last_updated': checklist['last_updated']
        }
    
    def create_template(self, name, service_type, tasks):
        """Create new checklist template"""
        templates = self.get_checklist_templates()
        
        template_id = f"TEMP{len(templates) + 1:03d}"
        
        new_template = {
            'template_id': template_id,
            'name': name,
            'service_type': service_type,
            'created_date': get_hawaii_time().isoformat(),
            'tasks': tasks
        }
        
        templates.append(new_template)
        
        with open(self.templates_file, 'w') as f:
            json.dump(templates, f, indent=2)
            
        return new_template
    
    def get_jobs_by_completion_status(self):
        """Get jobs grouped by completion status"""
        checklists = self.get_all_checklists()
        
        status_groups = {
            'not_started': [],
            'in_progress': [],
            'completed': []
        }
        
        for checklist in checklists:
            status = checklist['status']
            if status in status_groups:
                status_groups[status].append({
                    'job_id': checklist['job_id'],
                    'service_type': checklist['service_type'],
                    'completion_percentage': checklist['completion_percentage'],
                    'last_updated': checklist['last_updated']
                })
        
        return status_groups

# Global checklist service instance
checklist_service = ChecklistService()