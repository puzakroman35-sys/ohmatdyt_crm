# BE-006: Create Case (multipart) + Email Trigger - Implementation Summary

**Task:** BE-006  
**Date Completed:** October 28, 2025  
**Status:** ✅ COMPLETED

---

## Overview

Реалізовано ендпоінт створення звернення (case) оператором з підтримкою завантаження файлів через multipart/form-data та автоматичним тригером email-нотифікації для виконавців категорії.

---

## Implemented Components

### 1. Cases Router (`app/routers/cases.py`)

Створено новий роутер з наступними ендпоінтами:

#### `POST /api/cases` - Create Case with Attachments
- **Method:** POST
- **Content-Type:** multipart/form-data
- **Authentication:** Required (JWT)
- **Authorization:** OPERATOR role only

**Form Fields:**
- **Required:**
  - `category_id` (string/UUID) - ID категорії
  - `channel_id` (string/UUID) - ID каналу звернення
  - `applicant_name` (string, 1-200 chars) - Ім'я заявника
  - `summary` (string, min 1 char) - Опис звернення

- **Optional:**
  - `subcategory` (string, max 200 chars) - Підкатегорія
  - `applicant_phone` (string, max 50 chars) - Телефон заявника
  - `applicant_email` (string) - Email заявника
  - `files[]` (array of files) - Прикріплені файли

**Response:**
```json
{
  "id": "uuid",
  "public_id": 123456,
  "status": "NEW",
  "category_id": "uuid",
  "channel_id": "uuid",
  "applicant_name": "Іван Петренко",
  "applicant_phone": "+380501234567",
  "applicant_email": "ivan@example.com",
  "summary": "Опис звернення",
  "subcategory": "Підкатегорія",
  "author_id": "uuid",
  "responsible_id": null,
  "created_at": "2025-10-28T10:00:00Z",
  "updated_at": "2025-10-28T10:00:00Z"
}
```

**Validation:**
- Category must exist and be active
- Channel must exist and be active
- File types: pdf, doc, docx, xls, xlsx, jpg, jpeg, png
- File size: Maximum 10MB per file
- Phone: Minimum 9 digits (if provided)
- Email: Valid email format (if provided)

**Error Responses:**
- `400 Bad Request` - Invalid category/channel, file validation failed
- `403 Forbidden` - Not an OPERATOR
- `422 Unprocessable Entity` - Missing required fields, validation errors

#### `GET /api/cases/{case_id}` - Get Case by ID
- **Method:** GET
- **Authentication:** Required (JWT)
- **Authorization:** 
  - OPERATOR: Can view own cases
  - EXECUTOR/ADMIN: Can view all cases

#### `GET /api/cases` - List Cases
- **Method:** GET
- **Authentication:** Required (JWT)
- **Query Parameters:**
  - `skip` (int, default 0) - Pagination offset
  - `limit` (int, default 50, max 100) - Page size
  - `status` (CaseStatus) - Filter by status
  - `category_id` (UUID) - Filter by category
  - `channel_id` (UUID) - Filter by channel

**RBAC:**
- OPERATOR: Lists only own cases
- EXECUTOR/ADMIN: Lists all cases

---

### 2. File Upload Processing

**Implementation Details:**

1. **Validation:**
   - File type checked by extension and MIME type
   - File size checked before saving
   - Filename sanitized to prevent directory traversal

2. **Storage:**
   - Path: `MEDIA_ROOT/cases/{public_id}/{uuid}_{filename}`
   - UUID prefix added to prevent filename collisions
   - Directories created automatically

3. **Transaction Safety:**
   - If file save fails, case is deleted (rollback)
   - If attachment DB record fails, file is deleted

4. **Multiple Files:**
   - Supports uploading multiple files in one request
   - Each file validated independently
   - Errors reported with filename context

---

### 3. Email Notification System

#### Celery Task: `send_new_case_notification`

**Location:** `app/celery_app.py`

