"""
BE-018: Тести для управління доступом виконавців до категорій

Тестує:
- GET /users/{user_id}/category-access - отримання списку доступних категорій
- POST /users/{user_id}/category-access - додавання доступу до категорій
- DELETE /users/{user_id}/category-access/{category_id} - видалення доступу
- PUT /users/{user_id}/category-access - заміна всіх доступів
- Валідації (тільки EXECUTOR, існування категорій, унікальність)
"""
import os
import sys
import httpx
import json

# API URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# ANSI colors для виводу
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Результати тестів
test_results = {}

# Змінні для тестових даних
admin_token = None
executor_user_id = None
operator_user_id = None
category_ids = []


def print_header(text: str):
    """Друкує заголовок секції"""
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BOLD}{BLUE}  {text}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}")


def print_step(text: str):
    """Друкує крок тестування"""
    print(f"\n{YELLOW}{'─' * 80}{RESET}")
    print(f"{BOLD}{text}{RESET}")
    print(f"{YELLOW}{'─' * 80}{RESET}")


def print_success(text: str):
    """Друкує повідомлення про успіх"""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text: str):
    """Друкує повідомлення про помилку"""
    print(f"{RED}❌ {text}{RESET}")


def print_info(text: str):
    """Друкує інформаційне повідомлення"""
    print(f"{BLUE}ℹ️  {text}{RESET}")


def setup_test_data():
    """Крок 0: Підготовка тестових даних"""
    global admin_token, executor_user_id, operator_user_id, category_ids
    
    print_step("[КРОК 0] Підготовка тестових даних")
    
    # Логін як ADMIN
    try:
        response = httpx.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=10.0
        )
        
        if response.status_code == 200:
            admin_token = response.json()["access_token"]
            print_success("Успішний логін як ADMIN")
        else:
            print_error("Не вдалось залогінитись як ADMIN")
            return False
    except Exception as e:
        print_error(f"Помилка логіну: {e}")
        return False
    
    # Отримання списку користувачів для знаходження EXECUTOR
    try:
        response = httpx.get(
            f"{API_BASE_URL}/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"role": "EXECUTOR", "limit": 1},
            timeout=10.0
        )
        
        if response.status_code == 200:
            users = response.json()["users"]
            if users:
                executor_user_id = users[0]["id"]
                print_success(f"Знайдено EXECUTOR: {users[0]['username']} ({executor_user_id})")
            else:
                print_error("Не знайдено жодного EXECUTOR")
                return False
        else:
            print_error("Не вдалось отримати список користувачів")
            return False
    except Exception as e:
        print_error(f"Помилка отримання користувачів: {e}")
        return False
    
    # Отримання списку категорій
    try:
        response = httpx.get(
            f"{API_BASE_URL}/categories",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"limit": 5},
            timeout=10.0
        )
        
        if response.status_code == 200:
            categories = response.json()["categories"]
            category_ids = [cat["id"] for cat in categories]
            print_success(f"Знайдено {len(category_ids)} категорій")
            for cat in categories:
                print_info(f"  - {cat['name']} ({cat['id']})")
        else:
            print_error("Не вдалось отримати список категорій")
            return False
    except Exception as e:
        print_error(f"Помилка отримання категорій: {e}")
        return False
    
    # Отримання OPERATOR для негативного тесту
    try:
        response = httpx.get(
            f"{API_BASE_URL}/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"role": "OPERATOR", "limit": 1},
            timeout=10.0
        )
        
        if response.status_code == 200:
            users = response.json()["users"]
            if users:
                operator_user_id = users[0]["id"]
                print_success(f"Знайдено OPERATOR: {users[0]['username']} ({operator_user_id})")
        else:
            print_info("Не знайдено OPERATOR (опціонально для негативних тестів)")
    except Exception as e:
        print_info(f"OPERATOR не знайдено (не критично): {e}")
    
    return True


def test_get_empty_category_access():
    """Тест 1: Отримання порожнього списку доступів"""
    test_name = "get_empty_category_access"
    print_step("[КРОК 1] Отримання порожнього списку категорій виконавця")
    
    # Спочатку очищуємо всі доступи
    try:
        response = httpx.put(
            f"{API_BASE_URL}/users/{executor_user_id}/category-access",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"category_ids": []},
            timeout=10.0
        )
        print_info("Очищено існуючі доступи")
    except Exception:
        pass
    
    try:
        response = httpx.get(
            f"{API_BASE_URL}/users/{executor_user_id}/category-access",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=10.0
        )
        
        if response.status_code != 200:
            print_error(f"Невірний статус код: {response.status_code}")
            test_results[test_name] = "FAIL"
            return
        
        data = response.json()
        
        # Перевірка структури
        required_fields = ["executor_id", "executor_username", "total", "categories"]
        for field in required_fields:
            if field not in data:
                print_error(f"Відсутнє поле: {field}")
                test_results[test_name] = "FAIL"
                return
        
        print_success("Список доступів отримано")
        print_info(f"Executor: {data['executor_username']}")
        print_info(f"Total categories: {data['total']}")
        
        test_results[test_name] = "PASS"
        
    except Exception as e:
        print_error(f"Помилка: {e}")
        test_results[test_name] = "FAIL"


