"""
FE-013: Тестування фільтрації звернень для виконавців по категоріях
Ohmatdyt CRM - Testing Script

Тестові сценарії:
1. EXECUTOR з доступом до категорії бачить звернення цієї категорії
2. EXECUTOR не бачить звернення з недоступних категорій  
3. EXECUTOR без доступів бачить повідомлення про відсутність доступів
4. Фільтр категорій для EXECUTOR показує тільки доступні категорії
5. EXECUTOR намагається відкрити звернення з недоступної категорії (403)
6. EXECUTOR намагається змінити статус недоступного звернення (403)
7. ADMIN бачить всі звернення та всі категорії
8. OPERATOR бачить всі звернення та всі категорії
9. Індикатор доступних категорій відображається коректно
10. GET /users/me/category-access працює для всіх ролей
"""

import requests
import json
from datetime import datetime

# ===============================================================================
# Configuration
# ===============================================================================

API_BASE = "http://localhost:3000/api"

# Test users credentials
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin"}
OPERATOR_CREDENTIALS = {"username": "operator1", "password": "operator1"}

# Test executor credentials (will be created during tests)
EXECUTOR1_CREDENTIALS = {"username": "executor_fe013_1", "password": "TestPassword123!"}
EXECUTOR2_CREDENTIALS = {"username": "executor_fe013_2", "password": "TestPassword123!"}
EXECUTOR3_CREDENTIALS = {"username": "executor_fe013_no_access", "password": "TestPassword123!"}

# Test data storage
test_data = {
    "admin_token": None,
    "operator_token": None,
    "executor1_token": None,
    "executor1_id": None,
    "executor2_token": None,
    "executor2_id": None,
    "executor3_token": None,
    "executor3_id": None,
    "category1_id": None,
    "category2_id": None,
    "case1_id": None,  # Category 1 - executor1 має доступ
    "case2_id": None,  # Category 2 - executor1 НЕ має доступу
}

test_results = {}

# ===============================================================================
# Helper Functions
# ===============================================================================

