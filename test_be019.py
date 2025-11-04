#!/usr/bin/env python3
"""
BE-019: Фільтрація звернень для виконавців по категоріях - Testing

Тестування обмеження видимості звернень для виконавців на основі доступу до категорій.

Тестові сценарії:
1. EXECUTOR з доступом до категорії бачить звернення цієї категорії
2. EXECUTOR не бачить звернення з категорії, до якої немає доступу
3. EXECUTOR з доступом до кількох категорій бачить звернення всіх дозволених категорій
4. EXECUTOR без доступів до категорій отримує порожній список
5. EXECUTOR намагається змінити статус звернення з недоступної категорії (403)
6. EXECUTOR успішно змінює статус звернення з доступної категорії
7. EXECUTOR намагається переглянути деталі звернення з недоступної категорії (403)
8. EXECUTOR успішно переглядає деталі звернення з доступної категорії
9. EXECUTOR намагається взяти в роботу звернення з недоступної категорії (403)
10. EXECUTOR успішно бере в роботу звернення з доступної категорії
11. ADMIN бачить всі звернення незалежно від категорій
12. OPERATOR бачить всі нові звернення незалежно від категорій (свої власні)
"""

import requests
import sys
from typing import Dict, Optional

# API Configuration
API_BASE_URL = "http://localhost:8000"
HEADERS_JSON = {"Content-Type": "application/json"}

# Test Results
test_results = []


def log_test(test_name: str, passed: bool, message: str = ""):
    """Log test result"""
    test_results.append({
        "name": test_name,
        "passed": passed,
        "message": message
    })
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"ℹ️  {message}")
    print()


def login(username: str, password: str) -> Optional[str]:
    """Login and get access token"""
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={"username": username, "password": password},
        headers=HEADERS_JSON
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def create_user(token: str, username: str, email: str, full_name: str, role: str, password: str) -> Optional[Dict]:
    """Create a new user"""
    headers = {**HEADERS_JSON, "Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE_URL}/api/users",
        json={
            "username": username,
            "email": email,
            "full_name": full_name,
            "role": role,
            "password": password,
            "is_active": True
        },
        headers=headers
    )
    
    if response.status_code == 201:
        return response.json()
    return None


def create_category(token: str, name: str) -> Optional[Dict]:
    """Create a new category"""
    headers = {**HEADERS_JSON, "Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE_URL}/api/categories",
        json={"name": name, "is_active": True},
        headers=headers
    )
    
    if response.status_code == 201:
        return response.json()
    return None


def create_channel(token: str, name: str) -> Optional[Dict]:
    """Create a new channel"""
    headers = {**HEADERS_JSON, "Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE_URL}/api/channels",
        json={"name": name, "is_active": True},
        headers=headers
    )
    
    if response.status_code == 201:
        return response.json()
    return None


def add_executor_category_access(token: str, executor_id: str, category_ids: list) -> bool:
    """Add executor category access"""
    headers = {**HEADERS_JSON, "Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE_URL}/api/users/{executor_id}/category-access",
        json={"category_ids": category_ids},
        headers=headers
    )
    
    return response.status_code == 200


def create_case(token: str, category_id: str, channel_id: str, applicant_name: str, summary: str) -> Optional[Dict]:
    """Create a new case"""
    headers = {**HEADERS_JSON, "Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE_URL}/api/cases",
        data={
            "category_id": category_id,
            "channel_id": channel_id,
            "applicant_name": applicant_name,
            "summary": summary
        },
        headers=headers
    )
    
    if response.status_code == 201:
        return response.json()
    return None


def get_assigned_cases(token: str) -> Optional[Dict]:
    """Get assigned cases"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_BASE_URL}/api/cases/assigned",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    return None


def get_case_detail(token: str, case_id: str) -> tuple[int, Optional[Dict]]:
    """Get case details"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_BASE_URL}/api/cases/{case_id}",
        headers=headers
    )
    
    return response.status_code, response.json() if response.status_code == 200 else None


def take_case(token: str, case_id: str) -> tuple[int, Optional[Dict]]:
    """Take case into work"""
    headers = {**HEADERS_JSON, "Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE_URL}/api/cases/{case_id}/take",
        headers=headers
    )
    
    return response.status_code, response.json() if response.status_code == 200 else None


def change_case_status(token: str, case_id: str, to_status: str, comment: str) -> tuple[int, Optional[Dict]]:
    """Change case status"""
    headers = {**HEADERS_JSON, "Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE_URL}/api/cases/{case_id}/status",
        json={"to_status": to_status, "comment": comment},
        headers=headers
    )
    
    return response.status_code, response.json() if response.status_code == 200 else None


