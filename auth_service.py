import json
import os
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service for Job Site Portal"""
    
    def __init__(self):
        self.clients_file = 'data/clients.json'
        self.staff_pin = "Money$$"  # Staff authentication PIN
        self.clients_cache = None
        self.load_clients()
    
    def load_clients(self):
        """Load client data from JSON file"""
        try:
            if os.path.exists(self.clients_file):
                with open(self.clients_file, 'r') as f:
                    self.clients_cache = json.load(f)
                logger.info(f"Loaded {len(self.clients_cache)} clients from {self.clients_file}")
            else:
                logger.warning(f"Clients file {self.clients_file} not found")
                self.clients_cache = []
        except Exception as e:
            logger.error(f"Error loading clients: {e}")
            self.clients_cache = []
    
    def find_client(self, client_id: str, job_id: str) -> Optional[Dict]:
        """Find client by client ID and job ID"""
        if not self.clients_cache:
            self.load_clients()
        
        for client in self.clients_cache:
            if client.get('clientId') == client_id and client.get('jobId') == job_id:
                return client
        return None
    
    def authenticate(self, client_id: str, job_id: str, staff_pin: Optional[str] = None) -> Tuple[bool, Optional[Dict], str]:
        """
        Authenticate user and determine access level
        
        Returns:
            (success: bool, client_data: dict, access_level: str)
            access_level can be 'client', 'staff', or 'denied'
        """
        # Find the client/job combination
        client = self.find_client(client_id, job_id)
        
        if not client:
            logger.warning(f"Authentication failed: Invalid client ID {client_id} or job ID {job_id}")
            return False, None, 'denied'
        
        # Check if staff PIN provided and valid
        if staff_pin:
            if staff_pin == self.staff_pin:
                logger.info(f"Staff authentication successful for {client_id}/{job_id}")
                return True, client, 'staff'
            else:
                logger.warning(f"Invalid staff PIN for {client_id}/{job_id}")
                return False, None, 'denied'
        
        # Client access (no PIN required)
        logger.info(f"Client authentication successful for {client_id}/{job_id}")
        return True, client, 'client'
    
    def add_client(self, client_data: Dict) -> bool:
        """Add new client to the system"""
        try:
            if not self.clients_cache:
                self.load_clients()
            
            # Check if client already exists
            existing = self.find_client(client_data.get('clientId'), client_data.get('jobId'))
            if existing:
                logger.warning(f"Client {client_data.get('clientId')}/{client_data.get('jobId')} already exists")
                return False
            
            self.clients_cache.append(client_data)
            
            # Save to file
            with open(self.clients_file, 'w') as f:
                json.dump(self.clients_cache, f, indent=2)
            
            logger.info(f"Added new client: {client_data.get('clientId')}/{client_data.get('jobId')}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding client: {e}")
            return False
    
    def get_all_clients(self) -> list:
        """Get all clients for admin purposes"""
        if not self.clients_cache:
            self.load_clients()
        return self.clients_cache.copy()
    
    def is_staff_member(self, client_id: str, job_id: str) -> bool:
        """Check if the client ID/job ID combination belongs to a staff member"""
        client = self.find_client(client_id, job_id)
        return client and client.get('isStaff', False)

# Global authentication service instance
auth_service = AuthService()