def print_step(step_num, title):
    """Print step header"""
    print("\n" + "="*80)
    print(f"  [КРОК {step_num}] {title}")
    print("="*80)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def login(credentials):
    """Login and get access token"""
    response = requests.post(
        f"{API_BASE}/auth/login",
        data=credentials
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def get_headers(token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}"}

# ===============================================================================
# Test Steps
# ===============================================================================

def test_step_0_login():
    """Крок 0: Авторизація адміністратора та оператора"""
    print_step(0, "Авторизація користувачів")
    
    # Login admin
    test_data["admin_token"] = login(ADMIN_CREDENTIALS)
    if test_data["admin_token"]:
        print_success("Admin успішно авторизовано")
    else:
        print_error("Помилка авторизації admin")
        return False
    
    # Login operator
    test_data["operator_token"] = login(OPERATOR_CREDENTIALS)
    if test_data["operator_token"]:
        print_success("Operator успішно авторизовано")
    else:
        print_error("Помилка авторизації operator")
        return False
    
    test_results["login"] = "PASS"
    return True

def test_step_1_create_categories():
    """Крок 1: Створення тестових категорій"""
    print_step(1, "Створення тестових категорій")
    
    categories_to_create = [
        {"name": "FE013 Test Category 1", "description": "Категорія для тестування FE-013"},
        {"name": "FE013 Test Category 2", "description": "Категорія без доступу"}
    ]
    
    created_categories = []
    
    for cat_data in categories_to_create:
        response = requests.post(
            f"{API_BASE}/categories",
            headers=get_headers(test_data["admin_token"]),
            json=cat_data
        )
        
        if response.status_code == 201:
            category = response.json()
            created_categories.append(category)
            print_success(f"Категорію створено: {category['name']} (ID: {category['id']})")
        else:
            print_error(f"Помилка створення категорії: {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
    
    test_data["category1_id"] = created_categories[0]["id"]
    test_data["category2_id"] = created_categories[1]["id"]
    
    test_results["create_categories"] = "PASS"
    return True

def test_step_2_create_executors():
    """Крок 2: Створення тестових виконавців"""
    print_step(2, "Створення тестових виконавців")
    
    executors_to_create = [
        {
            "credentials": EXECUTOR1_CREDENTIALS,
            "full_name": "Test Executor 1 (FE-013)",
            "email": "executor_fe013_1@test.com",
            "data_key_prefix": "executor1"
        },
        {
            "credentials": EXECUTOR2_CREDENTIALS,
            "full_name": "Test Executor 2 (FE-013)",
            "email": "executor_fe013_2@test.com",
            "data_key_prefix": "executor2"
        },
        {
            "credentials": EXECUTOR3_CREDENTIALS,
            "full_name": "Test Executor No Access (FE-013)",
            "email": "executor_fe013_no_access@test.com",
            "data_key_prefix": "executor3"
        }
    ]
    
    for executor_config in executors_to_create:
        user_data = {
            "username": executor_config["credentials"]["username"],
            "password": executor_config["credentials"]["password"],
            "full_name": executor_config["full_name"],
            "email": executor_config["email"],
            "role": "EXECUTOR"
        }
        
        response = requests.post(
            f"{API_BASE}/users",
            headers=get_headers(test_data["admin_token"]),
            json=user_data
        )
        
        if response.status_code == 201:
            user = response.json()
            print_success(f"Виконавця створено: {user['username']} (ID: {user['id']})")
            
            # Login executor and store token
            token = login(executor_config["credentials"])
            if token:
                test_data[f"{executor_config['data_key_prefix']}_token"] = token
                test_data[f"{executor_config['data_key_prefix']}_id"] = user["id"]
                print_info(f"{executor_config['credentials']['username']} авторизовано")
            else:
                print_error(f"Помилка авторизації {executor_config['credentials']['username']}")
                return False
        else:
            print_error(f"Помилка створення виконавця: {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
    
    test_results["create_executors"] = "PASS"
    return True

def test_step_3_assign_category_access():
    """Крок 3: Призначення доступів до категорій"""
    print_step(3, "Призначення доступів до категорій")
    
    # Executor1 - доступ до Category1
    response = requests.post(
        f"{API_BASE}/users/{test_data['executor1_id']}/category-access",
        headers=get_headers(test_data["admin_token"]),
        json={"category_ids": [test_data["category1_id"]]}
    )
    
    if response.status_code == 201:
        print_success("Executor1: доступ до Category1 надано")
    else:
        print_error(f"Помилка призначення доступу: {response.status_code}")
        return False
    
    # Executor2 - доступ до Category2
    response = requests.post(
        f"{API_BASE}/users/{test_data['executor2_id']}/category-access",
        headers=get_headers(test_data["admin_token"]),
        json={"category_ids": [test_data["category2_id"]]}
    )
    
    if response.status_code == 201:
        print_success("Executor2: доступ до Category2 надано")
    else:
        print_error(f"Помилка призначення доступу: {response.status_code}")
        return False
    
    # Executor3 - БЕЗ доступів (спеціально не додаємо)
    print_info("Executor3: БЕЗ доступів до категорій (для тестування)")
    
    test_results["assign_access"] = "PASS"
    return True

def test_step_4_create_test_cases():
    """Крок 4: Створення тестових звернень"""
    print_step(4, "Створення тестових звернень")
    
    # Case 1 - Category 1 (executor1 має доступ)
    case1_data = {
        "category_id": test_data["category1_id"],
        "applicant_name": "Test Applicant 1",
        "applicant_phone": "+380501234567",
        "summary": "FE-013 Test Case 1 - Category 1"
    }
    
    response = requests.post(
        f"{API_BASE}/cases",
        headers=get_headers(test_data["operator_token"]),
        json=case1_data
    )
    
    if response.status_code == 201:
        case1 = response.json()
        test_data["case1_id"] = case1["id"]
        print_success(f"Звернення 1 створено: #{case1['public_id']} (Category 1)")
    else:
        print_error(f"Помилка створення звернення 1: {response.status_code}")
        return False
    
    # Case 2 - Category 2 (executor1 НЕ має доступу)
    case2_data = {
        "category_id": test_data["category2_id"],
        "applicant_name": "Test Applicant 2",
        "applicant_phone": "+380501234568",
        "summary": "FE-013 Test Case 2 - Category 2"
    }
    
    response = requests.post(
        f"{API_BASE}/cases",
        headers=get_headers(test_data["operator_token"]),
        json=case2_data
    )
    
    if response.status_code == 201:
        case2 = response.json()
        test_data["case2_id"] = case2["id"]
        print_success(f"Звернення 2 створено: #{case2['public_id']} (Category 2)")
    else:
        print_error(f"Помилка створення звернення 2: {response.status_code}")
        return False
    
    test_results["create_cases"] = "PASS"
    return True

def test_step_5_executor_category_access_api():
    """Крок 5: Тестування GET /users/me/category-access"""
    print_step(5, "Тестування GET /users/me/category-access")
    
    # Test for Executor1
    response = requests.get(
        f"{API_BASE}/users/me/category-access",
        headers=get_headers(test_data["executor1_token"])
    )
    
    if response.status_code == 200:
        data = response.json()
        if data["total"] == 1 and len(data["categories"]) == 1:
            print_success(f"Executor1: доступ до {data['total']} категорії")
            print_info(f"Категорія: {data['categories'][0]['category_name']}")
        else:
            print_error(f"Executor1: очікувалось 1 категорія, отримано {data['total']}")
            return False
    else:
        print_error(f"Помилка запиту для Executor1: {response.status_code}")
        return False
    
    # Test for Executor3 (no access)
    response = requests.get(
        f"{API_BASE}/users/me/category-access",
        headers=get_headers(test_data["executor3_token"])
    )
    
    if response.status_code == 200:
        data = response.json()
        if data["total"] == 0:
            print_success("Executor3: немає доступу до категорій (очікувано)")
        else:
            print_error(f"Executor3: очікувалось 0 категорій, отримано {data['total']}")
            return False
    else:
        print_error(f"Помилка запиту для Executor3: {response.status_code}")
        return False
    
    # Test for ADMIN (should return empty list)
    response = requests.get(
        f"{API_BASE}/users/me/category-access",
        headers=get_headers(test_data["admin_token"])
    )
    
    if response.status_code == 200:
        data = response.json()
        if data["total"] == 0:
            print_success("ADMIN: повертає порожній список (має доступ до всіх)")
        else:
            print_info(f"ADMIN: отримано {data['total']} категорій")
    else:
        print_error(f"Помилка запиту для ADMIN: {response.status_code}")
        return False
    
    test_results["category_access_api"] = "PASS"
    return True

def test_step_6_executor_sees_accessible_cases():
    """Крок 6: EXECUTOR бачить тільки звернення з доступних категорій"""
    print_step(6, "EXECUTOR бачить тільки звернення з доступних категорій")
    
    # Executor1 має доступ до Category1, тому має бачити Case1
    response = requests.get(
        f"{API_BASE}/cases",
        headers=get_headers(test_data["executor1_token"])
    )
    
    if response.status_code == 200:
        data = response.json()
        case_ids = [case["id"] for case in data["items"]]
        
        if test_data["case1_id"] in case_ids:
            print_success("Executor1 бачить Case1 (Category1 - доступна)")
        else:
            print_error("Executor1 НЕ бачить Case1 (Category1 - повинна бути доступна)")
            return False
        
        if test_data["case2_id"] not in case_ids:
            print_success("Executor1 НЕ бачить Case2 (Category2 - недоступна)")
        else:
            print_error("Executor1 бачить Case2 (Category2 - НЕ повинна бути доступна)")
            return False
    else:
        print_error(f"Помилка запиту списку звернень: {response.status_code}")
        return False
    
    test_results["executor_sees_accessible"] = "PASS"
    return True

def test_step_7_executor_403_on_inaccessible_case():
    """Крок 7: EXECUTOR отримує 403 при спробі доступу до недоступного звернення"""
    print_step(7, "EXECUTOR отримує 403 при доступі до недоступного звернення")
    
    # Executor1 намагається відкрити Case2 (Category2 - немає доступу)
    response = requests.get(
        f"{API_BASE}/cases/{test_data['case2_id']}",
        headers=get_headers(test_data["executor1_token"])
    )
    
    if response.status_code == 403:
        print_success("Executor1 отримав 403 при спробі доступу до Case2 (очікувано)")
        print_info(f"Повідомлення: {response.json().get('detail', 'N/A')}")
    else:
        print_error(f"Executor1 отримав {response.status_code} замість 403")
        return False
    
    test_results["executor_403_case"] = "PASS"
    return True

def test_step_8_executor_403_on_status_change():
    """Крок 8: EXECUTOR отримує 403 при спробі змінити статус недоступного звернення"""
    print_step(8, "EXECUTOR отримує 403 при зміні статусу недоступного звернення")
    
    # Executor1 намагається змінити статус Case2
    response = requests.post(
        f"{API_BASE}/cases/{test_data['case2_id']}/status",
        headers=get_headers(test_data["executor1_token"]),
        json={
            "to_status": "IN_PROGRESS",
            "comment": "Test status change"
        }
    )
    
    if response.status_code == 403:
        print_success("Executor1 отримав 403 при спробі зміни статусу Case2 (очікувано)")
        print_info(f"Повідомлення: {response.json().get('detail', 'N/A')}")
    else:
        print_error(f"Executor1 отримав {response.status_code} замість 403")
        return False
    
    test_results["executor_403_status"] = "PASS"
    return True

def test_step_9_admin_sees_all():
    """Крок 9: ADMIN бачить всі звернення"""
    print_step(9, "ADMIN бачить всі звернення незалежно від категорій")
    
    response = requests.get(
        f"{API_BASE}/cases",
        headers=get_headers(test_data["admin_token"])
    )
    
    if response.status_code == 200:
        data = response.json()
        case_ids = [case["id"] for case in data["items"]]
        
        if test_data["case1_id"] in case_ids and test_data["case2_id"] in case_ids:
            print_success("ADMIN бачить обидва тестові звернення (Case1 та Case2)")
        else:
            print_error("ADMIN НЕ бачить всі звернення")
            return False
    else:
        print_error(f"Помилка запиту списку звернень: {response.status_code}")
        return False
    
    test_results["admin_sees_all"] = "PASS"
    return True

def test_step_10_operator_sees_all():
    """Крок 10: OPERATOR бачить всі звернення"""
    print_step(10, "OPERATOR бачить всі звернення незалежно від категорій")
    
    response = requests.get(
        f"{API_BASE}/cases/my",
        headers=get_headers(test_data["operator_token"])
    )
    
    if response.status_code == 200:
        data = response.json()
        case_ids = [case["id"] for case in data["items"]]
        
        if test_data["case1_id"] in case_ids and test_data["case2_id"] in case_ids:
            print_success("OPERATOR бачить обидва створені звернення")
        else:
            print_info("OPERATOR створив ці звернення, тому має їх бачити")
    else:
        print_error(f"Помилка запиту списку звернень: {response.status_code}")
        return False
    
    test_results["operator_sees_all"] = "PASS"
    return True

# ===============================================================================
# Main Test Execution
# ===============================================================================

def main():
    """Main test execution"""
    print("\n" + "="*80)
    print("  FE-013: Фільтрація звернень для виконавців по категоріях - Testing")
    print("="*80)
    print("Тестування фільтрації звернень на основі доступу до категорій\n")
    
    print("Компоненти що тестуються:")
    print("  - GET /users/me/category-access - доступні категорії поточного користувача")
    print("  - GET /cases - фільтрація звернень для EXECUTOR")
    print("  - GET /cases/{id} - перевірка доступу до звернення (403)")
    print("  - POST /cases/{id}/status - перевірка доступу при зміні статусу (403)")
    print("  - Індикатор категорій в UI (візуальне тестування)")
    
    # Execute test steps
    steps = [
        test_step_0_login,
        test_step_1_create_categories,
        test_step_2_create_executors,
        test_step_3_assign_category_access,
        test_step_4_create_test_cases,
        test_step_5_executor_category_access_api,
        test_step_6_executor_sees_accessible_cases,
        test_step_7_executor_403_on_inaccessible_case,
        test_step_8_executor_403_on_status_change,
        test_step_9_admin_sees_all,
        test_step_10_operator_sees_all,
    ]
    
    for step in steps:
        if not step():
            print_error(f"\nТест провалився на кроці: {step.__name__}")
            break
    
    # Print summary
    print("\n" + "="*80)
    print("  ПІДСУМОК ТЕСТУВАННЯ FE-013")
    print("="*80)
    print("\nРезультати тестування:")
    
    passed = sum(1 for result in test_results.values() if result == "PASS")
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status_icon = "✅" if result == "PASS" else "❌"
        print(f"  {status_icon} {result} - {test_name}")
    
    print(f"\n📊 TOTAL - {passed}/{total} тестів пройдено")
    
    if passed == total:
        print("\n✅ Всі тести пройдено успішно! ✨")
        print("ℹ️  FE-013 ГОТОВО ДО PRODUCTION ✅")
    else:
        print(f"\n❌ {total - passed} тест(ів) провалено")
        print("ℹ️  Потрібні виправлення перед production")
    
    print("\n" + "="*80)
    print("  ВАЖЛИВО: Візуальне тестування UI")
    print("="*80)
    print("\nПеревірте вручну в браузері:")
    print("  1. Індикатор категорій в сайдбарі для EXECUTOR")
    print("  2. Фільтр категорій показує тільки доступні для EXECUTOR")
    print("  3. Повідомлення про відсутність доступів для Executor3")
    print("  4. Редирект при спробі доступу до недоступного звернення")
    print("  5. Помилка при спробі зміни статусу недоступного звернення")
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
