#!/usr/bin/env python3
"""
Test script for inquiry alert system
Verify that (808) 452-9779 receives SMS alerts for new inquiries
"""

import logging
from notification_service import NotificationService

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_inquiry_alerts():
    """Test inquiry alert system for new customer inquiries"""
    
    print("🔔 Testing Inquiry Alert System for SPANK Handyman Services")
    print("=" * 60)
    
    # Initialize notification service
    service = NotificationService()
    
    print(f"✅ Admin alert phone: +18084529779")
    print(f"✅ Twilio phone: {service.twilio_phone}")
    print(f"✅ Twilio configured: {bool(service.twilio_client)}")
    
    # Test contact inquiry alert
    print("\n📞 Testing contact inquiry alert...")
    contact_result = service.send_inquiry_alert(
        inquiry_type="contact",
        customer_name="John Doe",
        phone_number="+18085551234",
        email="john.doe@example.com"
    )
    
    if contact_result:
        print("✅ Contact inquiry alert sent successfully")
    else:
        print("❌ Contact inquiry alert failed")
    
    # Test consultation inquiry alert
    print("\n🏗️ Testing consultation inquiry alert...")
    consultation_result = service.send_inquiry_alert(
        inquiry_type="consultation",
        customer_name="Jane Smith",
        phone_number="+18085555678",
        email="jane.smith@example.com",
        service_type="Kitchen Renovation"
    )
    
    if consultation_result:
        print("✅ Consultation inquiry alert sent successfully")
    else:
        print("❌ Consultation inquiry alert failed")
    
    print("\n" + "=" * 60)
    print("🏁 Inquiry alert system test complete!")
    print("📱 Admin should receive alerts at: (808) 452-9779")

if __name__ == "__main__":
    test_inquiry_alerts()