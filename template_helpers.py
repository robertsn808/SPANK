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