"""
Тест GET /api/users/me/category-access
"""

import requests

API_BASE = "http://localhost:8000/api"

# 1. Авторизація
print("1. Авторизація...")
response = requests.post(
    f"{API_BASE}/auth/login",
    data={"username": "admin", "password": "admin"}
)

if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"✅ Авторизовано, token: {token[:20]}...")
else:
    print(f"❌ Помилка авторизації: {response.status_code}")
    print(response.text)
    exit(1)

# 2. Тест endpoint
print("\n2. Тест GET /api/users/me/category-access...")
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(
    f"{API_BASE}/users/me/category-access",
    headers=headers
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ Успішно!")
    print(f"User ID: {data['executor_id']}")
    print(f"Username: {data['executor_username']}")
    print(f"Total categories: {data['total']}")
    if data['categories']:
        print(f"Categories:")
        for cat in data['categories']:
            print(f"  - {cat['category_name']} ({cat['category_id']})")
else:
    print(f"\n❌ Помилка: {response.status_code}")
