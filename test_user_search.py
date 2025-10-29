"""
Тест пошуку користувачів
"""
import requests

API_URL = "http://localhost:8000"

# Спочатку потрібно залогінитись
def login():
    response = requests.post(
        f"{API_URL}/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Помилка логіну: {response.status_code}")
        print(response.text)
        return None

# Тест пошуку користувачів
def test_search(token, search_query):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Тест без пошуку
    print("\n=== Тест БЕЗ пошуку ===")
    response = requests.get(
        f"{API_URL}/api/users",
        headers=headers,
        params={
            "skip": 0,
            "limit": 20,
            "order_by": "created_at",
            "order": "desc"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Знайдено користувачів: {data['total']}")
        for user in data['users'][:3]:  # Показуємо перших 3
            print(f"  - {user['username']} ({user['full_name']}) - {user['email']}")
    else:
        print(f"Помилка: {response.status_code}")
        print(response.text)
    
    # Тест З пошуком
    print(f"\n=== Тест З пошуком: '{search_query}' ===")
    response = requests.get(
        f"{API_URL}/api/users",
        headers=headers,
        params={
            "skip": 0,
            "limit": 20,
            "search": search_query,
            "order_by": "created_at",
            "order": "desc"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Знайдено користувачів: {data['total']}")
        for user in data['users']:
            print(f"  - {user['username']} ({user['full_name']}) - {user['email']}")
    else:
        print(f"Помилка: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("Логінимось як admin...")
    token = login()
    
    if token:
        print("✅ Успішний логін!")
        
        # Тестуємо різні пошукові запити
        test_search(token, "admi")
        test_search(token, "admin")
        test_search(token, "test")
    else:
        print("❌ Не вдалось залогінитись")
