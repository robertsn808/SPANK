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