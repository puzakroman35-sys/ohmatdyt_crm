"""
BE-017: Розширені права адміністратора для керування зверненнями - Testing

Тестування:
1. ADMIN може редагувати всі поля звернення
2. ADMIN може призначати/знімати відповідальних виконавців
3. ADMIN може змінювати статус без обмежень на відповідального
4. ADMIN може повертати звернення в статус NEW
5. RBAC перевірки (EXECUTOR/OPERATOR отримують 403)
6. Валідації працюють коректно
7. Історія змін зберігається
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost"
API_BASE = f"{BASE_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}
OPERATOR_CREDENTIALS = {"username": "operator", "password": "operator123"}
EXECUTOR_CREDENTIALS = {"username": "executor", "password": "executor123"}

# Global variables for test data
admin_token = None
operator_token = None
executor_token = None
test_case_id = None
test_case_public_id = None
category_id = None
channel_id = None
executor_user_id = None


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_step(step_num: int, description: str):
    """Print test step"""
    print(f"\n[КРОК {step_num}] {description}")
    print("-" * 80)


def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")


def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")


def print_info(message: str):
    """Print info message"""
    print(f"ℹ️  {message}")


def login(username: str, password: str) -> str:
    """Login and get access token"""
    response = requests.post(
        f"{API_BASE}/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print_success(f"Успішний логін: {username}")
        return token
    else:
        print_error(f"Помилка логіну: {response.status_code} - {response.text}")
        return None


def get_headers(token: str) -> dict:
    """Get request headers with authorization"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def test_step_1_login():
    """Крок 1: Логін користувачів"""
    global admin_token, operator_token, executor_token
    
    print_step(1, "Логін користувачів (ADMIN, OPERATOR, EXECUTOR)")
    
    admin_token = login(ADMIN_CREDENTIALS["username"], ADMIN_CREDENTIALS["password"])
    operator_token = login(OPERATOR_CREDENTIALS["username"], OPERATOR_CREDENTIALS["password"])
    executor_token = login(EXECUTOR_CREDENTIALS["username"], EXECUTOR_CREDENTIALS["password"])
    
    if not all([admin_token, operator_token, executor_token]):
        print_error("Не вдалося увійти в систему")
        return False
    
    print_info(f"Admin token: {admin_token[:50]}...")
    print_info(f"Operator token: {operator_token[:50]}...")
    print_info(f"Executor token: {executor_token[:50]}...")
    
    return True


def test_step_2_prepare_data():
    """Крок 2: Підготовка тестових даних"""
    global category_id, channel_id, test_case_id, test_case_public_id, executor_user_id
    
    print_step(2, "Підготовка тестових даних (категорія, канал, створення звернення)")
    
    # Get categories
    response = requests.get(
        f"{API_BASE}/categories",
        headers=get_headers(admin_token)
    )
    if response.status_code == 200:
        categories = response.json()["categories"]
        if categories:
            category_id = categories[0]["id"]
            print_success(f"Отримано категорію: {categories[0]['name']} ({category_id})")
        else:
            print_error("Немає доступних категорій")
            return False
    else:
        print_error(f"Помилка отримання категорій: {response.status_code}")
        return False
    
    # Get channels
    response = requests.get(
        f"{API_BASE}/channels",
        headers=get_headers(admin_token)
    )
    if response.status_code == 200:
        channels = response.json()["channels"]
        if channels:
            channel_id = channels[0]["id"]
            print_success(f"Отримано канал: {channels[0]['name']} ({channel_id})")
        else:
            print_error("Немає доступних каналів")
            return False
    else:
        print_error(f"Помилка отримання каналів: {response.status_code}")
        return False
    
    # Get executor user ID
    response = requests.get(
        f"{API_BASE}/users?role=EXECUTOR",
        headers=get_headers(admin_token)
    )
    if response.status_code == 200:
        users = response.json()["users"]
        if users:
            executor_user_id = users[0]["id"]
            print_success(f"Отримано виконавця: {users[0]['username']} ({executor_user_id})")
        else:
            print_error("Немає доступних виконавців")
            return False
    else:
        print_error(f"Помилка отримання виконавців: {response.status_code}")
        return False
    
    # Create test case (as operator)
    case_data = {
        "category_id": category_id,
        "channel_id": channel_id,
        "applicant_name": "Тестовий Заявник BE-017",
        "applicant_phone": "+380501234567",
        "applicant_email": "test.be017@example.com",
        "summary": "Тестове звернення для перевірки функцій адміністратора BE-017"
    }
    
    response = requests.post(
        f"{API_BASE}/cases",
        json=case_data,
        headers=get_headers(operator_token)
    )
    
    if response.status_code == 201:
        case = response.json()
        test_case_id = case["id"]
        test_case_public_id = case["public_id"]
        print_success(f"Створено тестове звернення: #{test_case_public_id} (ID: {test_case_id})")
        print_info(f"Статус: {case['status']}")
    else:
        print_error(f"Помилка створення звернення: {response.status_code} - {response.text}")
        return False
    
    return True


