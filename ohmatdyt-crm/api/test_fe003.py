"""
Test FE-003: Create Case Form
Тест форми створення звернення з завантаженням файлів
"""

import requests
import json
from io import BytesIO

# API URL
API_URL = "http://localhost:8000"

def test_fe003_create_case_with_files():
    """
    Тест створення звернення через API з файлами
    """
    
    print("=" * 60)
    print("FE-003: Тест створення звернення з файлами")
    print("=" * 60)
    
    # 1. Логін як operator (тільки оператор може створювати звернення)
    print("\n1. Логін як operator...")
    login_response = requests.post(
        f"{API_URL}/auth/login",
        json={"username": "operator1", "password": "Operator123!"},
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Помилка логіну: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    print("✅ Логін успішний")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Отримання списку категорій (доступно всім авторизованим)
    print("\n2. Отримання категорій...")
    categories_response = requests.get(f"{API_URL}/api/categories", headers=headers)
    
    if categories_response.status_code != 200:
        print(f"❌ Помилка отримання категорій: {categories_response.status_code}")
        return
    
    categories_data = categories_response.json()
    categories = categories_data.get('categories', [])
    active_categories = [c for c in categories if c.get('is_active', False)]
    
    if not active_categories:
        print("❌ Немає активних категорій")
        return
    
    category_id = active_categories[0]['id']
    print(f"✅ Знайдено категорію: {active_categories[0]['name']} (ID: {category_id})")
    
    # 3. Отримання списку каналів
    print("\n3. Отримання каналів...")
    channels_response = requests.get(f"{API_URL}/api/channels", headers=headers)
    
    if channels_response.status_code != 200:
        print(f"❌ Помилка отримання каналів: {channels_response.status_code}")
        return
    
    channels_data = channels_response.json()
    channels = channels_data.get('channels', [])
    active_channels = [c for c in channels if c.get('is_active', False)]
    
    if not active_channels:
        print("❌ Немає активних каналів")
        return
    
    channel_id = active_channels[0]['id']
    print(f"✅ Знайдено канал: {active_channels[0]['name']} (ID: {channel_id})")
    
    # 4. Створення звернення БЕЗ файлів
    print("\n4. Створення звернення без файлів...")
    
    case_data = {
        'category_id': category_id,
        'channel_id': channel_id,
        'applicant_name': 'Тестовий Заявник Іванович',
        'applicant_phone': '+380501234567',
        'applicant_email': 'test@example.com',
        'subcategory': 'Тестова підкатегорія',
        'summary': 'Тестове звернення для перевірки функціональності FE-003. Це детальний опис проблеми.'
    }
    
    create_response = requests.post(
        f"{API_URL}/api/cases",
        data=case_data,
        headers=headers
    )
    
    if create_response.status_code not in [200, 201]:
        print(f"❌ Помилка створення звернення: {create_response.status_code}")
        print(create_response.text)
        return
    
    case_result = create_response.json()
    public_id = case_result['public_id']
    case_id = case_result['id']
    
    print(f"✅ Звернення створено успішно!")
    print(f"   Public ID: #{public_id}")
    print(f"   Case ID: {case_id}")
    print(f"   Статус: {case_result['status']}")
    
    # 5. Створення звернення З файлами
    print("\n5. Створення звернення з файлами...")
    
    # Створюємо тестові файли
    test_pdf = BytesIO(b"%PDF-1.4\n%Test PDF file\nHello World")
    test_pdf.name = "test_document.pdf"
    
    test_txt = BytesIO(b"Test text file content")
    test_txt.name = "test_notes.txt"
    
    files = [
        ('files', ('test_document.pdf', test_pdf, 'application/pdf')),
        ('files', ('test_image.jpg', BytesIO(b'\xFF\xD8\xFF\xE0'), 'image/jpeg'))
    ]
    
    case_data_with_files = {
        'category_id': category_id,
        'channel_id': channel_id,
        'applicant_name': 'Заявник З Файлами',
        'applicant_phone': '+380509876543',
        'summary': 'Звернення з прикріпленими файлами для тестування завантаження.'
    }
    
    # Видаляємо Content-Type з headers для multipart/form-data
    upload_headers = {"Authorization": f"Bearer {token}"}
    
    create_with_files_response = requests.post(
        f"{API_URL}/api/cases",
        data=case_data_with_files,
        files=files,
        headers=upload_headers
    )
    
    if create_with_files_response.status_code not in [200, 201]:
        print(f"❌ Помилка створення звернення з файлами: {create_with_files_response.status_code}")
        print(create_with_files_response.text)
    else:
        case_with_files = create_with_files_response.json()
        print(f"✅ Звернення з файлами створено успішно!")
        print(f"   Public ID: #{case_with_files['public_id']}")
        print(f"   Статус: {case_with_files['status']}")
    
    # 6. Валідація - спроба створити звернення з некоректними даними
    print("\n6. Тест валідації: відсутнє обов'язкове поле...")
    
    invalid_data = {
        'category_id': category_id,
        # channel_id відсутній (обов'язкове поле)
        'applicant_name': 'Test',
        'summary': 'Test'
    }
    
    invalid_response = requests.post(
        f"{API_URL}/api/cases",
        data=invalid_data,
        headers=headers
    )
    
    if invalid_response.status_code == 422:
        print("✅ Валідація працює: 422 Unprocessable Entity")
    else:
        print(f"⚠️  Очікувався статус 422, отримано: {invalid_response.status_code}")
    
    # 7. Тест валідації коротких полів
    print("\n7. Тест валідації: короткий текст...")
    
    short_data = {
        'category_id': category_id,
        'channel_id': channel_id,
        'applicant_name': 'A',  # Занадто коротке
        'summary': 'Short'  # Занадто коротке
    }
    
    short_response = requests.post(
        f"{API_URL}/api/cases",
        data=short_data,
        headers=headers
    )
    
    if short_response.status_code in [400, 422]:
        print(f"✅ Валідація коротких полів працює: {short_response.status_code}")
    else:
        print(f"⚠️  Очікувався статус 400/422, отримано: {short_response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ Всі тести FE-003 завершено")
    print("=" * 60)

if __name__ == "__main__":
    test_fe003_create_case_with_files()
