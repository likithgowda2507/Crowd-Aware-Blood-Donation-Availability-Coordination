import requests
import time
import os

BASE_URL = "http://127.0.0.1:5000/api"

def test_full_flow():
    session = requests.Session()
    
    # 0. Register a new donor
    print("0. Testing Registration...")
    timestamp = int(time.time())
    donor_email = f"donor_{timestamp}@example.com"
    donor_user = f"donor_{timestamp}"
    
    reg_data = {
        "username": donor_user,
        "email": donor_email,
        "password": "password123",
        "role": "donor"
    }
    
    resp = session.post(f"{BASE_URL}/register", json=reg_data)
    if resp.status_code == 201:
        print("   Registration successful.")
    elif resp.status_code == 400 and "already" in resp.text:
       print("   User already exists (ok for retry).")
    else:
       print(f"   Registration failed: {resp.text}")
       return

    # 1. Login as Donor
    print("1. Testing Donor Login...")
    login_data = {
        "email": donor_email,
        "password": "password123",
        "role": "donor"
    }
    resp = session.post(f"{BASE_URL}/login", json=login_data)
    assert resp.status_code == 200, f"Donor login failed: {resp.text}"
    donor_id = resp.json()['user_id']
    print("   Donor login successful.")
    
    # 2. Upload Report
    print("2. Testing Report Upload...")
    # Create a dummy file
    with open("dummy_report.txt", "w") as f:
        f.write("This is a dummy blood report.")
        
    with open("dummy_report.txt", "rb") as f:
        files = {'report': f}
        data = {'donor_id': donor_id}
        resp = session.post(f"{BASE_URL}/upload_report", files=files, data=data)
        
    assert resp.status_code == 201, f"Upload failed: {resp.text}"
    print("   Report uploaded successfully.")
    os.remove("dummy_report.txt")
    
    # 3. Login as Admin
    print("3. Testing Admin Login...")
    admin_data = {
        "email": "admin@bloodconnect.com",
        "password": "admin123",
        "role": "admin"
    }
    resp = session.post(f"{BASE_URL}/login", json=admin_data)
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    print("   Admin login successful.")
    
    # 4. View Reports
    print("4. Testing View Reports...")
    resp = session.get(f"{BASE_URL}/reports")
    assert resp.status_code == 200, f"Get reports failed: {resp.text}"
    reports = resp.json()
    print(f"   Found {len(reports)} reports.")
    
    # Find our report
    my_report = None
    for r in reports:
        if r['donor_name'] == donor_user and r['status'] == 'pending':
            my_report = r
            break
            
    assert my_report is not None, "Newly uploaded report not found in pending list."
    print("   Found pending report.")
    
    # 5. Verify Report
    print("5. Testing Verify Report...")
    verify_data = {"action": "approve"}
    resp = session.post(f"{BASE_URL}/verify_report/{my_report['id']}", json=verify_data)
    assert resp.status_code == 200, f"Verify failed: {resp.text}"
    print("   Report approved.")
    
    # 6. Check Status Again
    resp = session.get(f"{BASE_URL}/reports")
    reports = resp.json()
    updated_report = next((r for r in reports if r['id'] == my_report['id']), None)
    assert updated_report['status'] == 'approved', "Status not updated."
    print("   Verification confirmed.")
    
    print("\nALL TESTS PASSED!")

if __name__ == "__main__":
    try:
        test_full_flow()
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
