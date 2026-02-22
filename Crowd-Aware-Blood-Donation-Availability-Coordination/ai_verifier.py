"""
AI Verification Service for BloodConnect
Automatically screens user registrations and flags suspicious entries
"""

import re
import json
from datetime import datetime

class AIVerifier:
    """AI-powered verification system for user registrations"""
    
    # Suspicious patterns
    SUSPICIOUS_EMAILS = [
        r'test@test\.com',
        r'fake@fake\.com',
        r'admin@admin\.com',
        r'.*@example\.com',
        r'.*@test\.com',
        r'.*@fake\.com',
        r'(.)\1{3,}@',  # Repeated characters (e.g., aaaa@)
    ]
    
    SUSPICIOUS_NAMES = [
        r'^test',
        r'^fake',
        r'^admin',
        r'^asdf',
        r'^qwerty',
        r'(.)\1{4,}',  # 5+ repeated characters
    ]
    
    def __init__(self):
        self.verification_notes = []
        self.confidence_score = 100
    
    def verify_user(self, user_data, role):
        """
        Main verification method
        Returns: (status, confidence_score, notes)
        """
        self.verification_notes = []
        self.confidence_score = 100
        
        # Common checks for all roles
        self._check_email(user_data.get('email', ''))
        self._check_phone(user_data.get('phone', ''))
        self._check_username(user_data.get('username', ''))
        
        # Role-specific checks
        if role == 'donor':
            self._verify_donor(user_data)
        elif role == 'hospital':
            self._verify_hospital(user_data)
        elif role == 'bank':
            self._verify_blood_bank(user_data)
        
        # Determine status based on confidence score
        if self.confidence_score >= 80:
            status = 'auto_approved'
        else:
            status = 'flagged'
        
        return status, self.confidence_score, json.dumps(self.verification_notes)
    
    def _check_email(self, email):
        """Validate email format and check for suspicious patterns"""
        if not email:
            self._add_flag("Missing email address", 30)
            return
        
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            self._add_flag("Invalid email format", 25)
        
        # Check suspicious patterns
        for pattern in self.SUSPICIOUS_EMAILS:
            if re.search(pattern, email.lower()):
                self._add_flag(f"Suspicious email pattern detected: {email}", 40)
                break
    
    def _check_phone(self, phone):
        """Validate phone number"""
        if not phone:
            self._add_flag("Missing phone number", 15)
            return
        
        # Remove spaces and dashes
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check if it's a valid 10-digit number
        if not re.match(r'^\d{10}$', clean_phone):
            self._add_flag("Invalid phone number format (should be 10 digits)", 20)
        
        # Check for repeated digits
        if re.search(r'(\d)\1{6,}', clean_phone):
            self._add_flag("Suspicious phone number (repeated digits)", 25)
    
    def _check_username(self, username):
        """Check username for suspicious patterns"""
        if not username:
            self._add_flag("Missing username", 20)
            return
        
        for pattern in self.SUSPICIOUS_NAMES:
            if re.search(pattern, username.lower()):
                self._add_flag(f"Suspicious username pattern: {username}", 30)
                break
    
    def _verify_donor(self, data):
        """Donor-specific verification"""
        # Check blood group
        valid_blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        blood_group = data.get('blood_group', '')
        
        if not blood_group:
            self._add_flag("Missing blood group", 15)
        elif blood_group not in valid_blood_groups:
            self._add_flag(f"Invalid blood group: {blood_group}", 25)
        
        # Check address completeness
        if not data.get('address'):
            self._add_flag("Missing address", 10)
        if not data.get('city'):
            self._add_flag("Missing city", 10)
        if not data.get('state'):
            self._add_flag("Missing state", 10)
    
    def _verify_hospital(self, data):
        """Hospital-specific verification"""
        # Check registration ID
        if not data.get('registration_id'):
            self._add_flag("Missing hospital registration ID", 25)
        
        # Check hospital type
        valid_types = ['government', 'private', 'trust', 'charitable']
        hospital_type = data.get('hospital_type', '').lower()
        
        if not hospital_type:
            self._add_flag("Missing hospital type", 15)
        elif hospital_type not in valid_types:
            self._add_flag(f"Invalid hospital type: {hospital_type}", 20)
        
        # Check contact person
        if not data.get('contact_person'):
            self._add_flag("Missing contact person name", 15)
        
        # Check address completeness
        if not data.get('address'):
            self._add_flag("Missing address", 15)
        if not data.get('city'):
            self._add_flag("Missing city", 15)
        
        # Check capacity
        capacity = data.get('capacity')
        if capacity:
            try:
                cap = int(capacity)
                if cap < 10 or cap > 10000:
                    self._add_flag(f"Unrealistic hospital capacity: {cap}", 20)
            except (ValueError, TypeError):
                self._add_flag("Invalid capacity format", 15)
    
    def _verify_blood_bank(self, data):
        """Blood bank-specific verification"""
        # Check license ID
        if not data.get('license_id'):
            self._add_flag("Missing blood bank license ID", 30)
        
        # Check operating hours
        if not data.get('operating_hours'):
            self._add_flag("Missing operating hours", 10)
        
        # Check contact person
        if not data.get('contact_person'):
            self._add_flag("Missing contact person name", 15)
        
        # Check address completeness
        if not data.get('address'):
            self._add_flag("Missing address", 15)
        if not data.get('city'):
            self._add_flag("Missing city", 15)
        
        # Check capacity
        capacity = data.get('capacity')
        if capacity:
            try:
                cap = int(capacity)
                if cap < 50 or cap > 50000:
                    self._add_flag(f"Unrealistic blood bank capacity: {cap}", 20)
            except (ValueError, TypeError):
                self._add_flag("Invalid capacity format", 15)
    
    def _add_flag(self, reason, penalty):
        """Add a verification flag and reduce confidence score"""
        self.verification_notes.append({
            'reason': reason,
            'penalty': penalty,
            'timestamp': datetime.utcnow().isoformat()
        })
        self.confidence_score = max(0, self.confidence_score - penalty)

# Singleton instance
ai_verifier = AIVerifier()
