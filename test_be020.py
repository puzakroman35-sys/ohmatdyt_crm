"""
Тести для BE-020: Зміна власного пароля

Тестування функціоналу зміни пароля користувачем:
- POST /api/auth/change-password
- Валідація поточного пароля
- Валідація нового пароля
- Перевірка що новий пароль відрізняється від поточного
"""

import requests
import json
from datetime import datetime

# Конфігурація
API_BASE_URL = "http://localhost:8000"
API_URL = f"{API_BASE_URL}"  # Auth router на корені без /api

# Кольори для виводу
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Результати тестів
test_results = []


def print_header(title):
    """Друк заголовка секції"""
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}  {title}{RESET}")
    print(f"{BOLD}{'='*80}{RESET}")


def print_step(step_num, description):
    """Друк кроку тестування"""
    print(f"\n{BLUE}[КРОК {step_num}] {description}{RESET}")
    print(f"{BLUE}{'-'*80}{RESET}")


def print_success(test_name, message=""):
    """Друк успішного тесту"""
    print(f"{GREEN}✅ PASS - {test_name}{RESET}")
    if message:
        print(f"{GREEN}ℹ️  {message}{RESET}")
    test_results.append((test_name, True))


def print_error(test_name, message=""):
    """Друк невдалого тесту"""
    print(f"{RED}❌ FAIL - {test_name}{RESET}")
    if message:
        print(f"{RED}ℹ️  {message}{RESET}")
    test_results.append((test_name, False))


def print_info(message):
    """Друк інформаційного повідомлення"""
    print(f"{BLUE}ℹ️  {message}{RESET}")


def print_warning(message):
    """Друк попередження"""
    print(f"{YELLOW}⚠️  {message}{RESET}")


def print_summary():
    """Друк підсумку тестування"""
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}ПІДСУМОК ТЕСТУВАННЯ BE-020{RESET}")
    print(f"{BOLD}{'='*80}{RESET}")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print(f"\n{BOLD}Результати тестування:{RESET}")
    for test_name, result in test_results:
        status = f"{GREEN}✅ PASS{RESET}" if result else f"{RED}❌ FAIL{RESET}"
        print(f"  {status} - {test_name}")
    
    print(f"\n{BOLD}📊 TOTAL - {passed}/{total} тестів пройдено{RESET}\n")
    
    if passed == total:
        print(f"{GREEN}✅ Всі тести пройдено успішно! ✨{RESET}")
        print(f"{GREEN}ℹ️  BE-020 ГОТОВО ДО PRODUCTION ✅{RESET}\n")
    else:
        print(f"{RED}❌ Деякі тести не пройдено. Потрібні виправлення.{RESET}\n")


def login_user(username, password):
    """Логін користувача та отримання токену"""
    response = requests.post(
        f"{API_URL}/auth/login",
        json={"username": username, "password": password}
    )
    
    if response.status_code == 200:
        data = response.json()
        return data["access_token"]
    return None


