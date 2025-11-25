import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API base URL
BASE_URL = "https://crm.ohmatdyt.com.ua/api"

# Login credentials (admin)
LOGIN_DATA = {
    "username": "admin",
    "password": "admin123"  # Замініть на правильний пароль
}

print("=== Testing CRM API Date Filter ===\n")

# Step 1: Login
print("1. Logging in...")
try:
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json=LOGIN_DATA,
        verify=False,
        timeout=10
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        exit(1)
    
    tokens = login_response.json()
    access_token = tokens.get("access_token")
    print(f"✅ Login successful")
    print(f"   Token: {access_token[:50]}...")
    
except Exception as e:
    print(f"❌ Error during login: {e}")
    exit(1)

# Step 2: Test date filter
print("\n2. Testing date filter (2025-11-25)...")
headers = {
    "Authorization": f"Bearer {access_token}"
}

params = {
    "skip": 0,
    "limit": 20,
    "date_from": "2025-11-25",
    "date_to": "2025-11-25",
    "order_by": "-created_at"
}

try:
    cases_response = requests.get(
        f"{BASE_URL}/cases",
        params=params,
        headers=headers,
        verify=False,
        timeout=10
    )
    
    if cases_response.status_code != 200:
        print(f"❌ API request failed: {cases_response.status_code}")
        print(cases_response.text)
        exit(1)
    
    data = cases_response.json()
    cases = data.get("cases", [])
    total = data.get("total", 0)
    
    print(f"✅ API Response:")
    print(f"   Total: {total}")
    print(f"   Cases returned: {len(cases)}")
    print()
    
    if cases:
        print("   Cases found:")
        for case in cases:
            print(f"     #{case.get('public_id')}: {case.get('applicant_name')}")
            print(f"       Created: {case.get('created_at')}")
            print(f"       Status: {case.get('status')}")
            print()
    else:
        print("   ⚠️  No cases found for date 2025-11-25!")
        print()
        print("   Expected to find case #119179 (created at 14:06:21)")
        
except Exception as e:
    print(f"❌ Error during API request: {e}")
    exit(1)
