"""
Test script to verify last_status_change_at field in API response
"""
import requests
import json

# API endpoint
url = "http://localhost:8000/api/cases/my?skip=0&limit=3"

# You need to login first and get a valid token
# For now, just testing the endpoint structure
try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print("\n❌ Need authentication. Login first to get a token.")
        print("This is expected - the endpoint requires authentication.")
    else:
        data = response.json()
        print(f"\n✅ Response structure:")
        print(json.dumps(data, indent=2))
        
        if 'cases' in data and len(data['cases']) > 0:
            first_case = data['cases'][0]
            if 'last_status_change_at' in first_case:
                print(f"\n✅ SUCCESS: 'last_status_change_at' field is present!")
                print(f"   Value: {first_case['last_status_change_at']}")
            else:
                print(f"\n❌ ERROR: 'last_status_change_at' field is MISSING")
                print(f"   Available fields: {list(first_case.keys())}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("To test properly:")
print("1. Login at http://localhost:3000")
print("2. Open browser DevTools (F12)")
print("3. Go to Network tab")
print("4. Navigate to http://localhost:3000/cases")
print("5. Find the API request to /api/cases/my or /api/cases/assigned")
print("6. Check if 'last_status_change_at' is present in the response")
print("="*60)