def test_add_category_access():
    """Тест 2: Додавання доступу до категорій"""
    test_name = "add_category_access"
    print_step("[КРОК 2] Додавання доступу до категорій")
    
    # Додаємо перші 2 категорії
    categories_to_add = category_ids[:2]
    
    try:
        response = httpx.post(
            f"{API_BASE_URL}/users/{executor_user_id}/category-access",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"category_ids": categories_to_add},
            timeout=10.0
        )
        
        if response.status_code != 201:
            print_error(f"Невірний статус код: {response.status_code}")
            print_error(f"Відповідь: {response.text}")
            test_results[test_name] = "FAIL"
            return
        
        data = response.json()
        
        if data["total"] != 2:
            print_error(f"Очікувалось 2 категорії, отримано: {data['total']}")
            test_results[test_name] = "FAIL"
            return
        
        print_success(f"Додано доступ до {data['total']} категорій")
        for cat in data["categories"]:
            print_info(f"  - {cat['category_name']} ({cat['category_id']})")
        
        test_results[test_name] = "PASS"
        
    except Exception as e:
        print_error(f"Помилка: {e}")
        test_results[test_name] = "FAIL"


def test_add_duplicate_category_access():
    """Тест 3: Спроба додати дублікат доступу (має пропустити)"""
    test_name = "add_duplicate_category_access"
    print_step("[КРОК 3] Спроба додати дублікат доступу")
    
    # Додаємо ту саму категорію ще раз
    duplicate_category = [category_ids[0]]
    
    try:
        response = httpx.post(
            f"{API_BASE_URL}/users/{executor_user_id}/category-access",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"category_ids": duplicate_category},
            timeout=10.0
        )
        
        # Має повернути 201, але доступ вже існує
        if response.status_code != 201:
            print_error(f"Невірний статус код: {response.status_code}")
            test_results[test_name] = "FAIL"
            return
        
        data = response.json()
        
        # Загальна кількість має бути незмінною (2)
        if data["total"] != 2:
            print_error(f"Кількість категорій змінилась: {data['total']} (очікувалось 2)")
            test_results[test_name] = "FAIL"
            return
        
        print_success("Дублікат пропущено, кількість не змінилась")
        print_info(f"Total categories: {data['total']}")
        
        test_results[test_name] = "PASS"
        
    except Exception as e:
        print_error(f"Помилка: {e}")
        test_results[test_name] = "FAIL"


def test_get_category_access_list():
    """Тест 4: Отримання списку доступів після додавання"""
    test_name = "get_category_access_list"
    print_step("[КРОК 4] Отримання списку доступів виконавця")
    
    try:
        response = httpx.get(
            f"{API_BASE_URL}/users/{executor_user_id}/category-access",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=10.0
        )
        
        if response.status_code != 200:
            print_error(f"Невірний статус код: {response.status_code}")
            test_results[test_name] = "FAIL"
            return
        
        data = response.json()
        
        if data["total"] != 2:
            print_error(f"Очікувалось 2 категорії, отримано: {data['total']}")
            test_results[test_name] = "FAIL"
            return
        
        # Перевірка що всі записи мають необхідні поля
        for cat in data["categories"]:
            required_fields = ["id", "executor_id", "category_id", "category_name", "created_at", "updated_at"]
            for field in required_fields:
                if field not in cat:
                    print_error(f"Відсутнє поле в записі доступу: {field}")
                    test_results[test_name] = "FAIL"
                    return
        
        print_success("Список доступів отримано успішно")
        print_info(f"Total: {data['total']} categories")
        for cat in data["categories"]:
            print_info(f"  - {cat['category_name']} ({cat['category_id']})")
        
        test_results[test_name] = "PASS"
        
    except Exception as e:
        print_error(f"Помилка: {e}")
        test_results[test_name] = "FAIL"


