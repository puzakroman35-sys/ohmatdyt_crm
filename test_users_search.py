"""
Test script for users search functionality
"""
import requests

# API URL
API_URL = "http://localhost:8000"

# Test credentials (admin)
USERNAME = "admin"
PASSWORD = "admin123"


def login():
    """Login and get token"""
    response = requests.post(
        f"{API_URL}/api/auth/login",
        data={
            "username": USERNAME,
            "password": PASSWORD
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✓ Login successful")
        return token
    else:
        print(f"✗ Login failed: {response.text}")
        return None


def test_users_search(token, search_term):
    """Test users search"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{API_URL}/api/users",
        headers=headers,
        params={"search": search_term}
    )
    
    if response.status_code == 200:
        data = response.json()
        users = data.get("users", [])
        total = data.get("total", 0)
        
        print(f"\n✓ Search for '{search_term}':")
        print(f"  Found {total} user(s)")
        
        for user in users:
            print(f"  - {user['full_name']} (@{user['username']}, {user['email']})")
        
        return True
    else:
        print(f"\n✗ Search failed: {response.text}")
        return False


def test_users_without_search(token):
    """Test users without search (all users)"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{API_URL}/api/users",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        total = data.get("total", 0)
        
        print(f"\n✓ All users: {total}")
        return True
    else:
        print(f"\n✗ Failed to get users: {response.text}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Users Search Functionality")
    print("=" * 60)
    
    # Login
    token = login()
    if not token:
        exit(1)
    
    # Test without search
    test_users_without_search(token)
    
    # Test searches
    test_users_search(token, "admin")
    test_users_search(token, "operator")
    test_users_search(token, "executor")
    test_users_search(token, "test")
    
    print("\n" + "=" * 60)
    print("Testing completed!")
    print("=" * 60)
