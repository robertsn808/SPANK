"""
Financial Reporting Service for SPANKKS Construction
Comprehensive financial analysis, profit/loss statements, job costing, and tax reporting
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
import calendar

class FinancialReportingService:
    """Comprehensive financial reporting and analysis system"""
    
    def __init__(self):
        self.data_dir = 'data'
        self.hawaii_get_rate = 0.045  # 4.5% Hawaii GET tax rate
        
    def generate_profit_loss_statement(self, start_date: str, end_date: str) -> Dict:
        """Generate comprehensive Profit & Loss Statement"""
        try:
            from job_tracking_service import job_tracking_service
            
            # Get all financial data within date range
            jobs = job_tracking_service.get_job_records()
            payments = job_tracking_service.get_payment_logs()
            materials = job_tracking_service._load_materials()
            labor = job_tracking_service._load_labor()
            
            # Filter by date range
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            
            filtered_payments = []
            for payment in payments:
                payment_date = datetime.fromisoformat(payment['date_received'].split('T')[0])
                if start_dt <= payment_date <= end_dt:
                    filtered_payments.append(payment)
            
            filtered_materials = []
            for material in materials:
                material_date = datetime.fromisoformat(material['purchase_date'].split('T')[0])
                if start_dt <= material_date <= end_dt:
                    filtered_materials.append(material)
            
            filtered_labor = []
            for labor_entry in labor:
                labor_date = datetime.fromisoformat(labor_entry['work_date'])
                if start_dt <= labor_date <= end_dt:
                    filtered_labor.append(labor_entry)
            
            # Calculate Revenue
            total_revenue = sum(payment['payment_amount'] for payment in filtered_payments)
            collected_tax = total_revenue * self.hawaii_get_rate / (1 + self.hawaii_get_rate)
            net_revenue = total_revenue - collected_tax
            
            # Calculate Cost of Goods Sold (COGS)
            material_costs = sum(material['total_cost'] for material in filtered_materials)
            labor_costs = sum(labor_entry['labor_cost'] + 
                            (labor_entry.get('overtime_hours', 0) * labor_entry.get('overtime_rate', 0))
                            for labor_entry in filtered_labor)
            total_cogs = material_costs + labor_costs
            
            # Calculate Gross Profit
            gross_profit = net_revenue - total_cogs
            gross_margin = (gross_profit / net_revenue * 100) if net_revenue > 0 else 0
            
            # Only include actual tracked operating expenses (none yet tracked)
            operating_expenses = {}
            total_operating_expenses = 0
            
            # Calculate Operating Profit (same as gross profit without tracked expenses)
            operating_profit = gross_profit
            operating_margin = (operating_profit / net_revenue * 100) if net_revenue > 0 else 0
            
            # Calculate Net Income (no taxes deducted without actual expense tracking)
            net_income = operating_profit
            net_margin = (net_income / net_revenue * 100) if net_revenue > 0 else 0
            
            return {
                'period': f"{start_date} to {end_date}",
                'revenue': {
                    'gross_revenue': total_revenue,
                    'collected_hawaii_get': collected_tax,
                    'net_revenue': net_revenue
                },
                'cost_of_goods_sold': {
                    'materials': material_costs,
                    'labor': labor_costs,
                    'total_cogs': total_cogs
                },
                'gross_profit': {
                    'amount': gross_profit,
                    'margin_percentage': gross_margin
                },
                'operating_expenses': operating_expenses,
                'total_operating_expenses': total_operating_expenses,
                'operating_profit': {
                    'amount': operating_profit,
                    'margin_percentage': operating_margin
                },
                'estimated_taxes': estimated_taxes,
                'net_income': {
                    'amount': net_income,
                    'margin_percentage': net_margin
                },
                'summary': {
                    'total_jobs': len(jobs),
                    'jobs_completed': len([j for j in jobs if j.get('status') == 'completed']),
                    'average_job_value': total_revenue / len(filtered_payments) if filtered_payments else 0,
                    'revenue_per_day': total_revenue / ((end_dt - start_dt).days + 1)
                }
            }
            
        except Exception as e:
            logging.error(f"Error generating P&L statement: {e}")
            return {}
    
    def generate_job_costing_report(self, job_id: str = None) -> Dict:
        """Generate detailed job costing report for profitability analysis"""
        try:
            from job_tracking_service import job_tracking_service
            
            jobs = job_tracking_service.get_job_records()
            payments = job_tracking_service.get_payment_logs()
            materials = job_tracking_service._load_materials()
            labor = job_tracking_service._load_labor()
            
            job_costing_data = []
            
            target_jobs = [jobs] if job_id else jobs
            if job_id:
                target_jobs = [job for job in jobs if job['job_id'] == job_id]
            
            for job in target_jobs:
                job_id = job['job_id']
                
                # Get job-specific data
                job_payments = [p for p in payments if p.get('job_id') == job_id]
                job_materials = [m for m in materials if m.get('job_id') == job_id]
                job_labor = [l for l in labor if l.get('job_id') == job_id]
                
                # Calculate revenue
                total_revenue = sum(p['payment_amount'] for p in job_payments)
                
                # Calculate costs
                material_costs = sum(m['total_cost'] for m in job_materials)
                labor_costs = sum(l['labor_cost'] + 
                               (l.get('overtime_hours', 0) * l.get('overtime_rate', 0))
                               for l in job_labor)
                
                # Equipment/rental costs (placeholder - would be enhanced with actual tracking)
                equipment_costs = material_costs * 0.05  # 5% estimate for equipment usage
                
                total_costs = material_costs + labor_costs + equipment_costs
                
                # Calculate profit
                gross_profit = total_revenue - total_costs
                profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
                
                # Labor hours analysis
                total_labor_hours = sum(l.get('hours_worked', 0) for l in job_labor)
                avg_hourly_rate = (labor_costs / total_labor_hours) if total_labor_hours > 0 else 0
                
                job_costing_data.append({
                    'job_id': job_id,
                    'client_name': job['client_name'],
                    'service_type': job['service_type'],
                    'status': job.get('status', 'unknown'),
                    'estimated_cost': job.get('estimated_cost', 0),
                    'actual_revenue': total_revenue,
                    'costs': {
                        'materials': material_costs,
                        'labor': labor_costs,
                        'equipment': equipment_costs,
                        'total': total_costs
                    },
                    'profit_analysis': {
                        'gross_profit': gross_profit,
                        'profit_margin': profit_margin,
                        'estimated_vs_actual': total_revenue - job.get('estimated_cost', 0)
                    },
                    'labor_analysis': {
                        'total_hours': total_labor_hours,
                        'average_hourly_rate': avg_hourly_rate,
                        'estimated_hours': job.get('estimated_labor_hours', 0),
                        'efficiency': (job.get('estimated_labor_hours', 0) / total_labor_hours * 100) if total_labor_hours > 0 else 0
                    },
                    'materials_breakdown': [
                        {
                            'supplier': m.get('supplier_name', 'Unknown'),
                            'cost': m['total_cost'],
                            'date': m.get('purchase_date', '')
                        } for m in job_materials
                    ]
                })
            
            # Summary statistics
            if job_costing_data:
                total_revenue_all = sum(j['actual_revenue'] for j in job_costing_data)
                total_profit_all = sum(j['profit_analysis']['gross_profit'] for j in job_costing_data)
                avg_profit_margin = (total_profit_all / total_revenue_all * 100) if total_revenue_all > 0 else 0
                
                summary = {
                    'total_jobs_analyzed': len(job_costing_data),
                    'total_revenue': total_revenue_all,
                    'total_profit': total_profit_all,
                    'average_profit_margin': avg_profit_margin,
                    'most_profitable_job': max(job_costing_data, key=lambda x: x['profit_analysis']['profit_margin']),
                    'least_profitable_job': min(job_costing_data, key=lambda x: x['profit_analysis']['profit_margin'])
                }
            else:
                summary = {}
            
            return {
                'job_costing_data': job_costing_data,
                'summary': summary,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating job costing report: {e}")
            return {}
    
    def generate_invoice_report(self, status_filter: str = None) -> Dict:
        """Generate comprehensive invoice status and payment tracking report"""
        try:
            from job_tracking_service import job_tracking_service
            
            quotes = job_tracking_service.get_quote_history()
            payments = job_tracking_service.get_payment_logs()
            jobs = job_tracking_service.get_job_records()
            
            invoice_data = []
            
            # Convert quotes to invoice format for reporting
            for quote in quotes:
                if quote.get('quote_status') == 'accepted':
                    # Find related payments
                    quote_payments = [p for p in payments if p.get('quote_id') == quote['quote_id']]
                    total_paid = sum(p['payment_amount'] for p in quote_payments)
                    outstanding = quote['total_amount'] - total_paid
                    
                    # Determine payment status
                    if outstanding <= 0:
                        payment_status = 'paid'
                    elif total_paid > 0:
                        payment_status = 'partial'
                    else:
                        payment_status = 'unpaid'
                    
                    # Calculate days overdue (assuming 30 day terms)
                    invoice_date = datetime.fromisoformat(quote['date_sent'].split('T')[0])
                    due_date = invoice_date + timedelta(days=30)
                    days_overdue = (datetime.now() - due_date).days if datetime.now() > due_date else 0
                    
                    invoice_data.append({
                        'invoice_number': quote['quote_id'].replace('Q', 'I'),  # Convert quote ID to invoice format
                        'quote_id': quote['quote_id'],
                        'client_name': quote['client_name'],
                        'client_phone': quote['client_phone'],
                        'service_type': quote['service_type'],
                        'invoice_date': quote['date_sent'],
                        'due_date': due_date.isoformat(),
                        'amount_billed': quote['total_amount'],
                        'amount_paid': total_paid,
                        'outstanding_balance': outstanding,
                        'payment_status': payment_status,
                        'days_overdue': max(0, days_overdue),
                        'payment_history': [
                            {
                                'date': p['date_received'],
                                'amount': p['payment_amount'],
                                'method': p['payment_method']
                            } for p in quote_payments
                        ]
                    })
            
            # Filter by status if specified
            if status_filter:
                invoice_data = [inv for inv in invoice_data if inv['payment_status'] == status_filter]
            
            # Calculate summary statistics
            total_billed = sum(inv['amount_billed'] for inv in invoice_data)
            total_paid = sum(inv['amount_paid'] for inv in invoice_data)
            total_outstanding = sum(inv['outstanding_balance'] for inv in invoice_data)
            
            overdue_invoices = [inv for inv in invoice_data if inv['days_overdue'] > 0]
            total_overdue = sum(inv['outstanding_balance'] for inv in overdue_invoices)
            
            summary = {
                'total_invoices': len(invoice_data),
                'total_billed': total_billed,
                'total_paid': total_paid,
                'total_outstanding': total_outstanding,
                'collection_rate': (total_paid / total_billed * 100) if total_billed > 0 else 0,
                'overdue_count': len(overdue_invoices),
                'total_overdue': total_overdue,
                'average_days_to_payment': sum(inv['days_overdue'] for inv in invoice_data if inv['payment_status'] == 'paid') / len([inv for inv in invoice_data if inv['payment_status'] == 'paid']) if invoice_data else 0
            }
            
            return {
                'invoices': invoice_data,
                'summary': summary,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating invoice report: {e}")
            return {}
    
    def generate_client_payment_summary(self, client_filter: str = None) -> Dict:
        """Generate lifetime and monthly payment history per client"""
        try:
            from job_tracking_service import job_tracking_service
            
            jobs = job_tracking_service.get_job_records()
            payments = job_tracking_service.get_payment_logs()
            quotes = job_tracking_service.get_quote_history()
            
            client_data = {}
            
            # Aggregate data by client
            for job in jobs:
                client_name = job['client_name']
                if client_name not in client_data:
                    client_data[client_name] = {
                        'client_name': client_name,
                        'client_phone': job.get('client_phone', ''),
                        'client_email': job.get('client_email', ''),
                        'total_jobs': 0,
                        'total_billed': 0,
                        'total_paid': 0,
                        'outstanding_balance': 0,
                        'job_history': [],
                        'payment_history': []
                    }
                
                client_data[client_name]['total_jobs'] += 1
                client_data[client_name]['total_billed'] += job.get('estimated_cost', 0)
                client_data[client_name]['outstanding_balance'] += job.get('outstanding_balance', 0)
                
                client_data[client_name]['job_history'].append({
                    'job_id': job['job_id'],
                    'service_type': job['service_type'],
                    'date': job.get('created_at', ''),
                    'amount': job.get('estimated_cost', 0),
                    'status': job.get('status', '')
                })
            
            # Add payment data
            for payment in payments:
                client_name = payment['client_name']
                if client_name in client_data:
                    client_data[client_name]['total_paid'] += payment['payment_amount']
                    client_data[client_name]['payment_history'].append({
                        'date': payment['date_received'],
                        'amount': payment['payment_amount'],
                        'method': payment['payment_method'],
                        'job_id': payment.get('job_id', '')
                    })
            
            # Calculate additional metrics for each client
            for client_name, data in client_data.items():
                data['average_invoice_value'] = data['total_billed'] / data['total_jobs'] if data['total_jobs'] > 0 else 0
                data['payment_rate'] = (data['total_paid'] / data['total_billed'] * 100) if data['total_billed'] > 0 else 0
                data['lifetime_value'] = data['total_paid']
                
                # Calculate payment frequency
                if data['payment_history']:
                    payment_dates = [datetime.fromisoformat(p['date'].split('T')[0]) for p in data['payment_history']]
                    if len(payment_dates) > 1:
                        date_range = (max(payment_dates) - min(payment_dates)).days
                        data['payment_frequency_days'] = date_range / len(payment_dates) if len(payment_dates) > 0 else 0
                    else:
                        data['payment_frequency_days'] = 0
                else:
                    data['payment_frequency_days'] = 0
            
            # Filter by client if specified
            if client_filter:
                client_data = {k: v for k, v in client_data.items() if client_filter.lower() in k.lower()}
            
            # Sort by lifetime value (descending)
            sorted_clients = sorted(client_data.values(), key=lambda x: x['lifetime_value'], reverse=True)
            
            # Calculate summary statistics
            summary = {
                'total_clients': len(sorted_clients),
                'total_lifetime_value': sum(c['total_paid'] for c in sorted_clients),
                'average_client_value': sum(c['total_paid'] for c in sorted_clients) / len(sorted_clients) if sorted_clients else 0,
                'top_client': sorted_clients[0] if sorted_clients else None,
                'clients_with_outstanding': len([c for c in sorted_clients if c['outstanding_balance'] > 0]),
                'total_outstanding_all_clients': sum(c['outstanding_balance'] for c in sorted_clients)
            }
            
            return {
                'clients': sorted_clients,
                'summary': summary,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating client payment summary: {e}")
            return {}
    
    def generate_materials_report(self, date_range: tuple = None) -> Dict:
        """Generate materials and supplies cost/usage report"""
        try:
            from job_tracking_service import job_tracking_service
            
            materials = job_tracking_service._load_materials()
            
            # Filter by date range if specified
            if date_range:
                start_date, end_date = date_range
                start_dt = datetime.fromisoformat(start_date)
                end_dt = datetime.fromisoformat(end_date)
                
                materials = [
                    m for m in materials 
                    if start_dt <= datetime.fromisoformat(m['purchase_date'].split('T')[0]) <= end_dt
                ]
            
            # Aggregate by material type and supplier
            material_summary = {}
            supplier_summary = {}
            
            for material in materials:
                supplier = material.get('supplier_name', 'Unknown')
                
                if supplier not in supplier_summary:
                    supplier_summary[supplier] = {
                        'total_spent': 0,
                        'total_orders': 0,
                        'items_purchased': []
                    }
                
                supplier_summary[supplier]['total_spent'] += material['total_cost']
                supplier_summary[supplier]['total_orders'] += 1
                
                # Process individual items
                for item in material.get('items', []):
                    item_name = item.get('name', 'Unknown Item')
                    
                    if item_name not in material_summary:
                        material_summary[item_name] = {
                            'total_quantity': 0,
                            'total_cost': 0,
                            'average_unit_cost': 0,
                            'jobs_used': set(),
                            'suppliers': set(),
                            'purchase_history': []
                        }
                    
                    material_summary[item_name]['total_quantity'] += item.get('quantity', 0)
                    material_summary[item_name]['total_cost'] += item.get('total_cost', 0)
                    material_summary[item_name]['jobs_used'].add(material.get('job_id', ''))
                    material_summary[item_name]['suppliers'].add(supplier)
                    material_summary[item_name]['purchase_history'].append({
                        'date': material['purchase_date'],
                        'quantity': item.get('quantity', 0),
                        'unit_cost': item.get('unit_cost', 0),
                        'supplier': supplier,
                        'job_id': material.get('job_id', '')
                    })
                    
                    supplier_summary[supplier]['items_purchased'].append({
                        'item_name': item_name,
                        'quantity': item.get('quantity', 0),
                        'cost': item.get('total_cost', 0),
                        'job_id': material.get('job_id', '')
                    })
            
            # Calculate averages and convert sets to lists
            for item_name, data in material_summary.items():
                if data['total_quantity'] > 0:
                    data['average_unit_cost'] = data['total_cost'] / data['total_quantity']
                data['jobs_used'] = list(data['jobs_used'])
                data['suppliers'] = list(data['suppliers'])
                data['jobs_count'] = len(data['jobs_used'])
            
            # Sort materials by total cost (descending)
            sorted_materials = sorted(
                [(name, data) for name, data in material_summary.items()],
                key=lambda x: x[1]['total_cost'],
                reverse=True
            )
            
            # Sort suppliers by total spent (descending)
            sorted_suppliers = sorted(
                [(name, data) for name, data in supplier_summary.items()],
                key=lambda x: x[1]['total_spent'],
                reverse=True
            )
            
            # Calculate summary statistics
            total_material_cost = sum(m['total_cost'] for m in materials)
            total_orders = len(materials)
            average_order_value = total_material_cost / total_orders if total_orders > 0 else 0
            
            summary = {
                'total_material_cost': total_material_cost,
                'total_orders': total_orders,
                'average_order_value': average_order_value,
                'unique_materials': len(material_summary),
                'unique_suppliers': len(supplier_summary),
                'most_expensive_material': sorted_materials[0] if sorted_materials else None,
                'preferred_supplier': sorted_suppliers[0] if sorted_suppliers else None
            }
            
            return {
                'materials': dict(sorted_materials),
                'suppliers': dict(sorted_suppliers),
                'summary': summary,
                'raw_materials_data': materials,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating materials report: {e}")
            return {}
    
    def generate_tax_summary_report(self, tax_year: int = None) -> Dict:
        """Generate comprehensive tax summary for Hawaii GET and federal taxes"""
        try:
            from job_tracking_service import job_tracking_service
            
            if not tax_year:
                tax_year = datetime.now().year
            
            # Get all financial data for the tax year
            payments = job_tracking_service.get_payment_logs()
            materials = job_tracking_service._load_materials()
            labor = job_tracking_service._load_labor()
            
            # Filter by tax year
            year_payments = [
                p for p in payments 
                if datetime.fromisoformat(p['date_received'].split('T')[0]).year == tax_year
            ]
            
            year_materials = [
                m for m in materials 
                if datetime.fromisoformat(m['purchase_date'].split('T')[0]).year == tax_year
            ]
            
            year_labor = [
                l for l in labor 
                if datetime.fromisoformat(l['work_date']).year == tax_year
            ]
            
            # Calculate gross income
            gross_income = sum(p['payment_amount'] for p in year_payments)
            
            # Calculate Hawaii GET tax collected (embedded in gross income)
            hawaii_get_collected = gross_income * self.hawaii_get_rate / (1 + self.hawaii_get_rate)
            net_income_after_get = gross_income - hawaii_get_collected
            
            # Calculate deductible expenses
            material_expenses = sum(m['total_cost'] for m in year_materials)
            labor_expenses = sum(l['labor_cost'] + (l.get('overtime_hours', 0) * l.get('overtime_rate', 0)) 
                               for l in year_labor)
            
            # Only use actual tracked expenses - no estimates
            total_deductible_expenses = material_expenses + labor_expenses
            
            # Calculate taxable income
            taxable_income = net_income_after_get - total_deductible_expenses
            
            # Estimate federal and state taxes
            federal_tax_rate = 0.22  # Estimated federal tax rate
            hawaii_state_tax_rate = 0.085  # Hawaii state tax rate (approximate)
            
            estimated_federal_tax = max(0, taxable_income * federal_tax_rate)
            estimated_hawaii_tax = max(0, taxable_income * hawaii_state_tax_rate)
            
            # Calculate quarterly tax estimates
            quarterly_federal = estimated_federal_tax / 4
            quarterly_hawaii = estimated_hawaii_tax / 4
            quarterly_total = quarterly_federal + quarterly_hawaii
            
            # Calculate quarterly GET tax payments due
            quarterly_get_due = hawaii_get_collected / 4
            
            # Monthly breakdown
            monthly_breakdown = []
            for month in range(1, 13):
                month_payments = [
                    p for p in year_payments 
                    if datetime.fromisoformat(p['date_received'].split('T')[0]).month == month
                ]
                
                month_income = sum(p['payment_amount'] for p in month_payments)
                month_get = month_income * self.hawaii_get_rate / (1 + self.hawaii_get_rate)
                
                monthly_breakdown.append({
                    'month': calendar.month_name[month],
                    'month_number': month,
                    'gross_income': month_income,
                    'get_collected': month_get,
                    'net_income': month_income - month_get
                })
            
            return {
                'tax_year': tax_year,
                'income_summary': {
                    'gross_income': gross_income,
                    'hawaii_get_collected': hawaii_get_collected,
                    'net_income_after_get': net_income_after_get
                },
                'deductible_expenses': {
                    'materials': material_expenses,
                    'labor': labor_expenses,
                    'total_deductions': total_deductible_expenses
                },
                'taxable_income': taxable_income,
                'tax_estimates': {
                    'federal_tax': estimated_federal_tax,
                    'hawaii_state_tax': estimated_hawaii_tax,
                    'total_income_tax': estimated_federal_tax + estimated_hawaii_tax
                },
                'quarterly_estimates': {
                    'federal': quarterly_federal,
                    'hawaii_state': quarterly_hawaii,
                    'hawaii_get': quarterly_get_due,
                    'total_quarterly': quarterly_total + quarterly_get_due
                },
                'monthly_breakdown': monthly_breakdown,
                'tax_calendar': {
                    'q1_due': f"{tax_year}-04-15",
                    'q2_due': f"{tax_year}-06-15", 
                    'q3_due': f"{tax_year}-09-15",
                    'q4_due': f"{tax_year + 1}-01-15",
                    'annual_due': f"{tax_year + 1}-04-15"
                },
                'hawaii_get_info': {
                    'rate': self.hawaii_get_rate,
                    'filing_frequency': 'Monthly or Quarterly based on volume',
                    'annual_collected': hawaii_get_collected
                },
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating tax summary report: {e}")
            return {}

# Global instance
financial_reporting_service = FinancialReportingService()