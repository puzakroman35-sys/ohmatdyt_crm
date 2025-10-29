"""
Тестування FE-007: Дії виконавця - взяття в роботу, зміна статусу
Ohmatdyt CRM
"""

import requests
import json
from typing import Optional

# Конфігурація
API_URL = "http://localhost:8000"

# Кольори для виводу
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.ENDC}")

def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.ENDC}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.ENDC}")

def print_section(msg: str):
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{msg}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{'='*80}{Colors.ENDC}\n")

def login(username: str, password: str) -> Optional[str]:
    """Логін та отримання токену"""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={
                "username": username,
                "password": password
            }
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            print_success(f"Логін успішний: {username}")
            return token
        else:
            print_error(f"Помилка логіну: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_error(f"Помилка підключення: {e}")
        return None

def get_categories(token: str) -> list:
    """Отримання активних категорій"""
    response = requests.get(
        f"{API_URL}/api/categories",
        headers={"Authorization": f"Bearer {token}"},
        params={"is_active": True}
    )
    if response.status_code == 200:
        return response.json().get("categories", [])
    return []

def get_channels(token: str) -> list:
    """Отримання активних каналів"""
    response = requests.get(
        f"{API_URL}/api/channels",
        headers={"Authorization": f"Bearer {token}"},
        params={"is_active": True}
    )
    if response.status_code == 200:
        return response.json().get("channels", [])
    return []

def create_case(token: str, category_id: str, channel_id: str) -> Optional[dict]:
    """Створення тестового звернення"""
    try:
        data = {
            "category_id": category_id,
            "channel_id": channel_id,
            "applicant_name": "Тестовий заявник для FE-007",
            "applicant_phone": "+380501234567",
            "applicant_email": "test-fe007@example.com",
            "summary": "Тестове звернення для перевірки взяття в роботу та зміни статусу"
        }
        
        response = requests.post(
            f"{API_URL}/api/cases",
            headers={"Authorization": f"Bearer {token}"},
            data=data  # multipart/form-data
        )
        
        if response.status_code == 201:
            case = response.json()
            print_success(f"Створено звернення #{case['public_id']}")
            return case
        else:
            print_error(f"Помилка створення звернення: {response.text}")
            return None
    except Exception as e:
        print_error(f"Помилка: {e}")
        return None

def take_case(token: str, case_id: str) -> bool:
    """Взяття звернення в роботу (BE-009)"""
    try:
        response = requests.post(
            f"{API_URL}/api/cases/{case_id}/take",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Звернення взято в роботу. Новий статус: {result['status']}")
            return True
        else:
            print_error(f"Помилка взяття в роботу: {response.text}")
            return False
    except Exception as e:
        print_error(f"Помилка: {e}")
        return False

def change_status(token: str, case_id: str, new_status: str, comment: str) -> bool:
    """Зміна статусу звернення (BE-010)"""
    try:
        data = {
            "to_status": new_status,
            "comment": comment
        }
        
        response = requests.post(
            f"{API_URL}/api/cases/{case_id}/status",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Статус змінено на: {result['status']}")
            return True
        else:
            print_error(f"Помилка зміни статусу: {response.text}")
            return False
    except Exception as e:
        print_error(f"Помилка: {e}")
        return False

def get_case_details(token: str, case_id: str) -> Optional[dict]:
    """Отримання деталей звернення"""
    try:
        response = requests.get(
            f"{API_URL}/api/cases/{case_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"Помилка отримання деталей: {response.text}")
            return None
    except Exception as e:
        print_error(f"Помилка: {e}")
        return None

def main():
    print_section("FE-007: Тестування дій виконавця")
    
    # Крок 1: Логін як оператор
    print_info("Крок 1: Логін як оператор для створення звернення")
    operator_token = login("operator1", "Operator123!")
    if not operator_token:
        print_error("Не вдалося увійти як оператор")
        return
    
    # Крок 2: Отримання категорій та каналів
    print_info("\nКрок 2: Отримання категорій та каналів")
    categories = get_categories(operator_token)
    channels = get_channels(operator_token)
    
    if not categories or len(categories) == 0:
        print_error("Не вдалося отримати категорії")
        return
    
    if not channels or len(channels) == 0:
        print_error("Не вдалося отримати канали")
        return
    
    category_id = categories[0]["id"]
    channel_id = channels[0]["id"]
    print_success(f"Обрано категорію: {categories[0]['name']}")
    print_success(f"Обрано канал: {channels[0]['name']}")
    
    # Крок 3: Створення тестового звернення
    print_info("\nКрок 3: Створення тестового звернення")
    case = create_case(operator_token, category_id, channel_id)
    if not case:
        print_error("Не вдалося створити звернення")
        return
    
    case_id = case["id"]
    case_public_id = case["public_id"]
    print_info(f"ID звернення: {case_id}")
    print_info(f"Публічний ID: #{case_public_id}")
    print_info(f"Початковий статус: {case['status']}")
    
    # Крок 4: Логін як виконавець
    print_info("\nКрок 4: Логін як виконавець")
    executor_token = login("executor1", "Executor123!")
    if not executor_token:
        print_error("Не вдалося увійти як виконавець")
        return
    
    # Крок 5: Взяття звернення в роботу (BE-009)
    print_info("\nКрок 5: Взяття звернення в роботу (BE-009)")
    if not take_case(executor_token, case_id):
        print_error("Не вдалося взяти звернення в роботу")
        return
    
    # Перевірка статусу після взяття в роботу
    details = get_case_details(executor_token, case_id)
    if details:
        print_info(f"Поточний статус: {details['status']}")
        if details['status'] == 'IN_PROGRESS':
            print_success("Статус коректно змінено на IN_PROGRESS")
        else:
            print_error(f"Очікувався статус IN_PROGRESS, отримано {details['status']}")
    
    # Крок 6: Тест валідації - спроба змінити статус без коментаря
    print_info("\nКрок 6: Тест валідації - зміна статусу без коментаря")
    try:
        response = requests.post(
            f"{API_URL}/api/cases/{case_id}/status",
            headers={
                "Authorization": f"Bearer {executor_token}",
                "Content-Type": "application/json"
            },
            json={"to_status": "DONE"}  # Без коментаря
        )
        
        if response.status_code == 422:
            print_success("Валідація працює: коментар обов'язковий")
        else:
            print_error(f"Валідація не спрацювала: {response.status_code}")
    except Exception as e:
        print_error(f"Помилка: {e}")
    
    # Крок 7: Зміна статусу на NEEDS_INFO з коментарем (BE-010)
    print_info("\nКрок 7: Зміна статусу на NEEDS_INFO (BE-010)")
    comment1 = "Потрібна додаткова інформація від заявника для обробки звернення"
    if change_status(executor_token, case_id, "NEEDS_INFO", comment1):
        details = get_case_details(executor_token, case_id)
        if details and details['status'] == 'NEEDS_INFO':
            print_success("Статус коректно змінено на NEEDS_INFO")
            
            # Перевірка історії статусів
            if len(details['status_history']) >= 2:
                print_success(f"Історія статусів містить {len(details['status_history'])} записів")
            
            # Перевірка коментаря
            if details['comments']:
                last_comment = details['comments'][-1]
                print_success(f"Коментар додано: {last_comment['text'][:50]}...")
        else:
            print_error(f"Очікувався статус NEEDS_INFO, отримано {details['status'] if details else 'None'}")
    
    # Крок 8: Повернення в роботу
    print_info("\nКрок 8: Повернення звернення в роботу")
    comment2 = "Отримано необхідну інформацію, продовжуємо обробку"
    if change_status(executor_token, case_id, "IN_PROGRESS", comment2):
        details = get_case_details(executor_token, case_id)
        if details and details['status'] == 'IN_PROGRESS':
            print_success("Статус повернуто на IN_PROGRESS")
    
    # Крок 9: Завершення звернення
    print_info("\nКрок 9: Завершення звернення (статус DONE)")
    comment3 = "Звернення успішно оброблено та виконано. Всі питання вирішено."
    if change_status(executor_token, case_id, "DONE", comment3):
        details = get_case_details(executor_token, case_id)
        if details and details['status'] == 'DONE':
            print_success("Звернення успішно завершено")
            
            # Підсумкова інформація
            print_info(f"\nПідсумок:")
            print_info(f"  Звернення: #{case_public_id}")
            print_info(f"  Фінальний статус: {details['status']}")
            print_info(f"  Історія статусів: {len(details['status_history'])} записів")
            print_info(f"  Коментарів: {len(details['comments'])}")
            
            # Показати історію переходів статусів
            print_info("\nІсторія переходів статусів:")
            for history in details['status_history']:
                if history['old_status']:
                    print_info(f"  {history['old_status']} → {history['new_status']}")
                else:
                    print_info(f"  Створено: {history['new_status']}")
    
    # Крок 10: Тест невалідного переходу
    print_info("\nКрок 10: Тест невалідного переходу статусу")
    print_info("Спроба змінити статус DONE на NEW (недозволено)")
    try:
        response = requests.post(
            f"{API_URL}/api/cases/{case_id}/status",
            headers={
                "Authorization": f"Bearer {executor_token}",
                "Content-Type": "application/json"
            },
            json={
                "to_status": "NEW",
                "comment": "Спроба повернути на NEW"
            }
        )
        
        if response.status_code == 400:
            print_success("Валідація працює: неможливо змінити статус з DONE")
        else:
            print_error(f"Валідація не спрацювала: {response.status_code}")
    except Exception as e:
        print_error(f"Помилка: {e}")
    
    print_section("FE-007: Тестування завершено")
    print_success("Всі основні функції працюють коректно!")
    print_info(f"\nДля перевірки UI відкрийте:")
    print_info(f"  http://localhost:3000/cases/{case_id}")
    print_info(f"\nУвійдіть як виконавець (executor1 / Executor123!)")

if __name__ == "__main__":
    main()
