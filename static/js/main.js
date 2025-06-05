/**
 * Main JavaScript file for Triton Concrete Coating Website
 * Handles interactive features, form validation, and user experience enhancements
 */

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Main initialization function
 */
function initializeApp() {
    try {
        // Core functionality first
        initSmoothScrolling();
        initFormValidation();
        initLoadingStates();
        initNavbarBehavior();
        
        // UI enhancements
        initAnimations();
        initGalleryInteractions();
        
        // Form enhancements
        initContactFormEnhancements();
        initConsultationFormEnhancements();
        
        // Admin features (if present)
        initAdminDashboardFeatures();
        
        // Accessibility and performance
        initAccessibilityFeatures();
        initPerformanceOptimizations();
        
        // Mobile-specific optimizations
        initMobileOptimizations();
        
        console.log('✅ App initialized successfully');
    } catch (error) {
        console.error('❌ Error initializing app:', error);
        // Fallback: ensure basic functionality works
        try {
            initSmoothScrolling();
            initFormValidation();
        } catch (fallbackError) {
            console.error('❌ Critical error in fallback initialization:', fallbackError);
        }
    }
}

/**
 * Mobile-specific optimizations
 */
function initMobileOptimizations() {
    // Improve touch responsiveness
    document.addEventListener('touchstart', function() {}, { passive: true });
    
    // Optimize scroll performance on mobile
    let ticking = false;
    function updateOnScroll() {
        updateNavbarOnScroll();
        ticking = false;
    }
    
    document.addEventListener('scroll', function() {
        if (!ticking) {
            requestAnimationFrame(updateOnScroll);
            ticking = true;
        }
    }, { passive: true });
    
    // Handle orientation changes
    window.addEventListener('orientationchange', function() {
        setTimeout(() => {
            handleResponsiveChanges();
        }, 100);
    });
    
    // Improve form experience on mobile
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        // Prevent zoom on focus for iOS
        if (input.type !== 'file') {
            input.addEventListener('focus', function() {
                if (window.innerWidth <= 768) {
                    this.style.fontSize = '16px';
                }
            });
        }
    });
}

/**
 * Initialize animations
 */
function initAnimations() {
    // Add scroll animations or other UI animations here
}

/**
 * Initialize navbar behavior
 */
function initNavbarBehavior() {
    const navbar = document.querySelector('.navbar');
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (!navbar) return;
    
    let lastScrollTop = 0;
    
    // Enhanced scroll behavior
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Add shadow when scrolled
        if (scrollTop > 10) {
            navbar.classList.add('shadow');
        } else {
            navbar.classList.remove('shadow');
        }
        
        // Hide navbar on scroll down (mobile only)
        if (window.innerWidth <= 768) {
            if (scrollTop > lastScrollTop && scrollTop > 100) {
                navbar.style.transform = 'translateY(-100%)';
            } else {
                navbar.style.transform = 'translateY(0)';
            }
        }
        
        lastScrollTop = scrollTop;
    });
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (navbarCollapse && navbarCollapse.classList.contains('show')) {
            if (!navbar.contains(e.target)) {
                const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                    toggle: false
                });
                bsCollapse.hide();
            }
        }
    });
    
    // Close mobile menu when clicking on nav links
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                    toggle: false
                });
                bsCollapse.hide();
            }
        });
    });
    
    // Smooth transition for navbar
    navbar.style.transition = 'transform 0.3s ease-in-out, box-shadow 0.3s ease';
}

/**
 * Initialize gallery interactions
 */
function initGalleryInteractions() {
    // Add gallery lightbox or image interactions
}

/**
 * Initialize contact form enhancements
 */
function initContactFormEnhancements() {
    // Add contact form specific enhancements
}

/**
 * Initialize admin dashboard features
 */
function initAdminDashboardFeatures() {
    // Add admin dashboard specific JavaScript features
}

/**
 * Initialize accessibility features
 */
function initAccessibilityFeatures() {
    // Add accessibility enhancements
}

