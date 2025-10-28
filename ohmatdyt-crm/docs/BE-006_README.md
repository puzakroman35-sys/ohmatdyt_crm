# BE-006: Створення звернення з файлами та email-тригером

## Опис

Реалізація ендпоінту створення звернення (case) з можливістю завантаження файлів через multipart/form-data та автоматичним тригером email-нотифікації для виконавців.

## Основні функції

- ✅ Multipart форма для створення звернень з файлами
- ✅ Валідація типів файлів (pdf, doc, docx, xls, xlsx, jpg, jpeg, png)
- ✅ Валідація розміру файлів (максимум 10MB)
- ✅ Автоматична генерація унікального 6-значного public_id
- ✅ RBAC: тільки OPERATOR може створювати звернення
- ✅ Email-тригер через Celery для нотифікації виконавців
- ✅ Retry механізм з експоненційною затримкою

## API Endpoints

### POST /api/cases

Створення нового звернення з опціональними файлами.

**Content-Type:** `multipart/form-data`

**Authorization:** Bearer token (OPERATOR role)

**Form Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| category_id | UUID string | Yes | ID категорії звернення |
| channel_id | UUID string | Yes | ID каналу звернення |
| applicant_name | string (1-200) | Yes | Ім'я заявника |
| summary | string | Yes | Опис звернення |
| subcategory | string (max 200) | No | Підкатегорія |
| applicant_phone | string (max 50) | No | Телефон заявника |
| applicant_email | email | No | Email заявника |
| files[] | file | No | Прикріплені файли (multiple) |

**Response:** `201 Created`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "public_id": 123456,
  "status": "NEW",
  "category_id": "660e8400-e29b-41d4-a716-446655440000",
  "channel_id": "770e8400-e29b-41d4-a716-446655440000",
  "applicant_name": "Іван Петренко",
  "applicant_phone": "+380501234567",
  "applicant_email": "ivan@example.com",
  "summary": "Проблема з обладнанням",
  "subcategory": "Комп'ютерна техніка",
  "author_id": "880e8400-e29b-41d4-a716-446655440000",
  "responsible_id": null,
  "created_at": "2025-10-28T10:00:00Z",
  "updated_at": "2025-10-28T10:00:00Z"
}
```

### GET /api/cases

Отримання списку звернень з фільтрацією.

**Query Parameters:**

- `skip` (int, default 0) - Пропустити N записів
- `limit` (int, default 50, max 100) - Кількість записів
- `status` (CaseStatus) - Фільтр по статусу
- `category_id` (UUID) - Фільтр по категорії
- `channel_id` (UUID) - Фільтр по каналу

**RBAC:**
- OPERATOR: бачить тільки свої звернення
- EXECUTOR/ADMIN: бачить всі звернення

### GET /api/cases/{case_id}

Отримання звернення по ID.

**RBAC:**
- OPERATOR: може переглядати тільки свої звернення
- EXECUTOR/ADMIN: може переглядати всі звернення

## Валідація файлів

### Дозволені типи

- Документи: `pdf`, `doc`, `docx`, `xls`, `xlsx`
- Зображення: `jpg`, `jpeg`, `png`

### Обмеження

- Максимальний розмір файлу: **10MB**
- Кількість файлів: необмежена
- Ім'я файлу: санітизується автоматично

### Зберігання

```
MEDIA_ROOT/cases/{public_id}/{uuid}_{filename}
```

Приклад: `/var/app/media/cases/123456/a1b2c3d4_document.pdf`

## Email Нотифікації

### Тригер

Нотифікація відправляється автоматично після успішного створення звернення.

### Celery Task

**Назва:** `app.celery_app.send_new_case_notification`

**Параметри:**
- `case_id` (UUID string) - ID звернення
- `case_public_id` (int) - Публічний 6-значний ID
- `category_id` (UUID string) - ID категорії

**Retry механізм:**
- Максимум спроб: 5
- Затримка: експоненційна (60s, 120s, 240s, 480s, 960s)

### Отримувачі

На даний момент: всі активні користувачі з роллю EXECUTOR або ADMIN.

Майбутнє: фільтрація по категорії (вимагає додаткової таблиці executor_categories).

## Приклади використання

### cURL: Створення без файлів

```bash
curl -X POST "http://localhost:8000/api/cases" \
  -H "Authorization: Bearer YOUR_OPERATOR_TOKEN" \
  -F "category_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "channel_id=660e8400-e29b-41d4-a716-446655440000" \
  -F "applicant_name=Марія Коваленко" \
  -F "summary=Запит на консультацію"
```

### cURL: Створення з файлами

```bash
curl -X POST "http://localhost:8000/api/cases" \
  -H "Authorization: Bearer YOUR_OPERATOR_TOKEN" \
  -F "category_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "channel_id=660e8400-e29b-41d4-a716-446655440000" \
  -F "applicant_name=Іван Петренко" \
  -F "applicant_phone=+380501234567" \
  -F "applicant_email=ivan@example.com" \
  -F "summary=Проблема з обладнанням" \
  -F "subcategory=Комп'ютерна техніка" \
  -F "files=@document.pdf" \
  -F "files=@screenshot.png"
```

### Python: Requests

```python
import requests

url = "http://localhost:8000/api/cases"
headers = {"Authorization": f"Bearer {operator_token}"}

