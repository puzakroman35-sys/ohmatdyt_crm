import requests
from datetime import datetime

# Test API endpoint
url = "https://crm.ohmatdyt.com.ua/api/cases"
params = {
    "skip": 0,
    "limit": 20,
    "date_from": "2025-11-25",
    "date_to": "2025-11-25",
    "order_by": "-created_at"
}

print(f"Testing: {url}")
print(f"Params: {params}")
print()

try:
    response = requests.get(url, params=params, timeout=10, verify=False)
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        cases = data.get("cases", [])
        total = data.get("total", 0)
        
        print(f"Total cases returned: {len(cases)}")
        print(f"Total count: {total}")
        print()
        
        if cases:
            print("Cases found:")
            for case in cases:
                print(f"  - #{case.get('public_id')}: {case.get('applicant_name')} - {case.get('created_at')}")
        else:
            print("No cases found!")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
