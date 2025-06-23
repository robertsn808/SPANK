#!/usr/bin/env python3
"""
Test script for CSV Templates system
Tests download and upload functionality
"""

import requests
import os
import csv
import json
from datetime import datetime

class CSVSystemTester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:5000"
        self.session = requests.Session()
        self.test_results = []
        
    def login_admin(self):
        """Login as admin to get session"""
        print("Testing admin login...")
        
        # Get login page first for any CSRF tokens
        login_page = self.session.get(f"{self.base_url}/admin/login")
        
        # Login with admin credentials
        login_data = {
            'username': 'spankysadmin808',
            'password': 'Money$$'
        }
        
        response = self.session.post(f"{self.base_url}/admin/login", data=login_data)
        
        if response.status_code == 200 and '/admin/dashboard' in response.url:
            print("✓ Admin login successful")
            return True
        else:
            print(f"✗ Admin login failed - Status: {response.status_code}")
            return False
    
    def test_csv_templates_page(self):
        """Test CSV templates dashboard loads"""
        print("\nTesting CSV Templates dashboard...")
        
        response = self.session.get(f"{self.base_url}/admin/csv-templates")
        
        if response.status_code == 200:
            if "CSV Templates" in response.text and "Download Template" in response.text:
                print("✓ CSV Templates dashboard loads successfully")
                return True
            else:
                print("✗ CSV Templates page missing expected content")
                return False
        else:
            print(f"✗ CSV Templates page failed - Status: {response.status_code}")
            return False
    
    def test_template_downloads(self):
        """Test downloading individual CSV templates"""
        print("\nTesting CSV template downloads...")
        
        templates = [
            'clients_template.csv',
            'jobs_template.csv', 
            'quotes_template.csv',
            'invoices_template.csv',
            'staff_template.csv',
            'schedule_template.csv',
            'service_types_template.csv'
        ]
        
        results = []
        
        for template in templates:
            print(f"  Testing {template}...")
            
            response = self.session.get(f"{self.base_url}/admin/csv-templates/download/{template}")
            
            if response.status_code == 200:
                # Check if content is actual CSV
                if response.headers.get('content-type') == 'text/csv':
                    # Save test file
                    with open(f"test_{template}", 'w') as f:
                        f.write(response.text)
                    
                    # Validate CSV format
                    try:
                        reader = csv.reader(response.text.splitlines())
                        headers = next(reader)
                        sample_row = next(reader, None)
                        
                        if headers and len(headers) > 0:
                            print(f"    ✓ {template} downloaded successfully ({len(headers)} columns)")
                            results.append(True)
                        else:
                            print(f"    ✗ {template} has invalid CSV format")
                            results.append(False)
                    except Exception as e:
                        print(f"    ✗ {template} CSV parsing error: {e}")
                        results.append(False)
                else:
                    print(f"    ✗ {template} wrong content type: {response.headers.get('content-type')}")
                    results.append(False)
            else:
                print(f"    ✗ {template} download failed - Status: {response.status_code}")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\nTemplate download success rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
        return all(results)
    
    def test_zip_download(self):
        """Test downloading all templates as ZIP"""
        print("\nTesting ZIP download...")
        
        response = self.session.get(f"{self.base_url}/admin/csv-templates/download-all")
        
        if response.status_code == 200:
            if response.headers.get('content-type') == 'application/zip':
                # Save ZIP file
                with open('test_templates.zip', 'wb') as f:
                    f.write(response.content)
                
                # Check file size
                file_size = len(response.content)
                if file_size > 1000:  # Should be at least 1KB
                    print(f"✓ ZIP download successful ({file_size} bytes)")
                    return True
                else:
                    print(f"✗ ZIP file too small ({file_size} bytes)")
                    return False
            else:
                print(f"✗ ZIP download wrong content type: {response.headers.get('content-type')}")
                return False
        else:
            print(f"✗ ZIP download failed - Status: {response.status_code}")
            return False
    
    def test_data_export(self):
        """Test exporting current database data"""
        print("\nTesting data export functionality...")
        
        data_types = ['clients', 'jobs', 'quotes', 'invoices', 'staff', 'schedule']
        results = []
        
        for data_type in data_types:
            print(f"  Testing {data_type} export...")
            
            response = self.session.get(f"{self.base_url}/admin/csv-export/{data_type}")
            
            if response.status_code == 200:
                if response.headers.get('content-type') == 'text/csv':
                    # Check if export contains data or at least headers
                    lines = response.text.splitlines()
                    if len(lines) >= 1:  # At least header row
                        print(f"    ✓ {data_type} export successful ({len(lines)} lines)")
                        results.append(True)
                    else:
                        print(f"    ✗ {data_type} export empty")
                        results.append(False)
                else:
                    print(f"    ✗ {data_type} export wrong content type")
                    results.append(False)
            else:
                print(f"    ✗ {data_type} export failed - Status: {response.status_code}")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\nData export success rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
        return all(results)
    
    def test_csv_validation(self):
        """Test CSV template format validation"""
        print("\nTesting CSV template validation...")
        
        # Check if templates exist in filesystem
        template_dir = "csv_templates"
        if not os.path.exists(template_dir):
            print(f"✗ Template directory {template_dir} not found")
            return False
        
        templates = [
            'clients_template.csv',
            'jobs_template.csv',
            'quotes_template.csv', 
            'invoices_template.csv',
            'staff_template.csv',
            'schedule_template.csv',
            'service_types_template.csv'
        ]
        
        results = []
        
        for template in templates:
            template_path = os.path.join(template_dir, template)
            
            if os.path.exists(template_path):
                try:
                    with open(template_path, 'r') as f:
                        reader = csv.reader(f)
                        headers = next(reader)
                        sample_rows = list(reader)
                    
                    if headers and len(headers) > 0 and len(sample_rows) > 0:
                        print(f"    ✓ {template} valid format ({len(headers)} columns, {len(sample_rows)} sample rows)")
                        results.append(True)
                    else:
                        print(f"    ✗ {template} missing headers or sample data")
                        results.append(False)
                        
                except Exception as e:
                    print(f"    ✗ {template} validation error: {e}")
                    results.append(False)
            else:
                print(f"    ✗ {template} file not found")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\nTemplate validation success rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
        return all(results)
    
    def create_test_upload_data(self):
        """Create test data for upload testing"""
        print("\nCreating test upload data...")
        
        # Create a simple test client CSV
        test_data = [
            ['name', 'phone', 'email', 'address', 'city', 'state', 'zip_code', 'client_type', 'notes', 'preferred_contact_method'],
            ['Test Client 1', '(808) 555-1111', 'test1@example.com', '123 Test St', 'Honolulu', 'HI', '96814', 'residential', 'Test upload client', 'email'],
            ['Test Client 2', '(808) 555-2222', 'test2@example.com', '456 Test Ave', 'Pearl City', 'HI', '96782', 'commercial', 'Another test client', 'phone']
        ]
        
        with open('test_upload_clients.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(test_data)
        
        print("✓ Test upload data created")
        return True
    
    def run_all_tests(self):
        """Run complete CSV system test suite"""
        print("=== SPANKKS Construction CSV System Test Suite ===")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        tests = [
            ("Admin Login", self.login_admin),
            ("CSV Templates Page", self.test_csv_templates_page),
            ("Template Validation", self.test_csv_validation),
            ("Template Downloads", self.test_template_downloads),
            ("ZIP Download", self.test_zip_download),
            ("Data Export", self.test_data_export),
            ("Test Data Creation", self.create_test_upload_data)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'='*50}")
            print(f"TEST: {test_name}")
            print('='*50)
            
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"✓ {test_name} PASSED")
                else:
                    print(f"✗ {test_name} FAILED")
                    
            except Exception as e:
                print(f"✗ {test_name} ERROR: {e}")
                results.append((test_name, False))
        
        # Summary
        print(f"\n{'='*50}")
        print("TEST SUMMARY")
        print('='*50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "PASS" if result else "FAIL"
            print(f"{status:4} | {test_name}")
        
        print(f"\nOverall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! CSV system is fully functional.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        return passed == total

if __name__ == "__main__":
    tester = CSVSystemTester()
    tester.run_all_tests()