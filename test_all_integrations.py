#!/usr/bin/env python3
"""
Comprehensive test script for all SPANKKS Construction integrations
Tests contact forms, Twilio SMS, photo uploads, and API endpoints
"""

import requests
import json
import os
import tempfile
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:5000"

class IntegrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = {
            'contact_form': None,
            'consultation_form': None,
            'photo_upload': None,
            'quote_api': None,
            'invoice_api': None,
            'twilio_status': None
        }
    
    def test_contact_form(self):
        """Test contact form submission and inquiry alerts"""
        logger.info("Testing contact form submission...")
        
        contact_data = {
            'name': 'John Test',
            'email': 'john.test@example.com',
            'phone': '(808) 555-0123',
            'subject': 'Testing Contact Form',
            'message': 'This is a test message for contact form integration.'
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/contact", data=contact_data)
            
            if response.status_code in [200, 302]:  # Success or redirect
                logger.info("✅ Contact form submission successful")
                self.results['contact_form'] = 'PASS'
            else:
                logger.error(f"❌ Contact form failed: {response.status_code}")
                self.results['contact_form'] = f'FAIL - {response.status_code}'
                
        except Exception as e:
            logger.error(f"❌ Contact form error: {e}")
            self.results['contact_form'] = f'ERROR - {e}'
    
    def test_consultation_form(self):
        """Test consultation booking form"""
        logger.info("Testing consultation form submission...")
        
        consultation_data = {
            'name': 'Jane Test',
            'email': 'jane.test@example.com',
            'phone': '(808) 555-0456',
            'service': 'Drywall Repair',
            'preferred_date': '2025-06-25',
            'preferred_time': '10:00 AM',
            'location': '123 Test St, Honolulu, HI',
            'description': 'Testing consultation booking system'
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/consultation", data=consultation_data)
            
            if response.status_code in [200, 302]:
                logger.info("✅ Consultation form submission successful")
                self.results['consultation_form'] = 'PASS'
            else:
                logger.error(f"❌ Consultation form failed: {response.status_code}")
                self.results['consultation_form'] = f'FAIL - {response.status_code}'
                
        except Exception as e:
            logger.error(f"❌ Consultation form error: {e}")
            self.results['consultation_form'] = f'ERROR - {e}'
    
    def create_test_image(self):
        """Create a test image for photo upload"""
        img = Image.new('RGB', (800, 600), color='blue')
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        img.save(temp_file.name, 'JPEG')
        temp_file.close()
        
        return temp_file.name
    
    def test_photo_upload(self):
        """Test job photo upload system"""
        logger.info("Testing photo upload system...")
        
        job_id = "TEST123"
        test_image_path = self.create_test_image()
        
        try:
            # Test before photos upload
            with open(test_image_path, 'rb') as img_file:
                files = {'photos': ('test_before.jpg', img_file, 'image/jpeg')}
                response = self.session.post(f"{BASE_URL}/upload/{job_id}/before", files=files)
            
            if response.status_code == 201:
                logger.info("✅ Photo upload successful")
                self.results['photo_upload'] = 'PASS'
                
                # Test photo retrieval
                photo_response = self.session.get(f"{BASE_URL}/photos/{job_id}")
                if photo_response.status_code == 200:
                    logger.info("✅ Photo retrieval successful")
                else:
                    logger.warning(f"⚠️ Photo retrieval failed: {photo_response.status_code}")
            else:
                logger.error(f"❌ Photo upload failed: {response.status_code}")
                self.results['photo_upload'] = f'FAIL - {response.status_code}'
                
        except Exception as e:
            logger.error(f"❌ Photo upload error: {e}")
            self.results['photo_upload'] = f'ERROR - {e}'
        finally:
            # Cleanup
            if os.path.exists(test_image_path):
                os.unlink(test_image_path)
    
    def test_quote_api(self):
        """Test multi-line quote generation API"""
        logger.info("Testing quote generation API...")
        
        quote_data = {
            "clientId": "TEST001",
            "jobId": "JOB_TEST", 
            "customer": "API Test Customer",
            "customer_phone": "(808) 555-0789",
            "job_location": "456 API Test St, Honolulu, HI",
            "employee_name": "Test Representative",
            "quote_days": 30,
            "items": [
                {
                    "description": "API Test - Drywall repair",
                    "unit_price": 100.00,
                    "quantity": 1,
                    "line_total": 100.00
                },
                {
                    "description": "API Test - Paint application",
                    "unit_price": 75.00,
                    "quantity": 1,
                    "line_total": 75.00
                }
            ],
            "total_sub": 175.00,
            "total_discount": 0.00,
            "total_tax": 8.25,
            "total": 183.25
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/generate-quote",
                headers={"Content-Type": "application/json"},
                json=quote_data
            )
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"✅ Quote API successful - Quote ID: {result.get('quoteId')}")
                self.results['quote_api'] = f"PASS - {result.get('quoteId')}"
            else:
                logger.error(f"❌ Quote API failed: {response.status_code}")
                self.results['quote_api'] = f'FAIL - {response.status_code}'
                
        except Exception as e:
            logger.error(f"❌ Quote API error: {e}")
            self.results['quote_api'] = f'ERROR - {e}'
    
    def test_invoice_api(self):
        """Test invoice generation API"""
        logger.info("Testing invoice generation API...")
        
        invoice_data = {
            "clientId": "TEST002",
            "jobId": "INV_TEST",
            "customer": "Invoice Test Customer",
            "total": 250.00
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/generate-invoice",
                headers={"Content-Type": "application/json"},
                json=invoice_data
            )
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"✅ Invoice API successful - Invoice ID: {result.get('invoiceId')}")
                self.results['invoice_api'] = f"PASS - {result.get('invoiceId')}"
            else:
                logger.error(f"❌ Invoice API failed: {response.status_code}")
                self.results['invoice_api'] = f'FAIL - {response.status_code}'
                
        except Exception as e:
            logger.error(f"❌ Invoice API error: {e}")
            self.results['invoice_api'] = f'ERROR - {e}'
    
    def test_twilio_status(self):
        """Test Twilio configuration status"""
        logger.info("Testing Twilio integration status...")
        
        try:
            response = self.session.get(f"{BASE_URL}/twilio-status")
            
            if response.status_code == 200:
                result = response.json()
                twilio_status = result.get('twilio_configured', False)
                sendgrid_status = result.get('sendgrid_configured', False)
                
                if twilio_status and sendgrid_status:
                    logger.info("✅ Twilio and SendGrid fully configured")
                    self.results['twilio_status'] = 'PASS - Full Integration'
                elif twilio_status:
                    logger.info("⚠️ Twilio configured, SendGrid needs setup")
                    self.results['twilio_status'] = 'PARTIAL - Twilio Only'
                else:
                    logger.warning("⚠️ Twilio/SendGrid need configuration")
                    self.results['twilio_status'] = 'NEEDS CONFIG'
            else:
                logger.error(f"❌ Twilio status check failed: {response.status_code}")
                self.results['twilio_status'] = f'FAIL - {response.status_code}'
                
        except Exception as e:
            logger.error(f"❌ Twilio status error: {e}")
            self.results['twilio_status'] = f'ERROR - {e}'
    
    def run_all_tests(self):
        """Run all integration tests"""
        logger.info("🚀 Starting SPANKKS Construction Integration Tests")
        logger.info("=" * 60)
        
        # Test all components
        self.test_contact_form()
        self.test_consultation_form()
        self.test_photo_upload()
        self.test_quote_api()
        self.test_invoice_api()
        self.test_twilio_status()
        
        # Print results
        logger.info("\n" + "=" * 60)
        logger.info("🎯 INTEGRATION TEST RESULTS")
        logger.info("=" * 60)
        
        for test_name, result in self.results.items():
            status_icon = "✅" if result and result.startswith('PASS') else "❌"
            logger.info(f"{status_icon} {test_name.replace('_', ' ').title()}: {result}")
        
        # Summary
        passed_tests = sum(1 for result in self.results.values() 
                         if result and result.startswith('PASS'))
        total_tests = len(self.results)
        
        logger.info("=" * 60)
        logger.info(f"📊 SUMMARY: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 All integrations working correctly!")
        else:
            logger.warning("⚠️ Some integrations need attention")
        
        return self.results

def main():
    """Main test function"""
    tester = IntegrationTester()
    results = tester.run_all_tests()
    
    # Check if any critical systems failed
    critical_systems = ['contact_form', 'quote_api', 'invoice_api']
    critical_failures = [name for name in critical_systems 
                        if not results.get(name, '').startswith('PASS')]
    
    if critical_failures:
        logger.error(f"🚨 Critical system failures detected: {critical_failures}")
        return 1
    else:
        logger.info("✅ All critical systems operational")
        return 0

if __name__ == "__main__":
    exit(main())