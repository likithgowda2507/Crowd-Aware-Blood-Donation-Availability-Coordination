from app import app, db, User

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if admin exists
        if not User.query.filter_by(role='admin').first():
            print("Creating admin user...")
            admin = User(username='admin', email='admin@bloodconnect.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")
            
        print("Database initialized.")

if __name__ == "__main__":
    init_db()
