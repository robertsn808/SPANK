#!/usr/bin/env python3
"""
Test script for API endpoints - demonstrating external integration capabilities
Tests the /api/generate-quote and /api/download-quote endpoints
"""

import requests
import json
import sys
import os
from datetime import datetime

def test_quote_generation_api():
    """Test the quote generation API endpoint"""
    print("Testing Quote Generation API")
    print("=" * 40)
    
    # Base URL for the application
    base_url = "http://localhost:5000"  # Adjust if running on different port
    
    # Test data matching the Node.js example
    test_cases = [
        {
            "name": "Drywall Repair Test",
            "data": {
                "clientId": "CLIENT001",
                "jobId": "JOB123",
                "customer": "John Smith",
                "phone": "(808) 555-0123",
                "serviceType": "Drywall Repair",
                "price": 275
            }
        },
        {
            "name": "Flooring Installation Test",
            "data": {
                "clientId": "CLIENT002", 
                "jobId": "JOB124",
                "customer": "Maria Garcia",
                "phone": "(808) 555-0124",
                "serviceType": "Flooring Installation",
                "price": 1250
            }
        },
        {
            "name": "Fence Repair Test",
            "data": {
                "clientId": "CLIENT003",
                "jobId": "JOB125", 
                "customer": "David Kim",
                "phone": "(808) 555-0125",
                "serviceType": "Fence Repair",
                "price": 650
            }
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n📋 Running: {test_case['name']}")
        
        try:
            # Send POST request to generate quote
            response = requests.post(
                f"{base_url}/api/generate-quote",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 201:
                result_data = response.json()
                print(f"✅ Quote generated successfully:")
                print(f"   Quote ID: {result_data['quoteId']}")
                print(f"   Customer: {result_data['customer']}")
                print(f"   Service: {result_data['serviceType']}")
                print(f"   Price: ${result_data['price']:.2f}")
                print(f"   Total (with tax): ${result_data['total']:.2f}")
                print(f"   Download URL: {result_data['downloadUrl']}")
                print(f"   View URL: {result_data['viewUrl']}")
                
                # Test PDF download
                quote_id = result_data['quoteId']
                download_response = requests.get(f"{base_url}/api/download-quote/{quote_id}")
                
                if download_response.status_code == 200:
                    print(f"✅ PDF download successful ({len(download_response.content)} bytes)")
                else:
                    print(f"❌ PDF download failed: {download_response.status_code}")
                
                results.append({
                    'test': test_case['name'],
                    'status': 'success',
                    'quote_id': quote_id,
                    'data': result_data
                })
                
            else:
                print(f"❌ Quote generation failed: {response.status_code}")
                print(f"   Error: {response.text}")
                results.append({
                    'test': test_case['name'],
                    'status': 'failed',
                    'error': response.text
                })
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            results.append({
                'test': test_case['name'],
                'status': 'error',
                'error': str(e)
            })
    
    return results

def test_form_data_submission():
    """Test API with form data instead of JSON"""
    print("\n🔄 Testing Form Data Submission")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    form_data = {
        "clientId": "FORM001",
        "jobId": "FORM123",
        "customer": "Sarah Johnson", 
        "phone": "(808) 555-0199",
        "serviceType": "General Repair",
        "price": "450"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/generate-quote",
            data=form_data,
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Form submission successful:")
            print(f"   Quote ID: {result['quoteId']}")
            print(f"   Customer: {result['customer']}")
            print(f"   Total: ${result['total']:.2f}")
            return True
        else:
            print(f"❌ Form submission failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def display_integration_examples():
    """Display examples for external integration"""
    print("\n🔧 Integration Examples")
    print("=" * 40)
    
    # JavaScript/Node.js example
    js_example = """
// JavaScript/Node.js Integration Example
const generateQuote = async (quoteData) => {
    try {
        const response = await fetch('http://your-domain.com/api/generate-quote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                clientId: quoteData.clientId,
                jobId: quoteData.jobId,
                customer: quoteData.customer,
                phone: quoteData.phone,
                serviceType: quoteData.serviceType,
                price: quoteData.price
            })
        });
        
        const result = await response.json();
        console.log('Quote generated:', result.quoteId);
        return result;
    } catch (error) {
        console.error('Error generating quote:', error);
    }
};
"""
    
    # cURL example
    curl_example = """
# cURL Integration Example
curl -X POST http://your-domain.com/api/generate-quote \\
  -H "Content-Type: application/json" \\
  -d '{
    "clientId": "CLIENT001",
    "jobId": "JOB123",
    "customer": "John Doe",
    "phone": "(808) 555-0123",
    "serviceType": "Drywall Repair",
    "price": 275
  }'
"""
    
    # Python example
    python_example = """
# Python Integration Example
import requests

def create_spankks_quote(customer, phone, service, price, job_id=None):
    url = "http://your-domain.com/api/generate-quote"
    data = {
        "customer": customer,
        "phone": phone,
        "serviceType": service,
        "price": price,
        "jobId": job_id
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Quote generation failed: {response.text}")
"""
    
    print("JavaScript/Node.js:")
    print(js_example)
    print("\ncURL:")
    print(curl_example)
    print("\nPython:")
    print(python_example)

def main():
    """Main test function"""
    print("🏗️ SPANKKS Construction - API Integration Test")
    print("Testing external integration capabilities")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Test quote generation API
    results = test_quote_generation_api()
    
    # Test form data submission
    form_success = test_form_data_submission()
    
    # Display summary
    print("\n📊 Test Summary")
    print("=" * 40)
    
    successful_tests = [r for r in results if r['status'] == 'success']
    failed_tests = [r for r in results if r['status'] != 'success']
    
    print(f"✅ Successful API tests: {len(successful_tests)}")
    print(f"❌ Failed API tests: {len(failed_tests)}")
    print(f"🔄 Form data test: {'✅ Passed' if form_success else '❌ Failed'}")
    
    if successful_tests:
        print(f"\n📋 Generated Quotes:")
        for test in successful_tests:
            print(f"   • {test['quote_id']} - {test['test']}")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"   • {test['test']}: {test.get('error', 'Unknown error')}")
    
    # Display integration examples
    display_integration_examples()
    
    print(f"\n🎯 API Endpoints Available:")
    print(f"   POST /api/generate-quote - Generate professional quotes")
    print(f"   GET  /api/download-quote/<id> - Download quote PDFs")
    print(f"\n💼 Integration Notes:")
    print(f"   • Supports both JSON and form data")
    print(f"   • Automatically creates contacts if they don't exist")
    print(f"   • Generates professional PDFs with SPANKKS branding")
    print(f"   • Sends SMS notifications to admin (808) 452-9779")
    print(f"   • Includes Hawaii GET tax calculations")
    
    return len(failed_tests) == 0 and form_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)