"""
Initialize Database Tables from SQLAlchemy Models
This script creates all tables based on the models defined in app.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User

def init_database():
    """Initialize database tables from SQLAlchemy models"""
    print("=" * 60)
    print("Initializing Database from SQLAlchemy Models")
    print("=" * 60)
    
    with app.app_context():
        # Drop all existing tables
        print("\n🗑️  Dropping existing tables...")
        db.drop_all()
        
        # Create all tables
        print("🔨 Creating tables from models...")
        db.create_all()
        
        print("\n✅ Database tables created successfully!")
        print("\nTables created:")
        print("  - user (donors, banks, hospitals, admins)")
        print("  - report (donor medical reports)")
        print("  - blood_request (hospital blood requests)")
        print("  - blood_inventory (blood bank inventory)")
        print("  - notification (user notifications)")
        print("  - campaign (donation camps)")
        print("  - appointment (donor appointments)")
        
        # Create sample data
        print("\n📝 Creating sample data...")
        
        # Sample Blood Bank
        bank = User(
            username='citybloodbank',
            email='city@bloodbank.com',
            role='bank',
            phone='9876543210',
            contact_person='Dr. Kumar',
            address='Main Road',
            city='Pollachi',
            state='Tamil Nadu',
            pincode='642001',
            license_id='LIC-001',
            operating_hours='24/7',
            capacity=500
        )
        bank.set_password('password123')
        db.session.add(bank)
        
        # Sample Hospital
        hospital = User(
            username='cityhospital',
            email='city@hospital.com',
            role='hospital',
            phone='9876543211',
            contact_person='Dr. Sharma',
            address='Hospital Road',
            city='Pollachi',
            state='Tamil Nadu',
            pincode='642001',
            registration_id='HOSP-001',
            hospital_type='private',
            capacity=100
        )
        hospital.set_password('password123')
        db.session.add(hospital)
        
        # Sample Donor
        donor = User(
            username='johndonor',
            email='john@donor.com',
            role='donor',
            phone='9876543212',
            blood_group='O+',
            address='Donor Street',
            city='Pollachi',
            state='Tamil Nadu',
            pincode='642001',
            donation_type='Free'
        )
        donor.set_password('password123')
        db.session.add(donor)
        
        db.session.commit()
        
        print("\n✅ Sample data created!")
        print("\nSample Accounts:")
        print("  Blood Bank: city@bloodbank.com (password: password123)")
        print("  Hospital: city@hospital.com (password: password123)")
        print("  Donor: john@donor.com (password: password123)")
        
        print("\n" + "=" * 60)
        print("Database initialization complete!")
        print("=" * 60)

if __name__ == "__main__":
    init_database()
