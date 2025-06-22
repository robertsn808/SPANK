import os
import io
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfgen import canvas
from models import get_hawaii_time

class PDFGenerator:
    """Professional PDF generation service for SPANKKS Construction quotes and invoices"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Create custom styles for SPANKKS Construction branding"""
        self.styles.add(ParagraphStyle(
            name='SPANKKSHeader',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#2C5AA0'),
            spaceAfter=12,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#666666'),
            alignment=TA_RIGHT
        ))

        self.styles.add(ParagraphStyle(
            name='CustomerInfo',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6
        ))

        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=white,
            alignment=TA_CENTER
        ))

    def generate_quote_pdf(self, quote_data, output_path):
        """Generate professional quote PDF"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        story = []

        # Header with company branding
        story.extend(self._build_header("PROFESSIONAL QUOTE"))
        story.append(Spacer(1, 12))

        # Quote metadata
        story.extend(self._build_quote_metadata(quote_data))
        story.append(Spacer(1, 20))

        # Items table
        story.extend(self._build_items_table(quote_data['items']))
        story.append(Spacer(1, 20))

        # Totals section
        story.extend(self._build_totals_section(quote_data))
        story.append(Spacer(1, 20))

        # Terms and conditions
        story.extend(self._build_quote_terms(quote_data.get('quote_days', 30)))

        doc.build(story)
        return output_path

    def generate_invoice_pdf(self, invoice_data, output_path):
        """Generate professional invoice PDF"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        story = []

        # Header with company branding
        story.extend(self._build_header("INVOICE"))
        story.append(Spacer(1, 12))

        # Invoice metadata
        story.extend(self._build_invoice_metadata(invoice_data))
        story.append(Spacer(1, 20))

        # Items table
        story.extend(self._build_items_table(invoice_data['items']))
        story.append(Spacer(1, 20))

        # Totals section
        story.extend(self._build_totals_section(invoice_data))
        story.append(Spacer(1, 20))

        # Payment terms and instructions
        story.extend(self._build_invoice_terms(invoice_data))

        doc.build(story)
        return output_path

    def _build_header(self, document_type):
        """Build professional header with SPANKKS Construction branding"""
        elements = []

        # Company name and document type
        elements.append(Paragraph("SPANKKS CONSTRUCTION LLC", self.styles['SPANKKSHeader']))
        elements.append(Paragraph(document_type, self.styles['Heading2']))
        elements.append(Spacer(1, 6))

        # Company contact information
        company_info = """
        <b>Professional Construction & Home Improvements</b><br/>
        Licensed & Insured | Serving O'ahu<br/>
        Phone: (808) 778-9132<br/>
        Email: spank808@gmail.com
        """
        elements.append(Paragraph(company_info, self.styles['CompanyInfo']))

        return elements

    def _build_quote_metadata(self, quote_data):
        """Build quote-specific metadata section"""
        elements = []

        # Create two-column layout for quote info
        quote_info = [
            ['Quote #:', quote_data.get('quote_id', 'PENDING')],
            ['Date:', quote_data.get('date', get_hawaii_time().strftime('%B %d, %Y'))],
            ['Valid Until:', quote_data.get('valid_until', (get_hawaii_time() + timedelta(days=30)).strftime('%B %d, %Y'))],
            ['Prepared by:', quote_data.get('employee_name', 'SPANKKS Construction Team')]
        ]

        customer_info = [
            ['Customer:', quote_data.get('customer', 'Customer Name')],
            ['Phone:', quote_data.get('customer_phone', 'Phone Number')],
            ['Location:', quote_data.get('job_location', 'Job Address')],
            ['Service Type:', quote_data.get('service_type', 'General Services').title()]
        ]

        # Combine into single table
        combined_data = []
        for i in range(max(len(quote_info), len(customer_info))):
            row = []
            if i < len(quote_info):
                row.extend(quote_info[i])
            else:
                row.extend(['', ''])

            row.append('')  # Spacer column

            if i < len(customer_info):
                row.extend(customer_info[i])
            else:
                row.extend(['', ''])

            combined_data.append(row)

        table = Table(combined_data, colWidths=[1*inch, 1.5*inch, 0.3*inch, 1*inch, 2*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTNAME', (3, 0), (4, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(table)
        return elements

    def _build_invoice_metadata(self, invoice_data):
        """Build invoice-specific metadata section"""
        elements = []

        # Invoice information
        invoice_info = [
            ['Invoice #:', invoice_data.get('invoice_id', 'PENDING')],
            ['Date:', invoice_data.get('created_date', get_hawaii_time().strftime('%B %d, %Y'))],
            ['Due Date:', invoice_data.get('due_date', (get_hawaii_time() + timedelta(days=30)).strftime('%B %d, %Y'))],
            ['Terms:', invoice_data.get('payment_terms', 'Net 30')]
        ]

        customer_info = [
            ['Bill To:', invoice_data.get('customer', 'Customer Name')],
            ['Phone:', invoice_data.get('customer_phone', 'Phone Number')],
            ['Address:', invoice_data.get('job_location', 'Customer Address')],
            ['Status:', invoice_data.get('status', 'Pending').title()]
        ]

        # Combine into single table
        combined_data = []
        for i in range(max(len(invoice_info), len(customer_info))):
            row = []
            if i < len(invoice_info):
                row.extend(invoice_info[i])
            else:
                row.extend(['', ''])

            row.append('')  # Spacer column

            if i < len(customer_info):
                row.extend(customer_info[i])
            else:
                row.extend(['', ''])

            combined_data.append(row)

        table = Table(combined_data, colWidths=[1*inch, 1.5*inch, 0.3*inch, 1*inch, 2*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTNAME', (3, 0), (4, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(table)
        return elements

    def _build_items_table(self, items):
        """Build professional items table"""
        elements = []

        # Table header
        data = [['Item#', 'Description', 'Qty', 'Unit', 'Unit Price', 'Line Total']]

        # Add items
        for i, item in enumerate(items, 1):
            if hasattr(item, 'description'):  # Quote/Invoice item object
                data.append([
                    str(i),
                    item.description,
                    f"{item.quantity:.2f}",
                    item.unit,
                    f"${item.unit_price:.2f}",
                    f"${item.total:.2f}"
                ])
            else:  # Dictionary format
                data.append([
                    str(i),
                    item.get('description', ''),
                    f"{item.get('quantity', 1):.2f}",
                    item.get('unit', 'each'),
                    f"${item.get('unit_price', 0):.2f}",
                    f"${item.get('line_total', 0):.2f}"
                ])

        table = Table(data, colWidths=[0.5*inch, 2.5*inch, 0.7*inch, 0.7*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2C5AA0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Data styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Item numbers
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Quantities and prices
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Descriptions

            # Grid and padding
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#CCCCCC')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#F8F9FA')])
        ]))

        elements.append(table)
        return elements

    def _build_totals_section(self, data):
        """Build professional totals section"""
        elements = []

        # Calculate totals if not provided
        if 'total_sub' not in data:
            if hasattr(data.get('items', [{}])[0], 'total'):
                subtotal = sum(item.total for item in data['items'])
            else:
                subtotal = sum(item.get('line_total', 0) for item in data['items'])
        else:
            subtotal = data['total_sub']

        discount = data.get('total_discount', 0)
        tax_rate = data.get('tax_rate', 0.04712)  # Hawaii GET tax
        tax_amount = (subtotal - discount) * tax_rate
        total = subtotal - discount + tax_amount

        # Build totals table
        totals_data = []

        if discount > 0:
            totals_data.append(['Subtotal:', f"${subtotal:.2f}"])
            totals_data.append(['Discount:', f"-${discount:.2f}"])
            totals_data.append(['Adjusted Subtotal:', f"${subtotal - discount:.2f}"])
        else:
            totals_data.append(['Subtotal:', f"${subtotal:.2f}"])

        totals_data.append(['Hawaii GET Tax (4.712%):', f"${tax_amount:.2f}"])
        totals_data.append(['', ''])  # Spacer
        totals_data.append(['TOTAL:', f"${total:.2f}"])

        table = Table(totals_data, colWidths=[3.5*inch, 1.5*inch], hAlign='RIGHT')
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LINEABOVE', (0, -1), (-1, -1), 2, black),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#F0F0F0')),
        ]))

        elements.append(table)
        return elements

    def _build_quote_terms(self, quote_days):
        """Build quote terms and conditions"""
        elements = []

        terms_text = f"""
        <b>Quote Terms & Conditions:</b><br/><br/>

        • This quote is valid for <b>{quote_days} days</b> from the date above<br/>
        • All work will be performed by licensed and insured professionals<br/>
        • Materials and labor are guaranteed for quality and workmanship<br/>
        • Final pricing may vary based on site conditions and material changes<br/>
        • A 50% deposit is required to begin work<br/><br/>

        <b>Ready to get started?</b> Call us at <b>(808) 778-9132</b> or email <b>spank808@gmail.com</b><br/>
        We look forward to working with you on your project!<br/><br/>

        <i>SPANKKS Construction LLC - Licensed & Insured | Serving O'ahu with Pride</i>
        """

        elements.append(Paragraph(terms_text, self.styles['Normal']))
        return elements

    def _build_invoice_terms(self, invoice_data):
        """Build invoice payment terms and instructions"""
        elements = []

        payment_terms = invoice_data.get('payment_terms', 'Net 30')

        terms_text = f"""
        <b>Payment Terms:</b> {payment_terms}<br/><br/>

        <b>Payment Methods:</b><br/>
        • Cash or Check (made payable to SPANKKS Construction LLC)<br/>
        • Venmo: @SPANKKSConstruction<br/>
        • Bank Transfer (contact for details)<br/><br/>

        <b>Late Payment:</b> 1.5% monthly service charge on overdue balances<br/>
        <b>Questions?</b> Contact us at (808) 778-9132 or spank808@gmail.com<br/><br/>

        <i>Thank you for choosing SPANKKS Construction for your project!</i>
        """

        elements.append(Paragraph(terms_text, self.styles['Normal']))
        return elements

