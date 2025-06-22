"""
Analytics Configuration and Settings for SPANKKS Construction
Centralized configuration for all analytics components
"""

import os
from datetime import datetime
import pytz

class AnalyticsConfig:
    """Centralized configuration for analytics system"""
    
    # Hawaii timezone
    HAWAII_TZ = pytz.timezone('Pacific/Honolulu')
    
    # Business metrics thresholds
    PERFORMANCE_THRESHOLDS = {
        'conversion_rate': {
            'excellent': 50,
            'good': 35,
            'fair': 25,
            'poor': 15
        },
        'completion_time_days': {
            'excellent': 7,
            'good': 10,
            'fair': 14,
            'poor': 21
        },
        'customer_retention': {
            'excellent': 50,
            'good': 35,
            'fair': 25,
            'poor': 15
        },
        'capacity_utilization': {
            'excellent': 85,
            'good': 70,
            'fair': 55,
            'poor': 40
        }
    }
    
    # Alert thresholds for performance monitoring
    ALERT_THRESHOLDS = {
        'low_conversion_rate': 25,
        'high_completion_time': 14,
        'low_customer_retention': 20,
        'revenue_decline': -10,
        'capacity_overload': 90,
        'outstanding_invoices': 0.4
    }
    
    # Hawaii market factors
    HAWAII_MARKET = {
        'seasonal_factors': {
            'winter': 1.3,  # Peak tourist season
            'summer': 1.1,  # Local activity
            'shoulder': 0.9  # Moderate periods
        },
        'market_growth_rate': 0.08,  # 8% annual growth
        'tourism_factor': 1.12,      # Tourism boost
        'cost_inflation': 1.04,      # 4% cost inflation
        'get_tax_rate': 0.045        # 4.5% O'ahu GET tax
    }
    
    # Service hour estimates for scheduling
    SERVICE_HOURS = {
        'Drywall Services': 6,
        'Flooring Installation': 8,
        'Fence Building': 10,
        'General Handyman': 4,
        'Plumbing Repair': 3,
        'Electrical Work': 4,
        'Painting': 5,
        'Home Renovation': 12,
        'Custom Service': 5  # Default
    }
    
    # Analytics refresh intervals (seconds)
    REFRESH_INTERVALS = {
        'real_time_metrics': 60,      # 1 minute
        'performance_alerts': 300,    # 5 minutes
        'ml_insights': 900,           # 15 minutes
        'business_intelligence': 1800, # 30 minutes
        'daily_insights': 3600        # 1 hour
    }
    
    # ML confidence levels
    ML_CONFIDENCE = {
        'high': {'min_quotes': 15, 'min_customers': 10},
        'medium': {'min_quotes': 8, 'min_customers': 5},
        'developing': {'min_quotes': 0, 'min_customers': 0}
    }
    
    # ROI calculation parameters
    ROI_INVESTMENT_LEVELS = {
        'low': {'revenue_growth': 1500, 'operational': 1000, 'general': 2000},
        'medium': {'revenue_growth': 8000, 'operational': 5000, 'general': 7500},
        'high': {'revenue_growth': 25000, 'operational': 15000, 'general': 22500}
    }
    
    # Business health scoring weights
    HEALTH_SCORE_WEIGHTS = {
        'conversion_rate': 0.25,
        'efficiency': 0.25,
        'retention': 0.25,
        'cash_flow': 0.25
    }
    
    @classmethod
    def get_current_time(cls):
        """Get current Hawaii time"""
        return datetime.now(cls.HAWAII_TZ)
    
    @classmethod
    def get_performance_grade(cls, metric_type, value):
        """Get performance grade for a metric"""
        thresholds = cls.PERFORMANCE_THRESHOLDS.get(metric_type, {})
        
        if value >= thresholds.get('excellent', 100):
            return 'A', 'Excellent'
        elif value >= thresholds.get('good', 80):
            return 'B', 'Good'
        elif value >= thresholds.get('fair', 60):
            return 'C', 'Fair'
        else:
            return 'D', 'Needs Improvement'
    
    @classmethod
    def get_seasonal_factor(cls, month):
        """Get seasonal factor for a given month"""
        if month in [12, 1, 2]:  # Winter
            return cls.HAWAII_MARKET['seasonal_factors']['winter']
        elif month in [6, 7, 8]:  # Summer
            return cls.HAWAII_MARKET['seasonal_factors']['summer']
        else:  # Shoulder seasons
            return cls.HAWAII_MARKET['seasonal_factors']['shoulder']
    
    @classmethod
    def get_ml_confidence_level(cls, quote_count, customer_count):
        """Determine ML confidence level based on data volume"""
        if (quote_count >= cls.ML_CONFIDENCE['high']['min_quotes'] and 
            customer_count >= cls.ML_CONFIDENCE['high']['min_customers']):
            return 'High'
        elif (quote_count >= cls.ML_CONFIDENCE['medium']['min_quotes'] and 
              customer_count >= cls.ML_CONFIDENCE['medium']['min_customers']):
            return 'Medium'
        else:
            return 'Developing'
    
    @classmethod
    def calculate_business_health_score(cls, metrics):
        """Calculate overall business health score"""
        scores = {}
        weights = cls.HEALTH_SCORE_WEIGHTS
        
        # Conversion rate score (0-100)
        conversion_score = min(100, (metrics.get('conversion_rate', 0) / 50) * 100)
        scores['conversion'] = conversion_score
        
        # Efficiency score (inverse of completion time)
        completion_time = max(1, metrics.get('completion_time', 14))
        efficiency_score = min(100, (14 / completion_time) * 100)
        scores['efficiency'] = efficiency_score
        
        # Retention score
        retention_score = min(100, (metrics.get('retention_rate', 0) / 40) * 100)
        scores['retention'] = retention_score
        
        # Cash flow score
        outstanding_ratio = metrics.get('outstanding_ratio', 0)
        cash_flow_score = max(0, 100 - outstanding_ratio)
        scores['cash_flow'] = cash_flow_score
        
        # Weighted overall score
        overall_score = sum(score * weights[key] for key, score in {
            'conversion_rate': conversion_score,
            'efficiency': efficiency_score,
            'retention': retention_score,
            'cash_flow': cash_flow_score
        }.items())
        
        grade, status = cls.get_performance_grade('overall', overall_score)
        
        return {
            'overall_score': round(overall_score, 1),
            'grade': grade,
            'status': status,
            'component_scores': {k: round(v, 1) for k, v in scores.items()}
        }

# Analytics configuration instance
config = AnalyticsConfig()