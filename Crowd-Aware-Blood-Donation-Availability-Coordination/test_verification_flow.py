import requests
import time
import os

BASE_URL = "http://127.0.0.1:5001/api"

def test_donor_verification_flow():
    print("TEST: Donor Verification & Restricted Login")
    timestamp = int(time.time())
    username = f"verif_donor_{timestamp}"
    email = f"verif_{timestamp}@example.com"
    
    # 1. Register Donor with Profile Info (and file)
    print("1. Registering Donor...")
    with open("health_report.txt", "w") as f: f.write("Health Report Content")
    
    with open("health_report.txt", "rb") as f:
        files = {'report': f}
        data = {
            'username': username,
            'email': email,
            'password': 'password123',
            'role': 'donor',
            'donation_type': 'Paid',
            'phone': '9876543210',
            'blood_group': 'O+',
            'medical_conditions': 'None'
        }
        res = session.post(f"{BASE_URL}/register", data=data, files=files)
        print(f"   Register Status: {res.status_code}") # Expect 201
        
    # 2. Try Login (Should be BLOCKED)
    print("2. Attempting Login (Should Fail)...")
    res = session.post(f"{BASE_URL}/login", json={
        "email": email, "password": "password123", "role": "donor"
    })
    print(f"   Login Status: {res.status_code}") # Expect 403
    if res.status_code == 403:
        print("   SUCCESS: Login blocked.")
    else:
        print(f"   FAILURE: Login allowed or other error: {res.status_code}")
        return

    # 3. Create Admin (if needed, or use default)
    # Default admin is created by app.py on init
    admin_login = {"email": "admin@bloodconnect.com", "password": "admin123", "role": "admin"}
    res = session.post(f"{BASE_URL}/login", json=admin_login)
    
    # 4. Admin Verify - Check Details
    print("3. Admin Checking Reports...")
    res = session.get(f"{BASE_URL}/reports")
    reports = res.json()
    target_report_id = None
    for r in reports:
        if r['donor_name'] == username:
            target_report_id = r['id']
            print(f"   Found Report. Type: {r.get('donation_type')}, Blood: {r.get('blood_group')}, Medical: {r.get('medical_conditions')}")
            if r.get('blood_group') == 'O+':
                print("   SUCCESS: Admin sees correct details.")
            else:
                 print("   FAILURE: Admin sees wrong details.")
            break
            
    if not target_report_id:
        print("   FAILURE: Report not found.")
        return

    # 5. Approve Report
    print("4. Approving Report...")
    res = session.post(f"{BASE_URL}/verify_report/{target_report_id}", json={"action": "approve"})
    print(f"   Verify Status: {res.status_code}")

    # 6. Try Login Again (Should be ALLOWED)
    print("5. Attempting Login Again (Should Succeed)...")
    res = session.post(f"{BASE_URL}/login", json={
        "email": email, "password": "password123", "role": "donor"
    })
    print(f"   Login Status: {res.status_code}") # Expect 200
    if res.status_code == 200:
         print("   SUCCESS: Login allowed after approval.")
    else:
         print(f"   FAILURE: Login blocked/failed: {res.status_code}")

    if os.path.exists("health_report.txt"):
        os.remove("health_report.txt")

if __name__ == "__main__":
    session = requests.Session()
    test_donor_verification_flow()
