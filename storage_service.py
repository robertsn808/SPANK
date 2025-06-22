import json
import os
from datetime import datetime
import logging
from typing import List, Optional

class StorageService:
    """Comprehensive storage service for SPANKKS Construction CRM"""

    def __init__(self):
        self.data_dir = "data"
        self.ensure_data_directory()

    def ensure_data_directory(self):
        """Ensure data directory and required files exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logging.info(f"Created data directory: {self.data_dir}")

        # Initialize empty files if they don't exist
        files = ['contacts.json', 'jobs.json', 'quotes.json', 'invoices.json', 
                'service_requests.json', 'contact_messages.json']
        for file in files:
            filepath = os.path.join(self.data_dir, file)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    json.dump([], f)
                logging.info(f"Created empty data file: {file}")

    def load_data(self, filename: str) -> List[dict]:
        """Load data from JSON file with error handling"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    logging.debug(f"Loaded {len(data)} records from {filename}")
                    return data
            return []
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error loading {filename}: {e}")
            return []

    def save_data(self, filename: str, data: List[dict]) -> bool:
        """Save data to JSON file with error handling"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logging.debug(f"Saved {len(data)} records to {filename}")
            return True
        except Exception as e:
            logging.error(f"Error saving {filename}: {e}")
            return False

# Global storage instance
storage_service = StorageService()