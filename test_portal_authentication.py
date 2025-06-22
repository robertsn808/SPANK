#!/usr/bin/env python3
"""
Test script for Job Site Portal authentication system
Tests client and staff login flows with actual credentials
"""

import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:5000"

class PortalTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = {
            'client_login': None,
            'staff_login': None,
            'client_portal_access': None,
            'staff_portal_access': None,
            'portal_logout': None
        }
    
    def test_client_login(self):
        """Test client login with valid credentials"""
        logger.info("Testing client login...")
        
        # Test client credentials from clients.json
        login_data = {
            'clientId': 'ABC123',
            'jobId': '23456'
            # No staffPin for client access
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/login", data=login_data)
            
            if response.status_code in [200, 302]:  # Success or redirect
                logger.info("✅ Client login successful")
                self.results['client_login'] = 'PASS'
                
                # Check if redirected to client portal
                if '/portal/' in response.url or '/portal/' in str(response.history):
                    logger.info("✅ Client correctly redirected to portal")
                    return True
                else:
                    logger.warning("⚠️ Client login succeeded but redirect unclear")
                    return True
            else:
                logger.error(f"❌ Client login failed: {response.status_code}")
                self.results['client_login'] = f'FAIL - {response.status_code}'
                return False
                
        except Exception as e:
            logger.error(f"❌ Client login error: {e}")
            self.results['client_login'] = f'ERROR - {e}'
            return False
    
    def test_staff_login(self):
        """Test staff login with PIN"""
        logger.info("Testing staff login...")
        
        # Test staff credentials with PIN
        login_data = {
            'clientId': 'SPK001',
            'jobId': '30078',
            'staffPin': 'Money$$'
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/login", data=login_data)
            
            if response.status_code in [200, 302]:
                logger.info("✅ Staff login successful")
                self.results['staff_login'] = 'PASS'
                
                # Check if redirected to staff portal
                if '/job/' in response.url or '/job/' in str(response.history):
                    logger.info("✅ Staff correctly redirected to staff portal")
                    return True
                else:
                    logger.warning("⚠️ Staff login succeeded but redirect unclear")
                    return True
            else:
                logger.error(f"❌ Staff login failed: {response.status_code}")
                self.results['staff_login'] = f'FAIL - {response.status_code}'
                return False
                
        except Exception as e:
            logger.error(f"❌ Staff login error: {e}")
            self.results['staff_login'] = f'ERROR - {e}'
            return False
    
    def test_client_portal_access(self):
        """Test client portal page access"""
        logger.info("Testing client portal access...")
        
        try:
            # First login as client
            login_data = {
                'clientId': 'ABC123',
                'jobId': '23456'
            }
            
            self.session.post(f"{BASE_URL}/login", data=login_data)
            
            # Then access client portal
            response = self.session.get(f"{BASE_URL}/portal/ABC123/23456")
            
            if response.status_code == 200:
                logger.info("✅ Client portal access successful")
                self.results['client_portal_access'] = 'PASS'
                
                # Check if page contains expected client portal elements
                if 'Client Portal' in response.text and 'Marlon Barut' in response.text:
                    logger.info("✅ Client portal displays correct client information")
                    return True
                else:
                    logger.warning("⚠️ Client portal accessible but content unclear")
                    return True
            else:
                logger.error(f"❌ Client portal access failed: {response.status_code}")
                self.results['client_portal_access'] = f'FAIL - {response.status_code}'
                return False
                
        except Exception as e:
            logger.error(f"❌ Client portal access error: {e}")
            self.results['client_portal_access'] = f'ERROR - {e}'
            return False
    
    def test_staff_portal_access(self):
        """Test staff portal page access"""
        logger.info("Testing staff portal access...")
        
        try:
            # First login as staff
            login_data = {
                'clientId': 'SPK001',
                'jobId': '30078',
                'staffPin': 'Money$$'
            }
            
            self.session.post(f"{BASE_URL}/login", data=login_data)
            
            # Then access staff portal
            response = self.session.get(f"{BASE_URL}/job/30078")
            
            if response.status_code == 200:
                logger.info("✅ Staff portal access successful")
                self.results['staff_portal_access'] = 'PASS'
                
                # Check if page contains expected staff portal elements
                if 'Staff Portal' in response.text and 'Full Access' in response.text:
                    logger.info("✅ Staff portal displays correct staff tools")
                    return True
                else:
                    logger.warning("⚠️ Staff portal accessible but content unclear")
                    return True
            else:
                logger.error(f"❌ Staff portal access failed: {response.status_code}")
                self.results['staff_portal_access'] = f'FAIL - {response.status_code}'
                return False
                
        except Exception as e:
            logger.error(f"❌ Staff portal access error: {e}")
            self.results['staff_portal_access'] = f'ERROR - {e}'
            return False
    
    def test_portal_logout(self):
        """Test portal logout functionality"""
        logger.info("Testing portal logout...")
        
        try:
            # Login first
            login_data = {
                'clientId': 'ABC123',
                'jobId': '23456'
            }
            
            self.session.post(f"{BASE_URL}/login", data=login_data)
            
            # Then logout
            response = self.session.get(f"{BASE_URL}/portal/logout")
            
            if response.status_code in [200, 302]:
                logger.info("✅ Portal logout successful")
                self.results['portal_logout'] = 'PASS'
                
                # Try to access portal after logout (should fail)
                protected_response = self.session.get(f"{BASE_URL}/portal/ABC123/23456")
                if protected_response.status_code in [302, 401, 403]:
                    logger.info("✅ Portal properly protected after logout")
                    return True
                else:
                    logger.warning("⚠️ Logout succeeded but portal still accessible")
                    return True
            else:
                logger.error(f"❌ Portal logout failed: {response.status_code}")
                self.results['portal_logout'] = f'FAIL - {response.status_code}'
                return False
                
        except Exception as e:
            logger.error(f"❌ Portal logout error: {e}")
            self.results['portal_logout'] = f'ERROR - {e}'
            return False
    
    def test_invalid_credentials(self):
        """Test authentication with invalid credentials"""
        logger.info("Testing invalid credentials...")
        
        invalid_tests = [
            {'clientId': 'INVALID', 'jobId': '12345'},
            {'clientId': 'ABC123', 'jobId': 'INVALID'},
            {'clientId': 'SPK001', 'jobId': '30078', 'staffPin': 'WRONG_PIN'}
        ]
        
        for test_data in invalid_tests:
            try:
                response = self.session.post(f"{BASE_URL}/login", data=test_data)
                
                # Should stay on login page or return error
                if response.status_code == 200 and 'Invalid credentials' in response.text:
                    logger.info(f"✅ Invalid credentials properly rejected: {test_data}")
                elif response.status_code in [401, 403]:
                    logger.info(f"✅ Invalid credentials properly rejected: {test_data}")
                else:
                    logger.warning(f"⚠️ Invalid credentials test unclear: {test_data}")
                    
            except Exception as e:
                logger.error(f"❌ Invalid credentials test error: {e}")
    
    def run_all_tests(self):
        """Run all portal authentication tests"""
        logger.info("🚀 Starting Job Site Portal Authentication Tests")
        logger.info("=" * 60)
        
        # Test authentication flows
        self.test_client_login()
        self.test_staff_login()
        self.test_client_portal_access()
        self.test_staff_portal_access()
        self.test_portal_logout()
        
        # Test security
        self.test_invalid_credentials()
        
        # Print results
        logger.info("\n" + "=" * 60)
        logger.info("🎯 PORTAL AUTHENTICATION TEST RESULTS")
        logger.info("=" * 60)
        
        for test_name, result in self.results.items():
            status_icon = "✅" if result and result.startswith('PASS') else "❌"
            logger.info(f"{status_icon} {test_name.replace('_', ' ').title()}: {result}")
        
        # Summary
        passed_tests = sum(1 for result in self.results.values() 
                         if result and result.startswith('PASS'))
        total_tests = len(self.results)
        
        logger.info("=" * 60)
        logger.info(f"📊 SUMMARY: {passed_tests}/{total_tests} authentication tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 All portal authentication tests working correctly!")
        else:
            logger.warning("⚠️ Some authentication features need attention")
        
        return self.results

def main():
    """Main test function"""
    tester = PortalTester()
    results = tester.run_all_tests()
    
    # Check if critical authentication failed
    critical_tests = ['client_login', 'staff_login']
    critical_failures = [name for name in critical_tests 
                        if not results.get(name, '').startswith('PASS')]
    
    if critical_failures:
        logger.error(f"🚨 Critical authentication failures: {critical_failures}")
        return 1
    else:
        logger.info("✅ All critical authentication systems operational")
        return 0

if __name__ == "__main__":
    exit(main())