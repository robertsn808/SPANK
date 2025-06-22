"""
Centralized Analytics Manager for SPANKKS Construction
Coordinates all analytics components for optimal performance
"""

from analytics_config import config
from analytics_service import analytics_service
from business_intelligence import business_intelligence
from ml_analytics import ml_analytics
from performance_monitor import performance_monitor
from automated_insights import automated_insights
import logging
from datetime import datetime
import json

class AnalyticsManager:
    """Centralized manager for all analytics components"""
    
    def __init__(self):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._cache = {}
        self._last_update = {}
    
    def get_comprehensive_analytics(self, storage, force_refresh=False):
        """Get comprehensive analytics with intelligent caching"""
        cache_key = 'comprehensive_analytics'
        
        # Check cache validity
        if not force_refresh and self._is_cache_valid(cache_key, self.config.REFRESH_INTERVALS['business_intelligence']):
            return self._cache[cache_key]
        
        try:
            # Generate all analytics components
            analytics_data = {
                'timestamp': self.config.get_current_time().isoformat(),
                'business_report': analytics_service.generate_business_report(storage),
                'executive_briefing': business_intelligence.generate_executive_briefing(storage),
                'ml_insights': ml_analytics.generate_ml_insights(storage),
                'performance_data': performance_monitor.generate_executive_dashboard_data(storage),
                'daily_insights': automated_insights.generate_daily_insights(storage),
                'system_status': self._get_system_status(storage)
            }
            
            # Cache the results
            self._cache[cache_key] = analytics_data
            self._last_update[cache_key] = datetime.now()
            
            self.logger.info("Comprehensive analytics generated successfully")
            return analytics_data
            
        except Exception as e:
            self.logger.error(f"Error generating comprehensive analytics: {e}")
            return self._get_fallback_analytics()
    
    def get_real_time_metrics(self, storage):
        """Get real-time performance metrics"""
        cache_key = 'real_time_metrics'
        
        if self._is_cache_valid(cache_key, self.config.REFRESH_INTERVALS['real_time_metrics']):
            return self._cache[cache_key]
        
        try:
            metrics = performance_monitor.monitor_real_time_metrics(storage)
            health_score = self.config.calculate_business_health_score(metrics)
            
            real_time_data = {
                'timestamp': self.config.get_current_time().isoformat(),
                'metrics': metrics,
                'health_score': health_score,
                'system_status': 'operational'
            }
            
            self._cache[cache_key] = real_time_data
            self._last_update[cache_key] = datetime.now()
            
            return real_time_data
            
        except Exception as e:
            self.logger.error(f"Error getting real-time metrics: {e}")
            return {'error': str(e), 'timestamp': self.config.get_current_time().isoformat()}
    
    def get_performance_alerts(self, storage):
        """Get current performance alerts"""
        cache_key = 'performance_alerts'
        
        if self._is_cache_valid(cache_key, self.config.REFRESH_INTERVALS['performance_alerts']):
            return self._cache[cache_key]
        
        try:
            alerts_data = performance_monitor.generate_performance_alerts(storage)
            
            # Enhance alerts with configuration-based priorities
            enhanced_alerts = self._enhance_alerts(alerts_data['alerts'])
            
            alert_summary = {
                'timestamp': self.config.get_current_time().isoformat(),
                'alerts': enhanced_alerts,
                'summary': alerts_data['alert_summary'],
                'recommendations': self._generate_alert_recommendations(enhanced_alerts)
            }
            
            self._cache[cache_key] = alert_summary
            self._last_update[cache_key] = datetime.now()
            
            return alert_summary
            
        except Exception as e:
            self.logger.error(f"Error getting performance alerts: {e}")
            return {'alerts': [], 'error': str(e)}
    
    def get_business_insights(self, storage):
        """Get strategic business insights"""
        cache_key = 'business_insights'
        
        if self._is_cache_valid(cache_key, self.config.REFRESH_INTERVALS['ml_insights']):
            return self._cache[cache_key]
        
        try:
            # Get ML insights
            ml_data = ml_analytics.generate_ml_insights(storage)
            
            # Get business intelligence
            bi_data = business_intelligence.generate_executive_briefing(storage)
            
            # Combine and structure insights
            insights = {
                'timestamp': self.config.get_current_time().isoformat(),
                'confidence_level': self._determine_confidence_level(storage),
                'seasonal_insights': ml_data.get('seasonal_demand', {}),
                'pricing_insights': ml_data.get('pricing_optimization', {}),
                'customer_insights': ml_data.get('customer_lifetime_value', {}),
                'growth_forecast': ml_data.get('growth_forecast', {}),
                'strategic_position': bi_data.get('strategic_insights', {}),
                'market_opportunities': bi_data.get('market_analysis', {}).get('market_opportunities', [])
            }
            
            self._cache[cache_key] = insights
            self._last_update[cache_key] = datetime.now()
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error getting business insights: {e}")
            return {'error': str(e)}
    
    def get_executive_summary(self, storage):
        """Get executive summary for rapid decision making"""
        try:
            # Get latest comprehensive data
            comp_data = self.get_comprehensive_analytics(storage)
            real_time = self.get_real_time_metrics(storage)
            alerts = self.get_performance_alerts(storage)
            
            # Generate executive summary
            summary = {
                'timestamp': self.config.get_current_time().isoformat(),
                'business_status': comp_data['daily_insights']['executive_summary']['business_status'],
                'health_score': real_time.get('health_score', {}),
                'key_metrics': {
                    'revenue': comp_data['business_report']['revenue']['total_revenue'],
                    'conversion_rate': comp_data['business_report']['revenue']['quote_conversion_rate'],
                    'customer_count': comp_data['business_report']['customers']['total_customers'],
                    'completion_rate': comp_data['business_report']['operations']['completion_rate']
                },
                'critical_alerts': len([a for a in alerts.get('alerts', []) if a.get('urgency') == 'high']),
                'top_priorities': comp_data['daily_insights']['action_priorities'][:3],
                'growth_outlook': comp_data['ml_insights']['growth_forecast']['annual_projection']['growth_rate'],
                'recommendations': self._get_executive_recommendations(comp_data, alerts)
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating executive summary: {e}")
            return {'error': str(e)}
    
    def _is_cache_valid(self, cache_key, max_age_seconds):
        """Check if cached data is still valid"""
        if cache_key not in self._cache or cache_key not in self._last_update:
            return False
        
        age = (datetime.now() - self._last_update[cache_key]).total_seconds()
        return age < max_age_seconds
    
    def _get_system_status(self, storage):
        """Get overall system status"""
        try:
            # Check data availability
            quotes = storage.get_all_quotes()
            customers = storage.get_all_contacts()
            jobs = storage.get_all_jobs()
            
            # Determine confidence level
            confidence = self._determine_confidence_level(storage)
            
            # Calculate system health
            data_health = 'good' if len(quotes) > 5 and len(customers) > 3 else 'fair' if len(quotes) > 0 else 'developing'
            
            return {
                'overall_status': 'operational',
                'data_health': data_health,
                'confidence_level': confidence,
                'last_activity': self.config.get_current_time().isoformat(),
                'components': {
                    'analytics_service': 'active',
                    'ml_insights': 'active',
                    'business_intelligence': 'active',
                    'performance_monitor': 'active'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {'overall_status': 'degraded', 'error': str(e)}
    
    def _determine_confidence_level(self, storage):
        """Determine ML confidence level based on data volume"""
        quotes = storage.get_all_quotes()
        customers = storage.get_all_contacts()
        
        return self.config.get_ml_confidence_level(len(quotes), len(customers))
    
    def _enhance_alerts(self, alerts):
        """Enhance alerts with configuration-based metadata"""
        enhanced = []
        
        for alert in alerts:
            enhanced_alert = alert.copy()
            
            # Add configuration-based severity scoring
            if alert.get('type') == 'critical':
                enhanced_alert['severity_score'] = 90
            elif alert.get('type') == 'warning':
                enhanced_alert['severity_score'] = 60
            else:
                enhanced_alert['severity_score'] = 30
            
            # Add time-based urgency
            enhanced_alert['age_hours'] = 0  # New alert
            enhanced_alert['escalation_needed'] = enhanced_alert['severity_score'] > 80
            
            enhanced.append(enhanced_alert)
        
        return sorted(enhanced, key=lambda x: x['severity_score'], reverse=True)
    
    def _generate_alert_recommendations(self, alerts):
        """Generate recommendations based on alerts"""
        recommendations = []
        
        critical_alerts = [a for a in alerts if a.get('severity_score', 0) > 80]
        
        if critical_alerts:
            recommendations.append("Address critical performance issues immediately")
        
        conversion_alerts = [a for a in alerts if 'conversion' in a.get('title', '').lower()]
        if conversion_alerts:
            recommendations.append("Review pricing and sales processes")
        
        cash_flow_alerts = [a for a in alerts if 'cash flow' in a.get('title', '').lower()]
        if cash_flow_alerts:
            recommendations.append("Accelerate invoice collection efforts")
        
        if not recommendations:
            recommendations.append("Continue monitoring current performance")
        
        return recommendations[:3]
    
    def _get_executive_recommendations(self, comp_data, alerts):
        """Get executive-level recommendations"""
        recommendations = []
        
        # Revenue recommendations
        revenue = comp_data['business_report']['revenue']['total_revenue']
        if revenue < 10000:
            recommendations.append("Focus on customer acquisition and service delivery expansion")
        elif revenue < 50000:
            recommendations.append("Optimize pricing strategy and implement customer retention programs")
        else:
            recommendations.append("Consider market expansion and operational scaling opportunities")
        
        # Performance recommendations
        conversion_rate = comp_data['business_report']['revenue']['quote_conversion_rate']
        if conversion_rate < 30:
            recommendations.append("Improve quote conversion through pricing review and process optimization")
        
        # Growth recommendations
        growth_rate = comp_data['business_report']['growth']['monthly_revenue_growth']
        if growth_rate > 10:
            recommendations.append("Capitalize on strong growth with capacity expansion planning")
        elif growth_rate < 0:
            recommendations.append("Implement immediate revenue recovery strategies")
        
        return recommendations[:3]
    
    def _get_fallback_analytics(self):
        """Get basic fallback analytics in case of errors"""
        return {
            'timestamp': self.config.get_current_time().isoformat(),
            'status': 'limited_data',
            'message': 'Analytics system operational with limited data',
            'basic_metrics': {
                'system_health': 'operational',
                'data_status': 'developing',
                'recommendations': ['Continue building business foundation with quality service delivery']
            }
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
        self._last_update.clear()
        self.logger.info("Analytics cache cleared")
    
    def get_cache_status(self):
        """Get current cache status"""
        return {
            'cached_items': list(self._cache.keys()),
            'last_updates': {k: v.isoformat() for k, v in self._last_update.items()},
            'cache_size': len(self._cache)
        }

# Initialize the analytics manager
analytics_manager = AnalyticsManager()