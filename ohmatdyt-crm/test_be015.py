"""
BE-015: Тести для healthcheck та логування

Тестує:
- GET /healthz endpoint
- Перевірку DB та Redis з'єднань
- Структуроване логування
- Request tracking middleware
"""
import os
import sys
import httpx
import json
from unittest.mock import patch, MagicMock

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


def test_healthz_endpoint():
    """Тест 1: Перевірка /healthz endpoint"""
    test_name = "healthz_endpoint"
    print_step("[КРОК 1] Тестування /healthz endpoint")
    
    try:
        response = httpx.get(f"{API_BASE_URL}/healthz", timeout=10.0)
        
        if response.status_code != 200:
            print_error(f"Невірний статус код: {response.status_code}")
            test_results[test_name] = "FAIL"
            return
        
        data = response.json()
        print_info(f"Відповідь: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # Перевірка структури відповіді
        required_fields = ["status", "timestamp", "version", "services", "filesystem"]
        for field in required_fields:
            if field not in data:
                print_error(f"Відсутнє поле: {field}")
                test_results[test_name] = "FAIL"
                return
        
        # Перевірка вкладених полів
        if "database" not in data["services"]:
            print_error("Відсутнє поле services.database")
            test_results[test_name] = "FAIL"
            return
        
        if "redis" not in data["services"]:
            print_error("Відсутнє поле services.redis")
            test_results[test_name] = "FAIL"
            return
        
        print_success("✅ /healthz endpoint працює коректно")
        print_info(f"Статус: {data['status']}")
        print_info(f"Database: {data['services']['database']}")
        print_info(f"Redis: {data['services']['redis']}")
        print_info(f"Version: {data['version']}")
        
        test_results[test_name] = "PASS"
        
    except Exception as e:
        print_error(f"Помилка: {str(e)}")
        test_results[test_name] = "FAIL"


def test_healthz_with_request_id():
    """Тест 2: Перевірка X-Request-ID в headers"""
    test_name = "request_id_header"
    print_step("[КРОК 2] Перевірка X-Request-ID middleware")
    
    try:
        # Відправляємо запит з власним request-id
        custom_request_id = "test-request-123"
        headers = {"X-Request-ID": custom_request_id}
        
        response = httpx.get(
            f"{API_BASE_URL}/healthz",
            headers=headers,
            timeout=10.0
        )
        
        if response.status_code != 200:
            print_error(f"Невірний статус код: {response.status_code}")
            test_results[test_name] = "FAIL"
            return
        
        # Перевірка, що request-id повернувся в headers
        if "X-Request-ID" not in response.headers:
            print_error("X-Request-ID відсутній в response headers")
            test_results[test_name] = "FAIL"
            return
        
        returned_id = response.headers["X-Request-ID"]
        print_info(f"Відправлено Request-ID: {custom_request_id}")
        print_info(f"Отримано Request-ID: {returned_id}")
        
        if returned_id == custom_request_id:
            print_success("Request-ID middleware працює коректно")
            test_results[test_name] = "PASS"
        else:
            print_error("Request-ID не співпадає")
            test_results[test_name] = "FAIL"
        
    except Exception as e:
        print_error(f"Помилка: {str(e)}")
        test_results[test_name] = "FAIL"


def test_legacy_health_endpoint():
    """Тест 3: Перевірка legacy /health endpoint"""
    test_name = "legacy_health_endpoint"
    print_step("[КРОК 3] Перевірка legacy /health endpoint (backward compatibility)")
    
    try:
        response = httpx.get(f"{API_BASE_URL}/health", timeout=10.0)
        
        if response.status_code != 200:
            print_error(f"Невірний статус код: {response.status_code}")
            test_results[test_name] = "FAIL"
            return
        
        data = response.json()
        
        # Має повертати ту саму структуру що й /healthz
        if "status" not in data or "services" not in data:
            print_error("Legacy endpoint не повертає правильну структуру")
            test_results[test_name] = "FAIL"
            return
        
        print_success("Legacy /health endpoint працює")
        print_info("Backward compatibility забезпечено")
        test_results[test_name] = "PASS"
        
    except Exception as e:
        print_error(f"Помилка: {str(e)}")
        test_results[test_name] = "FAIL"


def test_root_endpoint():
    """Тест 4: Перевірка root endpoint з логуванням"""
    test_name = "root_endpoint_logging"
    print_step("[КРОК 4] Тестування root endpoint та логування")
    
    try:
        response = httpx.get(f"{API_BASE_URL}/", timeout=10.0)
        
        if response.status_code != 200:
            print_error(f"Невірний статус код: {response.status_code}")
            test_results[test_name] = "FAIL"
            return
        
        data = response.json()
        
        # Перевірка наявності X-Request-ID
        if "X-Request-ID" not in response.headers:
            print_error("X-Request-ID відсутній (middleware не працює)")
            test_results[test_name] = "FAIL"
            return
        
        print_success("Root endpoint працює")
        print_info(f"Message: {data.get('message')}")
        print_info(f"Version: {data.get('version')}")
        print_info(f"Request-ID: {response.headers['X-Request-ID']}")
        test_results[test_name] = "PASS"
        
    except Exception as e:
        print_error(f"Помилка: {str(e)}")
        test_results[test_name] = "FAIL"


def test_multiple_requests_unique_ids():
    """Тест 5: Перевірка унікальності request-id для різних запитів"""
    test_name = "unique_request_ids"
    print_step("[КРОК 5] Перевірка унікальності request-id")
    
    try:
        request_ids = []
        
        # Робимо 5 запитів
        for i in range(5):
            response = httpx.get(f"{API_BASE_URL}/healthz", timeout=10.0)
            
            if "X-Request-ID" in response.headers:
                request_id = response.headers["X-Request-ID"]
                request_ids.append(request_id)
                print_info(f"Запит {i+1}: {request_id}")
        
        # Перевірка унікальності
        if len(request_ids) != len(set(request_ids)):
            print_error("Request-ID не унікальні!")
            test_results[test_name] = "FAIL"
            return
        
        print_success(f"Всі {len(request_ids)} request-id унікальні")
        test_results[test_name] = "PASS"
        
    except Exception as e:
        print_error(f"Помилка: {str(e)}")
        test_results[test_name] = "FAIL"


def print_summary():
    """Друкує підсумок тестування"""
    print_header("ПІДСУМОК ТЕСТУВАННЯ BE-015")
    
    print(f"\n{BOLD}Результати тестування:{RESET}")
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results.items():
        if result == "PASS":
            print(f"  {GREEN}✅ PASS{RESET} - {test_name}")
            passed += 1
        else:
            print(f"  {RED}❌ FAIL{RESET} - {test_name}")
            failed += 1
    
    total = passed + failed
    print(f"\n{BOLD}📊 TOTAL - {passed}/{total} тестів пройдено{RESET}")
    
    if failed == 0:
        print(f"\n{GREEN}{BOLD}✅ Всі тести пройдено успішно! ✨{RESET}")
        print(f"{BLUE}ℹ️  BE-015 ГОТОВО ДО PRODUCTION ✅{RESET}")
        return 0
    else:
        print(f"\n{RED}{BOLD}❌ Деякі тести не пройдено{RESET}")
        return 1


def main():
    """Основна функція тестування"""
    print_header("BE-015: Healthcheck та базове логування - Testing")
    print("Тестування healthcheck endpoint та structured logging\n")
    print(f"Компоненти що тестуються:")
    print(f"  - GET /healthz endpoint з перевіркою DB та Redis")
    print(f"  - X-Request-ID middleware для request tracking")
    print(f"  - Structured JSON logging (перевіряється візуально в логах)")
    print(f"  - Legacy /health endpoint (backward compatibility)")
    
    # Перевірка доступності API
    print_step("[ПЕРЕВІРКА] Підключення до API")
    try:
        response = httpx.get(f"{API_BASE_URL}/", timeout=10.0)
        print_success(f"API доступний: {API_BASE_URL}")
    except Exception as e:
        print_error(f"API недоступний: {e}")
        print_info("Переконайтесь що API запущений (docker-compose up)")
        return 1
    
    # Запуск тестів
    test_healthz_endpoint()
    test_healthz_with_request_id()
    test_legacy_health_endpoint()
    test_root_endpoint()
    test_multiple_requests_unique_ids()
    
    # Підсумок
    return print_summary()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
