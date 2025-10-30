# BE-017: Розширені права адміністратора

## Опис

Реалізація повного доступу адміністратора до всіх звернень з можливістю редагування полів, зміни статусів та управління відповідальними виконавцями.

## Нові API Endpoints

### 1. PATCH /api/cases/{case_id}
**Редагування полів звернення (ADMIN only)**

**Доступні поля:**
- `category_id` - Зміна категорії
- `subcategory` - Зміна підкатегорії
- `channel_id` - Зміна каналу
- `applicant_name` - Редагування імені заявника
- `applicant_phone` - Редагування телефону
- `applicant_email` - Редагування email
- `summary` - Редагування опису звернення

**Приклад запиту:**
```bash
curl -X PATCH http://localhost/api/cases/{case_id} \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "Новий Заявник",
    "applicant_email": "new@example.com"
  }'
```

### 2. PATCH /api/cases/{case_id}/assign
**Призначення/зняття відповідального (ADMIN only)**

**Request Body:**
```json
{
  "assigned_to_id": "executor-uuid"  // або null для зняття
}
```

**Приклад призначення:**
```bash
curl -X PATCH http://localhost/api/cases/{case_id}/assign \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"assigned_to_id": "executor-uuid"}'
```

**Приклад зняття:**
```bash
curl -X PATCH http://localhost/api/cases/{case_id}/assign \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"assigned_to_id": null}'
```

### 3. POST /api/cases/{case_id}/status (Розширено)
**Зміна статусу з розширеними правами для ADMIN**

**ADMIN може:**
- Змінювати статус без перевірки на відповідального
- Змінювати статус з будь-якого в будь-який
- Повертати звернення зі статусу DONE/REJECTED в NEW

**Приклад повернення в NEW:**
```bash
curl -X POST http://localhost/api/cases/{case_id}/status \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to_status": "NEW",
    "comment": "Повторний розгляд необхідний"
  }'
```

## RBAC Правила

| Endpoint | ADMIN | EXECUTOR | OPERATOR |
|----------|-------|----------|----------|
| PATCH /cases/{id} | ✅ | ❌ 403 | ❌ 403 |
| PATCH /cases/{id}/assign | ✅ | ❌ 403 | ❌ 403 |
| POST /cases/{id}/status | ✅ (без обмежень) | ✅ (обмеження) | ❌ 403 |

## Валідації

### Редагування полів
- Email: валідний формат EmailStr
- Телефон: мінімум 9 цифр
- Категорія: повинна існувати та бути активною
- Канал: повинен існувати та бути активним

### Призначення виконавця
- Користувач повинен існувати
- Роль: EXECUTOR або ADMIN
- Статус: is_active = true

## Автоматична зміна статусів

### При призначенні виконавця
```
assigned_to_id = executor_uuid
→ status = IN_PROGRESS (якщо був NEW)
→ StatusHistory запис
```

### При знятті виконавця
```
assigned_to_id = null
→ status = NEW
→ StatusHistory запис
```

## Логування

Всі зміни логуються в таблицю `status_history`:

```python
{
  "id": "uuid",
  "case_id": "case-uuid",
  "old_status": "IN_PROGRESS",
  "new_status": "DONE",
  "changed_by_id": "admin-uuid",
  "created_at": "2025-10-30T12:00:00"
}
```

## Тестування

Запуск тестів:
```bash
cd ohmatdyt-crm
python test_be017.py
```

**Тестові сценарії:**
- ✅ ADMIN редагує поля звернення
- ✅ ADMIN призначає виконавця
- ✅ ADMIN знімає виконавця
- ✅ ADMIN змінює статус без обмежень
- ✅ ADMIN повертає звернення в NEW
- ✅ RBAC перевірки (OPERATOR/EXECUTOR отримують 403)
- ✅ Валідації (email, категорії)

## Помилки

### 403 Forbidden
```json
{
  "detail": "Access denied. Admin privileges required."
}
```

### 400 Bad Request (валідація)
```json
{
  "detail": "value is not a valid email address"
}
```

### 400 Bad Request (неіснуюча категорія)
```json
{
  "detail": "Category with id '...' not found"
}
```

### 404 Not Found
```json
{
  "detail": "Case with id '...' not found"
}
```

## Документація

- **Implementation Summary:** [BE-017_IMPLEMENTATION_SUMMARY.md](./BE-017_IMPLEMENTATION_SUMMARY.md)
- **Project Status:** [PROJECT_STATUS.md](../PROJECT_STATUS.md)
- **Task Definition:** [tasks/BE-017.md](../tasks/BE-017.md)

## Статус

✅ **PRODUCTION READY** - Всі функції протестовані та готові до використання
