/**
 * Contextual Help Tooltips with Playful Illustrations
 * Interactive help system for SPANKKS Construction admin dashboard
 */

class ContextualTooltips {
    constructor() {
        this.activeTooltips = new Map();
        this.tooltipData = new Map();
        this.defaultDelay = 500;
        this.hideDelay = 300;
        this.init();
    }

    init() {
        this.loadTooltipData();
        this.bindEvents();
        this.createTooltipContainer();
    }

    loadTooltipData() {
        // Define help content for different elements
        this.tooltipData = new Map([
            // Dashboard elements
            ['quote-builder', {
                title: 'Quote Builder',
                content: 'Create professional quotes for customers with automatic Hawaii tax calculations and service templates.',
                illustration: 'quote',
                position: 'bottom',
                theme: 'info'
            }],
            ['scheduler', {
                title: 'Appointment Scheduler',
                content: 'Manage appointments and view the weekly schedule. Click on time slots to add new appointments.',
                illustration: 'calendar',
                position: 'bottom',
                theme: 'success'
            }],
            ['customer-management', {
                title: 'Customer Management',
                content: 'View all customers, their project history, and manage contact information. Track customer lifetime value.',
                illustration: 'customer',
                position: 'bottom',
                theme: 'info'
            }],
            ['analytics-dashboard', {
                title: 'Business Analytics',
                content: 'View comprehensive business insights including revenue metrics, customer trends, and performance analytics.',
                illustration: 'analytics',
                position: 'bottom',
                theme: 'success'
            }],
            ['staff-management', {
                title: 'Staff Management',
                content: 'Manage staff schedules, assign jobs, and track team availability and performance.',
                illustration: 'tools',
                position: 'bottom',
                theme: 'info'
            }],
            ['inventory-dashboard', {
                title: 'Inventory Management',
                content: 'Track materials, monitor stock levels, and manage supplier information for projects.',
                illustration: 'tools',
                position: 'bottom',
                theme: 'warning'
            }],
            ['notification-center', {
                title: 'Notification Center',
                content: 'Stay updated with customer inquiries, appointment reminders, and system alerts.',
                illustration: 'notification',
                position: 'left',
                theme: 'info'
            }],
            // Form elements
            ['hawaii-tax', {
                title: 'Hawaii GET Tax',
                content: 'Automatically calculated at 4.712% for O\'ahu. This field updates automatically when you change the subtotal.',
                illustration: 'quote',
                position: 'top',
                theme: 'info'
            }],
            ['service-type', {
                title: 'Service Categories',
                content: 'Select the type of service to apply appropriate templates and pricing. Custom options are available for unique projects.',
                illustration: 'tools',
                position: 'right',
                theme: 'info'
            }],
            ['appointment-status', {
                title: 'Appointment Status',
                content: 'Track appointment progress: Pending (new), Confirmed (scheduled), Completed (finished), or Cancelled.',
                illustration: 'calendar',
                position: 'top',
                theme: 'success'
            }],
            // Quick Actions
            ['quick-actions-toggle', {
                title: 'Quick Actions Menu',
                content: 'Access all major business functions quickly. Organized by Core Business, Operations, Analytics, and Advanced Tools.',
                illustration: 'tools',
                position: 'left',
                theme: 'success'
            }],
            ['weekly-schedule', {
                title: 'Weekly Schedule View',
                content: 'Your main dashboard showing this week\'s appointments. Click on any day or time slot to manage appointments.',
                illustration: 'calendar',
                position: 'top',
                theme: 'success'
            }]
        ]);
    }

    createTooltipContainer() {
        if (document.getElementById('tooltip-container')) return;
        
        const container = document.createElement('div');
        container.id = 'tooltip-container';
        container.style.position = 'absolute';
        container.style.top = '0';
        container.style.left = '0';
        container.style.pointerEvents = 'none';
        container.style.zIndex = '1060';
        document.body.appendChild(container);
    }

