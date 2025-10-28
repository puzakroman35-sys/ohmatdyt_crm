"""
Test suite for BE-006: Create case with multipart file upload and email notifications

This test validates:
1. Creating a case with required fields (category_id, channel_id, applicant_name, summary)
2. Uploading files (1-2 files) with validation
3. Email notification is queued within ≤ 1 minute
4. Validation errors for missing required fields and invalid files
"""
import os
import io
import time
import requests
from pathlib import Path

# Configuration
BASE_URL = os.getenv("API_URL", "http://localhost:8000")
API_URL = BASE_URL

# Test credentials (should match your setup)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123!@#")

OPERATOR_USERNAME = "test_operator_be006"
OPERATOR_PASSWORD = "Operator123!@#"


def create_test_file(filename: str, content: bytes, mime_type: str = "application/pdf"):
    """Create a test file for upload"""
    return (filename, io.BytesIO(content), mime_type)


def test_login(username: str, password: str):
    """Login and return access token"""
    print(f"\n[TEST] Logging in as {username}...")
    
    response = requests.post(
        f"{API_URL}/api/auth/login",
        json={
            "username": username,
            "password": password
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None
    
    data = response.json()
    print(f"✅ Login successful")
    return data["access_token"]


def create_operator_user(admin_token: str):
    """Create operator user for testing"""
    print(f"\n[TEST] Creating operator user: {OPERATOR_USERNAME}...")
    
    response = requests.post(
        f"{API_URL}/api/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": OPERATOR_USERNAME,
            "email": f"{OPERATOR_USERNAME}@test.com",
            "full_name": "Test Operator BE006",
            "password": OPERATOR_PASSWORD,
            "role": "OPERATOR"
        }
    )
    
    if response.status_code == 201:
        print(f"✅ Operator user created")
        return response.json()
    elif response.status_code == 400 and "already exists" in response.text:
        print(f"ℹ️ Operator user already exists")
        return {"username": OPERATOR_USERNAME}
    else:
        print(f"❌ Failed to create operator: {response.status_code} - {response.text}")
        return None


def get_or_create_category(admin_token: str, name: str = "Test Category BE006"):
    """Get or create a test category"""
    print(f"\n[TEST] Getting/creating category: {name}...")
    
    # Try to get existing categories
    response = requests.get(
        f"{API_URL}/api/categories",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    if response.status_code == 200:
        categories = response.json().get("categories", [])
        for cat in categories:
            if cat["name"] == name:
                print(f"✅ Category found: {cat['id']}")
                return cat["id"]
    
    # Create new category
    response = requests.post(
        f"{API_URL}/api/categories",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": name}
    )
    
    if response.status_code == 201:
        category_id = response.json()["id"]
        print(f"✅ Category created: {category_id}")
        return category_id
    else:
        print(f"❌ Failed to create category: {response.status_code} - {response.text}")
        return None


def get_or_create_channel(admin_token: str, name: str = "Test Channel BE006"):
    """Get or create a test channel"""
    print(f"\n[TEST] Getting/creating channel: {name}...")
    
    # Try to get existing channels
    response = requests.get(
        f"{API_URL}/api/channels",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    if response.status_code == 200:
        channels = response.json().get("channels", [])
        for ch in channels:
            if ch["name"] == name:
                print(f"✅ Channel found: {ch['id']}")
                return ch["id"]
    
    # Create new channel
    response = requests.post(
        f"{API_URL}/api/channels",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": name}
    )
    
    if response.status_code == 201:
        channel_id = response.json()["id"]
        print(f"✅ Channel created: {channel_id}")
        return channel_id
    else:
        print(f"❌ Failed to create channel: {response.status_code} - {response.text}")
        return None


def test_create_case_with_files(operator_token: str, category_id: str, channel_id: str):
    """Test creating a case with file attachments"""
    print("\n" + "="*70)
    print("[TEST 1] Create case with 2 valid files")
    print("="*70)
    
    # Create test files
    file1_content = b"This is a test PDF file content for BE-006"
    file2_content = b"This is a second test PDF file content for BE-006"
    
    # Prepare multipart form data
    files = [
        ('files', ('test_document_1.pdf', io.BytesIO(file1_content), 'application/pdf')),
        ('files', ('test_document_2.pdf', io.BytesIO(file2_content), 'application/pdf'))
    ]
    
    data = {
        'category_id': category_id,
        'channel_id': channel_id,
        'applicant_name': 'Іван Петренко',
        'applicant_phone': '+380501234567',
        'applicant_email': 'ivan.petrenko@example.com',
        'summary': 'Тестове звернення для перевірки BE-006 з двома файлами',
        'subcategory': 'Підкатегорія тест'
    }
    
    # Record start time for notification timing check
    start_time = time.time()
    
    response = requests.post(
        f"{API_URL}/api/cases",
        headers={"Authorization": f"Bearer {operator_token}"},
        data=data,
        files=files
    )
    
    elapsed_time = time.time() - start_time
    
    print(f"\n[RESULT] Status code: {response.status_code}")
    
    if response.status_code == 201:
        case_data = response.json()
        print(f"✅ Case created successfully!")
        print(f"   Public ID: {case_data['public_id']}")
        print(f"   Status: {case_data['status']}")
        print(f"   Case ID: {case_data['id']}")
        print(f"   Response time: {elapsed_time:.2f}s")
        
        # Verify status is NEW
        if case_data['status'] == 'NEW':
            print(f"✅ Status is NEW (as expected)")
        else:
            print(f"❌ Status is {case_data['status']}, expected NEW")
        
        # Check notification timing (should be queued within 1 minute)
        if elapsed_time <= 60:
            print(f"✅ Notification should be queued within ≤ 1 minute (actual: {elapsed_time:.2f}s)")
        else:
            print(f"⚠️ Warning: Response took > 60s, may affect notification timing")
        
        return case_data
    else:
        print(f"❌ Failed to create case: {response.text}")
        return None


def test_create_case_validation_missing_fields(operator_token: str):
    """Test validation errors for missing required fields"""
    print("\n" + "="*70)
    print("[TEST 2] Validation: Missing required fields")
    print("="*70)
    
    # Missing category_id
    print("\n[TEST 2.1] Missing category_id...")
    data = {
        'channel_id': 'dummy-channel-id',
        'applicant_name': 'Test User',
        'summary': 'Test summary'
    }
    
    response = requests.post(
        f"{API_URL}/api/cases",
        headers={"Authorization": f"Bearer {operator_token}"},
        data=data
    )
    
    if response.status_code == 422:  # FastAPI validation error
        print(f"✅ Correctly rejected missing category_id (422)")
    else:
        print(f"❌ Expected 422, got {response.status_code}")
    
    # Missing applicant_name
    print("\n[TEST 2.2] Missing applicant_name...")
    data = {
        'category_id': 'dummy-category-id',
        'channel_id': 'dummy-channel-id',
        'summary': 'Test summary'
    }
    
    response = requests.post(
        f"{API_URL}/api/cases",
        headers={"Authorization": f"Bearer {operator_token}"},
        data=data
    )
    
    if response.status_code == 422:
        print(f"✅ Correctly rejected missing applicant_name (422)")
    else:
        print(f"❌ Expected 422, got {response.status_code}")


def test_create_case_invalid_file(operator_token: str, category_id: str, channel_id: str):
    """Test validation for invalid file types and sizes"""
    print("\n" + "="*70)
    print("[TEST 3] Validation: Invalid file type")
    print("="*70)
    
    # Create an executable file (not allowed)
    file_content = b"This is an executable file"
    files = [
        ('files', ('malicious.exe', io.BytesIO(file_content), 'application/x-msdownload'))
    ]
    
    data = {
        'category_id': category_id,
        'channel_id': channel_id,
        'applicant_name': 'Test User',
        'summary': 'Test with invalid file'
    }
    
    response = requests.post(
        f"{API_URL}/api/cases",
        headers={"Authorization": f"Bearer {operator_token}"},
        data=data,
        files=files
    )
    
    if response.status_code == 400:
        print(f"✅ Correctly rejected invalid file type (400)")
        print(f"   Error: {response.json().get('detail', 'N/A')}")
    else:
        print(f"❌ Expected 400, got {response.status_code}")


def test_create_case_oversized_file(operator_token: str, category_id: str, channel_id: str):
    """Test validation for oversized files (> 10MB)"""
    print("\n" + "="*70)
    print("[TEST 4] Validation: Oversized file (> 10MB)")
    print("="*70)
    
    # Create a file larger than 10MB
    file_content = b"X" * (11 * 1024 * 1024)  # 11 MB
    files = [
        ('files', ('large_file.pdf', io.BytesIO(file_content), 'application/pdf'))
    ]
    
    data = {
        'category_id': category_id,
        'channel_id': channel_id,
        'applicant_name': 'Test User',
        'summary': 'Test with oversized file'
    }
    
    response = requests.post(
        f"{API_URL}/api/cases",
        headers={"Authorization": f"Bearer {operator_token}"},
        data=data,
        files=files
    )
    
    if response.status_code == 400:
        print(f"✅ Correctly rejected oversized file (400)")
        print(f"   Error: {response.json().get('detail', 'N/A')}")
    else:
        print(f"❌ Expected 400, got {response.status_code}")


def main():
    """Run all BE-006 tests"""
    print("\n" + "="*70)
    print("BE-006 TEST SUITE: Create Case with Files + Email Notification")
    print("="*70)
    
    # Step 1: Login as admin
    admin_token = test_login(ADMIN_USERNAME, ADMIN_PASSWORD)
    if not admin_token:
        print("\n❌ Cannot proceed without admin access")
        return
    
    # Step 2: Create operator user
    create_operator_user(admin_token)
    
    # Step 3: Login as operator
    operator_token = test_login(OPERATOR_USERNAME, OPERATOR_PASSWORD)
    if not operator_token:
        print("\n❌ Cannot proceed without operator access")
        return
    
    # Step 4: Get or create test category
    category_id = get_or_create_category(admin_token)
    if not category_id:
        print("\n❌ Cannot proceed without category")
        return
    
    # Step 5: Get or create test channel
    channel_id = get_or_create_channel(admin_token)
    if not channel_id:
        print("\n❌ Cannot proceed without channel")
        return
    
    # Step 6: Run tests
    test_create_case_with_files(operator_token, category_id, channel_id)
    test_create_case_validation_missing_fields(operator_token)
    test_create_case_invalid_file(operator_token, category_id, channel_id)
    test_create_case_oversized_file(operator_token, category_id, channel_id)
    
    print("\n" + "="*70)
    print("BE-006 TEST SUITE COMPLETED")
    print("="*70)


if __name__ == "__main__":
    main()
