# SPANKKS Construction CSV Upload Templates

## Overview
These CSV templates provide standardized formats for bulk data upload to the SPANKKS Construction database. Each template includes sample data to guide proper formatting.

## Available Templates

### 1. clients_template.csv
Upload client/customer information including contact details and preferences.
- **Fields**: name, phone, email, address, city, state, zip_code, client_type, notes, preferred_contact_method
- **Client Types**: residential, commercial
- **Contact Methods**: phone, email, text

### 2. jobs_template.csv
Upload job records with service details and scheduling information.
- **Fields**: client_name, client_email, job_title, service_type, description, location, priority, status, estimated_hours, hourly_rate, materials_cost, scheduled_date, scheduled_time, completion_date, notes
- **Status Options**: pending, quoted, scheduled, in_progress, completed, cancelled
- **Priority Levels**: low, medium, high

### 3. schedule_template.csv
Upload appointment and scheduling data.
- **Fields**: client_name, client_phone, client_email, appointment_date, appointment_time, duration_minutes, service_type, description, location, priority, status, assigned_staff, notes
- **Date Format**: YYYY-MM-DD
- **Time Format**: HH:MM (24-hour)

### 4. service_types_template.csv
Upload service categories with pricing and specifications.
- **Fields**: service_name, category, base_hourly_rate, unit_type, unit_price, estimated_hours, description, materials_included, equipment_required, skill_level
- **Categories**: Drywall Services, Flooring Installation, Fence Building, General Handyman
- **Skill Levels**: beginner, intermediate, advanced

### 5. staff_template.csv
Upload employee information and availability.
- **Fields**: name, phone, email, role, hourly_rate, skills, availability, hire_date, status, emergency_contact, emergency_phone, notes
- **Roles**: Lead Technician, Flooring Specialist, General Handyman, Fence Specialist
- **Status Options**: active, inactive, on_leave

### 6. quotes_template.csv
Upload quote records with Hawaii tax calculations.
- **Fields**: client_name, client_email, quote_title, service_type, description, quantity, unit, unit_price, line_total, total_before_tax, hawaii_tax_rate, hawaii_tax_amount, total_amount, status, valid_until, notes
- **Tax Rate**: 0.04712 (4.712% O'ahu GET tax)
- **Status Options**: draft, pending, approved, declined, expired

### 7. invoices_template.csv
Upload invoice records with payment tracking.
- **Fields**: client_name, client_email, invoice_title, service_type, description, quantity, unit, unit_price, line_total, total_before_tax, hawaii_tax_rate, hawaii_tax_amount, total_amount, payment_status, payment_method, payment_date, due_date, notes
- **Payment Status**: paid, pending, overdue, partial
- **Payment Methods**: cash, check, venmo, zelle, bank_transfer, credit_card

## Usage Instructions

1. Download the appropriate CSV template
2. Replace sample data with your actual data
3. Maintain the header row format
4. Use consistent date formats (YYYY-MM-DD)
5. Ensure phone numbers use (XXX) XXX-XXXX format
6. Hawaii GET tax rate is pre-calculated at 4.712%
7. Upload through the admin dashboard bulk import feature

## Data Validation

- Phone numbers will be automatically formatted
- Email addresses must be valid format
- Dates must be in YYYY-MM-DD format
- Monetary amounts should use decimal format (123.45)
- Required fields cannot be empty

## Support

For assistance with CSV uploads or data formatting, contact the SPANKKS Construction admin team.