    bindEvents() {
        // Handle help trigger buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.help-trigger') || e.target.closest('.help-trigger')) {
                e.preventDefault();
                e.stopPropagation();
                const trigger = e.target.closest('.help-trigger') || e.target;
                this.toggleTooltip(trigger);
            }
        });

        // Handle hover events for elements with data-help attribute
        document.addEventListener('mouseenter', (e) => {
            const helpElement = e.target.closest('[data-help]');
            if (helpElement && !helpElement.hasAttribute('data-help-click-only')) {
                this.showTooltip(helpElement, true);
            }
        }, true);

        document.addEventListener('mouseleave', (e) => {
            const helpElement = e.target.closest('[data-help]');
            if (helpElement && !helpElement.hasAttribute('data-help-click-only')) {
                this.hideTooltip(helpElement);
            }
        }, true);

        // Handle click events for click-only tooltips
        document.addEventListener('click', (e) => {
            const helpElement = e.target.closest('[data-help][data-help-click-only]');
            if (helpElement) {
                e.preventDefault();
                this.toggleTooltip(helpElement);
            }
        });

        // Hide tooltips when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.contextual-tooltip') && !e.target.closest('[data-help]') && !e.target.closest('.help-trigger')) {
                this.hideAllTooltips();
            }
        });

        // Handle escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideAllTooltips();
            }
        });
    }

    showTooltip(element, isHover = false) {
        const helpKey = element.getAttribute('data-help');
        const customContent = element.getAttribute('data-help-content');
        const customPosition = element.getAttribute('data-help-position');
        const customTheme = element.getAttribute('data-help-theme');

        let tooltipConfig = this.tooltipData.get(helpKey);
        
        // Use custom content if provided
        if (customContent) {
            tooltipConfig = {
                title: element.getAttribute('data-help-title') || 'Help',
                content: customContent,
                illustration: element.getAttribute('data-help-illustration') || 'tools',
                position: customPosition || 'top',
                theme: customTheme || 'info'
            };
        }

        if (!tooltipConfig) {
            console.warn(`No tooltip configuration found for: ${helpKey}`);
            return;
        }

        // Don't show hover tooltips if there's already a click tooltip
        if (isHover && this.activeTooltips.has(element) && this.activeTooltips.get(element).isClickTooltip) {
            return;
        }

        this.hideTooltip(element);

        const tooltip = this.createTooltipElement(tooltipConfig);
        tooltip.isClickTooltip = !isHover;
        
        this.positionTooltip(tooltip, element, tooltipConfig.position);
        this.activeTooltips.set(element, tooltip);

        // Add to container
        document.getElementById('tooltip-container').appendChild(tooltip);

        // Show with animation
        requestAnimationFrame(() => {
            tooltip.classList.add('show');
            if (!isHover) {
                tooltip.classList.add('bounce');
            }
        });

        // Auto-hide hover tooltips
        if (isHover) {
            tooltip.autoHideTimer = setTimeout(() => {
                this.hideTooltip(element);
            }, 5000);
        }
    }

    createTooltipElement(config) {
        const tooltip = document.createElement('div');
        tooltip.className = `contextual-tooltip ${config.position} ${config.theme}`;
        
        const illustration = document.createElement('div');
        illustration.className = `tooltip-illustration illustration-${config.illustration}`;
        
        const content = document.createElement('div');
        content.className = 'contextual-tooltip-content';
        
        const text = document.createElement('div');
        text.className = 'tooltip-text';
        text.innerHTML = `<strong>${config.title}</strong><br>${config.content}`;
        
        content.appendChild(illustration);
        content.appendChild(text);
        tooltip.appendChild(content);

        // Add close button for click tooltips
        const closeBtn = document.createElement('button');
        closeBtn.className = 'tooltip-close';
        closeBtn.innerHTML = '×';
        closeBtn.onclick = (e) => {
            e.stopPropagation();
            this.hideTooltip(Array.from(this.activeTooltips.keys()).find(key => this.activeTooltips.get(key) === tooltip));
        };
        tooltip.appendChild(closeBtn);

        return tooltip;
    }

    positionTooltip(tooltip, element, position) {
        const rect = element.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
        
        let top, left;
        
        switch (position) {
            case 'top':
                top = rect.top + scrollTop - 10;
                left = rect.left + scrollLeft + (rect.width / 2);
                break;
            case 'bottom':
                top = rect.bottom + scrollTop + 10;
                left = rect.left + scrollLeft + (rect.width / 2);
                break;
            case 'left':
                top = rect.top + scrollTop + (rect.height / 2);
                left = rect.left + scrollLeft - 10;
                break;
            case 'right':
                top = rect.top + scrollTop + (rect.height / 2);
                left = rect.right + scrollLeft + 10;
                break;
            default:
                top = rect.bottom + scrollTop + 10;
                left = rect.left + scrollLeft + (rect.width / 2);
        }
        
        tooltip.style.top = `${top}px`;
        tooltip.style.left = `${left}px`;
        
        // Ensure tooltip stays within viewport
        requestAnimationFrame(() => {
            this.adjustTooltipPosition(tooltip);
        });
    }

    adjustTooltipPosition(tooltip) {
        const rect = tooltip.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        // Adjust horizontal position
        if (rect.right > viewportWidth - 10) {
            tooltip.style.left = `${viewportWidth - rect.width - 10}px`;
        }
        if (rect.left < 10) {
            tooltip.style.left = '10px';
        }
        
        // Adjust vertical position
        if (rect.bottom > viewportHeight - 10) {
            tooltip.style.top = `${viewportHeight - rect.height - 10 + window.pageYOffset}px`;
        }
        if (rect.top < 10) {
            tooltip.style.top = `${10 + window.pageYOffset}px`;
        }
    }

    toggleTooltip(element) {
        if (this.activeTooltips.has(element)) {
            this.hideTooltip(element);
        } else {
            this.showTooltip(element, false);
        }
    }

    hideTooltip(element) {
        if (!this.activeTooltips.has(element)) return;
        
        const tooltip = this.activeTooltips.get(element);
        
        if (tooltip.autoHideTimer) {
            clearTimeout(tooltip.autoHideTimer);
        }
        
        tooltip.classList.remove('show');
        
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.parentNode.removeChild(tooltip);
            }
        }, 300);
        
        this.activeTooltips.delete(element);
    }

    hideAllTooltips() {
        for (const element of this.activeTooltips.keys()) {
            this.hideTooltip(element);
        }
    }

    // Public API methods
    addTooltip(elementId, config) {
        const element = document.getElementById(elementId);
        if (element) {
            element.setAttribute('data-help', elementId);
            this.tooltipData.set(elementId, config);
        }
    }

    removeTooltip(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            this.hideTooltip(element);
            element.removeAttribute('data-help');
            this.tooltipData.delete(elementId);
        }
    }

    updateTooltip(elementId, config) {
        this.tooltipData.set(elementId, config);
    }
}

