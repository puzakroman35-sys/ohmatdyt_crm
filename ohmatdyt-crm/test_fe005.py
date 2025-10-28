"""
Test suite for FE-005: Cases List for Executors with Category Filters and Overdue Highlighting

Тести для функціональності списку звернень виконавця:
1. Фільтрація за категоріями
2. Фільтр прострочених звернень (overdue)
3. Взяття звернення в роботу (take case)
4. Перевірка RBAC для виконавців
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def login(username: str, password: str):
    """Логін користувача та отримання токену"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
    data = response.json()
    assert "access_token" in data, "No access token in response"
    return data["access_token"]

def get_headers(token: str):
    """Створити headers з JWT токеном"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def test_fe005():
    """Головний тестовий сценарій для FE-005"""
    print("\n=== TEST FE-005: Executor Cases List with Filters ===\n")
    
    # 1. Логін як EXECUTOR
    print("1. Логін як executor1...")
    executor_token = login("executor1", "Executor123!")
    executor_headers = get_headers(executor_token)
    print("✅ Executor logged in successfully")
    
    # 2. Отримання списку категорій
    print("\n2. Завантаження списку категорій...")
    response = requests.get(
        f"{BASE_URL}/api/categories",
        headers=executor_headers,
        params={"is_active": True}
    )
    assert response.status_code == 200, f"Failed to get categories: {response.text}"
    categories = response.json()
    
    # Перевірка формату відповіді
    if isinstance(categories, dict) and 'categories' in categories:
        categories = categories['categories']
    
    assert len(categories) > 0, "No categories found"
    category = categories[0]
    print(f"✅ Знайдено категорію: {category['name']} (ID: {category['id']})")
    
    # 3. Логін як OPERATOR для створення тестових звернень
    print("\n3. Логін як operator для створення тестових звернень...")
    operator_token = login("operator1", "Operator123!")
    operator_headers = get_headers(operator_token)
    
    # Отримання каналу
    response = requests.get(
        f"{BASE_URL}/api/channels",
        headers=operator_headers,
        params={"is_active": True}
    )
    assert response.status_code == 200
    channels = response.json()
    
    # Перевірка формату відповіді
    if isinstance(channels, dict) and 'channels' in channels:
        channels = channels['channels']
    
    assert len(channels) > 0, "No channels found"
    channel = channels[0]
    print(f"✅ Знайдено канал: {channel['name']}")
    
    # 4. Створення тестового звернення
    print("\n4. Створення тестового звернення зі статусом NEW...")
    case_data = {
        "category_id": category["id"],
        "channel_id": channel["id"],
        "applicant_name": "Test Applicant FE005",
        "summary": "Тестове звернення для перевірки функціоналу виконавця",
        "applicant_phone": "+380501234567",
        "applicant_email": "test@example.com"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/cases",
        headers={"Authorization": f"Bearer {operator_token}"},  # Без Content-Type для multipart
        data=case_data  # requests автоматично встановить multipart/form-data
    )
    assert response.status_code == 201, f"Failed to create case: {response.text}"
    created_case = response.json()
    case_id = created_case["id"]
    public_id = created_case["public_id"]
    print(f"✅ Звернення створено: #{public_id} (ID: {case_id})")
    
    # 5. Тест фільтру за категорією (EXECUTOR)
    print("\n5. Фільтрація звернень за категорією...")
    response = requests.get(
        f"{BASE_URL}/api/cases/assigned",
        headers=executor_headers,
        params={"category_id": category["id"]}
    )
    assert response.status_code == 200, f"Failed to filter by category: {response.text}"
    filtered_data = response.json()
    print(f"✅ Знайдено {filtered_data['total']} звернень у категорії '{category['name']}'")
    
    # 6. Тест фільтру overdue
    print("\n6. Фільтрація прострочених звернень (overdue=true)...")
    response = requests.get(
        f"{BASE_URL}/api/cases/assigned",
        headers=executor_headers,
        params={"overdue": "true"}
    )
    assert response.status_code == 200, f"Failed to filter overdue: {response.text}"
    overdue_data = response.json()
    print(f"✅ Знайдено {overdue_data['total']} прострочених звернень")
    
    # 7. Тест фільтру НЕ прострочених (overdue=false)
    print("\n7. Фільтрація НЕ прострочених звернень (overdue=false)...")
    response = requests.get(
        f"{BASE_URL}/api/cases/assigned",
        headers=executor_headers,
        params={"overdue": "false"}
    )
    assert response.status_code == 200, f"Failed to filter non-overdue: {response.text}"
    non_overdue_data = response.json()
    print(f"✅ Знайдено {non_overdue_data['total']} НЕ прострочених звернень")
    
    # 8. Тест "Взяти в роботу" (Take Case)
    print(f"\n8. Взяття звернення #{public_id} в роботу...")
    response = requests.post(
        f"{BASE_URL}/api/cases/{case_id}/take",
        headers=executor_headers
    )
    assert response.status_code == 200, f"Failed to take case: {response.text}"
    taken_case = response.json()
    assert taken_case["status"] == "IN_PROGRESS", f"Status not IN_PROGRESS: {taken_case['status']}"
    assert taken_case["responsible_id"] is not None, "Responsible not set"
    print(f"✅ Звернення взято в роботу! Статус: {taken_case['status']}")
    
    # 9. Перевірка, що повторне взяття неможливе
    print(f"\n9. Спроба повторно взяти звернення #{public_id}...")
    response = requests.post(
        f"{BASE_URL}/api/cases/{case_id}/take",
        headers=executor_headers
    )
    assert response.status_code == 400, f"Should fail to take case twice: {response.status_code}"
    print(f"✅ Повторне взяття заблоковано (очікувана помилка 400): {response.json()['detail']}")
    
    # 10. Тест комбінованих фільтрів: category + status + overdue
    print("\n10. Комбінований фільтр: категорія + статус + НЕ прострочені...")
    response = requests.get(
        f"{BASE_URL}/api/cases/assigned",
        headers=executor_headers,
        params={
            "category_id": category["id"],
            "status": "IN_PROGRESS",
            "overdue": "false"
        }
    )
    assert response.status_code == 200, f"Failed combined filter: {response.text}"
    combined_data = response.json()
    print(f"✅ Знайдено {combined_data['total']} звернень з комбінованим фільтром")
    
    # 11. Перевірка RBAC: OPERATOR не може взяти звернення
    print("\n11. Перевірка RBAC: Спроба operator взяти звернення...")
    # Створюємо нове звернення для тесту
    response = requests.post(
        f"{BASE_URL}/api/cases",
        headers={"Authorization": f"Bearer {operator_token}"},
        data={
            "category_id": category["id"],
            "channel_id": channel["id"],
            "applicant_name": "Test RBAC",
            "summary": "Тестове звернення для RBAC"
        }
    )
    assert response.status_code == 201
    rbac_case = response.json()
    rbac_case_id = rbac_case["id"]
    
    # Спроба operator взяти звернення
    response = requests.post(
        f"{BASE_URL}/api/cases/{rbac_case_id}/take",
        headers={"Authorization": f"Bearer {operator_token}"}
    )
    assert response.status_code == 403, f"OPERATOR should not be able to take cases: {response.status_code}"
    print(f"✅ RBAC працює: OPERATOR отримав 403 Forbidden")
    
    # 12. Перевірка фільтру за датою створення
    print("\n12. Фільтрація за датою створення (сьогодні)...")
    today = datetime.now().strftime("%Y-%m-%d")
    response = requests.get(
        f"{BASE_URL}/api/cases/assigned",
        headers=executor_headers,
        params={
            "date_from": today,
            "date_to": today
        }
    )
    assert response.status_code == 200, f"Failed date filter: {response.text}"
    date_data = response.json()
    print(f"✅ Знайдено {date_data['total']} звернень створених сьогодні")
    
    print("\n=== ✅ ALL FE-005 TESTS PASSED ===\n")
    
    # Підсумок результатів
    print("📊 ПІДСУМОК ТЕСТІВ:")
    print(f"   - Категорія: {category['name']}")
    print(f"   - Канал: {channel['name']}")
    print(f"   - Створено звернень: 2")
    print(f"   - Фільтр за категорією: {filtered_data['total']} звернень")
    print(f"   - Прострочені: {overdue_data['total']} звернень")
    print(f"   - НЕ прострочені: {non_overdue_data['total']} звернень")
    print(f"   - Взято в роботу: #{public_id}")
    print(f"   - RBAC перевірка: ✅ Passed")
    print(f"   - Фільтр за датою: {date_data['total']} звернень")
    
    print("\n✅ Всі функції FE-005 працюють коректно!")

if __name__ == "__main__":
    try:
        test_fe005()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
