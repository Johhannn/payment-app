import requests
import time

base_url = 'http://127.0.0.1:8000'
email = 'admin@example.com'
password = 'adminpassword123'

print("--- Starting Verification ---")

# 1. Login
print(f"1. Attempting login for {email}...")
try:
    auth_resp = requests.post(f"{base_url}/token/", json={'email': email, 'password': password})
    print(f"   Status Code: {auth_resp.status_code}")
    
    if auth_resp.status_code == 200:
        tokens = auth_resp.json()
        if 'access' in tokens:
            print("   SUCCESS: Access token received.")
            access_token = tokens['access']
            
            # 2. Protected Route
            print("2. Attempting to access protected '/users/' route...")
            headers = {'Authorization': f'Bearer {access_token}'}
            user_resp = requests.get(f"{base_url}/users/", headers=headers)
            print(f"   Status Code: {user_resp.status_code}")
            
            if user_resp.status_code == 200:
                print("   SUCCESS: Protected data received.")
                print("   User count:", len(user_resp.json()))
                print("\nVerification: PASSED")
            else:
                print(f"   FAILED: {user_resp.text}")
        else:
            print("   FAILED: 'access' token not found in response.")
            print(f"   Response: {tokens}")
    else:
        print(f"   FAILED: Login failed. {auth_resp.text}")

except Exception as e:
    print(f"\nEXCEPTION: {e}")
    # Check if server is reachable
    try:
        requests.get(base_url)
    except:
        print("   Server seems to be down.")

print("--- End Verification ---")
