import requests

# Login
r = requests.post('http://localhost:8000/auth/login', json={'username': 'admin', 'password': 'Admin123!'})
print(f"Login status: {r.status_code}")
if r.ok:
    token = r.json()['access_token']
    print(f"Token: {token[:20]}...")
    
    # Create category
    r2 = requests.post('http://localhost:8000/categories', 
                       json={'name': 'TestCategory123', 'is_active': True},
                       headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})
    print(f"\nCreate category status: {r2.status_code}")
    print(f"Response: {r2.text}")
else:
    print(f"Login failed: {r.text}")
