import requests
import time
import os

BASE_URL = "http://127.0.0.1:5000/api"

def test_full_system_flow():
    session = requests.Session()
    timestamp = int(time.time())
    
    # --- DONOR FLOW ---
    print("\n--- 1. DONOR FLOW ---")
    donor_email = f"donor_{timestamp}@example.com"
    donor_user = f"donor_{timestamp}"
    
    # Register Donor
    print("Registering Donor...")
    resp = session.post(f"{BASE_URL}/register", json={
        "username": donor_user, "email": donor_email, "password": "password123", "role": "donor"
    })
    assert resp.status_code == 201 or "already" in resp.text, f"Donor Reg failed: {resp.text}"
    
    # Login Donor
    print("Logging in Donor...")
    resp = session.post(f"{BASE_URL}/login", json={
        "email": donor_email, "password": "password123", "role": "donor"
    })
    assert resp.status_code == 200, f"Donor Login failed: {resp.text}"
    donor_id = resp.json()['user_id']
    
    # Upload Report
    print("Uploading Report...")
    with open("dummy_report.txt", "w") as f: f.write("Dummy Report Content")
    with open("dummy_report.txt", "rb") as f:
        resp = session.post(f"{BASE_URL}/upload_report", files={'report': f}, data={'donor_id': donor_id})
    assert resp.status_code == 201, f"Upload failed: {resp.text}"
    os.remove("dummy_report.txt")
    print("Donor actions complete.")
    
    # --- HOSPITAL FLOW ---
    print("\n--- 2. HOSPITAL FLOW ---")
    hospital_email = f"hospital_{timestamp}@example.com"
    hospital_user = f"hospital_{timestamp}"
    
    # Register Hospital
    print("Registering Hospital...")
    resp = session.post(f"{BASE_URL}/register", json={
        "username": hospital_user, "email": hospital_email, "password": "password123", "role": "hospital"
    })
    assert resp.status_code == 201, f"Hospital Reg failed: {resp.text}"
    
    # Login Hospital
    print("Logging in Hospital...")
    resp = session.post(f"{BASE_URL}/login", json={
        "email": hospital_email, "password": "password123", "role": "hospital"
    })
    assert resp.status_code == 200, f"Hospital Login failed: {resp.text}"
    hospital_id = resp.json()['user_id']
    
    # Request Blood
    print("Submitting Blood Request...")
    req_data = {
        "hospital_id": hospital_id,
        "patient_name": "John Doe",
        "patient_id": "PT-1001",
        "blood_group": "A+",
        "units": 2,
        "priority": "urgent",
        "reason": "Surgery",
        "blood_bank": "City Blood Bank"
    }
    resp = session.post(f"{BASE_URL}/request_blood", json=req_data)
    assert resp.status_code == 201, f"Request failed: {resp.text}"
    
    # Check Hospital Requests (Pending)
    print("Checking My Requests (expecting Pending)...")
    resp = session.get(f"{BASE_URL}/hospital/requests?hospital_id={hospital_id}")
    req_list = resp.json()
    my_request = req_list[0]
    assert my_request['status'] == 'pending', "Request should be pending"
    print("Hospital actions complete.")

    # --- ADMIN FLOW ---
    print("\n--- 3. ADMIN FLOW ---")
    
    # Login Admin
    print("Logging in Admin...")
    resp = session.post(f"{BASE_URL}/login", json={
        "email": "admin@bloodconnect.com", "password": "admin123", "role": "admin"
    })
    assert resp.status_code == 200, f"Admin Login failed: {resp.text}"
    
    # Verify Donor Report
    print("Verifying Donor Report...")
    resp = session.get(f"{BASE_URL}/reports")
    report_list = resp.json()
    target_report = next((r for r in report_list if r['donor_name'] == donor_user), None)
    assert target_report, "Uploaded report not found"
    
    resp = session.post(f"{BASE_URL}/verify_report/{target_report['id']}", json={"action": "approve"})
    assert resp.status_code == 200, "Report verification failed"
    print("Report approved.")
    
    # Verify Hospital Request
    print("Verifying Hospital Request...")
    resp = session.get(f"{BASE_URL}/admin/requests")
    admin_requests = resp.json()
    target_request = next((r for r in admin_requests if r['hospital_name'] == hospital_user), None)
    assert target_request, "Hospital request not found for admin"
    
    resp = session.post(f"{BASE_URL}/admin/verify_request/{target_request['id']}", json={"action": "approve"})
    assert resp.status_code == 200, "Request verification failed"
    print("Blood request approved.")
    
    # --- FINAL CHECK ---
    print("\n--- 4. FINAL STATUS CHECK ---")
    resp = session.get(f"{BASE_URL}/hospital/requests?hospital_id={hospital_id}")
    req_list = resp.json()
    final_req = req_list[0]
    assert final_req['status'] == 'approved', "Final status should be approved"
    print("Hospital sees Approved status.")
    
    print("\n*** ALL TESTS PASSED SUCCESSFULLY ***")

if __name__ == "__main__":
    try:
        test_full_system_flow()
    except Exception as e:
        print(f"\n!!! TEST FAILED: {e}")
