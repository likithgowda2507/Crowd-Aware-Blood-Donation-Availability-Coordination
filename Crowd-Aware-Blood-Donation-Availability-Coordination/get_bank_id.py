from app import app, User

with app.app_context():
    bank = User.query.filter_by(role='blood_bank').first()
    if bank:
        print(f"Bank ID: {bank.id}")
    else:
        print("No bank found")
