#!/usr/bin/env python3
"""
Test script for PDF generation system using the provided sample data
This will create sample contacts, quotes, and invoices to test the CRM system
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import HandymanStorage, Contact, Quote, QuoteItem, Invoice, get_hawaii_time
from pdf_service import generate_quote_pdf, generate_invoice_pdf

def create_sample_data():
    """Create sample data matching the provided sample"""
    storage = HandymanStorage()
    
    # Create sample contact
    contact_data = {
        'name': 'Jane Doe',
        'email': 'jane.doe@email.com',
        'phone': '(808) 123-4567',
        'address': '1234 Palm Drive, Honolulu, HI 96815',
        'notes': 'Referred by neighbor, interested in multiple services',
        'tags': ['residential', 'multi-service', 'referral']
    }
    
    contact = storage.add_contact(contact_data)
    print(f"✓ Created contact: {contact.name} (ID: {contact.id})")
    
    # Create sample quote items matching the provided data
    quote_items = [
        QuoteItem(
            description="Drywall Repair (10ft)",
            quantity=1.0,
            unit_price=150.00,
            unit="patch"
        ),
        QuoteItem(
            description="Vinyl Flooring Install (100 sqft)",
            quantity=100.0,
            unit_price=4.50,
            unit="sq ft"
        ),
        QuoteItem(
            description="Fence Repair – 2 Panels",
            quantity=2.0,
            unit_price=200.00,
            unit="panel"
        )
    ]
    
    # Calculate total
    total_amount = sum(item.total for item in quote_items)
    
    # Create quote
    hawaii_time = get_hawaii_time()
    valid_until = (hawaii_time + timedelta(days=30)).strftime('%Y-%m-%d')
    
    quote_data = {
        'contact_id': contact.id,
        'service_type': 'general',
        'items': quote_items,
        'total_amount': total_amount,
        'valid_until': valid_until,
        'notes': 'Multi-service project including drywall, flooring, and fence work'
    }
    
    quote = storage.add_quote(quote_data)
    print(f"✓ Created quote: Q{quote.id:04d} for ${total_amount:.2f}")
    
    # Create invoice from quote
    invoice_data = {
        'contact_id': contact.id,
        'quote_id': quote.id,
        'items': quote_items,
        'subtotal': total_amount,
        'tax_rate': 0.04712,  # Hawaii GET tax
        'payment_terms': 'Net 30'
    }
    
    invoice = storage.add_invoice(invoice_data)
    print(f"✓ Created invoice: INV{invoice.id:04d} for ${invoice.total_amount:.2f}")
    
    return storage, contact, quote, invoice

def test_pdf_generation():
    """Test PDF generation with sample data"""
    print("🔧 Testing PDF Generation System")
    print("=" * 50)
    
    # Create sample data
    storage, contact, quote, invoice = create_sample_data()
    
    # Ensure PDF directory exists
    os.makedirs("static/pdfs", exist_ok=True)
    
    try:
        # Test quote PDF generation
        print("\n📄 Generating Quote PDF...")
        quote_filename = generate_quote_pdf(quote, contact)
        quote_path = f"static/pdfs/{quote_filename}"
        
        if os.path.exists(quote_path):
            file_size = os.path.getsize(quote_path)
            print(f"✓ Quote PDF generated: {quote_filename} ({file_size} bytes)")
        else:
            print("❌ Quote PDF generation failed")
            return False
        
        # Test invoice PDF generation
        print("\n🧾 Generating Invoice PDF...")
        invoice_filename = generate_invoice_pdf(invoice, contact)
        invoice_path = f"static/pdfs/{invoice_filename}"
        
        if os.path.exists(invoice_path):
            file_size = os.path.getsize(invoice_path)
            print(f"✓ Invoice PDF generated: {invoice_filename} ({file_size} bytes)")
        else:
            print("❌ Invoice PDF generation failed")
            return False
        
        # Display sample data summary
        print("\n📋 Sample Data Summary:")
        print(f"   Customer: {contact.name}")
        print(f"   Phone: {contact.phone}")
        print(f"   Address: {contact.address}")
        print(f"   Quote ID: Q{quote.id:04d}")
        print(f"   Quote Total: ${quote.total_amount:.2f}")
        print(f"   Invoice ID: INV{invoice.id:04d}")
        print(f"   Invoice Total: ${invoice.total_amount:.2f}")
        print(f"   Tax Amount: ${invoice.tax_amount:.2f}")
        
        print("\n📁 Generated Files:")
        print(f"   Quote PDF: {quote_path}")
        print(f"   Invoice PDF: {invoice_path}")
        
        print("\n✅ PDF Generation Test Completed Successfully!")
        return True
        
    except Exception as e:
        print(f"❌ PDF Generation Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🏗️ SPANKKS Construction - CRM PDF Test")
    print("Testing comprehensive PDF generation system")
    print("Using sample data from provided specifications\n")
    
    success = test_pdf_generation()
    
    if success:
        print("\n🎉 All tests passed! The CRM system is ready for use.")
        print("\nNext steps:")
        print("1. Log into admin dashboard with credentials:")
        print("   Username: spankysadmin808")
        print("   Password: Money$$")
        print("2. Navigate to CRM Dashboard")
        print("3. View sample contact, quote, and invoice")
        print("4. Test PDF download and email functionality")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
    
    return success

if __name__ == "__main__":
    main()