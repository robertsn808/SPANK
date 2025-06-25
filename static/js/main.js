// SPANKKS Construction - Main JavaScript
console.log(`
🏗️ Spankks Construction
🏝️ Professional construction and home improvements across O'ahu
📞 Contact: (808) 778-9132
🌐 Licensed & Insured

Built with ❤️ for the local community
`);

// Global variables
let currentPage = 1;
let currentFilters = {
    quick: 'all',
    chips: {}
};
let sortConfig = {
    column: null,
    direction: 'asc'
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    console.log('Updating table with filters:', currentFilters, 'Sort:', sortConfig, 'Page:', currentPage);

    // Initialize mobile navigation
    initializeMobileNavigation();

    // Initialize dashboard widgets
    initializeDashboardWidgets();

    // Initialize form handlers
    initializeFormHandlers();

    // Initialize modal handlers
    initializeModalHandlers();

    // Initialize responsive features
    initializeResponsiveFeatures();

    console.log('✅ App initialized successfully');
}

// Mobile Navigation
function initializeMobileNavigation() {
    const mobileToggle = document.querySelector('.mobile-nav-toggle');
    const sidebar = document.querySelector('.sidebar');

    if (mobileToggle && sidebar) {
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.toggle('mobile-open');
        });

        // Close sidebar when clicking outside
        document.addEventListener('click', function(e) {
            if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target)) {
                sidebar.classList.remove('mobile-open');
            }
        });
    }
}

// Dashboard Widgets
function initializeDashboardWidgets() {
    // Auto-refresh functionality
    const refreshInterval = 30000; // 30 seconds

    if (window.location.pathname.includes('/admin/')) {
        setInterval(function() {
            updateDashboardMetrics();
        }, refreshInterval);
    }

    // Initialize quick action buttons
    const quickActions = document.querySelectorAll('.quick-action');
    quickActions.forEach(function(action) {
        action.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href !== '#') {
                window.location.href = href;
            }
        });
    });

    // Logo animation - disabled to prevent flashing
    const logo = document.querySelector('.navbar-brand img');
    if (logo) {
        // Ensure logo is always visible and stable
        logo.style.display = 'block';
        logo.style.opacity = '1';
        logo.style.visibility = 'visible';

        // Optional: Add subtle hover effect without transform
        logo.parentElement.addEventListener('mouseenter', () => {
            logo.style.filter = 'brightness(1.1)';
        });

        logo.parentElement.addEventListener('mouseleave', () => {
            logo.style.filter = '';
        });
    }
}

// Form Handlers
function initializeFormHandlers() {
    // Contact form
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            validateContactForm(e);
        });
    }

    // Consultation form
    const consultationForm = document.getElementById('consultationForm');
    if (consultationForm) {
        consultationForm.addEventListener('submit', function(e) {
            validateConsultationForm(e);
        });
    }

    // Quote form
    const quoteForm = document.getElementById('quoteForm');
    if (quoteForm) {
        quoteForm.addEventListener('submit', function(e) {
            validateQuoteForm(e);
        });
    }
}

