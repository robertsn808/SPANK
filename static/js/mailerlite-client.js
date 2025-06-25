/**
 * MailerLite Client-side Integration for SPANKKS Construction
 * Uses fetch API for email functionality
 */

class MailerLiteClient {
    constructor() {
        this.baseUrl = '/api/email';
        this.apiKey = null; // Will be set server-side
    }

    /**
     * Send quote email via MailerLite
     */
    async sendQuoteEmail(quoteData, clientData) {
        try {
            const response = await fetch(`${this.baseUrl}/send-quote`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    quote: quoteData,
                    client: clientData
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showSuccessNotification('Quote email sent successfully!');
                return true;
            } else {
                this.showErrorNotification(`Failed to send email: ${result.error}`);
                return false;
            }
        } catch (error) {
            console.error('Send quote email error:', error);
            this.showErrorNotification('Network error while sending email');
            return false;
        }
    }

    /**
     * Send invoice reminder
     */
    async sendInvoiceReminder(invoiceData, clientData) {
        try {
            const response = await fetch(`${this.baseUrl}/send-reminder`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    invoice: invoiceData,
                    client: clientData
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showSuccessNotification('Reminder email sent successfully!');
                return true;
            } else {
                this.showErrorNotification(`Failed to send reminder: ${result.error}`);
                return false;
            }
        } catch (error) {
            console.error('Send reminder error:', error);
            this.showErrorNotification('Network error while sending reminder');
            return false;
        }
    }

    /**
     * Send job completion notification
     */
    async sendJobCompletionEmail(jobData, clientData) {
        try {
            const response = await fetch(`${this.baseUrl}/send-completion`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    job: jobData,
                    client: clientData
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showSuccessNotification('Completion notification sent!');
                return true;
            } else {
                this.showErrorNotification(`Failed to send notification: ${result.error}`);
                return false;
            }
        } catch (error) {
            console.error('Send completion email error:', error);
            this.showErrorNotification('Network error while sending notification');
            return false;
        }
    }

    /**
     * Subscribe client to newsletter
     */
    async subscribeToNewsletter(email, name = '') {
        try {
            const response = await fetch(`${this.baseUrl}/subscribe`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    name: name,
                    source: 'SPANKKS Construction Website'
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showSuccessNotification('Successfully subscribed to updates!');
                return true;
            } else {
                this.showErrorNotification(`Subscription failed: ${result.error}`);
                return false;
            }
        } catch (error) {
            console.error('Newsletter subscription error:', error);
            this.showErrorNotification('Network error during subscription');
            return false;
        }
    }

    /**
     * Send bulk emails (for marketing campaigns)
     */
    async sendBulkEmail(emailData) {
        try {
            const response = await fetch(`${this.baseUrl}/send-bulk`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(emailData)
            });

            const result = await response.json();
            
            if (result.success) {
                this.showSuccessNotification(`Bulk email sent to ${result.sent_count} recipients`);
                return true;
            } else {
                this.showErrorNotification(`Bulk email failed: ${result.error}`);
                return false;
            }
        } catch (error) {
            console.error('Bulk email error:', error);
            this.showErrorNotification('Network error during bulk email');
            return false;
        }
    }

    /**
     * Get email analytics
     */
    async getEmailAnalytics(dateRange = '30d') {
        try {
            const response = await fetch(`${this.baseUrl}/analytics?range=${dateRange}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();
            
            if (result.success) {
                return result.data;
            } else {
                console.error('Analytics error:', result.error);
                return null;
            }
        } catch (error) {
            console.error('Get analytics error:', error);
            return null;
        }
    }

    /**
     * Show success notification
     */
    showSuccessNotification(message) {
        // Create and show toast notification
        const toast = this.createToast(message, 'success');
        this.showToast(toast);
    }

    /**
     * Show error notification
     */
    showErrorNotification(message) {
        // Create and show toast notification
        const toast = this.createToast(message, 'error');
        this.showToast(toast);
    }

    /**
     * Create toast notification element
     */
    createToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        return toast;
    }

    /**
     * Show toast notification
     */
    showToast(toast) {
        // Get or create toast container
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1050';
            document.body.appendChild(container);
        }
        
        container.appendChild(toast);
        
        // Initialize and show toast
        if (typeof bootstrap !== 'undefined') {
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
            
            // Remove toast element after it's hidden
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        } else {
            // Fallback if Bootstrap is not available
            toast.style.display = 'block';
            setTimeout(() => {
                toast.style.opacity = '0';
                setTimeout(() => toast.remove(), 300);
            }, 5000);
        }
    }

    /**
     * Test MailerLite connection
     */
    async testConnection() {
        try {
            const response = await fetch(`${this.baseUrl}/test`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();
            return result.success;
        } catch (error) {
            console.error('Connection test error:', error);
            return false;
        }
    }
}

// Global instance
window.MailerLite = new MailerLiteClient();

// Helper functions for common use cases
window.sendQuoteEmail = async function(quoteNumber) {
    try {
        // Get quote data from current page or API
        const quoteData = await fetch(`/api/admin/quotes/${quoteNumber}`).then(r => r.json());
        const clientData = {
            email: quoteData.client_email,
            name: quoteData.client_name
        };
        
        return await window.MailerLite.sendQuoteEmail(quoteData, clientData);
    } catch (error) {
        console.error('Send quote email helper error:', error);
        return false;
    }
};

window.sendInvoiceReminder = async function(invoiceNumber) {
    try {
        // Get invoice data from current page or API
        const invoiceData = await fetch(`/api/admin/invoices/${invoiceNumber}`).then(r => r.json());
        const clientData = {
            email: invoiceData.client_email,
            name: invoiceData.client_name
        };
        
        return await window.MailerLite.sendInvoiceReminder(invoiceData, clientData);
    } catch (error) {
        console.error('Send reminder helper error:', error);
        return false;
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Test connection on load (optional)
    // window.MailerLite.testConnection().then(connected => {
    //     console.log('MailerLite connection:', connected ? 'OK' : 'Failed');
    // });
});