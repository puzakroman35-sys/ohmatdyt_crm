"""
Test API with authentication to verify last_status_change_at field
"""
import requests
import json

# Login credentials
login_data = {
    "username": "executor1",
    "password": "Executor123!"
}

print("1️⃣  Logging in as executor1...")
login_response = requests.post("http://localhost:8000/auth/login", json=login_data)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

tokens = login_response.json()
access_token = tokens.get("access_token")
print(f"✅ Login successful! Got access token.")

# Now test the cases endpoint
print("\n2️⃣  Fetching cases from /api/cases/assigned...")
headers = {
    "Authorization": f"Bearer {access_token}"
}

cases_response = requests.get("http://localhost:8000/api/cases/assigned?skip=0&limit=3", headers=headers)

if cases_response.status_code != 200:
    print(f"❌ Failed to fetch cases: {cases_response.status_code}")
    print(cases_response.text)
    exit(1)

data = cases_response.json()
print(f"✅ Successfully fetched cases!")
print(f"   Total cases: {data.get('total', 0)}")

if 'cases' in data and len(data['cases']) > 0:
    print(f"\n3️⃣  Checking first case for 'last_status_change_at' field...")
    first_case = data['cases'][0]
    
    print(f"\n📋 Case #{first_case.get('public_id', 'N/A')}:")
    print(f"   Status: {first_case.get('status', 'N/A')}")
    print(f"   Created: {first_case.get('created_at', 'N/A')}")
    print(f"   Updated: {first_case.get('updated_at', 'N/A')}")
    
    if 'last_status_change_at' in first_case:
        print(f"   ✅ last_status_change_at: {first_case['last_status_change_at']}")
        print(f"\n🎉 SUCCESS! The 'last_status_change_at' field is present in the API response!")
        
        # Calculate days since last status change
        from datetime import datetime, timezone
        last_change = datetime.fromisoformat(first_case['last_status_change_at'].replace('Z', '+00:00'))
        days_diff = (datetime.now(timezone.utc) - last_change).days
        print(f"\n⏰ Days since last status change: {days_diff} days")
        
        if days_diff >= 3:
            print(f"   ⚠️  This case should be highlighted (>= 3 days)")
        else:
            print(f"   ✓ This case is recent (< 3 days)")
    else:
        print(f"   ❌ ERROR: 'last_status_change_at' field is MISSING!")
        print(f"\n   Available fields in response:")
        for key in first_case.keys():
            print(f"      - {key}")
else:
    print("ℹ️  No cases found to test.")

print("\n" + "="*70)
print("Next steps:")
print("1. If field is present: Clear browser cache and reload http://localhost:3000/cases")
print("2. Check browser DevTools Console for any errors")
print("3. Verify the CSS styles are applied (bleed-red background for stale cases)")
print("="*70)