# Initialize PDF service
pdf_generator = PDFGenerator()

def generate_quote_pdf(quote, contact, output_dir="static/pdfs"):
    """Generate PDF for a quote object"""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"quote_{quote.id}_{contact.name.replace(' ', '_')}.pdf"
    output_path = os.path.join(output_dir, filename)

    # Convert quote data to PDF format
    quote_data = {
        'quote_id': f"Q{quote.id:04d}",
        'date': quote.created_date,
        'valid_until': quote.valid_until,
        'customer': contact.name,
        'customer_phone': contact.phone,
        'job_location': contact.address or 'Address on file',
        'service_type': quote.service_type,
        'employee_name': 'SPANKKS Construction Team',
        'items': quote.items,
        'quote_days': 30
    }

    pdf_generator.generate_quote_pdf(quote_data, output_path)
    return filename

def generate_invoice_pdf(invoice, contact, output_dir="static/pdfs"):
    """Generate PDF for an invoice object"""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"invoice_{invoice.id}_{contact.name.replace(' ', '_')}.pdf"
    output_path = os.path.join(output_dir, filename)

    # Convert invoice data to PDF format
    invoice_data = {
        'invoice_id': f"INV{invoice.id:04d}",
        'created_date': invoice.created_date,
        'due_date': invoice.due_date,
        'customer': contact.name,
        'customer_phone': contact.phone,
        'job_location': contact.address or 'Address on file',
        'payment_terms': invoice.payment_terms,
        'status': invoice.status,
        'items': invoice.items,
        'tax_rate': invoice.tax_rate
    }

    pdf_generator.generate_invoice_pdf(invoice_data, output_path)
    return filename

