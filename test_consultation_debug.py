#!/usr/bin/env python3
"""
Debug script to test consultation form submission and identify the exact error source
"""

import requests
import json

def test_consultation_form():
    """Test consultation form submission with detailed error tracking"""
    
    url = "https://55aaf5ec-c5b6-4121-a14c-1212e14193ca-00-3buax92jvgag1.riker.replit.dev/consultation"
    
    # Test data
    form_data = {
        'name': 'Debug Test Client',
        'email': 'debug@test.com',
        'phone': '808-555-9999',
        'service': 'Consultation',
        'project_type': 'Kitchen',
        'consultation_type': 'Phone',
        'preferred_date': '2025-06-25',
        'preferred_time': '10:00',
        'message': 'Debug test message',
        'square_footage': '200'
    }
    
    try:
        print("Testing consultation form submission...")
        print(f"URL: {url}")
        print(f"Data: {form_data}")
        
        response = requests.post(url, data=form_data, allow_redirects=False)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print(f"Redirect Location: {response.headers.get('Location', 'No location header')}")
            print("SUCCESS: Form submitted successfully with redirect")
        elif response.status_code == 200:
            print("Form returned 200 - checking for error messages")
            if "error" in response.text.lower():
                print("ERROR: Found error message in response")
            else:
                print("Form returned HTML content without redirect")
        else:
            print(f"UNEXPECTED: Status code {response.status_code}")
        
        return response.status_code == 302
        
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    success = test_consultation_form()
    print(f"\nTest Result: {'PASS' if success else 'FAIL'}")