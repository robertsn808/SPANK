/**
 * SPANKKS Construction Toast Notification System
 * Provides consistent user feedback across all application actions
 */

class ToastNotifications {
    constructor() {
        this.container = null;
        this.init();
    }
    
    init() {
        this.createContainer();
        this.bindGlobalErrorHandlers();
    }
    
    createContainer() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container position-fixed top-0 end-0 p-3';
            this.container.style.zIndex = '9999';
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('toast-container');
        }
    }
    
    show(message, type = 'info', duration = 5000, options = {}) {
        const toast = this.createToast(message, type, duration, options);
        this.container.appendChild(toast);
        
        // Initialize Bootstrap toast
        const bsToast = new bootstrap.Toast(toast, {
            delay: duration,
            autohide: duration > 0
        });
        
        // Show toast with animation
        bsToast.show();
        
        // Auto-remove after hide
        toast.addEventListener('hidden.bs.toast', () => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        });
        
        return toast;
    }
    
    createToast(message, type, duration, options) {
        const toastId = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-triangle',
            warning: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle',
            loading: 'fas fa-spinner fa-spin'
        };
        
        const colors = {
            success: 'text-success',
            error: 'text-danger',
            warning: 'text-warning',
            info: 'text-primary',
            loading: 'text-info'
        };
        
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = 'toast';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        const progressBar = duration > 0 ? `
            <div class="toast-progress">
                <div class="toast-progress-bar" style="animation-duration: ${duration}ms;"></div>
            </div>
        ` : '';
        
        const actionButton = options.action ? `
            <button type="button" class="btn btn-sm btn-outline-secondary ms-2" onclick="${options.action.callback}">
                ${options.action.text}
            </button>
        ` : '';
        
        toast.innerHTML = `
            <div class="toast-header">
                <i class="${icons[type]} ${colors[type]} me-2"></i>
                <strong class="me-auto">${options.title || this.getDefaultTitle(type)}</strong>
                <small class="text-muted">${this.getTimeStamp()}</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
                ${actionButton}
            </div>
            ${progressBar}
        `;
        
        return toast;
    }
    
    getDefaultTitle(type) {
        const titles = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Information',
            loading: 'Processing'
        };
        return titles[type] || 'Notification';
    }
    
    getTimeStamp() {
        const now = new Date();
        return now.toLocaleTimeString('en-US', { 
            hour12: true, 
            hour: 'numeric', 
            minute: '2-digit' 
        });
    }
    
    // Convenience methods for different types
    success(message, options = {}) {
        return this.show(message, 'success', 4000, options);
    }
    
    error(message, options = {}) {
        return this.show(message, 'error', 8000, options);
    }
    
    warning(message, options = {}) {
        return this.show(message, 'warning', 6000, options);
    }
    
    info(message, options = {}) {
        return this.show(message, 'info', 5000, options);
    }
    
    loading(message, options = {}) {
        return this.show(message, 'loading', 0, options);
    }
    
    // Specific business action notifications
    invoiceMarkedPaid(invoiceId, amount) {
        this.success(`Invoice ${invoiceId} marked as paid ($${amount})`, {
            title: 'Payment Recorded',
            action: {
                text: 'View Invoice',
                callback: `window.location.href='/admin/invoice-details/${invoiceId}'`
            }
        });
    }
    
    quoteGenerated(quoteId, customerName) {
        this.success(`Quote ${quoteId} generated for ${customerName}`, {
            title: 'Quote Created',
            action: {
                text: 'Download PDF',
                callback: `window.open('/api/download-quote?quote_id=${quoteId}', '_blank')`
            }
        });
    }
    
    staffAssigned(staffName, jobId) {
        this.success(`${staffName} assigned to job ${jobId}`, {
            title: 'Staff Assigned'
        });
    }
    
    photoUploaded(photoType, jobId) {
        this.success(`${photoType} photo uploaded for job ${jobId}`, {
            title: 'Photo Added'
        });
    }
    
    jobCompleted(jobId, customerName) {
        this.success(`Job ${jobId} completed for ${customerName}`, {
            title: 'Job Finished',
            action: {
                text: 'Generate Invoice',
                callback: `window.location.href='/invoice-generator?jobId=${jobId}'`
            }
        });
    }
    
    appointmentScheduled(customerName, date) {
        this.success(`Appointment scheduled for ${customerName} on ${date}`, {
            title: 'Appointment Booked'
        });
    }
    
    customerInquiry(customerName, serviceType) {
        this.info(`New inquiry from ${customerName} for ${serviceType}`, {
            title: 'New Customer Inquiry',
            action: {
                text: 'View Details',
                callback: `window.location.href='/admin/dashboard'`
            }
        });
    }
    
    // Network and system notifications
    networkError() {
        this.error('Network connection error. Please check your internet connection and try again.', {
            title: 'Connection Error',
            action: {
                text: 'Retry',
                callback: 'window.location.reload()'
            }
        });
    }
    
    systemMaintenance() {
        this.warning('System maintenance in progress. Some features may be temporarily unavailable.', {
            title: 'System Maintenance'
        });
    }
    
    dataAutoSaved() {
        this.info('Your changes have been automatically saved.', {
            title: 'Auto-saved'
        });
    }
    
    // Bind global error handlers
    bindGlobalErrorHandlers() {
        // Handle fetch errors
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            try {
                const response = await originalFetch(...args);
                
                if (!response.ok) {
                    if (response.status >= 500) {
                        this.error('Server error occurred. Please try again later.');
                    } else if (response.status === 404) {
                        this.error('Requested resource not found.');
                    } else if (response.status === 403) {
                        this.error('Access denied. Please check your permissions.');
                    } else if (response.status === 401) {
                        this.error('Authentication required. Please log in again.');
                    }
                }
                
                return response;
            } catch (error) {
                this.networkError();
                throw error;
            }
        };
        
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.error('An unexpected error occurred. Please try again.');
        });
        
        // Handle JavaScript errors
        window.addEventListener('error', (event) => {
            console.error('JavaScript error:', event.error);
            this.error('An application error occurred. Please refresh the page.');
        });
    }
    
    // Form submission helpers
    handleFormSubmission(form, endpoint, options = {}) {
        const loadingToast = this.loading(options.loadingMessage || 'Processing request...');
        
        const formData = new FormData(form);
        
        return fetch(endpoint, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            this.hide(loadingToast);
            
            if (response.ok) {
                return response.json().then(data => {
                    this.success(data.message || 'Request completed successfully');
                    return data;
                });
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        })
        .catch(error => {
            this.hide(loadingToast);
            this.error(error.message || 'Request failed');
            throw error;
        });
    }
}

