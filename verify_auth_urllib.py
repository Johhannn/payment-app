import urllib.request
import urllib.parse
import json
import ssl

# Ignore SSL certificate errors (if any)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base_url = 'http://127.0.0.1:8000'
email = 'admin@example.com'
password = 'adminpassword123'

def make_request(url, method='GET', data=None, headers=None):
    if headers is None:
        headers = {}
    
    if data:
        data_bytes = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    else:
        data_bytes = None

    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            status = response.status
            body = response.read().decode('utf-8')
            return status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        return e.code, body
    except Exception as e:
        return None, str(e)

print("--- Starting Verification (urllib) ---")

# 1. Login
login_url = f"{base_url}/token/"
print(f"1. POST {login_url}")
status, body = make_request(login_url, 'POST', {'email': email, 'password': password})
print(f"   Status: {status}")

if status == 200:
    try:
        tokens = json.loads(body)
        if 'access' in tokens:
            print("   SUCCESS: Access token obtained.")
            access_token = tokens['access']
            
            # 2. Protected Route
            users_url = f"{base_url}/users/"
            print(f"2. GET {users_url}")
            headers = {'Authorization': f'Bearer {access_token}'}
            status, body = make_request(users_url, 'GET', headers=headers)
            print(f"   Status: {status}")
            
            if status == 200:
                print("   SUCCESS: Accessed protected endpoint.")
                users = json.loads(body)
                print(f"   User count: {len(users)}")
                print("\nVERIFICATION PASSED")
            else:
                print("   FAILED to access protected endpoint.")
                print(f"   Response: {body}")
        else:
            print("   FAILED: 'access' key missing in response.")
            print(f"   Body: {body}")
    except json.JSONDecodeError:
        print("   FAILED: Invalid JSON response.")
        print(f"   Body: {body}")
else:
    print("   FAILED: Login failed.")
    print(f"   Reason: {body}")

print("--- End Verification ---")
