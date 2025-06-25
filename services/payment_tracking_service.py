"""
Payment Tracking Service - Manual payment processing for cash, check, Venmo, Zelle
Handles payment logging, receipt generation, and payment status tracking
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pytz

class PaymentTrackingService:
    def __init__(self):
        self.hawaii_tz = pytz.timezone('Pacific/Honolulu')
        self.payments_file = 'data/payments.json'
        self.receipts_file = 'data/receipts.json'
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Ensure payment data files exist"""
        os.makedirs('data', exist_ok=True)
        
        if not os.path.exists(self.payments_file):
            with open(self.payments_file, 'w') as f:
                json.dump([], f, indent=2)
        
        if not os.path.exists(self.receipts_file):
            with open(self.receipts_file, 'w') as f:
                json.dump([], f, indent=2)
    
    def _load_payments(self) -> List[Dict]:
        """Load payments from JSON file"""
        try:
            with open(self.payments_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_payments(self, payments: List[Dict]):
        """Save payments to JSON file"""
        with open(self.payments_file, 'w') as f:
            json.dump(payments, f, indent=2)
    
    def log_payment(self, invoice_id: str, amount: float, payment_method: str, 
                   notes: str = '', received_by: str = 'admin') -> Dict:
        """Log a manual payment received"""
        hawaii_now = datetime.now(self.hawaii_tz)
        
        # Generate payment ID
        payments = self._load_payments()
        payment_id = f"PAY{len(payments) + 1:04d}"
        
        payment_record = {
            'payment_id': payment_id,
            'invoice_id': invoice_id,
            'amount': float(amount),
            'payment_method': payment_method,  # cash, check, venmo, zelle, stripe, square
            'payment_date': hawaii_now.isoformat(),
            'received_by': received_by,
            'notes': notes,
            'status': 'completed',
            'receipt_generated': False,
            'created_at': hawaii_now.isoformat()
        }
        
        payments.append(payment_record)
        self._save_payments(payments)
        
        logging.info(f"Payment logged: {payment_id} - ${amount} via {payment_method} for invoice {invoice_id}")
        return payment_record
    
    def mark_invoice_paid(self, invoice_id: str, amount: float, payment_method: str, 
                         notes: str = '', received_by: str = 'admin') -> bool:
        """Mark an invoice as paid and log the payment"""
        try:
            # Log the payment
            payment_record = self.log_payment(invoice_id, amount, payment_method, notes, received_by)
            
            # Update invoice status in storage
            from models import HandymanStorage
            storage = HandymanStorage()
            
            # Get all invoices and update the specific one
            invoices = storage.get_all_invoices() or []
            for invoice in invoices:
                if invoice.get('id') == invoice_id or str(invoice.get('invoice_number', '')).endswith(invoice_id):
                    invoice['payment_status'] = 'paid'
                    invoice['payment_date'] = payment_record['payment_date']
                    invoice['payment_method'] = payment_method
                    invoice['payment_id'] = payment_record['payment_id']
                    break
            
            # Save updated invoices
            storage._save_invoices_to_file(invoices)
            
            logging.info(f"Invoice {invoice_id} marked as paid")
            return True
            
        except Exception as e:
            logging.error(f"Error marking invoice as paid: {e}")
            return False
    
    def get_payments_by_invoice(self, invoice_id: str) -> List[Dict]:
        """Get all payments for a specific invoice"""
        payments = self._load_payments()
        return [p for p in payments if p['invoice_id'] == invoice_id]
    
    def get_recent_payments(self, days: int = 30) -> List[Dict]:
        """Get recent payments within specified days"""
        payments = self._load_payments()
        cutoff_date = datetime.now(self.hawaii_tz) - timedelta(days=days)
        
        recent_payments = []
        for payment in payments:
            try:
                payment_date = datetime.fromisoformat(payment['payment_date'])
                if payment_date >= cutoff_date:
                    recent_payments.append(payment)
            except (ValueError, KeyError):
                continue
        
        return sorted(recent_payments, key=lambda x: x['payment_date'], reverse=True)
    
    def get_payment_summary(self) -> Dict:
        """Get payment summary statistics"""
        payments = self._load_payments()
        
        total_amount = sum(p.get('amount', 0) for p in payments)
        payment_methods = {}
        
        for payment in payments:
            method = payment.get('payment_method', 'unknown')
            payment_methods[method] = payment_methods.get(method, 0) + payment.get('amount', 0)
        
        return {
            'total_payments': len(payments),
            'total_amount': total_amount,
            'payment_methods': payment_methods,
            'latest_payment': payments[-1] if payments else None
        }
    
    def generate_receipt(self, payment_id: str) -> Optional[Dict]:
        """Generate receipt data for a payment"""
        payments = self._load_payments()
        payment = next((p for p in payments if p['payment_id'] == payment_id), None)
        
        if not payment:
            return None
        
        # Get invoice details
        from models import HandymanStorage
        storage = HandymanStorage()
        invoices = storage.get_all_invoices() or []
        invoice = next((inv for inv in invoices 
                       if inv.get('id') == payment['invoice_id'] or 
                       str(inv.get('invoice_number', '')).endswith(payment['invoice_id'])), None)
        
        receipt_data = {
            'receipt_id': f"REC-{payment_id}",
            'payment_id': payment_id,
            'invoice_id': payment['invoice_id'],
            'customer_name': invoice.get('customer_name', 'Unknown') if invoice else 'Unknown',
            'amount_paid': payment['amount'],
            'payment_method': payment['payment_method'],
            'payment_date': payment['payment_date'],
            'received_by': payment['received_by'],
            'notes': payment['notes'],
            'business_info': {
                'name': 'SPANKKS Construction LLC',
                'address': 'Oahu, Hawaii',
                'phone': '(808) 778-9132',
                'email': 'spank808@gmail.com'
            }
        }
        
        return receipt_data

from datetime import timedelta