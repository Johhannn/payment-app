import requests
import time
import random

base_url = 'http://127.0.0.1:8000'
rand_id = random.randint(1000, 9999)
email = f'newstudent{rand_id}@example.com'
password = 'securepassword123'
full_name = f'New Student {rand_id}'
phone_number = f'98765{rand_id}'

print("--- Starting Registration Verification ---")

# 1. Register
print(f"1. Attempting registration for {email}...")
try:
    reg_data = {
        'email': email,
        'password': password,
        'full_name': full_name,
        'phone_number': phone_number
    }
    reg_resp = requests.post(f"{base_url}/register/", json=reg_data)
    print(f"   Status Code: {reg_resp.status_code}")
    
    if reg_resp.status_code == 201:
        print("   SUCCESS: User registered.")
        print(f"   Response: {reg_resp.json()}")

        # 2. Login
        print(f"2. Attempting login for {email}...")
        auth_resp = requests.post(f"{base_url}/token/", json={'email': email, 'password': password})
        print(f"   Status Code: {auth_resp.status_code}")
        
        if auth_resp.status_code == 200:
            tokens = auth_resp.json()
            if 'access' in tokens:
                print("   SUCCESS: Access token received.")
                access_token = tokens['access']
                print("\nVerification: PASSED")
            else:
                print("   FAILED: 'access' token not found in response.")
        else:
            print(f"   FAILED: Login failed. {auth_resp.text}")

    else:
        print(f"   FAILED: Registration failed. {reg_resp.text}")

except Exception as e:
    print(f"\nEXCEPTION: {e}")
    try:
        requests.get(base_url)
    except:
        print("   Server seems to be down.")

print("--- End Verification ---")
