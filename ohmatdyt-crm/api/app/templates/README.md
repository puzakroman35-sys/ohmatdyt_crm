# Email Templates Documentation

## Огляд

Система email нотифікацій використовує Jinja2 для рендерингу професійних HTML шаблонів. Всі шаблони наслідуються від базового layout та мають responsive дизайн.

## Структура

```
app/templates/emails/
├── base.html           # Базовий layout з header, footer, CSS
├── new_case.html       # Нове звернення для виконавця
├── case_taken.html     # Справу взято в роботу
├── status_changed.html # Зміна статусу справи
├── new_comment.html    # Новий коментар
├── temp_password.html  # Тимчасовий пароль
├── reassigned.html     # Передача справи
└── escalation.html     # Ескалація (термінове)
```

## Base Template (base.html)

Містить:
- **Header**: Gradient background, логотип Ohmatdyt
- **CSS**: Inline styles для email-safe дизайну
- **Footer**: Copyright, контакти
- **Responsive**: Mobile-friendly з max-width 600px

### CSS Classes:

- `.container` - головний контейнер
- `.header` - синій gradient header
- `.content` - основний контент
- `.info-block` - блоки з інформацією (синій border)
- `.status-badge` - кольорові badges для статусів
  - `.status-new` - новий (синій)
  - `.status-in-progress` - в роботі (жовтий)
  - `.status-needs-info` - потрібна інфо (червоний)
  - `.status-done` - виконано (зелений)
  - `.status-rejected` - відхилено (сірий)
- `.comment-box` - блок для коментарів
- `.button` - CTA кнопки
- `.footer` - футер з інформацією

## Templates Usage

### 1. NEW_CASE (new_case.html)

**Коли відправляється**: При створенні нової справи

**Context variables**:
```python
{
    "executor_name": "Іванов Іван Іванович",
    "case_public_id": "123456",
    "category_name": "Консультація",
    "channel_name": "Телефон",
    "created_at": "29.10.2025 14:30",
    "applicant_name": "Петренко Марія",
    "applicant_phone": "+380501234567",  # optional
    "applicant_email": "maria@example.com",  # optional
    "description": "Текст звернення...",
    "subcategory": "Кардіологія",  # optional
}
```

**Приклад використання**:
```python
text, html = render_template("new_case", context)
send_email(
    to=executor.email,
    subject=f"Нове звернення #{case_public_id}",
    body_text=text,
    body_html=html,
)
```

### 2. CASE_TAKEN (case_taken.html)

**Коли відправляється**: Коли виконавець бере справу в роботу

**Context variables**:
```python
{
    "case_public_id": "123456",
    "executor_name": "Сидоренко Олена",
    "executor_email": "sidorenko@ohmatdyt.com",
    "taken_at": "29.10.2025 15:00",
    "category_name": "Консультація",
    "applicant_name": "Петренко Марія",
}
```

### 3. STATUS_CHANGED (status_changed.html)

**Коли відправляється**: При зміні статусу справи

**Context variables**:
```python
{
    "case_public_id": "123456",
    "old_status_display": "Нове",
    "new_status_display": "Виконано",
    "new_status": "DONE",  # NEW, IN_PROGRESS, NEEDS_INFO, DONE, REJECTED
    "new_status_class": "done",  # new, in-progress, needs-info, done, rejected
    "changed_at": "29.10.2025 16:00",
    "executor_name": "Сидоренко Олена",
    "status_comment": "Консультація надана",  # optional
    "category_name": "Консультація",
    "applicant_name": "Петренко Марія",
}
```

**Status Mapping**:
- `NEW` → "Нове", class: `new`
- `IN_PROGRESS` → "В роботі", class: `in-progress`
- `NEEDS_INFO` → "Потрібна інформація", class: `needs-info`
- `DONE` → "Виконано", class: `done`
- `REJECTED` → "Відхилено", class: `rejected`

### 4. NEW_COMMENT (new_comment.html)

**Коли відправляється**: При додаванні коментаря

**Context variables**:
```python
{
    "case_public_id": "123456",
    "author_name": "Коваленко Тетяна",
    "author_role": "Оператор",  # OPERATOR, EXECUTOR, ADMIN
    "is_internal": False,  # True для внутрішніх коментарів
    "created_at": "29.10.2025 17:00",
    "comment_text": "Текст коментаря...",
    "comment_type": "Публічний",  # or "Внутрішній"
    "category_name": "Консультація",
    "status_display": "В роботі",
    "status_class": "in-progress",
    "applicant_name": "Петренко Марія",
}
```

