import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import pytz

class BusinessIntelligence:
    """Advanced business intelligence for strategic decision making"""
    
    def __init__(self):
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
    
    def generate_market_insights(self, storage):
        """Analyze market trends and competitive positioning"""
        quotes = storage.get_all_quotes()
        jobs = storage.get_all_jobs()
        contacts = storage.get_all_contacts()
        
        # Service pricing analysis
        service_pricing = defaultdict(list)
        for quote in quotes:
            if hasattr(quote, 'service_type') and hasattr(quote, 'total_amount'):
                service_pricing[quote.service_type].append(quote.total_amount)
        
        # Calculate average pricing per service
        avg_pricing = {}
        for service, prices in service_pricing.items():
            avg_pricing[service] = {
                'average_price': sum(prices) / len(prices),
                'min_price': min(prices),
                'max_price': max(prices),
                'quote_count': len(prices)
            }
        
        # Customer acquisition cost analysis
        total_customers = len(contacts)
        monthly_acquisition = defaultdict(int)
        for contact in contacts:
            if hasattr(contact, 'created_date'):
                try:
                    if isinstance(contact.created_date, str):
                        date_obj = datetime.fromisoformat(contact.created_date.replace('Z', '+00:00'))
                    else:
                        date_obj = contact.created_date
                    month_key = date_obj.strftime('%Y-%m')
                    monthly_acquisition[month_key] += 1
                except:
                    month_key = datetime.now().strftime('%Y-%m')
                    monthly_acquisition[month_key] += 1
        
        # Market opportunity scoring
        opportunities = []
        for service, data in avg_pricing.items():
            if data['quote_count'] >= 3:  # Minimum sample size
                price_variance = data['max_price'] - data['min_price']
                opportunity_score = (data['quote_count'] * 10) + (price_variance / data['average_price'] * 100)
                
                opportunities.append({
                    'service': service,
                    'opportunity_score': round(opportunity_score, 1),
                    'avg_price': data['average_price'],
                    'demand_level': 'High' if data['quote_count'] > 10 else 'Medium' if data['quote_count'] > 5 else 'Low',
                    'pricing_flexibility': 'High' if price_variance > data['average_price'] * 0.3 else 'Medium'
                })
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        return {
            'service_pricing_analysis': avg_pricing,
            'market_opportunities': opportunities[:5],  # Top 5 opportunities
            'monthly_customer_acquisition': dict(monthly_acquisition),
            'total_addressable_market': sum([data['average_price'] * data['quote_count'] for data in avg_pricing.values()])
        }
    
    def analyze_operational_efficiency(self, storage):
        """Deep dive into operational performance metrics"""
        jobs = storage.get_all_jobs()
        quotes = storage.get_all_quotes()
        
        # Job completion timeline analysis
        completion_times = []
        for job in jobs:
            if hasattr(job, 'status') and job.status == 'completed':
                if hasattr(job, 'created_date') and hasattr(job, 'updated_date'):
                    days = (job.updated_date - job.created_date).days
                    completion_times.append(days)
        
        # Resource utilization metrics
        monthly_job_volume = defaultdict(int)
        service_complexity = defaultdict(list)
        
        for job in jobs:
            if hasattr(job, 'created_date'):
                month_key = job.created_date.strftime('%Y-%m')
                monthly_job_volume[month_key] += 1
            
            if hasattr(job, 'service_type') and hasattr(job, 'estimated_hours'):
                service_complexity[job.service_type].append(job.estimated_hours)
        
        # Efficiency scoring
        efficiency_metrics = {
            'avg_completion_time': sum(completion_times) / len(completion_times) if completion_times else 0,
            'job_volume_trend': dict(monthly_job_volume),
            'capacity_utilization': min(100, (len(jobs) / 50) * 100),  # Assuming 50 job capacity
            'service_complexity_analysis': {
                service: {
                    'avg_hours': sum(hours) / len(hours),
                    'complexity_score': 'High' if sum(hours) / len(hours) > 8 else 'Medium' if sum(hours) / len(hours) > 4 else 'Low'
                }
                for service, hours in service_complexity.items() if hours
            }
        }
        
        return efficiency_metrics
    
    def generate_strategic_recommendations(self, storage):
        """AI-powered strategic business recommendations"""
        market_insights = self.generate_market_insights(storage)
        efficiency_metrics = self.analyze_operational_efficiency(storage)
        
        recommendations = []
        
        # Revenue optimization recommendations
        top_opportunity = market_insights['market_opportunities'][0] if market_insights['market_opportunities'] else None
        if top_opportunity and top_opportunity['opportunity_score'] > 50:
            recommendations.append({
                'category': 'Revenue Growth',
                'priority': 'High',
                'title': f'Expand {top_opportunity["service"]} Services',
                'description': f'High demand service with {top_opportunity["demand_level"].lower()} market penetration.',
                'impact': f'Potential 25-40% revenue increase in this category',
                'action_items': [
                    'Develop specialized pricing strategy',
                    'Train additional crew members',
                    'Create targeted marketing campaign'
                ],
                'timeline': '30-60 days',
                'investment_required': 'Medium'
            })
        
        # Operational efficiency recommendations
        if efficiency_metrics['avg_completion_time'] > 14:
            recommendations.append({
                'category': 'Operational Excellence',
                'priority': 'High',
                'title': 'Optimize Project Timeline',
                'description': f'Current average completion time is {efficiency_metrics["avg_completion_time"]:.1f} days.',
                'impact': '20-30% improvement in customer satisfaction',
                'action_items': [
                    'Implement project management software',
                    'Standardize workflow processes',
                    'Conduct crew efficiency training'
                ],
                'timeline': '45-90 days',
                'investment_required': 'Low'
            })
        
        # Market expansion recommendations
        if efficiency_metrics['capacity_utilization'] > 80:
            recommendations.append({
                'category': 'Business Growth',
                'priority': 'Medium',
                'title': 'Scale Operations',
                'description': 'High capacity utilization indicates demand exceeds current capability.',
                'impact': '50-75% increase in monthly job capacity',
                'action_items': [
                    'Hire additional crew members',
                    'Invest in additional equipment',
                    'Expand service territories'
                ],
                'timeline': '60-120 days',
                'investment_required': 'High'
            })
        
        # Technology advancement recommendations
        recommendations.append({
            'category': 'Technology Integration',
            'priority': 'Medium',
            'title': 'Implement Digital Workflow',
            'description': 'Enhance customer experience with digital project tracking.',
            'impact': 'Improved customer satisfaction and operational efficiency',
            'action_items': [
                'Deploy mobile apps for crew',
                'Implement IoT sensors for equipment',
                'Automate customer communications'
            ],
            'timeline': '90-180 days',
            'investment_required': 'Medium'
        })
        
        return recommendations
    
    def calculate_roi_projections(self, storage, recommendations):
        """Calculate return on investment for strategic recommendations"""
        from analytics_service import analytics_service
        
        business_report = analytics_service.generate_business_report(storage)
        current_revenue = business_report['revenue']['total_revenue']
        
        roi_analysis = []
        
        for rec in recommendations:
            if rec['category'] == 'Revenue Growth':
                # Estimate revenue impact
                potential_increase = current_revenue * 0.3  # 30% increase assumption
                investment_cost = {
                    'Low': 2000,
                    'Medium': 8000,
                    'High': 25000
                }.get(rec['investment_required'], 5000)
                
                roi_percentage = ((potential_increase - investment_cost) / investment_cost) * 100 if investment_cost > 0 else 0
                payback_months = investment_cost / (potential_increase / 12) if potential_increase > 0 else 12
                annual_return = potential_increase
                
            elif rec['category'] == 'Operational Excellence':
                # Estimate cost savings
                cost_savings = current_revenue * 0.15  # 15% efficiency gain
                investment_cost = {
                    'Low': 1500,
                    'Medium': 5000,
                    'High': 15000
                }.get(rec['investment_required'], 3000)
                
                roi_percentage = ((cost_savings - investment_cost) / investment_cost) * 100 if investment_cost > 0 else 0
                payback_months = investment_cost / (cost_savings / 12) if cost_savings > 0 else 12
                annual_return = cost_savings
                
            else:
                # General business growth
                potential_increase = current_revenue * 0.2
                investment_cost = {
                    'Low': 3000,
                    'Medium': 10000,
                    'High': 30000
                }.get(rec['investment_required'], 10000)
                
                roi_percentage = ((potential_increase - investment_cost) / investment_cost) * 100 if investment_cost > 0 else 0
                payback_months = investment_cost / (potential_increase / 12) if potential_increase > 0 else 12
                annual_return = potential_increase
            
            roi_analysis.append({
                'recommendation': rec['title'],
                'investment_required': investment_cost,
                'projected_annual_return': annual_return,
                'roi_percentage': round(roi_percentage, 1),
                'payback_period_months': round(payback_months, 1),
                'risk_level': 'Low' if roi_percentage > 200 else 'Medium' if roi_percentage > 100 else 'High'
            })
        
        return roi_analysis
    
    def generate_executive_briefing(self, storage):
        """Generate comprehensive executive briefing document"""
        from analytics_service import analytics_service
        
        # Gather all intelligence data
        business_report = analytics_service.generate_business_report(storage)
        cash_flow = analytics_service.get_cash_flow_forecast(storage)
        market_insights = self.generate_market_insights(storage)
        efficiency_metrics = self.analyze_operational_efficiency(storage)
        recommendations = self.generate_strategic_recommendations(storage)
        roi_projections = self.calculate_roi_projections(storage, recommendations)
        
        # Executive summary
        executive_briefing = {
            'briefing_date': datetime.now(self.hawaii_tz).strftime('%Y-%m-%d %H:%M:%S'),
            'company': 'SPANKKS Construction LLC',
            'period': 'Current Business Cycle',
            
            # Key performance indicators
            'kpi_summary': {
                'total_revenue': business_report['revenue']['total_revenue'],
                'conversion_rate': business_report['revenue']['quote_conversion_rate'],
                'customer_count': business_report['customers']['total_customers'],
                'pipeline_value': cash_flow['total_pipeline_value'],
                'operational_efficiency': efficiency_metrics['capacity_utilization']
            },
            
            # Strategic insights
            'strategic_insights': {
                'top_market_opportunity': market_insights['market_opportunities'][0] if market_insights['market_opportunities'] else None,
                'operational_status': 'Excellent' if efficiency_metrics['capacity_utilization'] > 85 else 'Good',
                'growth_trajectory': 'Positive' if business_report['growth']['monthly_revenue_growth'] > 0 else 'Stable',
                'competitive_position': 'Strong' if business_report['revenue']['quote_conversion_rate'] > 40 else 'Moderate'
            },
            
            # Action priorities
            'action_priorities': recommendations[:3],  # Top 3 recommendations
            'roi_analysis': roi_projections,
            
            # Market position
            'market_analysis': market_insights,
            'operational_metrics': efficiency_metrics
        }
        
        return executive_briefing

# Initialize business intelligence service
business_intelligence = BusinessIntelligence()