/**
 * Initialize performance optimizations
 */
function initPerformanceOptimizations() {
    // Add performance optimizations like lazy loading
}

/**
 * Smooth scrolling for anchor links
 */
function initSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Enhanced form validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
    });
}

/**
 * Validate individual form field
 */
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required';
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }
    }
    
    // Phone validation
    if (field.type === 'tel' && value) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        const cleanPhone = value.replace(/[\s\-\(\)\.]/g, '');
        if (!phoneRegex.test(cleanPhone)) {
            isValid = false;
            errorMessage = 'Please enter a valid phone number';
        }
    }
    
    // Date validation (not in the past)
    if (field.type === 'date' && value) {
        const selectedDate = new Date(value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        if (selectedDate < today) {
            isValid = false;
            errorMessage = 'Please select a future date';
        }
    }
    
    if (!isValid) {
        showFieldError(field, errorMessage);
    } else {
        clearFieldError(field);
    }
    
    return isValid;
}

/**
 * Validate entire form
 */
function validateForm(form) {
    const fields = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    fields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Show field error
 */
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

/**
 * Clear field error
 */
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

/**
 * Loading states for forms and buttons
 */
function initLoadingStates() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && validateForm(this)) {
                setLoadingState(submitBtn);
            }
        });
    });
}

/**
 * Set button loading state
 */
function setLoadingState(button) {
    const originalText = button.textContent;
    button.disabled = true;
    button.setAttribute('data-original-text', originalText);
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
    
    // Reset after 10 seconds as fallback
    setTimeout(() => {
        resetLoadingState(button);
    }, 10000);
}

/**
 * Reset button loading state
 */
function resetLoadingState(button) {
    button.disabled = false;
    button.classList.remove('btn-loading');
    
    const originalText = button.getAttribute('data-original-text');
    if (originalText) {
        button.innerHTML = originalText;
    }
}

/**
 * Initialize scroll animations
 */
function initAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observe elements to animate
    const animateElements = document.querySelectorAll('.card, .service-card, .feature-icon, .gallery-item');
    animateElements.forEach(el => {
        observer.observe(el);
    });
}

/**
 * Navbar behavior on scroll
 */
function initNavbarBehavior() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    let lastScrollTop = 0;
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Add shadow when scrolled
        if (scrollTop > 10) {
            navbar.classList.add('shadow');
        } else {
            navbar.classList.remove('shadow');
        }
        
        lastScrollTop = scrollTop;
    });
}

/**
 * Enhanced gallery interactions
 */
function initGalleryInteractions() {
    // Gallery filter functionality (enhanced version)
    const filterButtons = document.querySelectorAll('[data-filter]');
    const galleryItems = document.querySelectorAll('.gallery-item');
    
    if (filterButtons.length === 0) return;
    
    filterButtons.forEach(button => {
        // Add touch-friendly events
        ['click', 'touchend'].forEach(event => {
            button.addEventListener(event, function(e) {
                e.preventDefault();
                const filter = this.getAttribute('data-filter');
                
                try {
                    // Update active button with animation
                    filterButtons.forEach(btn => {
                        btn.classList.remove('active');
                        btn.style.transform = 'scale(1)';
                    });
                    
                    this.classList.add('active');
                    this.style.transform = 'scale(1.05)';
                    
                    // Filter gallery items with animation
                    galleryItems.forEach((item, index) => {
                        const category = item.getAttribute('data-category');
                        const shouldShow = filter === 'all' || category === filter;
                        
                        if (shouldShow) {
                            setTimeout(() => {
                                item.style.display = 'block';
                                item.style.opacity = '0';
                                item.style.transform = 'translateY(20px)';
                                
                                setTimeout(() => {
                                    item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                                    item.style.opacity = '1';
                                    item.style.transform = 'translateY(0)';
                                }, 50);
                            }, index * 50);
                        } else {
                            item.style.opacity = '0';
                            item.style.transform = 'translateY(-20px)';
                            setTimeout(() => {
                                item.style.display = 'none';
                            }, 300);
                        }
                    });
                    
                    // Announce filter change to screen readers
                    announceToScreenReader(`Showing ${filter === 'all' ? 'all' : filter} gallery items`);
                } catch (error) {
                    console.error('Error filtering gallery:', error);
                }
            });
        });
    });
    
    // Gallery image modal functionality
    initGalleryModal();
}

