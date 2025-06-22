"""
Phone Number Formatting Utility for SPANKKS Construction
Ensures consistent phone number formatting across the application
"""

import re

class PhoneFormatter:
    """Professional phone number formatting and validation"""
    
    @staticmethod
    def format_phone(phone_number):
        """
        Format phone number to standard (XXX) XXX-XXXX format
        Handles various input formats and returns consistent output
        """
        if not phone_number:
            return ""
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', str(phone_number))
        
        # Handle different digit lengths
        if len(digits) == 10:
            # Standard US phone number
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            # US phone number with country code
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        elif len(digits) == 7:
            # Local number (add Hawaii area code)
            return f"(808) {digits[:3]}-{digits[3:]}"
        else:
            # Return original if format is unclear
            return phone_number
    
    @staticmethod
    def is_valid_phone(phone_number):
        """Validate phone number format"""
        if not phone_number:
            return False
        
        digits = re.sub(r'\D', '', str(phone_number))
        
        # Valid formats: 7 digits (local), 10 digits (US), 11 digits (US with country code)
        return len(digits) in [7, 10, 11]
    
    @staticmethod
    def to_clickable_format(phone_number):
        """Convert phone number to tel: link format"""
        if not phone_number:
            return ""
        
        digits = re.sub(r'\D', '', str(phone_number))
        
        if len(digits) == 10:
            return f"tel:+1{digits}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"tel:+{digits}"
        elif len(digits) == 7:
            return f"tel:+1808{digits}"
        else:
            return f"tel:{digits}"
    
    @staticmethod
    def clean_for_storage(phone_number):
        """Clean phone number for database storage (digits only)"""
        if not phone_number:
            return ""
        
        return re.sub(r'\D', '', str(phone_number))
    
    @staticmethod
    def format_hawaii_business_phone(phone_number=None):
        """Format SPANKKS Construction business phone number"""
        if phone_number is None:
            phone_number = "8087789132"  # Default business number
        
        return PhoneFormatter.format_phone(phone_number)

# Global formatter instance
phone_formatter = PhoneFormatter()