import json
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import logging

logger = logging.getLogger(__name__)

def generate_quote_pdf(quote, contact):
    """Generate PDF for quote"""
    try:
        # Ensure pdfs directory exists
        os.makedirs('static/pdfs', exist_ok=True)

        filename = f"quote_{quote.id}_{contact.name.replace(' ', '_')}.pdf"
        filepath = os.path.join('static/pdfs', filename)

        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Company header
        company_style = ParagraphStyle(
            'CompanyHeader',
            parent=styles['Title'],
            fontSize=24,
            textColor=colors.blue,
            alignment=TA_CENTER
        )
        story.append(Paragraph("SPANKKS Construction", company_style))
        story.append(Spacer(1, 12))

        # Quote header
        quote_style = ParagraphStyle(
            'QuoteHeader',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.black,
            alignment=TA_LEFT
        )
        story.append(Paragraph(f"Quote #{quote.id:04d}", quote_style))
        story.append(Spacer(1, 12))

        # Customer and quote info
        info_data = [
            ['Customer:', contact.name, 'Date:', datetime.now().strftime('%m/%d/%Y')],
            ['Phone:', contact.phone, 'Valid Until:', quote.valid_until],
            ['Email:', contact.email, 'Service Type:', quote.service_type.replace('_', ' ').title()],
            ['Address:', contact.address, '', '']
        ]

        info_table = Table(info_data, colWidths=[1*inch, 2.5*inch, 1*inch, 1.5*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 24))

        # Line items
        story.append(Paragraph("Quote Details", styles['Heading2']))
        story.append(Spacer(1, 12))

        # Items table
        items_data = [['Description', 'Quantity', 'Unit', 'Unit Price', 'Total']]
        for item in quote.items:
            items_data.append([
                item.description,
                str(item.quantity),
                item.unit,
                f"${item.unit_price:.2f}",
                f"${item.total:.2f}"
            ])

        # Add subtotal and total
        items_data.append(['', '', '', 'Subtotal:', f"${quote.total_amount:.2f}"])
        hawaii_tax = quote.total_amount * 0.04712  # Hawaii GET tax
        items_data.append(['', '', '', 'Tax (4.712%):', f"${hawaii_tax:.2f}"])
        items_data.append(['', '', '', 'Total:', f"${quote.total_amount + hawaii_tax:.2f}"])

        items_table = Table(items_data, colWidths=[3*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
        items_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
            ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -4), 1, colors.black),
            ('LINEBELOW', (3, -3), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('BACKGROUND', (3, -1), (-1, -1), colors.lightgrey),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 24))

        # Terms and conditions
        story.append(Paragraph("Terms & Conditions", styles['Heading3']))
        terms = """
        This quote is valid for 30 days from the date issued.
        Work will be performed by licensed and insured professionals.
        Material costs may vary based on availability and selection.
        Payment terms: 50% down, 50% upon completion.
        """
        story.append(Paragraph(terms, styles['Normal']))

        # Build PDF
        doc.build(story)
        logger.info(f"Generated quote PDF: {filename}")
        return filename

    except Exception as e:
        logger.error(f"Error generating quote PDF: {e}")
        return None

