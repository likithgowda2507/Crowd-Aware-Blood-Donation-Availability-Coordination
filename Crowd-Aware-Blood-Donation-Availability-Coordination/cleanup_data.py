from app import app, db, Campaign, Notification, BloodInventory, BloodRequest

def clean_generated_data():
    with app.app_context():
        print("Cleaning up auto-generated data...")
        
        # Delete Campaigns (Auto-created by emergency logic)
        num_camps = Campaign.query.delete()
        print(f"- Deleted {num_camps} Campaigns")
        
        # Delete Notifications (Auto-created by alerts)
        num_notifs = Notification.query.delete()
        print(f"- Deleted {num_notifs} Notifications")
        
        # Delete Mock Inventory (Seeded)
        num_inv = BloodInventory.query.delete()
        print(f"- Deleted {num_inv} Inventory items")
        
        # Delete Blood Requests (The test ones)
        num_req = BloodRequest.query.delete()
        print(f"- Deleted {num_req} Blood Requests")
        
        db.session.commit()
        print("Cleanup complete.")

if __name__ == "__main__":
    clean_generated_data()
