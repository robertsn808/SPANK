"""
Comprehensive Workflow Automation Service for SPANKKS Construction
Automates business processes from quote generation through job completion
"""

import json
import os
import logging
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class WorkflowStage:
    """Represents a stage in the business workflow"""
    name: str
    description: str
    duration_days: int
    actions: List[str]
    next_stage: Optional[str] = None
    auto_advance: bool = False

class WorkflowAutomationService:
    """Service for automating business workflows and improving conversion rates"""
    
    def __init__(self):
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
        self.logger = logging.getLogger(__name__)
        self.data_dir = 'data'
        self._ensure_data_directory()
        self._initialize_workflow_stages()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
    
    def _initialize_workflow_stages(self):
        """Initialize the business workflow stages"""
        self.workflow_stages = {
            'quote_sent': WorkflowStage(
                name='Quote Sent',
                description='Quote has been generated and sent to customer',
                duration_days=3,
                actions=['Send follow-up email', 'Schedule phone call'],
                next_stage='quote_follow_up',
                auto_advance=True
            ),
            'quote_follow_up': WorkflowStage(
                name='Quote Follow-up',
                description='Following up on quote with customer',
                duration_days=4,
                actions=['Phone call reminder', 'Offer consultation'],
                next_stage='quote_reminder',
                auto_advance=True
            ),
            'quote_reminder': WorkflowStage(
                name='Quote Reminder',
                description='Final reminder before quote expires',
                duration_days=7,
                actions=['Final reminder email', 'Offer discount'],
                next_stage='quote_expired',
                auto_advance=True
            ),
            'quote_accepted': WorkflowStage(
                name='Quote Accepted',
                description='Customer has accepted the quote',
                duration_days=1,
                actions=['Create job', 'Generate invoice', 'Schedule work'],
                next_stage='job_scheduled',
                auto_advance=True
            ),
            'job_scheduled': WorkflowStage(
                name='Job Scheduled',
                description='Work has been scheduled with customer',
                duration_days=7,
                actions=['Confirm schedule', 'Prepare materials', 'Assign crew'],
                next_stage='job_preparation',
                auto_advance=False
            ),
            'job_preparation': WorkflowStage(
                name='Job Preparation',
                description='Preparing for job execution',
                duration_days=2,
                actions=['Gather materials', 'Brief crew', 'Final confirmation'],
                next_stage='job_in_progress',
                auto_advance=False
            ),
            'job_in_progress': WorkflowStage(
                name='Job In Progress',
                description='Work is being performed',
                duration_days=3,
                actions=['Daily check-ins', 'Progress photos', 'Quality control'],
                next_stage='job_completion',
                auto_advance=False
            ),
            'job_completion': WorkflowStage(
                name='Job Completion',
                description='Work has been completed',
                duration_days=1,
                actions=['Final inspection', 'Customer walkthrough', 'Invoice payment'],
                next_stage='follow_up',
                auto_advance=True
            ),
            'follow_up': WorkflowStage(
                name='Follow-up',
                description='Post-completion customer satisfaction',
                duration_days=7,
                actions=['Satisfaction survey', 'Request review', 'Future service offer'],
                next_stage='completed',
                auto_advance=True
            ),
            'completed': WorkflowStage(
                name='Completed',
                description='Workflow completed successfully',
                duration_days=0,
                actions=['Archive records', 'Update analytics'],
                next_stage=None,
                auto_advance=False
            ),
            'quote_expired': WorkflowStage(
                name='Quote Expired',
                description='Quote has expired without acceptance',
                duration_days=30,
                actions=['Archive quote', 'Add to nurture campaign'],
                next_stage='nurture_campaign',
                auto_advance=True
            ),
            'nurture_campaign': WorkflowStage(
                name='Nurture Campaign',
                description='Long-term customer nurturing',
                duration_days=90,
                actions=['Seasonal reminders', 'Special offers', 'Educational content'],
                next_stage='completed',
                auto_advance=False
            )
        }
    
    def _get_hawaii_time(self):
        """Get current Hawaii time"""
        return datetime.now(self.hawaii_tz)
    
    def _load_json_file(self, filename: str) -> List[Dict]:
        """Load data from JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def _save_json_file(self, filename: str, data: List[Dict]) -> bool:
        """Save data to JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving {filename}: {e}")
            return False
    
    def initialize_quote_workflow(self, quote_id: int) -> Dict[str, Any]:
        """Initialize workflow automation for a new quote"""
        current_time = self._get_hawaii_time()
        
        # Load existing workflows
        workflows = self._load_json_file('workflow_tracking.json')
        
        # Create new workflow entry
        workflow_entry = {
            'id': len(workflows) + 1,
            'quote_id': quote_id,
            'current_stage': 'quote_sent',
            'stage_entered': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'next_action_due': (current_time + timedelta(days=self.workflow_stages['quote_sent'].duration_days)).strftime('%Y-%m-%d'),
            'actions_completed': [],
            'stages_history': [
                {
                    'stage': 'quote_sent',
                    'entered': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'actions': self.workflow_stages['quote_sent'].actions.copy()
                }
            ],
            'status': 'active',
            'created_date': current_time.strftime('%Y-%m-%d'),
            'priority': 'normal',
            'automation_enabled': True
        }
        
        workflows.append(workflow_entry)
        self._save_json_file('workflow_tracking.json', workflows)
        
        # Schedule first automated action
        self._schedule_workflow_action(workflow_entry['id'], 'quote_follow_up_email', 1)
        
        self.logger.info(f"Initialized workflow for quote {quote_id}")
        
        return {
            'workflow_id': workflow_entry['id'],
            'current_stage': 'quote_sent',
            'next_action_due': workflow_entry['next_action_due'],
            'actions_scheduled': ['follow_up_email', 'phone_reminder']
        }
    
    def advance_workflow_stage(self, quote_id: int, new_stage: str, manual: bool = False) -> Dict[str, Any]:
        """Advance a workflow to the next stage"""
        current_time = self._get_hawaii_time()
        
        # Load workflows
        workflows = self._load_json_file('workflow_tracking.json')
        
        # Find the workflow for this quote
        workflow = None
        workflow_index = None
        for i, w in enumerate(workflows):
            if w.get('quote_id') == quote_id:
                workflow = w
                workflow_index = i
                break
        
        if not workflow:
            return {'success': False, 'error': 'Workflow not found for quote'}
        
        # Validate stage transition
        if new_stage not in self.workflow_stages:
            return {'success': False, 'error': f'Invalid workflow stage: {new_stage}'}
        
        old_stage = workflow['current_stage']
        
        # Update workflow
        workflow['current_stage'] = new_stage
        workflow['stage_entered'] = current_time.strftime('%Y-%m-%d %H:%M:%S')
        
        stage_config = self.workflow_stages[new_stage]
        workflow['next_action_due'] = (current_time + timedelta(days=stage_config.duration_days)).strftime('%Y-%m-%d')
        
        # Add to history
        workflow['stages_history'].append({
            'stage': new_stage,
            'entered': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'actions': stage_config.actions.copy(),
            'advanced_manually': manual
        })
        
        # Handle special stage transitions
        if new_stage == 'quote_accepted':
            self._handle_quote_acceptance(quote_id, workflow)
        elif new_stage == 'job_completion':
            self._handle_job_completion(quote_id, workflow)
        elif new_stage == 'completed':
            workflow['status'] = 'completed'
            workflow['completed_date'] = current_time.strftime('%Y-%m-%d')
        
        # Save updated workflow
        workflows[workflow_index] = workflow
        self._save_json_file('workflow_tracking.json', workflows)
        
        # Schedule next automated actions if applicable
        if stage_config.auto_advance and stage_config.next_stage:
            self._schedule_workflow_action(workflow['id'], f'advance_to_{stage_config.next_stage}', stage_config.duration_days)
        
        self.logger.info(f"Advanced workflow for quote {quote_id} from {old_stage} to {new_stage}")
        
        return {
            'success': True,
            'workflow_id': workflow['id'],
            'old_stage': old_stage,
            'new_stage': new_stage,
            'next_action_due': workflow['next_action_due'],
            'actions_required': stage_config.actions
        }
    
    def _handle_quote_acceptance(self, quote_id: int, workflow: Dict):
        """Handle automated actions when quote is accepted"""
        # Create job automatically
        jobs = self._load_json_file('jobs.json')
        quotes = self._load_json_file('quotes.json')
        
        quote = next((q for q in quotes if q.get('id') == quote_id), None)
        if not quote:
            self.logger.error(f"Quote {quote_id} not found for job creation")
            return
        
        # Create job entry
        new_job = {
            'id': len(jobs) + 1,
            'quote_id': quote_id,
            'contact_id': quote.get('contact_id'),
            'service_type': quote.get('service_type'),
            'total_amount': quote.get('total_amount'),
            'status': 'scheduled',
            'created_date': self._get_hawaii_time().strftime('%Y-%m-%d'),
            'workflow_id': workflow['id'],
            'priority': 'normal',
            'estimated_hours': self._estimate_job_duration(quote.get('service_type')),
            'materials_needed': self._generate_materials_list(quote),
            'crew_assigned': [],
            'notes': f"Job created automatically from accepted quote Q{quote_id:04d}"
        }
        
        jobs.append(new_job)
        self._save_json_file('jobs.json', jobs)
        
        # Update quote status
        quote['status'] = 'accepted'
        quote['accepted_date'] = self._get_hawaii_time().strftime('%Y-%m-%d')
        quotes = [q if q.get('id') != quote_id else quote for q in quotes]
        self._save_json_file('quotes.json', quotes)
        
        workflow['job_id'] = new_job['id']
        self.logger.info(f"Created job {new_job['id']} from accepted quote {quote_id}")
    
    def _handle_job_completion(self, quote_id: int, workflow: Dict):
        """Handle automated actions when job is completed"""
        # Update job status
        jobs = self._load_json_file('jobs.json')
        job_id = workflow.get('job_id')
        
        if job_id:
            for job in jobs:
                if job.get('id') == job_id:
                    job['status'] = 'completed'
                    job['completed_date'] = self._get_hawaii_time().strftime('%Y-%m-%d')
                    break
            
            self._save_json_file('jobs.json', jobs)
        
        # Schedule customer satisfaction survey
        self._schedule_workflow_action(workflow['id'], 'send_satisfaction_survey', 1)
        
        # Request customer review
        self._schedule_workflow_action(workflow['id'], 'request_customer_review', 3)
        
        self.logger.info(f"Completed job workflow for quote {quote_id}")
    
    def _estimate_job_duration(self, service_type: str) -> int:
        """Estimate job duration in hours"""
        duration_estimates = {
            'drywall_services': 8,
            'flooring_installation': 16,
            'electrical_work': 6,
            'plumbing_services': 4,
            'general_handyman': 6,
            'fence_installation': 20,
            'painting_services': 12,
            'bathroom_renovation': 40,
            'kitchen_renovation': 80
        }
        return duration_estimates.get(service_type, 8)
    
    def _generate_materials_list(self, quote: Dict) -> List[str]:
        """Generate materials list based on service type"""
        service_type = quote.get('service_type', '')
        
        materials_map = {
            'drywall_services': ['Drywall sheets', 'Joint compound', 'Drywall screws', 'Tape'],
            'flooring_installation': ['Flooring material', 'Underlayment', 'Adhesive', 'Trim'],
            'electrical_work': ['Electrical wire', 'Outlets', 'Switches', 'Wire nuts'],
            'plumbing_services': ['Pipes', 'Fittings', 'Valves', 'Sealant'],
            'fence_installation': ['Fence panels', 'Posts', 'Hardware', 'Concrete']
        }
        
        return materials_map.get(service_type, ['Standard materials'])
    
    def _schedule_workflow_action(self, workflow_id: int, action_type: str, days_from_now: int):
        """Schedule an automated workflow action"""
        scheduled_actions = self._load_json_file('scheduled_actions.json')
        
        action_date = self._get_hawaii_time() + timedelta(days=days_from_now)
        
        action = {
            'id': len(scheduled_actions) + 1,
            'workflow_id': workflow_id,
            'action_type': action_type,
            'scheduled_date': action_date.strftime('%Y-%m-%d'),
            'scheduled_time': '09:00:00',  # 9 AM Hawaii time
            'status': 'pending',
            'created_date': self._get_hawaii_time().strftime('%Y-%m-%d'),
            'attempts': 0,
            'max_attempts': 3
        }
        
        scheduled_actions.append(action)
        self._save_json_file('scheduled_actions.json', scheduled_actions)
    
    def process_automated_actions(self) -> Dict[str, Any]:
        """Process all pending automated actions"""
        current_date = self._get_hawaii_time().strftime('%Y-%m-%d')
        scheduled_actions = self._load_json_file('scheduled_actions.json')
        
        processed_actions = {
            'executed': [],
            'failed': [],
            'skipped': []
        }
        
        for action in scheduled_actions:
            if (action.get('status') == 'pending' and 
                action.get('scheduled_date') <= current_date and
                action.get('attempts', 0) < action.get('max_attempts', 3)):
                
                try:
                    result = self._execute_automated_action(action)
                    if result['success']:
                        action['status'] = 'completed'
                        action['completed_date'] = current_date
                        processed_actions['executed'].append(action)
                    else:
                        action['attempts'] = action.get('attempts', 0) + 1
                        action['last_error'] = result.get('error', 'Unknown error')
                        if action['attempts'] >= action.get('max_attempts', 3):
                            action['status'] = 'failed'
                            processed_actions['failed'].append(action)
                        
                except Exception as e:
                    action['attempts'] = action.get('attempts', 0) + 1
                    action['last_error'] = str(e)
                    processed_actions['failed'].append(action)
            else:
                processed_actions['skipped'].append(action)
        
        self._save_json_file('scheduled_actions.json', scheduled_actions)
        
        return {
            'processed_date': current_date,
            'total_executed': len(processed_actions['executed']),
            'total_failed': len(processed_actions['failed']),
            'total_skipped': len(processed_actions['skipped']),
            'details': processed_actions
        }
    
    def _execute_automated_action(self, action: Dict) -> Dict[str, Any]:
        """Execute a specific automated action"""
        action_type = action.get('action_type')
        workflow_id = action.get('workflow_id')
        
        # Map action types to execution methods
        action_handlers = {
            'quote_follow_up_email': self._send_quote_follow_up_email,
            'quote_reminder_email': self._send_quote_reminder_email,
            'advance_to_quote_follow_up': self._auto_advance_workflow_stage,
            'advance_to_quote_reminder': self._auto_advance_workflow_stage,
            'advance_to_quote_expired': self._auto_advance_workflow_stage,
            'send_satisfaction_survey': self._send_satisfaction_survey,
            'request_customer_review': self._request_customer_review
        }
        
        handler = action_handlers.get(action_type)
        if handler:
            return handler(workflow_id, action)
        else:
            return {'success': False, 'error': f'Unknown action type: {action_type}'}
    
    def _send_quote_follow_up_email(self, workflow_id: int, action: Dict) -> Dict[str, Any]:
        """Send quote follow-up email"""
        # This would integrate with email service
        self.logger.info(f"Sending quote follow-up email for workflow {workflow_id}")
        return {'success': True, 'message': 'Follow-up email sent'}
    
    def _send_quote_reminder_email(self, workflow_id: int, action: Dict) -> Dict[str, Any]:
        """Send quote reminder email"""
        self.logger.info(f"Sending quote reminder email for workflow {workflow_id}")
        return {'success': True, 'message': 'Reminder email sent'}
    
    def _auto_advance_workflow_stage(self, workflow_id: int, action: Dict) -> Dict[str, Any]:
        """Automatically advance workflow to next stage"""
        action_type = action.get('action_type')
        if 'advance_to_' in action_type:
            target_stage = action_type.replace('advance_to_', '')
            
            # Find quote_id for this workflow
            workflows = self._load_json_file('workflow_tracking.json')
            workflow = next((w for w in workflows if w.get('id') == workflow_id), None)
            
            if workflow:
                return self.advance_workflow_stage(workflow['quote_id'], target_stage, manual=False)
            else:
                return {'success': False, 'error': 'Workflow not found'}
        
        return {'success': False, 'error': 'Invalid advance action'}
    
    def _send_satisfaction_survey(self, workflow_id: int, action: Dict) -> Dict[str, Any]:
        """Send customer satisfaction survey"""
        self.logger.info(f"Sending satisfaction survey for workflow {workflow_id}")
        return {'success': True, 'message': 'Satisfaction survey sent'}
    
    def _request_customer_review(self, workflow_id: int, action: Dict) -> Dict[str, Any]:
        """Request customer review"""
        self.logger.info(f"Requesting customer review for workflow {workflow_id}")
        return {'success': True, 'message': 'Review request sent'}
    
    def get_workflow_analytics(self) -> Dict[str, Any]:
        """Get comprehensive workflow analytics"""
        workflows = self._load_json_file('workflow_tracking.json')
        current_date = self._get_hawaii_time().strftime('%Y-%m-%d')
        
        analytics = {
            'total_workflows': len(workflows),
            'active_workflows': len([w for w in workflows if w.get('status') == 'active']),
            'completed_workflows': len([w for w in workflows if w.get('status') == 'completed']),
            'stage_distribution': {},
            'conversion_rates': {},
            'average_stage_duration': {},
            'bottlenecks': [],
            'performance_metrics': {}
        }
        
        # Calculate stage distribution
        for workflow in workflows:
            stage = workflow.get('current_stage', 'unknown')
            analytics['stage_distribution'][stage] = analytics['stage_distribution'].get(stage, 0) + 1
        
        # Calculate conversion rates
        total_quotes = len(workflows)
        if total_quotes > 0:
            accepted_quotes = len([w for w in workflows if 'quote_accepted' in [s.get('stage') for s in w.get('stages_history', [])]])
            completed_jobs = len([w for w in workflows if w.get('status') == 'completed'])
            
            analytics['conversion_rates'] = {
                'quote_acceptance_rate': (accepted_quotes / total_quotes) * 100,
                'job_completion_rate': (completed_jobs / total_quotes) * 100 if total_quotes > 0 else 0
            }
        
        # Identify bottlenecks (stages with long durations)
        stage_durations = {}
        for workflow in workflows:
            for i, stage_entry in enumerate(workflow.get('stages_history', [])):
                stage = stage_entry.get('stage')
                if i < len(workflow['stages_history']) - 1:
                    # Calculate duration to next stage
                    next_stage = workflow['stages_history'][i + 1]
                    duration = self._calculate_stage_duration(stage_entry.get('entered'), next_stage.get('entered'))
                    if stage not in stage_durations:
                        stage_durations[stage] = []
                    stage_durations[stage].append(duration)
        
        # Calculate average durations and identify bottlenecks
        for stage, durations in stage_durations.items():
            if durations:
                avg_duration = sum(durations) / len(durations)
                analytics['average_stage_duration'][stage] = round(avg_duration, 2)
                
                # Consider a bottleneck if average duration > expected duration + 50%
                expected_duration = self.workflow_stages.get(stage, WorkflowStage('', '', 7, [])).duration_days
                if avg_duration > expected_duration * 1.5:
                    analytics['bottlenecks'].append({
                        'stage': stage,
                        'average_duration': avg_duration,
                        'expected_duration': expected_duration,
                        'delay_factor': round(avg_duration / expected_duration, 2)
                    })
        
        # Performance metrics
        analytics['performance_metrics'] = {
            'automation_rate': len([w for w in workflows if w.get('automation_enabled')]) / len(workflows) * 100 if workflows else 0,
            'on_time_completion': self._calculate_on_time_completion_rate(workflows),
            'customer_satisfaction_score': 85.0,  # This would come from actual surveys
            'repeat_customer_rate': self._calculate_repeat_customer_rate()
        }
        
        return analytics
    
    def _calculate_stage_duration(self, start_date: str, end_date: str) -> float:
        """Calculate duration between two dates in days"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
            return (end - start).days
        except:
            return 0.0
    
    def _calculate_on_time_completion_rate(self, workflows: List[Dict]) -> float:
        """Calculate percentage of workflows completed on time"""
        completed_workflows = [w for w in workflows if w.get('status') == 'completed']
        if not completed_workflows:
            return 0.0
        
        on_time_count = 0
        for workflow in completed_workflows:
            # This is a simplified calculation - in practice would compare actual vs expected completion
            total_stages = len(workflow.get('stages_history', []))
            if total_stages >= 3:  # Consider on-time if workflow progressed through at least 3 stages
                on_time_count += 1
        
        return (on_time_count / len(completed_workflows)) * 100
    
    def _calculate_repeat_customer_rate(self) -> float:
        """Calculate repeat customer rate"""
        contacts = self._load_json_file('contacts.json')
        if not contacts:
            return 0.0
        
        repeat_customers = len([c for c in contacts if len(c.get('job_history', [])) > 1])
        return (repeat_customers / len(contacts)) * 100