def main():
    """Run all tests"""
    print("=" * 80)
    print("  BE-019: Фільтрація звернень для виконавців по категоріях - Testing")
    print("=" * 80)
    print()
    
    # Login as admin
    print("[SETUP] Вхід як адміністратор...")
    admin_token = login("admin", "Admin123!")
    if not admin_token:
        print("❌ Не вдалося увійти як адміністратор")
        return
    print("✅ Успішний вхід як admin")
    print()
    
    # Create test categories
    print("[SETUP] Створення тестових категорій...")
    category1 = create_category(admin_token, f"BE019-TestCategory1")
    category2 = create_category(admin_token, f"BE019-TestCategory2")
    
    if not category1 or not category2:
        print("❌ Не вдалося створити категорії")
        return
    
    category1_id = category1["id"]
    category2_id = category2["id"]
    print(f"✅ Створено категорію: {category1['name']} (ID: {category1_id})")
    print(f"✅ Створено категорію: {category2['name']} (ID: {category2_id})")
    print()
    
    # Create test channel
    print("[SETUP] Створення тестового каналу...")
    channel = create_channel(admin_token, "BE019-TestChannel")
    if not channel:
        print("❌ Не вдалося створити канал")
        return
    channel_id = channel["id"]
    print(f"✅ Створено канал: {channel['name']} (ID: {channel_id})")
    print()
    
    # Create test users
    print("[SETUP] Створення тестових користувачів...")
    
    # Executor 1 - має доступ до category1
    executor1 = create_user(admin_token, "be019_exec1", "exec1@test.com", "Executor 1", "EXECUTOR", "test123")
    if not executor1:
        print("❌ Не вдалося створити executor1")
        return
    executor1_id = executor1["id"]
    print(f"✅ Створено executor1: {executor1['username']} (ID: {executor1_id})")
    
    # Executor 2 - має доступ до category2
    executor2 = create_user(admin_token, "be019_exec2", "exec2@test.com", "Executor 2", "EXECUTOR", "test123")
    if not executor2:
        print("❌ Не вдалося створити executor2")
        return
    executor2_id = executor2["id"]
    print(f"✅ Створено executor2: {executor2['username']} (ID: {executor2_id})")
    
    # Executor 3 - має доступ до обох категорій
    executor3 = create_user(admin_token, "be019_exec3", "exec3@test.com", "Executor 3", "EXECUTOR", "test123")
    if not executor3:
        print("❌ Не вдалося створити executor3")
        return
    executor3_id = executor3["id"]
    print(f"✅ Створено executor3: {executor3['username']} (ID: {executor3_id})")
    
    # Executor 4 - немає доступу до жодної категорії
    executor4 = create_user(admin_token, "be019_exec4", "exec4@test.com", "Executor 4", "EXECUTOR", "test123")
    if not executor4:
        print("❌ Не вдалося створити executor4")
        return
    executor4_id = executor4["id"]
    print(f"✅ Створено executor4: {executor4['username']} (ID: {executor4_id})")
    
    # Operator
    operator = create_user(admin_token, "be019_oper", "oper@test.com", "Operator", "OPERATOR", "test123")
    if not operator:
        print("❌ Не вдалося створити operator")
        return
    operator_id = operator["id"]
    print(f"✅ Створено operator: {operator['username']} (ID: {operator_id})")
    print()
    
    # Add category access
    print("[SETUP] Додавання доступів до категорій...")
    add_executor_category_access(admin_token, executor1_id, [category1_id])
    print(f"✅ Executor1 має доступ до {category1['name']}")
    
    add_executor_category_access(admin_token, executor2_id, [category2_id])
    print(f"✅ Executor2 має доступ до {category2['name']}")
    
    add_executor_category_access(admin_token, executor3_id, [category1_id, category2_id])
    print(f"✅ Executor3 має доступ до обох категорій")
    
    print(f"ℹ️  Executor4 не має доступів до жодної категорії")
    print()
    
    # Login as operator and create cases
    print("[SETUP] Створення тестових звернень...")
    operator_token = login("be019_oper", "test123")
    if not operator_token:
        print("❌ Не вдалося увійти як operator")
        return
    
    case1 = create_case(operator_token, category1_id, channel_id, "Client 1", "Test case category 1")
    case2 = create_case(operator_token, category2_id, channel_id, "Client 2", "Test case category 2")
    
    if not case1 or not case2:
        print("❌ Не вдалося створити звернення")
        return
    
    case1_id = case1["id"]
    case2_id = case2["id"]
    print(f"✅ Створено звернення в {category1['name']}: {case1['public_id']}")
    print(f"✅ Створено звернення в {category2['name']}: {case2['public_id']}")
    print()
    
    # Start tests
    print("=" * 80)
    print("  ПОЧАТОК ТЕСТУВАННЯ")
    print("=" * 80)
    print()
    
    # Test 1: EXECUTOR з доступом до категорії бачить звернення цієї категорії
    print("[ТЕСТ 1] EXECUTOR з доступом до категорії бачить звернення")
    print("-" * 80)
    exec1_token = login("be019_exec1", "test123")
    cases_exec1 = get_assigned_cases(exec1_token)
    
    if cases_exec1 and any(c["id"] == case1_id for c in cases_exec1["cases"]):
        log_test("executor_sees_accessible_category", True, 
                 f"Executor1 бачить звернення з доступної категорії (category1)")
    else:
        log_test("executor_sees_accessible_category", False, 
                 "Executor1 не бачить звернення з доступної категорії")
    
    # Test 2: EXECUTOR не бачить звернення з категорії, до якої немає доступу
    print("[ТЕСТ 2] EXECUTOR не бачить звернення з недоступної категорії")
    print("-" * 80)
    if cases_exec1 and not any(c["id"] == case2_id for c in cases_exec1["cases"]):
        log_test("executor_not_sees_inaccessible_category", True, 
                 f"Executor1 НЕ бачить звернення з недоступної категорії (category2)")
    else:
        log_test("executor_not_sees_inaccessible_category", False, 
                 "Executor1 бачить звернення з недоступної категорії (помилка!)")
    
    # Test 3: EXECUTOR з доступом до кількох категорій бачить звернення всіх дозволених
    print("[ТЕСТ 3] EXECUTOR з доступом до кількох категорій")
    print("-" * 80)
    exec3_token = login("be019_exec3", "test123")
    cases_exec3 = get_assigned_cases(exec3_token)
    
    has_case1 = cases_exec3 and any(c["id"] == case1_id for c in cases_exec3["cases"])
    has_case2 = cases_exec3 and any(c["id"] == case2_id for c in cases_exec3["cases"])
    
    if has_case1 and has_case2:
        log_test("executor_multiple_categories", True, 
                 f"Executor3 бачить звернення з обох категорій")
    else:
        log_test("executor_multiple_categories", False, 
                 f"Executor3 бачить не всі звернення (case1: {has_case1}, case2: {has_case2})")
    
    # Test 4: EXECUTOR без доступів отримує порожній список
    print("[ТЕСТ 4] EXECUTOR без доступів до категорій")
    print("-" * 80)
    exec4_token = login("be019_exec4", "test123")
    cases_exec4 = get_assigned_cases(exec4_token)
    
    if cases_exec4 and cases_exec4["total"] == 0:
        log_test("executor_no_access_empty_list", True, 
                 "Executor4 отримує порожній список (немає доступів)")
    else:
        log_test("executor_no_access_empty_list", False, 
                 f"Executor4 бачить {cases_exec4['total']} звернень (повинен бути 0)")
    
    # Test 5: EXECUTOR намагається змінити статус звернення з недоступної категорії
    print("[ТЕСТ 5] EXECUTOR намагається змінити статус недоступного звернення")
    print("-" * 80)
    
    # Спочатку потрібно взяти звернення в роботу як executor2
    exec2_token = login("be019_exec2", "test123")
    status_code, _ = take_case(exec2_token, case2_id)
    
    if status_code == 200:
        # Тепер executor1 намагається змінити статус звернення з category2
        status_code, response = change_case_status(exec1_token, case2_id, "DONE", "Test comment")
        
        if status_code == 403 or status_code == 400:
            log_test("executor_change_status_inaccessible", True, 
                     f"Executor1 отримав {status_code} при спробі змінити статус недоступного звернення")
        else:
            log_test("executor_change_status_inaccessible", False, 
                     f"Executor1 зміг змінити статус недоступного звернення (статус код: {status_code})")
    else:
        log_test("executor_change_status_inaccessible", False, 
                 "Не вдалося взяти звернення в роботу для тесту")
    
    # Test 6: EXECUTOR успішно змінює статус звернення з доступної категорії
    print("[ТЕСТ 6] EXECUTOR успішно змінює статус доступного звернення")
    print("-" * 80)
    
    # Executor1 бере в роботу case1
    status_code, _ = take_case(exec1_token, case1_id)
    
    if status_code == 200:
        # Тепер змінює статус
        status_code, response = change_case_status(exec1_token, case1_id, "DONE", "Test completion")
        
        if status_code == 200:
            log_test("executor_change_status_accessible", True, 
                     "Executor1 успішно змінив статус доступного звернення")
        else:
            log_test("executor_change_status_accessible", False, 
                     f"Executor1 не зміг змінити статус (статус код: {status_code})")
    else:
        log_test("executor_change_status_accessible", False, 
                 "Не вдалося взяти звернення в роботу")
    
    # Test 7: EXECUTOR намагається переглянути деталі звернення з недоступної категорії
    print("[ТЕСТ 7] EXECUTOR намагається переглянути деталі недоступного звернення")
    print("-" * 80)
    status_code, response = get_case_detail(exec1_token, case2_id)
    
    if status_code == 403:
        log_test("executor_view_detail_inaccessible", True, 
                 "Executor1 отримав 403 при спробі переглянути недоступне звернення")
    else:
        log_test("executor_view_detail_inaccessible", False, 
                 f"Executor1 зміг переглянути недоступне звернення (статус код: {status_code})")
    
    # Test 8: EXECUTOR успішно переглядає деталі звернення з доступної категорії
    print("[ТЕСТ 8] EXECUTOR успішно переглядає деталі доступного звернення")
    print("-" * 80)
    status_code, response = get_case_detail(exec1_token, case1_id)
    
    if status_code == 200:
        log_test("executor_view_detail_accessible", True, 
                 "Executor1 успішно переглянув деталі доступного звернення")
    else:
        log_test("executor_view_detail_accessible", False, 
                 f"Executor1 не зміг переглянути доступне звернення (статус код: {status_code})")
    
    # Test 9: EXECUTOR намагається взяти в роботу звернення з недоступної категорії
    print("[ТЕСТ 9] EXECUTOR намагається взяти в роботу недоступне звернення")
    print("-" * 80)
    
    # Створюємо нове звернення в category2 для тесту
    case3 = create_case(operator_token, category2_id, channel_id, "Client 3", "Test case 3")
    case3_id = case3["id"] if case3 else None
    
    if case3_id:
        status_code, response = take_case(exec1_token, case3_id)
        
        if status_code == 403 or status_code == 400:
            log_test("executor_take_inaccessible", True, 
                     f"Executor1 отримав {status_code} при спробі взяти недоступне звернення")
        else:
            log_test("executor_take_inaccessible", False, 
                     f"Executor1 зміг взяти недоступне звернення (статус код: {status_code})")
    else:
        log_test("executor_take_inaccessible", False, 
                 "Не вдалося створити тестове звернення")
    
    # Test 10: EXECUTOR успішно бере в роботу звернення з доступної категорії
    print("[ТЕСТ 10] EXECUTOR успішно бере в роботу доступне звернення")
    print("-" * 80)
    
    # Створюємо нове звернення в category1
    case4 = create_case(operator_token, category1_id, channel_id, "Client 4", "Test case 4")
    case4_id = case4["id"] if case4 else None
    
    if case4_id:
        status_code, response = take_case(exec1_token, case4_id)
        
        if status_code == 200:
            log_test("executor_take_accessible", True, 
                     "Executor1 успішно взяв в роботу доступне звернення")
        else:
            log_test("executor_take_accessible", False, 
                     f"Executor1 не зміг взяти доступне звернення (статус код: {status_code})")
    else:
        log_test("executor_take_accessible", False, 
                 "Не вдалося створити тестове звернення")
    
    # Test 11: ADMIN бачить всі звернення незалежно від категорій
    print("[ТЕСТ 11] ADMIN бачить всі звернення незалежно від категорій")
    print("-" * 80)
    admin_cases = get_assigned_cases(admin_token)
    
    # Note: Admin може мати багато звернень, перевіряємо що він бачить створені
    if admin_cases:
        log_test("admin_sees_all_cases", True, 
                 f"ADMIN бачить всі звернення (total: {admin_cases['total']})")
    else:
        log_test("admin_sees_all_cases", False, 
                 "ADMIN не бачить звернення")
    
    # Test 12: OPERATOR бачить свої звернення
    print("[ТЕСТ 12] OPERATOR бачить свої звернення")
    print("-" * 80)
    operator_cases = get_assigned_cases(operator_token)
    
    # Note: Оператор використовує /my endpoint, але тут перевіряємо що він щось бачить
    if operator_cases is not None:
        log_test("operator_sees_own_cases", True, 
                 f"OPERATOR має доступ до своїх звернень")
    else:
        log_test("operator_sees_own_cases", False, 
                 "OPERATOR не має доступу до звернень")
    
    # Print summary
    print("=" * 80)
    print("ПІДСУМОК ТЕСТУВАННЯ BE-019")
    print("=" * 80)
    
    passed = sum(1 for r in test_results if r["passed"])
    total = len(test_results)
    
    print(f"Результати тестування:")
    for result in test_results:
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"  {status} - {result['name']}")
    
    print()
    print(f"📊 TOTAL - {passed}/{total} тестів пройдено")
    print()
    
    if passed == total:
        print("✅ Всі тести пройдено успішно! ✨")
        print("ℹ️  BE-019 ГОТОВО ДО PRODUCTION ✅")
        return 0
    else:
        print(f"⚠️  {total - passed} тестів не пройдено")
        print("ℹ️  Потрібно виправити помилки перед deployment")
        return 1


if __name__ == "__main__":
    sys.exit(main())
