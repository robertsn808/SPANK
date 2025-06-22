import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import pytz

class BusinessAnalytics:
    """Professional business analytics for SPANKKS Construction"""
    
    def __init__(self):
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
    
    def get_revenue_metrics(self, storage):
        """Calculate comprehensive revenue metrics"""
        invoices = storage.get_all_invoices()
        quotes = storage.get_all_quotes()
        
        # Calculate revenue from paid invoices
        total_revenue = 0
        monthly_revenue = defaultdict(float)
        service_revenue = defaultdict(float)
        
        for invoice in invoices:
            if invoice.status == 'paid':
                total_revenue += invoice.total_amount
                
                # Monthly breakdown
                try:
                    if isinstance(invoice.created_date, str):
                        date_obj = datetime.fromisoformat(invoice.created_date.replace('Z', '+00:00'))
                    else:
                        date_obj = invoice.created_date
                    month_key = date_obj.strftime('%Y-%m')
                    monthly_revenue[month_key] += invoice.total_amount
                except:
                    # Fallback to current month if date parsing fails
                    month_key = datetime.now().strftime('%Y-%m')
                    monthly_revenue[month_key] += invoice.total_amount
                
                # Service type breakdown
                service_revenue[invoice.service_type] += invoice.total_amount
        
        # Quote conversion metrics
        total_quotes = len(quotes)
        accepted_quotes = len([q for q in quotes if q.status == 'accepted'])
        conversion_rate = (accepted_quotes / total_quotes * 100) if total_quotes > 0 else 0
        
        # Average quote value
        quote_values = [q.total_amount for q in quotes if hasattr(q, 'total_amount')]
        avg_quote_value = sum(quote_values) / len(quote_values) if quote_values else 0
        
        return {
            'total_revenue': total_revenue,
            'monthly_revenue': dict(monthly_revenue),
            'service_revenue': dict(service_revenue),
            'quote_conversion_rate': round(conversion_rate, 1),
            'average_quote_value': round(avg_quote_value, 2),
            'total_quotes': total_quotes,
            'accepted_quotes': accepted_quotes
        }
    
    def get_customer_insights(self, storage):
        """Analyze customer behavior and value"""
        contacts = storage.get_all_contacts()
        quotes = storage.get_all_quotes()
        invoices = storage.get_all_invoices()
        
        # Customer lifetime value calculation
        customer_values = defaultdict(float)
        customer_jobs = defaultdict(int)
        
        for invoice in invoices:
            if invoice.status == 'paid':
                customer_values[invoice.contact_id] += invoice.total_amount
                customer_jobs[invoice.contact_id] += 1
        
        # Top customers by value
        top_customers = sorted(customer_values.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Customer acquisition trends
        monthly_new_customers = defaultdict(int)
        for contact in contacts:
            try:
                if isinstance(contact.created_date, str):
                    date_obj = datetime.fromisoformat(contact.created_date.replace('Z', '+00:00'))
                else:
                    date_obj = contact.created_date
                month_key = date_obj.strftime('%Y-%m')
                monthly_new_customers[month_key] += 1
            except:
                # Fallback to current month if date parsing fails
                month_key = datetime.now().strftime('%Y-%m')
                monthly_new_customers[month_key] += 1
        
        # Repeat customer rate
        repeat_customers = len([c for c in customer_jobs.values() if c > 1])
        repeat_rate = (repeat_customers / len(contacts) * 100) if contacts else 0
        
        return {
            'total_customers': len(contacts),
            'top_customers': top_customers,
            'monthly_new_customers': dict(monthly_new_customers),
            'repeat_customer_rate': round(repeat_rate, 1),
            'average_customer_value': round(sum(customer_values.values()) / len(customer_values), 2) if customer_values else 0
        }
    
    def get_operational_metrics(self, storage):
        """Track operational efficiency"""
        jobs = storage.get_all_jobs()
        quotes = storage.get_all_quotes()
        
        # Job completion metrics
        completed_jobs = [j for j in jobs if j.status == 'completed']
        in_progress_jobs = [j for j in jobs if j.status == 'in_progress']
        scheduled_jobs = [j for j in jobs if j.status == 'scheduled']
        
        # Average time from quote to completion
        quote_to_completion_days = []
        for job in completed_jobs:
            if hasattr(job, 'quote_id'):
                quote = next((q for q in quotes if q.id == job.quote_id), None)
                if quote:
                    days_diff = (job.updated_date - quote.created_date).days
                    quote_to_completion_days.append(days_diff)
        
        avg_completion_time = sum(quote_to_completion_days) / len(quote_to_completion_days) if quote_to_completion_days else 0
        
        # Service type demand
        service_demand = defaultdict(int)
        for quote in quotes:
            service_demand[quote.service_type] += 1
        
        return {
            'total_jobs': len(jobs),
            'completed_jobs': len(completed_jobs),
            'in_progress_jobs': len(in_progress_jobs),
            'scheduled_jobs': len(scheduled_jobs),
            'completion_rate': round(len(completed_jobs) / len(jobs) * 100, 1) if jobs else 0,
            'avg_completion_time_days': round(avg_completion_time, 1),
            'service_demand': dict(service_demand)
        }
    
    def get_growth_projections(self, storage):
        """Calculate growth trends and projections"""
        invoices = storage.get_all_invoices()
        contacts = storage.get_all_contacts()
        
        # Monthly revenue trend
        monthly_data = defaultdict(lambda: {'revenue': 0, 'customers': 0})
        
        for invoice in invoices:
            if invoice.status == 'paid':
                try:
                    if isinstance(invoice.created_date, str):
                        date_obj = datetime.fromisoformat(invoice.created_date.replace('Z', '+00:00'))
                    else:
                        date_obj = invoice.created_date
                    month_key = date_obj.strftime('%Y-%m')
                    monthly_data[month_key]['revenue'] += invoice.total_amount
                except:
                    month_key = datetime.now().strftime('%Y-%m')
                    monthly_data[month_key]['revenue'] += invoice.total_amount
        
        for contact in contacts:
            try:
                if isinstance(contact.created_date, str):
                    date_obj = datetime.fromisoformat(contact.created_date.replace('Z', '+00:00'))
                else:
                    date_obj = contact.created_date
                month_key = date_obj.strftime('%Y-%m')
                monthly_data[month_key]['customers'] += 1
            except:
                month_key = datetime.now().strftime('%Y-%m')
                monthly_data[month_key]['customers'] += 1
        
        # Calculate growth rates
        sorted_months = sorted(monthly_data.keys())
        if len(sorted_months) >= 2:
            current_month = monthly_data[sorted_months[-1]]
            previous_month = monthly_data[sorted_months[-2]]
            
            revenue_growth = ((current_month['revenue'] - previous_month['revenue']) / previous_month['revenue'] * 100) if previous_month['revenue'] > 0 else 0
            customer_growth = ((current_month['customers'] - previous_month['customers']) / previous_month['customers'] * 100) if previous_month['customers'] > 0 else 0
        else:
            revenue_growth = 0
            customer_growth = 0
        
        # Simple projection (3-month average growth)
        if len(sorted_months) >= 3:
            recent_revenues = [monthly_data[month]['revenue'] for month in sorted_months[-3:]]
            avg_monthly_revenue = sum(recent_revenues) / len(recent_revenues)
            projected_quarterly_revenue = avg_monthly_revenue * 3
        else:
            projected_quarterly_revenue = 0
        
        return {
            'monthly_revenue_growth': round(revenue_growth, 1),
            'monthly_customer_growth': round(customer_growth, 1),
            'projected_quarterly_revenue': round(projected_quarterly_revenue, 2),
            'monthly_trends': dict(monthly_data)
        }
    
    def generate_business_report(self, storage):
        """Generate comprehensive business analytics report"""
        revenue_metrics = self.get_revenue_metrics(storage)
        customer_insights = self.get_customer_insights(storage)
        operational_metrics = self.get_operational_metrics(storage)
        growth_projections = self.get_growth_projections(storage)
        
        return {
            'report_date': datetime.now(self.hawaii_tz).strftime('%Y-%m-%d %H:%M:%S'),
            'revenue': revenue_metrics,
            'customers': customer_insights,
            'operations': operational_metrics,
            'growth': growth_projections
        }
    
    def get_cash_flow_forecast(self, storage):
        """Generate cash flow projections based on scheduled jobs and quotes"""
        quotes = storage.get_all_quotes()
        jobs = storage.get_all_jobs()
        invoices = storage.get_all_invoices()
        
        # Current outstanding amounts
        pending_quotes = [q for q in quotes if q.status == 'pending']
        outstanding_invoices = [i for i in invoices if i.status in ['sent', 'overdue']]
        scheduled_jobs = [j for j in jobs if j.status == 'scheduled']
        
        # Calculate potential revenue
        pending_quote_value = sum([q.total_amount for q in pending_quotes if hasattr(q, 'total_amount')])
        outstanding_invoice_value = sum([i.total_amount for i in outstanding_invoices])
        scheduled_job_value = sum([j.estimated_value for j in scheduled_jobs if hasattr(j, 'estimated_value')])
        
        # Monthly projections (next 6 months)
        monthly_projections = []
        current_month_revenue = sum([i.total_amount for i in invoices if i.status == 'paid' and 
                                   (datetime.now() - i.created_date).days <= 30])
        
        for i in range(6):
            # Simple projection based on current trends
            month_projection = current_month_revenue * (1 + 0.05 * i)  # 5% growth assumption
            monthly_projections.append({
                'month': (datetime.now() + timedelta(days=30*i)).strftime('%B %Y'),
                'projected_revenue': round(month_projection, 2),
                'confidence': max(90 - i*10, 50)  # Decreasing confidence over time
            })
        
        return {
            'pending_quote_value': pending_quote_value,
            'outstanding_invoice_value': outstanding_invoice_value,
            'scheduled_job_value': scheduled_job_value,
            'total_pipeline_value': pending_quote_value + outstanding_invoice_value + scheduled_job_value,
            'monthly_projections': monthly_projections,
            'current_month_revenue': current_month_revenue
        }
    
    def get_predictive_insights(self, storage):
        """Generate AI-powered business predictions"""
        revenue_metrics = self.get_revenue_metrics(storage)
        customer_insights = self.get_customer_insights(storage)
        operational_metrics = self.get_operational_metrics(storage)
        
        insights = []
        
        # Revenue trend prediction
        if revenue_metrics['quote_conversion_rate'] > 50:
            insights.append({
                'type': 'opportunity',
                'title': 'Strong Conversion Performance',
                'prediction': 'High conversion rate indicates strong market position. Consider raising prices by 5-10%.',
                'confidence': 85,
                'impact': 'Revenue increase of $2,000-4,000 monthly'
            })
        
        # Customer growth prediction
        if customer_insights['repeat_customer_rate'] > 40:
            insights.append({
                'type': 'growth',
                'title': 'Customer Loyalty Strength',
                'prediction': 'High repeat rate suggests strong customer satisfaction. Implement referral program.',
                'confidence': 90,
                'impact': '20-30% increase in new customers'
            })
        
        # Operational efficiency prediction
        if operational_metrics['completion_rate'] > 90:
            insights.append({
                'type': 'efficiency',
                'title': 'Operational Excellence',
                'prediction': 'High completion rate enables capacity expansion. Consider hiring additional crew.',
                'confidence': 75,
                'impact': '40-60% capacity increase'
            })
        
        # Service demand prediction
        top_service = max(operational_metrics['service_demand'], key=operational_metrics['service_demand'].get) if operational_metrics['service_demand'] else None
        if top_service:
            insights.append({
                'type': 'market',
                'title': f'{top_service} Market Opportunity',
                'prediction': f'High demand for {top_service} services. Consider specialization and premium pricing.',
                'confidence': 80,
                'impact': '15-25% revenue increase in this category'
            })
        
        return insights

    def get_performance_alerts(self, storage):
        """Generate performance alerts and recommendations"""
        alerts = []
        
        revenue_metrics = self.get_revenue_metrics(storage)
        customer_insights = self.get_customer_insights(storage)
        operational_metrics = self.get_operational_metrics(storage)
        cash_flow = self.get_cash_flow_forecast(storage)
        
        # Low conversion rate alert
        if revenue_metrics['quote_conversion_rate'] < 30:
            alerts.append({
                'type': 'warning',
                'title': 'Low Quote Conversion Rate',
                'message': f"Current conversion rate is {revenue_metrics['quote_conversion_rate']}%. Consider reviewing pricing or follow-up processes.",
                'action': 'Review quote strategy',
                'priority': 'high'
            })
        
        # High completion time alert
        if operational_metrics['avg_completion_time_days'] > 14:
            alerts.append({
                'type': 'warning',
                'title': 'Extended Project Timeline',
                'message': f"Average completion time is {operational_metrics['avg_completion_time_days']} days. Consider optimizing workflow.",
                'action': 'Review project scheduling',
                'priority': 'medium'
            })
        
        # Cash flow alert
        if cash_flow['outstanding_invoice_value'] > cash_flow['current_month_revenue'] * 0.5:
            alerts.append({
                'type': 'warning',
                'title': 'Outstanding Invoices Alert',
                'message': f"${cash_flow['outstanding_invoice_value']:,.0f} in outstanding invoices. Consider payment follow-up.",
                'action': 'Accelerate collections',
                'priority': 'high'
            })
        
        # Low repeat customer rate
        if customer_insights['repeat_customer_rate'] < 25:
            alerts.append({
                'type': 'info',
                'title': 'Customer Retention Opportunity',
                'message': f"Only {customer_insights['repeat_customer_rate']}% of customers are repeat clients. Consider loyalty programs.",
                'action': 'Implement customer retention strategy',
                'priority': 'medium'
            })
        
        # No recent jobs alert
        jobs = storage.get_all_jobs()
        recent_jobs = [j for j in jobs if (datetime.now() - j.created_date).days <= 7]
        if len(recent_jobs) == 0:
            alerts.append({
                'type': 'warning',
                'title': 'No Recent Job Activity',
                'message': 'No jobs scheduled in the past week. Consider increasing marketing efforts.',
                'action': 'Review marketing strategy',
                'priority': 'high'
            })
        
        return alerts

# Initialize analytics service
analytics_service = BusinessAnalytics()