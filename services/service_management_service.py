"""
Service Management Service for SPANKKS Construction
Handles service catalog, pricing, categories, and bulk operations
"""

import json
import logging
import csv
import io
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import os

class ServiceManagementService:
    """Professional service management system"""
    
    def __init__(self):
        self.db_url = os.environ.get('DATABASE_URL')
        
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
    
    def get_all_services(self, active_only: bool = False) -> List[Dict]:
        """Get all services from database"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT id, name, category, description, base_price, unit, active, 
                               created_at, updated_at
                        FROM services
                    """
                    if active_only:
                        query += " WHERE active = true"
                    query += " ORDER BY category, name"
                    
                    cursor.execute(query)
                    return [dict(service) for service in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting services: {e}")
            return []
    
    def get_service_categories(self) -> List[Dict]:
        """Get unique service categories with counts"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT category, COUNT(*) as service_count,
                               COUNT(CASE WHEN active = true THEN 1 END) as active_count
                        FROM services
                        GROUP BY category
                        ORDER BY category
                    """)
                    return [dict(cat) for cat in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting service categories: {e}")
            return []
    
    def get_service_by_id(self, service_id: int) -> Optional[Dict]:
        """Get service by ID"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, name, category, description, base_price, unit, active
                        FROM services
                        WHERE id = %s
                    """, (service_id,))
                    
                    result = cursor.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            logging.error(f"Error getting service by ID: {e}")
            return None
    
    def create_service(self, data: Dict) -> Dict[str, Any]:
        """Create new service"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO services (name, category, description, base_price, unit, active)
                        VALUES (%(name)s, %(category)s, %(description)s, %(base_price)s, %(unit)s, %(active)s)
                        RETURNING id
                    """, {
                        'name': data['name'],
                        'category': data['category'],
                        'description': data.get('description', ''),
                        'base_price': float(data['base_price']),
                        'unit': data.get('unit', 'flat'),
                        'active': data.get('active', True)
                    })
                    
                    service_id = cursor.fetchone()['id']
                    conn.commit()
                    
                    return {
                        'success': True,
                        'service_id': service_id,
                        'message': 'Service created successfully'
                    }
        except Exception as e:
            logging.error(f"Error creating service: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def update_service(self, service_id: int, data: Dict) -> Dict[str, Any]:
        """Update existing service"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE services 
                        SET name = %(name)s, category = %(category)s, description = %(description)s,
                            base_price = %(base_price)s, unit = %(unit)s, active = %(active)s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %(id)s
                    """, {
                        'id': service_id,
                        'name': data['name'],
                        'category': data['category'],
                        'description': data.get('description', ''),
                        'base_price': float(data['base_price']),
                        'unit': data.get('unit', 'flat'),
                        'active': data.get('active', True)
                    })
                    
                    conn.commit()
                    
                    return {
                        'success': True,
                        'message': 'Service updated successfully'
                    }
        except Exception as e:
            logging.error(f"Error updating service: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def delete_service(self, service_id: int) -> Dict[str, Any]:
        """Delete service (soft delete by setting active=false)"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE services 
                        SET active = false, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (service_id,))
                    
                    conn.commit()
                    
                    return {
                        'success': True,
                        'message': 'Service deactivated successfully'
                    }
        except Exception as e:
            logging.error(f"Error deleting service: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def bulk_import_services(self, csv_data: str) -> Dict[str, Any]:
        """Import services from CSV data"""
        try:
            # Parse CSV
            csv_file = io.StringIO(csv_data)
            reader = csv.DictReader(csv_file)
            
            # Validate required fields
            required_fields = ['name', 'category', 'base_price', 'unit']
            fieldnames = reader.fieldnames or []
            
            missing_fields = [field for field in required_fields if field not in fieldnames]
            if missing_fields:
                return {
                    'success': False,
                    'message': f'Missing required CSV headers: {", ".join(missing_fields)}'
                }
            
            # Process data
            services_to_import = []
            errors = []
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 because of header
                try:
                    # Validate and clean data
                    service = {
                        'name': row['name'].strip(),
                        'category': row['category'].strip(),
                        'description': row.get('description', '').strip(),
                        'base_price': float(row['base_price']),
                        'unit': row.get('unit', 'flat').strip(),
                        'active': row.get('active', 'true').lower() in ['true', '1', 'yes']
                    }
                    
                    # Validate unit
                    valid_units = ['sqft', 'hour', 'flat', 'linear_ft', 'each']
                    if service['unit'] not in valid_units:
                        errors.append(f"Row {row_num}: Invalid unit '{service['unit']}'. Must be one of: {', '.join(valid_units)}")
                        continue
                    
                    services_to_import.append(service)
                    
                except ValueError as e:
                    errors.append(f"Row {row_num}: Invalid price format - {str(e)}")
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            if errors:
                return {
                    'success': False,
                    'message': 'CSV validation failed',
                    'errors': errors
                }
            
            # Import to database
            imported_count = 0
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    for service in services_to_import:
                        try:
                            cursor.execute("""
                                INSERT INTO services (name, category, description, base_price, unit, active)
                                VALUES (%(name)s, %(category)s, %(description)s, %(base_price)s, %(unit)s, %(active)s)
                            """, service)
                            imported_count += 1
                        except Exception as e:
                            logging.error(f"Error importing service {service['name']}: {e}")
                    
                    conn.commit()
            
            return {
                'success': True,
                'message': f'Successfully imported {imported_count} services',
                'imported_count': imported_count
            }
            
        except Exception as e:
            logging.error(f"Error importing services: {e}")
            return {
                'success': False,
                'message': f'Import failed: {str(e)}'
            }
    
    def export_services_csv(self) -> str:
        """Export all services to CSV format"""
        try:
            services = self.get_all_services()
            
            output = io.StringIO()
            fieldnames = ['name', 'category', 'description', 'base_price', 'unit', 'active']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            
            writer.writeheader()
            for service in services:
                writer.writerow({
                    'name': service['name'],
                    'category': service['category'],
                    'description': service['description'] or '',
                    'base_price': str(service['base_price']),
                    'unit': service['unit'],
                    'active': 'true' if service['active'] else 'false'
                })
            
            return output.getvalue()
            
        except Exception as e:
            logging.error(f"Error exporting services: {e}")
            return ""
    
    def get_service_statistics(self) -> Dict[str, Any]:
        """Get service statistics"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_services,
                            COUNT(CASE WHEN active = true THEN 1 END) as active_services,
                            COUNT(DISTINCT category) as total_categories,
                            AVG(base_price) as avg_price
                        FROM services
                    """)
                    
                    stats = cursor.fetchone()
                    return {
                        'total_services': stats['total_services'],
                        'active_services': stats['active_services'],
                        'total_categories': stats['total_categories'],
                        'avg_price': float(stats['avg_price']) if stats['avg_price'] else 0
                    }
        except Exception as e:
            logging.error(f"Error getting service statistics: {e}")
            return {
                'total_services': 0,
                'active_services': 0,
                'total_categories': 0,
                'avg_price': 0
            }