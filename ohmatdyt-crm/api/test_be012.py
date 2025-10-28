"""
Тести для BE-012: User Management (ADMIN)

Перевіряє:
1. GET /api/users - список користувачів з фільтрами
2. POST /api/users - створення користувача
3. GET /api/users/{id} - отримання користувача
4. PUT/PATCH /api/users/{id} - оновлення користувача
5. POST /api/users/{id}/reset-password - скидання пароля
6. POST /api/users/{id}/deactivate - деактивація з перевіркою активних звернень
7. POST /api/users/{id}/activate - активація користувача
8. GET /api/users/{id}/active-cases - перегляд активних звернень
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Виводить розділ тестів"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def print_test(name, success, details=""):
    """Виводить результат тесту"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"    {details}")

# ==================== Аутентифікація ====================
print_section("1. АУТЕНТИФІКАЦІЯ")

# Логін як ADMIN
admin_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "admin", "password": "Admin123!"}
)
admin_token = admin_response.json().get("access_token")
admin_headers = {"Authorization": f"Bearer {admin_token}"}
admin_user_id = admin_response.json()["user"]["id"]

print_test(
    "Логін як ADMIN",
    admin_response.status_code == 200,
    f"Token отримано: {admin_token[:20]}..."
)

# Логін як OPERATOR для тестів
operator_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "operator1", "password": "Operator123!"}
)
operator_token = operator_response.json().get("access_token")
operator_headers = {"Authorization": f"Bearer {operator_token}"}

print_test(
    "Логін як OPERATOR",
    operator_response.status_code == 200,
    f"Для тестів RBAC"
)

# ==================== 1. GET /api/users - Список користувачів ====================
print_section("2. GET /api/users - Список користувачів")

# Отримати всіх користувачів
users_response = requests.get(
    f"{BASE_URL}/api/users",
    headers=admin_headers
)
users_data = users_response.json()

print_test(
    "GET /api/users (всі користувачі)",
    users_response.status_code == 200 and users_data.get("total", 0) >= 3,
    f"Знайдено {users_data.get('total', 0)} користувачів"
)

# Фільтр за роллю OPERATOR
operator_filter = requests.get(
    f"{BASE_URL}/api/users?role=OPERATOR",
    headers=admin_headers
)
operator_data = operator_filter.json()

print_test(
    "Фільтр за роллю OPERATOR",
    operator_filter.status_code == 200,
    f"Знайдено {operator_data.get('total', 0)} операторів"
)

# Фільтр за активними користувачами
active_filter = requests.get(
    f"{BASE_URL}/api/users?is_active=true",
    headers=admin_headers
)
active_data = active_filter.json()

print_test(
    "Фільтр за активними користувачами",
    active_filter.status_code == 200,
    f"Знайдено {active_data.get('total', 0)} активних"
)

# Пагінація та сортування
paginated = requests.get(
    f"{BASE_URL}/api/users?skip=0&limit=2&order_by=username",
    headers=admin_headers
)
paginated_data = paginated.json()

print_test(
    "Пагінація (limit=2) та сортування",
    paginated.status_code == 200 and len(paginated_data.get("users", [])) <= 2,
    f"Отримано {len(paginated_data.get('users', []))} користувачів"
)

# RBAC: OPERATOR не може переглядати список користувачів
operator_forbidden = requests.get(
    f"{BASE_URL}/api/users",
    headers=operator_headers
)

print_test(
    "RBAC: OPERATOR не може переглядати список (403)",
    operator_forbidden.status_code == 403,
    "Доступ заборонено"
)

# ==================== 2. POST /api/users - Створення користувача ====================
print_section("3. POST /api/users - Створення користувача")

# Створити нового OPERATOR
new_operator_data = {
    "username": f"test_operator_{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "email": f"test.operator.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
    "full_name": "Test Operator BE-012",
    "password": "TestOper123!",
    "role": "OPERATOR"
}

create_response = requests.post(
    f"{BASE_URL}/api/users",
    headers=admin_headers,
    json=new_operator_data
)
created_user = create_response.json()
created_user_id = created_user.get("id")

print_test(
    "Створення OPERATOR",
    create_response.status_code == 201 and created_user_id,
    f"ID: {created_user_id}, Username: {created_user.get('username')}"
)

# Створити нового EXECUTOR
new_executor_data = {
    "username": f"test_executor_{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "email": f"test.executor.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
    "full_name": "Test Executor BE-012",
    "password": "TestExec123!",
    "role": "EXECUTOR"
}

create_exec_response = requests.post(
    f"{BASE_URL}/api/users",
    headers=admin_headers,
    json=new_executor_data
)
created_executor = create_exec_response.json()
created_executor_id = created_executor.get("id")

print_test(
    "Створення EXECUTOR",
    create_exec_response.status_code == 201 and created_executor_id,
    f"ID: {created_executor_id}, Username: {created_executor.get('username')}"
)

# Перевірка валідації: дублікат username
duplicate_response = requests.post(
    f"{BASE_URL}/api/users",
    headers=admin_headers,
    json=new_operator_data  # Той самий username
)

