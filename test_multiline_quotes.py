#!/usr/bin/env python3
"""
Test script for multi-line quote generation API
Tests the enhanced /api/generate-quote endpoint with req.body.items[] array structure
"""

import requests
import json

# Base URL for testing
BASE_URL = "http://localhost:5000"

def test_multiline_quote_generation():
    """Test multi-line quote generation with itemized descriptions"""
    
    # Test data matching the frontend form structure
    test_data = {
        "clientId": "CLIENT001",
        "jobId": "JOB001", 
        "customer": "John Smith",
        "customer_phone": "(808) 555-0123",
        "job_location": "123 Main St, Honolulu, HI 96815",
        "employee_name": "Mike Johnson",
        "quote_days": 30,
        "date": "2025-06-22",
        "items": [
            {
                "description": "Drywall repair - living room wall (8x10 area)",
                "unit_price": 200.00,
                "quantity": 1,
                "line_total": 200.00
            },
            {
                "description": "Paint - 2 coats premium paint",
                "unit_price": 150.00,
                "quantity": 1, 
                "line_total": 150.00
            },
            {
                "description": "Texture matching and priming",
                "unit_price": 100.00,
                "quantity": 1,
                "line_total": 100.00
            }
        ],
        "total_sub": 450.00,
        "total_discount": 50.00,
        "total_tax": 18.85,  # Hawaii GET tax 4.712%
        "total": 418.85
    }
    
    print("🧪 Testing Multi-Line Quote Generation")
    print("=" * 50)
    print(f"📋 Items: {len(test_data['items'])} line items")
    print(f"💰 Subtotal: ${test_data['total_sub']:.2f}")
    print(f"🎯 Total: ${test_data['total']:.2f}")
    print()
    
    try:
        # Send request to API
        response = requests.post(
            f"{BASE_URL}/api/generate-quote",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        print(f"📡 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Quote Generation Successful!")
            print(f"📄 Quote ID: {result.get('quoteId')}")
            print(f"👤 Customer: {result.get('customer')}")
            print(f"💵 Total: ${result.get('total', 0):.2f}")
            print(f"📥 Download URL: {result.get('downloadUrl')}")
            print(f"🔗 View URL: {result.get('viewUrl')}")
            
            # Test PDF download
            if result.get('downloadUrl'):
                pdf_response = requests.get(f"{BASE_URL}{result['downloadUrl']}")
                if pdf_response.status_code == 200:
                    print(f"📁 PDF Size: {len(pdf_response.content)} bytes")
                    print("✅ PDF Download Successful!")
                else:
                    print(f"❌ PDF Download Failed: {pdf_response.status_code}")
            
        else:
            print(f"❌ Quote Generation Failed")
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"🚫 Network Error: {e}")
    except Exception as e:
        print(f"💥 Unexpected Error: {e}")

def test_legacy_quote_compatibility():
    """Test backward compatibility with legacy single-item quotes"""
    
    legacy_data = {
        "clientId": "LEGACY001",
        "jobId": "LEGACY_JOB",
        "customer": "Jane Doe",
        "phone": "(808) 123-4567",
        "serviceType": "Drywall Repair",
        "price": 500.00
    }
    
    print("\n🔄 Testing Legacy Quote Compatibility")
    print("=" * 50)
    print(f"🏠 Service: {legacy_data['serviceType']}")
    print(f"💰 Price: ${legacy_data['price']:.2f}")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate-quote",
            headers={"Content-Type": "application/json"},
            json=legacy_data,
            timeout=30
        )
        
        print(f"📡 Legacy API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Legacy Quote Generation Successful!")
            print(f"📄 Quote ID: {result.get('quoteId')}")
            print(f"💵 Total: ${result.get('total', 0):.2f}")
            
        else:
            print(f"❌ Legacy Quote Generation Failed")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"💥 Legacy Test Error: {e}")

def main():
    """Main test function"""
    print("🚀 SPANKKS Multi-Line Quote API Testing")
    print("=" * 60)
    
    # Test new multi-line functionality
    test_multiline_quote_generation()
    
    # Test backward compatibility  
    test_legacy_quote_compatibility()
    
    print("\n🎯 Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()