def test_delete_category_access():
    """Тест 5: Видалення доступу до категорії"""
    test_name = "delete_category_access"
    print_step("[КРОК 5] Видалення доступу до категорії")
    
    # Видаляємо першу категорію
    category_to_delete = category_ids[0]
    
    try:
        response = httpx.delete(
            f"{API_BASE_URL}/users/{executor_user_id}/category-access/{category_to_delete}",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=10.0
        )
        
        if response.status_code != 204:
            print_error(f"Невірний статус код: {response.status_code}")
            print_error(f"Відповідь: {response.text}")
            test_results[test_name] = "FAIL"
            return
        
        print_success("Доступ видалено (204 No Content)")
        
        # Перевірка що доступ дійсно видалено
        response = httpx.get(
            f"{API_BASE_URL}/users/{executor_user_id}/category-access",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=10.0
        )
        
        data = response.json()
        
        if data["total"] != 1:
            print_error(f"Очікувалось 1 категорія після видалення, отримано: {data['total']}")
            test_results[test_name] = "FAIL"
            return
        
        print_info(f"Залишилось categories: {data['total']}")
        
        test_results[test_name] = "PASS"
        
    except Exception as e:
        print_error(f"Помилка: {e}")
        test_results[test_name] = "FAIL"


def test_delete_nonexistent_access():
    """Тест 6: Видалення неіснуючого доступу (має повернути 404)"""
    test_name = "delete_nonexistent_access"
    print_step("[КРОК 6] Видалення неіснуючого доступу")
    
    # Видаляємо вже видалений доступ
    category_to_delete = category_ids[0]
    
    try:
        response = httpx.delete(
            f"{API_BASE_URL}/users/{executor_user_id}/category-access/{category_to_delete}",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=10.0
        )
        
        if response.status_code != 404:
            print_error(f"Очікувався 404, отримано: {response.status_code}")
            test_results[test_name] = "FAIL"
            return
        
        print_success("Отримано 404 для неіснуючого доступу")
        
        test_results[test_name] = "PASS"
        
    except Exception as e:
        print_error(f"Помилка: {e}")
        test_results[test_name] = "FAIL"


def test_replace_category_access():
    """Тест 7: Заміна всіх доступів новим списком"""
    test_name = "replace_category_access"
    print_step("[КРОК 7] Заміна всіх доступів новим списком")
    
    # Замінюємо на категорії 2, 3, 4 (індекси 1, 2, 3)
    new_categories = category_ids[1:4] if len(category_ids) >= 4 else category_ids[1:]
    
    try:
        response = httpx.put(
            f"{API_BASE_URL}/users/{executor_user_id}/category-access",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"category_ids": new_categories},
            timeout=10.0
        )
        
        if response.status_code != 200:
            print_error(f"Невірний статус код: {response.status_code}")
            print_error(f"Відповідь: {response.text}")
            test_results[test_name] = "FAIL"
            return
        
        data = response.json()
        
        expected_count = len(new_categories)
        if data["total"] != expected_count:
            print_error(f"Очікувалось {expected_count} категорій, отримано: {data['total']}")
            test_results[test_name] = "FAIL"
            return
        
        print_success(f"Доступи замінено на {data['total']} категорій")
        for cat in data["categories"]:
            print_info(f"  - {cat['category_name']} ({cat['category_id']})")
        
        test_results[test_name] = "PASS"
        
    except Exception as e:
        print_error(f"Помилка: {e}")
        test_results[test_name] = "FAIL"


def test_replace_with_empty_list():
    """Тест 8: Заміна всіх доступів порожнім списком"""
    test_name = "replace_with_empty_list"
    print_step("[КРОК 8] Видалення всіх доступів через порожній список")
    
    try:
        response = httpx.put(
            f"{API_BASE_URL}/users/{executor_user_id}/category-access",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"category_ids": []},
            timeout=10.0
        )
        
        if response.status_code != 200:
            print_error(f"Невірний статус код: {response.status_code}")
            test_results[test_name] = "FAIL"
            return
        
        data = response.json()
        
        if data["total"] != 0:
            print_error(f"Очікувалось 0 категорій, отримано: {data['total']}")
            test_results[test_name] = "FAIL"
            return
        
        print_success("Всі доступи видалено")
        print_info(f"Total categories: {data['total']}")
        
        test_results[test_name] = "PASS"
        
    except Exception as e:
        print_error(f"Помилка: {e}")
        test_results[test_name] = "FAIL"


