# Professional Handyman Services Website

## Overview

This is a comprehensive Flask-based web application for a professional handyman business. The application features a complete business website with customer-facing services and an AI-powered lead generation system in the management portal.

## System Architecture

The application follows a simple Flask MVC pattern with the following structure:

- **Frontend**: Bootstrap 5-based responsive web interface with custom CSS and JavaScript
- **Backend**: Flask web framework with Python 3.11
- **Data Storage**: In-memory data storage using Python classes (ready for database integration)
- **Deployment**: Configured for Replit with Gunicorn WSGI server
- **Environment**: Nix-based development environment with PostgreSQL ready for integration

## Key Components

### Application Structure
- `main.py` - Main application entry point for production
- `app.py` - Flask application factory and configuration
- `routes.py` - All route handlers and business logic
- `models.py` - Data models (ContactMessage, Booking, BookingStorage)

### Frontend Components
- **Base Template** (`templates/base.html`) - Main layout with navigation
- **Public Pages**: Home, About, Gallery, Reviews, Contact, Consultation
- **Admin Interface**: Separate admin dashboard with authentication
- **Responsive Design**: Mobile-first Bootstrap 5 implementation

### Data Models
- **ContactMessage**: Customer inquiries with AI analysis and priority scoring
- **ServiceRequest**: Handyman service requests with AI recommendations
- **Lead**: Lead management with AI scoring and follow-up suggestions
- **Staff**: Employee management (basic structure in place)
- **HandymanStorage**: In-memory storage manager for all business data

## Data Flow

1. **Customer Journey**: 
   - Browse services → Request consultation → Form submission → Admin review
   
2. **Admin Workflow**:
   - Admin login → Dashboard view → Manage bookings/messages → Update status

3. **Storage Pattern**:
   - Data stored in memory using Python classes
   - Ready for database migration (PostgreSQL configured in environment)

## External Dependencies

### Core Dependencies
- **Flask 3.1.1**: Web framework
- **Bootstrap 5.3.0**: Frontend framework
- **Font Awesome 6.4.0**: Icons
- **Gunicorn 23.0.0**: WSGI server

### Additional Libraries
- **psycopg2-binary**: PostgreSQL adapter (ready for database integration)
- **flask-sqlalchemy**: ORM (available but not yet implemented)
- **email-validator**: Form validation
- **pytz**: Timezone handling (Hawaii timezone support)

### Frontend Assets
- **Google Fonts**: Poppins font family
- **Video Background**: Hero section with autoplay video
- **Custom CSS**: Professional styling with gradients and animations

## Deployment Strategy

### Replit Configuration
- **Runtime**: Python 3.11 with Nix package manager
- **Server**: Gunicorn with auto-scaling deployment target
- **Port Configuration**: Internal 5000, external 80
- **Environment**: OpenSSL and PostgreSQL packages pre-installed

### Production Settings
- Session management with secure secret key
- Debug mode disabled in production
- Proper error handling and logging

## Changelog