**Implementation:**
```python
@celery.task(
    name="app.celery_app.send_new_case_notification",
    bind=True,
    max_retries=5,
    default_retry_delay=60
)
def send_new_case_notification(self, case_id: str, case_public_id: int, category_id: str):
    # Retrieves case and category details
    # Gets all executors (EXECUTOR/ADMIN roles)
    # Sends email notifications (placeholder)
    # Retries on failure with exponential backoff
```

**Features:**
- **Retry Mechanism:** Up to 5 retries with exponential backoff (60s, 120s, 240s, 480s, 960s)
- **Error Handling:** Exceptions logged and retried
- **Executor Selection:** Currently gets all active EXECUTOR/ADMIN users (will be enhanced for category-specific executors)

**Notification Flow:**
1. Case created successfully
2. Task queued with `send_new_case_notification.delay(case_id, public_id, category_id)`
3. Task picks up notification from Redis queue
4. Retrieves case, category, and executor information
5. Logs notification details (placeholder for actual email)
6. Returns success or retries on error

**Current Implementation:**
- Logs notification to console
- Placeholder for actual SMTP email sending
- Full SMTP integration will be implemented in BE-014

---

### 4. CRUD Enhancements

#### `delete_case(db, case_id)` - Added in `app/crud.py`
```python
async def delete_case(db: Session, case_id: UUID) -> bool:
    """
    Delete case by ID (hard delete).
    Note: This will cascade delete all attachments.
    """
```

**Purpose:** Used for rollback when file upload fails during case creation.

#### `get_executors_for_category(db, category_id)` - Added in `app/crud.py`
```python
async def get_executors_for_category(db: Session, category_id: UUID) -> list[models.User]:
    """
    Get all active executors (users with EXECUTOR or ADMIN role).
    
    Note: In the future, this can be enhanced to filter by category assignment.
    For now, returns all active executors.
    """
```

**Current Behavior:** Returns all active users with EXECUTOR or ADMIN role.  
**Future Enhancement:** Will filter by category assignment (requires category-executor relationship table).

---

### 5. Integration with Main Application

**Changes in `app/main.py`:**
```python
from app.routers import auth, categories, channels, attachments, cases

# Include routers
app.include_router(cases.router)
```

Cases router now registered and available at `/api/cases/*`.

---

## Test Suite

**File:** `api/test_be006.py`

### Test Cases

#### 1. Happy Path: Create Case with 2 Files
- Creates case with valid data
- Uploads 2 PDF files
- Verifies status=NEW
- Checks public_id generated
- Measures response time (should be < 60s for notification queuing)

#### 2. Validation: Missing Required Fields
- Tests missing `category_id` → 422 error
- Tests missing `applicant_name` → 422 error
- Verifies proper error messages

#### 3. Validation: Invalid File Type
- Uploads `.exe` file
- Expects 400 error
- Verifies error message mentions file type

#### 4. Validation: Oversized File
- Uploads 11MB file
- Expects 400 error
- Verifies error message mentions file size

### Running Tests

```bash
# From api directory
python test_be006.py
```

**Prerequisites:**
- API server running at `http://localhost:8000`
- Admin user credentials in environment or defaults
- Database with categories and channels tables

---

## API Usage Examples

### Example 1: Create Case with Files (cURL)

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
  -F "files=@document1.pdf" \
  -F "files=@photo.jpg"
```

### Example 2: Create Case without Files (Python)

```python
import requests

url = "http://localhost:8000/api/cases"
headers = {"Authorization": f"Bearer {operator_token}"}
data = {
    "category_id": "550e8400-e29b-41d4-a716-446655440000",
    "channel_id": "660e8400-e29b-41d4-a716-446655440000",
    "applicant_name": "Марія Коваленко",
    "summary": "Запит на консультацію"
}

response = requests.post(url, headers=headers, data=data)
case = response.json()
print(f"Case created: {case['public_id']}")
```

### Example 3: Create Case with Files (Python)

```python
import requests

