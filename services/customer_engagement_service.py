"""
Customer Engagement Service for SPANKKS Construction
Manages customer lifecycle, retention strategies, and satisfaction tracking
"""

import json
import os
import logging
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional, Any

class CustomerEngagementService:
    """Service for managing customer engagement and retention strategies"""
    
    def __init__(self):
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
        self.logger = logging.getLogger(__name__)
        self.data_dir = 'data'
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
    
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
    
    def track_customer_interaction(self, contact_id: int, interaction_type: str, details: str) -> Dict[str, Any]:
        """Track customer interactions for engagement analysis"""
        current_time = self._get_hawaii_time()
        
        # Load existing interactions
        interactions = self._load_json_file('customer_interactions.json')
        
        interaction = {
            'id': len(interactions) + 1,
            'contact_id': contact_id,
            'interaction_type': interaction_type,  # email, phone, visit, quote_request, job_completion
            'details': details,
            'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'date': current_time.strftime('%Y-%m-%d'),
            'engagement_score': self._calculate_engagement_score(interaction_type),
            'follow_up_needed': self._requires_follow_up(interaction_type)
        }
        
        interactions.append(interaction)
        self._save_json_file('customer_interactions.json', interactions)
        
        # Update customer engagement profile
        self._update_customer_engagement_profile(contact_id, interaction)
        
        return interaction
    
    def _calculate_engagement_score(self, interaction_type: str) -> int:
        """Calculate engagement score based on interaction type"""
        score_map = {
            'quote_request': 8,
            'phone_call_inbound': 7,
            'email_inquiry': 6,
            'website_visit': 4,
            'job_completion': 10,
            'payment_made': 9,
            'referral_given': 10,
            'complaint': 3,
            'cancellation': 1
        }
        return score_map.get(interaction_type, 5)
    
    def _requires_follow_up(self, interaction_type: str) -> bool:
        """Determine if interaction requires follow-up"""
        follow_up_types = ['quote_request', 'complaint', 'phone_call_inbound', 'email_inquiry']
        return interaction_type in follow_up_types
    
    def _update_customer_engagement_profile(self, contact_id: int, interaction: Dict):
        """Update customer's engagement profile with new interaction"""
        profiles = self._load_json_file('customer_engagement_profiles.json')
        
        # Find existing profile or create new one
        profile = None
        profile_index = None
        for i, p in enumerate(profiles):
            if p.get('contact_id') == contact_id:
                profile = p
                profile_index = i
                break
        
        if not profile:
            profile = {
                'contact_id': contact_id,
                'total_interactions': 0,
                'last_interaction': None,
                'engagement_score': 0,
                'engagement_level': 'new',
                'preferred_contact_method': 'email',
                'interaction_frequency': 0,
                'lifetime_value': 0,
                'satisfaction_score': 5.0,
                'retention_risk': 'low',
                'next_engagement_date': None,
                'engagement_history': []
            }
            profiles.append(profile)
            profile_index = len(profiles) - 1
        
        # Update profile with new interaction
        profile['total_interactions'] += 1
        profile['last_interaction'] = interaction['timestamp']
        profile['engagement_score'] += interaction['engagement_score']
        profile['engagement_history'].append({
            'type': interaction['interaction_type'],
            'date': interaction['date'],
            'score': interaction['engagement_score']
        })
        
        # Calculate engagement level
        profile['engagement_level'] = self._calculate_engagement_level(profile['engagement_score'], profile['total_interactions'])
        
        # Calculate interaction frequency (interactions per month)
        if len(profile['engagement_history']) > 1:
            first_interaction = datetime.strptime(profile['engagement_history'][0]['date'], '%Y-%m-%d')
            last_interaction = datetime.strptime(profile['engagement_history'][-1]['date'], '%Y-%m-%d')
            days_span = (last_interaction - first_interaction).days
            if days_span > 0:
                profile['interaction_frequency'] = (profile['total_interactions'] * 30) / days_span
        
        # Update retention risk
        profile['retention_risk'] = self._assess_retention_risk(profile)
        
        # Schedule next engagement
        profile['next_engagement_date'] = self._calculate_next_engagement_date(profile)
        
        profiles[profile_index] = profile
        self._save_json_file('customer_engagement_profiles.json', profiles)
    
    def _calculate_engagement_level(self, total_score: int, total_interactions: int) -> str:
        """Calculate customer engagement level"""
        if total_interactions == 0:
            return 'new'
        
        avg_score = total_score / total_interactions
        
        if avg_score >= 8:
            return 'highly_engaged'
        elif avg_score >= 6:
            return 'engaged'
        elif avg_score >= 4:
            return 'moderately_engaged'
        else:
            return 'low_engagement'
    
    def _assess_retention_risk(self, profile: Dict) -> str:
        """Assess customer retention risk"""
        current_date = self._get_hawaii_time().date()
        
        if not profile['last_interaction']:
            return 'low'
        
        last_interaction_date = datetime.strptime(profile['last_interaction'], '%Y-%m-%d %H:%M:%S').date()
        days_since_last = (current_date - last_interaction_date).days
        
        # Risk assessment based on engagement level and recency
        engagement_level = profile['engagement_level']
        
        if engagement_level == 'highly_engaged':
            return 'low' if days_since_last < 60 else 'medium'
        elif engagement_level == 'engaged':
            return 'low' if days_since_last < 45 else 'medium' if days_since_last < 90 else 'high'
        elif engagement_level == 'moderately_engaged':
            return 'medium' if days_since_last < 30 else 'high'
        else:
            return 'high'
    
    def _calculate_next_engagement_date(self, profile: Dict) -> str:
        """Calculate when to next engage with customer"""
        current_date = self._get_hawaii_time().date()
        engagement_level = profile['engagement_level']
        
        # Engagement frequency based on level
        days_to_add = {
            'highly_engaged': 30,    # Monthly for highly engaged
            'engaged': 21,           # Every 3 weeks
            'moderately_engaged': 14, # Bi-weekly
            'low_engagement': 7,      # Weekly
            'new': 3                 # Every 3 days for new customers
        }
        
        next_date = current_date + timedelta(days=days_to_add.get(engagement_level, 14))
        return next_date.strftime('%Y-%m-%d')
    
    def get_customers_for_engagement(self, engagement_type: str = 'all') -> List[Dict]:
        """Get customers who need engagement based on criteria"""
        profiles = self._load_json_file('customer_engagement_profiles.json')
        contacts = self._load_json_file('contacts.json')
        current_date = self._get_hawaii_time().strftime('%Y-%m-%d')
        
        customers_for_engagement = []
        
        for profile in profiles:
            # Check if customer needs engagement
            needs_engagement = False
            reason = ""
            
            if engagement_type == 'due' or engagement_type == 'all':
                if profile.get('next_engagement_date', '9999-12-31') <= current_date:
                    needs_engagement = True
                    reason = 'scheduled_engagement'
            
            if engagement_type == 'retention_risk' or engagement_type == 'all':
                if profile.get('retention_risk') == 'high':
                    needs_engagement = True
                    reason = 'retention_risk'
            
            if engagement_type == 'new_customers' or engagement_type == 'all':
                if profile.get('engagement_level') == 'new':
                    needs_engagement = True
                    reason = 'new_customer'
            
            if needs_engagement:
                # Get contact details
                contact = next((c for c in contacts if c.get('id') == profile['contact_id']), {})
                
                customer_data = {
                    'contact_id': profile['contact_id'],
                    'name': contact.get('name', 'Unknown'),
                    'email': contact.get('email', ''),
                    'phone': contact.get('phone', ''),
                    'engagement_level': profile['engagement_level'],
                    'retention_risk': profile['retention_risk'],
                    'last_interaction': profile['last_interaction'],
                    'total_interactions': profile['total_interactions'],
                    'engagement_score': profile['engagement_score'],
                    'next_engagement_date': profile['next_engagement_date'],
                    'reason': reason,
                    'suggested_actions': self._get_suggested_engagement_actions(profile)
                }
                
                customers_for_engagement.append(customer_data)
        
        return customers_for_engagement
    
    def _get_suggested_engagement_actions(self, profile: Dict) -> List[str]:
        """Get suggested engagement actions based on customer profile"""
        engagement_level = profile['engagement_level']
        retention_risk = profile['retention_risk']
        
        actions = []
        
        if engagement_level == 'new':
            actions.extend([
                'Send welcome email with service overview',
                'Schedule follow-up call within 48 hours',
                'Offer free consultation'
            ])
        elif engagement_level == 'low_engagement':
            actions.extend([
                'Send personalized check-in email',
                'Offer special discount for returning customers',
                'Request feedback on previous experience'
            ])
        elif retention_risk == 'high':
            actions.extend([
                'Priority phone call to reconnect',
                'Offer exclusive loyalty discount',
                'Send satisfaction survey'
            ])
        else:
            actions.extend([
                'Send seasonal service reminders',
                'Share relevant home improvement tips',
                'Invite to refer friends and family'
            ])
        
        # Add service-specific suggestions
        last_interactions = profile.get('engagement_history', [])[-3:]  # Last 3 interactions
        if any('quote' in interaction.get('type', '') for interaction in last_interactions):
            actions.append('Follow up on previous quote status')
        
        return actions
    
    def generate_engagement_campaign(self, target_audience: str) -> Dict[str, Any]:
        """Generate targeted engagement campaign"""
        current_time = self._get_hawaii_time()
        customers = self.get_customers_for_engagement(target_audience)
        
        campaign = {
            'id': f"ENG_{current_time.strftime('%Y%m%d_%H%M%S')}",
            'name': f"Customer Engagement - {target_audience.replace('_', ' ').title()}",
            'target_audience': target_audience,
            'created_date': current_time.strftime('%Y-%m-%d'),
            'target_customers': len(customers),
            'campaign_type': 'engagement',
            'status': 'planned',
            'customers': customers,
            'success_metrics': {
                'target_response_rate': 25.0,
                'target_conversion_rate': 10.0,
                'target_satisfaction_increase': 0.5
            },
            'content_suggestions': self._generate_campaign_content(target_audience),
            'execution_timeline': self._create_campaign_timeline(len(customers))
        }
        
        # Save campaign
        campaigns = self._load_json_file('engagement_campaigns.json')
        campaigns.append(campaign)
        self._save_json_file('engagement_campaigns.json', campaigns)
        
        return campaign
    
    def _generate_campaign_content(self, target_audience: str) -> Dict[str, List[str]]:
        """Generate content suggestions for engagement campaign"""
        content_templates = {
            'new_customers': {
                'email_subjects': [
                    'Welcome to the SPANKKS Construction Family!',
                    'Your Home Improvement Journey Starts Here',
                    'Exclusive New Customer Benefits Inside'
                ],
                'key_messages': [
                    'Professional construction services across O\'ahu',
                    'Licensed, insured, and locally trusted',
                    'Free consultations for new customers'
                ]
            },
            'retention_risk': {
                'email_subjects': [
                    'We Miss You! Special Offer Inside',
                    'Your Home Deserves the Best - Let\'s Reconnect',
                    'Exclusive Comeback Discount Just for You'
                ],
                'key_messages': [
                    'We value your previous trust in our services',
                    '20% discount on your next project',
                    'Updated services and improved processes'
                ]
            },
            'due': {
                'email_subjects': [
                    'Seasonal Home Maintenance Reminder',
                    'Time for Your Regular Check-In',
                    'New Services Available in Your Area'
                ],
                'key_messages': [
                    'Regular maintenance prevents costly repairs',
                    'New services now available',
                    'Preferred customer pricing'
                ]
            },
            'all': {
                'email_subjects': [
                    'SPANKKS Construction Monthly Update',
                    'Home Improvement Tips & Special Offers',
                    'What\'s New at SPANKKS Construction'
                ],
                'key_messages': [
                    'Professional construction services',
                    'Customer success stories',
                    'Educational content and tips'
                ]
            }
        }
        
        return content_templates.get(target_audience, content_templates['all'])
    
    def _create_campaign_timeline(self, customer_count: int) -> List[Dict]:
        """Create execution timeline for campaign"""
        current_date = self._get_hawaii_time().date()
        
        timeline = [
            {
                'phase': 'preparation',
                'start_date': current_date.strftime('%Y-%m-%d'),
                'end_date': (current_date + timedelta(days=2)).strftime('%Y-%m-%d'),
                'tasks': ['Finalize content', 'Review customer list', 'Setup tracking']
            },
            {
                'phase': 'execution',
                'start_date': (current_date + timedelta(days=3)).strftime('%Y-%m-%d'),
                'end_date': (current_date + timedelta(days=10)).strftime('%Y-%m-%d'),
                'tasks': ['Send emails', 'Make follow-up calls', 'Track responses']
            },
            {
                'phase': 'follow_up',
                'start_date': (current_date + timedelta(days=11)).strftime('%Y-%m-%d'),
                'end_date': (current_date + timedelta(days=21)).strftime('%Y-%m-%d'),
                'tasks': ['Follow up with respondents', 'Schedule consultations', 'Update customer profiles']
            },
            {
                'phase': 'analysis',
                'start_date': (current_date + timedelta(days=22)).strftime('%Y-%m-%d'),
                'end_date': (current_date + timedelta(days=28)).strftime('%Y-%m-%d'),
                'tasks': ['Analyze results', 'Update strategies', 'Plan next campaign']
            }
        ]
        
        return timeline
    
    def get_engagement_analytics(self) -> Dict[str, Any]:
        """Get comprehensive engagement analytics"""
        profiles = self._load_json_file('customer_engagement_profiles.json')
        interactions = self._load_json_file('customer_interactions.json')
        campaigns = self._load_json_file('engagement_campaigns.json')
        
        current_date = self._get_hawaii_time().date()
        
        analytics = {
            'customer_base': {
                'total_customers': len(profiles),
                'engagement_distribution': {},
                'retention_risk_distribution': {},
                'average_engagement_score': 0,
                'new_customers_this_month': 0
            },
            'interaction_metrics': {
                'total_interactions': len(interactions),
                'interactions_this_month': 0,
                'interaction_types': {},
                'average_interactions_per_customer': 0
            },
            'engagement_health': {
                'customers_needing_attention': 0,
                'high_risk_customers': 0,
                'highly_engaged_customers': 0,
                'engagement_trend': 'stable'
            },
            'campaign_performance': {
                'active_campaigns': 0,
                'completed_campaigns': 0,
                'average_response_rate': 0,
                'total_customers_reached': 0
            }
        }
        
        # Calculate customer base metrics
        if profiles:
            engagement_levels = [p.get('engagement_level', 'new') for p in profiles]
            retention_risks = [p.get('retention_risk', 'low') for p in profiles]
            engagement_scores = [p.get('engagement_score', 0) for p in profiles]
            
            # Engagement distribution
            for level in engagement_levels:
                analytics['customer_base']['engagement_distribution'][level] = analytics['customer_base']['engagement_distribution'].get(level, 0) + 1
            
            # Retention risk distribution
            for risk in retention_risks:
                analytics['customer_base']['retention_risk_distribution'][risk] = analytics['customer_base']['retention_risk_distribution'].get(risk, 0) + 1
            
            # Average engagement score
            analytics['customer_base']['average_engagement_score'] = sum(engagement_scores) / len(engagement_scores)
            
            # New customers this month
            current_month = current_date.strftime('%Y-%m')
            analytics['customer_base']['new_customers_this_month'] = len([
                p for p in profiles 
                if p.get('last_interaction', '').startswith(current_month)
            ])
        
        # Calculate interaction metrics
        if interactions:
            current_month_interactions = [
                i for i in interactions 
                if i.get('date', '').startswith(current_date.strftime('%Y-%m'))
            ]
            analytics['interaction_metrics']['interactions_this_month'] = len(current_month_interactions)
            
            # Interaction types
            for interaction in interactions:
                interaction_type = interaction.get('interaction_type', 'unknown')
                analytics['interaction_metrics']['interaction_types'][interaction_type] = analytics['interaction_metrics']['interaction_types'].get(interaction_type, 0) + 1
            
            # Average interactions per customer
            if profiles:
                analytics['interaction_metrics']['average_interactions_per_customer'] = len(interactions) / len(profiles)
        
        # Calculate engagement health
        customers_needing_attention = self.get_customers_for_engagement('all')
        analytics['engagement_health']['customers_needing_attention'] = len(customers_needing_attention)
        analytics['engagement_health']['high_risk_customers'] = len([c for c in customers_needing_attention if c.get('retention_risk') == 'high'])
        analytics['engagement_health']['highly_engaged_customers'] = len([p for p in profiles if p.get('engagement_level') == 'highly_engaged'])
        
        # Campaign performance
        active_campaigns = [c for c in campaigns if c.get('status') == 'active']
        completed_campaigns = [c for c in campaigns if c.get('status') == 'completed']
        
        analytics['campaign_performance']['active_campaigns'] = len(active_campaigns)
        analytics['campaign_performance']['completed_campaigns'] = len(completed_campaigns)
        
        return analytics