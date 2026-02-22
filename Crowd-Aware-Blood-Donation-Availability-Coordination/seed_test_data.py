from app import app, db, User, Campaign, Appointment, Report, BloodInventory, Notification
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def seed_data():
    with app.app_context():
        # Ensure fresh start for test data (optional, but good for verification)
        # db.drop_all()
        # db.create_all()
        
        # 1. Create a Blood Bank
        bank = User.query.filter_by(email='redcross@example.com').first()
        if not bank:
            bank = User(
                username='Red Cross Blood Bank',
                email='redcross@example.com',
                password_hash=generate_password_hash('password'),
                role='blood_bank',
                address='123 Health St, Medical District',
                phone='555-0199'
            )
            db.session.add(bank)
            db.session.commit()
            print(f"Created Bank: {bank.username} (ID: {bank.id})")
        
        # 2. Create a Donor
        donor = User.query.filter_by(email='johndoe@example.com').first()
        if not donor:
            donor = User(
                username='John Doe',
                email='johndoe@example.com',
                password_hash=generate_password_hash('password'),
                role='donor',
                blood_group='O+',
                address='456 Donor Ln',
                phone='555-0200'
            )
            db.session.add(donor)
            db.session.commit()
            print(f"Created Donor: {donor.username} (ID: {donor.id})")
        
        # 3. Create a Campaign
        campaign = Campaign.query.filter_by(name='Summer Blood Drive').first()
        if not campaign:
            campaign = Campaign(
                organizer_id=bank.id,
                name='Summer Blood Drive',
                location='City Center Park',
                date=datetime.utcnow() + timedelta(days=5),
                start_time='09:00',
                end_time='17:00'
            )
            # Add description if model supports it, but checking app.py snippet, it doesn't show description.
            # Wait, snippet for Campaign showed: organizer_id, name, location, date, start_time, end_time, status, target_blood_groups, created_at.
            # It did NOT show description. So I will remove description too.
            db.session.add(campaign)
            db.session.commit()
            print(f"Created Campaign: {campaign.name} (ID: {campaign.id})")
            
        # 4. Create Past Donations (Reports)
        # Add 3 approved reports to simulate donation history
        if Report.query.filter_by(donor_id=donor.id).count() == 0:
            for i in range(3):
                report = Report(
                    donor_id=donor.id,
                    filename=f'report_{i}.pdf',
                    status='approved',
                    upload_date=datetime.utcnow() - timedelta(days=100 + (i*30)) # Past dates
                )
                db.session.add(report)
            db.session.commit()
            print("Created 3 Past Donation Reports")

        # 5. Create Appointments
        # One upcoming
        if Appointment.query.filter_by(donor_id=donor.id).count() == 0:
            upcoming_appt = Appointment(
                donor_id=donor.id,
                camp_id=campaign.id, # Booking for the campaign
                date=campaign.date,
                time_slot='10:00',
                status='scheduled'
            )
            db.session.add(upcoming_appt)
            
            # One past
            past_appt = Appointment(
                donor_id=donor.id,
                bank_id=bank.id, # Direct booking with bank
                date=datetime.utcnow() - timedelta(days=30),
                time_slot='14:00',
                status='completed'
            )
            db.session.add(past_appt)
            
            db.session.commit()
            print("Created Upcoming and Past Appointments")

        # 6. Create Notifications
        if Notification.query.filter_by(user_id=donor.id).count() == 0:
            notifs = [
                Notification(user_id=donor.id, type='urgent', message='Urgent: O+ Blood Needed by City Hospital.', created_at=datetime.utcnow() - timedelta(hours=2)),
                Notification(user_id=donor.id, type='success', message='Donation Slot Confirmed for Feb 15.', created_at=datetime.utcnow() - timedelta(days=1)),
                Notification(user_id=donor.id, type='info', message='New Camp Near You at Community Center.', created_at=datetime.utcnow() - timedelta(days=2))
            ]
            for n in notifs:
                db.session.add(n)
            db.session.commit()
            print("Created 3 Notifications")
            
        print("\nSeed Data Creation Complete.")
        print(f"Test Donor ID: {donor.id}")

if __name__ == "__main__":
    seed_data()
