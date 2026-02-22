from app import app, db, User, BloodInventory
from datetime import datetime, timedelta
import random

def seed_analytics_data():
    with app.app_context():
        print("Seeding analytics data...")
        
        # Get a blood bank
        bank = User.query.filter_by(role='blood_bank').first()
        if not bank:
            print("No blood bank found. Please run seed_db.py first.")
            return

        # Clear existing inventory for analytics purity (optional, but good for demo)
        BloodInventory.query.delete()
        
        groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        # Determine today
        today = datetime.utcnow()
        
        # Generate data for past 6 months
        for i in range(6):
            # Month offset: i=0 (this month), i=5 (5 months ago)
            # Create a date in that month
            month_date = today - timedelta(days=30 * i)
            
            # Create random inventory entries for that month
            for bg in groups:
                # Random units collected/added in that month
                units = random.randint(10, 50) 
                
                stock = BloodInventory(
                    bank_id=bank.id,
                    blood_group=bg,
                    units=units,
                    expiry_date=month_date + timedelta(days=45), # Expired or expiring, doesn't matter for trend
                    added_date=month_date
                )
                db.session.add(stock)
                
        db.session.commit()
        print("Analytics data seeded successfully.")

if __name__ == "__main__":
    seed_analytics_data()
