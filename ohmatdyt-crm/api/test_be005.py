"""
Test script for BE-005: Attachments (file validation and storage)

This script tests:
1. Successful upload of allowed file types
2. Rejection of files with invalid type
3. Rejection of files exceeding size limit
4. File download functionality
5. RBAC for attachment operations
"""

import os
import io
import sys
import asyncio
import httpx
from pathlib import Path

# API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")

# Test credentials (from previous tests)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin123!@#"

OPERATOR_USERNAME = "test_operator"
OPERATOR_PASSWORD = "Operator123!@#"


async def login(username: str, password: str) -> str:
    """Login and return access token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/api/auth/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code != 200:
            raise Exception(f"Login failed: {response.text}")
        
        data = response.json()
        return data["access_token"]


async def create_test_case(token: str) -> tuple[str, int]:
    """Create a test case and return (case_id, public_id)"""
    async with httpx.AsyncClient() as client:
        # First, get categories and channels
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get first active category
        response = await client.get(f"{API_BASE_URL}/api/categories", headers=headers)
        categories = response.json()["categories"]
        if not categories:
            raise Exception("No categories found")
        category_id = categories[0]["id"]
        
        # Get first active channel
        response = await client.get(f"{API_BASE_URL}/api/channels", headers=headers)
        channels = response.json()["channels"]
        if not channels:
            raise Exception("No channels found")
        channel_id = channels[0]["id"]
        
        # Create case
        case_data = {
            "category_id": category_id,
            "channel_id": channel_id,
            "applicant_name": "Test Applicant for Attachments",
            "applicant_phone": "+380123456789",
            "applicant_email": "test@example.com",
            "summary": "Test case for attachment upload"
        }
        
        response = await client.post(
            f"{API_BASE_URL}/api/cases",
            json=case_data,
            headers=headers
        )
        
        if response.status_code != 201:
            raise Exception(f"Failed to create case: {response.text}")
        
        case = response.json()
        return case["id"], case["public_id"]


async def test_upload_valid_file(token: str, case_id: str):
    """Test 1: Upload a valid PDF file"""
    print("\n=== Test 1: Upload valid PDF file ===")
    
    # Create a dummy PDF file content
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"
    
    async with httpx.AsyncClient() as client:
        files = {
            "file": ("test_document.pdf", io.BytesIO(pdf_content), "application/pdf")
        }
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.post(
            f"{API_BASE_URL}/api/attachments/cases/{case_id}/upload",
            files=files,
            headers=headers
        )
        
        if response.status_code == 201:
            print("✅ PASS: Valid PDF uploaded successfully")
            data = response.json()
            print(f"   Attachment ID: {data['id']}")
            print(f"   Original name: {data['original_name']}")
            print(f"   Size: {data['size_bytes']} bytes")
            print(f"   MIME type: {data['mime_type']}")
            return data['id']
        else:
            print(f"❌ FAIL: Expected 201, got {response.status_code}")
            print(f"   Response: {response.text}")
            return None


async def test_upload_invalid_type(token: str, case_id: str):
    """Test 2: Try to upload a file with invalid type"""
    print("\n=== Test 2: Upload invalid file type (.exe) ===")
    
    # Create a dummy executable file
    exe_content = b"MZ\x90\x00"  # PE executable header
    
    async with httpx.AsyncClient() as client:
        files = {
            "file": ("malware.exe", io.BytesIO(exe_content), "application/x-msdownload")
        }
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.post(
            f"{API_BASE_URL}/api/attachments/cases/{case_id}/upload",
            files=files,
            headers=headers
        )
        
        if response.status_code == 400:
            print("✅ PASS: Invalid file type rejected (400)")
            print(f"   Error: {response.json()['detail']}")
        else:
            print(f"❌ FAIL: Expected 400, got {response.status_code}")
            print(f"   Response: {response.text}")


async def test_upload_oversized_file(token: str, case_id: str):
    """Test 3: Try to upload a file exceeding size limit"""
    print("\n=== Test 3: Upload oversized file (>10MB) ===")
    
    # Create a large file (11MB)
    large_content = b"0" * (11 * 1024 * 1024)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        files = {
            "file": ("large_file.pdf", io.BytesIO(large_content), "application/pdf")
        }
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.post(
            f"{API_BASE_URL}/api/attachments/cases/{case_id}/upload",
            files=files,
            headers=headers
        )
        
        if response.status_code == 400:
            print("✅ PASS: Oversized file rejected (400)")
            print(f"   Error: {response.json()['detail']}")
        else:
            print(f"❌ FAIL: Expected 400, got {response.status_code}")
            print(f"   Response: {response.text}")


async def test_list_attachments(token: str, case_id: str):
    """Test 4: List all attachments for a case"""
    print("\n=== Test 4: List case attachments ===")
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.get(
            f"{API_BASE_URL}/api/attachments/cases/{case_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PASS: Listed attachments successfully")
            print(f"   Total attachments: {data['total']}")
            for att in data['attachments']:
                print(f"   - {att['original_name']} ({att['size_bytes']} bytes)")
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            print(f"   Response: {response.text}")


async def test_download_attachment(token: str, attachment_id: str):
    """Test 5: Download an attachment"""
    print("\n=== Test 5: Download attachment ===")
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.get(
            f"{API_BASE_URL}/api/attachments/{attachment_id}/download",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ PASS: Attachment downloaded successfully")
            print(f"   Content-Type: {response.headers.get('content-type')}")
            print(f"   Size: {len(response.content)} bytes")
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            print(f"   Response: {response.text}")


async def test_rbac_operator_cannot_access_others_attachments(
    operator_token: str,
    admin_case_id: str
):
    """Test 6: RBAC - Operator cannot access other user's attachments"""
    print("\n=== Test 6: RBAC - Operator cannot access other's attachments ===")
    
    # Create a dummy file
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"
    
    async with httpx.AsyncClient() as client:
        files = {
            "file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")
        }
        headers = {"Authorization": f"Bearer {operator_token}"}
        
        response = await client.post(
            f"{API_BASE_URL}/api/attachments/cases/{admin_case_id}/upload",
            files=files,
            headers=headers
        )
        
        if response.status_code == 403:
            print("✅ PASS: Operator blocked from uploading to other's case (403)")
            print(f"   Error: {response.json()['detail']}")
        else:
            print(f"❌ FAIL: Expected 403, got {response.status_code}")
            print(f"   Response: {response.text}")