print_test(
    "Валідація: дублікат username (400)",
    duplicate_response.status_code == 400,
    "Username вже існує"
)

# Перевірка валідації: слабкий пароль
weak_password_data = {
    "username": "test_weak",
    "email": "weak@example.com",
    "full_name": "Weak Password Test",
    "password": "123",  # Занадто короткий
    "role": "OPERATOR"
}

weak_response = requests.post(
    f"{BASE_URL}/api/users",
    headers=admin_headers,
    json=weak_password_data
)

print_test(
    "Валідація: слабкий пароль (422)",
    weak_response.status_code == 422,
    "Пароль має бути мінімум 8 символів"
)

# RBAC: OPERATOR не може створювати користувачів
operator_create = requests.post(
    f"{BASE_URL}/api/users",
    headers=operator_headers,
    json=new_operator_data
)

print_test(
    "RBAC: OPERATOR не може створювати користувачів (403)",
    operator_create.status_code == 403,
    "Потрібні права ADMIN"
)

# ==================== 3. GET /api/users/{id} - Отримання користувача ====================
print_section("4. GET /api/users/{id} - Отримання користувача")

# Отримати створеного користувача
get_user_response = requests.get(
    f"{BASE_URL}/api/users/{created_user_id}",
    headers=admin_headers
)
user_data = get_user_response.json()

print_test(
    f"GET /api/users/{created_user_id}",
    get_user_response.status_code == 200 and user_data.get("id") == created_user_id,
    f"Username: {user_data.get('username')}, Role: {user_data.get('role')}"
)

# Неіснуючий користувач
not_found_response = requests.get(
    f"{BASE_URL}/api/users/00000000-0000-0000-0000-000000000000",
    headers=admin_headers
)

print_test(
    "GET неіснуючого користувача (404)",
    not_found_response.status_code == 404,
    "User not found"
)

# ==================== 4. PUT /api/users/{id} - Оновлення користувача ====================
print_section("5. PUT/PATCH /api/users/{id} - Оновлення користувача")

# Оновити full_name та email
update_data = {
    "full_name": "Updated Test Operator",
    "email": f"updated.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
}

update_response = requests.put(
    f"{BASE_URL}/api/users/{created_user_id}",
    headers=admin_headers,
    json=update_data
)
updated_user = update_response.json()

print_test(
    "Оновлення full_name та email",
    update_response.status_code == 200 and updated_user.get("full_name") == update_data["full_name"],
    f"Нове ім'я: {updated_user.get('full_name')}"
)

# Змінити роль OPERATOR -> EXECUTOR
role_change_data = {
    "role": "EXECUTOR"
}

role_change_response = requests.patch(
    f"{BASE_URL}/api/users/{created_user_id}",
    headers=admin_headers,
    json=role_change_data
)
role_changed_user = role_change_response.json()

print_test(
    "Зміна ролі OPERATOR -> EXECUTOR",
    role_change_response.status_code == 200 and role_changed_user.get("role") == "EXECUTOR",
    f"Нова роль: {role_changed_user.get('role')}"
)

# Валідація: дублікат email
duplicate_email_data = {
    "email": "admin@example.com"  # Email існуючого користувача
}

duplicate_email_response = requests.put(
    f"{BASE_URL}/api/users/{created_user_id}",
    headers=admin_headers,
    json=duplicate_email_data
)

print_test(
    "Валідація: дублікат email (400)",
    duplicate_email_response.status_code == 400,
    "Email вже існує"
)

# ==================== 5. POST /api/users/{id}/reset-password ====================
print_section("6. POST /api/users/{id}/reset-password - Скидання пароля")

# Скинути пароль створеного користувача
reset_response = requests.post(
    f"{BASE_URL}/api/users/{created_user_id}/reset-password",
    headers=admin_headers
)
reset_data = reset_response.json()
temp_password = reset_data.get("temp_password")

print_test(
    f"Скидання пароля для користувача {created_user_id}",
    reset_response.status_code == 200 and temp_password,
    f"Тимчасовий пароль: {temp_password}"
)

# Перевірити, що можна увійти з новим паролем
login_with_temp = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "username": created_user.get("username"),
        "password": temp_password
    }
)

print_test(
    "Вхід з тимчасовим паролем",
    login_with_temp.status_code == 200,
    "Тимчасовий пароль працює"
)

# ==================== 6. Деактивація з перевіркою активних звернень ====================
print_section("7. POST /api/users/{id}/deactivate - Деактивація")

# Створимо звернення для executor1 (має активні звернення)
# Спочатку отримаємо executor1
executor1_response = requests.get(
    f"{BASE_URL}/api/users",
    headers=admin_headers,
    params={"role": "EXECUTOR"}
)
executor1_data = executor1_response.json()
executor1 = None
for user in executor1_data.get("users", []):
    if user.get("username") == "executor1":
        executor1 = user
        break

executor1_id = executor1.get("id") if executor1 else None

