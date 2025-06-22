/**
 * Confirmation Modal System for SPANKKS Construction
 * Handles "Are you sure?" dialogs for critical actions
 */

class ConfirmationModal {
    constructor() {
        this.currentModal = null;
        this.init();
    }
    
    init() {
        this.createModalHTML();
        this.bindGlobalConfirmations();
    }
    
    createModalHTML() {
        if (document.getElementById('confirmationModal')) return;
        
        const modalHTML = `
            <div class="modal fade" id="confirmationModal" tabindex="-1" data-bs-backdrop="static">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="confirmModalTitle">
                                <i class="fas fa-exclamation-triangle text-warning me-2"></i>
                                Confirm Action
                            </h5>
                        </div>
                        <div class="modal-body">
                            <p id="confirmModalMessage">Are you sure you want to perform this action?</p>
                            <div id="confirmModalDetails" class="mt-3" style="display: none;">
                                <div class="alert alert-warning">
                                    <small id="confirmModalDetailsText"></small>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-danger" id="confirmModalAction">Confirm</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
    
    show(options = {}) {
        const modal = document.getElementById('confirmationModal');
        const title = document.getElementById('confirmModalTitle');
        const message = document.getElementById('confirmModalMessage');
        const details = document.getElementById('confirmModalDetails');
        const detailsText = document.getElementById('confirmModalDetailsText');
        const actionBtn = document.getElementById('confirmModalAction');
        
        // Set content
        title.innerHTML = `<i class="${options.icon || 'fas fa-exclamation-triangle text-warning'} me-2"></i>${options.title || 'Confirm Action'}`;
        message.textContent = options.message || 'Are you sure you want to perform this action?';
        
        if (options.details) {
            details.style.display = 'block';
            detailsText.textContent = options.details;
        } else {
            details.style.display = 'none';
        }
        
        // Set button text and style
        actionBtn.textContent = options.confirmText || 'Confirm';
        actionBtn.className = `btn ${options.confirmClass || 'btn-danger'}`;
        
        // Handle confirmation action
        const newActionBtn = actionBtn.cloneNode(true);
        actionBtn.parentNode.replaceChild(newActionBtn, actionBtn);
        
        newActionBtn.addEventListener('click', () => {
            if (options.onConfirm) {
                options.onConfirm();
            }
            bootstrap.Modal.getInstance(modal).hide();
        });
        
        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        return bsModal;
    }
    
    // Convenience methods for common actions
    confirmDelete(itemName, onConfirm, details = null) {
        return this.show({
            title: 'Delete Item',
            message: `Are you sure you want to delete "${itemName}"?`,
            details: details || 'This action cannot be undone.',
            confirmText: 'Delete',
            confirmClass: 'btn-danger',
            icon: 'fas fa-trash text-danger',
            onConfirm: onConfirm
        });
    }
    
    confirmCancel(onConfirm, hasUnsavedChanges = false) {
        return this.show({
            title: 'Cancel Changes',
            message: 'Are you sure you want to cancel?',
            details: hasUnsavedChanges ? 'Any unsaved changes will be lost.' : null,
            confirmText: 'Yes, Cancel',
            confirmClass: 'btn-warning',
            icon: 'fas fa-times text-warning',
            onConfirm: onConfirm
        });
    }
    
    confirmSubmit(formName, onConfirm, details = null) {
        return this.show({
            title: 'Submit Form',
            message: `Ready to submit ${formName}?`,
            details: details,
            confirmText: 'Submit',
            confirmClass: 'btn-success',
            icon: 'fas fa-check text-success',
            onConfirm: onConfirm
        });
    }
    
    confirmPayment(amount, invoiceId, onConfirm) {
        return this.show({
            title: 'Mark as Paid',
            message: `Mark invoice ${invoiceId} as paid?`,
            details: `Payment amount: $${amount}. This will update the invoice status and customer records.`,
            confirmText: 'Mark Paid',
            confirmClass: 'btn-success',
            icon: 'fas fa-dollar-sign text-success',
            onConfirm: onConfirm
        });
    }
    
    confirmJobCompletion(jobId, customerName, onConfirm) {
        return this.show({
            title: 'Complete Job',
            message: `Mark job ${jobId} as completed?`,
            details: `This will finalize the job for ${customerName} and trigger invoice generation if needed.`,
            confirmText: 'Complete Job',
            confirmClass: 'btn-success',
            icon: 'fas fa-check-circle text-success',
            onConfirm: onConfirm
        });
    }
    
    confirmStaffAssignment(staffName, jobId, onConfirm) {
        return this.show({
            title: 'Assign Staff',
            message: `Assign ${staffName} to job ${jobId}?`,
            details: 'The staff member will receive notification and access to job details.',
            confirmText: 'Assign',
            confirmClass: 'btn-primary',
            icon: 'fas fa-user-plus text-primary',
            onConfirm: onConfirm
        });
    }
    
    // Global confirmation binding
    bindGlobalConfirmations() {
        document.addEventListener('click', (e) => {
            const target = e.target.closest('[data-confirm]');
            if (!target) return;
            
            e.preventDefault();
            e.stopPropagation();
            
            const confirmType = target.dataset.confirm;
            const confirmMessage = target.dataset.confirmMessage;
            const confirmDetails = target.dataset.confirmDetails;
            const confirmTitle = target.dataset.confirmTitle;
            const confirmText = target.dataset.confirmText;
            const confirmClass = target.dataset.confirmClass;
            
            const originalAction = () => {
                if (target.href) {
                    window.location.href = target.href;
                } else if (target.onclick) {
                    target.onclick();
                } else if (target.type === 'submit') {
                    target.closest('form').submit();
                }
            };
            
            switch (confirmType) {
                case 'delete':
                    const itemName = target.dataset.itemName || 'this item';
                    this.confirmDelete(itemName, originalAction, confirmDetails);
                    break;
                    
                case 'cancel':
                    const hasChanges = target.dataset.hasChanges === 'true';
                    this.confirmCancel(originalAction, hasChanges);
                    break;
                    
                case 'submit':
                    const formName = target.dataset.formName || 'this form';
                    this.confirmSubmit(formName, originalAction, confirmDetails);
                    break;
                    
                case 'payment':
                    const amount = target.dataset.amount;
                    const invoiceId = target.dataset.invoiceId;
                    this.confirmPayment(amount, invoiceId, originalAction);
                    break;
                    
                case 'complete':
                    const jobId = target.dataset.jobId;
                    const customerName = target.dataset.customerName;
                    this.confirmJobCompletion(jobId, customerName, originalAction);
                    break;
                    
                case 'assign':
                    const staffName = target.dataset.staffName;
                    const assignJobId = target.dataset.jobId;
                    this.confirmStaffAssignment(staffName, assignJobId, originalAction);
                    break;
                    
                default:
                    this.show({
                        title: confirmTitle || 'Confirm Action',
                        message: confirmMessage || 'Are you sure?',
                        details: confirmDetails,
                        confirmText: confirmText || 'Confirm',
                        confirmClass: confirmClass || 'btn-primary',
                        onConfirm: originalAction
                    });
            }
        });
        
        // Form submission confirmations
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (!form.dataset.confirmSubmit) return;
            
            e.preventDefault();
            
            const formName = form.dataset.formName || form.name || 'form';
            const hasRequired = form.querySelectorAll('[required]').length > 0;
            const details = hasRequired ? 'Please ensure all required fields are completed.' : null;
            
            this.confirmSubmit(formName, () => form.submit(), details);
        });
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.confirmModal = new ConfirmationModal();
    
    // Global helper functions
    window.confirmDelete = (itemName, callback, details) => {
        return window.confirmModal.confirmDelete(itemName, callback, details);
    };
    
    window.confirmCancel = (callback, hasChanges) => {
        return window.confirmModal.confirmCancel(callback, hasChanges);
    };
    
    window.confirmSubmit = (formName, callback, details) => {
        return window.confirmModal.confirmSubmit(formName, callback, details);
    };
    
    window.confirmAction = (options) => {
        return window.confirmModal.show(options);
    };
});