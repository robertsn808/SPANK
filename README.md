# SPANKKS Construction - Complete Business Management System

## Overview
Professional construction business website with comprehensive admin portal built with Flask and PostgreSQL. Features complete customer lifecycle management from initial contact through project completion and payment processing.

## Features

### Customer-Facing Website
- Responsive design optimized for mobile and desktop
- Professional service catalog with Hawaii market pricing
- Contact forms and consultation booking
- SPANKKS SKOOL educational platform (16 courses, 32+ lessons)
- Service request system with automatic notifications

### Admin Dashboard
- Complete business management portal
- Customer relationship management (CRM)
- Quote generation with Hawaii GET tax calculations (4.712%)
- Job scheduling and task management
- Invoice creation and payment tracking
- Staff management with role-based permissions
- Business analytics and financial reporting
- Inventory and materials tracking

### Portal Access
- Secure client portals for project updates
- Staff portals for field crew management
- Real-time job status updates
- Photo documentation system
- Task checklist management

## Technical Stack
- **Backend**: Flask (Python 3.11)
- **Database**: PostgreSQL with 12 core tables
- **Frontend**: Bootstrap 5, responsive design
- **Authentication**: Session-based security
- **Server**: Gunicorn WSGI for production
- **Environment**: Configured for Replit deployment

## Database Schema
- `clients` - Customer information and contact preferences
- `quotes` - Quote generation with line items and tax calculations
- `jobs` - Project scheduling and status tracking
- `invoices` - Billing and payment management
- `staff` - Employee management and role assignments
- `service_types` - Service catalog and pricing
- `client_portal_access` - Secure portal authentication
- `scheduling_calendar` - Appointment and job scheduling
- `photo_documentation` - Before/after project photos
- `materials_used` - Materials tracking and cost analysis
- `checklists` - Task management and completion tracking
- `notifications` - Admin notification system

## Installation

### Requirements
- Python 3.11+
- PostgreSQL database
- Environment variables: `DATABASE_URL`, `SESSION_SECRET`

### Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure PostgreSQL database connection
3. Run database migrations (tables auto-create on first run)
4. Start server: `gunicorn --bind 0.0.0.0:5000 main:app`

## Admin Access
- **Username**: `spankysadmin808`
- **Password**: `Money$$`
- **Portal**: `/admin/login`

## Key URLs
- **Public Website**: `/`
- **Admin Dashboard**: `/admin-home`
- **Client Portal**: `/client-portal`
- **API Endpoints**: `/api/*` (15+ endpoints for business operations)

## Business Features
- Hawaii-specific tax calculations (4.712% GET tax)
- Multi-project client management
- Authentic Oahu market pricing ($60-$124/hr services)
- Complete quote-to-invoice workflow
- Staff scheduling and capacity management
- Financial reporting with P&L statements
- Customer satisfaction tracking

## Security
- Session-based authentication
- Role-based access control
- Secure portal credentials
- Data validation and sanitization
- PostgreSQL prepared statements

## Deployment
Configured for production deployment with:
- Gunicorn WSGI server
- PostgreSQL connection pooling
- Error handling and logging
- Mobile-responsive design
- Hawaii timezone support

---
*Generated: June 25, 2025*
*SPANKKS Construction - Professional Business Management System*