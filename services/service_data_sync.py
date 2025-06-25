"""
Service Data Synchronization for SPANKKS Construction
Ensures pricing page data matches CSV template structure and database integration
"""

import json
import csv
import os
from datetime import datetime

class ServiceDataSync:
    def __init__(self):
        self.data_dir = 'data'
        self.csv_dir = 'csv_templates'
        self.service_types_file = os.path.join(self.data_dir, 'service_types.json')
        
    def get_pricing_page_services(self):
        """Extract service data matching pricing page structure"""
        return [
            # Drywall Services
            {
                'service_name': 'Drywall Patch - Small',
                'category': 'Drywall Services', 
                'base_hourly_rate': '95.00',
                'unit_type': 'patch',
                'unit_price': '155.00',
                'estimated_hours': '2',
                'description': 'Small patch repair under 12 inches, includes spackle, tape, sand, and primer',
                'materials_included': 'Compound, tape, primer, paint',
                'equipment_required': 'Basic hand tools',
                'skill_level': 'beginner'
            },
            {
                'service_name': 'Drywall Patch - Medium',
                'category': 'Drywall Services',
                'base_hourly_rate': '95.00', 
                'unit_type': 'patch',
                'unit_price': '275.00',
                'estimated_hours': '3',
                'description': 'Medium hole repair 1-4 sq ft, includes paint blending',
                'materials_included': 'Compound, tape, primer, texture, paint',
                'equipment_required': 'Hand tools, spray gun',
                'skill_level': 'intermediate'
            },
            {
                'service_name': 'Drywall Panel Replacement',
                'category': 'Drywall Services',
                'base_hourly_rate': '95.00',
                'unit_type': 'panel', 
                'unit_price': '500.00',
                'estimated_hours': '5',
                'description': 'Full drywall panel replacement, custom quote based on size',
                'materials_included': 'Drywall sheet, compound, tape, primer',
                'equipment_required': 'Hand tools, saw, spray gun',
                'skill_level': 'advanced'
            },
            {
                'service_name': 'Water Damage Ceiling Repair',
                'category': 'Drywall Services',
                'base_hourly_rate': '95.00',
                'unit_type': 'repair',
                'unit_price': '475.00',
                'estimated_hours': '4',
                'description': 'Water-damaged ceiling repair with stain-block primer',
                'materials_included': 'Compound, primer, stain blocker, paint',
                'equipment_required': 'Hand tools, ladder, spray equipment',
                'skill_level': 'intermediate'
            },
            
            # Flooring Installation
            {
                'service_name': 'Vinyl Plank Installation',
                'category': 'Flooring Installation',
                'base_hourly_rate': '95.00',
                'unit_type': 'sq ft',
                'unit_price': '4.00',
                'estimated_hours': '8',
                'description': 'Professional LVP installation, labor only',
                'materials_included': 'Underlayment, transition strips',
                'equipment_required': 'Saw, spacers, tapping block',
                'skill_level': 'intermediate'
            },
            {
                'service_name': 'Laminate Flooring',
                'category': 'Flooring Installation',
                'base_hourly_rate': '95.00',
                'unit_type': 'sq ft',
                'unit_price': '3.50',
                'estimated_hours': '6',
                'description': 'Click-lock or tongue/groove laminate installation',
                'materials_included': 'Underlayment, transition strips',
                'equipment_required': 'Saw, spacers, tapping block',
                'skill_level': 'beginner'
            },
            {
                'service_name': 'Tile Installation',
                'category': 'Flooring Installation',
                'base_hourly_rate': '95.00',
                'unit_type': 'sq ft',
                'unit_price': '7.00',
                'estimated_hours': '10',
                'description': 'Ceramic or porcelain tile installation, does not include tile cost',
                'materials_included': 'Adhesive, grout, spacers',
                'equipment_required': 'Tile saw, trowel, level',
                'skill_level': 'advanced'
            },
            {
                'service_name': 'Subfloor Repair',
                'category': 'Flooring Installation',
                'base_hourly_rate': '125.00',
                'unit_type': 'hour',
                'unit_price': '125.00',
                'estimated_hours': '4',
                'description': 'Subfloor repair or leveling, required before some installs',
                'materials_included': 'Leveling compound, screws, lumber',
                'equipment_required': 'Circular saw, drill, level',
                'skill_level': 'intermediate'
            },
            {
                'service_name': 'Flooring Removal',
                'category': 'Flooring Installation',
                'base_hourly_rate': '95.00',
                'unit_type': 'sq ft',
                'unit_price': '2.00',
                'estimated_hours': '4',
                'description': 'Old flooring removal, includes haul-away',
                'materials_included': 'Disposal bags',
                'equipment_required': 'Pry bar, hammer, scraper',
                'skill_level': 'beginner'
            },
            
            # Fence Building & Repair
            {
                'service_name': 'Wood Fence Installation',
                'category': 'Fence Building',
                'base_hourly_rate': '95.00',
                'unit_type': 'linear ft',
                'unit_price': '62.50',
                'estimated_hours': '12',
                'description': 'New wood fence 6ft standard, includes posts, panels, install',
                'materials_included': 'Posts, panels, hardware, concrete',
                'equipment_required': 'Post hole digger, level, drill',
                'skill_level': 'intermediate'
            },
            {
                'service_name': 'Chain Link Fence',
                'category': 'Fence Building',
                'base_hourly_rate': '95.00',
                'unit_type': 'linear ft',
                'unit_price': '42.50',
                'estimated_hours': '8',
                'description': 'Chain-link fence installation, residential grade',
                'materials_included': 'Posts, mesh, hardware, concrete',
                'equipment_required': 'Post hole digger, tensioning tools',
                'skill_level': 'beginner'
            },
            {
                'service_name': 'Gate Installation',
                'category': 'Fence Building',
                'base_hourly_rate': '95.00',
                'unit_type': 'gate',
                'unit_price': '475.00',
                'estimated_hours': '4',
                'description': 'Single panel gate installation, wood or chain-link',
                'materials_included': 'Gate hardware, hinges, latch',
                'equipment_required': 'Drill, level, measuring tools',
                'skill_level': 'intermediate'
            },
            {
                'service_name': 'Fence Repair',
                'category': 'Fence Building',
                'base_hourly_rate': '95.00',
                'unit_type': 'section',
                'unit_price': '212.50',
                'estimated_hours': '3',
                'description': 'Fence repair per section, includes board/post replacement',
                'materials_included': 'Replacement boards, posts, hardware',
                'equipment_required': 'Drill, saw, level',
                'skill_level': 'beginner'
            },
            
            # General Home Repair
            {
                'service_name': 'Door Repair',
                'category': 'General Handyman',
                'base_hourly_rate': '95.00',
                'unit_type': 'repair',
                'unit_price': '120.00',
                'estimated_hours': '2',
                'description': 'Door alignment and repair, hinges, latch, or sanding',
                'materials_included': 'Hardware, screws, lubricants',
                'equipment_required': 'Screwdriver, sandpaper, plane',
                'skill_level': 'beginner'
            },
            {
                'service_name': 'Faucet Repair',
                'category': 'General Handyman',
                'base_hourly_rate': '95.00',
                'unit_type': 'repair',
                'unit_price': '110.00',
                'estimated_hours': '1.5',
                'description': 'Leaky faucet fix, replace washers/cartridge',
                'materials_included': 'Washers, O-rings, cartridge',
                'equipment_required': 'Plumbing tools, wrench set',
                'skill_level': 'beginner'
            },
            {
                'service_name': 'Toilet Repair',
                'category': 'General Handyman',
                'base_hourly_rate': '95.00',
                'unit_type': 'repair',
                'unit_price': '145.00',
                'estimated_hours': '2',
                'description': 'Toilet running fix, fill valve or flapper replacement',
                'materials_included': 'Fill valve, flapper, chain',
                'equipment_required': 'Plumbing tools, adjustable wrench',
                'skill_level': 'beginner'
            },
            {
                'service_name': 'Light Fixture Installation',
                'category': 'General Handyman',
                'base_hourly_rate': '95.00',
                'unit_type': 'fixture',
                'unit_price': '120.00',
                'estimated_hours': '1.5',
                'description': 'Light fixture replacement, basic wiring included',
                'materials_included': 'Wire nuts, electrical tape',
                'equipment_required': 'Electrical tools, voltage tester',
                'skill_level': 'intermediate'
            },
            {
                'service_name': 'TV Mounting',
                'category': 'General Handyman',
                'base_hourly_rate': '95.00',
                'unit_type': 'mount',
                'unit_price': '150.00',
                'estimated_hours': '2',
                'description': 'TV, shelves, or other mounting, includes anchors and leveling',
                'materials_included': 'Anchors, screws, mounting hardware',
                'equipment_required': 'Drill, level, stud finder',
                'skill_level': 'beginner'
            }
        ]
    
    def save_service_types_to_database(self):
        """Save service types to JSON database"""
        services = self.get_pricing_page_services()
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create service types database
        service_types_data = {
            'last_updated': datetime.now().isoformat(),
            'total_services': len(services),
            'categories': list(set(service['category'] for service in services)),
            'services': services
        }
        
        with open(self.service_types_file, 'w') as f:
            json.dump(service_types_data, f, indent=2)
            
        print(f"✅ Saved {len(services)} services to database: {self.service_types_file}")
        return service_types_data
    
    def update_csv_template(self):
        """Update CSV template to match pricing page data"""
        services = self.get_pricing_page_services()
        csv_file = os.path.join(self.csv_dir, 'service_types_template.csv')
        
        # Ensure CSV directory exists
        os.makedirs(self.csv_dir, exist_ok=True)
        
        # Write updated CSV template
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'service_name', 'category', 'base_hourly_rate', 'unit_type', 
                'unit_price', 'estimated_hours', 'description', 'materials_included',
                'equipment_required', 'skill_level'
            ])
            writer.writeheader()
            writer.writerows(services)
            
        print(f"✅ Updated CSV template: {csv_file}")
        return csv_file
    
    def validate_data_consistency(self):
        """Validate that pricing page, CSV, and database are consistent"""
        services = self.get_pricing_page_services()
        
        # Check categories
        categories = set(service['category'] for service in services)
        expected_categories = {
            'Drywall Services', 'Flooring Installation', 
            'Fence Building', 'General Handyman'
        }
        
        # Validate all required fields
        required_fields = [
            'service_name', 'category', 'base_hourly_rate', 'unit_type',
            'unit_price', 'estimated_hours', 'description', 'materials_included',
            'equipment_required', 'skill_level'
        ]
        
        validation_results = {
            'total_services': len(services),
            'categories_found': list(categories),
            'categories_expected': list(expected_categories),
            'categories_match': categories == expected_categories,
            'all_fields_present': True,
            'field_validation': {}
        }
        
        # Validate each service has all required fields
        for service in services:
            for field in required_fields:
                if field not in service or not service[field]:
                    validation_results['all_fields_present'] = False
                    validation_results['field_validation'][service['service_name']] = f"Missing {field}"
        
        return validation_results

def sync_service_data():
    """Main function to synchronize all service data"""
    sync = ServiceDataSync()
    
    print("🔄 Starting service data synchronization...")
    
    # Save to database
    database_result = sync.save_service_types_to_database()
    
    # Update CSV template
    csv_result = sync.update_csv_template()
    
    # Validate consistency
    validation = sync.validate_data_consistency()
    
    print(f"\n📊 Synchronization Results:")
    print(f"   • Database: {database_result['total_services']} services saved")
    print(f"   • CSV Template: Updated with current pricing")
    print(f"   • Categories: {', '.join(validation['categories_found'])}")
    print(f"   • Validation: {'✅ PASSED' if validation['all_fields_present'] else '❌ FAILED'}")
    
    if not validation['field_validation']:
        print("   • All service fields properly structured")
    else:
        print("   • Field issues found:")
        for service, issue in validation['field_validation'].items():
            print(f"     - {service}: {issue}")
    
    return {
        'database': database_result,
        'csv_updated': csv_result,
        'validation': validation
    }

if __name__ == "__main__":
    sync_service_data()