def generate_invoice_pdf(invoice, contact):
    """Generate PDF for invoice"""
    try:
        # Ensure pdfs directory exists
        os.makedirs('static/pdfs', exist_ok=True)

        filename = f"invoice_{invoice.id}_{contact.name.replace(' ', '_')}.pdf"
        filepath = os.path.join('static/pdfs', filename)

        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Company header
        company_style = ParagraphStyle(
            'CompanyHeader',
            parent=styles['Title'],
            fontSize=24,
            textColor=colors.red,
            alignment=TA_CENTER
        )
        story.append(Paragraph("SPANKKS Construction", company_style))
        story.append(Spacer(1, 12))

        # Invoice header
        invoice_style = ParagraphStyle(
            'InvoiceHeader',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.black,
            alignment=TA_LEFT
        )
        story.append(Paragraph(f"Invoice #{invoice.id:04d}", invoice_style))
        story.append(Spacer(1, 12))

        # Customer and invoice info
        info_data = [
            ['Bill To:', contact.name, 'Invoice Date:', invoice.created_date],
            ['Phone:', contact.phone, 'Due Date:', invoice.due_date],
            ['Email:', contact.email, 'Payment Terms:', invoice.payment_terms],
            ['Address:', contact.address, 'Status:', invoice.status.title()]
        ]

        info_table = Table(info_data, colWidths=[1*inch, 2.5*inch, 1*inch, 1.5*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 24))

        # Line items
        story.append(Paragraph("Invoice Details", styles['Heading2']))
        story.append(Spacer(1, 12))

        # Items table
        items_data = [['Description', 'Quantity', 'Unit', 'Unit Price', 'Total']]
        for item in invoice.items:
            items_data.append([
                item.description,
                str(item.quantity),
                item.unit,
                f"${item.unit_price:.2f}",
                f"${item.total:.2f}"
            ])

        # Add totals
        items_data.append(['', '', '', 'Subtotal:', f"${invoice.subtotal:.2f}"])
        items_data.append(['', '', '', f'Tax ({invoice.tax_rate*100:.1f}%):', f"${invoice.tax_amount:.2f}"])
        items_data.append(['', '', '', 'Total Amount:', f"${invoice.total_amount:.2f}"])

        items_table = Table(items_data, colWidths=[3*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
        items_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
            ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -4), 1, colors.black),
            ('LINEBELOW', (3, -3), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('BACKGROUND', (3, -1), (-1, -1), colors.lightgrey),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 24))

        # Payment information
        story.append(Paragraph("Payment Information", styles['Heading3']))
        payment_info = f"""
        Amount Due: ${invoice.total_amount:.2f}
        Payment Terms: {invoice.payment_terms}
        Please remit payment to SPANKKS Construction.
        Thank you for your business!
        """
        story.append(Paragraph(payment_info, styles['Normal']))

        # Build PDF
        doc.build(story)
        logger.info(f"Generated invoice PDF: {filename}")
        return filename

    except Exception as e:
        logger.error(f"Error generating invoice PDF: {e}")
        return None

class StorageService:
    """Storage service"""