async def test_delete_attachment(token: str, attachment_id: str):
    """Test 7: Delete an attachment"""
    print("\n=== Test 7: Delete attachment ===")
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.delete(
            f"{API_BASE_URL}/api/attachments/{attachment_id}",
            headers=headers
        )
        
        if response.status_code == 204:
            print("✅ PASS: Attachment deleted successfully (204)")
        else:
            print(f"❌ FAIL: Expected 204, got {response.status_code}")
            print(f"   Response: {response.text}")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("BE-005: Attachment Upload and Validation Tests")
    print("=" * 60)
    
    try:
        # Login as admin
        print("\n🔐 Logging in as admin...")
        admin_token = await login(ADMIN_USERNAME, ADMIN_PASSWORD)
        print("✅ Admin login successful")
        
        # Login as operator
        print("\n🔐 Logging in as operator...")
        operator_token = await login(OPERATOR_USERNAME, OPERATOR_PASSWORD)
        print("✅ Operator login successful")
        
        # Create test case as admin
        print("\n📝 Creating test case as admin...")
        admin_case_id, admin_public_id = await create_test_case(admin_token)
        print(f"✅ Test case created: {admin_public_id}")
        
        # Test 1: Upload valid file
        attachment_id = await test_upload_valid_file(admin_token, admin_case_id)
        
        # Test 2: Upload invalid type
        await test_upload_invalid_type(admin_token, admin_case_id)
        
        # Test 3: Upload oversized file
        await test_upload_oversized_file(admin_token, admin_case_id)
        
        # Test 4: List attachments
        await test_list_attachments(admin_token, admin_case_id)
        
        # Test 5: Download attachment
        if attachment_id:
            await test_download_attachment(admin_token, attachment_id)
        
        # Test 6: RBAC - operator cannot access admin's attachments
        await test_rbac_operator_cannot_access_others_attachments(
            operator_token,
            admin_case_id
        )
        
        # Test 7: Delete attachment
        if attachment_id:
            await test_delete_attachment(admin_token, attachment_id)
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
