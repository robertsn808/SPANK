from app import db
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))


class ServiceCategory(db.Model):
    __tablename__ = 'service_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer, default=0)
    icon = db.Column(db.String(50))  # FontAwesome icon class
    color = db.Column(db.String(7))  # Hex color code
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    service_types = db.relationship('ServiceType', backref='service_category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'display_order': self.display_order,
            'icon': self.icon,
            'color': self.color,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'service_count': len(self.service_types)
        }


class ServiceType(db.Model):
    __tablename__ = 'service_types'
    
    id = db.Column(db.Integer, primary_key=True)
    service_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('service_categories.id'))
    
    # Pricing information
    price_min = db.Column(db.Numeric(10, 2))
    price_max = db.Column(db.Numeric(10, 2))
    price_type = db.Column(db.String(20), default='fixed')  # fixed, hourly, sqft, linear, estimate
    
    # Duration information
    duration_min = db.Column(db.Numeric(4, 1))  # in hours
    duration_max = db.Column(db.Numeric(4, 1))  # in hours
    duration_unit = db.Column(db.String(10), default='hours')  # hours, days, weeks
    
    # Access and user configuration
    requires_portal = db.Column(db.Boolean, default=False)
    user_type = db.Column(db.String(20), nullable=False)  # client, bizcontacts, staff, other
    status = db.Column(db.String(20), default='active')  # active, inactive, seasonal
    
    # Tax and business settings
    taxable = db.Column(db.Boolean, default=True)
    available_online = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(50), default='admin')
    
    def to_dict(self):
        return {
            'id': self.id,
            'service_code': self.service_code,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id,
            'category_name': self.service_category.name if self.service_category else None,
            'price_min': float(self.price_min) if self.price_min else None,
            'price_max': float(self.price_max) if self.price_max else None,
            'price_type': self.price_type,
            'duration_min': float(self.duration_min) if self.duration_min else None,
            'duration_max': float(self.duration_max) if self.duration_max else None,
            'duration_unit': self.duration_unit,
            'requires_portal': self.requires_portal,
            'user_type': self.user_type,
            'status': self.status,
            'taxable': self.taxable,
            'available_online': self.available_online,
            'display_order': self.display_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }


class PackageType(db.Model):
    __tablename__ = 'package_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    package_type = db.Column(db.String(50), nullable=False)  # bundle, seasonal, promotional, custom
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    packages = db.relationship('ServicePackage', backref='package_type_ref', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'package_type': self.package_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'package_count': len(self.packages)
        }


class ServicePackage(db.Model):
    __tablename__ = 'service_packages'
    
    id = db.Column(db.Integer, primary_key=True)
    package_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    package_type_id = db.Column(db.Integer, db.ForeignKey('package_types.id'))
    
    # Pricing
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_percentage = db.Column(db.Numeric(5, 2), default=0)
    final_price = db.Column(db.Numeric(10, 2))
    
    # Package details
    estimated_duration = db.Column(db.String(50))  # "2-3 days", "1 week", etc.
    includes_materials = db.Column(db.Boolean, default=False)
    requires_portal = db.Column(db.Boolean, default=True)
    user_type = db.Column(db.String(20), default='client')
    
    # Availability
    status = db.Column(db.String(20), default='active')
    seasonal_start = db.Column(db.Date)
    seasonal_end = db.Column(db.Date)
    limited_time = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'package_code': self.package_code,
            'name': self.name,
            'description': self.description,
            'package_type_id': self.package_type_id,
            'package_type_name': self.package_type_ref.name if self.package_type_ref else None,
            'base_price': float(self.base_price),
            'discount_percentage': float(self.discount_percentage) if self.discount_percentage else 0,
            'final_price': float(self.final_price) if self.final_price else float(self.base_price),
            'estimated_duration': self.estimated_duration,
            'includes_materials': self.includes_materials,
            'requires_portal': self.requires_portal,
            'user_type': self.user_type,
            'status': self.status,
            'seasonal_start': self.seasonal_start.isoformat() if self.seasonal_start else None,
            'seasonal_end': self.seasonal_end.isoformat() if self.seasonal_end else None,
            'limited_time': self.limited_time,
            'display_order': self.display_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# Many-to-many relationship table for packages and services
package_services = db.Table('package_services',
    db.Column('package_id', db.Integer, db.ForeignKey('service_packages.id'), primary_key=True),
    db.Column('service_id', db.Integer, db.ForeignKey('service_types.id'), primary_key=True),
    db.Column('quantity', db.Integer, default=1),
    db.Column('custom_price', db.Numeric(10, 2))  # Override service price in package
)


