# Виправлення відображення категорії та каналу в таблиці звернень

## Проблема

На сторінці `/cases` в таблиці звернень для колонок "Категорія" та "Канал" відображалося "Невідомо", хоча при детальному перегляді звернення ці значення були присутні.

## Причина

API endpoints `/api/cases`, `/api/cases/my` та `/api/cases/assigned` повертали тільки базову схему `CaseResponse`, яка містила лише ID категорії (`category_id`) та каналу (`channel_id`), але не самі об'єкти `category` та `channel`.

Frontend компонент `cases.tsx` очікував вкладені об'єкти:
```typescript
render: (category: any) => category?.name || 'Невідомо'
render: (channel: any) => channel?.name || 'Невідомо'
```

Оскільки об'єкти були `undefined`, завжди відображалося "Невідомо".

## Рішення

### 1. Оновлено CRUD функцію (`api/app/crud.py`)

Додано імпорт `joinedload` та оновлено функцію `get_all_cases`:

```python
from sqlalchemy.orm import Session, joinedload

def get_all_cases(...):
    query = select(models.Case).options(
        joinedload(models.Case.category),
        joinedload(models.Case.channel),
        joinedload(models.Case.responsible)
    )
    # ... rest of the function
```

Це забезпечує завантаження пов'язаних об'єктів category, channel та responsible одним SQL запитом (eager loading).

### 2. Оновлено API endpoints (`api/app/routers/cases.py`)

Оновлено три endpoints для повернення вкладених об'єктів:

#### `/api/cases/my` (для операторів)
```python
case_responses = [
    schemas.CaseResponse(
        # ... existing fields ...
        category=schemas.CategoryResponse(...) if case.category else None,
        channel=schemas.ChannelResponse(...) if case.channel else None,
        responsible=schemas.UserResponse(...) if case.responsible else None
    )
    for case in cases
]
```

#### `/api/cases/assigned` (для виконавців)
Аналогічні зміни як для `/api/cases/my`

#### `/api/cases` (загальний список)
Аналогічні зміни як для `/api/cases/my`

### 3. Використовувана схема (`api/app/schemas.py`)

Схема `CaseResponse` вже містила опціональні поля для вкладених об'єктів:

```python
class CaseResponse(CaseBase):
    # ... other fields ...
    category: Optional[CategoryResponse] = None
    channel: Optional[ChannelResponse] = None
    author: Optional[UserResponse] = None
    responsible: Optional[UserResponse] = None
```

Тепер ці поля заповнюються правильними даними.

## Змінені файли

1. `ohmatdyt-crm/api/app/crud.py` - додано `joinedload` для завантаження пов'язаних об'єктів
2. `ohmatdyt-crm/api/app/routers/cases.py` - оновлено формування відповідей у трьох endpoints

## Результат

Після застосування змін:
- ✅ В таблиці звернень відображаються правильні назви категорій
- ✅ В таблиці звернень відображаються правильні назви каналів  
- ✅ В таблиці звернень відображається відповідальний виконавець (якщо призначений)
- ✅ Немає додаткових N+1 SQL запитів завдяки `joinedload`

## Тестування

1. Перезапустіть API контейнер:
   ```bash
   docker-compose restart api
   ```

2. Відкрийте http://localhost:3000/cases

3. Перевірте, що в колонках "Категорія" та "Канал" відображаються правильні значення замість "Невідомо"

## Дата виправлення
29 жовтня 2025