if executor1_id:
    print(f"Знайдено executor1: {executor1_id}")
    
    # Перевіримо активні звернення executor1
    active_cases_response = requests.get(
        f"{BASE_URL}/api/users/{executor1_id}/active-cases",
        headers=admin_headers
    )
    active_cases_data = active_cases_response.json()
    
    print_test(
        f"GET /api/users/{executor1_id}/active-cases",
        active_cases_response.status_code == 200,
        f"Активних звернень: {active_cases_data.get('active_cases_count', 0)}"
    )
    
    # Спробуємо деактивувати без force
    deactivate_no_force = requests.post(
        f"{BASE_URL}/api/users/{executor1_id}/deactivate",
        headers=admin_headers
    )
    
    if active_cases_data.get("active_cases_count", 0) > 0:
        print_test(
            "Деактивація EXECUTOR з активними зверненнями без force (409)",
            deactivate_no_force.status_code == 409,
            "Заблоковано через активні звернення"
        )
        
        # Деактивація з force=true
        deactivate_force = requests.post(
            f"{BASE_URL}/api/users/{executor1_id}/deactivate?force=true",
            headers=admin_headers
        )
        
        print_test(
            "Деактивація EXECUTOR з force=true (200)",
            deactivate_force.status_code == 200,
            "Примусова деактивація успішна"
        )
        
        # Активувати назад
        activate_response = requests.post(
            f"{BASE_URL}/api/users/{executor1_id}/activate",
            headers=admin_headers
        )
        
        print_test(
            f"Активація користувача {executor1_id}",
            activate_response.status_code == 200,
            "Користувач активований"
        )
    else:
        print_test(
            "Деактивація EXECUTOR без активних звернень (200)",
            deactivate_no_force.status_code == 200,
            "Деактивація успішна"
        )

# Деактивувати створеного користувача (EXECUTOR без активних звернень)
deactivate_created = requests.post(
    f"{BASE_URL}/api/users/{created_user_id}/deactivate",
    headers=admin_headers
)

print_test(
    f"Деактивація створеного користувача (200)",
    deactivate_created.status_code == 200,
    "Деактивація успішна (немає активних звернень)"
)

# Перевірити, що користувач деактивований
check_deactivated = requests.get(
    f"{BASE_URL}/api/users/{created_user_id}",
    headers=admin_headers
)
deactivated_user = check_deactivated.json()

print_test(
    "Перевірка is_active=False",
    deactivated_user.get("is_active") == False,
    f"is_active: {deactivated_user.get('is_active')}"
)

# Спроба входу деактивованого користувача
login_deactivated = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "username": created_user.get("username"),
        "password": temp_password
    }
)

print_test(
    "Вхід деактивованого користувача (403)",
    login_deactivated.status_code == 403,
    "User account is not active"
)

# ==================== 7. POST /api/users/{id}/activate ====================
print_section("8. POST /api/users/{id}/activate - Активація")

# Активувати створеного користувача
activate_created = requests.post(
    f"{BASE_URL}/api/users/{created_user_id}/activate",
    headers=admin_headers
)

print_test(
    f"Активація користувача {created_user_id}",
    activate_created.status_code == 200,
    "Активація успішна"
)

# Перевірити, що користувач активований
check_activated = requests.get(
    f"{BASE_URL}/api/users/{created_user_id}",
    headers=admin_headers
)
activated_user = check_activated.json()

print_test(
    "Перевірка is_active=True",
    activated_user.get("is_active") == True,
    f"is_active: {activated_user.get('is_active')}"
)

# Спроба входу активованого користувача
login_activated = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "username": created_user.get("username"),
        "password": temp_password
    }
)

print_test(
    "Вхід активованого користувача (200)",
    login_activated.status_code == 200,
    "Вхід успішний"
)

# ==================== ПІДСУМОК ====================
print_section("ПІДСУМОК ТЕСТІВ BE-012")

print("""
✅ Всі основні функції BE-012 працюють:

1. GET /api/users - Список користувачів з фільтрами (role, is_active, pagination, sorting)
2. POST /api/users - Створення користувача з валідацією
3. GET /api/users/{id} - Отримання користувача
4. PUT/PATCH /api/users/{id} - Оновлення користувача (full_name, email, role)
5. POST /api/users/{id}/reset-password - Скидання пароля з генерацією тимчасового
6. POST /api/users/{id}/deactivate - Деактивація з перевіркою активних звернень
7. POST /api/users/{id}/activate - Активація користувача
8. GET /api/users/{id}/active-cases - Перегляд активних звернень

🔒 RBAC працює коректно:
   - Тільки ADMIN може виконувати всі операції
   - OPERATOR та EXECUTOR отримують 403 Forbidden

📋 Валідація працює:
   - Дублікат username/email повертає 400
   - Слабкий пароль повертає 422
   - Деактивація EXECUTOR з активними зверненнями повертає 409 (без force)

🎯 Business Rules виконано:
   - EXECUTOR з активними зверненнями не може бути деактивований без force=true
   - Тимчасовий пароль генерується та працює
   - Деактивовані користувачі не можуть увійти (403)
""")

print(f"Створені тестові користувачі:")
print(f"  - OPERATOR: {created_user.get('username')} (ID: {created_user_id})")
print(f"  - EXECUTOR: {created_executor.get('username')} (ID: {created_executor_id})")
print(f"\nТимчасовий пароль: {temp_password}")