### 5. TEMP_PASSWORD (temp_password.html)

**Коли відправляється**: При створенні/скиданні паролю

**Context variables**:
```python
{
    "username": "newuser",
    "email": "newuser@ohmatdyt.com",
    "role_display": "Виконавець",  # Оператор, Виконавець, Адміністратор
    "temp_password": "TempPass123!",
}
```

### 6. REASSIGNED (reassigned.html)

**Коли відправляється**: При передачі справи іншому виконавцю

**Context variables**:
```python
{
    "case_public_id": "123456",
    "old_executor_name": "Іванов Іван",
    "new_executor_name": "Сидоренко Олена",
    "reassigned_at": "29.10.2025 18:00",
    "reassignment_reason": "Іванов в відпустці",  # optional
    "category_name": "Консультація",
    "status_display": "В роботі",
    "status_class": "in-progress",
    "applicant_name": "Петренко Марія",
}
```

### 7. ESCALATION (escalation.html)

**Коли відправляється**: При ескалації справи (прострочення)

**Context variables**:
```python
{
    "case_public_id": "123456",
    "escalation_reason": "Термін обробки перевищено більше ніж на 3 дні",
    "created_at": "25.10.2025 10:00",
    "escalated_at": "29.10.2025 10:00",
    "executor_name": "Іванов Іван",
    "status_display": "В роботі",
    "status_class": "in-progress",
    "days_overdue": 4,
    "category_name": "Консультація",
    "applicant_name": "Петренко Марія",
    "applicant_phone": "+380501234567",  # optional
    "description": "Текст звернення...",
}
```

## Automatic Context Variables

Всі шаблони автоматично отримують:
- `current_year` - поточний рік (для footer)
- `crm_url` - URL CRM системи (з .env)

## Template Customization

### Зміна кольорів:

У `base.html` можна змінити:
```css
/* Primary color (headers, buttons) */
background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);

/* Status colors */
.status-new { background-color: #e6f7ff; color: #0050b3; }
.status-in-progress { background-color: #fff7e6; color: #ad6800; }
.status-needs-info { background-color: #fff1f0; color: #a8071a; }
.status-done { background-color: #f6ffed; color: #135200; }
```

### Додавання нового шаблону:

1. Створіть новий файл у `app/templates/emails/your_template.html`
2. Наслідуйтесь від base:
   ```html
   {% extends "emails/base.html" %}
   
   {% block content %}
   <h2>Your Content Here</h2>
   {% endblock %}
   ```
3. Додайте text версію в `email_service.py` → `_generate_text_version()`
4. Використовуйте:
   ```python
   text, html = render_template("your_template", context)
   ```

## Testing Templates

### Візуальний тест:

Відкрийте HTML файл у браузері:
```bash
# Windows
start app/templates/emails/new_case.html

# Linux/Mac
xdg-open app/templates/emails/new_case.html
```

### Тест рендерингу:

```python
from app.email_service import render_template

context = {"executor_name": "Test", ...}
text, html = render_template("new_case", context)
print(html)
```

### Email client testing:

Відправте тестовий email собі:
```python
from app.email_service import send_email, render_template

text, html = render_template("new_case", test_context)
send_email(
    to="your@email.com",
    subject="Test Email",
    body_text=text,
    body_html=html,
)
```

## Production Checklist

- [ ] SMTP credentials налаштовані в .env
- [ ] CRM_URL вказує на production domain
- [ ] EMAILS_FROM_EMAIL використовує офіційний домен
- [ ] Протестовано у Gmail, Outlook, Apple Mail
- [ ] Mobile responsive перевірено
- [ ] Links працюють коректно
- [ ] Unsubscribe link додано (якщо потрібно)

## Troubleshooting

### Шаблон не рендериться:

- Перевірте чи існує файл у `app/templates/emails/`
- Перевірте syntax Jinja2 ({% %}, {{ }})
- Перевірте чи всі змінні передані в context

### Email виглядає поганно:

- Використовуйте inline CSS (не external stylesheets)
- Уникайте JavaScript
- Тестуйте в різних email клієнтах
- Використовуйте таблиці для layout (якщо потрібно)

### SMTP помилки:

- Перевірте credentials у .env
- Перевірте SMTP_PORT та TLS/SSL settings
- Дивіться логи: `docker-compose logs -f worker`
- Тестуйте з іншим SMTP провайдером

## References

- Jinja2 Documentation: https://jinja.palletsprojects.com/
- Email Design Best Practices: https://www.campaignmonitor.com/css/
- SMTP Testing: https://mailtrap.io/
