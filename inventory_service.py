"""
Inventory Management Service for SPANKKS Construction
Handles inventory tracking, materials usage, and automatic deductions
"""

import json
import os
from datetime import datetime
import pytz
from models import get_hawaii_time

class InventoryService:
    """Comprehensive inventory management system"""
    
    def __init__(self):
        self.inventory_file = 'data/inventory.json'
        self.job_materials_file = 'data/job_materials.json'
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Ensure inventory data files exist"""
        if not os.path.exists('data'):
            os.makedirs('data')
            
        if not os.path.exists(self.inventory_file):
            with open(self.inventory_file, 'w') as f:
                json.dump([], f, indent=2)
                
        if not os.path.exists(self.job_materials_file):
            with open(self.job_materials_file, 'w') as f:
                json.dump([], f, indent=2)
    
    def get_all_inventory(self):
        """Get all inventory items"""
        try:
            with open(self.inventory_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def add_inventory_item(self, item_data):
        """Add new inventory item"""
        inventory = self.get_all_inventory()
        
        # Generate unique item ID
        item_id = f"INV{str(len(inventory) + 1).zfill(3)}"
        
        new_item = {
            'item_id': item_id,
            'name': item_data['name'],
            'category': item_data.get('category', 'General'),
            'description': item_data.get('description', ''),
            'unit': item_data.get('unit', 'each'),
            'current_stock': int(item_data.get('current_stock', 0)),
            'minimum_stock': int(item_data.get('minimum_stock', 5)),
            'unit_cost': float(item_data.get('unit_cost', 0.0)),
            'supplier': item_data.get('supplier', ''),
            'location': item_data.get('location', 'Main Storage'),
            'created_date': get_hawaii_time().isoformat(),
            'last_updated': get_hawaii_time().isoformat(),
            'status': 'active'
        }
        
        inventory.append(new_item)
        
        with open(self.inventory_file, 'w') as f:
            json.dump(inventory, f, indent=2)
            
        return new_item
    
    def update_inventory_item(self, item_id, updates):
        """Update inventory item"""
        inventory = self.get_all_inventory()
        
        for item in inventory:
            if item['item_id'] == item_id:
                item.update(updates)
                item['last_updated'] = get_hawaii_time().isoformat()
                break
        
        with open(self.inventory_file, 'w') as f:
            json.dump(inventory, f, indent=2)
            
        return True
    
    def get_low_stock_items(self):
        """Get items with stock below minimum threshold"""
        inventory = self.get_all_inventory()
        return [item for item in inventory 
                if item['current_stock'] <= item['minimum_stock'] 
                and item['status'] == 'active']
    
    def log_material_usage(self, job_id, materials_used):
        """Log materials used for a specific job"""
        job_materials = self.get_job_materials()
        
        # Create material usage record
        usage_record = {
            'usage_id': f"MAT{len(job_materials) + 1:05d}",
            'job_id': job_id,
            'materials': materials_used,
            'logged_date': get_hawaii_time().isoformat(),
            'total_cost': 0.0,
            'status': 'logged'
        }
        
        inventory = self.get_all_inventory()
        total_cost = 0.0
        
        # Process each material and update inventory
        for material in materials_used:
            material_name = material['name']
            quantity_used = int(material['quantity'])
            
            # Find matching inventory item
            for inv_item in inventory:
                if inv_item['name'].lower() == material_name.lower():
                    # Calculate cost
                    material_cost = quantity_used * inv_item['unit_cost']
                    total_cost += material_cost
                    
                    # Update material record with cost info
                    material['unit_cost'] = inv_item['unit_cost']
                    material['total_cost'] = material_cost
                    material['inventory_id'] = inv_item['item_id']
                    
                    # Deduct from inventory
                    inv_item['current_stock'] = max(0, inv_item['current_stock'] - quantity_used)
                    inv_item['last_updated'] = get_hawaii_time().isoformat()
                    break
            else:
                # Material not found in inventory - mark as manual entry
                material['unit_cost'] = 0.0
                material['total_cost'] = 0.0
                material['inventory_id'] = None
                material['note'] = 'Not found in inventory - manual entry'
        
        usage_record['total_cost'] = total_cost
        job_materials.append(usage_record)
        
        # Save updates
        with open(self.job_materials_file, 'w') as f:
            json.dump(job_materials, f, indent=2)
            
        with open(self.inventory_file, 'w') as f:
            json.dump(inventory, f, indent=2)
            
        return usage_record
    
    def get_job_materials(self):
        """Get all job materials records"""
        try:
            with open(self.job_materials_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def get_materials_by_job(self, job_id):
        """Get materials used for specific job"""
        job_materials = self.get_job_materials()
        return [record for record in job_materials if record['job_id'] == job_id]
    
    def get_inventory_summary(self):
        """Get inventory summary statistics"""
        inventory = self.get_all_inventory()
        
        if not inventory:
            return {
                'total_items': 0,
                'total_value': 0.0,
                'low_stock_count': 0,
                'categories': {},
                'status_counts': {}
            }
        
        total_value = sum(item['current_stock'] * item['unit_cost'] for item in inventory)
        low_stock_items = self.get_low_stock_items()
        
        # Category breakdown
        categories = {}
        for item in inventory:
            cat = item['category']
            if cat not in categories:
                categories[cat] = {'count': 0, 'value': 0.0}
            categories[cat]['count'] += 1
            categories[cat]['value'] += item['current_stock'] * item['unit_cost']
        
        # Status breakdown
        status_counts = {}
        for item in inventory:
            status = item['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_items': len(inventory),
            'total_value': round(total_value, 2),
            'low_stock_count': len(low_stock_items),
            'categories': categories,
            'status_counts': status_counts,
            'low_stock_items': low_stock_items
        }
    
    def search_inventory(self, query):
        """Search inventory by name or description"""
        inventory = self.get_all_inventory()
        query_lower = query.lower()
        
        return [item for item in inventory 
                if query_lower in item['name'].lower() 
                or query_lower in item['description'].lower()
                or query_lower in item['category'].lower()]
    
    def get_job_cost_analysis(self, job_id):
        """Get detailed cost analysis for a job"""
        materials_records = self.get_materials_by_job(job_id)
        
        if not materials_records:
            return {
                'total_material_cost': 0.0,
                'materials_count': 0,
                'cost_breakdown': [],
                'profitability_notes': 'No materials logged for this job'
            }
        
        total_cost = sum(record['total_cost'] for record in materials_records)
        all_materials = []
        
        for record in materials_records:
            all_materials.extend(record['materials'])
        
        # Group by material type
        material_summary = {}
        for material in all_materials:
            name = material['name']
            if name not in material_summary:
                material_summary[name] = {
                    'total_quantity': 0,
                    'total_cost': 0.0,
                    'unit_cost': material.get('unit_cost', 0.0)
                }
            material_summary[name]['total_quantity'] += int(material['quantity'])
            material_summary[name]['total_cost'] += material.get('total_cost', 0.0)
        
        cost_breakdown = [
            {
                'material': name,
                'quantity': data['total_quantity'],
                'unit_cost': data['unit_cost'],
                'total_cost': data['total_cost']
            }
            for name, data in material_summary.items()
        ]
        
        return {
            'total_material_cost': round(total_cost, 2),
            'materials_count': len(all_materials),
            'cost_breakdown': cost_breakdown,
            'usage_records': materials_records
        }

# Global inventory service instance
inventory_service = InventoryService()