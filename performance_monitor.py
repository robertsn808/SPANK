import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import pytz

class PerformanceMonitor:
    """Real-time performance monitoring and automated alerts for SPANKKS Construction"""
    
    def __init__(self):
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
        self.alert_thresholds = {
            'low_conversion_rate': 25,  # Below 25% quote acceptance
            'high_completion_time': 14,  # Above 14 days average
            'low_customer_retention': 20,  # Below 20% repeat customers
            'revenue_decline': -10,  # More than 10% revenue drop
            'capacity_overload': 90,  # Above 90% capacity utilization
            'outstanding_invoices': 0.4  # Outstanding invoices > 40% of monthly revenue
        }
    
    def monitor_real_time_metrics(self, storage):
        """Monitor critical business metrics in real-time"""
        from analytics_service import analytics_service
        
        # Get current metrics
        business_report = analytics_service.generate_business_report(storage)
        cash_flow = analytics_service.get_cash_flow_forecast(storage)
        
        current_time = datetime.now(self.hawaii_tz)
        
        # Real-time KPIs
        real_time_metrics = {
            'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'conversion_rate': business_report['revenue']['quote_conversion_rate'],
            'completion_time': business_report['operations']['avg_completion_time_days'],
            'customer_retention': business_report['customers']['repeat_customer_rate'],
            'capacity_utilization': business_report['operations']['completion_rate'],
            'outstanding_ratio': (cash_flow.get('outstanding_invoice_value', 0) / max(1, cash_flow.get('current_month_revenue', 1))) * 100 if cash_flow.get('current_month_revenue', 0) > 0 else 0,
            'pipeline_health': cash_flow['total_pipeline_value'],
            'revenue_trend': business_report['growth']['monthly_revenue_growth']
        }
        
        return real_time_metrics
    
    def generate_performance_alerts(self, storage):
        """Generate automated performance alerts based on thresholds"""
        metrics = self.monitor_real_time_metrics(storage)
        alerts = []
        
        # Conversion rate alert
        if metrics['conversion_rate'] < self.alert_thresholds['low_conversion_rate']:
            alerts.append({
                'type': 'critical',
                'category': 'Sales Performance',
                'title': 'Low Quote Conversion Rate',
                'message': f"Conversion rate dropped to {metrics['conversion_rate']:.1f}% (threshold: {self.alert_thresholds['low_conversion_rate']}%)",
                'impact': 'Revenue loss and competitive disadvantage',
                'recommended_actions': [
                    'Review pricing strategy',
                    'Analyze competitor rates',
                    'Improve quote presentation',
                    'Follow up faster with prospects'
                ],
                'urgency': 'high',
                'timestamp': metrics['timestamp']
            })
        
        # Completion time alert
        if metrics['completion_time'] > self.alert_thresholds['high_completion_time']:
            alerts.append({
                'type': 'warning',
                'category': 'Operational Efficiency',
                'title': 'Extended Project Timeline',
                'message': f"Average completion time increased to {metrics['completion_time']:.1f} days (threshold: {self.alert_thresholds['high_completion_time']} days)",
                'impact': 'Customer satisfaction decline and capacity constraints',
                'recommended_actions': [
                    'Analyze workflow bottlenecks',
                    'Optimize crew scheduling',
                    'Review material procurement',
                    'Implement project management tools'
                ],
                'urgency': 'medium',
                'timestamp': metrics['timestamp']
            })
        
        # Customer retention alert
        if metrics['customer_retention'] < self.alert_thresholds['low_customer_retention']:
            alerts.append({
                'type': 'warning',
                'category': 'Customer Relations',
                'title': 'Low Customer Retention',
                'message': f"Repeat customer rate at {metrics['customer_retention']:.1f}% (threshold: {self.alert_thresholds['low_customer_retention']}%)",
                'impact': 'Increased customer acquisition costs and reduced lifetime value',
                'recommended_actions': [
                    'Implement follow-up system',
                    'Launch loyalty program',
                    'Improve service quality',
                    'Create maintenance reminder system'
                ],
                'urgency': 'medium',
                'timestamp': metrics['timestamp']
            })
        
        # Revenue trend alert
        if metrics['revenue_trend'] < self.alert_thresholds['revenue_decline']:
            alerts.append({
                'type': 'critical',
                'category': 'Financial Performance',
                'title': 'Revenue Decline Detected',
                'message': f"Revenue trend showing {metrics['revenue_trend']:.1f}% decline",
                'impact': 'Business sustainability risk and cash flow concerns',
                'recommended_actions': [
                    'Increase marketing efforts',
                    'Expand service offerings',
                    'Review pricing strategy',
                    'Analyze market conditions'
                ],
                'urgency': 'high',
                'timestamp': metrics['timestamp']
            })
        
        # Outstanding invoices alert
        if metrics['outstanding_ratio'] > self.alert_thresholds['outstanding_invoices'] * 100:
            alerts.append({
                'type': 'warning',
                'category': 'Cash Flow',
                'title': 'High Outstanding Invoices',
                'message': f"Outstanding invoices at {metrics['outstanding_ratio']:.1f}% of monthly revenue",
                'impact': 'Cash flow constraints and working capital issues',
                'recommended_actions': [
                    'Accelerate collection efforts',
                    'Review payment terms',
                    'Implement automated reminders',
                    'Consider early payment discounts'
                ],
                'urgency': 'medium',
                'timestamp': metrics['timestamp']
            })
        
        return {
            'alerts': alerts,
            'alert_summary': {
                'total_alerts': len(alerts),
                'critical_alerts': len([a for a in alerts if a['type'] == 'critical']),
                'warning_alerts': len([a for a in alerts if a['type'] == 'warning']),
                'high_urgency': len([a for a in alerts if a['urgency'] == 'high'])
            },
            'metrics': metrics
        }
    
    def track_daily_performance(self, storage):
        """Track daily performance trends"""
        jobs = storage.get_all_jobs()
        quotes = storage.get_all_quotes()
        contacts = storage.get_all_contacts()
        
        today = datetime.now(self.hawaii_tz).date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        
        # Today's metrics
        todays_jobs = [j for j in jobs if j.get('created_date') is not None and j.created_date.date() == today]
        todays_quotes = [q for q in quotes if q.get('created_date') is not None and q.created_date.date() == today]
        todays_contacts = [c for c in contacts if c.get('created_date') is not None and c.created_date.date() == today]
        
        # Yesterday's metrics
        yesterdays_jobs = [j for j in jobs if j.get('created_date') is not None and j.created_date.date() == yesterday]
        yesterdays_quotes = [q for q in quotes if q.get('created_date') is not None and q.created_date.date() == yesterday]
        
        # Weekly metrics
        week_jobs = [j for j in jobs if j.get('created_date') is not None and j.created_date.date() >= week_ago]
        week_quotes = [q for q in quotes if q.get('created_date') is not None and q.created_date.date() >= week_ago]
        
        daily_performance = {
            'date': today.strftime('%Y-%m-%d'),
            'today': {
                'jobs_created': len(todays_jobs),
                'quotes_generated': len(todays_quotes),
                'new_contacts': len(todays_contacts),
                'completed_jobs': len([j for j in todays_jobs if j.get('status') is not None and j.status == 'completed'])
            },
            'yesterday_comparison': {
                'jobs_change': len(todays_jobs) - len(yesterdays_jobs),
                'quotes_change': len(todays_quotes) - len(yesterdays_quotes),
                'performance_trend': 'improving' if len(todays_jobs) > len(yesterdays_jobs) else 'declining' if len(todays_jobs) < len(yesterdays_jobs) else 'stable'
            },
            'weekly_summary': {
                'total_jobs': len(week_jobs),
                'total_quotes': len(week_quotes),
                'daily_average_jobs': len(week_jobs) / 7,
                'daily_average_quotes': len(week_quotes) / 7
            }
        }
        
        return daily_performance
    
    def monitor_crew_productivity(self, storage):
        """Monitor crew productivity and utilization"""
        jobs = storage.get_all_jobs()
        
        # Analyze job completion patterns
        productivity_metrics = {
            'jobs_in_progress': len([j for j in jobs if j.get('status') is not None and j.status == 'in_progress']),
            'jobs_completed_today': 0,
            'average_completion_rate': 0,
            'crew_utilization': 0,
            'bottleneck_analysis': []
        }
        
        today = datetime.now(self.hawaii_tz).date()
        completed_today = [j for j in jobs if j.get('status') is not None and j.status == 'completed' and 
                          j.get('updated_date') is not None and j.updated_date.date() == today]
        
        productivity_metrics['jobs_completed_today'] = len(completed_today)
        
        # Analyze service type completion rates
        service_completion = defaultdict(lambda: {'total': 0, 'completed': 0})
        for job in jobs:
            if job.get('service_type') is not None:
                service_completion[job.service_type]['total'] += 1
                if job.get('status') is not None and job.status == 'completed':
                    service_completion[job.service_type]['completed'] += 1
        
        # Identify bottlenecks
        for service, data in service_completion.items():
            if data['total'] >= 3:  # Minimum sample size
                completion_rate = (data['completed'] / data['total']) * 100
                if completion_rate < 70:  # Below 70% completion rate
                    productivity_metrics['bottleneck_analysis'].append({
                        'service': service,
                        'completion_rate': round(completion_rate, 1),
                        'total_jobs': data['total'],
                        'issue': 'Low completion rate - potential workflow bottleneck'
                    })
        
        return productivity_metrics
    
    def generate_executive_dashboard_data(self, storage):
        """Generate real-time data for executive dashboard"""
        performance_alerts = self.generate_performance_alerts(storage)
        daily_performance = self.track_daily_performance(storage)
        crew_productivity = self.monitor_crew_productivity(storage)
        
        # Executive summary
        executive_data = {
            'last_updated': datetime.now(self.hawaii_tz).strftime('%Y-%m-%d %H:%M:%S'),
            'system_status': 'optimal' if performance_alerts['alert_summary']['critical_alerts'] == 0 else 'attention_needed',
            'daily_performance': daily_performance,
            'productivity_metrics': crew_productivity,
            'alerts': performance_alerts['alerts'][:5],  # Top 5 alerts
            'key_metrics': performance_alerts['metrics'],
            'health_score': self._calculate_business_health_score(performance_alerts['metrics']),
            'recommendations': self._generate_immediate_recommendations(performance_alerts['alerts'])
        }
        
        return executive_data
    
    def _calculate_business_health_score(self, metrics):
        """Calculate overall business health score (0-100)"""
        scores = []
        
        # Conversion rate score
        conversion_score = min(100, (metrics['conversion_rate'] / 50) * 100)
        scores.append(conversion_score)
        
        # Efficiency score
        efficiency_score = min(100, (14 / max(1, metrics['completion_time'])) * 100)
        scores.append(efficiency_score)
        
        # Retention score
        retention_score = min(100, (metrics['customer_retention'] / 40) * 100)
        scores.append(retention_score)
        
        # Cash flow score
        cash_flow_score = max(0, 100 - metrics['outstanding_ratio'])
        scores.append(cash_flow_score)
        
        # Overall health score
        health_score = sum(scores) / len(scores)
        
        return {
            'overall_score': round(health_score, 1),
            'grade': 'A' if health_score >= 90 else 'B' if health_score >= 80 else 'C' if health_score >= 70 else 'D' if health_score >= 60 else 'F',
            'component_scores': {
                'conversion': round(conversion_score, 1),
                'efficiency': round(efficiency_score, 1),
                'retention': round(retention_score, 1),
                'cash_flow': round(cash_flow_score, 1)
            }
        }
    
    def _generate_immediate_recommendations(self, alerts):
        """Generate immediate actionable recommendations"""
        if not alerts:
            return ["Continue current performance - all metrics within healthy ranges"]
        
        recommendations = []
        
        # Group alerts by category
        alert_categories = defaultdict(list)
        for alert in alerts:
            alert_categories[alert['category']].append(alert)
        
        # Generate category-specific recommendations
        for category, category_alerts in alert_categories.items():
            if category == 'Sales Performance':
                recommendations.append("Immediate: Review and adjust pricing strategy for better conversion")
            elif category == 'Operational Efficiency':
                recommendations.append("Priority: Optimize crew scheduling and project workflows")
            elif category == 'Customer Relations':
                recommendations.append("Focus: Implement customer retention and follow-up programs")
            elif category == 'Financial Performance':
                recommendations.append("Urgent: Enhance marketing and business development efforts")
            elif category == 'Cash Flow':
                recommendations.append("Action: Accelerate invoice collection and payment processing")
        
        return recommendations[:3]  # Top 3 recommendations

# Initialize performance monitor
performance_monitor = PerformanceMonitor()