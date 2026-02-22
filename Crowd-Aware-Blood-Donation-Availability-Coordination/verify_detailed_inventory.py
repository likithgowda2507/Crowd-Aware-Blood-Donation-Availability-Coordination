import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:5001/api'

def test_detailed_inventory():
    print("Testing Detailed Inventory API...")
    
    # 1. Get a valid Bank ID
    print("Fetching list of banks...")
    res = requests.get(f"{BASE_URL}/banks")
    if res.status_code != 200:
        print("Failed to fetch banks.")
        return
        
    banks = res.json()
    if not banks:
        print("No banks found. Cannot test.")
        return
        
    target_bank = banks[0]
    user_id = target_bank['id']
    print(f"Testing with Bank: {target_bank['name']} (ID: {user_id})")
    
    # 2. Check Detailed API
    print("Fetching detailed inventory...")
    res = requests.get(f"{BASE_URL}/bank/inventory/details/{user_id}")
    if res.status_code == 200:
        data = res.json()
        print(f"Retrieved {len(data)} items.")
        if len(data) > 0:
            for item in data:
                print(f"- {item['bag_id']} | {item['blood_group']} | {item['status']} | {item['volume']}")
        
        # Always add test stock to verify individual bag creation
        print("Attempting to add stock (3 units of O+)...")
        requests.post(f"{BASE_URL}/inventory/update", json={
            "bank_id": user_id,
            "blood_group": "O+",
            "units": 3,
            "expiry_date": (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
        })
        # Re-fetch
        res = requests.get(f"{BASE_URL}/bank/inventory/details/{user_id}")
        data = res.json()
        print(f"Refetched: {len(data)} items.")
        for item in data:
            print(f"- {item['bag_id']} | {item['blood_group']} | {item['status']} | {item['volume']}")
            
        # specific check
        o_plus_items = [i for i in data if i['blood_group'] == 'O+' and i['units'] == 1]
        # logic: newly added ones should have units=1 (450ml). Old one has 5 (2250ml).
        if len(o_plus_items) >= 3:
            print("SUCCESS: 3 separate O+ bags created (units=1 each).")
        else:
            print(f"FAILURE: Expected 3 O+ bags with units=1, found {len(o_plus_items)}")
            
    else:
        print(f"Failed to fetch details: {res.status_code} - {res.text}")

if __name__ == "__main__":
    test_detailed_inventory()