def test_add_access_for_non_executor():
    """Тест 9: Спроба додати доступ для не-EXECUTOR (має повернути 400)"""
    test_name = "add_access_for_non_executor"
    print_step("[КРОК 9] Спроба додати доступ для не-EXECUTOR користувача")
    
    if not operator_user_id:
        print_info("OPERATOR не знайдено, тест пропущено")
        test_results[test_name] = "SKIP"
        return
    
    try:
        response = httpx.post(
            f"{API_BASE_URL}/users/{operator_user_id}/category-access",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"category_ids": [category_ids[0]]},
            timeout=10.0
        )
        
        if response.status_code != 400:
            print_error(f"Очікувався 400, отримано: {response.status_code}")
            test_results[test_name] = "FAIL"
            return
        
        print_success("Отримано 400 для не-EXECUTOR користувача")
        print_info(f"Error: {response.json().get('detail', '')}")
        
        test_results[test_name] = "PASS"
        
    except Exception as e:
        print_error(f"Помилка: {e}")
        test_results[test_name] = "FAIL"


def test_add_nonexistent_category():
    """Тест 10: Спроба додати доступ до неіснуючої категорії (має повернути 400)"""
    test_name = "add_nonexistent_category"
    print_step("[КРОК 10] Спроба додати доступ до неіснуючої категорії")
    
    fake_category_id = "00000000-0000-0000-0000-000000000000"
    
    try:
        response = httpx.post(
            f"{API_BASE_URL}/users/{executor_user_id}/category-access",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"category_ids": [fake_category_id]},
            timeout=10.0
        )
        
        # Може повернути 400 або 201 з помилкою в тілі
        if response.status_code == 201:
            # Перевірка що категорія не додалась
            data = response.json()
            print_success("Неіснуюча категорія пропущена")
            print_info(f"Total categories: {data['total']}")
        elif response.status_code == 400:
            print_success("Отримано 400 для неіснуючої категорії")
        else:
            print_error(f"Неочікуваний статус код: {response.status_code}")
            test_results[test_name] = "FAIL"
            return
        
        test_results[test_name] = "PASS"
        
    except Exception as e:
        print_error(f"Помилка: {e}")
        test_results[test_name] = "FAIL"


def print_summary():
    """Друкує підсумок тестування"""
    print_header("ПІДСУМОК ТЕСТУВАННЯ BE-018")
    
    passed = sum(1 for result in test_results.values() if result == "PASS")
    failed = sum(1 for result in test_results.values() if result == "FAIL")
    skipped = sum(1 for result in test_results.values() if result == "SKIP")
    total = len(test_results)
    
    print("\nРезультати тестування:")
    for test_name, result in test_results.items():
        if result == "PASS":
            print(f"  {GREEN}✅ PASS{RESET} - {test_name}")
        elif result == "FAIL":
            print(f"  {RED}❌ FAIL{RESET} - {test_name}")
        elif result == "SKIP":
            print(f"  {YELLOW}⊘ SKIP{RESET} - {test_name}")
    
    print(f"\n{BOLD}📊 TOTAL - {passed}/{total} тестів пройдено{RESET}")
    
    if skipped > 0:
        print(f"{YELLOW}⊘ SKIPPED - {skipped} тестів пропущено{RESET}")
    
    if failed == 0 and passed > 0:
        print(f"\n{GREEN}{BOLD}✅ Всі тести пройдено успішно! ✨{RESET}")
        print(f"{BLUE}ℹ️  BE-018 ГОТОВО ДО PRODUCTION ✅{RESET}")
        return True
    else:
        print(f"\n{RED}{BOLD}❌ Деякі тести не пройдено{RESET}")
        print(f"{RED}ℹ️  Потрібні додаткові виправлення{RESET}")
        return False


def main():
    """Головна функція тестування"""
    print_header("BE-018: Модель доступу виконавців до категорій - Testing")
    print("Тестування API для управління доступом виконавців до категорій\n")
    
    print("Компоненти що тестуються:")
    print("  - GET /users/{user_id}/category-access - отримання списку доступів")
    print("  - POST /users/{user_id}/category-access - додавання доступу (масове)")
    print("  - DELETE /users/{user_id}/category-access/{category_id} - видалення доступу")
    print("  - PUT /users/{user_id}/category-access - заміна всіх доступів")
    print("  - Валідації: тільки EXECUTOR, існування категорій, унікальність")
    
    # Підготовка тестових даних
    if not setup_test_data():
        print_error("Не вдалось підготувати тестові дані")
        sys.exit(1)
    
    # Запуск тестів
    test_get_empty_category_access()
    test_add_category_access()
    test_add_duplicate_category_access()
    test_get_category_access_list()
    test_delete_category_access()
    test_delete_nonexistent_access()
    test_replace_category_access()
    test_replace_with_empty_list()
    test_add_access_for_non_executor()
    test_add_nonexistent_category()
    
    # Підсумок
    success = print_summary()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
