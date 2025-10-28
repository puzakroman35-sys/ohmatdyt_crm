"""
Simplified BE-010 test using existing users
"""
import os
import requests

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

print("Testing BE-010 with existing users...")
print(f"API URL: {BASE_URL}")

# Try to login with existing users from scripts/create_test_admin.py
users_to_try = [
    ("admin", "Admin123!"),
    ("operator1", "Operator123!"),
    ("executor1", "Executor123!"),
]

tokens = {}

for username, password in users_to_try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    
    if response.status_code == 200:
        tokens[username] = response.json()["access_token"]
        print(f"[OK] Logged in as {username}")
    else:
        print(f"[FAIL] Could not login as {username}: {response.status_code} - {response.text}")

print(f"\nSuccessfully logged in: {list(tokens.keys())}")

# Try to list users
if "admin" in tokens:
    response = requests.get(
        f"{BASE_URL}/api/users",
        headers={"Authorization": f"Bearer {tokens['admin']}"}
    )
    print(f"\nUsers list status: {response.status_code}")
    if response.status_code == 200:
        users = response.json().get("users", [])
        print(f"Found {len(users)} users:")
        for user in users[:10]:  # Print first 10
            print(f"  - {user['username']} ({user['role']})")
