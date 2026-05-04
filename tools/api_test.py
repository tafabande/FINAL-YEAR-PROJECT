import requests
import json

url = "http://localhost:5000/api/users"
payload = {
    "username": "apitestuser",
    "password": "password123",
    "role": "ordinary"
}
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 201:
        get_response = requests.get(url)
        print(f"User List: {get_response.text}")
except Exception as e:
    print(f"Error: {e}")