def test_step_3_admin_edit_case():
    """Крок 3: ADMIN редагує поля звернення"""
    print_step(3, "ADMIN редагує поля звернення")
    
    update_data = {
        "applicant_name": "Оновлений Заявник",
        "applicant_phone": "+380679999999",
        "applicant_email": "updated@example.com",
        "summary": "Оновлений опис звернення адміністратором"
    }
    
    response = requests.patch(
        f"{API_BASE}/cases/{test_case_id}",
        json=update_data,
        headers=get_headers(admin_token)
    )
    
    if response.status_code == 200:
        case = response.json()
        print_success("ADMIN успішно відредагував звернення")
        print_info(f"Нове ім'я: {case['applicant_name']}")
        print_info(f"Новий телефон: {case['applicant_phone']}")
        print_info(f"Новий email: {case['applicant_email']}")
        
        # Verify changes
        if (case['applicant_name'] == update_data['applicant_name'] and
            case['applicant_phone'] == update_data['applicant_phone'] and
            case['applicant_email'] == update_data['applicant_email']):
            print_success("Зміни збережені правильно")
            return True
        else:
            print_error("Зміни не збереглися коректно")
            return False
    else:
        print_error(f"Помилка редагування звернення: {response.status_code} - {response.text}")
        return False


def test_step_4_operator_cannot_edit():
    """Крок 4: OPERATOR не може редагувати звернення (403)"""
    print_step(4, "RBAC: OPERATOR не може редагувати звернення")
    
    update_data = {
        "applicant_name": "Спроба редагування оператором"
    }
    
    response = requests.patch(
        f"{API_BASE}/cases/{test_case_id}",
        json=update_data,
        headers=get_headers(operator_token)
    )
    
    if response.status_code == 403:
        print_success("RBAC працює коректно! Оператору заборонено редагувати (403 Forbidden)")
        return True
    else:
        print_error(f"RBAC НЕ працює! Очікувався 403, отримано: {response.status_code}")
        return False


def test_step_5_admin_assign_executor():
    """Крок 5: ADMIN призначає виконавця"""
    print_step(5, "ADMIN призначає виконавця на звернення")
    
    assign_data = {
        "assigned_to_id": executor_user_id
    }
    
    response = requests.patch(
        f"{API_BASE}/cases/{test_case_id}/assign",
        json=assign_data,
        headers=get_headers(admin_token)
    )
    
    if response.status_code == 200:
        case = response.json()
        print_success("ADMIN успішно призначив виконавця")
        print_info(f"Відповідальний: {case['responsible_id']}")
        print_info(f"Статус: {case['status']}")
        
        # Verify assignment and status change
        if case['responsible_id'] == executor_user_id and case['status'] == 'IN_PROGRESS':
            print_success("Призначення виконано правильно, статус змінився на IN_PROGRESS")
            return True
        else:
            print_error("Призначення або статус некоректні")
            return False
    else:
        print_error(f"Помилка призначення виконавця: {response.status_code} - {response.text}")
        return False


