import requests
import time
import os

BASE_URL = "http://127.0.0.1:5001/api"

def test_donation_type():
    print("Testing Registration with Donation Type...")
    timestamp = int(time.time())
    
    # Test Paid Donation
    username = f"paid_donor_{timestamp}"
    email = f"paid_{timestamp}@example.com"
    
    #Create dummy file
    with open("paid_report.txt", "w") as f: f.write("Paid Report")
    
    with open("paid_report.txt", "rb") as f:
        print(f"Registering {username} as PAID donor...")
        files = {'report': f}
        data = {
            'username': username,
            'email': email,
            'password': 'password123',
            'role': 'donor',
            'donation_type': 'Paid'
        }
        resp = session.post(f"{BASE_URL}/register", data=data, files=files)
        assert resp.status_code == 201, f"Registration failed: {resp.text}"

    # Verify Admin side
    print("Verifying Admin View...")
    login_data = {"email": "admin@bloodconnect.com", "password": "admin123", "role": "admin"}
    # Admin might need to be created if DB was wiped. 
    # But wait, app.py doesn't auto-create admin? 
    # Usually I should rely on the app to be running.
    # If I wiped the DB, I need to make sure Admin exists.
    # I'll rely on the previous flow or just create one here if login fails.
    
    resp = session.post(f"{BASE_URL}/login", json=login_data)
    if resp.status_code != 200:
        print("Admin not found (DB wiped?), creating admin...")
        session.post(f"{BASE_URL}/register", json={
            "username": "admin", "email": "admin@bloodconnect.com", "password": "admin123", "role": "admin"
        })
        resp = session.post(f"{BASE_URL}/login", json=login_data)
        assert resp.status_code == 200, "Admin login failed after creation"

    resp = session.get(f"{BASE_URL}/reports")
    reports = resp.json()
    
    found = False
    for r in reports:
        if r['donor_name'] == username:
            print(f"Found report. Donation Type: {r.get('donation_type')}")
            if r.get('donation_type') == 'Paid':
                found = True
            break
            
    if found:
        print("TEST PASSED: Donation Type 'Paid' correctly saved and retrieved.")
    else:
        print("TEST FAILED: Type mismatch or report not found.")
        
    # DIRECT DB CHECK
    import sqlite3
    try:
        conn = sqlite3.connect('database/blood_donation.db')
        cursor = conn.cursor()
        
        # Check columns
        cursor.execute("PRAGMA table_info(user)")
        columns = [info[1] for info in cursor.fetchall()]
        print(f"DB Columns in User table: {columns}")
        
        if 'donation_type' not in columns:
            print("CRITICAL: donation_type column MISSING in DB")
        
        # Check data
        cursor.execute("SELECT username, donation_type FROM user WHERE username=?", (username,))
        row = cursor.fetchone()
        print(f"DB Row for {username}: {row}")
        
        conn.close()
    except Exception as e:
        print(f"DB Check failed: {e}")

    if os.path.exists("paid_report.txt"):
        os.remove("paid_report.txt")

if __name__ == "__main__":
    session = requests.Session()
    test_donation_type()
