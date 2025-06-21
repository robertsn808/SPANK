#!/usr/bin/env python3
"""
Test script for Twilio SendGrid integration
Run this to test SMS and email functionality with provided credentials
"""

import os
import logging
from notification_service import NotificationService

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_twilio_integration():
    """Test Twilio SMS and SendGrid email integration"""
    
    # Your provided credentials
    TWILIO_SID = "US56bbfe10c643f708191c41349097faa4"
    TWILIO_TOKEN = "4cd27b48274be507ac9163775722ad8e"
    TWILIO_PHONE = "+18778102726"
    
    print("🔧 Testing Twilio SendGrid Integration for SPANK Handyman Services")
    print("=" * 60)
    
    # Create notification service with your credentials
    service = NotificationService()
    service.twilio_sid = TWILIO_SID
    service.twilio_token = TWILIO_TOKEN
    service.twilio_phone = TWILIO_PHONE
    
    # Initialize Twilio client
    if service.twilio_sid and service.twilio_token:
        from twilio.rest import Client
        service.twilio_client = Client(service.twilio_sid, service.twilio_token)
        print("✅ Twilio client initialized successfully")
    else:
        print("❌ Twilio credentials missing")
        return
    
    # Test SMS functionality
    print("\n📱 Testing SMS functionality...")
    test_phone = input("Enter phone number for SMS test (format: +18085551234): ").strip()
    
    if test_phone:
        try:
            sms_result = service.send_spank_buck_sms(
                to_phone=test_phone,
                amount=5,
                reason="testing Twilio SMS integration",
                customer_name="Test User"
            )
            
            if sms_result:
                print("✅ SMS sent successfully!")
            else:
                print("❌ SMS failed to send")
                
        except Exception as e:
            print(f"❌ SMS error: {e}")
    
    # Test email functionality (if SendGrid key provided)
    print("\n📧 Testing email functionality...")
    sendgrid_key = input("Enter SendGrid API key (or press Enter to skip): ").strip()
    
    if sendgrid_key:
        service.sendgrid_key = sendgrid_key
        test_email = input("Enter email address for test: ").strip()
        
        if test_email:
            try:
                email_result = service.send_twilio_sendgrid_email(
                    to_email=test_email,
                    amount=5,
                    reason="testing SendGrid email integration",
                    customer_name="Test User"
                )
                
                if email_result:
                    print("✅ Email sent successfully!")
                else:
                    print("❌ Email failed to send")
                    
            except Exception as e:
                print(f"❌ Email error: {e}")
    else:
        print("⏭️  Skipping email test (no SendGrid key provided)")
    
    # Test integrated SPANK Buck reward
    print("\n🎉 Testing integrated SPANK Buck reward...")
    reward_phone = input("Enter phone number for reward test (or press Enter to skip): ").strip()
    
    if reward_phone:
        reward_email = input("Enter email for reward test (optional): ").strip() or None
        
        try:
            reward_result = service.send_spank_buck_reward(
                phone_number=reward_phone,
                amount=25,
                reason="testing integrated SPANK Buck system",
                customer_name="Test Customer",
                email=reward_email
            )
            
            if reward_result:
                print("✅ SPANK Buck reward sent successfully!")
            else:
                print("❌ SPANK Buck reward failed")
                
        except Exception as e:
            print(f"❌ Reward error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Twilio SendGrid integration test complete!")
    print("📞 Contact: (808) 778-9132 | 📧 spank808@gmail.com")

if __name__ == "__main__":
    test_twilio_integration()