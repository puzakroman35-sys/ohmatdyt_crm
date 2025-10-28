"""
Швидкий тест для перевірки UUID serialization fix
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_uuid_serialization():
    print("=" * 60)
    print("TEST: UUID Serialization Fix")
    print("=" * 60)
    
    # 1. Login as admin
    print("\n1. Login as ADMIN...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "Admin123!"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # 2. Test GET /api/users (should work)
    print("\n2. Testing GET /api/users...")
    get_response = requests.get(f"{BASE_URL}/api/users", headers=headers)
    
    if get_response.status_code != 200:
        print(f"❌ GET /api/users failed: {get_response.status_code}")
        print(f"Response: {get_response.text}")
        return False
    
    users_data = get_response.json()
    print(f"✅ GET /api/users successful - {users_data.get('total', 0)} users found")
    
    # 3. Test POST /api/users (the problematic endpoint)
    print("\n3. Testing POST /api/users (UUID serialization test)...")
    new_user = {
        "username": f"test_uuid_user",
        "email": "uuid_test@example.com",
        "full_name": "UUID Test User",
        "password": "TestPass123!",
        "role": "OPERATOR"
    }
    
    post_response = requests.post(
        f"{BASE_URL}/api/users",
        headers=headers,
        json=new_user
    )
    
    if post_response.status_code == 201:
        print("✅ POST /api/users successful!")
        user_data = post_response.json()
        print(f"   Created user: {user_data.get('username')}")
        print(f"   User ID: {user_data.get('id')}")
        print(f"   ID type check: {type(user_data.get('id'))}")
        
        if isinstance(user_data.get('id'), str):
            print("   ✅ UUID serialized to string correctly!")
        else:
            print(f"   ⚠️ UUID type is {type(user_data.get('id'))}")
        
        return True
    else:
        print(f"❌ POST /api/users failed: {post_response.status_code}")
        print(f"Response: {post_response.text[:500]}")
        return False

if __name__ == "__main__":
    try:
        success = test_uuid_serialization()
        print("\n" + "=" * 60)
        if success:
            print("🎉 UUID SERIALIZATION FIX SUCCESSFUL!")
            print("=" * 60)
            sys.exit(0)
        else:
            print("❌ UUID SERIALIZATION STILL HAS ISSUES")
            print("=" * 60)
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
