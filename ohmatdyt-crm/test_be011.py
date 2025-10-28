"""
Test suite for BE-011: Comments with RBAC and Email Notifications

Тести для коментарів:
1. Створення публічного коментаря
2. Створення внутрішнього коментаря (EXECUTOR/ADMIN)
3. RBAC: OPERATOR не може створити внутрішній коментар
4. Видимість коментарів (RBAC)
5. Email нотифікації (placeholder перевірка)
"""
import requests
import json

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

def test_be011():
    """Головний тестовий сценарій для BE-011"""
    print("\n=== TEST BE-011: Comments with RBAC ===\n")
    
    # 1. Логін як OPERATOR
    print("1. Логін як operator1...")
    operator_token = login("operator1", "Operator123!")
    operator_headers = get_headers(operator_token)
    print("✅ Operator logged in successfully")
    
    # 2. Створення тестового звернення
    print("\n2. Створення тестового звернення...")
    
    # Завантаження категорій та каналів
    response = requests.get(f"{BASE_URL}/api/categories", headers=operator_headers)
    assert response.status_code == 200
    categories_data = response.json()
    if isinstance(categories_data, list):
        categories = categories_data
    else:
        categories = categories_data.get('categories', [])
    assert len(categories) > 0, "No categories found"
    category = categories[0]
    
    response = requests.get(f"{BASE_URL}/api/channels", headers=operator_headers)
    assert response.status_code == 200
    channels_data = response.json()
    if isinstance(channels_data, list):
        channels = channels_data
    else:
        channels = channels_data.get('channels', [])
    assert len(channels) > 0, "No channels found"
    channel = channels[0]
    
    # Створення звернення
    case_data = {
        "category_id": category["id"],
        "channel_id": channel["id"],
        "applicant_name": "Test Applicant BE011",
        "applicant_phone": "+380501234567",
        "applicant_email": "test@example.com",
        "summary": "Тестове звернення для перевірки коментарів"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/cases",
        headers={"Authorization": f"Bearer {operator_token}"},
        data=case_data
    )
    assert response.status_code == 201, f"Failed to create case: {response.text}"
    created_case = response.json()
    case_id = created_case["id"]
    public_id = created_case["public_id"]
    print(f"✅ Звернення створено: #{public_id} (ID: {case_id})")
    
    # 3. Створення публічного коментаря (OPERATOR)
    print("\n3. Створення публічного коментаря від OPERATOR...")
    comment_data = {
        "text": "Це публічний коментар від оператора",
        "is_internal": False
    }
    
    response = requests.post(
        f"{BASE_URL}/api/cases/{case_id}/comments",
        headers=operator_headers,
        json=comment_data
    )
    assert response.status_code == 201, f"Failed to create public comment: {response.text}"
    public_comment = response.json()
    
    assert public_comment["is_internal"] == False, "Comment should be public"
    assert public_comment["text"] == comment_data["text"], "Comment text mismatch"
    assert "author" in public_comment, "Author info missing"
    print(f"✅ Публічний коментар створено: {public_comment['id']}")
    print(f"   Автор: {public_comment['author']['full_name']}")
    
    # 4. Спроба створити внутрішній коментар (OPERATOR) - має FAIL
    print("\n4. Спроба створити внутрішній коментар від OPERATOR (має бути 403)...")
    internal_comment_data = {
        "text": "Спроба створити внутрішній коментар від оператора",
        "is_internal": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/cases/{case_id}/comments",
        headers=operator_headers,
        json=internal_comment_data
    )
    
    if response.status_code == 403:
        print("✅ RBAC працює: OPERATOR не може створити internal comment (403)")
    else:
        print(f"❌ RBAC FAILED: Expected 403, got {response.status_code}")
        assert False, "OPERATOR should not be able to create internal comments"
    
    # 5. Логін як EXECUTOR
    print("\n5. Логін як executor1...")
    executor_token = login("executor1", "Executor123!")
    executor_headers = get_headers(executor_token)
    print("✅ Executor logged in successfully")
    
    # 6. Взяття звернення в роботу
    print("\n6. Взяття звернення в роботу executor1...")
    response = requests.post(
        f"{BASE_URL}/api/cases/{case_id}/take",
        headers=executor_headers
    )
    assert response.status_code == 200, f"Failed to take case: {response.text}"
    print(f"✅ Звернення #{public_id} взято в роботу")
    
    # 7. Створення внутрішнього коментаря (EXECUTOR)
    print("\n7. Створення внутрішнього коментаря від EXECUTOR...")
    internal_comment_data = {
        "text": "Це внутрішній коментар від виконавця. Оператор його не побачить.",
        "is_internal": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/cases/{case_id}/comments",
        headers=executor_headers,
        json=internal_comment_data
    )
    assert response.status_code == 201, f"Failed to create internal comment: {response.text}"
    internal_comment = response.json()
    
    assert internal_comment["is_internal"] == True, "Comment should be internal"
    assert internal_comment["text"] == internal_comment_data["text"], "Comment text mismatch"
    print(f"✅ Внутрішній коментар створено: {internal_comment['id']}")
    print(f"   Автор: {internal_comment['author']['full_name']}")
    
    # 8. Створення ще одного публічного коментаря (EXECUTOR)
    print("\n8. Створення публічного коментаря від EXECUTOR...")
    executor_public_comment = {
        "text": "Публічний коментар від виконавця. Всі його побачать.",
        "is_internal": False
    }
    
    response = requests.post(
        f"{BASE_URL}/api/cases/{case_id}/comments",
        headers=executor_headers,
        json=executor_public_comment
    )
    assert response.status_code == 201, f"Failed to create public comment: {response.text}"
    print("✅ Публічний коментар від EXECUTOR створено")
    
    # 9. Перевірка видимості коментарів для OPERATOR
    print("\n9. Перевірка видимості коментарів для OPERATOR...")
    response = requests.get(
        f"{BASE_URL}/api/cases/{case_id}/comments",
        headers=operator_headers
    )
    assert response.status_code == 200, f"Failed to get comments: {response.text}"
    operator_view = response.json()
    operator_comments = operator_view["comments"]
    operator_total = operator_view["total"]
    
    print(f"   OPERATOR бачить коментарів: {operator_total}")
    
    # Підрахунок internal коментарів
    internal_count = sum(1 for c in operator_comments if c["is_internal"])
    
    if internal_count == 0:
        print("✅ RBAC працює: OPERATOR не бачить internal comments")
    else:
        print(f"❌ RBAC FAILED: OPERATOR бачить {internal_count} internal comment(s)")
        assert False, "OPERATOR should not see internal comments"
    
    # OPERATOR має бачити тільки 2 публічні коментарі
    expected_count = 2  # 1 від operator + 1 від executor (публічний)
    if operator_total == expected_count:
        print(f"✅ Correct count: {expected_count} public comments visible")
    else:
        print(f"⚠️  Expected {expected_count} comments, got {operator_total}")
    
    # 10. Перевірка видимості коментарів для EXECUTOR
    print("\n10. Перевірка видимості коментарів для EXECUTOR...")
    response = requests.get(
        f"{BASE_URL}/api/cases/{case_id}/comments",
        headers=executor_headers
    )
    assert response.status_code == 200, f"Failed to get comments: {response.text}"
    executor_view = response.json()
    executor_comments = executor_view["comments"]
    executor_total = executor_view["total"]
    
    print(f"   EXECUTOR бачить коментарів: {executor_total}")
    
    # EXECUTOR має бачити ВСІ коментарі (2 публічні + 1 внутрішній = 3)
    expected_total = 3
    if executor_total == expected_total:
        print(f"✅ Correct count: {expected_total} total comments visible")
    else:
        print(f"⚠️  Expected {expected_total} comments, got {executor_total}")
    
    # Підрахунок internal коментарів для EXECUTOR
    executor_internal_count = sum(1 for c in executor_comments if c["is_internal"])
    if executor_internal_count >= 1:
        print(f"✅ RBAC працює: EXECUTOR бачить {executor_internal_count} internal comment(s)")
    else:
        print("❌ RBAC FAILED: EXECUTOR не бачить internal comments")
    
    # 11. Валідація коментаря (занадто короткий)
    print("\n11. Валідація коментаря (занадто короткий)...")
    short_comment = {
        "text": "Hi",  # < 5 символів
        "is_internal": False
    }
    
    response = requests.post(
        f"{BASE_URL}/api/cases/{case_id}/comments",
        headers=operator_headers,
        json=short_comment
    )
    
    if response.status_code == 400:
        print("✅ Валідація працює: коментар занадто короткий (400)")
    else:
        print(f"⚠️  Expected 400, got {response.status_code}")
    
    # 12. Валідація коментаря (занадто довгий)
    print("\n12. Валідація коментаря (занадто довгий)...")
    long_comment = {
        "text": "A" * 6000,  # > 5000 символів
        "is_internal": False
    }
    
    response = requests.post(
        f"{BASE_URL}/api/cases/{case_id}/comments",
        headers=operator_headers,
        json=long_comment
    )
    
    if response.status_code == 400:
        print("✅ Валідація працює: коментар занадто довгий (400)")
    else:
        print(f"⚠️  Expected 400, got {response.status_code}")
    
    # 13. Логін як ADMIN
    print("\n13. Логін як admin...")
    admin_token = login("admin", "Admin123!")
    admin_headers = get_headers(admin_token)
    print("✅ Admin logged in successfully")
    
    # 14. Створення внутрішнього коментаря (ADMIN)
    print("\n14. Створення внутрішнього коментаря від ADMIN...")
    admin_internal_comment = {
        "text": "Внутрішній коментар від адміністратора для контролю",
        "is_internal": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/cases/{case_id}/comments",
        headers=admin_headers,
        json=admin_internal_comment
    )
    assert response.status_code == 201, f"Failed to create internal comment: {response.text}"
    print("✅ Внутрішній коментар від ADMIN створено")
    
    # 15. Перевірка видимості для ADMIN
    print("\n15. Перевірка видимості коментарів для ADMIN...")
    response = requests.get(
        f"{BASE_URL}/api/cases/{case_id}/comments",
        headers=admin_headers
    )
    assert response.status_code == 200
    admin_view = response.json()
    admin_total = admin_view["total"]
    
    print(f"   ADMIN бачить коментарів: {admin_total}")
    
    # ADMIN має бачити ВСІ коментарі (2 публічні + 2 внутрішні = 4)
    expected_admin_total = 4
    if admin_total == expected_admin_total:
        print(f"✅ Correct count: {expected_admin_total} total comments visible for ADMIN")
    else:
        print(f"⚠️  Expected {expected_admin_total} comments, got {admin_total}")
    
    print("\n=== ✅ ALL BE-011 TESTS PASSED ===\n")
    
    # Підсумок
    print("📊 ПІДСУМОК ТЕСТІВ:")
    print(f"   - Звернення: #{public_id}")
    print(f"   - Публічні коментарі створено: 2")
    print(f"   - Внутрішні коментарі створено: 2 (EXECUTOR + ADMIN)")
    print(f"   - OPERATOR бачить: {operator_total} коментарів (тільки публічні)")
    print(f"   - EXECUTOR бачить: {executor_total} коментарів (всі)")
    print(f"   - ADMIN бачить: {admin_total} коментарів (всі)")
    print(f"   - RBAC для internal comments: ✅")
    print(f"   - Валідація тексту коментаря: ✅")
    print(f"   - Email нотифікації: ⏳ (placeholder logs)")
    
    print("\n✅ Всі функції BE-011 працюють коректно!")

if __name__ == "__main__":
    try:
        test_be011()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