/**
 * Gallery modal for image viewing
 */
function initGalleryModal() {
    const galleryImages = document.querySelectorAll('.gallery-card img');
    
    galleryImages.forEach(img => {
        img.addEventListener('click', function() {
            createImageModal(this);
        });
        
        // Add cursor pointer
        img.style.cursor = 'pointer';
    });
}

/**
 * Create modal for gallery image
 */
function createImageModal(img) {
    try {
        // Create modal elements
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.setAttribute('tabindex', '-1');
        modal.setAttribute('aria-labelledby', 'imageModalLabel');
        modal.setAttribute('aria-hidden', 'true');
        
        const modalSize = window.innerWidth <= 768 ? 'modal-fullscreen-sm-down' : 'modal-lg';
        
        modal.innerHTML = `
            <div class="modal-dialog ${modalSize} modal-dialog-centered">
                <div class="modal-content bg-dark">
                    <div class="modal-header border-0">
                        <h5 class="modal-title text-white" id="imageModalLabel">${img.alt || 'Gallery Image'}</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body text-center p-0">
                        <img src="${img.src}" alt="${img.alt || 'Gallery Image'}" class="img-fluid" 
                             style="max-height: 80vh; width: auto; object-fit: contain;"
                             onerror="this.onerror=null; this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2VlZSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LXNpemU9IjE4IiBmaWxsPSIjYWFhIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+SW1hZ2UgTm90IEZvdW5kPC90ZXh0Pjwvc3ZnPg==';">
                        <div class="p-3">
                            <small class="text-muted d-block mt-2">Tap outside or press ESC to close</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Show modal with error handling
        const bsModal = new bootstrap.Modal(modal, {
            backdrop: true,
            keyboard: true,
            focus: true
        });
        
        bsModal.show();
        
        // Mobile-friendly: Close on swipe down
        if (window.innerWidth <= 768) {
            let startY = 0;
            const modalContent = modal.querySelector('.modal-content');
            
            modalContent.addEventListener('touchstart', function(e) {
                startY = e.touches[0].clientY;
            });
            
            modalContent.addEventListener('touchmove', function(e) {
                const currentY = e.touches[0].clientY;
                const diff = currentY - startY;
                
                if (diff > 100) { // Swipe down threshold
                    bsModal.hide();
                }
            });
        }
        
        // Remove modal from DOM when hidden
        modal.addEventListener('hidden.bs.modal', function() {
            try {
                document.body.removeChild(modal);
            } catch (e) {
                console.warn('Modal already removed from DOM');
            }
        });
        
        // Handle image load errors
        const modalImg = modal.querySelector('img');
        modalImg.addEventListener('error', function() {
            console.warn('Gallery image failed to load:', img.src);
            announceToScreenReader('Image could not be loaded');
        });
        
    } catch (error) {
        console.error('Error creating image modal:', error);
        announceToScreenReader('Unable to open image viewer');
    }
}

/**
 * Enhanced contact form features
 */
function initContactFormEnhancements() {
    const contactForm = document.querySelector('#contact_message');
    if (!contactForm) return;
    
    // Auto-resize textarea
    contactForm.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
    
    // Character counter for message field
    if (contactForm.hasAttribute('maxlength')) {
        addCharacterCounter(contactForm);
    }
}

/**
 * Enhanced consultation form features
 */
function initConsultationFormEnhancements() {
    const consultationForm = document.querySelector('form[action*="consultation"]');
    if (!consultationForm) return;
    
    // Service-specific field visibility
    const serviceSelect = consultationForm.querySelector('#service');
    if (serviceSelect) {
        serviceSelect.addEventListener('change', function() {
            handleServiceChange(this.value);
        });
    }
    
    // Auto-fill preferred date with next business day
    const dateInput = consultationForm.querySelector('#preferred_date');
    if (dateInput && !dateInput.value) {
        const nextBusinessDay = getNextBusinessDay();
        dateInput.value = nextBusinessDay.toISOString().split('T')[0];
    }
    
    // Phone number formatting
    const phoneInput = consultationForm.querySelector('#phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            formatPhoneNumber(this);
        });
    }
}

/**
 * Handle service selection changes
 */
function handleServiceChange(serviceValue) {
    // Add service-specific field logic here if needed
    console.log('Service changed to:', serviceValue);
}

/**
 * Get next business day
 */
function getNextBusinessDay() {
    const date = new Date();
    date.setDate(date.getDate() + 1);
    
    // Skip weekends
    while (date.getDay() === 0 || date.getDay() === 6) {
        date.setDate(date.getDate() + 1);
    }
    
    return date;
}

/**
 * Format phone number
 */
function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length >= 6) {
        value = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
    } else if (value.length >= 3) {
        value = value.replace(/(\d{3})(\d{3})/, '($1) $2');
    }
    input.value = value;
}


function handleServiceChange(service) {
    // Add service-specific tips or requirements
    const serviceInfo = {
        'garage-floor': 'Tip: Measure your garage for accurate pricing',
        'outdoor-concrete': 'Note: Weather conditions may affect scheduling',
        'industrial-epoxy': 'Info: Site assessment required for industrial projects',
        'decorative-concrete': 'Design consultation available for custom patterns'
    };
    
    // Remove existing service tips
    const existingTip = document.querySelector('.service-tip');
    if (existingTip) {
        existingTip.remove();
    }
    
    // Add new service tip
    if (serviceInfo[service]) {
        const serviceSelect = document.querySelector('#service');
        const tipDiv = document.createElement('div');
        tipDiv.className = 'service-tip alert alert-info mt-2';
        tipDiv.innerHTML = `<i class="fas fa-info-circle me-2"></i>${serviceInfo[service]}`;
        
        serviceSelect.parentNode.appendChild(tipDiv);
    }
}

/**
 * Get next business day
 */
function getNextBusinessDay() {
    const today = new Date();
    let nextDay = new Date(today);
    nextDay.setDate(today.getDate() + 1);
    
    // Skip weekends
    while (nextDay.getDay() === 0 || nextDay.getDay() === 6) {
        nextDay.setDate(nextDay.getDate() + 1);
    }
    
    return nextDay;
}

/**
 * Format phone number input
 */
function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    
    if (value.length >= 10) {
        if (value.startsWith('1') && value.length === 11) {
            value = value.substring(1);
        }
        
        const formatted = `(${value.substring(0, 3)}) ${value.substring(3, 6)}-${value.substring(6, 10)}`;
        input.value = formatted;
    }
}

/**
 * Add character counter to textarea
 */
function addCharacterCounter(textarea) {
    const maxLength = parseInt(textarea.getAttribute('maxlength'));
    
    const counter = document.createElement('div');
    counter.className = 'character-counter text-muted small mt-1';
    
    function updateCounter() {
        const remaining = maxLength - textarea.value.length;
        counter.textContent = `${remaining} characters remaining`;
        
        if (remaining < 50) {
            counter.classList.add('text-warning');
        } else {
            counter.classList.remove('text-warning');
        }
    }
    
    textarea.addEventListener('input', updateCounter);
    textarea.parentNode.appendChild(counter);
    updateCounter();
}

/**
 * Admin dashboard enhancements
 */
function initAdminDashboardFeatures() {
    // Auto-refresh dashboard data
    if (window.location.pathname.includes('/admin/dashboard')) {
        initDashboardAutoRefresh();
        initBookingSearch();
        initBookingFilters();
    }
}

/**
 * Dashboard auto-refresh
 */
function initDashboardAutoRefresh() {
    // Refresh every 5 minutes
    setInterval(() => {
        const bookingsTable = document.querySelector('.table-responsive');
        if (bookingsTable) {
            // Add subtle loading indicator
            const loadingIndicator = document.createElement('div');
            loadingIndicator.className = 'position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-white bg-opacity-75';
            loadingIndicator.innerHTML = '<div class="spinner-border text-primary" role="status"></div>';
            
            bookingsTable.style.position = 'relative';
            bookingsTable.appendChild(loadingIndicator);
            
            // Simulate refresh (in real app, this would be an AJAX call)
            setTimeout(() => {
                loadingIndicator.remove();
            }, 1000);
        }
    }, 300000); // 5 minutes
}

/**
 * Booking search functionality
 */
function initBookingSearch() {
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'form-control mb-3';
    searchInput.placeholder = 'Search bookings by name, email, or service...';
    
    const tableContainer = document.querySelector('.table-responsive');
    if (tableContainer) {
        tableContainer.parentNode.insertBefore(searchInput, tableContainer);
        
        searchInput.addEventListener('input', function() {
            filterBookings(this.value);
        });
    }
}

/**
 * Filter bookings based on search term
 */
function filterBookings(searchTerm) {
    const rows = document.querySelectorAll('tbody tr');
    const term = searchTerm.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(term) || term === '') {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * Booking status filters
 */
function initBookingFilters() {
    const filterButtons = document.createElement('div');
    filterButtons.className = 'btn-group mb-3';
    filterButtons.innerHTML = `
        <button type="button" class="btn btn-outline-secondary active" data-status="all">All</button>
        <button type="button" class="btn btn-outline-warning" data-status="pending">Pending</button>
        <button type="button" class="btn btn-outline-success" data-status="confirmed">Confirmed</button>
        <button type="button" class="btn btn-outline-info" data-status="completed">Completed</button>
    `;
    
    const tableContainer = document.querySelector('.table-responsive');
    if (tableContainer) {
        tableContainer.parentNode.insertBefore(filterButtons, tableContainer);
        
        filterButtons.addEventListener('click', function(e) {
            if (e.target.matches('button[data-status]')) {
                const status = e.target.getAttribute('data-status');
                
                // Update active button
                filterButtons.querySelectorAll('button').forEach(btn => {
                    btn.classList.remove('active');
                });
                e.target.classList.add('active');
                
                // Filter by status
                filterBookingsByStatus(status);
            }
        });
    }
}

/**
 * Filter bookings by status
 */
function filterBookingsByStatus(status) {
    const rows = document.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        if (status === 'all') {
            row.style.display = '';
        } else {
            const statusBadge = row.querySelector('.badge');
            if (statusBadge && statusBadge.textContent.toLowerCase() === status) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
}

/**
 * Accessibility enhancements
 */
function initAccessibilityFeatures() {
    // Skip to main content link
    addSkipLink();
    
    // Focus management for modals
    initFocusManagement();
    
    // Keyboard navigation improvements
    initKeyboardNavigation();
    
    // ARIA live regions for dynamic content
    initAriaLiveRegions();
}

/**
 * Add skip to main content link
 */
function addSkipLink() {
    const skipLink = document.createElement('a');
    skipLink.href = '#main';
    skipLink.className = 'sr-only sr-only-focusable position-absolute top-0 start-0 z-index-1060 btn btn-primary';
    skipLink.textContent = 'Skip to main content';
    
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    const main = document.querySelector('main');
    if (main && !main.id) {
        main.id = 'main';
    }
}

/**
 * Focus management for better accessibility
 */
function initFocusManagement() {
    // Trap focus in modals
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            const modal = document.querySelector('.modal.show');
            if (modal) {
                trapFocus(e, modal);
            }
        }
    });
}

/**
 * Trap focus within an element
 */
function trapFocus(e, container) {
    const focusableElements = container.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];
    
    if (e.shiftKey) {
        if (document.activeElement === firstFocusable) {
            lastFocusable.focus();
            e.preventDefault();
        }
    } else {
        if (document.activeElement === lastFocusable) {
            firstFocusable.focus();
            e.preventDefault();
        }
    }
}

/**
 * Enhanced keyboard navigation
 */
function initKeyboardNavigation() {
    // ESC key to close modals and dropdowns
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            // Close open modals
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const bsModal = bootstrap.Modal.getInstance(openModal);
                if (bsModal) {
                    bsModal.hide();
                }
            }
            
            // Close open dropdowns
            const openDropdown = document.querySelector('.dropdown-menu.show');
            if (openDropdown) {
                const dropdown = bootstrap.Dropdown.getInstance(openDropdown.previousElementSibling);
                if (dropdown) {
                    dropdown.hide();
                }
            }
        }
    });
}

/**
 * ARIA live regions for dynamic content updates
 */
function initAriaLiveRegions() {
    // Create live region for status updates
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.className = 'sr-only';
    liveRegion.id = 'live-region';
    
    document.body.appendChild(liveRegion);
}

/**
 * Announce message to screen readers
 */
function announceToScreenReader(message) {
    const liveRegion = document.getElementById('live-region');
    if (liveRegion) {
        liveRegion.textContent = message;
        
        // Clear after announcement
        setTimeout(() => {
            liveRegion.textContent = '';
        }, 1000);
    }
}

/**
 * Performance optimizations
 */
function initPerformanceOptimizations() {
    // Lazy load images
    initLazyLoading();
    
    // Debounce scroll and resize events
    initEventDebouncing();
    
    // Preload critical resources
    preloadCriticalResources();
}

/**
 * Lazy loading for images
 */
function initLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

/**
 * Debounce events for better performance
 */
function initEventDebouncing() {
    let scrollTimeout;
    let resizeTimeout;
    
    // Debounced scroll handler
    window.addEventListener('scroll', function() {
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        
        scrollTimeout = setTimeout(() => {
            // Handle scroll events here
            updateNavbarOnScroll();
        }, 10);
    });
    
    // Debounced resize handler
    window.addEventListener('resize', function() {
        if (resizeTimeout) {
            clearTimeout(resizeTimeout);
        }
        
        resizeTimeout = setTimeout(() => {
            // Handle resize events here
            handleResponsiveChanges();
        }, 250);
    });
}

/**
 * Update navbar appearance on scroll
 */
function updateNavbarOnScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    if (scrollTop > 100) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
}

/**
 * Handle responsive layout changes
 */
function handleResponsiveChanges() {
    // Adjust gallery grid on resize
    const galleryItems = document.querySelectorAll('.gallery-item');
    if (galleryItems.length > 0) {
        // Force reflow for masonry-like layouts
        galleryItems.forEach(item => {
            item.style.opacity = '0';
            setTimeout(() => {
                item.style.opacity = '1';
            }, 50);
        });
    }
}

/**
 * Preload critical resources
 */
function preloadCriticalResources() {
    const criticalImages = [
        'https://pixabay.com/get/g5eef83515dd5beb58efc3b1c09a62690532a181d42cd0a1f8f9a5e76fc032cbe610d30f88cd10b817faee64afb4b868e62f1b25ac05c78a4ba69e3cac8d6554f_1280.jpg'
    ];
    
    criticalImages.forEach(src => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'image';
        link.href = src;
        document.head.appendChild(link);
    });
}

/**
 * Utility function to format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Utility function to format date
 */
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

/**
 * Console welcome message
 */
console.log(`
🌺 Triton Concrete Coating Website
🏝️ Serving O'ahu with professional concrete coating solutions
📞 Contact: (808) 599-0908
🌐 Licensed & Insured

Built with ❤️ for the local community
`);
