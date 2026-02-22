import requests
import time
import os

BASE_URL = "http://127.0.0.1:5001/api"

def test_registration_with_upload():
    print("Testing Registration with File Upload...")
    timestamp = int(time.time())
    email = f"new_donor_{timestamp}@example.com"
    username = f"new_donor_{timestamp}"
    
    #Create dummy file
    with open("reg_report.txt", "w") as f: f.write("Registration Report Content")
    
    with open("reg_report.txt", "rb") as f:
        files = {'report': f}
        data = {
            'username': username,
            'email': email,
            'password': 'password123',
            'role': 'donor'
            # Note: other fields are optional in backend model for now, or default nullable
        }
        
        try:
            resp = session.post(f"{BASE_URL}/register", data=data, files=files)
            print(f"Response Status: {resp.status_code}")
            print(f"Response Text: {resp.text}")
            
            if resp.status_code == 201:
                print("Registration successful.")
            else:
                print("Registration failed.")
                return
        except Exception as e:
            print(f"Request failed: {e}")
            return

    # Verify Admin received it
    print("Verifying Admin side...")
    login_data = {"email": "admin@bloodconnect.com", "password": "admin123", "role": "admin"}
    resp = session.post(f"{BASE_URL}/login", json=login_data)
    assert resp.status_code == 200, "Admin login failed"
    
    resp = session.get(f"{BASE_URL}/reports")
    reports = resp.json()
    
    found = False
    for r in reports:
        if r['donor_name'] == username:
            print(f"Found report for {username}: {r['filename']}")
            found = True
            break
            
    if found:
        print("TEST PASSED: Report uploaded during registration.")
    else:
        print("TEST FAILED: Report not found.")
        
    if os.path.exists("reg_report.txt"):
        os.remove("reg_report.txt")

if __name__ == "__main__":
    session = requests.Session()
    test_registration_with_upload()