- June 18, 2025. Initial setup
- June 19, 2025. Transformed to handyman business with AI lead generator
- June 21, 2025. Integrated SPANK logo and completed branding
- June 21, 2025. Created comprehensive "Spank School" educational platform with interactive DIY courses, live Q&A webinars, troubleshooter simulator, tool guides, quizzes, and gamification
- June 21, 2025. Enhanced Spank School with comprehensive interactive course content: toilet repair (4 lessons), faucet repair, drywall patching, electrical safety courses with step-by-step guidance, interactive quizzes, safety warnings, and video tutorial integration
- June 21, 2025. Regenerated SPANK School with modern card-based design, removed user progress tracking, implemented $5 SPANK Buck email reward system for course completion and referrals
- June 21, 2025. Completely regenerated pricing page with authentic Oahu/Honolulu market rates ($60-$124/hr), added comprehensive service pricing table with "Learn DIY" SPANK School links, implemented membership plans ($89-$249/month), and fixed homepage background image
- June 21, 2025. Added comprehensive Knowledge Quiz system (5 questions, 4/5 passing score for $5 SPANK Bucks monthly reward) and interactive Problem Solver with step-by-step troubleshooting for faucets, toilets, and electrical outlets
- June 21, 2025. Implemented multi-page lesson navigation with visual SVG illustrations, progress indicators, and enhanced quiz feedback system for immersive learning experience
- June 21, 2025. Built comprehensive SPANK Buck notification system with RapidAPI/SendGrid email integration, Twilio SMS support, professional HTML email templates, and API endpoints for course completion ($5) and referral rewards ($25)
- June 21, 2025. Implemented comprehensive mobile-first responsive design optimization across all pages with touch-friendly buttons, adaptive typography, mobile navigation enhancements, and device-specific CSS optimizations for desktop, tablet, and mobile viewing experiences
- June 21, 2025. Configured Twilio SendGrid integration with provided credentials (SID: US56bbfe10c643f708191c41349097faa4, Phone: +18778102726) for unified SMS and email delivery system
- June 21, 2025. Added inquiry alert system to notify (808) 452-9779 via SMS for all new contact form submissions and consultation requests with customer details
- June 21, 2025. Rebranded from "SPANK Handyman Services" to "Spankks Construction" with specialization in flooring, drywall, and home repair services
- June 21, 2025. Updated contact information to spank808@gmail.com and (808) 778-9132
- June 21, 2025. Integrated comprehensive Nextdoor Business Hub into admin dashboard with neighborhood engagement tools, service request management, review tracking, and promotional features
- June 21, 2025. Implemented authentic Spankks Construction LLC pricing structure with real-world rates: drywall services ($155-$600), flooring installation ($3-$8/sq.ft), fence building ($35-$70/linear ft), general repairs ($90-$200), and home renovations ($2,500-$25,000) including Spankks Bucks integration and bundle discounts
- June 21, 2025. Enhanced admin dashboard with comprehensive job opportunities section featuring lead tracking from Nextdoor, TaskRabbit, Thumbtack, referrals, and direct inquiries with interactive opportunity management and quick action tools
- June 21, 2025. Rebranded "SPANK School" to "SPANKKS SKOOL" throughout website and implemented SPANKKS SKOOL 2.0 with professional course structure: Basics Everyone Should Know, Surface & Structure, Before You Renovate, and Fence & Exterior sections showcasing Spankks Construction expertise while guiding customers to professional services
- June 21, 2025. Added comprehensive Smart Home Upgrades course to SPANKKS SKOOL featuring 4-lesson structure covering smart switches vs bulbs, renovation planning with Spankks, kitchen/bath smart fixtures, and bonus $85 smart switch install offer for renovation estimates
- June 21, 2025. Enhanced desktop pricing page styling with pricing-card CSS class for improved visual hierarchy, better spacing, and professional presentation on larger screens while maintaining mobile responsiveness
- June 21, 2025. Updated hero backgrounds: home page features SPANKKS fence construction photo showing professional team at work, SPANKKS SKOOL page features character mascot creating educational brand identity
- June 21, 2025. Updated website favicon and background wallpapers across pricing, contact, and SPANKKS SKOOL pages to use new SPANKKS logo with construction worker character, hammer, and wrench tools for consistent branding
- June 21, 2025. Updated navigation bar logo and homepage about section image to use new SPANKKS logo featuring construction worker with tools, completing comprehensive brand identity update across all website elements
- June 21, 2025. Enhanced SPANKKS SKOOL with comprehensive interactive Toolbelt Basics course featuring 3 lessons: Know Your Tools (drag-and-drop tool matching), Start with the Basics (toolbelt simulator with 6-slot limitation), and Keep Things Handy (toolbox organization activity) with visual step-by-step guides, interactive elements, checkpoint quizzes, and $5 SPANK Buck completion rewards
- June 21, 2025. Expanded SPANKKS SKOOL with comprehensive course catalog: added interactive "Hang a Picture" course (anchor selection simulator, leveling activities), "Squeaky Door Fix" course (sound identification, hinge repair simulator), and full intermediate-level section including "Install a Smart Lock" ($10 SPANK Bucks), "Fix a Running Toilet", "Build a Storage Shelf", "Caulk a Bathtub Like a Pro", and "Install a Ceiling Light Fixture" with compatibility quizzes, step-by-step simulations, and progressive skill unlocking system
- June 21, 2025. Implemented comprehensive "Caulk a Bathtub Like a Pro" course with drag-and-scrape caulk removal simulator, virtual caulk gun alignment practice, and professional bead application techniques, plus "Install a Ceiling Light Fixture" course featuring circuit breaker safety simulator, voltage testing practice, and color-coded wire matching activities with electrical safety protocols
- June 21, 2025. Added "DIY Smart Switches Installation" course ($10 SPANK Bucks) with 4 interactive lessons: understanding smart switches, tools/safety checks with voltage testing simulator, wire identification with drag-and-drop matching, and step-by-step installation progress tracker with brand recommendations (Lutron Caseta, TP-Link Kasa)
- June 21, 2025. Created "Installing a Doggy Door" ($5 SPANK Bucks) and "Choosing the Right Anchor" ($5 SPANK Bucks) beginner courses based on user-provided guides, featuring pet sizing guidance, wall type identification, weight-based anchor selection, and comprehensive installation instructions with Spankks Construction professional service integration
- June 21, 2025. Updated navigation branding to capitalize "SPANKKS Construction" and corrected logo image path for consistent brand presentation
- June 21, 2025. Enhanced admin dashboard with comprehensive business analytics including revenue tracking, customer insights, weekly performance metrics, lead source analysis, and customer satisfaction monitoring with visual progress indicators
- June 21, 2025. Added advanced business management tools: Project Tracking dashboard for timeline monitoring and deadline alerts, Analytics Dashboard with conversion funnel analysis and monthly performance trends, plus integrated navigation for seamless workflow management
- June 21, 2025. Implemented comprehensive customer relationship management system with Customer Feedback dashboard for satisfaction tracking and automated follow-up campaigns, Bulk Communications tool for targeted promotional campaigns with SPANK Buck integration, seasonal promotions management, and customer segmentation analytics with performance metrics tracking
- June 22, 2025. Built comprehensive CRM system with contact database management (job history tracking, total revenue per customer), interactive quote builder with service templates and Hawaii tax calculations, invoice generation engine with PDF capabilities, drag-and-drop job scheduling with weekly calendar view, mobile-optimized job cards for crew access with status updates and note-taking, complete customer lifecycle tracking from quote to completion
- June 22, 2025. Implemented professional PDF generation system using ReportLab with SPANKKS Construction branding, automated quote and invoice PDF creation with Hawaii GET tax calculations, email delivery integration via Twilio SendGrid, comprehensive quote-to-invoice workflow with status tracking, mobile-friendly PDF downloads and customer email distribution, tested with sample data matching provided specifications (Jane Doe, $1000 quote, $1047.12 invoice)
- June 22, 2025. Built Node.js-compatible API integration with /api/generate-quote and /api/download-quote endpoints supporting JSON and form data, automatic contact creation, professional PDF generation with SPANKKS branding, Hawaii tax calculations, service-specific quote categorization, and comprehensive external integration capabilities tested with multiple quote scenarios (Q0001-Q0005)
- June 22, 2025. Completed Node.js-style invoice generation API with /api/generate-invoice and /api/download-invoice endpoints, automatic subtotal calculation from total amounts, reverse Hawaii tax computation, seamless CRM integration, professional PDF generation, and comprehensive testing with 3 successful invoice scenarios (I0001-I0003) demonstrating full quote-to-invoice workflow capabilities
- June 22, 2025. Implemented comprehensive job photo upload system with before/after photo documentation, metadata tracking, file size validation (16MB max), support for JPEG/PNG/HEIC formats, automated admin notifications via Twilio SMS, RESTful API endpoints for upload/retrieval/deletion, and mobile-optimized photo management interface with drag-and-drop functionality
- June 22, 2025. Enhanced frontend form with multi-line quote capabilities supporting req.body.items[] array structure with description, unit_price, line_total fields, interactive line item management, real-time pricing calculations, discount/tax handling, live summary updates, and maintained backward compatibility with legacy single-item quotes
- June 22, 2025. Verified all inquiry forms, Twilio integrations, and API endpoints with comprehensive testing: contact forms (PASS), consultation requests (PASS), photo uploads (PASS), quote generation API (PASS), invoice generation API (PASS), with proper error handling and admin notifications for all customer touchpoints

## User Preferences

Preferred communication style: Simple, everyday language.

## Technical Notes

### Ready for Database Integration
The application currently uses in-memory storage but is architected for easy database integration:
- PostgreSQL is configured in the environment
- SQLAlchemy is available as a dependency
- Models are structured for easy ORM conversion

### Authentication System
- Simple admin authentication with hardcoded credentials
- Session-based login management
- Admin-only access to dashboard and booking management

### Mobile Optimization
- Responsive design with Bootstrap 5
- Touch-friendly interface elements
- Optimized for Hawaii's mobile-first user base

### Hawaii-Specific Features
- Hawaii timezone support (Pacific/Honolulu)
- Local business focus and messaging
- Phone number and local service area emphasis