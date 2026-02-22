from app import app, User

with app.app_context():
    user = User.query.filter(User.username.like('%susu%')).first()
    if user:
        print(f"Found User: {user.username}, ID: {user.id}, Role: {user.role}, City: {user.city}, Address: {user.address}")
    else:
        print("User 'susu' not found.")
