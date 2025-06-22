#!/usr/bin/env python3
import sys
sys.path.append('.')

from models import HandymanStorage

# Initialize storage
storage = HandymanStorage()

# Check quotes
quotes = storage.get_all_quotes()
print(f"Total quotes in storage: {len(quotes)}")

if quotes:
    print("\nRecent quotes:")
    for quote in quotes[-5:]:  # Last 5 quotes
        print(f"- Quote ID: {quote.id}")
        print(f"  Contact ID: {quote.contact_id}")
        print(f"  Service: {quote.service_type}")
        print(f"  Total: ${quote.total_amount}")
        print(f"  Created: {getattr(quote, 'created_date', 'N/A')}")
        print()

# Check contacts
contacts = storage.get_all_contacts()
print(f"Total contacts in storage: {len(contacts)}")

if contacts:
    print("\nRecent contacts:")
    for contact in contacts[-3:]:  # Last 3 contacts
        print(f"- Contact ID: {contact.id}")
        print(f"  Name: {contact.name}")
        print(f"  Phone: {contact.phone}")
        print(f"  Email: {contact.email}")
        print()