// Initialize toast system
window.toastManager = new ToastNotificationManager();
        .then(response => response.json())
        .then(data => {
            // Hide loading toast
            bootstrap.Toast.getInstance(loadingToast).hide();
            
            if (data.success) {
                this.success(options.successMessage || data.message || 'Operation completed successfully');
                if (options.onSuccess) {
                    options.onSuccess(data);
                }
            } else {
                this.error(options.errorMessage || data.error || 'Operation failed');
                if (options.onError) {
                    options.onError(data);
                }
            }
            
            return data;
        })
        .catch(error => {
            bootstrap.Toast.getInstance(loadingToast).hide();
            this.error(options.errorMessage || 'Request failed. Please try again.');
            if (options.onError) {
                options.onError(error);
            }
            throw error;
        });
    }
}

// CSS for toast notifications and progress bars
const toastStyles = `
<style>
.toast-container {
    max-width: 400px;
}

.toast {
    margin-bottom: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    border: none;
    border-radius: 8px;
    overflow: hidden;
}

.toast-header {
    background: rgba(255,255,255,0.95);
    border-bottom: 1px solid rgba(0,0,0,0.1);
    padding: 12px 16px;
}

.toast-body {
    background: white;
    padding: 16px;
    font-size: 14px;
    line-height: 1.4;
}

.toast-progress {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: rgba(0,0,0,0.1);
    overflow: hidden;
}

.toast-progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #007bff, #0056b3);
    width: 100%;
    animation: toast-progress 0s linear forwards;
    transform-origin: left;
}

@keyframes toast-progress {
    from { transform: scaleX(1); }
    to { transform: scaleX(0); }
}

.toast.show {
    animation: slideInRight 0.3s ease-out;
}

.toast.hide {
    animation: slideOutRight 0.3s ease-in;
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes slideOutRight {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}

/* Mobile responsive */
@media (max-width: 576px) {
    .toast-container {
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        right: 10px !important;
        max-width: none !important;
    }
    
    .toast {
        margin-bottom: 8px;
    }
}
</style>
`;

// Initialize global toast system
document.addEventListener('DOMContentLoaded', function() {
    // Add styles to document
    document.head.insertAdjacentHTML('beforeend', toastStyles);
    
    // Initialize global toast instance
    window.toast = new ToastNotifications();
    
    // Backward compatibility aliases
    window.showToast = (message, type, duration, options) => {
        return window.toast.show(message, type, duration, options);
    };
    
    window.showSuccess = (message, options) => window.toast.success(message, options);
    window.showError = (message, options) => window.toast.error(message, options);
    window.showWarning = (message, options) => window.toast.warning(message, options);
    window.showInfo = (message, options) => window.toast.info(message, options);
    window.showLoading = (message, options) => window.toast.loading(message, options);
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ToastNotifications;
}