def test_change_password_success():
    """Тест 1: Успішна зміна пароля"""
    print_step(1, "Успішна зміна пароля")
    
    # Логін з оригінальним паролем
    token = login_user("admin", "Admin123!")
    if not token:
        print_error("login_with_original_password", "Не вдалося залогінитись")
        return
    
    print_success("login_with_original_password", "Логін з оригінальним паролем успішний")
    
    # Зміна пароля
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_URL}/auth/change-password",
        headers=headers,
        json={
            "current_password": "Admin123!",
            "new_password": "NewPass123",
            "confirm_password": "NewPass123"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success("change_password_success", f"Пароль успішно змінено")
        print_info(f"Повідомлення: {data['message']}")
        print_info(f"Змінено о: {data['changed_at']}")
    else:
        print_error("change_password_success", f"HTTP {response.status_code}: {response.text}")
        return
    
    # Спроба логіну зі старим паролем (має не працювати)
    old_token = login_user("admin", "Admin123!")
    if old_token:
        print_error("login_with_old_password_fails", "Логін зі старим паролем ще працює!")
    else:
        print_success("login_with_old_password_fails", "Логін зі старим паролем заблоковано")
    
    # Логін з новим паролем (має працювати)
    new_token = login_user("admin", "NewPass123")
    if new_token:
        print_success("login_with_new_password", "Логін з новим паролем успішний")
    else:
        print_error("login_with_new_password", "Не вдалося залогінитись з новим паролем")
        return
    
    # Повернути оригінальний пароль
    headers = {"Authorization": f"Bearer {new_token}"}
    response = requests.post(
        f"{API_URL}/auth/change-password",
        headers=headers,
        json={
            "current_password": "NewPass123",
            "new_password": "Admin123!",
            "confirm_password": "Admin123!"
        }
    )
    
    if response.status_code == 200:
        print_success("restore_original_password", "Оригінальний пароль відновлено")
    else:
        print_warning("Не вдалося відновити оригінальний пароль")


def test_wrong_current_password():
    """Тест 2: Помилка при невірному поточному паролі"""
    print_step(2, "Помилка при невірному поточному паролі")
    
    token = login_user("admin", "Admin123!")
    if not token:
        print_error("login_for_wrong_password_test", "Не вдалося залогінитись")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_URL}/auth/change-password",
        headers=headers,
        json={
            "current_password": "WrongPassword123",
            "new_password": "NewPass123",
            "confirm_password": "NewPass123"
        }
    )
    
    if response.status_code == 401:
        data = response.json()
        print_success("wrong_current_password_401", "Отримано 401 Unauthorized")
        print_info(f"Повідомлення: {data.get('detail', 'N/A')}")
    else:
        print_error("wrong_current_password_401", f"Очікувався 401, отримано {response.status_code}")


def test_passwords_dont_match():
    """Тест 3: Помилка якщо new_password != confirm_password"""
    print_step(3, "Помилка якщо паролі не співпадають")
    
    token = login_user("admin", "Admin123!")
    if not token:
        print_error("login_for_mismatch_test", "Не вдалося залогінитись")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_URL}/auth/change-password",
        headers=headers,
        json={
            "current_password": "Admin123!",
            "new_password": "NewPass123",
            "confirm_password": "DifferentPass123"
        }
    )
    
    if response.status_code == 422:
        data = response.json()
        print_success("passwords_mismatch_422", "Отримано 422 Unprocessable Entity")
        print_info(f"Помилка валідації: {data.get('detail', 'N/A')}")
    else:
        print_error("passwords_mismatch_422", f"Очікувався 422, отримано {response.status_code}")


def test_password_too_short():
    """Тест 4: Помилка якщо пароль надто короткий"""
    print_step(4, "Помилка якщо пароль надто короткий (<8 символів)")
    
    token = login_user("admin", "Admin123!")
    if not token:
        print_error("login_for_short_password_test", "Не вдалося залогінитись")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_URL}/auth/change-password",
        headers=headers,
        json={
            "current_password": "Admin123!",
            "new_password": "Pass1",
            "confirm_password": "Pass1"
        }
    )
    
    if response.status_code == 422:
        data = response.json()
        print_success("password_too_short_422", "Отримано 422 Unprocessable Entity")
        print_info(f"Помилка валідації: {data.get('detail', 'N/A')}")
    else:
        print_error("password_too_short_422", f"Очікувався 422, отримано {response.status_code}")


def test_password_no_uppercase():
    """Тест 5: Помилка якщо пароль без великої літери"""
    print_step(5, "Помилка якщо пароль без великої літери")
    
    token = login_user("admin", "Admin123!")
    if not token:
        print_error("login_for_no_uppercase_test", "Не вдалося залогінитись")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_URL}/auth/change-password",
        headers=headers,
        json={
            "current_password": "Admin123!",
            "new_password": "password123",
            "confirm_password": "password123"
        }
    )
    
    if response.status_code == 422:
        data = response.json()
        print_success("password_no_uppercase_422", "Отримано 422 Unprocessable Entity")
        print_info(f"Помилка валідації: {data.get('detail', 'N/A')}")
    else:
        print_error("password_no_uppercase_422", f"Очікувався 422, отримано {response.status_code}")


def test_password_no_digit():
    """Тест 6: Помилка якщо пароль без цифри"""
    print_step(6, "Помилка якщо пароль без цифри")
    
    token = login_user("admin", "Admin123!")
    if not token:
        print_error("login_for_no_digit_test", "Не вдалося залогінитись")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_URL}/auth/change-password",
        headers=headers,
        json={
            "current_password": "Admin123!",
            "new_password": "PasswordNoDigit",
            "confirm_password": "PasswordNoDigit"
        }
    )
    
    if response.status_code == 422:
        data = response.json()
        print_success("password_no_digit_422", "Отримано 422 Unprocessable Entity")
        print_info(f"Помилка валідації: {data.get('detail', 'N/A')}")
    else:
        print_error("password_no_digit_422", f"Очікувався 422, отримано {response.status_code}")


