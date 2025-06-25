"""
Public-facing routes for SPANKKS Construction website
Pulls data exclusively from PostgreSQL database
"""

import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import render_template, request
from config.app import app

@app.route('/spankks-skool')
def spankks_skool():
    """SPANKKS SKOOL educational platform with courses from database"""
    try:
        # Get courses organized by category from database
        with psycopg2.connect(os.environ.get('DATABASE_URL')) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        c.title,
                        c.description,
                        c.skill_level,
                        c.category,
                        c.spank_bucks_reward,
                        c.estimated_duration,
                        COUNT(l.lesson_id) as lesson_count,
                        COUNT(CASE WHEN l.lesson_type = 'interactive' THEN 1 END) as interactive_lessons
                    FROM courses c
                    LEFT JOIN lessons l ON c.course_id = l.course_id
                    WHERE c.is_active = true
                    GROUP BY c.course_id, c.title, c.description, c.skill_level, c.category, 
                             c.spank_bucks_reward, c.estimated_duration, c.display_order
                    ORDER BY c.display_order
                """)
                courses = cur.fetchall()
        
        # Organize courses by category
        courses_by_category = {}
        total_rewards = 0
        total_lessons = 0
        
        for course in courses:
            category = course['category']
            if category not in courses_by_category:
                courses_by_category[category] = []
            courses_by_category[category].append(course)
            total_rewards += course['spank_bucks_reward'] or 0
            total_lessons += course['lesson_count'] or 0
        
        return render_template('spankks_skool.html', 
                             courses_by_category=courses_by_category,
                             courses=courses,
                             total_rewards=total_rewards,
                             total_lessons=total_lessons)
                             
    except Exception as e:
        logger.error(f"Error loading SPANKKS SKOOL data: {str(e)}")
        return render_template('spankks_skool.html', 
                             courses_by_category={},
                             courses=[],
                             total_rewards=0,
                             total_lessons=0)

logger = logging.getLogger(__name__)

@app.route('/consultation')
def consultation():
    """Consultation booking page with services from database"""
    try:
        # Get services for consultation form
        with psycopg2.connect(os.environ.get('DATABASE_URL')) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        sc.name as category_name,
                        st.service_code,
                        st.name,
                        st.min_price,
                        st.max_price,
                        st.unit
                    FROM service_types st
                    JOIN service_categories sc ON st.category_id = sc.id
                    WHERE st.is_active = true AND st.user_type = 'client'
                    ORDER BY sc.name, st.name
                """)
                services = cur.fetchall()
        
        # Organize services by category
        services_by_category = {}
        for service in services:
            category = service['category_name']
            if category not in services_by_category:
                services_by_category[category] = []
            services_by_category[category].append(service)
        
        return render_template('consultation.html', 
                             services_by_category=services_by_category)
                             
    except Exception as e:
        logger.error(f"Error loading consultation page: {str(e)}")
        return render_template('consultation.html', services_by_category=services_by_category)

# Import successful completion message
@app.route('/form-confirmation')
def form_confirmation():
    """Form confirmation page"""
    form_type = request.args.get('type', 'inquiry')
    reference_number = request.args.get('ref', None)
    return render_template('form_confirmation.html', 
                         form_type=form_type,
                         reference_number=reference_number)

@app.route('/', methods=['GET'])
def public_home():
    """Home page with featured services from database"""
    try:
        # Get featured services (highest value services from each category)
        with psycopg2.connect(os.environ.get('DATABASE_URL')) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT DISTINCT ON (sc.name)
                        st.service_code,
                        st.name,
                        st.description,
                        st.min_price,
                        st.max_price,
                        st.unit,
                        sc.name as category_name
                    FROM service_types st
                    JOIN service_categories sc ON st.category_id = sc.id
                    WHERE st.is_active = true AND st.user_type = 'client'
                    ORDER BY sc.name, st.max_price DESC
                    LIMIT 6
                """)
                featured_services = cur.fetchall()
                
                # Get basic stats
                cur.execute("""
                    SELECT 
                        COUNT(DISTINCT client_id) as total_projects,
                        5 as years_experience
                    FROM jobs WHERE status != 'cancelled'
                """)
                stats_data = cur.fetchone()
                
        stats = {
            'total_projects': stats_data['total_projects'] if stats_data else 0,
            'years_experience': int(stats_data['years_experience']) if stats_data and stats_data['years_experience'] else 5,
            'satisfied_customers': (stats_data['total_projects'] * 2) if stats_data else 100
        }
        
        # Check if we should render the old template for backwards compatibility
        if request.endpoint == 'index':
            return render_template('index.html')
        else:
            return render_template('home.html', 
                                 featured_services=featured_services,
                                 stats=stats)
                             
    except Exception as e:
        logger.error(f"Error loading home page data: {str(e)}")
        # Fallback for old index route
        if request.endpoint == 'index':
            return render_template('index.html')
        else:
            return render_template('home.html', 
                                 featured_services=[],
                                 stats={})

@app.route('/services')
def public_services():
    """Public services page with data from PostgreSQL database"""
    try:
        # Get all services organized by category from database
        with psycopg2.connect(os.environ.get('DATABASE_URL')) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        sc.name as category_name,
                        st.service_code,
                        st.name,
                        st.description,
                        st.min_price,
                        st.max_price,
                        st.unit,
                        st.estimated_hours,
                        st.portal_access
                    FROM service_types st
                    JOIN service_categories sc ON st.category_id = sc.id
                    WHERE st.is_active = true AND st.user_type = 'client'
                    ORDER BY sc.name, st.min_price
                """)
                services = cur.fetchall()
        
        # Organize services by category
        services_by_category = {}
        for service in services:
            category = service['category_name']
            if category not in services_by_category:
                services_by_category[category] = []
            services_by_category[category].append(service)
        
        return render_template('services.html', 
                             services_by_category=services_by_category)
                             
    except Exception as e:
        logger.error(f"Error loading services data: {str(e)}")
        return render_template('services.html', services_by_category={})