// Modal Handlers
function initializeModalHandlers() {
    // Bootstrap modal events
    const modals = document.querySelectorAll('.modal');
    modals.forEach(function(modal) {
        modal.addEventListener('shown.bs.modal', function() {
            const firstInput = modal.querySelector('input:not([type="hidden"]), select, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });
}

// Responsive Features
function initializeResponsiveFeatures() {
    // Handle viewport changes
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            handleViewportChange();
        }, 250);
    });

    // Initial viewport check
    handleViewportChange();
}

function handleViewportChange() {
    const isMobile = window.innerWidth < 768;
    const dashboard = document.querySelector('.dashboard-content');

    if (dashboard) {
        if (isMobile) {
            dashboard.classList.add('mobile-view');
        } else {
            dashboard.classList.remove('mobile-view');
        }
    }
}

// Dashboard Metrics Update
function updateDashboardMetrics() {
    if (typeof fetch === 'undefined') {
        return; // Skip if fetch is not available
    }

    fetch('/api/dashboard/metrics')
        .then(function(response) {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Failed to fetch metrics');
        })
        .then(function(data) {
            updateMetricCards(data);
        })
        .catch(function(error) {
            console.log('Metrics update skipped:', error.message);
        });
}

function updateMetricCards(data) {
    // Update metric values if elements exist
    const elements = {
        totalRequests: document.querySelector('[data-metric="total-requests"]'),
        pendingRequests: document.querySelector('[data-metric="pending-requests"]'),
        totalMessages: document.querySelector('[data-metric="total-messages"]'),
        weekAppointments: document.querySelector('[data-metric="week-appointments"]')
    };

    Object.keys(elements).forEach(function(key) {
        const element = elements[key];
        if (element && data[key] !== undefined) {
            element.textContent = data[key];
        }
    });
}

// Form Validation Functions
function validateContactForm(e) {
    const form = e.target;
    const name = form.querySelector('[name="contact_name"]');
    const email = form.querySelector('[name="contact_email"]');
    const message = form.querySelector('[name="contact_message"]');

    let isValid = true;
    const errors = [];

    if (!name || !name.value.trim()) {
        errors.push('Name is required');
        isValid = false;
    }

    if (!email || !email.value.trim()) {
        errors.push('Email is required');
        isValid = false;
    } else if (!isValidEmail(email.value)) {
        errors.push('Please enter a valid email address');
        isValid = false;
    }

    if (!message || !message.value.trim()) {
        errors.push('Message is required');
        isValid = false;
    }

    if (!isValid) {
        e.preventDefault();
        showValidationErrors(errors);
    }
}

function validateConsultationForm(e) {
    const form = e.target;
    const name = form.querySelector('[name="name"]');
    const email = form.querySelector('[name="email"]');
    const phone = form.querySelector('[name="phone"]');
    const service = form.querySelector('[name="service"]');

    let isValid = true;
    const errors = [];

    if (!name || !name.value.trim()) {
        errors.push('Name is required');
        isValid = false;
    }

    if (!email || !email.value.trim()) {
        errors.push('Email is required');
        isValid = false;
    } else if (!isValidEmail(email.value)) {
        errors.push('Please enter a valid email address');
        isValid = false;
    }

    if (!phone || !phone.value.trim()) {
        errors.push('Phone number is required');
        isValid = false;
    }

    if (!service || !service.value) {
        errors.push('Please select a service');
        isValid = false;
    }

    if (!isValid) {
        e.preventDefault();
        showValidationErrors(errors);
    }
}

function validateQuoteForm(e) {
    const form = e.target;
    const customer = form.querySelector('[name="customer"]');
    const phone = form.querySelector('[name="phone"]');
    const serviceType = form.querySelector('[name="serviceType"]');
    const price = form.querySelector('[name="price"]');

    let isValid = true;
    const errors = [];

    if (!customer || !customer.value.trim()) {
        errors.push('Customer name is required');
        isValid = false;
    }

    if (!phone || !phone.value.trim()) {
        errors.push('Phone number is required');
        isValid = false;
    }

    if (!serviceType || !serviceType.value.trim()) {
        errors.push('Service type is required');
        isValid = false;
    }

    if (!price || !price.value || isNaN(parseFloat(price.value))) {
        errors.push('Valid price is required');
        isValid = false;
    }

    if (!isValid) {
        e.preventDefault();
        showValidationErrors(errors);
    }
}

// Utility Functions
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showValidationErrors(errors) {
    let errorMessage = 'Please correct the following errors:\n\n';
    errors.forEach(function(error) {
        errorMessage += '• ' + error + '\n';
    });
    alert(errorMessage);
}

// API Helper Functions
function makeRequest(url, options) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };

    const finalOptions = Object.assign({}, defaultOptions, options || {});

    return fetch(url, finalOptions)
        .then(function(response) {
            if (!response.ok) {
                throw new Error('Request failed: ' + response.status);
            }
            return response.json();
        });
}

// Admin-specific functions
function viewBooking(bookingId) {
    if (confirm('View booking details for ID: ' + bookingId + '?')) {
        window.location.href = '/admin/booking/' + bookingId;
    }
}

function updateStatus(bookingId) {
    const newStatus = prompt('Enter new status (pending, confirmed, completed, cancelled):');
    if (newStatus && ['pending', 'confirmed', 'completed', 'cancelled'].includes(newStatus.toLowerCase())) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/admin/booking/' + bookingId + '/update';

        const statusInput = document.createElement('input');
        statusInput.type = 'hidden';
        statusInput.name = 'status';
        statusInput.value = newStatus.toLowerCase();

        form.appendChild(statusInput);
        document.body.appendChild(form);
        form.submit();
    }
}

function viewMessage(messageId) {
    if (confirm('View message details for ID: ' + messageId + '?')) {
        window.location.href = '/admin/message/' + messageId;
    }
}

function markRead(messageId) {
    if (confirm('Mark message as read?')) {
        window.location.href = '/admin/message/' + messageId + '/read';
    }
}

function markNotificationComplete(notificationId) {
    if (confirm('Mark this notification as complete?')) {
        makeRequest('/admin/notifications/' + notificationId + '/complete', {
            method: 'POST'
        })
        .then(function(data) {
            if (data.success) {
                location.reload();
            } else {
                alert('Error: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(function(error) {
            alert('Error: ' + error.message);
        });
    }
}

// Health check function
function performHealthCheck() {
    makeRequest('/api/health-check')
        .then(function(data) {
            console.log('Health check passed:', data);
        })
        .catch(function(error) {
            console.log('Health check failed:', error.message);
        });
}

// Auto-refresh dashboard functionality
function refreshDashboard() {
    if (window.location.pathname.includes('/admin/dashboard')) {
        location.reload();
    }
}

// Initialize auto-refresh every 60 seconds for admin dashboard
if (window.location.pathname.includes('/admin/dashboard')) {
    setInterval(refreshDashboard, 60000);
}

// Export functions for global access
window.spankksApp = {
    viewBooking: viewBooking,
    updateStatus: updateStatus,
    viewMessage: viewMessage,
    markRead: markRead,
    markNotificationComplete: markNotificationComplete,
    refreshDashboard: refreshDashboard,
    performHealthCheck: performHealthCheck
};