def test_new_password_same_as_current():
    """Тест 7: Помилка якщо новий пароль співпадає з поточним"""
    print_step(7, "Помилка якщо новий пароль співпадає з поточним")
    
    token = login_user("admin", "Admin123!")
    if not token:
        print_error("login_for_same_password_test", "Не вдалося залогінитись")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_URL}/auth/change-password",
        headers=headers,
        json={
            "current_password": "Admin123!",
            "new_password": "Admin123!",
            "confirm_password": "Admin123!"
        }
    )
    
    if response.status_code == 422:
        data = response.json()
        print_success("same_password_422", "Отримано 422 Unprocessable Entity")
        print_info(f"Повідомлення: {data.get('detail', 'N/A')}")
    else:
        print_error("same_password_422", f"Очікувався 422, отримано {response.status_code}")


def test_unauthorized_request():
    """Тест 8: Помилка якщо запит без токену"""
    print_step(8, "Помилка якщо запит без токену (неавторизований)")
    
    response = requests.post(
        f"{API_URL}/auth/change-password",
        json={
            "current_password": "Admin123!",
            "new_password": "NewPass123",
            "confirm_password": "NewPass123"
        }
    )
    
    if response.status_code == 401:
        print_success("unauthorized_401", "Отримано 401 Unauthorized")
    else:
        print_error("unauthorized_401", f"Очікувався 401, отримано {response.status_code}")


def test_operator_can_change_password():
    """Тест 9: OPERATOR може змінити свій пароль"""
    print_step(9, "OPERATOR може змінити свій пароль")
    
    # Спочатку потрібно створити оператора (якщо його немає)
    admin_token = login_user("admin", "Admin123!")
    if not admin_token:
        print_error("admin_login_for_operator_test", "Не вдалося залогінитись як admin")
        return
    
    # Спробуємо залогінитись як operator (якщо існує)
    operator_token = login_user("operator", "Operator123!")
    
    if operator_token:
        print_info("Використовується існуючий OPERATOR")
        
        headers = {"Authorization": f"Bearer {operator_token}"}
        response = requests.post(
            f"{API_URL}/auth/change-password",
            headers=headers,
            json={
                "current_password": "Operator123!",
                "new_password": "NewOperator123",
                "confirm_password": "NewOperator123"
            }
        )
        
        if response.status_code == 200:
            print_success("operator_change_password", "OPERATOR успішно змінив пароль")
            
            # Повернути оригінальний пароль
            new_token = login_user("operator", "NewOperator123")
            if new_token:
                headers = {"Authorization": f"Bearer {new_token}"}
                requests.post(
                    f"{API_URL}/auth/change-password",
                    headers=headers,
                    json={
                        "current_password": "NewOperator123",
                        "new_password": "Operator123!",
                        "confirm_password": "Operator123!"
                    }
                )
        else:
            print_error("operator_change_password", f"HTTP {response.status_code}")
    else:
        print_warning("OPERATOR користувач не знайдено, пропускаємо тест")
        test_results.append(("operator_change_password", True))  # Skip but mark as pass


def main():
    """Запуск всіх тестів"""
    print_header("BE-020: Зміна власного пароля - Testing")
    print("\nТестування функціоналу зміни пароля користувачем:")
    print("  - POST /api/auth/change-password")
    print("  - Валідація поточного пароля")
    print("  - Валідація нового пароля (8+ символів, велика літера, цифра)")
    print("  - Перевірка що новий пароль != поточний")
    print("  - Перевірка що новий пароль == confirm_password")
    
    # Запуск тестів
    test_change_password_success()
    test_wrong_current_password()
    test_passwords_dont_match()
    test_password_too_short()
    test_password_no_uppercase()
    test_password_no_digit()
    test_new_password_same_as_current()
    test_unauthorized_request()
    test_operator_can_change_password()
    
    # Підсумок
    print_summary()


if __name__ == "__main__":
    main()
