import json
import os
import math
from datetime import datetime, timedelta
from collections import defaultdict
import pytz

class MLAnalytics:
    """Machine learning analytics for construction business optimization"""
    
    def __init__(self):
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
    
    def predict_seasonal_demand(self, storage):
        """Predict seasonal demand patterns for construction services"""
        service_requests = storage.get_all_service_requests()
        quotes = storage.get_all_quotes()
        
        # Analyze seasonal patterns
        monthly_demand = defaultdict(lambda: defaultdict(int))
        
        for request in service_requests:
            if hasattr(request, 'preferred_date') and request.preferred_date:
                try:
                    date = datetime.strptime(request.preferred_date, '%Y-%m-%d')
                    month = date.month
                    service = request.service
                    monthly_demand[month][service] += 1
                except:
                    continue
        
        # Calculate seasonal indices
        seasonal_predictions = {}
        for month in range(1, 13):
            month_name = datetime(2025, month, 1).strftime('%B')
            total_demand = sum(monthly_demand[month].values())
            
            # Hawaii-specific seasonal factors
            if month in [12, 1, 2]:  # Winter - peak tourist season
                seasonal_factor = 1.3
                weather_impact = "Dry season - optimal construction conditions"
            elif month in [6, 7, 8]:  # Summer - locals active
                seasonal_factor = 1.1
                weather_impact = "Summer heat - indoor projects preferred"
            elif month in [3, 4, 5, 9, 10, 11]:  # Shoulder seasons
                seasonal_factor = 0.9
                weather_impact = "Moderate conditions - all services viable"
            else:
                seasonal_factor = 1.0
                weather_impact = "Standard conditions"
            
            top_services = sorted(monthly_demand[month].items(), key=lambda x: x[1], reverse=True)[:3]
            
            seasonal_predictions[month_name] = {
                'demand_level': total_demand,
                'seasonal_factor': seasonal_factor,
                'weather_impact': weather_impact,
                'top_services': top_services,
                'predicted_growth': round((total_demand * seasonal_factor - total_demand) / total_demand * 100, 1) if total_demand > 0 else 0
            }
        
        return seasonal_predictions
    
    def optimize_pricing_strategy(self, storage):
        """ML-driven pricing optimization based on demand and competition"""
        quotes = storage.get_all_quotes()
        
        # Analyze quote acceptance patterns
        service_pricing = defaultdict(list)
        acceptance_rates = defaultdict(lambda: {'accepted': 0, 'total': 0})
        
        for quote in quotes:
            if hasattr(quote, 'service_type') and hasattr(quote, 'total_amount'):
                service = quote.service_type
                price = quote.total_amount
                
                service_pricing[service].append(price)
                acceptance_rates[service]['total'] += 1
                
                if hasattr(quote, 'status') and quote.status == 'accepted':
                    acceptance_rates[service]['accepted'] += 1
        
        # Calculate optimal pricing
        pricing_recommendations = {}
        
        for service, prices in service_pricing.items():
            if len(prices) >= 3:  # Minimum sample size
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)
                
                # Calculate acceptance rate
                total_quotes = acceptance_rates[service]['total']
                accepted_quotes = acceptance_rates[service]['accepted']
                acceptance_rate = (accepted_quotes / total_quotes * 100) if total_quotes > 0 else 0
                
                # Price optimization logic
                if acceptance_rate > 80:
                    # High acceptance - can increase prices
                    recommended_price = avg_price * 1.1
                    strategy = "Increase pricing by 10% - high demand service"
                elif acceptance_rate < 30:
                    # Low acceptance - reduce prices
                    recommended_price = avg_price * 0.9
                    strategy = "Reduce pricing by 10% - improve competitiveness"
                else:
                    # Optimal range
                    recommended_price = avg_price
                    strategy = "Maintain current pricing - optimal acceptance rate"
                
                # Hawaii market adjustments
                hawaii_factor = 1.15  # Higher cost of living
                recommended_price *= hawaii_factor
                
                pricing_recommendations[service] = {
                    'current_avg_price': round(avg_price, 2),
                    'recommended_price': round(recommended_price, 2),
                    'price_range': f"${min_price:.0f} - ${max_price:.0f}",
                    'acceptance_rate': round(acceptance_rate, 1),
                    'strategy': strategy,
                    'confidence_level': min(95, len(prices) * 10),  # Higher confidence with more data
                    'potential_revenue_impact': round((recommended_price - avg_price) * accepted_quotes, 2)
                }
        
        return pricing_recommendations
    
    def predict_customer_lifetime_value(self, storage):
        """Predict customer lifetime value using ML patterns"""
        contacts = storage.get_all_contacts()
        invoices = storage.get_all_invoices()
        
        # Customer value analysis
        customer_values = defaultdict(lambda: {'total_spent': 0, 'jobs_count': 0, 'avg_job_value': 0, 'recency': 0})
        
        for invoice in invoices:
            if hasattr(invoice, 'contact_id') and hasattr(invoice, 'total_amount'):
                contact_id = invoice.contact_id
                amount = invoice.total_amount
                
                customer_values[contact_id]['total_spent'] += amount
                customer_values[contact_id]['jobs_count'] += 1
                
                if hasattr(invoice, 'created_date'):
                    days_since = (datetime.now() - invoice.created_date).days
                    customer_values[contact_id]['recency'] = int(days_since)
        
        # Calculate CLV predictions
        clv_predictions = {}
        
        for contact_id, data in customer_values.items():
            if data['jobs_count'] > 0:
                data['avg_job_value'] = float(data['total_spent'] / data['jobs_count'])
                
                # CLV prediction model
                # Factors: frequency, recency, monetary value
                frequency_score = min(10, data['jobs_count'])  # Cap at 10
                recency_score = max(1, 10 - (data['recency'] / 30))  # Decay over time
                monetary_score = min(10, data['avg_job_value'] / 500)  # Normalize to scale
                
                # Weighted CLV score
                clv_score = (frequency_score * 0.4 + recency_score * 0.3 + monetary_score * 0.3)
                
                # Predict future value
                predicted_annual_value = data['avg_job_value'] * (frequency_score / 2)
                predicted_lifetime_value = predicted_annual_value * 5  # 5-year projection
                
                # Customer segmentation
                if clv_score >= 8:
                    segment = "VIP Customer"
                    retention_strategy = "Premium service, exclusive offers"
                elif clv_score >= 6:
                    segment = "High Value"
                    retention_strategy = "Loyalty rewards, priority scheduling"
                elif clv_score >= 4:
                    segment = "Regular Customer"
                    retention_strategy = "Regular follow-ups, service reminders"
                else:
                    segment = "Occasional Customer"
                    retention_strategy = "Re-engagement campaigns, special promotions"
                
                clv_predictions[contact_id] = {
                    'current_value': round(data['total_spent'], 2),
                    'predicted_clv': round(predicted_lifetime_value, 2),
                    'clv_score': round(clv_score, 1),
                    'segment': segment,
                    'retention_strategy': retention_strategy,
                    'jobs_count': data['jobs_count'],
                    'avg_job_value': round(data['avg_job_value'], 2),
                    'risk_level': 'High' if recency_score < 3 else 'Medium' if recency_score < 6 else 'Low'
                }
        
        # Sort by CLV
        sorted_customers = sorted(clv_predictions.items(), key=lambda x: x[1]['predicted_clv'], reverse=True)
        
        return {
            'customer_predictions': dict(sorted_customers[:20]),  # Top 20 customers
            'segment_distribution': self._calculate_segment_distribution(clv_predictions),
            'total_predicted_value': sum([pred['predicted_clv'] for pred in clv_predictions.values()])
        }
    
    def _calculate_segment_distribution(self, clv_predictions):
        """Calculate distribution of customers across segments"""
        segments = defaultdict(int)
        for pred in clv_predictions.values():
            segments[pred['segment']] += 1
        return dict(segments)
    
    def optimize_crew_scheduling(self, storage):
        """Optimize crew scheduling using workload analysis"""
        jobs = storage.get_all_jobs()
        
        # Analyze job patterns
        daily_workload = defaultdict(lambda: {'job_count': 0, 'estimated_hours': 0})
        service_duration = defaultdict(list)
        
        for job in jobs:
            if hasattr(job, 'scheduled_date') and job.scheduled_date:
                try:
                    date_str = job.scheduled_date.strftime('%Y-%m-%d') if hasattr(job.scheduled_date, 'strftime') else job.scheduled_date
                    daily_workload[date_str]['job_count'] += 1
                    
                    # Estimate hours based on service type
                    if hasattr(job, 'service_type'):
                        hours = self._estimate_service_hours(job.service_type)
                        daily_workload[date_str]['estimated_hours'] += hours
                        service_duration[job.service_type].append(hours)
                except:
                    continue
        
        # Optimization recommendations
        optimization_insights = {
            'peak_days': [],
            'underutilized_days': [],
            'crew_requirements': {},
            'efficiency_recommendations': []
        }
        
        # Analyze workload distribution
        for date, workload in daily_workload.items():
            if workload['estimated_hours'] > 32:  # Assuming 4 crew members * 8 hours
                optimization_insights['peak_days'].append({
                    'date': date,
                    'jobs': workload['job_count'],
                    'hours': workload['estimated_hours'],
                    'recommendation': 'Consider additional crew or reschedule non-urgent jobs'
                })
            elif workload['estimated_hours'] < 16:  # Less than 2 crew members
                optimization_insights['underutilized_days'].append({
                    'date': date,
                    'jobs': workload['job_count'],
                    'hours': workload['estimated_hours'],
                    'recommendation': 'Opportunity for additional bookings or maintenance tasks'
                })
        
        # Crew requirement analysis
        avg_daily_hours = sum([w['estimated_hours'] for w in daily_workload.values()]) / len(daily_workload) if daily_workload else 0
        recommended_crew_size = math.ceil(avg_daily_hours / 8)
        
        optimization_insights['crew_requirements'] = {
            'recommended_size': recommended_crew_size,
            'current_utilization': f"{avg_daily_hours:.1f} hours/day",
            'efficiency_score': min(100, (avg_daily_hours / (recommended_crew_size * 8)) * 100)
        }
        
        return optimization_insights
    
    def _estimate_service_hours(self, service_type):
        """Estimate hours required for different service types"""
        service_hours = {
            'Drywall Services': 6,
            'Flooring Installation': 8,
            'Fence Building': 10,
            'General Handyman': 4,
            'Plumbing Repair': 3,
            'Electrical Work': 4,
            'Painting': 5,
            'Home Renovation': 12
        }
        return service_hours.get(service_type, 5)  # Default 5 hours
    
    def generate_growth_forecast(self, storage):
        """Generate ML-based growth forecasting"""
        from analytics_service import analytics_service
        
        # Get historical data
        business_report = analytics_service.generate_business_report(storage)
        seasonal_demand = self.predict_seasonal_demand(storage)
        
        # Growth prediction model
        current_revenue = business_report['revenue']['total_revenue']
        current_customers = business_report['customers']['total_customers']
        conversion_rate = business_report['revenue']['quote_conversion_rate']
        
        # Hawaii construction market factors
        market_growth_rate = 0.08  # 8% annual growth in Hawaii construction
        tourism_factor = 1.12  # Tourism boost
        cost_inflation = 1.04  # 4% cost inflation
        
        # 12-month forecast
        monthly_forecasts = []
        base_monthly_revenue = current_revenue / 12 if current_revenue > 0 else 5000
        
        for month in range(1, 13):
            month_name = datetime(2025, month, 1).strftime('%B')
            
            # Get seasonal factor
            seasonal_factor = 1.0
            if month_name in seasonal_demand:
                seasonal_factor = seasonal_demand[month_name]['seasonal_factor']
            
            # Calculate projected revenue
            projected_revenue = base_monthly_revenue * seasonal_factor * tourism_factor
            
            # Add growth trend
            growth_multiplier = 1 + (market_growth_rate * (month / 12))
            projected_revenue *= growth_multiplier
            
            # Customer growth projection
            projected_customers = current_customers + (month * 2)  # 2 new customers per month
            
            monthly_forecasts.append({
                'month': month_name,
                'projected_revenue': round(projected_revenue, 2),
                'projected_customers': projected_customers,
                'confidence_level': max(60, 95 - (month * 3)),  # Decreasing confidence over time
                'key_factors': [
                    f"Seasonal factor: {seasonal_factor}x",
                    f"Market growth: {market_growth_rate*100}%",
                    f"Tourism impact: {(tourism_factor-1)*100:.0f}%"
                ]
            })
        
        return {
            'annual_projection': {
                'revenue': sum([f['projected_revenue'] for f in monthly_forecasts]),
                'customer_growth': monthly_forecasts[-1]['projected_customers'] - current_customers,
                'market_share_opportunity': "3-5% of O'ahu handyman market",
                'growth_rate': round(((sum([f['projected_revenue'] for f in monthly_forecasts]) - current_revenue) / current_revenue * 100), 1) if current_revenue > 0 else 0
            },
            'monthly_forecasts': monthly_forecasts,
            'risk_factors': [
                'Weather disruptions during rainy season',
                'Material cost fluctuations',
                'Tourism seasonality impacts',
                'Labor availability constraints'
            ],
            'growth_opportunities': [
                'Expand into commercial properties',
                'Develop maintenance contracts',
                'Add emergency repair services',
                'Partner with property management companies'
            ]
        }
    
    def generate_ml_insights(self, storage):
        """Generate comprehensive ML-driven business insights"""
        seasonal_demand = self.predict_seasonal_demand(storage)
        pricing_optimization = self.optimize_pricing_strategy(storage)
        clv_predictions = self.predict_customer_lifetime_value(storage)
        crew_optimization = self.optimize_crew_scheduling(storage)
        growth_forecast = self.generate_growth_forecast(storage)
        
        return {
            'insights_generated': datetime.now(self.hawaii_tz).strftime('%Y-%m-%d %H:%M:%S'),
            'seasonal_demand': seasonal_demand,
            'pricing_optimization': pricing_optimization,
            'customer_lifetime_value': clv_predictions,
            'crew_optimization': crew_optimization,
            'growth_forecast': growth_forecast,
            'ml_confidence': 'High' if len(storage.get_all_quotes()) > 10 else 'Medium' if len(storage.get_all_quotes()) > 5 else 'Developing'
        }

# Initialize ML analytics service
ml_analytics = MLAnalytics()