// Initialize tooltips when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.contextualTooltips = new ContextualTooltips();
});

// Utility function to add help triggers to elements
function addHelpTrigger(element, helpKey) {
    if (typeof element === 'string') {
        element = document.querySelector(element);
    }
    
    if (!element) return;
    
    const trigger = document.createElement('button');
    trigger.className = 'help-trigger';
    trigger.innerHTML = '?';
    trigger.setAttribute('data-help', helpKey);
    trigger.setAttribute('data-help-click-only', 'true');
    trigger.title = 'Click for help';
    
    element.style.position = 'relative';
    element.appendChild(trigger);
}

// Auto-add help triggers to elements with specific classes
document.addEventListener('DOMContentLoaded', () => {
    // Add help triggers to form groups
    document.querySelectorAll('.form-group, .input-group').forEach(group => {
        const input = group.querySelector('input, select, textarea');
        if (input && input.hasAttribute('data-help')) {
            addHelpTrigger(group, input.getAttribute('data-help'));
        }
    });
    
    // Add help triggers to buttons with data-help
    document.querySelectorAll('button[data-help], .btn[data-help]').forEach(btn => {
        if (!btn.querySelector('.help-trigger')) {
            addHelpTrigger(btn.parentElement || btn, btn.getAttribute('data-help'));
        }
    });
});