class MembershipType(db.Model):
    __tablename__ = 'membership_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    membership_level = db.Column(db.String(50), nullable=False)  # basic, premium, enterprise
    billing_cycle = db.Column(db.String(20), default='monthly')  # monthly, quarterly, yearly
    
    # Pricing
    monthly_price = db.Column(db.Numeric(10, 2))
    yearly_price = db.Column(db.Numeric(10, 2))
    setup_fee = db.Column(db.Numeric(10, 2), default=0)
    
    # Benefits
    discount_percentage = db.Column(db.Numeric(5, 2), default=0)
    priority_booking = db.Column(db.Boolean, default=False)
    free_consultations = db.Column(db.Integer, default=0)
    emergency_service = db.Column(db.Boolean, default=False)
    
    # Limits
    monthly_service_limit = db.Column(db.Integer)  # NULL for unlimited
    max_project_value = db.Column(db.Numeric(10, 2))  # NULL for unlimited
    
    # Status
    status = db.Column(db.String(20), default='active')
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    memberships = db.relationship('Membership', backref='membership_type_ref', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'membership_level': self.membership_level,
            'billing_cycle': self.billing_cycle,
            'monthly_price': float(self.monthly_price) if self.monthly_price else None,
            'yearly_price': float(self.yearly_price) if self.yearly_price else None,
            'setup_fee': float(self.setup_fee) if self.setup_fee else 0,
            'discount_percentage': float(self.discount_percentage) if self.discount_percentage else 0,
            'priority_booking': self.priority_booking,
            'free_consultations': self.free_consultations,
            'emergency_service': self.emergency_service,
            'monthly_service_limit': self.monthly_service_limit,
            'max_project_value': float(self.max_project_value) if self.max_project_value else None,
            'status': self.status,
            'display_order': self.display_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'member_count': len(self.memberships)
        }


class Membership(db.Model):
    __tablename__ = 'memberships'
    
    id = db.Column(db.Integer, primary_key=True)
    membership_code = db.Column(db.String(20), unique=True, nullable=False)
    membership_type_id = db.Column(db.Integer, db.ForeignKey('membership_types.id'), nullable=False)
    
    # Client information
    client_name = db.Column(db.String(100), nullable=False)
    client_email = db.Column(db.String(120), nullable=False)
    client_phone = db.Column(db.String(20))
    
    # Membership status
    status = db.Column(db.String(20), default='active')  # active, paused, cancelled, expired
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    auto_renew = db.Column(db.Boolean, default=True)
    
    # Usage tracking
    services_used_this_month = db.Column(db.Integer, default=0)
    total_savings = db.Column(db.Numeric(10, 2), default=0)
    
    # Payment
    last_payment_date = db.Column(db.Date)
    next_payment_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'membership_code': self.membership_code,
            'membership_type_id': self.membership_type_id,
            'membership_type_name': self.membership_type_ref.name if self.membership_type_ref else None,
            'client_name': self.client_name,
            'client_email': self.client_email,
            'client_phone': self.client_phone,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'auto_renew': self.auto_renew,
            'services_used_this_month': self.services_used_this_month,
            'total_savings': float(self.total_savings) if self.total_savings else 0,
            'last_payment_date': self.last_payment_date.isoformat() if self.last_payment_date else None,
            'next_payment_date': self.next_payment_date.isoformat() if self.next_payment_date else None,
            'payment_method': self.payment_method,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'notes': self.notes
        }


# Add packages relationship to ServiceType
ServiceType.packages = db.relationship('ServicePackage',
                                     secondary=package_services,
                                     backref=db.backref('services', lazy='dynamic'))


class ServiceBooking(db.Model):
    __tablename__ = 'service_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_reference = db.Column(db.String(50), unique=True, nullable=False)
    service_type_id = db.Column(db.Integer, db.ForeignKey('service_types.id'), nullable=False)
    
    # Client information
    client_name = db.Column(db.String(100), nullable=False)
    client_email = db.Column(db.String(120))
    client_phone = db.Column(db.String(20))
    
    # Booking details
    scheduled_date = db.Column(db.Date)
    scheduled_time = db.Column(db.Time)
    estimated_duration = db.Column(db.Numeric(4, 1))  # in hours
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    
    # Pricing
    quoted_price = db.Column(db.Numeric(10, 2))
    final_price = db.Column(db.Numeric(10, 2))
    
    # Portal access
    portal_access_granted = db.Column(db.Boolean, default=False)
    client_id = db.Column(db.String(20))
    job_id = db.Column(db.String(20))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationship
    service_type = db.relationship('ServiceType', backref='bookings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'booking_reference': self.booking_reference,
            'service_type_id': self.service_type_id,
            'service_type_name': self.service_type.name if self.service_type else None,
            'client_name': self.client_name,
            'client_email': self.client_email,
            'client_phone': self.client_phone,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'estimated_duration': float(self.estimated_duration) if self.estimated_duration else None,
            'status': self.status,
            'quoted_price': float(self.quoted_price) if self.quoted_price else None,
            'final_price': float(self.final_price) if self.final_price else None,
            'portal_access_granted': self.portal_access_granted,
            'client_id': self.client_id,
            'job_id': self.job_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'notes': self.notes
        }