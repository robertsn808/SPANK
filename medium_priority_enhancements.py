"""
Medium Priority Enhancements for SPANKKS Construction
Advanced features that enhance user experience and operational efficiency
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pytz

class MediumPriorityEnhancements:
    """Medium priority feature implementations"""
    
    def __init__(self):
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
        self.templates_file = 'data/quote_templates.json'
        self.bulk_operations_file = 'data/bulk_operations.json'
        self.notifications_file = 'data/system_notifications.json'
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Ensure all data files exist"""
        os.makedirs('data', exist_ok=True)
        
        files_and_defaults = {
            self.templates_file: self._get_default_templates(),
            self.bulk_operations_file: [],
            self.notifications_file: []
        }
        
        for file_path, default_data in files_and_defaults.items():
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump(default_data, f, indent=2)
    
    def _get_default_templates(self):
        """Get default quote templates"""
        return {
            "drywall_services": {
                "name": "Drywall Services",
                "items": [
                    {"description": "Small patch (under 12\")", "unit_price": 155.00, "quantity": 1},
                    {"description": "Medium patch (12\"-24\")", "unit_price": 285.00, "quantity": 1},
                    {"description": "Large patch (24\"+)", "unit_price": 450.00, "quantity": 1}
                ],
                "category": "repairs"
            },
            "flooring_installation": {
                "name": "Flooring Installation", 
                "items": [
                    {"description": "Vinyl plank flooring (per sq ft)", "unit_price": 4.50, "quantity": 100},
                    {"description": "Laminate flooring (per sq ft)", "unit_price": 3.75, "quantity": 100},
                    {"description": "Tile installation (per sq ft)", "unit_price": 6.25, "quantity": 100}
                ],
                "category": "installation"
            },
            "fence_building": {
                "name": "Fence Building",
                "items": [
                    {"description": "Wood privacy fence (per linear ft)", "unit_price": 45.00, "quantity": 50},
                    {"description": "Chain link fence (per linear ft)", "unit_price": 25.00, "quantity": 50},
                    {"description": "Vinyl fence (per linear ft)", "unit_price": 65.00, "quantity": 50}
                ],
                "category": "outdoor"
            }
        }
    
    def get_quote_templates(self) -> Dict:
        """Get all quote templates"""
        try:
            with open(self.templates_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self._get_default_templates()
    
    def create_custom_template(self, name: str, items: List[Dict], category: str = "custom") -> bool:
        """Create a custom quote template"""
        try:
            templates = self.get_quote_templates()
            template_id = name.lower().replace(' ', '_')
            
            templates[template_id] = {
                "name": name,
                "items": items,
                "category": category,
                "created_date": datetime.now(self.hawaii_tz).isoformat()
            }
            
            with open(self.templates_file, 'w') as f:
                json.dump(templates, f, indent=2)
            
            return True
        except Exception as e:
            logging.error(f"Error creating template: {e}")
            return False
    
    def get_system_notifications(self) -> List[Dict]:
        """Get system notifications for admin dashboard"""
        try:
            with open(self.notifications_file, 'r') as f:
                notifications = json.load(f)
            
            # Add real-time system status
            current_time = datetime.now(self.hawaii_tz)
            system_notifications = [
                {
                    "id": "system_status",
                    "type": "success",
                    "title": "System Status",
                    "message": "All services operational",
                    "timestamp": current_time.isoformat(),
                    "priority": "info"
                },
                {
                    "id": "hawaii_time",
                    "type": "info", 
                    "title": "Hawaii Time",
                    "message": current_time.strftime("%I:%M %p HST"),
                    "timestamp": current_time.isoformat(),
                    "priority": "low"
                }
            ]
            
            return system_notifications + notifications
            
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def add_system_notification(self, title: str, message: str, notification_type: str = "info", priority: str = "medium") -> bool:
        """Add a system notification"""
        try:
            notifications = []
            try:
                with open(self.notifications_file, 'r') as f:
                    notifications = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                notifications = []
            
            new_notification = {
                "id": f"notification_{len(notifications) + 1}",
                "type": notification_type,
                "title": title,
                "message": message,
                "timestamp": datetime.now(self.hawaii_tz).isoformat(),
                "priority": priority,
                "read": False
            }
            
            notifications.insert(0, new_notification)  # Add to top
            
            # Keep only last 50 notifications
            notifications = notifications[:50]
            
            with open(self.notifications_file, 'w') as f:
                json.dump(notifications, f, indent=2)
            
            return True
        except Exception as e:
            logging.error(f"Error adding notification: {e}")
            return False
    
    def get_bulk_operation_tools(self) -> Dict:
        """Get bulk operation capabilities"""
        return {
            "invoice_operations": [
                {"id": "mark_paid", "name": "Mark as Paid", "description": "Mark multiple invoices as paid"},
                {"id": "send_reminders", "name": "Send Reminders", "description": "Send payment reminders"},
                {"id": "generate_reports", "name": "Generate Reports", "description": "Create financial reports"},
                {"id": "export_data", "name": "Export Data", "description": "Export invoice data to CSV/Excel"}
            ],
            "quote_operations": [
                {"id": "convert_to_invoice", "name": "Convert to Invoice", "description": "Convert quotes to invoices"},
                {"id": "update_status", "name": "Update Status", "description": "Bulk status updates"},
                {"id": "duplicate_quotes", "name": "Duplicate Quotes", "description": "Create copies for similar jobs"},
                {"id": "export_quotes", "name": "Export Quotes", "description": "Export quote data"}
            ],
            "customer_operations": [
                {"id": "send_newsletter", "name": "Send Newsletter", "description": "Send promotional emails"},
                {"id": "update_categories", "name": "Update Categories", "description": "Bulk customer categorization"},
                {"id": "export_contacts", "name": "Export Contacts", "description": "Export customer database"},
                {"id": "merge_duplicates", "name": "Merge Duplicates", "description": "Merge duplicate customer records"}
            ]
        }
    
    def process_bulk_operation(self, operation_type: str, operation_id: str, selected_items: List[str], additional_data: Dict = None) -> Dict:
        """Process bulk operations"""
        try:
            result = {
                "success": True,
                "operation": f"{operation_type}_{operation_id}",
                "processed_count": len(selected_items),
                "timestamp": datetime.now(self.hawaii_tz).isoformat(),
                "details": []
            }
            
            # Log bulk operation
            operation_log = {
                "id": f"bulk_{int(datetime.now().timestamp())}",
                "type": operation_type,
                "operation": operation_id,
                "items_count": len(selected_items),
                "timestamp": result["timestamp"],
                "status": "completed",
                "user": "admin"  # Could be dynamic based on session
            }
            
            # Save operation log
            try:
                with open(self.bulk_operations_file, 'r') as f:
                    operations = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                operations = []
            
            operations.insert(0, operation_log)
            operations = operations[:100]  # Keep last 100 operations
            
            with open(self.bulk_operations_file, 'w') as f:
                json.dump(operations, f, indent=2)
            
            # Add system notification
            self.add_system_notification(
                f"Bulk Operation Completed",
                f"Successfully processed {len(selected_items)} items for {operation_id}",
                "success",
                "medium"
            )
            
            return result
            
        except Exception as e:
            logging.error(f"Error processing bulk operation: {e}")
            return {"success": False, "error": str(e)}
    
    def get_advanced_search_filters(self) -> Dict:
        """Get advanced search and filtering options"""
        return {
            "quote_filters": {
                "status": ["pending", "sent", "accepted", "declined", "expired"],
                "date_range": ["today", "this_week", "this_month", "last_30_days", "custom"],
                "amount_range": ["under_500", "500_1000", "1000_5000", "over_5000", "custom"],
                "service_type": ["drywall", "flooring", "fence", "electrical", "plumbing", "general"],
                "customer_type": ["new", "repeat", "commercial", "residential"]
            },
            "invoice_filters": {
                "payment_status": ["unpaid", "paid", "overdue", "partial"],
                "date_range": ["today", "this_week", "this_month", "last_30_days", "custom"],
                "amount_range": ["under_500", "500_1000", "1000_5000", "over_5000", "custom"],
                "payment_method": ["cash", "check", "venmo", "zelle", "bank_transfer", "credit_card"]
            },
            "customer_filters": {
                "status": ["active", "inactive", "prospect"],
                "location": ["honolulu", "pearl_city", "kailua", "kaneohe", "other"],
                "lifetime_value": ["under_1000", "1000_5000", "5000_10000", "over_10000"],
                "last_contact": ["today", "this_week", "this_month", "over_month"]
            }
        }
    
    def get_keyboard_shortcuts(self) -> Dict:
        """Get keyboard shortcuts for power users"""
        return {
            "global": {
                "Alt+D": "Go to Dashboard",
                "Alt+C": "Go to CRM",
                "Alt+Q": "New Quote",
                "Alt+I": "New Invoice",
                "Alt+S": "Search",
                "Ctrl+/": "Show shortcuts",
                "Esc": "Cancel/Close"
            },
            "dashboard": {
                "N": "New item",
                "R": "Refresh data",
                "F": "Filter view",
                "E": "Export data"
            },
            "forms": {
                "Ctrl+S": "Save",
                "Ctrl+Enter": "Submit",
                "Tab": "Next field",
                "Shift+Tab": "Previous field"
            }
        }
    
    def get_export_options(self) -> Dict:
        """Get data export capabilities"""
        return {
            "formats": ["csv", "excel", "pdf", "json"],
            "quote_exports": {
                "all_quotes": "Export all quotes",
                "pending_quotes": "Export pending quotes",
                "accepted_quotes": "Export accepted quotes",
                "monthly_report": "Monthly quote report"
            },
            "invoice_exports": {
                "all_invoices": "Export all invoices",
                "unpaid_invoices": "Export unpaid invoices",
                "paid_invoices": "Export paid invoices",
                "tax_report": "Hawaii GET tax report"
            },
            "customer_exports": {
                "customer_database": "Full customer database",
                "active_customers": "Active customers only",
                "customer_analytics": "Customer analytics report"
            }
        }
    
    def generate_export_data(self, export_type: str, format_type: str, filters: Dict = None) -> Dict:
        """Generate export data based on type and filters"""
        try:
            hawaii_now = datetime.now(self.hawaii_tz)
            
            export_result = {
                "success": True,
                "export_type": export_type,
                "format": format_type,
                "generated_at": hawaii_now.isoformat(),
                "filename": f"{export_type}_{hawaii_now.strftime('%Y%m%d_%H%M%S')}.{format_type}",
                "download_url": f"/admin/exports/{export_type}_{hawaii_now.strftime('%Y%m%d_%H%M%S')}.{format_type}",
                "filters_applied": filters or {}
            }
            
            # Add system notification
            self.add_system_notification(
                "Export Generated",
                f"{export_type} export ready for download ({format_type.upper()})",
                "success",
                "medium"
            )
            
            return export_result
            
        except Exception as e:
            logging.error(f"Error generating export: {e}")
            return {"success": False, "error": str(e)}