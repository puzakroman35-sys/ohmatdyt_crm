"""
Create test users via API
"""
import requests

BASE_URL = "http://localhost:8000"

# Login as admin
print("Logging in as admin...")
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "admin", "password": "Admin123!"}
)

if response.status_code != 200:
    print(f"Failed to login: {response.status_code} - {response.text}")
    exit(1)

admin_token = response.json()["access_token"]
print(f"✓ Admin logged in successfully")

headers = {
    "Authorization": f"Bearer {admin_token}",
    "Content-Type": "application/json"
}

# Create OPERATOR
print("\nCreating OPERATOR...")
operator_data = {
    "username": "operator",
    "email": "operator@ohmatdyt.com",
    "full_name": "Test Operator",
    "password": "Operator123!",
    "role": "OPERATOR"
}

response = requests.post(
    f"{BASE_URL}/users",
    json=operator_data,
    headers=headers
)

if response.status_code == 201:
    print(f"✓ Created OPERATOR: operator (operator@ohmatdyt.com)")
elif response.status_code == 400:
    print(f"OPERATOR already exists: {response.json().get('detail', '')}")
else:
    print(f"Failed to create OPERATOR: {response.status_code} - {response.text}")

# Create EXECUTOR
print("\nCreating EXECUTOR...")
executor_data = {
    "username": "executor",
    "email": "executor@ohmatdyt.com",
    "full_name": "Test Executor",
    "password": "Executor123!",
    "role": "EXECUTOR"
}

response = requests.post(
    f"{BASE_URL}/users",
    json=executor_data,
    headers=headers
)

if response.status_code == 201:
    print(f"✓ Created EXECUTOR: executor (executor@ohmatdyt.com)")
elif response.status_code == 400:
    print(f"EXECUTOR already exists: {response.json().get('detail', '')}")
else:
    print(f"Failed to create EXECUTOR: {response.status_code} - {response.text}")

print("\n✓ Test users setup complete!")
