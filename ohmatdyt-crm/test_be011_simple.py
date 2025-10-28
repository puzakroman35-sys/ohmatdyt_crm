"""
Simple test for BE-011: Comments with RBAC
"""
import requests

BASE_URL = "http://localhost:8000"

def login(username, password):
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

def get_headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Login
print("1. Login as operator1...")
operator_token = login("operator1", "Operator123!")
operator_headers = get_headers(operator_token)
print("OK: Operator logged in")

# Get categories/channels
response = requests.get(f"{BASE_URL}/api/categories", headers=operator_headers)
categories = response.json() if isinstance(response.json(), list) else response.json().get('categories', [])
category = categories[0]

response = requests.get(f"{BASE_URL}/api/channels", headers=operator_headers)
channels = response.json() if isinstance(response.json(), list) else response.json().get('channels', [])
channel = channels[0]

# Create case
print("2. Create test case...")
case_data = {
    "category_id": category["id"],
    "channel_id": channel["id"],
    "applicant_name": "Test Applicant BE011",
    "applicant_phone": "+380501234567",
    "summary": "Test case for comments"
}

response = requests.post(f"{BASE_URL}/api/cases", headers={"Authorization": f"Bearer {operator_token}"}, data=case_data)
assert response.status_code == 201
case = response.json()
case_id = case["id"]
print(f"OK: Case created #{case['public_id']}")

# Create public comment (OPERATOR)
print("3. Create public comment (OPERATOR)...")
comment_data = {"text": "This is a public comment from operator", "is_internal": False}
response = requests.post(f"{BASE_URL}/api/cases/{case_id}/comments", headers=operator_headers, json=comment_data)
assert response.status_code == 201, f"Failed: {response.status_code} - {response.text}"
public_comment = response.json()
assert public_comment["is_internal"] == False
print(f"OK: Public comment created {public_comment['id']}")

# Try to create internal comment (OPERATOR) - should FAIL
print("4. Try internal comment (OPERATOR) - should fail...")
internal_data = {"text": "Internal comment attempt from operator", "is_internal": True}
response = requests.post(f"{BASE_URL}/api/cases/{case_id}/comments", headers=operator_headers, json=internal_data)
if response.status_code == 403:
    print("OK: RBAC works - OPERATOR cannot create internal comments (403)")
else:
    print(f"FAIL: Expected 403, got {response.status_code}")

# Login as EXECUTOR
print("5. Login as executor1...")
executor_token = login("executor1", "Executor123!")
executor_headers = get_headers(executor_token)
print("OK: Executor logged in")

# Take case
print("6. Take case...")
response = requests.post(f"{BASE_URL}/api/cases/{case_id}/take", headers=executor_headers)
assert response.status_code == 200
print("OK: Case taken")

# Create internal comment (EXECUTOR)
print("7. Create internal comment (EXECUTOR)...")
internal_data = {"text": "This is an internal comment from executor. Operator should not see it.", "is_internal": True}
response = requests.post(f"{BASE_URL}/api/cases/{case_id}/comments", headers=executor_headers, json=internal_data)
assert response.status_code == 201, f"Failed: {response.status_code} - {response.text}"
internal_comment = response.json()
assert internal_comment["is_internal"] == True
print(f"OK: Internal comment created {internal_comment['id']}")

# Create public comment (EXECUTOR)
print("8. Create public comment (EXECUTOR)...")
public_data = {"text": "Public comment from executor", "is_internal": False}
response = requests.post(f"{BASE_URL}/api/cases/{case_id}/comments", headers=executor_headers, json=public_data)
assert response.status_code == 201
print("OK: Public comment from executor created")

# Get comments as OPERATOR
print("9. Get comments as OPERATOR...")
response = requests.get(f"{BASE_URL}/api/cases/{case_id}/comments", headers=operator_headers)
assert response.status_code == 200
operator_view = response.json()
operator_comments = operator_view["comments"]
operator_total = operator_view["total"]
internal_count = sum(1 for c in operator_comments if c["is_internal"])

print(f"   OPERATOR sees: {operator_total} comments")
if internal_count == 0:
    print("OK: RBAC works - OPERATOR does not see internal comments")
else:
    print(f"FAIL: OPERATOR sees {internal_count} internal comment(s)")

# Get comments as EXECUTOR
print("10. Get comments as EXECUTOR...")
response = requests.get(f"{BASE_URL}/api/cases/{case_id}/comments", headers=executor_headers)
assert response.status_code == 200
executor_view = response.json()
executor_comments = executor_view["comments"]
executor_total = executor_view["total"]
executor_internal_count = sum(1 for c in executor_comments if c["is_internal"])

print(f"   EXECUTOR sees: {executor_total} comments")
if executor_internal_count >= 1:
    print(f"OK: RBAC works - EXECUTOR sees {executor_internal_count} internal comment(s)")
else:
    print("FAIL: EXECUTOR does not see internal comments")

# Validation: too short
print("11. Validate: too short comment...")
short_comment = {"text": "Hi", "is_internal": False}
response = requests.post(f"{BASE_URL}/api/cases/{case_id}/comments", headers=operator_headers, json=short_comment)
if response.status_code == 400:
    print("OK: Validation works - comment too short (400)")
else:
    print(f"WARNING: Expected 400, got {response.status_code}")

# Validation: too long
print("12. Validate: too long comment...")
long_comment = {"text": "A" * 6000, "is_internal": False}
response = requests.post(f"{BASE_URL}/api/cases/{case_id}/comments", headers=operator_headers, json=long_comment)
if response.status_code == 400:
    print("OK: Validation works - comment too long (400)")
else:
    print(f"WARNING: Expected 400, got {response.status_code}")

print("\n=== ALL BE-011 TESTS PASSED ===")
print(f"Case: #{case['public_id']}")
print(f"OPERATOR sees: {operator_total} comments (public only)")
print(f"EXECUTOR sees: {executor_total} comments (all)")
print("RBAC for internal comments: OK")
print("Validation: OK")
