"""
Тест для перевірки, що API повертає об'єкти category та channel в списку звернень
"""
import requests
import json

# URL API
API_BASE_URL = "http://localhost:8000"

# Тестові дані користувача
TEST_USER = {
    "username": "admin",
    "password": "admin123"
}

def test_cases_list_includes_category_and_channel():
    """Перевірка, що список звернень включає об'єкти category та channel"""
    
    # 1. Авторизація
    print("1. Авторизація...")
    login_response = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Помилка авторизації: {login_response.status_code}")
        print(login_response.text)
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Авторизація успішна")
    
    # 2. Отримання списку звернень
    print("\n2. Отримання списку звернень...")
    cases_response = requests.get(
        f"{API_BASE_URL}/api/cases",
        headers=headers,
        params={"skip": 0, "limit": 5}
    )
    
    if cases_response.status_code != 200:
        print(f"❌ Помилка отримання списку: {cases_response.status_code}")
        print(cases_response.text)
        return False
    
    data = cases_response.json()
    cases = data.get("cases", [])
    
    if not cases:
        print("⚠️ Список звернень порожній")
        return False
    
    print(f"✅ Отримано {len(cases)} звернень")
    
    # 3. Перевірка першого звернення
    print("\n3. Перевірка першого звернення...")
    first_case = cases[0]
    
    print(f"\nДані першого звернення:")
    print(f"  ID: {first_case.get('public_id')}")
    print(f"  Category ID: {first_case.get('category_id')}")
    print(f"  Channel ID: {first_case.get('channel_id')}")
    
    # Перевірка наявності об'єкта category
    if 'category' not in first_case or first_case['category'] is None:
        print(f"\n❌ ПОМИЛКА: Об'єкт 'category' відсутній!")
        print(f"Доступні поля: {list(first_case.keys())}")
        return False
    
    category = first_case['category']
    print(f"\n  Category:")
    print(f"    - ID: {category.get('id')}")
    print(f"    - Name: {category.get('name')}")
    print(f"    ✅ Об'єкт category присутній")
    
    # Перевірка наявності об'єкта channel
    if 'channel' not in first_case or first_case['channel'] is None:
        print(f"\n❌ ПОМИЛКА: Об'єкт 'channel' відсутній!")
        print(f"Доступні поля: {list(first_case.keys())}")
        return False
    
    channel = first_case['channel']
    print(f"\n  Channel:")
    print(f"    - ID: {channel.get('id')}")
    print(f"    - Name: {channel.get('name')}")
    print(f"    ✅ Об'єкт channel присутній")
    
    # 4. Перевірка всіх звернень
    print(f"\n4. Перевірка всіх {len(cases)} звернень...")
    all_ok = True
    for i, case in enumerate(cases, 1):
        if not case.get('category') or not case.get('channel'):
            print(f"  ❌ Звернення #{i}: відсутні category або channel")
            all_ok = False
        else:
            print(f"  ✅ Звернення #{i}: category='{case['category']['name']}', channel='{case['channel']['name']}'")
    
    if all_ok:
        print(f"\n🎉 УСПІХ! Всі звернення містять об'єкти category та channel!")
        return True
    else:
        print(f"\n❌ ПОМИЛКА: Деякі звернення не містять повної інформації")
        return False


if __name__ == "__main__":
    print("="*60)
    print("Тест: Перевірка наявності category та channel в списку звернень")
    print("="*60)
    
    success = test_cases_list_includes_category_and_channel()
    
    print("\n" + "="*60)
    if success:
        print("РЕЗУЛЬТАТ: ✅ ТЕСТ ПРОЙДЕНО")
    else:
        print("РЕЗУЛЬТАТ: ❌ ТЕСТ НЕ ПРОЙДЕНО")
    print("="*60)
