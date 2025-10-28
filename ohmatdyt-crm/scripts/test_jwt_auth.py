"""
Quick test script for JWT authentication
Run: python scripts/test_jwt_auth.py
"""
import httpx
import json


API_URL = "http://localhost:8000"


def test_auth_flow():
    """Test complete authentication flow"""
    print("=" * 60)
    print("Testing JWT Authentication Flow")
    print("=" * 60)
    
    # Step 1: Create test user (requires admin or run manually)
    print("\n1. Creating test user...")
    print("   Note: User creation requires admin token or direct DB access")
    print("   Using existing user or create via migration/script")
    
    # Step 2: Login
    print("\n2. Testing login...")
    login_data = {
        "username": "admin",  # Adjust based on your test user
        "password": "admin123"  # Adjust based on your test user
    }
    
    try:
        response = httpx.post(f"{API_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            print("   ✅ Login successful!")
            tokens = response.json()
            print(f"   Access Token: {tokens['access_token'][:50]}...")
            print(f"   Refresh Token: {tokens['refresh_token'][:50]}...")
            print(f"   Expires in: {tokens['expires_in']} seconds")
            print(f"   User: {tokens['user']['username']} ({tokens['user']['role']})")
            
            access_token = tokens['access_token']
            refresh_token = tokens['refresh_token']
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Step 3: Get current user
    print("\n3. Testing GET /auth/me...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = httpx.get(f"{API_URL}/auth/me", headers=headers)
        
        if response.status_code == 200:
            print("   ✅ Got current user info!")
            user = response.json()
            print(f"   Username: {user['username']}")
            print(f"   Email: {user['email']}")
            print(f"   Role: {user['role']}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 4: Access protected endpoint
    print("\n4. Testing protected endpoint (GET /api/users)...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = httpx.get(f"{API_URL}/api/users", headers=headers)
        
        if response.status_code == 200:
            print("   ✅ Protected endpoint accessed!")
            users = response.json()
            print(f"   Total users: {users.get('total', 0)}")
        elif response.status_code == 403:
            print("   ⚠️  Access forbidden (not admin)")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 5: Test without token
    print("\n5. Testing endpoint without token...")
    try:
        response = httpx.get(f"{API_URL}/api/users")
        
        if response.status_code == 401:
            print("   ✅ Correctly rejected (401 Unauthorized)")
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 6: Refresh token
    print("\n6. Testing token refresh...")
    try:
        response = httpx.post(
            f"{API_URL}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        if response.status_code == 200:
            print("   ✅ Token refreshed successfully!")
            new_tokens = response.json()
            print(f"   New Access Token: {new_tokens['access_token'][:50]}...")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 7: Logout
    print("\n7. Testing logout...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = httpx.post(f"{API_URL}/auth/logout", headers=headers)
        
        if response.status_code == 204:
            print("   ✅ Logged out successfully!")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Authentication flow test completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_auth_flow()
