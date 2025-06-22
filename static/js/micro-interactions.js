/**
 * Micro-Interactions and Hover Effects JavaScript
 * Enhanced UI engagement for SPANKKS Construction
 */

class MicroInteractions {
    constructor() {
        this.observers = new Map();
        this.rippleElements = new Set();
        this.init();
    }

    init() {
        this.initScrollAnimations();
        this.initRippleEffects();
        this.initFormInteractions();
        this.initButtonAnimations();
        this.initCardAnimations();
        this.initNavigationEffects();
        this.initLoadingStates();
        this.initTooltipAnimations();
    }

    // =====================================================================
    // SCROLL-TRIGGERED ANIMATIONS
    // =====================================================================
    
    initScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    
                    // Trigger counter animations
                    if (entry.target.classList.contains('counter')) {
                        this.animateCounter(entry.target);
                    }
                    
                    // Stagger child animations
                    if (entry.target.classList.contains('stagger-children')) {
                        this.staggerChildAnimations(entry.target);
                    }
                }
            });
        }, observerOptions);

        // Add scroll animations to elements
        document.querySelectorAll('.fade-in-scroll, .counter, .stagger-children').forEach(el => {
            observer.observe(el);
        });

        this.observers.set('scroll', observer);
    }

    staggerChildAnimations(parent) {
        const children = parent.querySelectorAll('.stagger-item');
        children.forEach((child, index) => {
            setTimeout(() => {
                child.classList.add('animate-slideIn');
            }, index * 100);
        });
    }

    // =====================================================================
    // RIPPLE EFFECTS
    // =====================================================================
    
    initRippleEffects() {
        document.addEventListener('click', (e) => {
            const element = e.target.closest('.btn, .card, .ripple-effect');
            if (!element || element.disabled) return;

            this.createRipple(element, e);
        });
    }

    createRipple(element, event) {
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        const ripple = document.createElement('span');
        ripple.className = 'ripple';
        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: rippleAnimation 0.6s linear;
            left: ${x}px;
            top: ${y}px;
            width: ${size}px;
            height: ${size}px;
            pointer-events: none;
            z-index: 1000;
        `;

        if (!element.style.position || element.style.position === 'static') {
            element.style.position = 'relative';
        }
        element.style.overflow = 'hidden';

        element.appendChild(ripple);

        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.remove();
            }
        }, 600);
    }

    // =====================================================================
    // FORM INTERACTIONS
    // =====================================================================
    
    initFormInteractions() {
        // Floating labels
        document.querySelectorAll('.floating-label input, .floating-label textarea').forEach(input => {
            input.addEventListener('focus', () => {
                input.parentElement.classList.add('focused');
            });

            input.addEventListener('blur', () => {
                if (!input.value) {
                    input.parentElement.classList.remove('focused');
                }
            });

            // Check initial state
            if (input.value) {
                input.parentElement.classList.add('focused');
            }
        });

        // Form validation animations
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                this.animateFormValidation(form);
            });
        });

        // Input focus effects
        document.querySelectorAll('.form-control').forEach(input => {
            input.addEventListener('focus', () => {
                this.addInputFocusEffect(input);
            });

            input.addEventListener('blur', () => {
                this.removeInputFocusEffect(input);
            });
        });
    }

    addInputFocusEffect(input) {
        input.style.transform = 'scale(1.02)';
        input.style.borderColor = '#0d6efd';
        
        const label = input.previousElementSibling;
        if (label && label.tagName === 'LABEL') {
            label.style.color = '#0d6efd';
            label.style.fontWeight = '600';
        }
    }

    removeInputFocusEffect(input) {
        input.style.transform = 'scale(1)';
        
        const label = input.previousElementSibling;
        if (label && label.tagName === 'LABEL') {
            label.style.color = '';
            label.style.fontWeight = '';
        }
    }

    animateFormValidation(form) {
        const invalidInputs = form.querySelectorAll(':invalid');
        invalidInputs.forEach(input => {
            input.classList.add('shake');
            setTimeout(() => input.classList.remove('shake'), 500);
        });
    }

    // =====================================================================
    // BUTTON ANIMATIONS
    // =====================================================================
    
    initButtonAnimations() {
        document.querySelectorAll('.btn').forEach(button => {
            button.addEventListener('mouseenter', () => {
                this.addButtonHoverEffect(button);
            });

            button.addEventListener('mouseleave', () => {
                this.removeButtonHoverEffect(button);
            });

            button.addEventListener('click', () => {
                this.addButtonClickEffect(button);
            });
        });
    }

    addButtonHoverEffect(button) {
        if (button.classList.contains('btn-primary')) {
            button.style.transform = 'translateY(-2px)';
            button.style.boxShadow = '0 8px 25px rgba(13, 110, 253, 0.3)';
        }
    }

    removeButtonHoverEffect(button) {
        if (button.classList.contains('btn-primary')) {
            button.style.transform = '';
            button.style.boxShadow = '';
        }
    }

    addButtonClickEffect(button) {
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = '';
        }, 150);
    }

    // =====================================================================
    // CARD ANIMATIONS
    // =====================================================================
    
    initCardAnimations() {
        document.querySelectorAll('.card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                this.addCardHoverEffect(card);
            });

            card.addEventListener('mouseleave', () => {
                this.removeCardHoverEffect(card);
            });
        });
    }

    addCardHoverEffect(card) {
        card.style.transform = 'translateY(-10px) scale(1.02)';
        card.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.15)';
        
        // Animate service icons
        const icon = card.querySelector('.service-icon, .fa');
        if (icon) {
            icon.style.transform = 'scale(1.2) rotate(5deg)';
            icon.style.color = '#0d6efd';
        }
    }

    removeCardHoverEffect(card) {
        card.style.transform = '';
        card.style.boxShadow = '';
        
        const icon = card.querySelector('.service-icon, .fa');
        if (icon) {
            icon.style.transform = '';
            icon.style.color = '';
        }
    }

    // =====================================================================
    // NAVIGATION EFFECTS
    // =====================================================================
    
    initNavigationEffects() {
        // Navbar link animations
        document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
            link.addEventListener('mouseenter', () => {
                link.style.transform = 'translateY(-2px)';
                link.style.color = '#0d6efd';
            });

            link.addEventListener('mouseleave', () => {
                link.style.transform = '';
                link.style.color = '';
            });
        });

        // Logo animation
        const logo = document.querySelector('.navbar-brand img');
        if (logo) {
            logo.parentElement.addEventListener('mouseenter', () => {
                logo.style.transform = 'scale(1.1) rotate(5deg)';
            });

            logo.parentElement.addEventListener('mouseleave', () => {
                logo.style.transform = '';
            });
        }

        // Scroll-triggered navbar changes - DISABLED per user preference
        // User doesn't like navbar color changing on scroll
        /*
        let lastScroll = 0;
        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;
            const navbar = document.querySelector('.navbar');
            
            if (navbar) {
                if (currentScroll > 100) {
                    navbar.classList.add('scrolled');
                } else {
                    navbar.classList.remove('scrolled');
                }
            }
            
            lastScroll = currentScroll;
        });
        */
    }

    // =====================================================================
    // LOADING STATES
    // =====================================================================
    
    initLoadingStates() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    this.setLoadingState(submitBtn);
                }
            });
        });
    }

    setLoadingState(button) {
        button.disabled = true;
        button.classList.add('btn-loading');
        const originalText = button.innerHTML;
        button.setAttribute('data-original-text', originalText);
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';

        // Auto-reset after 10 seconds
        setTimeout(() => {
            this.resetLoadingState(button);
        }, 10000);
    }

    resetLoadingState(button) {
        button.disabled = false;
        button.classList.remove('btn-loading');
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.innerHTML = originalText;
        }
    }

    // =====================================================================
    // TOOLTIP ANIMATIONS
    // =====================================================================
    
    initTooltipAnimations() {
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            let tooltip = null;

            element.addEventListener('mouseenter', () => {
                tooltip = this.createTooltip(element, element.getAttribute('data-tooltip'));
            });

            element.addEventListener('mouseleave', () => {
                if (tooltip) {
                    tooltip.remove();
                    tooltip = null;
                }
            });
        });
    }

    createTooltip(element, text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'custom-tooltip';
        tooltip.textContent = text;
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 14px;
            pointer-events: none;
            z-index: 1000;
            animation: tooltipFadeIn 0.3s ease;
            white-space: nowrap;
        `;

        document.body.appendChild(tooltip);

        const rect = element.getBoundingClientRect();
        tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 8) + 'px';

        return tooltip;
    }

    // =====================================================================
    // COUNTER ANIMATIONS
    // =====================================================================
    
    animateCounter(element) {
        const target = parseInt(element.getAttribute('data-target') || element.textContent);
        const duration = parseInt(element.getAttribute('data-duration') || '2000');
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current);
        }, 16);
    }

    // =====================================================================
    // UTILITY METHODS
    // =====================================================================
    
    addPulseEffect(element) {
        element.classList.add('animate-pulse');
        setTimeout(() => {
            element.classList.remove('animate-pulse');
        }, 2000);
    }

    addBounceEffect(element) {
        element.classList.add('animate-bounce');
        setTimeout(() => {
            element.classList.remove('animate-bounce');
        }, 1000);
    }

    addShakeEffect(element) {
        element.classList.add('shake');
        setTimeout(() => {
            element.classList.remove('shake');
        }, 500);
    }

    // =====================================================================
    // CLEANUP
    // =====================================================================
    
    destroy() {
        this.observers.forEach(observer => observer.disconnect());
        this.observers.clear();
        this.rippleElements.clear();
    }
}

// Add CSS animations for shake effect
const shakeCSS = `
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

.shake {
    animation: shake 0.5s ease-in-out;
}

@keyframes tooltipFadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes rippleAnimation {
    to { transform: scale(4); opacity: 0; }
}

.navbar.scrolled {
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(10px);
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}
`;

// Inject CSS
const style = document.createElement('style');
style.textContent = shakeCSS;
document.head.appendChild(style);

// Initialize micro-interactions when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.microInteractions = new MicroInteractions();
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MicroInteractions;
}