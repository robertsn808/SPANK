from datetime import datetime
import pytz

def get_hawaii_time():
    """Get current time in Hawaii timezone"""
    hawaii_tz = pytz.timezone('Pacific/Honolulu')
    utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    return utc_now.astimezone(hawaii_tz)

def format_currency(amount):
    """Format amount as currency"""
    try:
        return f"${float(amount):,.2f}"
    except (ValueError, TypeError):
        return f"${0.00:,.2f}"

def format_phone(phone):
    """Format phone number"""
    if not phone:
        return ""
    # Remove all non-digits
    digits = ''.join(filter(str.isdigit, str(phone)))
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return str(phone)

def register_template_helpers(app):
    """Register all template helpers with Flask app"""
    # Add custom filters
    app.jinja_env.filters['format_currency'] = format_currency
    app.jinja_env.filters['format_phone'] = format_phone
    
    # Add global functions
    app.jinja_env.globals['get_hawaii_time'] = get_hawaii_time
    app.jinja_env.globals['business_phone'] = '(808) 778-9132'
    app.jinja_env.globals['business_email'] = 'spank808@gmail.com'

# Template helper functions
template_helpers = {
    'get_hawaii_time': get_hawaii_time,
    'format_currency': format_currency,
    'format_phone': format_phone
}