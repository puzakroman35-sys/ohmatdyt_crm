"""
Test BE-016: Executor Access Rules
Tests that EXECUTOR can see:
1. All NEW cases (available to take)
2. All cases where executor is assigned (responsible_id)
"""

import requests
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_case(case, prefix=""):
    """Print case information"""
    print(f"{prefix}Case #{case['public_id']}: {case['summary'][:50]}")
    print(f"{prefix}  Status: {case['status']}")
    print(f"{prefix}  Responsible: {case.get('responsible_id', 'None')}")

def get_auth_token(username, password):
    """Get authentication token"""
    response = requests.post(
        f"{API_URL}/auth/login",
        json={
            "username": username,
            "password": password
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed: {response.text}")

def test_executor_can_see_new_cases():
    """Test 1: EXECUTOR can see all NEW cases"""
    print_header("TEST 1: EXECUTOR Can See All NEW Cases")
    
    try:
        # Login as admin to create NEW cases
        admin_token = get_auth_token("admin", "Admin123!")
        print("✅ Logged in as ADMIN")
        
        # Get categories and channels
        response = requests.get(
            f"{API_URL}/api/categories",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        categories = response.json()["categories"]
        category_id = categories[0]["id"] if categories else None
        
        response = requests.get(
            f"{API_URL}/api/channels",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        channels = response.json()["channels"]
        channel_id = channels[0]["id"] if channels else None
        
        if not category_id or not channel_id:
            print("❌ No categories or channels found")
            return False
        
        # Create 2 NEW cases
        new_cases = []
        for i in range(2):
            response = requests.post(
                f"{API_URL}/api/cases",
                headers={"Authorization": f"Bearer {admin_token}"},
                data={
                    "category_id": category_id,
                    "channel_id": channel_id,
                    "applicant_name": f"Test Applicant {i+1}",
                    "applicant_phone": "+380501234567",
                    "summary": f"Test NEW case {i+1} - BE-016 Test {datetime.now().isoformat()}"
                }
            )
            if response.status_code == 201:
                case = response.json()
                new_cases.append(case)
                print(f"✅ Created NEW case #{case['public_id']}")
            else:
                print(f"❌ Failed to create case: {response.text}")
                return False
        
        # Login as executor
        executor_token = get_auth_token("executor1", "Executor123!")
        print("✅ Logged in as EXECUTOR")
        
        # Get assigned cases (should include NEW cases)
        response = requests.get(
            f"{API_URL}/api/cases/assigned",
            headers={"Authorization": f"Bearer {executor_token}"}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get assigned cases: {response.text}")
            return False
        
        data = response.json()
        executor_cases = data["cases"]
        
        print(f"\n✅ EXECUTOR sees {len(executor_cases)} total cases")
        
        # Check if NEW cases are visible
        new_case_ids = {c["id"] for c in new_cases}
        visible_new_case_ids = {c["id"] for c in executor_cases if c["id"] in new_case_ids}
        
        if len(visible_new_case_ids) == len(new_case_ids):
            print(f"✅ EXECUTOR can see all {len(new_case_ids)} NEW cases created")
            for case in executor_cases:
                if case["id"] in new_case_ids:
                    print_case(case, "  ")
            return True
        else:
            print(f"❌ EXECUTOR should see {len(new_case_ids)} NEW cases, but sees {len(visible_new_case_ids)}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_executor_can_see_assigned_cases():
    """Test 2: EXECUTOR can see cases assigned to them"""
    print_header("TEST 2: EXECUTOR Can See Assigned Cases")
    
    try:
        # Login as admin
        admin_token = get_auth_token("admin", "Admin123!")
        print("✅ Logged in as ADMIN")
        
        # Login as executor to get ID
        executor_token = get_auth_token("executor1", "Executor123!")
        response = requests.get(
            f"{API_URL}/api/users/me",
            headers={"Authorization": f"Bearer {executor_token}"}
        )
        executor_id = response.json()["id"]
        print(f"✅ Executor ID: {executor_id}")
        
        # Get categories and channels
        response = requests.get(
            f"{API_URL}/api/categories",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        categories = response.json()["categories"]
        category_id = categories[0]["id"] if categories else None
        
        response = requests.get(
            f"{API_URL}/api/channels",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        channels = response.json()["channels"]
        channel_id = channels[0]["id"] if channels else None
        
        # Create a NEW case
        response = requests.post(
            f"{API_URL}/api/cases",
            headers={"Authorization": f"Bearer {admin_token}"},
            data={
                "category_id": category_id,
                "channel_id": channel_id,
                "applicant_name": "Test Applicant",
                "applicant_phone": "+380501234567",
                "summary": f"Test case for assignment - BE-016 {datetime.now().isoformat()}"
            }
        )
        
        if response.status_code != 201:
            print(f"❌ Failed to create case: {response.text}")
            return False
        
        case = response.json()
        case_id = case["id"]
        print(f"✅ Created NEW case #{case['public_id']}")
        
        # Executor takes the case
        response = requests.post(
            f"{API_URL}/api/cases/{case_id}/take",
            headers={"Authorization": f"Bearer {executor_token}"}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to take case: {response.text}")
            return False
        
        taken_case = response.json()
        print(f"✅ Executor took case #{taken_case['public_id']}")
        print(f"  Status: {taken_case['status']}")
        print(f"  Responsible: {taken_case.get('responsible_id')}")
        
        # Verify executor can still see the case
        response = requests.get(
            f"{API_URL}/api/cases/assigned",
            headers={"Authorization": f"Bearer {executor_token}"}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get assigned cases: {response.text}")
            return False
        
        executor_cases = response.json()["cases"]
        case_ids = [c["id"] for c in executor_cases]
        
        if case_id in case_ids:
            print(f"✅ EXECUTOR can see assigned case #{taken_case['public_id']}")
            return True
        else:
            print(f"❌ EXECUTOR cannot see their assigned case")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_executor_cannot_see_other_assigned_cases():
    """Test 3: EXECUTOR cannot see cases assigned to other executors"""
    print_header("TEST 3: EXECUTOR Cannot See Other Executor's Cases")
    
    try:
        # Login as admin
        admin_token = get_auth_token("admin", "Admin123!")
        print("✅ Logged in as ADMIN")
        
        # Get categories and channels
        response = requests.get(
            f"{API_URL}/api/categories",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        categories = response.json()["categories"]
        category_id = categories[0]["id"] if categories else None
        
        response = requests.get(
            f"{API_URL}/api/channels",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        channels = response.json()["channels"]
        channel_id = channels[0]["id"] if channels else None
        
        # Create a NEW case
        response = requests.post(
            f"{API_URL}/api/cases",
            headers={"Authorization": f"Bearer {admin_token}"},
            data={
                "category_id": category_id,
                "channel_id": channel_id,
                "applicant_name": "Test Applicant",
                "applicant_phone": "+380501234567",
                "summary": f"Test case for another executor - BE-016 {datetime.now().isoformat()}"
            }
        )
        
        if response.status_code != 201:
            print(f"❌ Failed to create case: {response.text}")
            return False
        
        case = response.json()
        case_id = case["id"]
        print(f"✅ Created NEW case #{case['public_id']}")
        
        # Admin takes the case (simulating another executor)
        response = requests.post(
            f"{API_URL}/api/cases/{case_id}/take",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to take case: {response.text}")
            return False
        
        taken_case = response.json()
        print(f"✅ ADMIN took case #{taken_case['public_id']}")
        print(f"  Status: {taken_case['status']}")
        print(f"  Responsible: {taken_case.get('responsible_id')}")
        
        # Login as executor1 and check they cannot see this case
        executor_token = get_auth_token("executor1", "Executor123!")
        print("✅ Logged in as EXECUTOR")
        
        response = requests.get(
            f"{API_URL}/api/cases/assigned",
            headers={"Authorization": f"Bearer {executor_token}"}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get assigned cases: {response.text}")
            return False
        
        executor_cases = response.json()["cases"]
        case_ids = [c["id"] for c in executor_cases]
        
        if case_id not in case_ids:
            print(f"✅ EXECUTOR correctly cannot see case assigned to another user")
            return True
        else:
            print(f"❌ EXECUTOR should not see case assigned to another user")
            # Show case details
            for c in executor_cases:
                if c["id"] == case_id:
                    print_case(c, "  ")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_complete_workflow():
    """Test 4: Complete workflow - See NEW -> Take -> See in assigned"""
    print_header("TEST 4: Complete Workflow - NEW → TAKE → ASSIGNED")
    
    try:
        # Login as admin
        admin_token = get_auth_token("admin", "Admin123!")
        print("✅ Logged in as ADMIN")
        
        # Get categories and channels
        response = requests.get(
            f"{API_URL}/api/categories",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        categories = response.json()["categories"]
        category_id = categories[0]["id"] if categories else None
        
        response = requests.get(
            f"{API_URL}/api/channels",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        channels = response.json()["channels"]
        channel_id = channels[0]["id"] if channels else None
        
        # Create a NEW case
        response = requests.post(
            f"{API_URL}/api/cases",
            headers={"Authorization": f"Bearer {admin_token}"},
            data={
                "category_id": category_id,
                "channel_id": channel_id,
                "applicant_name": "Workflow Test",
                "applicant_phone": "+380501234567",
                "summary": f"Complete workflow test - BE-016 {datetime.now().isoformat()}"
            }
        )
        
        if response.status_code != 201:
            print(f"❌ Failed to create case: {response.text}")
            return False
        
        case = response.json()
        case_id = case["id"]
        case_public_id = case["public_id"]
        print(f"✅ Step 1: Created NEW case #{case_public_id}")
        
        # Login as executor
        executor_token = get_auth_token("executor1", "Executor123!")
        print("✅ Logged in as EXECUTOR")
        
        # Step 2: Check executor can see NEW case
        response = requests.get(
            f"{API_URL}/api/cases/assigned",
            headers={"Authorization": f"Bearer {executor_token}"}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get assigned cases: {response.text}")
            return False
        
        executor_cases = response.json()["cases"]
        case_ids_before = [c["id"] for c in executor_cases]
        
        if case_id not in case_ids_before:
            print(f"❌ Step 2 Failed: EXECUTOR cannot see NEW case #{case_public_id}")
            return False
        
        print(f"✅ Step 2: EXECUTOR can see NEW case #{case_public_id}")
        
        # Step 3: Take the case
        response = requests.post(
            f"{API_URL}/api/cases/{case_id}/take",
            headers={"Authorization": f"Bearer {executor_token}"}
        )
        
        if response.status_code != 200:
            print(f"❌ Step 3 Failed: Cannot take case: {response.text}")
            return False
        
        taken_case = response.json()
        print(f"✅ Step 3: Took case #{case_public_id}")
        print(f"  Status changed: NEW → {taken_case['status']}")
        print(f"  Responsible: {taken_case.get('responsible_id')}")
        
        # Step 4: Verify still visible in assigned cases
        response = requests.get(
            f"{API_URL}/api/cases/assigned",
            headers={"Authorization": f"Bearer {executor_token}"}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get assigned cases: {response.text}")
            return False
        
        executor_cases_after = response.json()["cases"]
        case_ids_after = [c["id"] for c in executor_cases_after]
        
        if case_id not in case_ids_after:
            print(f"❌ Step 4 Failed: EXECUTOR cannot see their assigned case #{case_public_id}")
            return False
        
        print(f"✅ Step 4: EXECUTOR can still see case #{case_public_id} (now assigned)")
        
        # Find the case and show its current status
        for c in executor_cases_after:
            if c["id"] == case_id:
                print_case(c, "  ")
                break
        
        print("\n✅ Complete workflow test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print_header("BE-016: Executor Access Rules - Test Suite")
    print("Testing that EXECUTOR can see:")
    print("1. All NEW cases (available to take)")
    print("2. All cases where executor is assigned")
    print("3. Cannot see cases assigned to others")
    
    results = []
    
    # Run tests
    results.append(("Test 1: See NEW Cases", test_executor_can_see_new_cases()))
    results.append(("Test 2: See Assigned Cases", test_executor_can_see_assigned_cases()))
    results.append(("Test 3: Cannot See Others", test_executor_cannot_see_other_assigned_cases()))
    results.append(("Test 4: Complete Workflow", test_complete_workflow()))
    
    # Print summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests PASSED! BE-016 implementation is correct.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) FAILED. Please review the implementation.")
        return 1

if __name__ == "__main__":
    exit(main())
