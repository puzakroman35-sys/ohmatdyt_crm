# BE-201: Розширена фільтрація звернень

## Швидкий старт

### Запуск тестів

```bash
# Запустіть Docker контейнери
docker-compose up -d

# Запустіть тестовий скрипт
python ohmatdyt-crm/test_be201.py
```

## Нові можливості

### 8 нових параметрів фільтрації:

1. **subcategory** - Фільтр по підкатегорії
2. **applicant_name** - Пошук по імені заявника (LIKE)
3. **applicant_phone** - Пошук по телефону (LIKE)
4. **applicant_email** - Пошук по email (LIKE)
5. **updated_date_from** - Дата оновлення від (ISO)
6. **updated_date_to** - Дата оновлення до (ISO)
7. **statuses** - Множинний вибір статусів (через кому)
8. **category_ids** - Множинний вибір категорій (через кому)
9. **channel_ids** - Множинний вибір каналів (через кому)

## Приклади використання

### Базовий пошук по заявнику

```bash
GET /api/cases?applicant_name=Іванов
```

### Множинний вибір статусів

```bash
GET /api/cases?statuses=NEW,IN_PROGRESS,NEEDS_INFO
```

### Комбінація фільтрів (AND логіка)

```bash
GET /api/cases?status=IN_PROGRESS&category_id={uuid}&applicant_name=Петров
```

### Складний запит

```bash
GET /api/cases?statuses=NEW,IN_PROGRESS&category_ids={uuid1},{uuid2}&applicant_email=gmail.com&limit=20&order_by=-created_at
```

## Логіка фільтрації

- **AND** - між різними типами фільтрів
- **OR** - всередині множинних параметрів (statuses, category_ids, channel_ids)

## Детальна документація

Дивіться: [BE-201_IMPLEMENTATION_SUMMARY.md](./BE-201_IMPLEMENTATION_SUMMARY.md)

## API документація

Swagger UI: http://localhost/docs

## Статус

✅ PRODUCTION READY (100%)
