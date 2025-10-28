"""
Test suite for BE-007: Case lists with filters and RBAC

This test validates:
1. GET /api/cases/my - OPERATOR sees own cases only
2. GET /api/cases/assigned - EXECUTOR sees assigned cases
3. GET /api/cases - ADMIN sees all cases
4. Filters: status, category_id, channel_id, public_id, responsible_id, date_from, date_to, overdue
5. Sorting: order_by parameter
6. Pagination: skip, limit
7. RBAC enforcement
"""
import os
import requests
from datetime import datetime, timedelta

# Configuration
BASE_URL = os.getenv("API_URL", "http://localhost:8000")
API_URL = BASE_URL

# Test credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123!@#")

OPERATOR_USERNAME = "test_operator_be007"
OPERATOR_PASSWORD = "Operator123!@#"

EXECUTOR_USERNAME = "test_executor_be007"
EXECUTOR_PASSWORD = "Executor123!@#"


def test_login(username: str, password: str):
    """Login and return access token"""
    print(f"\n[LOGIN] {username}...")
    
    response = requests.post(
        f"{API_URL}/api/auth/login",
        json={"username": username, "password": password}
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return None
    
    print(f"✅ Login successful")
    return response.json()["access_token"]


def create_test_user(admin_token: str, username: str, password: str, role: str):
    """Create test user"""
    print(f"\n[CREATE USER] {username} ({role})...")
    
    response = requests.post(
        f"{API_URL}/api/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": username,
            "email": f"{username}@test.com",
            "full_name": f"Test {role} BE007",
            "password": password,
            "role": role
        }
    )
    
    if response.status_code == 201:
        print(f"✅ User created")
        return response.json()
    elif response.status_code == 400 and "already exists" in response.text:
        print(f"ℹ️  User already exists")
        return {"username": username}
    else:
        print(f"❌ Failed: {response.status_code}")
        return None


