from app import app, db, User, BloodInventory, BloodRequest, Campaign, Notification, Report

def reset_database():
    with app.app_context():
        print("Resetting database...")
        
        # Delete data from dependent tables first
        num_rep = Report.query.delete()
        print(f"Deleted {num_rep} reports.")
        
        num_inv = BloodInventory.query.delete()
        print(f"Deleted {num_inv} inventory items.")
        
        num_req = BloodRequest.query.delete()
        print(f"Deleted {num_req} blood requests.")
        
        num_camp = Campaign.query.delete()
        print(f"Deleted {num_camp} campaigns.")
        
        num_notif = Notification.query.delete()
        print(f"Deleted {num_notif} notifications.")
        
        # Delete users except admin
        num_users = User.query.filter(User.role != 'admin').delete()
        print(f"Deleted {num_users} users (kept admin).")
        
        db.session.commit()
        print("Database reset complete. Admin account preserved.")

if __name__ == "__main__":
    reset_database()
