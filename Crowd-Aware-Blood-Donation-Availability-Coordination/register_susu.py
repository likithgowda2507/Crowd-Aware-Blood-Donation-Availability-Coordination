import requests

url = "http://127.0.0.1:5001/api/register"
data = {
    "username": "susu",
    "email": "susu@bloodbank.com",
    "password": "susu123",
    "role": "blood_bank",
    "phone": "9998887776",
    "city": "Bangalore",
    "address": "MG Road"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