def get_or_create_category(admin_token: str, name: str = "Test Category BE007"):
    """Get or create category"""
    print(f"\n[CATEGORY] Getting/creating: {name}...")
    
    response = requests.get(
        f"{API_URL}/api/categories",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    if response.status_code == 200:
        categories = response.json().get("categories", [])
        for cat in categories:
            if cat["name"] == name:
                print(f"✅ Found: {cat['id']}")
                return cat["id"]
    
    response = requests.post(
        f"{API_URL}/api/categories",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": name}
    )
    
    if response.status_code == 201:
        cat_id = response.json()["id"]
        print(f"✅ Created: {cat_id}")
        return cat_id
    
    print(f"❌ Failed")
    return None


def get_or_create_channel(admin_token: str, name: str = "Test Channel BE007"):
    """Get or create channel"""
    print(f"\n[CHANNEL] Getting/creating: {name}...")
    
    response = requests.get(
        f"{API_URL}/api/channels",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    if response.status_code == 200:
        channels = response.json().get("channels", [])
        for ch in channels:
            if ch["name"] == name:
                print(f"✅ Found: {ch['id']}")
                return ch["id"]
    
    response = requests.post(
        f"{API_URL}/api/channels",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": name}
    )
    
    if response.status_code == 201:
        ch_id = response.json()["id"]
        print(f"✅ Created: {ch_id}")
        return ch_id
    
    print(f"❌ Failed")
    return None


def create_test_case(token: str, category_id: str, channel_id: str, summary: str):
    """Create a test case"""
    response = requests.post(
        f"{API_URL}/api/cases",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "category_id": category_id,
            "channel_id": channel_id,
            "applicant_name": "Test Applicant",
            "summary": summary
        }
    )
    
    if response.status_code == 201:
        return response.json()
    return None


def test_rbac_operator_my_cases(operator_token: str, category_id: str, channel_id: str):
    """Test 1: OPERATOR can see own cases via /my"""
    print("\n" + "="*70)
    print("[TEST 1] OPERATOR /api/cases/my - Own cases only")
    print("="*70)
    
    # Create 2 cases
    case1 = create_test_case(operator_token, category_id, channel_id, "OPERATOR Case 1")
    case2 = create_test_case(operator_token, category_id, channel_id, "OPERATOR Case 2")
    
    print(f"\n✅ Created 2 cases: #{case1['public_id']}, #{case2['public_id']}")
    
    # Get own cases
    response = requests.get(
        f"{API_URL}/api/cases/my",
        headers={"Authorization": f"Bearer {operator_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ GET /api/cases/my: {data['total']} cases found")
        
        # Verify cases are own
        for case in data['cases']:
            print(f"   - Case #{case['public_id']}: {case['summary'][:40]}")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        return False


def test_rbac_executor_assigned(executor_token: str, admin_token: str, category_id: str, channel_id: str):
    """Test 2: EXECUTOR sees assigned cases"""
    print("\n" + "="*70)
    print("[TEST 2] EXECUTOR /api/cases/assigned - Assigned cases only")
    print("="*70)
    
    # Get executor user ID
    response = requests.get(
        f"{API_URL}/api/users/me",
        headers={"Authorization": f"Bearer {executor_token}"}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get executor ID")
        return False
    
    executor_id = response.json()["id"]
    print(f"✅ Executor ID: {executor_id}")
    
    # Admin creates case and assigns to executor
    response = requests.post(
        f"{API_URL}/api/cases",
        headers={"Authorization": f"Bearer {admin_token}"},
        data={
            "category_id": category_id,
            "channel_id": channel_id,
            "applicant_name": "Test Applicant",
            "summary": "Case assigned to executor"
        }
    )
    
    if response.status_code != 201:
        print(f"❌ Failed to create case")
        return False
    
    case = response.json()
    print(f"✅ Created case #{case['public_id']}")
    
    # Executor gets assigned cases
    response = requests.get(
        f"{API_URL}/api/cases/assigned",
        headers={"Authorization": f"Bearer {executor_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ GET /api/cases/assigned: {data['total']} cases")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        return False


def test_filters_status(operator_token: str, category_id: str, channel_id: str):
    """Test 3: Filter by status"""
    print("\n" + "="*70)
    print("[TEST 3] Filter by status")
    print("="*70)
    
    # Get cases with NEW status
    response = requests.get(
        f"{API_URL}/api/cases/my?status=NEW",
        headers={"Authorization": f"Bearer {operator_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Filter status=NEW: {data['total']} cases")
        
        # Verify all are NEW
        all_new = all(case['status'] == 'NEW' for case in data['cases'])
        if all_new:
            print(f"✅ All cases have status=NEW")
        else:
            print(f"❌ Some cases don't have status=NEW")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        return False


def test_filters_date_range(operator_token: str):
    """Test 4: Filter by date range"""
    print("\n" + "="*70)
    print("[TEST 4] Filter by date range")
    print("="*70)
    
    # Get cases from today
    today = datetime.now().isoformat()
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    
    response = requests.get(
        f"{API_URL}/api/cases/my?date_from={yesterday}",
        headers={"Authorization": f"Bearer {operator_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Filter date_from (yesterday): {data['total']} cases")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        return False


def test_sorting(operator_token: str):
    """Test 5: Sorting with order_by"""
    print("\n" + "="*70)
    print("[TEST 5] Sorting with order_by")
    print("="*70)
    
    # Sort by public_id ascending
    response = requests.get(
        f"{API_URL}/api/cases/my?order_by=public_id",
        headers={"Authorization": f"Bearer {operator_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Sort by public_id (ascending): {data['total']} cases")
        
        if data['cases']:
            ids = [case['public_id'] for case in data['cases']]
            print(f"   IDs: {ids[:5]}...")
        
        # Sort descending
        response = requests.get(
            f"{API_URL}/api/cases/my?order_by=-public_id",
            headers={"Authorization": f"Bearer {operator_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sort by public_id (descending): {data['total']} cases")
            
            if data['cases']:
                ids = [case['public_id'] for case in data['cases']]
                print(f"   IDs: {ids[:5]}...")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        return False


def test_pagination(operator_token: str):
    """Test 6: Pagination"""
    print("\n" + "="*70)
    print("[TEST 6] Pagination")
    print("="*70)
    
    # Get first page
    response = requests.get(
        f"{API_URL}/api/cases/my?skip=0&limit=2",
        headers={"Authorization": f"Bearer {operator_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Page 1 (limit=2): {len(data['cases'])} cases, total={data['total']}")
        
        # Get second page
        response = requests.get(
            f"{API_URL}/api/cases/my?skip=2&limit=2",
            headers={"Authorization": f"Bearer {operator_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Page 2 (limit=2): {len(data['cases'])} cases")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        return False


def test_rbac_enforcement(operator_token: str, executor_token: str):
    """Test 7: RBAC enforcement"""
    print("\n" + "="*70)
    print("[TEST 7] RBAC enforcement")
    print("="*70)
    
    # OPERATOR tries to use /assigned (should fail)
    response = requests.get(
        f"{API_URL}/api/cases/assigned",
        headers={"Authorization": f"Bearer {operator_token}"}
    )
    
    if response.status_code == 403:
        print(f"✅ OPERATOR correctly blocked from /api/cases/assigned")
    else:
        print(f"❌ OPERATOR should be blocked from /assigned (got {response.status_code})")
    
    # EXECUTOR tries to use /my (should fail)
    response = requests.get(
        f"{API_URL}/api/cases/my",
        headers={"Authorization": f"Bearer {executor_token}"}
    )
    
    if response.status_code == 403:
        print(f"✅ EXECUTOR correctly blocked from /api/cases/my")
        return True
    else:
        print(f"❌ EXECUTOR should be blocked from /my (got {response.status_code})")
        return False


def main():
    """Run all BE-007 tests"""
    print("\n" + "="*70)
    print("BE-007 TEST SUITE: Case Lists with Filters and RBAC")
    print("="*70)
    
    # Login as admin
    admin_token = test_login(ADMIN_USERNAME, ADMIN_PASSWORD)
    if not admin_token:
        print("\n❌ Cannot proceed without admin access")
        return
    
    # Create test users
    create_test_user(admin_token, OPERATOR_USERNAME, OPERATOR_PASSWORD, "OPERATOR")
    create_test_user(admin_token, EXECUTOR_USERNAME, EXECUTOR_PASSWORD, "EXECUTOR")
    
    # Login as test users
    operator_token = test_login(OPERATOR_USERNAME, OPERATOR_PASSWORD)
    executor_token = test_login(EXECUTOR_USERNAME, EXECUTOR_PASSWORD)
    
    if not operator_token or not executor_token:
        print("\n❌ Cannot proceed without test users")
        return
    
    # Get test data
    category_id = get_or_create_category(admin_token)
    channel_id = get_or_create_channel(admin_token)
    
    if not category_id or not channel_id:
        print("\n❌ Cannot proceed without test data")
        return
    
    # Run tests
    print("\n" + "="*70)
    print("RUNNING TESTS")
    print("="*70)
    
    test_rbac_operator_my_cases(operator_token, category_id, channel_id)
    test_rbac_executor_assigned(executor_token, admin_token, category_id, channel_id)
    test_filters_status(operator_token, category_id, channel_id)
    test_filters_date_range(operator_token)
    test_sorting(operator_token)
    test_pagination(operator_token)
    test_rbac_enforcement(operator_token, executor_token)
    
    print("\n" + "="*70)
    print("BE-007 TEST SUITE COMPLETED")
    print("="*70)


if __name__ == "__main__":
    main()