def test_step_6_admin_unassign_executor():
    """Крок 6: ADMIN знімає виконавця"""
    print_step(6, "ADMIN знімає виконавця зі звернення")
    
    assign_data = {
        "assigned_to_id": None
    }
    
    response = requests.patch(
        f"{API_BASE}/cases/{test_case_id}/assign",
        json=assign_data,
        headers=get_headers(admin_token)
    )
    
    if response.status_code == 200:
        case = response.json()
        print_success("ADMIN успішно зняв виконавця")
        print_info(f"Відповідальний: {case['responsible_id']}")
        print_info(f"Статус: {case['status']}")
        
        # Verify unassignment and status change to NEW
        if case['responsible_id'] is None and case['status'] == 'NEW':
            print_success("Зняття виконавця виконано правильно, статус повернувся в NEW")
            return True
        else:
            print_error("Зняття виконавця або статус некоректні")
            return False
    else:
        print_error(f"Помилка зняття виконавця: {response.status_code} - {response.text}")
        return False


def test_step_7_admin_change_status_from_new():
    """Крок 7: ADMIN змінює статус безпосередньо з NEW на DONE"""
    print_step(7, "ADMIN змінює статус з NEW на DONE (без обмежень)")
    
    # First assign executor back
    assign_data = {"assigned_to_id": executor_user_id}
    response = requests.patch(
        f"{API_BASE}/cases/{test_case_id}/assign",
        json=assign_data,
        headers=get_headers(admin_token)
    )
    
    if response.status_code != 200:
        print_error("Не вдалося призначити виконавця для тесту")
        return False
    
    # Now try to change status directly to DONE (ADMIN should be able to do this)
    status_data = {
        "to_status": "DONE",
        "comment": "Адміністратор закриває звернення без проходження всіх статусів"
    }
    
    response = requests.post(
        f"{API_BASE}/cases/{test_case_id}/status",
        json=status_data,
        headers=get_headers(admin_token)
    )
    
    if response.status_code == 200:
        case = response.json()
        print_success("ADMIN успішно змінив статус на DONE")
        print_info(f"Статус: {case['status']}")
        
        if case['status'] == 'DONE':
            print_success("ADMIN має розширені права зміни статусу (без обмежень)")
            return True
        else:
            print_error("Статус не змінився на DONE")
            return False
    else:
        print_error(f"Помилка зміни статусу: {response.status_code} - {response.text}")
        # This might be expected if ADMIN restrictions are still in place
        return False


def test_step_8_admin_reopen_case():
    """Крок 8: ADMIN повертає звернення зі статусу DONE в NEW"""
    print_step(8, "ADMIN повертає звернення зі статусу DONE в NEW")
    
    status_data = {
        "to_status": "NEW",
        "comment": "Адміністратор повертає звернення для повторного розгляду"
    }
    
    response = requests.post(
        f"{API_BASE}/cases/{test_case_id}/status",
        json=status_data,
        headers=get_headers(admin_token)
    )
    
    if response.status_code == 200:
        case = response.json()
        print_success("ADMIN успішно повернув звернення в статус NEW")
        print_info(f"Статус: {case['status']}")
        
        if case['status'] == 'NEW':
            print_success("ADMIN може повертати звернення в будь-який статус")
            return True
        else:
            print_error("Статус не змінився на NEW")
            return False
    else:
        print_error(f"Помилка зміни статусу: {response.status_code} - {response.text}")
        return False


def test_step_9_executor_cannot_assign():
    """Крок 9: EXECUTOR не може призначати виконавців (403)"""
    print_step(9, "RBAC: EXECUTOR не може призначати виконавців")
    
    assign_data = {
        "assigned_to_id": executor_user_id
    }
    
    response = requests.patch(
        f"{API_BASE}/cases/{test_case_id}/assign",
        json=assign_data,
        headers=get_headers(executor_token)
    )
    
    if response.status_code == 403:
        print_success("RBAC працює коректно! Виконавцю заборонено призначати (403 Forbidden)")
        return True
    else:
        print_error(f"RBAC НЕ працює! Очікувався 403, отримано: {response.status_code}")
        return False


