import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import pytz

class AutomatedInsights:
    """Automated business insights and strategic recommendations engine"""
    
    def __init__(self):
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
    
    def generate_daily_insights(self, storage):
        """Generate automated daily business insights"""
        from analytics_service import analytics_service
        from ml_analytics import ml_analytics
        from performance_monitor import performance_monitor
        
        # Gather comprehensive data
        business_report = analytics_service.generate_business_report(storage)
        ml_insights = ml_analytics.generate_ml_insights(storage)
        performance_data = performance_monitor.generate_executive_dashboard_data(storage)
        
        # Generate daily insights
        insights = {
            'date': datetime.now(self.hawaii_tz).strftime('%Y-%m-%d'),
            'executive_summary': self._generate_executive_summary(business_report, ml_insights, performance_data),
            'key_opportunities': self._identify_opportunities(business_report, ml_insights),
            'risk_assessment': self._assess_risks(performance_data),
            'optimization_recommendations': self._generate_optimization_recommendations(business_report, ml_insights),
            'market_position': self._analyze_market_position(business_report, ml_insights),
            'financial_health': self._assess_financial_health(business_report),
            'operational_efficiency': self._analyze_operational_efficiency(business_report, performance_data),
            'action_priorities': self._determine_action_priorities(business_report, ml_insights, performance_data)
        }
        
        return insights
    
    def _generate_executive_summary(self, business_report, ml_insights, performance_data):
        """Generate executive summary for daily insights"""
        revenue = business_report['revenue']['total_revenue']
        conversion_rate = business_report['revenue']['quote_conversion_rate']
        health_score = performance_data.get('health_score', {}).get('overall_score', 0)
        
        # Determine business status
        if health_score >= 90:
            status = "Excellent"
            outlook = "Strong performance across all metrics"
        elif health_score >= 80:
            status = "Good"
            outlook = "Solid performance with growth opportunities"
        elif health_score >= 70:
            status = "Fair"
            outlook = "Stable performance with areas for improvement"
        else:
            status = "Needs Attention"
            outlook = "Action required to improve performance"
        
        return {
            'business_status': status,
            'health_score': health_score,
            'outlook': outlook,
            'revenue_performance': f"${revenue:,.0f}" if revenue > 0 else "Building foundation",
            'conversion_efficiency': f"{conversion_rate}%" if conversion_rate > 0 else "Developing",
            'key_insight': self._get_key_daily_insight(business_report, ml_insights),
            'confidence_level': ml_insights.get('ml_confidence', 'Developing')
        }
    
    def _get_key_daily_insight(self, business_report, ml_insights):
        """Get the most important insight for today"""
        insights = []
        
        # Revenue insights
        if business_report['revenue']['total_revenue'] > 0:
            if business_report['revenue']['quote_conversion_rate'] > 50:
                insights.append("High conversion rate indicates strong market position - consider premium pricing")
            elif business_report['revenue']['quote_conversion_rate'] < 25:
                insights.append("Low conversion rate signals need for pricing or process review")
        
        # Customer insights
        if business_report['customers']['repeat_customer_rate'] > 40:
            insights.append("Strong customer loyalty presents referral program opportunity")
        elif business_report['customers']['repeat_customer_rate'] < 20:
            insights.append("Focus on customer retention strategies to improve lifetime value")
        
        # Operational insights
        if business_report['operations']['completion_rate'] > 90:
            insights.append("Excellent completion rate enables capacity expansion")
        elif business_report['operations']['avg_completion_time_days'] > 14:
            insights.append("Extended completion times may impact customer satisfaction")
        
        # Growth insights
        growth_rate = business_report['growth']['monthly_revenue_growth']
        if growth_rate > 10:
            insights.append("Strong growth trend supports business expansion plans")
        elif growth_rate < -5:
            insights.append("Revenue decline requires immediate marketing and operational review")
        
        return insights[0] if insights else "Continue building business foundation with quality service delivery"
    
    def _identify_opportunities(self, business_report, ml_insights):
        """Identify key business opportunities"""
        opportunities = []
        
        # High-value service opportunities
        if 'service_demand' in business_report['operations']:
            top_services = sorted(business_report['operations']['service_demand'].items(), 
                                key=lambda x: x[1], reverse=True)[:3]
            if top_services:
                opportunities.append({
                    'type': 'Service Expansion',
                    'title': f'Expand {top_services[0][0]} Services',
                    'description': f'High demand service with {top_services[0][1]} requests',
                    'potential_impact': 'Revenue increase of 20-30%',
                    'timeline': '30-45 days',
                    'investment_level': 'Medium'
                })
        
        # Pricing optimization opportunities
        if ml_insights.get('pricing_optimization'):
            for service, data in ml_insights['pricing_optimization'].items():
                if 'Increase' in data.get('strategy', ''):
                    opportunities.append({
                        'type': 'Pricing Optimization',
                        'title': f'Optimize {service} Pricing',
                        'description': f'High acceptance rate ({data["acceptance_rate"]}%) supports premium pricing',
                        'potential_impact': f'Additional ${data["potential_revenue_impact"]:,.0f} monthly',
                        'timeline': 'Immediate',
                        'investment_level': 'Low'
                    })
                    break  # Only show top opportunity
        
        # Customer retention opportunities
        retention_rate = business_report['customers']['repeat_customer_rate']
        if retention_rate < 30:
            opportunities.append({
                'type': 'Customer Retention',
                'title': 'Implement Customer Loyalty Program',
                'description': f'Current {retention_rate}% retention rate has significant improvement potential',
                'potential_impact': 'Increase customer lifetime value by 40-60%',
                'timeline': '60-90 days',
                'investment_level': 'Medium'
            })
        
        # Market expansion opportunities
        if business_report['operations']['completion_rate'] > 85:
            opportunities.append({
                'type': 'Market Expansion',
                'title': 'Expand Service Territory',
                'description': 'High operational efficiency supports geographic expansion',
                'potential_impact': 'Market reach increase of 25-40%',
                'timeline': '90-120 days',
                'investment_level': 'High'
            })
        
        return opportunities[:4]  # Top 4 opportunities
    
    def _assess_risks(self, performance_data):
        """Assess current business risks"""
        risks = []
        
        # Financial risks
        health_score = performance_data.get('health_score', {}).get('overall_score', 0)
        if health_score < 70:
            risks.append({
                'category': 'Financial',
                'risk': 'Business Health Below Threshold',
                'severity': 'High' if health_score < 60 else 'Medium',
                'description': f'Overall health score at {health_score}% indicates performance issues',
                'mitigation': 'Review all key metrics and implement improvement plan'
            })
        
        # Operational risks
        alerts = performance_data.get('alerts', [])
        critical_alerts = [a for a in alerts if a.get('type') == 'critical']
        if critical_alerts:
            for alert in critical_alerts[:2]:  # Top 2 critical alerts
                risks.append({
                    'category': 'Operational',
                    'risk': alert['title'],
                    'severity': 'High',
                    'description': alert['message'],
                    'mitigation': alert['recommended_actions'][0] if alert.get('recommended_actions') else 'Address immediately'
                })
        
        # Market risks
        daily_perf = performance_data.get('daily_performance', {})
        if daily_perf.get('yesterday_comparison', {}).get('performance_trend') == 'declining':
            risks.append({
                'category': 'Market',
                'risk': 'Declining Performance Trend',
                'severity': 'Medium',
                'description': 'Performance indicators showing downward trend',
                'mitigation': 'Analyze market conditions and adjust strategy'
            })
        
        return risks
    
    def _generate_optimization_recommendations(self, business_report, ml_insights):
        """Generate optimization recommendations"""
        recommendations = []
        
        # Revenue optimization
        conversion_rate = business_report['revenue']['quote_conversion_rate']
        if conversion_rate < 40:
            recommendations.append({
                'area': 'Revenue Generation',
                'recommendation': 'Improve Quote Conversion Process',
                'specific_actions': [
                    'Review pricing competitiveness',
                    'Enhance quote presentation quality',
                    'Implement faster response times',
                    'Add value-added service options'
                ],
                'expected_outcome': f'Increase conversion from {conversion_rate}% to 45-55%',
                'priority': 'High'
            })
        
        # Operational optimization
        completion_time = business_report['operations']['avg_completion_time_days']
        if completion_time > 10:
            recommendations.append({
                'area': 'Operational Efficiency',
                'recommendation': 'Streamline Project Workflows',
                'specific_actions': [
                    'Implement project management software',
                    'Standardize work procedures',
                    'Optimize material procurement',
                    'Cross-train crew members'
                ],
                'expected_outcome': f'Reduce completion time from {completion_time} to 7-10 days',
                'priority': 'Medium'
            })
        
        # Customer optimization
        retention_rate = business_report['customers']['repeat_customer_rate']
        if retention_rate < 35:
            recommendations.append({
                'area': 'Customer Experience',
                'recommendation': 'Enhance Customer Retention Strategy',
                'specific_actions': [
                    'Create automated follow-up system',
                    'Implement customer satisfaction surveys',
                    'Develop maintenance service offerings',
                    'Launch referral incentive program'
                ],
                'expected_outcome': f'Increase retention from {retention_rate}% to 40-50%',
                'priority': 'High'
            })
        
        return recommendations
    
    def _analyze_market_position(self, business_report, ml_insights):
        """Analyze current market position"""
        conversion_rate = business_report['revenue']['quote_conversion_rate']
        
        # Determine competitive position
        if conversion_rate > 50:
            position = "Market Leader"
            analysis = "Strong competitive position with high customer acceptance"
        elif conversion_rate > 35:
            position = "Strong Competitor"
            analysis = "Good market position with growth opportunities"
        elif conversion_rate > 20:
            position = "Market Participant"
            analysis = "Stable position requiring optimization"
        else:
            position = "Developing Position"
            analysis = "Building market presence and customer base"
        
        # Market insights
        seasonal_data = ml_insights.get('seasonal_demand', {})
        peak_months = []
        for month, data in seasonal_data.items():
            if data.get('seasonal_factor', 1.0) > 1.1:
                peak_months.append(month)
        
        return {
            'competitive_position': position,
            'market_analysis': analysis,
            'peak_seasons': peak_months[:3],
            'market_trends': 'Growing demand in Hawaii construction market',
            'competitive_advantages': self._identify_competitive_advantages(business_report),
            'areas_for_improvement': self._identify_improvement_areas(business_report)
        }
    
    def _identify_competitive_advantages(self, business_report):
        """Identify competitive advantages"""
        advantages = []
        
        if business_report['revenue']['quote_conversion_rate'] > 40:
            advantages.append("High customer acceptance rate")
        
        if business_report['operations']['completion_rate'] > 85:
            advantages.append("Excellent project completion record")
        
        if business_report['customers']['repeat_customer_rate'] > 30:
            advantages.append("Strong customer loyalty")
        
        if business_report['operations']['avg_completion_time_days'] < 10:
            advantages.append("Fast project turnaround")
        
        return advantages if advantages else ["Building competitive strengths"]
    
    def _identify_improvement_areas(self, business_report):
        """Identify areas for improvement"""
        improvements = []
        
        if business_report['revenue']['quote_conversion_rate'] < 30:
            improvements.append("Quote conversion optimization")
        
        if business_report['operations']['avg_completion_time_days'] > 14:
            improvements.append("Project timeline efficiency")
        
        if business_report['customers']['repeat_customer_rate'] < 25:
            improvements.append("Customer retention strategies")
        
        return improvements if improvements else ["Continue current performance"]
    
    def _assess_financial_health(self, business_report):
        """Assess financial health indicators"""
        revenue = business_report['revenue']['total_revenue']
        
        # Financial health assessment
        if revenue > 50000:
            health_status = "Strong"
            outlook = "Excellent financial foundation"
        elif revenue > 20000:
            health_status = "Good"
            outlook = "Solid financial performance"
        elif revenue > 5000:
            health_status = "Fair"
            outlook = "Building financial stability"
        else:
            health_status = "Developing"
            outlook = "Establishing revenue foundation"
        
        return {
            'financial_status': health_status,
            'outlook': outlook,
            'revenue_performance': f"${revenue:,.0f}" if revenue > 0 else "Foundation building",
            'growth_trend': f"{business_report['growth']['monthly_revenue_growth']}%",
            'recommendations': self._get_financial_recommendations(revenue, business_report)
        }
    
    def _get_financial_recommendations(self, revenue, business_report):
        """Get financial recommendations"""
        recommendations = []
        
        if revenue < 10000:
            recommendations.append("Focus on customer acquisition and service delivery")
            recommendations.append("Establish pricing strategy for market positioning")
        elif revenue < 30000:
            recommendations.append("Optimize pricing for higher-value services")
            recommendations.append("Implement customer retention programs")
        else:
            recommendations.append("Consider business expansion opportunities")
            recommendations.append("Invest in operational efficiency improvements")
        
        return recommendations
    
    def _analyze_operational_efficiency(self, business_report, performance_data):
        """Analyze operational efficiency"""
        completion_rate = business_report['operations']['completion_rate']
        completion_time = business_report['operations']['avg_completion_time_days']
        
        # Efficiency scoring
        if completion_rate > 90 and completion_time < 10:
            efficiency_level = "Excellent"
            analysis = "Outstanding operational performance"
        elif completion_rate > 80 and completion_time < 14:
            efficiency_level = "Good"
            analysis = "Strong operational efficiency"
        elif completion_rate > 70:
            efficiency_level = "Fair"
            analysis = "Moderate efficiency with improvement opportunities"
        else:
            efficiency_level = "Needs Improvement"
            analysis = "Operational optimization required"
        
        return {
            'efficiency_level': efficiency_level,
            'analysis': analysis,
            'completion_rate': f"{completion_rate}%",
            'average_completion_time': f"{completion_time} days",
            'optimization_opportunities': self._get_operational_optimizations(business_report)
        }
    
    def _get_operational_optimizations(self, business_report):
        """Get operational optimization opportunities"""
        optimizations = []
        
        completion_time = business_report['operations']['avg_completion_time_days']
        completion_rate = business_report['operations']['completion_rate']
        
        if completion_time > 14:
            optimizations.append("Streamline project workflows and scheduling")
        
        if completion_rate < 85:
            optimizations.append("Improve project completion processes")
        
        if not optimizations:
            optimizations.append("Maintain current high performance standards")
        
        return optimizations
    
    def _determine_action_priorities(self, business_report, ml_insights, performance_data):
        """Determine priority actions for today"""
        priorities = []
        
        # Critical alerts
        alerts = performance_data.get('alerts', [])
        critical_alerts = [a for a in alerts if a.get('urgency') == 'high']
        
        for alert in critical_alerts[:2]:  # Top 2 critical
            priorities.append({
                'priority': 'Critical',
                'action': alert['title'],
                'description': alert['message'],
                'timeline': 'Immediate'
            })
        
        # High-impact opportunities
        if business_report['revenue']['quote_conversion_rate'] < 30:
            priorities.append({
                'priority': 'High',
                'action': 'Review Pricing Strategy',
                'description': 'Low conversion rate requires pricing analysis',
                'timeline': 'This week'
            })
        
        # Growth opportunities
        if business_report['operations']['completion_rate'] > 85:
            priorities.append({
                'priority': 'Medium',
                'action': 'Evaluate Capacity Expansion',
                'description': 'High efficiency supports growth opportunities',
                'timeline': 'Next 30 days'
            })
        
        return priorities[:5]  # Top 5 priorities

# Initialize automated insights
automated_insights = AutomatedInsights()