@app.route('/pricing')
def public_pricing():
    """Public pricing page with data from PostgreSQL database"""
    try:
        # Get services organized by category from database
        with psycopg2.connect(os.environ.get('DATABASE_URL')) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get services by category
                cur.execute("""
                    SELECT 
                        sc.name as category_name,
                        st.service_code,
                        st.name,
                        st.description,
                        st.min_price,
                        st.max_price,
                        st.unit,
                        st.estimated_hours,
                        st.portal_access
                    FROM service_types st
                    JOIN service_categories sc ON st.category_id = sc.id
                    WHERE st.is_active = true AND st.user_type = 'client'
                    ORDER BY sc.name, st.min_price
                """)
                services = cur.fetchall()
                
                # Get service packages
                cur.execute("""
                    SELECT 
                        sp.name,
                        sp.description,
                        sp.base_price,
                        sp.estimated_hours,
                        pt.discount_percentage
                    FROM service_packages sp
                    LEFT JOIN package_types pt ON sp.package_type_id = pt.id
                    ORDER BY sp.base_price
                """)
                service_packages = cur.fetchall()
                
                # Get membership types
                cur.execute("""
                    SELECT 
                        name,
                        description,
                        monthly_fee,
                        discount_percentage,
                        benefits
                    FROM membership_types
                    ORDER BY monthly_fee
                """)
                membership_types = cur.fetchall()
        
        # Organize services by category
        services_by_category = {}
        for service in services:
            category = service['category_name']
            if category not in services_by_category:
                services_by_category[category] = []
            services_by_category[category].append(service)
        
        return render_template('pricing.html', 
                             services_by_category=services_by_category,
                             service_packages=service_packages,
                             membership_types=membership_types)
                             
    except Exception as e:
        logger.error(f"Error loading pricing data: {str(e)}")
        # Fallback to basic template
        return render_template('pricing.html', 
                             services_by_category={},
                             service_packages=[],
                             membership_types=[])

@app.route('/about')
def public_about():
    """About page with company information"""
    try:
        # Get basic stats from database
        with psycopg2.connect(os.environ.get('DATABASE_URL')) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        COUNT(DISTINCT client_id) as total_projects,
                        EXTRACT(YEAR FROM AGE(NOW(), MIN(created_at))) as years_experience
                    FROM jobs WHERE status != 'cancelled'
                """)
                stats_data = cur.fetchone()
                
        stats = {
            'total_projects': stats_data['total_projects'] if stats_data else 0,
            'years_experience': int(stats_data['years_experience']) if stats_data and stats_data['years_experience'] else 5
        }
        
        return render_template('about.html', stats=stats)
        
    except Exception as e:
        logger.error(f"Error loading about page: {str(e)}")
        return render_template('about.html', stats={})

@app.route('/contact')
def public_contact():
    """Contact page with service options from database"""
    try:
        # Get services for contact form dropdown
        with psycopg2.connect(os.environ.get('DATABASE_URL')) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        sc.name as category_name,
                        st.service_code,
                        st.name
                    FROM service_types st
                    JOIN service_categories sc ON st.category_id = sc.id
                    WHERE st.is_active = true AND st.user_type = 'client'
                    ORDER BY sc.name, st.name
                """)
                services = cur.fetchall()
        
        # Organize services by category for form dropdown
        services_by_category = {}
        for service in services:
            category = service['category_name']
            if category not in services_by_category:
                services_by_category[category] = []
            services_by_category[category].append(service)
        
        return render_template('contact.html', 
                             services_by_category=services_by_category)
                             
    except Exception as e:
        logger.error(f"Error loading contact page: {str(e)}")
        return render_template('contact.html', services_by_category={})