# Дані форми
data = {
    "category_id": "550e8400-e29b-41d4-a716-446655440000",
    "channel_id": "660e8400-e29b-41d4-a716-446655440000",
    "applicant_name": "Петро Сидоренко",
    "applicant_phone": "+380671234567",
    "summary": "Технічна проблема"
}

# Файли
files = [
    ('files', ('document.pdf', open('document.pdf', 'rb'), 'application/pdf')),
    ('files', ('photo.jpg', open('photo.jpg', 'rb'), 'image/jpeg'))
]

# Відправка запиту
response = requests.post(url, headers=headers, data=data, files=files)

if response.status_code == 201:
    case = response.json()
    print(f"✓ Case created: #{case['public_id']}")
else:
    print(f"✗ Error: {response.status_code}")
    print(response.text)
```

### JavaScript: Fetch API

```javascript
const formData = new FormData();
formData.append('category_id', '550e8400-e29b-41d4-a716-446655440000');
formData.append('channel_id', '660e8400-e29b-41d4-a716-446655440000');
formData.append('applicant_name', 'Олена Шевченко');
formData.append('summary', 'Запит на допомогу');

// Додати файли
const fileInput = document.getElementById('fileInput');
for (const file of fileInput.files) {
  formData.append('files', file);
}

fetch('http://localhost:8000/api/cases', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${operatorToken}`
  },
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Case created:', data.public_id);
})
.catch(error => {
  console.error('Error:', error);
});
```

## Тестування

### Запуск тестів

#### PowerShell (Windows)

```powershell
.\ohmatdyt-crm\scripts\test-be006.ps1
```

#### Bash (Linux/Mac)

```bash
cd ohmatdyt-crm/api
python test_be006.py
```

### Тестові сценарії

1. **Happy Path:** Створення з 2 файлами
2. **Validation:** Відсутні обов'язкові поля
3. **Validation:** Неприпустимий тип файлу (.exe)
4. **Validation:** Файл більше 10MB

### Очікувані результати

- ✅ Успішне створення → 201 Created
- ✅ Відсутні поля → 422 Unprocessable Entity
- ✅ Невалідний файл → 400 Bad Request

## Коди помилок

| Код | Опис |
|-----|------|
| 201 | Звернення успішно створено |
| 400 | Помилка валідації (файли, category/channel) |
| 403 | Недостатньо прав (не OPERATOR) |
| 404 | Категорія або канал не знайдено |
| 422 | Відсутні обов'язкові поля |
| 500 | Помилка сервера |

## Помилки та рішення

### Помилка: "Only operators can create cases"

**Причина:** Користувач не має роль OPERATOR.

**Рішення:** Увійдіть під користувачем з роллю OPERATOR або створіть нового:

```python
# Створення operator через API (потрібен ADMIN)
POST /api/users
{
  "username": "operator1",
  "email": "operator1@example.com",
  "full_name": "Operator One",
  "password": "SecurePass123!",
  "role": "OPERATOR"
}
```

### Помилка: "Category with id '...' not found"

**Причина:** Невірний UUID категорії або категорія не існує.

**Рішення:** Отримайте список категорій:

```bash
GET /api/categories
```

### Помилка: "File '...' exceeds maximum size"

**Причина:** Файл більше 10MB.

**Рішення:** Стисніть файл або розділіть на частини.

### Помилка: "File type '...' not allowed"

**Причина:** Неприпустимий тип файлу.

**Рішення:** Конвертуйте файл в один з дозволених форматів:
- Документи: pdf, doc, docx, xls, xlsx
- Зображення: jpg, jpeg, png

## Залежності

### Виконані

- ✅ BE-002: JWT Authentication
- ✅ BE-003: Categories & Channels
- ✅ BE-004: Cases Model & CRUD
- ✅ BE-005: Attachments

### Часткові

- ⚠️ BE-013: Celery/Redis (структура готова, worker окремо)
- ⚠️ BE-014: SMTP (placeholder, буде реалізовано пізніше)

## Майбутні покращення

1. **Executor-Category Assignment**
   - Прив'язка виконавців до категорій
   - Нотифікації тільки відповідальних виконавців

2. **Attachment Previews**
   - Thumbnail для зображень
   - PDF preview в браузері

3. **Bulk Upload**
   - Підтримка ZIP архівів
   - Drag-and-drop у фронтенді

4. **Email Templates**
   - HTML шаблони нотифікацій
   - Персоналізація повідомлень

## Додаткова інформація

- 📄 [BE-006_IMPLEMENTATION_SUMMARY.md](../BE-006_IMPLEMENTATION_SUMMARY.md) - Детальна документація
- 📋 [PROJECT_STATUS.md](../../PROJECT_STATUS.md) - Загальний статус проекту
- 📝 [tasks/BE-006.md](../../tasks/BE-006.md) - Оригінальне завдання

## Підтримка

При виникненні проблем:

1. Перевірте логи API: `docker-compose logs api`
2. Перевірте логи Celery: `docker-compose logs worker`
3. Перевірте статус Redis: `docker-compose logs redis`
4. Запустіть тести: `.\scripts\test-be006.ps1`

---

**Статус:** ✅ COMPLETED  
**Дата:** October 28, 2025