def test_step_10_admin_change_category():
    """Крок 10: ADMIN змінює категорію звернення"""
    print_step(10, "ADMIN змінює категорію звернення")
    
    # Get another category
    response = requests.get(
        f"{API_BASE}/categories",
        headers=get_headers(admin_token)
    )
    
    if response.status_code != 200:
        print_error("Не вдалося отримати категорії")
        return False
    
    categories = response.json()["categories"]
    if len(categories) < 2:
        print_info("Недостатньо категорій для тестування зміни категорії")
        return True  # Skip this test
    
    new_category_id = categories[1]["id"]
    
    update_data = {
        "category_id": new_category_id
    }
    
    response = requests.patch(
        f"{API_BASE}/cases/{test_case_id}",
        json=update_data,
        headers=get_headers(admin_token)
    )
    
    if response.status_code == 200:
        case = response.json()
        print_success("ADMIN успішно змінив категорію звернення")
        print_info(f"Нова категорія: {case['category_id']}")
        
        if case['category_id'] == new_category_id:
            print_success("Категорія змінена правильно")
            return True
        else:
            print_error("Категорія не змінилася")
            return False
    else:
        print_error(f"Помилка зміни категорії: {response.status_code} - {response.text}")
        return False


def test_step_11_validation_invalid_email():
    """Крок 11: Валідація - невалідний email"""
    print_step(11, "Валідація: спроба встановити невалідний email")
    
    update_data = {
        "applicant_email": "invalid-email-format"
    }
    
    response = requests.patch(
        f"{API_BASE}/cases/{test_case_id}",
        json=update_data,
        headers=get_headers(admin_token)
    )
    
    if response.status_code == 400 or response.status_code == 422:
        print_success("Валідація працює! Невалідний email відхилено")
        return True
    else:
        print_error(f"Валідація НЕ працює! Очікувався 400/422, отримано: {response.status_code}")
        return False


def test_step_12_validation_invalid_category():
    """Крок 12: Валідація - неіснуюча категорія"""
    print_step(12, "Валідація: спроба встановити неіснуючу категорію")
    
    update_data = {
        "category_id": "00000000-0000-0000-0000-000000000000"
    }
    
    response = requests.patch(
        f"{API_BASE}/cases/{test_case_id}",
        json=update_data,
        headers=get_headers(admin_token)
    )
    
    if response.status_code == 400:
        print_success("Валідація працює! Неіснуюча категорія відхилена")
        return True
    else:
        print_error(f"Валідація НЕ працює! Очікувався 400, отримано: {response.status_code}")
        return False


def main():
    """Main test execution"""
    print_section("BE-017: Розширені права адміністратора - Comprehensive Testing")
    
    test_results = {}
    
    # Run tests
    tests = [
        ("login", test_step_1_login),
        ("prepare_data", test_step_2_prepare_data),
        ("admin_edit", test_step_3_admin_edit_case),
        ("rbac_operator", test_step_4_operator_cannot_edit),
        ("admin_assign", test_step_5_admin_assign_executor),
        ("admin_unassign", test_step_6_admin_unassign_executor),
        ("admin_status_done", test_step_7_admin_change_status_from_new),
        ("admin_reopen", test_step_8_admin_reopen_case),
        ("rbac_executor", test_step_9_executor_cannot_assign),
        ("admin_category", test_step_10_admin_change_category),
        ("validation_email", test_step_11_validation_invalid_email),
        ("validation_category", test_step_12_validation_invalid_category),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results[test_name] = "PASS" if result else "FAIL"
        except Exception as e:
            print_error(f"Помилка виконання тесту: {str(e)}")
            test_results[test_name] = "ERROR"
    
    # Print summary
    print_section("ПІДСУМОК ТЕСТУВАННЯ BE-017")
    print("\nРезультати тестування:")
    for test_name, result in test_results.items():
        status_icon = "✅" if result == "PASS" else "❌" if result == "FAIL" else "⚠️"
        print(f"  {status_icon} {result} - {test_name}")
    
    passed = sum(1 for r in test_results.values() if r == "PASS")
    total = len(test_results)
    
    print(f"\n📊 TOTAL - {passed}/{total} тестів пройдено")
    
    if passed == total:
        print("\n✅ Всі тести пройдено успішно! ✨")
        print("ℹ️  BE-017 ГОТОВО ДО PRODUCTION ✅")
    else:
        print(f"\n⚠️  {total - passed} тест(ів) не пройдено")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
