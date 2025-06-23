#!/usr/bin/env python3
"""
Quick Actions Endpoint Verification Script
Tests all Quick Actions button endpoints to ensure they're working
"""

import requests
import json

# Quick Actions endpoints to test
ENDPOINTS = [
    '/admin/quote-builder',
    '/admin/staff', 
    '/admin/inventory',
    '/admin/checklists',
    '/admin/analytics-dashboard',
    '/admin/business-intelligence',
    '/admin/ml-insights',
    '/admin/integrated-analytics',
    '/admin/scheduler/unified',
    '/admin/scheduler/advanced'
]

BASE_URL = 'http://localhost:5000'

def test_endpoint(endpoint):
    """Test a single endpoint and return status"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", allow_redirects=False)
        status = response.status_code
        
        # 302 redirect to login is expected for admin routes
        if status == 302 and '/admin/login' in response.headers.get('Location', ''):
            return 'PROTECTED (redirects to login)'
        elif status == 200:
            return 'OK'
        elif status == 404:
            return 'NOT FOUND'
        else:
            return f'ERROR ({status})'
    except Exception as e:
        return f'FAILED ({str(e)})'

def main():
    """Test all Quick Actions endpoints"""
    print("Quick Actions Endpoint Verification")
    print("=" * 50)
    
    results = {}
    for endpoint in ENDPOINTS:
        status = test_endpoint(endpoint)
        results[endpoint] = status
        print(f"{endpoint:<30} {status}")
    
    print("\n" + "=" * 50)
    
    # Summary
    protected_count = sum(1 for status in results.values() if 'PROTECTED' in status)
    ok_count = sum(1 for status in results.values() if status == 'OK')
    not_found_count = sum(1 for status in results.values() if status == 'NOT FOUND')
    error_count = sum(1 for status in results.values() if 'ERROR' in status or 'FAILED' in status)
    
    print(f"Summary:")
    print(f"  Protected (Auth Required): {protected_count}")
    print(f"  OK (Public): {ok_count}")
    print(f"  Not Found: {not_found_count}")
    print(f"  Errors: {error_count}")
    
    if not_found_count > 0:
        print(f"\nMissing routes that need to be created:")
        for endpoint, status in results.items():
            if status == 'NOT FOUND':
                print(f"  {endpoint}")

if __name__ == '__main__':
    main()