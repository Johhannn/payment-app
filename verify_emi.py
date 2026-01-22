import requests
from datetime import datetime, timedelta

base_url = 'http://127.0.0.1:8000'
email = 'admin@example.com' # Assuming admin exists
password = 'adminpassword123'

print("--- Starting EMI Schedule Verification ---")

# 1. Login as Admin
print(f"1. Attempting login as Admin ({email})...")
try:
    auth_resp = requests.post(f"{base_url}/token/", json={'email': email, 'password': password})
    if auth_resp.status_code == 200:
        print("   SUCCESS: Admin logged in.")
        tokens = auth_resp.json()
        access_token = tokens['access']
        headers = {'Authorization': f'Bearer {access_token}'}

        # 2. Get Users to find a student ID
        print("2. Fetching users to find a student...")
        users_resp = requests.get(f"{base_url}/users/", headers=headers)
        if users_resp.status_code == 200:
            users = users_resp.json()
            student = next((u for u in users if u['role'] == 'Student'), None)
            
            if student:
                print(f"   Found Student: {student['email']} (ID: {student['id']})")
                
                # 3. Create EMI Schedule
                print("3. Creating EMI Schedule...")
                schedule_data = {
                    'user': student['id'],
                    'total_loan': 50000,
                    'tenure_months': 12,
                    'interest_rate': 10,
                    'first_due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                }
                
                create_resp = requests.post(f"{base_url}/emi/create/", json=schedule_data, headers=headers)
                print(f"   Status Code: {create_resp.status_code}")
                
                if create_resp.status_code == 201:
                    print("   SUCCESS: EMI Schedule created.")
                    print(f"   Response: {create_resp.json()[:1]} ... (truncated)")
                    print("\nVerification: PASSED")
                else:
                    print(f"   FAILED: {create_resp.text}")
                    
            else:
                print("   FAILED: No student user found to assign EMI.")
        else:
            print(f"   FAILED: Could not fetch users. {users_resp.text}")

    else:
        print(f"   FAILED: Login failed. {auth_resp.text}")

except Exception as e:
    print(f"\nEXCEPTION: {e}")

print("--- End Verification ---")
