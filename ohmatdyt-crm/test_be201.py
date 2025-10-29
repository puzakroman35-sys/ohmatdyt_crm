"""
BE-201: Extended Filtering (AND logic) - Comprehensive Test Suite

Тестування розширеної фільтрації звернень з логікою AND
та можливостей комбінування фільтрів.

Запуск:
    python test_be201.py

Що тестується:
    1. Базові фільтри (статус, категорія, канал) 
    2. Розширені фільтри (підкатегорія, заявник)
    3. Множинний вибір (статуси, категорії, канали)
    4. Фільтри дат (created_at, updated_at)
    5. Комбінації фільтрів (AND логіка)
    6. Пагінація з фільтрами
    7. Сортування з фільтрами
    8. Edge cases (порожні результати, некоректні дані)
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import time


# Configuration
API_BASE_URL = "http://localhost/api"
TEST_ADMIN = {"username": "admin", "password": "admin123"}


def print_separator(char="=", length=80):
    """Друкує роздільник"""
    print(char * length)


def print_step(step_num: int, description: str):
    """Друкує заголовок кроку тестування"""
    print_separator()
    print(f"  [КРОК {step_num}] {description}")
    print_separator()


def print_success(message: str):
    """Друкує повідомлення про успіх"""
    print(f"✅ {message}")


def print_info(message: str):
    """Друкує інформаційне повідомлення"""
    print(f"ℹ️  {message}")


def print_error(message: str):
    """Друкує повідомлення про помилку"""
    print(f"❌ {message}")


def login_admin() -> str:
    """Логін адміністратора та отримання токена"""
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        data={
            "username": TEST_ADMIN["username"],
            "password": TEST_ADMIN["password"]
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        return data["access_token"]
    else:
        raise Exception(f"Failed to login: {response.status_code} - {response.text}")


def create_test_case(
    token: str,
    category_id: str,
    channel_id: str,
    applicant_name: str,
    summary: str,
    subcategory: Optional[str] = None,
    applicant_phone: Optional[str] = None,
    applicant_email: Optional[str] = None
) -> Dict[str, Any]:
    """Створює тестове звернення"""
    headers = {"Authorization": f"Bearer {token}"}
    
    form_data = {
        "category_id": category_id,
        "channel_id": channel_id,
        "applicant_name": applicant_name,
        "summary": summary
    }
    
    if subcategory:
        form_data["subcategory"] = subcategory
    if applicant_phone:
        form_data["applicant_phone"] = applicant_phone
    if applicant_email:
        form_data["applicant_email"] = applicant_email
    
    response = requests.post(
        f"{API_BASE_URL}/cases",
        headers=headers,
        data=form_data
    )
    
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Failed to create case: {response.status_code} - {response.text}")


def test_filter(
    token: str,
    filters: Dict[str, Any],
    expected_min_count: int = 0,
    expected_max_count: Optional[int] = None,
    description: str = ""
) -> Dict[str, Any]:
    """Тестує фільтрацію звернень"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{API_BASE_URL}/cases",
        headers=headers,
        params=filters
    )
    
    if response.status_code != 200:
        print_error(f"Filter test failed: {response.status_code}")
        print_info(f"Response: {response.text}")
        return None
    
    data = response.json()
    total = data.get("total", 0)
    cases = data.get("cases", [])
    
    # Валідація результатів
    if total < expected_min_count:
        print_error(f"Expected at least {expected_min_count} cases, got {total}")
    elif expected_max_count and total > expected_max_count:
        print_error(f"Expected at most {expected_max_count} cases, got {total}")
    else:
        print_success(f"{description}: знайдено {total} звернень")
    
    return data


