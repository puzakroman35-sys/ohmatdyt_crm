"""
Простий тест для executors-efficiency endpoint
"""
import requests

# 1. Логін як admin
print("1. Logging in as admin...")
login_response = requests.post(
    "http://localhost:8000/auth/login",
    json={
        "username": "admin",
        "password": "Admin123!"
    }
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
print(f"✅ Login successful! Token: {token[:20]}...")

# 2. Запит до executors-efficiency
print("\n2. Testing /api/dashboard/executors-efficiency...")
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(
    "http://localhost:8000/api/dashboard/executors-efficiency",
    headers=headers
)

print(f"Status code: {response.status_code}")
print(f"Response headers: {dict(response.headers)}")

if response.status_code == 200:
    print(f"✅ Success!")
    data = response.json()
    print(f"Executors count: {len(data.get('executors', []))}")
    print(f"Response: {data}")
else:
    print(f"❌ Failed!")
    print(f"Response: {response.text}")
