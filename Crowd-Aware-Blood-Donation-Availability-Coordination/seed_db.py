from app import app, db, User, Report, BloodRequest
from datetime import datetime, timedelta

def seed_db():
    with app.app_context():
        # Check if admin exists
        if not User.query.filter_by(role='admin').first():
             print("Creating admin...")
             admin = User(username='admin', email='admin@bloodconnect.com', role='admin', account_status='active')
             admin.set_password('admin123')
             db.session.add(admin)

        # Create Donors
        print("Creating donors...")
        donors = [
            {'name': 'John Doe', 'email': 'john@example.com', 'blood': 'A+', 'type': 'Free', 'status': 'pending', 'file': 'dummy_report.txt'},
            {'name': 'Jane Smith', 'email': 'jane@example.com', 'blood': 'O-', 'type': 'Paid', 'status': 'pending', 'file': 'dummy_report.txt'},
            {'name': 'Bob Wilson', 'email': 'bob@example.com', 'blood': 'B+', 'type': 'Free', 'status': 'approved', 'file': 'dummy_report.txt'}
        ]

        for d in donors:
            if not User.query.filter_by(email=d['email']).first():
                user = User(
                    username=d['name'], 
                    email=d['email'], 
                    role='donor', 
                    blood_group=d['blood'], 
                    donation_type=d['type'],
                    account_status=d['status'], # Account status mirrors report status mostly
                    phone='1234567890',
                    medical_conditions='None'
                )
                user.set_password('password')
                db.session.add(user)
                db.session.commit()
                
                # Create Report
                report = Report(
                    donor_id=user.id,
                    filename=d['file'],
                    status=d['status']
                )
                db.session.add(report)

        # Create Hospitals
        print("Creating hospitals...")
        hospitals = [
            {'name': 'City Hospital', 'email': 'city@hospital.com', 'status': 'pending', 'type': 'Government'},
            {'name': 'General Hospital', 'email': 'general@hospital.com', 'status': 'active', 'type': 'Private'}
        ]
        
        for h in hospitals:
             if not User.query.filter_by(email=h['email']).first():
                user = User(
                    username=h['name'],
                    email=h['email'],
                    role='hospital',
                    account_status=h['status'],
                    phone='9876543210',
                    hospital_type=h['type'],
                    address='123 Hospital St',
                    city='Metropolis',
                    registration_id='REG123'
                )
                user.set_password('password')
                db.session.add(user)

        # Create Blood Banks
        print("Creating blood banks...")
        banks = [
            {'name': 'Red Cross Bank', 'email': 'red@bank.com', 'status': 'pending', 'lic': 'LIC001'},
            {'name': 'City Blood Bank', 'email': 'city@bank.com', 'status': 'active', 'lic': 'LIC002'}
        ]

        for b in banks:
             if not User.query.filter_by(email=b['email']).first():
                user = User(
                    username=b['name'],
                    email=b['email'],
                    role='blood_bank',
                    account_status=b['status'],
                    phone='5555555555',
                    license_id=b['lic'],
                    address='456 Bank Ave',
                    city='Metropolis',
                    capacity=1000
                )
                user.set_password('password')
                db.session.add(user)
                db.session.commit()
                
                # Add Mock Inventory
                from app import BloodInventory
                
                # Add some stock
                groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
                for bg in groups:
                    stock = BloodInventory(
                        bank_id=user.id,
                        blood_group=bg,
                        units=20, # Good stock
                        expiry_date=datetime.utcnow() + timedelta(days=30)
                    )
                    db.session.add(stock)
                    
                # Add one low stock item for shortage test for the first bank
                if b['status'] == 'active':
                    shortage_stock = BloodInventory(
                        bank_id=user.id,
                        blood_group='AB-',
                        units=5, # Shortage!
                        expiry_date=datetime.utcnow() + timedelta(days=60)
                    )
                    db.session.add(shortage_stock)
                
                # Add one expiring item
                expiring_stock = BloodInventory(
                    bank_id=user.id,
                    blood_group='O+',
                    units=15,
                    expiry_date=datetime.utcnow() + timedelta(days=5) # Expires in 5 days
                )
                db.session.add(expiring_stock)

        db.session.commit()
        print("Database seeded successfully.")

if __name__ == "__main__":
    seed_db()
