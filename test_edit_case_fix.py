#!/usr/bin/env python3
"""
Тест виправлення редагування звернень
Перевіряє, чи зберігаються зміни після редагування адміністратором
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"

def print_color(text, color):
    colors = {
        'cyan': '\033[96m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'white': '\033[97m',
        'gray': '\033[90m',
        'reset': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

def main():
    print_color("\n===== Тест виправлення редагування звернень =====", 'cyan')
    
    # 1. Авторізація ADMIN
    print_color("\n[1] Авторізація ADMIN...", 'yellow')
    login_response = requests.post(
        f"{API_URL}/auth/login",
        json={"username": "admin", "password": "Admin123!"}
    )
    
    if login_response.status_code != 200:
        print_color(f"✗ Помилка авторізації: {login_response.status_code}", 'red')
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print_color("✓ Авторизація успішна", 'green')
    
    # 2. Отримуємо список звернень
    print_color("\n[2] Отримання списку звернень...", 'yellow')
    cases_response = requests.get(
        f"{API_URL}/api/cases?limit=1",
        headers=headers
    )
    
    if cases_response.status_code != 200:
        print_color(f"✗ Помилка отримання звернень: {cases_response.status_code}", 'red')
        return False
    
    cases = cases_response.json()["cases"]
    if not cases:
        print_color("✗ Немає звернень для тестування", 'red')
        return False
    
    case_id = cases[0]["id"]
    case_public_id = cases[0]["public_id"]
    print_color(f"✓ Звернення отримано: #{case_public_id} (ID: {case_id})", 'green')
    
    # 3. Отримуємо детальну інформацію про звернення
    print_color("\n[3] Отримання деталей звернення...", 'yellow')
    before_response = requests.get(
        f"{API_URL}/api/cases/{case_id}",
        headers=headers
    )
    
    if before_response.status_code != 200:
        print_color(f"✗ Помилка отримання деталей: {before_response.status_code}", 'red')
        return False
    
    before_update = before_response.json()
    print_color("Поточні дані:", 'cyan')
    print_color(f"  Ім'я: {before_update['applicant_name']}", 'white')
    print_color(f"  Телефон: {before_update.get('applicant_phone', 'Не вказано')}", 'white')
    print_color(f"  Email: {before_update.get('applicant_email', 'Не вказано')}", 'white')
    summary_preview = before_update['summary'][:50] + "..." if len(before_update['summary']) > 50 else before_update['summary']
    print_color(f"  Опис: {summary_preview}", 'white')
    
    # 4. Редагуємо звернення
    print_color("\n[4] Редагування звернення...", 'yellow')
    timestamp = datetime.now().strftime("%H:%M:%S")
    update_data = {
        "applicant_name": f"Тестовий Користувач (Оновлено {timestamp})",
        "applicant_phone": "+380671234567",
        "applicant_email": "test_updated@example.com",
        "summary": f"Оновлений опис звернення - тест виправлення багу ({timestamp})"
    }
    
    print_color("Відправляємо оновлені дані:", 'cyan')
    print_color(json.dumps(update_data, indent=2, ensure_ascii=False), 'gray')
    
    update_response = requests.patch(
        f"{API_URL}/api/cases/{case_id}",
        json=update_data,
        headers={**headers, "Content-Type": "application/json"}
    )
    
    if update_response.status_code != 200:
        print_color(f"✗ Помилка при оновленні: {update_response.status_code}", 'red')
        print_color(f"Відповідь: {update_response.text}", 'red')
        return False
    
    print_color("✓ Запит на оновлення виконано успішно", 'green')
    
    # 5. Перевіряємо, чи збереглися зміни
    print_color("\n[5] Перевірка збережених змін...", 'yellow')
    import time
    time.sleep(1)
    
    after_response = requests.get(
        f"{API_URL}/api/cases/{case_id}",
        headers=headers
    )
    
    if after_response.status_code != 200:
        print_color(f"✗ Помилка отримання оновлених даних: {after_response.status_code}", 'red')
        return False
    
    after_update = after_response.json()
    print_color("Оновлені дані:", 'cyan')
    print_color(f"  Ім'я: {after_update['applicant_name']}", 'white')
    print_color(f"  Телефон: {after_update.get('applicant_phone', 'Не вказано')}", 'white')
    print_color(f"  Email: {after_update.get('applicant_email', 'Не вказано')}", 'white')
    summary_preview = after_update['summary'][:50] + "..." if len(after_update['summary']) > 50 else after_update['summary']
    print_color(f"  Опис: {summary_preview}", 'white')
    
    # 6. Порівнюємо значення
    print_color("\n[6] Перевірка результатів...", 'yellow')
    all_match = True
    
    if after_update['applicant_name'] != update_data['applicant_name']:
        print_color("✗ Ім'я не збереглося!", 'red')
        print_color(f"  Очікувалось: {update_data['applicant_name']}", 'gray')
        print_color(f"  Отримано: {after_update['applicant_name']}", 'gray')
        all_match = False
    else:
        print_color("✓ Ім'я збережено правильно", 'green')
    
    if after_update.get('applicant_phone') != update_data['applicant_phone']:
        print_color("✗ Телефон не зберігся!", 'red')
        print_color(f"  Очікувалось: {update_data['applicant_phone']}", 'gray')
        print_color(f"  Отримано: {after_update.get('applicant_phone')}", 'gray')
        all_match = False
    else:
        print_color("✓ Телефон збережено правильно", 'green')
    
    if after_update.get('applicant_email') != update_data['applicant_email']:
        print_color("✗ Email не зберігся!", 'red')
        print_color(f"  Очікувалось: {update_data['applicant_email']}", 'gray')
        print_color(f"  Отримано: {after_update.get('applicant_email')}", 'gray')
        all_match = False
    else:
        print_color("✓ Email збережено правильно", 'green')
    
    if after_update['summary'] != update_data['summary']:
        print_color("✗ Опис не зберігся!", 'red')
        print_color(f"  Очікувалось: {update_data['summary']}", 'gray')
        print_color(f"  Отримано: {after_update['summary']}", 'gray')
        all_match = False
    else:
        print_color("✓ Опис збережено правильно", 'green')
    
    # Підсумок
    print_color("\n===== ПІДСУМОК =====", 'cyan')
    if all_match:
        print_color("✓ ВСІ ЗМІНИ ЗБЕРЕГЛИСЯ ПРАВИЛЬНО!", 'green')
        return True
    else:
        print_color("✗ ДЕЯКІ ЗМІНИ НЕ ЗБЕРЕГЛИСЯ!", 'red')
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
