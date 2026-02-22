import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:5001/api'

def test_bank_features():
    print("Testing Blood Bank Features...")
    
    # 1. Create a Blood Bank User
    print("\n1. creating/finding blood bank...")
    # Register a test bank (might fail if exists, that's fine)
    bank_data = {
        "username": "TestBank",
        "email": "testbank@example.com",
        "password": "password123",
        "role": "blood_bank",
        "blood_group": "N/A",
        "city": "Test City"
    }
    res = requests.post(f"{BASE_URL}/register", json=bank_data)
    print(f"Register status: {res.status_code}")
    
    # Login to get ID
    login_data = {"email": "testbank@example.com", "password": "password123"}
    res = requests.post(f"{BASE_URL}/login", json=login_data)
    if res.status_code != 200:
        print("Login failed, aborting.")
        return
        
    user_id = res.json().get('user_id')
    print(f"Logged in as Bank ID: {user_id}")
    
    # 2. Update Inventory
    print("\n2. Updating Inventory...")
    inv_data = {
        "bank_id": user_id,
        "blood_group": "A+",
        "units": 10,
        "expiry_date": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    }
    res = requests.post(f"{BASE_URL}/inventory/update", json=inv_data)
    print(f"Add Stock: {res.status_code} - {res.json()}")
    
    # Verify Inventory
    res = requests.get(f"{BASE_URL}/bank/inventory/{user_id}")
    print(f"Inventory Check: {res.json()}")
    
    # 3. Create Campaign
    print("\n3. Creating Campaign...")
    camp_data = {
        "organizer_id": user_id,
        "name": "Test Camp 2026",
        "location": "Central Park",
        "date": (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d'),
        "start_time": "10:00",
        "end_time": "14:00",
        "target_blood_groups": "All"
    }
    res = requests.post(f"{BASE_URL}/campaigns", json=camp_data)
    print(f"Create Camp: {res.status_code} - {res.json()}")
    
    # Verify Camp Listing
    res = requests.get(f"{BASE_URL}/campaigns")
    camps = res.json()
    print(f"Total Camps: {len(camps)}")
    
    # 4. Check Requests (Empty initially)
    print("\n4. Checking Requests...")
    res = requests.get(f"{BASE_URL}/bank/requests/{user_id}")
    print(f"Requests: {res.json()}")
    
    print("\nTest Complete.")

if __name__ == "__main__":
    test_bank_features()
