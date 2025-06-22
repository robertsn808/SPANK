"""
Template Helper Functions for SPANKKS Construction
Provides Jinja2 template filters and functions for consistent formatting
"""

from phone_formatter import phone_formatter

def format_phone_display(phone_number):
    """Template filter for displaying formatted phone numbers"""
    return phone_formatter.format_phone(phone_number)

def phone_link(phone_number):
    """Template filter for creating clickable phone links"""
    return phone_formatter.to_clickable_format(phone_number)

def register_template_helpers(app):
    """Register all template helpers with Flask app"""
    app.jinja_env.filters['format_phone'] = format_phone_display
    app.jinja_env.filters['phone_link'] = phone_link
    
    # Global template variables
    app.jinja_env.globals['business_phone'] = phone_formatter.format_hawaii_business_phone()
    app.jinja_env.globals['business_phone_link'] = phone_formatter.to_clickable_format('8087789132')
from datetime import datetime
import pytz

def get_hawaii_time():
    """Get current time in Hawaii timezone"""
    hawaii_tz = pytz.timezone('Pacific/Honolulu')
    utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    return utc_now.astimezone(hawaii_tz)

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def format_phone(phone):
    """Format phone number"""
    if not phone:
        return ""
    # Remove all non-digits
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone

# Template helper functions
template_helpers = {
    'get_hawaii_time': get_hawaii_time,
    'format_currency': format_currency,
    'format_phone': format_phone
}