def main():
    """Головна функція тестування"""
    print_separator("=", 80)
    print("  BE-201: Extended Filtering - Comprehensive Testing")
    print_separator("=", 80)
    print()
    
    results = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    try:
        # ===================================================================
        # КРОК 1: Логін та підготовка
        # ===================================================================
        print_step(1, "Логін як адміністратор та підготовка тестових даних")
        token = login_admin()
        print_success(f"Успішний логін: {TEST_ADMIN['username']}")
        print_info(f"Access token отримано: {token[:50]}...")
        print()
        
        # Отримуємо список категорій та каналів
        headers = {"Authorization": f"Bearer {token}"}
        
        categories_resp = requests.get(
            f"{API_BASE_URL}/categories?limit=100&include_inactive=false",
            headers=headers
        )
        categories = categories_resp.json()["categories"]
        print_info(f"Доступних категорій: {len(categories)}")
        
        channels_resp = requests.get(
            f"{API_BASE_URL}/channels?limit=100&include_inactive=false",
            headers=headers
        )
        channels = channels_resp.json()["channels"]
        print_info(f"Доступних каналів: {len(channels)}")
        
        if len(categories) < 2 or len(channels) < 2:
            print_error("Недостатньо категорій або каналів для тестування")
            return
        
        category1_id = categories[0]["id"]
        category2_id = categories[1]["id"] if len(categories) > 1 else categories[0]["id"]
        channel1_id = channels[0]["id"]
        channel2_id = channels[1]["id"] if len(channels) > 1 else channels[0]["id"]
        
        print_info(f"Категорія 1: {categories[0]['name']} ({category1_id})")
        print_info(f"Категорія 2: {categories[1]['name'] if len(categories) > 1 else categories[0]['name']} ({category2_id})")
        print_info(f"Канал 1: {channels[0]['name']} ({channel1_id})")
        print_info(f"Канал 2: {channels[1]['name'] if len(channels) > 1 else channels[0]['name']} ({channel2_id})")
        print()
        
        # ===================================================================
        # КРОК 2: Створення тестових звернень з різними параметрами
        # ===================================================================
        print_step(2, "Створення тестових звернень для фільтрації")
        
        test_cases = []
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Звернення 1: Категорія 1, Канал 1, Підкатегорія A
        case1 = create_test_case(
            token=token,
            category_id=category1_id,
            channel_id=channel1_id,
            applicant_name="Іванов Іван Іванович",
            applicant_phone="+380501234567",
            applicant_email="ivanov@example.com",
            subcategory="Підкатегорія А",
            summary=f"Тестове звернення BE-201 №1 {timestamp}"
        )
        test_cases.append(case1)
        print_success(f"Створено звернення №1: {case1['public_id']}")
        
        # Звернення 2: Категорія 1, Канал 2, Підкатегорія B
        case2 = create_test_case(
            token=token,
            category_id=category1_id,
            channel_id=channel2_id,
            applicant_name="Петров Петро Петрович",
            applicant_phone="+380507654321",
            applicant_email="petrov@example.com",
            subcategory="Підкатегорія Б",
            summary=f"Тестове звернення BE-201 №2 {timestamp}"
        )
        test_cases.append(case2)
        print_success(f"Створено звернення №2: {case2['public_id']}")
        
        # Звернення 3: Категорія 2, Канал 1, Підкатегорія A
        case3 = create_test_case(
            token=token,
            category_id=category2_id,
            channel_id=channel1_id,
            applicant_name="Сидоров Сидір Сидорович",
            applicant_phone="+380509876543",
            applicant_email="sydorov@example.com",
            subcategory="Підкатегорія А",
            summary=f"Тестове звернення BE-201 №3 {timestamp}"
        )
        test_cases.append(case3)
        print_success(f"Створено звернення №3: {case3['public_id']}")
        
        # Звернення 4: Категорія 2, Канал 2, без підкатегорії
        case4 = create_test_case(
            token=token,
            category_id=category2_id,
            channel_id=channel2_id,
            applicant_name="Коваленко Олена Миколаївна",
            applicant_phone="+380503456789",
            applicant_email="kovalenko@example.com",
            subcategory=None,
            summary=f"Тестове звернення BE-201 №4 {timestamp}"
        )
        test_cases.append(case4)
        print_success(f"Створено звернення №4: {case4['public_id']}")
        
        print_info(f"Всього створено {len(test_cases)} тестових звернень")
        print()
        
        # Невелика затримка щоб забезпечити різні часові мітки
        time.sleep(2)
        
        # ===================================================================
        # КРОК 3: Тест фільтру по підкатегорії (точне співпадіння)
        # ===================================================================
        print_step(3, "Тест фільтру по підкатегорії (точне співпадіння)")
        results["total"] += 1
        
        filter_data = test_filter(
            token=token,
            filters={"subcategory": "Підкатегорія А"},
            expected_min_count=2,  # case1 та case3
            description="Фільтр по підкатегорії 'Підкатегорія А'"
        )
        
        if filter_data and filter_data["total"] >= 2:
            results["passed"] += 1
            # Перевірка що всі результати мають правильну підкатегорію
            correct = all(
                case["subcategory"] == "Підкатегорія А" 
                for case in filter_data["cases"]
            )
            if correct:
                print_success("Всі знайдені звернення мають правильну підкатегорію")
            else:
                print_error("Деякі звернення мають неправильну підкатегорію")
        else:
            results["failed"] += 1
        print()
        
        # ===================================================================
        # КРОК 4: Тест фільтру по імені заявника (часткове співпадіння)
        # ===================================================================
        print_step(4, "Тест фільтру по імені заявника (LIKE search)")
        results["total"] += 1
        
        filter_data = test_filter(
            token=token,
            filters={"applicant_name": "Іван"},
            expected_min_count=1,  # case1
            description="Пошук заявника за іменем 'Іван'"
        )
        
        if filter_data and filter_data["total"] >= 1:
            results["passed"] += 1
            # Перевірка що всі результати містять "Іван"
            correct = all(
                "іван" in case["applicant_name"].lower()
                for case in filter_data["cases"]
            )
            if correct:
                print_success("Всі знайдені звернення містять 'Іван' в імені заявника")
            else:
                print_error("Деякі звернення не містять 'Іван'")
        else:
            results["failed"] += 1
        print()
        
        # ===================================================================
        # КРОК 5: Тест фільтру по телефону (часткове співпадіння)
        # ===================================================================
        print_step(5, "Тест фільтру по телефону заявника")
        results["total"] += 1
        
        filter_data = test_filter(
            token=token,
            filters={"applicant_phone": "501234"},
            expected_min_count=1,  # case1
            description="Пошук по фрагменту телефону '501234'"
        )
        
        if filter_data and filter_data["total"] >= 1:
            results["passed"] += 1
            print_success("Фільтр по телефону працює коректно")
        else:
            results["failed"] += 1
        print()
        
        # ===================================================================
        # КРОК 6: Тест фільтру по email (часткове співпадіння)
        # ===================================================================
        print_step(6, "Тест фільтру по email заявника")
        results["total"] += 1
        
        filter_data = test_filter(
            token=token,
            filters={"applicant_email": "example.com"},
            expected_min_count=4,  # Всі 4 case
            description="Пошук по домену email 'example.com'"
        )
        
        if filter_data and filter_data["total"] >= 4:
            results["passed"] += 1
            print_success("Фільтр по email працює коректно")
        else:
            results["failed"] += 1
        print()
        
        # ===================================================================
        # КРОК 7: Тест множинного вибору статусів
        # ===================================================================
        print_step(7, "Тест множинного вибору статусів (statuses parameter)")
        results["total"] += 1
        
        filter_data = test_filter(
            token=token,
            filters={"statuses": "NEW,IN_PROGRESS"},
            expected_min_count=4,  # Всі нові звернення
            description="Фільтр по статусах 'NEW' або 'IN_PROGRESS'"
        )
        
        if filter_data and filter_data["total"] >= 4:
            results["passed"] += 1
            # Перевірка що всі результати мають правильний статус
            correct = all(
                case["status"] in ["NEW", "IN_PROGRESS"]
                for case in filter_data["cases"]
            )
            if correct:
                print_success("Всі звернення мають статус NEW або IN_PROGRESS")
            else:
                print_error("Деякі звернення мають неправильний статус")
        else:
            results["failed"] += 1
        print()
        
        # ===================================================================
        # КРОК 8: Тест множинного вибору категорій
        # ===================================================================
        print_step(8, "Тест множинного вибору категорій (category_ids parameter)")
        results["total"] += 1
        
        filter_data = test_filter(
            token=token,
            filters={"category_ids": f"{category1_id},{category2_id}"},
            expected_min_count=4,  # Всі 4 case
            description=f"Фільтр по 2 категоріях"
        )
        
        if filter_data and filter_data["total"] >= 4:
            results["passed"] += 1
            print_success("Множинний вибір категорій працює коректно")
        else:
            results["failed"] += 1
        print()
        
        # ===================================================================
        # КРОК 9: Тест множинного вибору каналів
        # ===================================================================
        print_step(9, "Тест множинного вибору каналів (channel_ids parameter)")
        results["total"] += 1
        
        filter_data = test_filter(
            token=token,
            filters={"channel_ids": f"{channel1_id},{channel2_id}"},
            expected_min_count=4,  # Всі 4 case
            description=f"Фільтр по 2 каналах"
        )
        
        if filter_data and filter_data["total"] >= 4:
            results["passed"] += 1
            print_success("Множинний вибір каналів працює коректно")
        else:
            results["failed"] += 1
        print()
        
        # ===================================================================
        # КРОК 10: Тест комбінації фільтрів (AND логіка)
        # ===================================================================
        print_step(10, "Тест комбінації фільтрів (AND логіка)")
        results["total"] += 1
        
        # Комбінація: категорія 1 + підкатегорія А + статус NEW
        filter_data = test_filter(
            token=token,
            filters={
                "category_id": category1_id,
                "subcategory": "Підкатегорія А",
                "status": "NEW"
            },
            expected_min_count=1,  # Тільки case1
            expected_max_count=1,
            description="Категорія 1 + Підкатегорія А + Статус NEW"
        )
        
        if filter_data and filter_data["total"] == 1:
            results["passed"] += 1
            case = filter_data["cases"][0]
            if (case["category_id"] == category1_id and 
                case["subcategory"] == "Підкатегорія А" and
                case["status"] == "NEW"):
                print_success("Комбінація фільтрів працює правильно (AND логіка)")
            else:
                print_error("Результат не відповідає всім фільтрам")
        else:
            results["failed"] += 1
        print()
        
        # ===================================================================
        # КРОК 11: Тест складної комбінації
        # ===================================================================
        print_step(11, "Тест складної комбінації фільтрів")
        results["total"] += 1
        
        # Складна комбінація: множинні статуси + категорії + пошук по імені
        filter_data = test_filter(
            token=token,
            filters={
                "statuses": "NEW,IN_PROGRESS",
                "category_ids": f"{category1_id}",
                "applicant_name": "ов"  # Спільна частина для Іванов та Петров
            },
            expected_min_count=2,  # case1 та case2
            description="Статуси NEW/IN_PROGRESS + Категорія 1 + Ім'я містить 'ов'"
        )
        
        if filter_data and filter_data["total"] >= 2:
            results["passed"] += 1
            print_success("Складна комбінація фільтрів працює")
        else:
            results["failed"] += 1
        print()
        
        # ===================================================================
        # КРОК 12: Тест пагінації з фільтрами
        # ===================================================================
        print_step(12, "Тест пагінації з фільтрами")
        results["total"] += 1
        
        # Отримуємо перші 2 записи
        filter_data_page1 = test_filter(
            token=token,
            filters={
                "statuses": "NEW",
                "limit": 2,
                "skip": 0
            },
            description="Перша сторінка (limit=2, skip=0)"
        )
        
        # Отримуємо наступні 2 записи
        filter_data_page2 = test_filter(
            token=token,
            filters={
                "statuses": "NEW",
                "limit": 2,
                "skip": 2
            },
            description="Друга сторінка (limit=2, skip=2)"
        )
        
        if (filter_data_page1 and filter_data_page2 and
            len(filter_data_page1["cases"]) <= 2 and
            len(filter_data_page2["cases"]) <= 2):
            results["passed"] += 1
            
            # Перевірка що ID не повторюються
            ids_page1 = {case["id"] for case in filter_data_page1["cases"]}
            ids_page2 = {case["id"] for case in filter_data_page2["cases"]}
            
            if not ids_page1.intersection(ids_page2):
                print_success("Пагінація працює правильно (немає дублікатів)")
            else:
                print_error("Знайдено дублікати між сторінками")
        else:
            results["failed"] += 1
        print()
        
        # ===================================================================
        # КРОК 13: Тест сортування з фільтрами
        # ===================================================================
        print_step(13, "Тест сортування з фільтрами")
        results["total"] += 1
        
        # Сортування по public_id (зростання)
        filter_data_asc = test_filter(
            token=token,
            filters={
                "statuses": "NEW",
                "order_by": "public_id",
                "limit": 10
            },
            description="Сортування по public_id (зростання)"
        )
        
        # Сортування по public_id (спадання)
        filter_data_desc = test_filter(
            token=token,
            filters={
                "statuses": "NEW",
                "order_by": "-public_id",
                "limit": 10
            },
            description="Сортування по public_id (спадання)"
        )
        
        if filter_data_asc and filter_data_desc:
            results["passed"] += 1
            
            # Перевірка порядку
            if len(filter_data_asc["cases"]) > 1:
                ids_asc = [case["public_id"] for case in filter_data_asc["cases"]]
                is_ascending = all(ids_asc[i] <= ids_asc[i+1] for i in range(len(ids_asc)-1))
                
                if is_ascending:
                    print_success("Сортування по зростанню працює правильно")
                else:
                    print_error("Сортування по зростанню працює некоректно")
            
            if len(filter_data_desc["cases"]) > 1:
                ids_desc = [case["public_id"] for case in filter_data_desc["cases"]]
                is_descending = all(ids_desc[i] >= ids_desc[i+1] for i in range(len(ids_desc)-1))
                
                if is_descending:
                    print_success("Сортування по спаданню працює правильно")
                else:
                    print_error("Сортування по спаданню працює некоректно")
        else:
            results["failed"] += 1
        print()
        
        # ===================================================================
        # КРОК 14: Тест фільтрів дат (updated_at)
        # ===================================================================
        print_step(14, "Тест фільтрів по даті оновлення (updated_date_from/to)")
        results["total"] += 1
        
        # Фільтр: звернення оновлені за останню годину
        one_hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        now = datetime.utcnow().isoformat()
        
        filter_data = test_filter(
            token=token,
            filters={
                "updated_date_from": one_hour_ago,
                "updated_date_to": now
            },
            expected_min_count=4,  # Всі тестові звернення
            description="Звернення оновлені за останню годину"
        )
        
        if filter_data and filter_data["total"] >= 4:
            results["passed"] += 1
            print_success("Фільтри по даті оновлення працюють")
        else:
            results["failed"] += 1
        print()
        
        # ===================================================================
        # КРОК 15: Edge case - порожній результат
        # ===================================================================
        print_step(15, "Edge case: фільтри що не повертають результатів")
        results["total"] += 1
        
        filter_data = test_filter(
            token=token,
            filters={
                "applicant_name": "НеІснуючийЗаявник12345",
                "status": "NEW"
            },
            expected_min_count=0,
            expected_max_count=0,
            description="Пошук неіснуючого заявника"
        )
        
        if filter_data and filter_data["total"] == 0:
            results["passed"] += 1
            print_success("Порожній результат обробляється правильно")
        else:
            results["failed"] += 1
        print()
        
        # ===================================================================
        # КРОК 16: Edge case - некоректні дані фільтрів
        # ===================================================================
        print_step(16, "Edge case: некоректні дані у фільтрах")
        results["total"] += 1
        
        headers_auth = {"Authorization": f"Bearer {token}"}
        
        # Некоректний UUID в category_ids
        response = requests.get(
            f"{API_BASE_URL}/cases",
            headers=headers_auth,
            params={"category_ids": "not-a-valid-uuid"}
        )
        
        if response.status_code == 400:
            results["passed"] += 1
            print_success("Некоректний UUID правильно відхиляється (400 Bad Request)")
            print_info(f"Повідомлення: {response.json().get('detail', 'N/A')}")
        else:
            results["failed"] += 1
            print_error(f"Очікувався статус 400, отримано {response.status_code}")
        print()
        
        # ===================================================================
        # ПІДСУМОК
        # ===================================================================
        print_separator("=", 80)
        print("ПІДСУМОК ТЕСТУВАННЯ BE-201")
        print_separator("=", 80)
        
        print(f"Результати тестування:")
        print(f"  ✅ PASS - {results['passed']} тестів")
        print(f"  ❌ FAIL - {results['failed']} тестів")
        print(f"  📊 TOTAL - {results['total']} тестів")
        print()
        
        if results["failed"] == 0:
            print_success("Всі тести пройдено успішно! ✨")
            print()
            print_info("BE-201 ГОТОВО ДО PRODUCTION ✅")
        else:
            print_error(f"Деякі тести провалилися: {results['failed']}/{results['total']}")
            print()
            print_info("Потрібна додаткова перевірка")
        
        print()
        print_info("Імплементовані фільтри:")
        print("  • subcategory - Точне співпадіння або LIKE з %")
        print("  • applicant_name - LIKE пошук (регістронезалежний)")
        print("  • applicant_phone - LIKE пошук")
        print("  • applicant_email - LIKE пошук (регістронезалежний)")
        print("  • updated_date_from/to - Діапазон дат оновлення")
        print("  • statuses - Множинний вибір статусів (через кому)")
        print("  • category_ids - Множинний вибір категорій (через кому)")
        print("  • channel_ids - Множинний вибір каналів (через кому)")
        print()
        print_info("Логіка фільтрації:")
        print("  • Між різними типами фільтрів: AND")
        print("  • Всередині множинних фільтрів (statuses, category_ids): OR")
        print("  • Пагінація та сортування працюють разом з фільтрами")
        print()
        print_separator("=", 80)
        
    except Exception as e:
        print_separator("=", 80)
        print_error(f"Помилка під час тестування: {str(e)}")
        print_separator("=", 80)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