url = "http://localhost:8000/api/cases"
headers = {"Authorization": f"Bearer {operator_token}"}
data = {
    "category_id": "550e8400-e29b-41d4-a716-446655440000",
    "channel_id": "660e8400-e29b-41d4-a716-446655440000",
    "applicant_name": "Петро Сидоренко",
    "applicant_phone": "+380671234567",
    "summary": "Технічна проблема"
}
files = [
    ('files', ('document.pdf', open('document.pdf', 'rb'), 'application/pdf')),
    ('files', ('screenshot.png', open('screenshot.png', 'rb'), 'image/png'))
]

response = requests.post(url, headers=headers, data=data, files=files)
case = response.json()
print(f"Case created: {case['public_id']}")
```

---

## Definition of Done (DoD) Checklist

- ✅ Успішне створення повертає `{ public_id, status=NEW, ... }`
- ✅ Файли прикріплюються і зберігаються з валідацією типу та розміру
- ✅ Нотифікація ставиться у чергу ≤ 1 хв після створення
- ✅ Валідаційні помилки: відсутні обов'язкові поля → 422
- ✅ Валідаційні помилки: недопустимий файл → 400
- ✅ Happy-path тест: створення з 1-2 файлами
- ✅ Тести для всіх валідаційних сценаріїв

---

## Dependencies

### Completed
- ✅ BE-002: JWT Authentication
- ✅ BE-003: Categories & Channels
- ✅ BE-004: Cases Model & CRUD
- ✅ BE-005: Attachments (File Upload)

### Partial
- ⚠️ BE-013: Celery/Redis Integration
  - Task structure implemented
  - Retry mechanism configured
  - Full worker setup in BE-013
  
- ⚠️ BE-014: SMTP Integration
  - Email sending is placeholder (console logs)
  - Full SMTP implementation in BE-014

---

## Known Limitations

1. **Email Notifications:**
   - Currently logs to console instead of sending actual emails
   - Full SMTP integration pending (BE-014)

2. **Executor Selection:**
   - Returns all active EXECUTOR/ADMIN users
   - Category-specific executor assignment not yet implemented
   - Requires executor-category relationship table (future enhancement)

3. **File Rollback:**
   - If case creation fails after files uploaded, orphaned files may remain
   - Implemented cleanup on attachment DB failure
   - Additional cleanup mechanisms may be needed

4. **Celery Worker:**
   - Must be running separately for notifications
   - Worker configuration in BE-013

---

## Future Enhancements

1. **Category-Executor Assignment:**
   - Create `executor_categories` table
   - Link executors to specific categories
   - Filter notifications by category assignment

2. **Notification Preferences:**
   - User preference for email notifications
   - Notification frequency settings
   - Digest vs. real-time notifications

3. **File Preview:**
   - Thumbnail generation for images
   - PDF preview in browser
   - File type icons

4. **Bulk Upload:**
   - Support for ZIP archives
   - Drag-and-drop file upload in frontend
   - Progress tracking for large files

---

## Related Files

### Created
- `api/app/routers/cases.py` - Cases endpoints
- `api/test_be006.py` - Test suite
- `BE-006_IMPLEMENTATION_SUMMARY.md` - This document

### Modified
- `api/app/main.py` - Added cases router
- `api/app/celery_app.py` - Added notification task
- `api/app/crud.py` - Added delete_case and get_executors_for_category
- `PROJECT_STATUS.md` - Updated status

### Existing (Used)
- `api/app/models.py` - Case and Attachment models
- `api/app/schemas.py` - Case and Attachment schemas
- `api/app/utils.py` - File validation utilities
- `api/app/database.py` - Database session
- `api/app/dependencies.py` - Authentication dependencies

---

## Conclusion

BE-006 успішно імплементовано з повною підтримкою:
- ✅ Multipart створення звернень
- ✅ Завантаження та валідація файлів
- ✅ RBAC контроль (тільки OPERATOR)
- ✅ Email тригер через Celery
- ✅ Retry механізм з експоненційною затримкою
- ✅ Комплексний тест-сьют

Система готова до інтеграції з фронтендом та подальшого розвитку функціоналу нотифікацій у BE-013 та BE-014.
