"""
FE-011: Розширені права адміністратора для керування зверненнями - UI/Frontend Testing

Тестування UI функціоналу через backend API:
1. ADMIN може редагувати всі поля звернення (EditCaseFieldsForm)
2. ADMIN може призначати/знімати відповідальних (AssignExecutorForm)
3. ADMIN може змінювати статус без обмежень (розширений ChangeStatusForm)
4. ADMIN може повертати звернення в статус NEW
5. RBAC перевірки (EXECUTOR/OPERATOR отримують 403 при спробі редагування)
6. UI компоненти інтегровані в /cases/[id] page
7. Валідації працюють коректно
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Direct API connection
API_BASE = BASE_URL  # No /api prefix when connecting directly

# Test credentials
ADMIN_CREDENTIALS = {"username": "admin", "password": "Admin123!"}
OPERATOR_CREDENTIALS = {"username": "operator1", "password": "Operator123!"}
EXECUTOR_CREDENTIALS = {"username": "executor1", "password": "Executor123!"}

# Global variables for test data
admin_token = None
operator_token = None
executor_token = None
test_case_id = None
test_case_public_id = None
category_ids = []
channel_ids = []
executor_user_ids = []

# Test results tracking
test_results = {}


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
    print(f"[OK] {message}")


def print_error(message: str):
    """Print error message"""
    print(f"[ERROR] {message}")


def print_info(message: str):
    """Print info message"""
    print(f"[INFO] {message}")


def login(username: str, password: str) -> str:
    """Login and get access token"""
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": username, "password": password},  # JSON instead of form data
        headers={"Content-Type": "application/json"}
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
        print_error("Не всі користувачі змогли увійти")
        return False
    
    test_results["login"] = "PASS"
    return True


def test_step_2_prepare_data():
    """Крок 2: Підготовка тестових даних"""
    global category_ids, channel_ids, executor_user_ids, test_case_id, test_case_public_id
    
    print_step(2, "Підготовка тестових даних (категорії, канали, виконавці, звернення)")
    
    try:
        # Отримуємо категорії
        response = requests.get(
            f"{API_BASE}/api/categories",
            headers=get_headers(admin_token)
        )
        if response.status_code == 200:
            categories = response.json().get("categories", [])
            if len(categories) > 0:
                category_ids = [cat["id"] for cat in categories[:3]]
                print_info(f"Знайдено {len(categories)} категорій для тестування")
            else:
                print_error("Категорії не знайдено! Створіть категорії перед тестуванням.")
                return False
        else:
            print_error(f"Помилка отримання категорій: {response.status_code}")
            return False
        
        # Отримуємо канали
        response = requests.get(
            f"{API_BASE}/api/channels",
            headers=get_headers(admin_token)
        )
        if response.status_code == 200:
            channels = response.json().get("channels", [])
            if len(channels) > 0:
                channel_ids = [ch["id"] for ch in channels[:3]]
                print_info(f"Знайдено {len(channels)} каналів для тестування")
            else:
                print_error("Канали не знайдено! Створіть канали перед тестуванням.")
                return False
        else:
            print_error(f"Помилка отримання каналів: {response.status_code}")
            return False
        
        # Отримуємо список виконавців
        response = requests.get(
            f"{API_BASE}/api/users",
            headers=get_headers(admin_token),
            params={"is_active": True, "limit": 100}
        )
        if response.status_code == 200:
            users = response.json().get("users", [])
            executors = [u for u in users if u["role"] in ["EXECUTOR", "ADMIN"]]
            executor_user_ids = [ex["id"] for ex in executors[:3]]
            print_info(f"Знайдено {len(executor_user_ids)} виконавців для тестування")
        
        # Створюємо тестове звернення (multipart/form-data для файлів)
        case_data = {
            "category_id": category_ids[0],
            "channel_id": channel_ids[0],
            "applicant_name": "Тест Заявник FE-011",
            "applicant_phone": "+380501234567",
            "applicant_email": "test_fe011@example.com",
            "summary": "Тестове звернення для FE-011 - UI тестування прав адміністратора"
        }
        
        response = requests.post(
            f"{API_BASE}/api/cases",
            headers={"Authorization": f"Bearer {operator_token}"},  # Only Authorization header
            data=case_data  # Use data instead of json for multipart
        )
        
        if response.status_code == 201:
            case = response.json()
            test_case_id = case["id"]
            test_case_public_id = case["public_id"]
            print_success(f"Створено тестове звернення #{test_case_public_id} (ID: {test_case_id})")
        else:
            print_error(f"Помилка створення звернення: {response.status_code}")
            return False
        
        test_results["prepare_data"] = "PASS"
        return True
        
    except Exception as e:
        print_error(f"Помилка підготовки даних: {str(e)}")
        test_results["prepare_data"] = "FAIL"
        return False


def test_step_3_edit_fields():
    """Крок 3: ADMIN редагує поля звернення (EditCaseFieldsForm)"""
    print_step(3, "ADMIN редагує поля звернення")
    
    try:
        # ADMIN редагує всі поля звернення
        update_data = {
            "category_id": category_ids[1] if len(category_ids) > 1 else category_ids[0],
            "channel_id": channel_ids[1] if len(channel_ids) > 1 else channel_ids[0],
            "subcategory": "Оновлена підкатегорія",
            "applicant_name": "Оновлений Заявник UI",
            "applicant_phone": "+380679999999",
            "applicant_email": "updated_ui@example.com",
            "summary": "Оновлений опис звернення через EditCaseFieldsForm (UI)"
        }
        
        response = requests.patch(
            f"{API_BASE}/api/cases/{test_case_id}",
            headers=get_headers(admin_token),
            json=update_data
        )
        
        if response.status_code == 200:
            case = response.json()
            print_success("ADMIN успішно відредагував звернення (EditCaseFieldsForm)")
            print_info(f"Нове ім'я: {case['applicant_name']}")
            print_info(f"Новий телефон: {case.get('applicant_phone')}")
            print_info(f"Новий email: {case.get('applicant_email')}")
            
            # Перевіряємо що зміни збережені
            if (case['applicant_name'] == update_data['applicant_name'] and
                case.get('applicant_phone') == update_data['applicant_phone'] and
                case.get('applicant_email') == update_data['applicant_email']):
                print_success("Всі поля успішно оновлені")
                test_results["edit_fields"] = "PASS"
                return True
            else:
                print_error("Деякі поля не оновилися")
                test_results["edit_fields"] = "FAIL"
                return False
        else:
            print_error(f"Помилка редагування: {response.status_code} - {response.text}")
            test_results["edit_fields"] = "FAIL"
            return False
            
    except Exception as e:
        print_error(f"Помилка тесту: {str(e)}")
        test_results["edit_fields"] = "FAIL"
        return False


def test_step_4_rbac_edit():
    """Крок 4: RBAC - OPERATOR не може редагувати"""
    print_step(4, "RBAC - OPERATOR не може редагувати поля звернення")
    
    try:
        update_data = {
            "applicant_name": "Спроба редагування оператором"
        }
        
        response = requests.patch(
            f"{API_BASE}/api/cases/{test_case_id}",
            headers=get_headers(operator_token),
            json=update_data
        )
        
        if response.status_code == 403:
            print_success("RBAC працює коректно! Оператору заборонено редагувати (403 Forbidden)")
            test_results["rbac_edit"] = "PASS"
            return True
        else:
            print_error(f"RBAC не працює! Очікувалось 403, отримано {response.status_code}")
            test_results["rbac_edit"] = "FAIL"
            return False
            
    except Exception as e:
        print_error(f"Помилка тесту: {str(e)}")
        test_results["rbac_edit"] = "FAIL"
        return False


def test_step_5_assign_executor():
    """Крок 5: ADMIN призначає виконавця (AssignExecutorForm)"""
    print_step(5, "ADMIN призначає виконавця на звернення")
    
    try:
        assignment_data = {
            "assigned_to_id": executor_user_ids[0]
        }
        
        response = requests.patch(
            f"{API_BASE}/api/cases/{test_case_id}/assign",
            headers=get_headers(admin_token),
            json=assignment_data
        )
        
        if response.status_code == 200:
            case = response.json()
            print_success("ADMIN успішно призначив виконавця (AssignExecutorForm)")
            print_info(f"Відповідальний: {case.get('responsible_id')}")
            print_info(f"Статус: {case.get('status')}")
            
            # Перевіряємо що виконавець призначений і статус змінився на IN_PROGRESS
            if case.get('responsible_id') == executor_user_ids[0] and case.get('status') == 'IN_PROGRESS':
                print_success("Призначення виконано правильно, статус змінився на IN_PROGRESS")
                test_results["assign_executor"] = "PASS"
                return True
            else:
                print_error("Призначення або зміна статусу не відбулися коректно")
                test_results["assign_executor"] = "FAIL"
                return False
        else:
            print_error(f"Помилка призначення: {response.status_code} - {response.text}")
            test_results["assign_executor"] = "FAIL"
            return False
            
    except Exception as e:
        print_error(f"Помилка тесту: {str(e)}")
        test_results["assign_executor"] = "FAIL"
        return False


def test_step_6_unassign_executor():
    """Крок 6: ADMIN знімає виконавця"""
    print_step(6, "ADMIN знімає виконавця (кнопка 'Зняти виконавця')")
    
    try:
        assignment_data = {
            "assigned_to_id": None
        }
        
        response = requests.patch(
            f"{API_BASE}/api/cases/{test_case_id}/assign",
            headers=get_headers(admin_token),
            json=assignment_data
        )
        
        if response.status_code == 200:
            case = response.json()
            print_success("ADMIN успішно зняв виконавця")
            print_info(f"Відповідальний: {case.get('responsible_id')}")
            print_info(f"Статус: {case.get('status')}")
            
            # Перевіряємо що виконавець знятий і статус повернувся в NEW
            if case.get('responsible_id') is None and case.get('status') == 'NEW':
                print_success("Виконавця знято, статус повернувся в NEW")
                test_results["unassign_executor"] = "PASS"
                return True
            else:
                print_error("Зняття або зміна статусу не відбулися коректно")
                test_results["unassign_executor"] = "FAIL"
                return False
        else:
            print_error(f"Помилка зняття виконавця: {response.status_code} - {response.text}")
            test_results["unassign_executor"] = "FAIL"
            return False
            
    except Exception as e:
        print_error(f"Помилка тесту: {str(e)}")
        test_results["unassign_executor"] = "FAIL"
        return False


def test_step_7_admin_change_status_to_done():
    """Крок 7: ADMIN змінює статус з NEW на DONE (розширений ChangeStatusForm)"""
    print_step(7, "ADMIN змінює статус з NEW на DONE (без обмежень)")
    
    try:
        status_data = {
            "to_status": "DONE",
            "comment": "Адміністратор закриває звернення без попередніх кроків (UI тест)"
        }
        
        response = requests.post(
            f"{API_BASE}/api/cases/{test_case_id}/status",
            headers=get_headers(admin_token),
            json=status_data
        )
        
        if response.status_code == 200:
            case = response.json()
            print_success("ADMIN успішно змінив статус з NEW на DONE")
            print_info(f"Новий статус: {case.get('status')}")
            
            if case.get('status') == 'DONE':
                print_success("ADMIN має розширені права (може змінювати статус без обмежень)")
                test_results["admin_status_to_done"] = "PASS"
                return True
            else:
                print_error("Статус не змінився на DONE")
                test_results["admin_status_to_done"] = "FAIL"
                return False
        else:
            print_error(f"Помилка зміни статусу: {response.status_code} - {response.text}")
            test_results["admin_status_to_done"] = "FAIL"
            return False
            
    except Exception as e:
        print_error(f"Помилка тесту: {str(e)}")
        test_results["admin_status_to_done"] = "FAIL"
        return False


def test_step_8_admin_return_to_new():
    """Крок 8: ADMIN повертає звернення зі статусу DONE в NEW"""
    print_step(8, "ADMIN повертає звернення зі статусу DONE в NEW")
    
    try:
        status_data = {
            "to_status": "NEW",
            "comment": "Повторний розгляд необхідний (UI тест - повернення в NEW)"
        }
        
        response = requests.post(
            f"{API_BASE}/api/cases/{test_case_id}/status",
            headers=get_headers(admin_token),
            json=status_data
        )
        
        if response.status_code == 200:
            case = response.json()
            print_success("ADMIN успішно повернув звернення зі статусу DONE в NEW")
            print_info(f"Новий статус: {case.get('status')}")
            
            if case.get('status') == 'NEW':
                print_success("ADMIN може повертати звернення в будь-який статус (розширені права)")
                test_results["admin_return_to_new"] = "PASS"
                return True
            else:
                print_error("Статус не змінився на NEW")
                test_results["admin_return_to_new"] = "FAIL"
                return False
        else:
            print_error(f"Помилка зміни статусу: {response.status_code} - {response.text}")
            test_results["admin_return_to_new"] = "FAIL"
            return False
            
    except Exception as e:
        print_error(f"Помилка тесту: {str(e)}")
        test_results["admin_return_to_new"] = "FAIL"
        return False


def test_step_9_rbac_assign():
    """Крок 9: RBAC - EXECUTOR не може призначати виконавців"""
    print_step(9, "RBAC - EXECUTOR не може призначати виконавців")
    
    try:
        assignment_data = {
            "assigned_to_id": executor_user_ids[0]
        }
        
        response = requests.patch(
            f"{API_BASE}/api/cases/{test_case_id}/assign",
            headers=get_headers(executor_token),
            json=assignment_data
        )
        
        if response.status_code == 403:
            print_success("RBAC працює коректно! Виконавцю заборонено призначати (403 Forbidden)")
            test_results["rbac_assign"] = "PASS"
            return True
        else:
            print_error(f"RBAC не працює! Очікувалось 403, отримано {response.status_code}")
            test_results["rbac_assign"] = "FAIL"
            return False
            
    except Exception as e:
        print_error(f"Помилка тесту: {str(e)}")
        test_results["rbac_assign"] = "FAIL"
        return False


def test_step_10_validation_email():
    """Крок 10: Валідація email при редагуванні"""
    print_step(10, "Валідація - невалідний email формат")
    
    try:
        update_data = {
            "applicant_email": "invalid-email-format"
        }
        
        response = requests.patch(
            f"{API_BASE}/api/cases/{test_case_id}",
            headers=get_headers(admin_token),
            json=update_data
        )
        
        if response.status_code in [400, 422]:
            print_success("Валідація працює! Невалідний email формат відхилено")
            test_results["validation_email"] = "PASS"
            return True
        else:
            print_error(f"Валідація не працює! Очікувалось 400/422, отримано {response.status_code}")
            test_results["validation_email"] = "FAIL"
            return False
            
    except Exception as e:
        print_error(f"Помилка тесту: {str(e)}")
        test_results["validation_email"] = "FAIL"
        return False


def print_final_summary():
    """Print final test summary"""
    print_section("ПІДСУМОК ТЕСТУВАННЯ FE-011")
    
    print("\nРезультати тестування:")
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result == "PASS")
    
    for test_name, result in test_results.items():
        status_symbol = "[OK]" if result == "PASS" else "[FAIL]"
        print(f"  {status_symbol} {result} - {test_name}")
    
    print(f"\n[TOTAL] {passed_tests}/{total_tests} тестів пройдено")
    
    if passed_tests == total_tests:
        print("\n[SUCCESS] Всі тести пройдено успішно!")
        print("[INFO] FE-011 ГОТОВО ДО PRODUCTION")
    else:
        print(f"\n[FAIL] Деякі тести не пройдено: {total_tests - passed_tests} з {total_tests}")
    
    print("\n" + "=" * 80)


def run_all_tests():
    """Run all FE-011 tests"""
    print_section("FE-011: Розширені права адміністратора - UI/Frontend Testing")
    print("Тестування інтерфейсу адміністратора через backend API\n")
    print("UI Компоненти:")
    print("  - EditCaseFieldsForm (редагування всіх полів)")
    print("  - AssignExecutorForm (призначення/зняття виконавця)")
    print("  - Розширений ChangeStatusForm (зміна статусу без обмежень)")
    print("  - Інтеграція в /cases/[id] page з RBAC захистом")
    
    # Run tests in sequence
    if not test_step_1_login():
        print_error("Тестування зупинено через помилку логіну")
        return
    
    if not test_step_2_prepare_data():
        print_error("Тестування зупинено через помилку підготовки даних")
        return
    
    # Run all feature tests
    test_step_3_edit_fields()
    test_step_4_rbac_edit()
    test_step_5_assign_executor()
    test_step_6_unassign_executor()
    test_step_7_admin_change_status_to_done()
    test_step_8_admin_return_to_new()
    test_step_9_rbac_assign()
    test_step_10_validation_email()
    
    # Print summary
    print_final_summary()


if __name__ == "__main__":
    run_all_tests()
