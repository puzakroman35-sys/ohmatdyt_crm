# Technical Specification (TS)
## Система управління зверненнями НДСЛ «Охматдит»

Версія: 1.0  
Дата: 28 жовтня 2025  
Статус: Готово до декомпозиції на задачі

---

## 0. Мета документа

Надати інженерно-орієнтовану специфікацію на базі PRD і обраного стеку (Docker Compose, Django 5+, Django-Ninja, Celery, Redis, PostgreSQL, Next.js, Redux Toolkit, Ant Design, JWT), яка дозволяє:
- розбити роботу на ізольовані, паралельно виконувані задачі;
- забезпечити однозначність контрактів API та моделі даних;
- визначити нефункціональні вимоги і способи їх досягнення;
- описати інфраструктуру, деплой, тестування та CI/CD.

Примітки/припущення:
- Використовуємо ASGI-сервер Uvicorn для Django-Ninja.  
- Використовуємо кастомну Django-модель користувача (AbstractUser) з полем `role` (OPERATOR, EXECUTOR, ADMIN) і M2M до категорій для виконавців.  
- Зберігання файлів: локальна FS (MEDIA_ROOT) у dev/stage; S3-сумісне сховище — опційно у prod (не входить в MVP).  
- JWT зберігається у httpOnly-cookie (front) або використовується як Bearer-токен в заголовку (API-клієнти).  
- Ідентифікатор звернення — публічний 6-цифровий `public_id` (унікальний), окремо від внутрішнього PK.

---

## 1. Архітектура рішення

### 1.1. Компоненти
- Backend API: Django 5 + Django-Ninja (ASGI/Uvicorn)
- Task processing: Celery worker + Celery beat (планувальник)
- Message broker: Redis
- DB: PostgreSQL 15+
- Frontend: Next.js (TypeScript) + Redux Toolkit + Ant Design
- Reverse proxy: Nginx (prod) для TLS/HTTPS та маршрутизації
- SMTP: зовнішній або внутрішній поштовий сервер

### 1.2. Середовища
- Local (developer): docker-compose, hot reload
- Stage (optional): docker-compose/swarm/k8s; перевірка інтеграцій
- Prod: docker-compose на сервері або k8s; HTTPS через Nginx + Let’s Encrypt

### 1.3. Потоки даних (коротко)
- Frontend <-> Backend API (HTTPS, JWT)
- Backend -> Redis (черги для email/ескалацій)
- Celery Worker -> SMTP (відправка листів)
- Backend -> PostgreSQL (персистенція)
- Backend <-> Storage (MEDIA/S3) для вкладень

---

## 2. Модель даних (ERD-рівень)

Основні сутності та поля (типи — Django/SQL, обов’язковість, індекси):

### 2.1. User (кастомний)
- id: PK
- username: str, unique, idx
- password: hashed
- full_name: str, required
- email: str, unique, idx
- role: enum(OPERATOR|EXECUTOR|ADMIN), idx
- is_active: bool (деактивація користувача)
- executor_categories: M2M -> Category (для role=EXECUTOR)
- created_at: datetime, idx
- updated_at: datetime

Бізнес-правила:
- username унікальний; email унікальний; пароль — мін. 8 символів (літери+цифри).  
- При role=EXECUTOR — обов’язкові категорії (>=1).  

### 2.2. Category
- id: PK
- name: str, unique
- is_active: bool (деактивація)
- created_at: datetime
- updated_at: datetime

### 2.3. Channel
- id: PK
- name: str, unique
- is_active: bool
- created_at: datetime
- updated_at: datetime

### 2.4. Case (звернення)
- id: PK
- public_id: int(6), unique, idx (100000–999999)
- category: FK -> Category (required)
- subcategory: str | null (MVP як вільний текст; нормалізація — Phase 2)
- channel: FK -> Channel (required)
- applicant_name: str (дозволено «Відмова назвати»)
- applicant_phone: str | null
- applicant_email: str | null
- summary: text (суть звернення)
- status: enum(NEW|IN_PROGRESS|NEEDS_INFO|REJECTED|DONE), idx
- responsible: FK -> User (EXECUTOR) | null (призначається при взятті в роботу або перепризначенні)
- author: FK -> User (OPERATOR) (хто створив)
- created_at: datetime, idx(desc)
- updated_at: datetime
- due_flags: jsonb | null (опц., для обчислюваних станів, наприклад, overdue)

Індекси: (status, created_at), (category, status), (author), (responsible)

### 2.5. CaseStatusHistory
- id: PK
- case: FK -> Case (idx)
- from_status: enum | null (для першого переходу)
- to_status: enum
- comment: text | null (обов’язково для більшості переходів згідно PRD)
- changed_by: FK -> User
- changed_at: datetime, idx

### 2.6. CaseComment
- id: PK
- case: FK -> Case (idx)
- author: FK -> User
- text: text
- is_internal: bool (внутрішній коментар)
- created_at: datetime, idx

Видимість: 
- is_internal=false: Оператор (author), Відповідальний, Адмін
- is_internal=true: Виконавці тієї ж категорії, Адміністратори

### 2.7. CaseAttachment
- id: PK
- case: FK -> Case (idx)
- file: FileField (шлях до файлу)
- original_name: str
- size_bytes: int (<= 10MB)
- mime_type: str (обмеження формату)
- uploaded_by: FK -> User
- created_at: datetime

Правила: 
- Формати: pdf, doc, docx, xls, xlsx, jpg, jpeg, png; розмір ≤ 10MB/файл.

### 2.8. NotificationLog (опційно)
- id: PK
- case: FK -> Case | null
- type: enum(NEW_CASE|STATUS_CHANGED|COMMENT_PUBLIC|COMMENT_INTERNAL|REASSIGNED|ESCALATION)
- recipients: jsonb (список email/ids)
- payload: jsonb
- sent_at: datetime | null
- status: enum(SENT|FAILED|RETRY_SCHEDULED)
- error: text | null

---

## 3. API контракти (Django-Ninja)

### 3.1. Загальні принципи
- Base URL: `/api/v1`
- Auth: JWT (Bearer) або httpOnly-cookie; refresh токени підтримуються.
- Content-Type: `application/json` (для файлів — multipart/form-data)
- Пагінація: `page` (>=1), `page_size` (<=100, default 20)
- Сортування: `order_by` (наприклад, `-created_at`)
- Валідація і помилки: 400 (validation), 401 (unauth), 403 (forbidden), 404 (not found), 409 (conflict), 422 (unprocessable), 500 (server)

### 3.2. Auth
- POST `/auth/login`  
  Request: { username, password }  
  Response: { access, refresh, user: {id, username, full_name, email, role} }
- POST `/auth/refresh`  
  Request: { refresh }  
  Response: { access }
- POST `/auth/logout` (опц., блэкліст)

### 3.3. Users (ADMIN)
- GET `/users` (filters: role, is_active; sort; paginate)
- POST `/users` (create)  
  Body: { username, full_name, email, password, role, executor_category_ids?[] }
- GET `/users/{id}`
- PUT/PATCH `/users/{id}` (editable: full_name, email, role, executor_category_ids)
- POST `/users/{id}/deactivate`  
  Валідація: якщо EXECUTOR має активні кейси (IN_PROGRESS|NEEDS_INFO) — 409 з переліком кейсів.
- POST `/users/{id}/reset-password`  
  Response: { temp_password } (показати один раз) + email відправляється Celery’ю.

### 3.4. Categories (ADMIN)
- GET `/categories` (include_inactive?=bool)
- POST `/categories` { name }
- PUT `/categories/{id}` { name }
- POST `/categories/{id}/deactivate`
- POST `/categories/{id}/activate`

### 3.5. Channels (ADMIN)
- Аналогічно Categories: GET/POST/PUT/activate/deactivate

### 3.6. Cases
- POST `/cases` (OPERATOR) — створити  
  multipart/form-data: { category_id, channel_id, applicant_name, applicant_phone?, applicant_email?, subcategory?, summary, files[] }  
  Response: { public_id, status=NEW, ... }
- GET `/cases/my` (OPERATOR) — тільки свої (author=current)
- GET `/cases/assigned` (EXECUTOR) — ті, де відповідальний=current або належать до категорій виконавця (для перегляду до взяття)
- GET `/cases` (роль-залежно) — фільтри: status, category_id, channel_id, date_from, date_to, public_id, responsible_id, overdue=true/false
- GET `/cases/{public_id}` — повна картка, з історією/коментарями/вкладеннями (видимість за роллю)
- POST `/cases/{public_id}/take` (EXECUTOR) — взяти в роботу  
  Rules: тільки NEW; статус -> IN_PROGRESS; responsible=current
- POST `/cases/{public_id}/status` (EXECUTOR=responsible) — змінити статус  
  Body: { to_status: IN_PROGRESS|NEEDS_INFO|REJECTED|DONE, comment: required }
- POST `/cases/{public_id}/reassign` (ADMIN) — перепризначення  
  Body: { responsible_id } (з переліку EXECUTOR з доступом до категорії)
- POST `/cases/{public_id}/comments` (OPERATOR|EXECUTOR)  
  Body: { text, is_internal=false|true }  
  Rules: is_internal=true — лише EXECUTOR/ADMIN

### 3.7. Case Files
- POST `/cases/{public_id}/files` (OPERATOR|EXECUTOR) — додати файл (MVP — при створенні; опц. — після створення)
- GET `/cases/{public_id}/files/{file_id}` — скачати (RBAC + підписані URL у prod)

### 3.8. Dashboard (Phase 3, ADMIN)
- GET `/dashboard/summary?period=day|week|month|quarter|year&from&to`
- GET `/dashboard/status-distribution?from&to`
- GET `/dashboard/overdue-list`
- GET `/dashboard/executors-efficiency?from&to`
- GET `/dashboard/categories-top?limit=5&from&to`

---

## 4. RBAC: ролі та доступи

| Роль | Доступ до кейсів | Видимість коментарів | Адмін-функції |
|---|---|---|---|
| OPERATOR | Створює свої; бачить лише свої; читає призначеного відповідального | Публічні | — |
| EXECUTOR | Бачить у своїх категоріях; бере в роботу; змінює статус своїх | Публічні + внутрішні своєї категорії | — |
| ADMIN | Повний доступ | Усі | Користувачі, Категорії, Канали, Перепризначення |

HTTP 403 при спробі доступу поза роллю.

---

## 5. Бізнес-флоу (послідовності)

### 5.1. Створення звернення (OPERATOR)
1) Заповнення форми -> валідації -> збереження в БД з `public_id` (6 цифр, унік.)
2) Прикріплення файлів (<=10MB; типи дозволені)
3) Статус = NEW
4) Celery-таск надсилає email виконавцям відповідної категорії (<=1 хв.)

### 5.2. Взяття в роботу (EXECUTOR)
- Доступно лише для NEW 
- Встановлюється responsible=current; статус -> IN_PROGRESS 
- Email оператору-автору

### 5.3. Зміна статусу (EXECUTOR=responsible)
- Потрібний коментар
- Переходи: IN_PROGRESS -> NEEDS_INFO|REJECTED|DONE
- Email оператору-автору
- Блокування редагувань при DONE/REJECTED (крім коментарів)

### 5.4. Коментарі
- Публічний: бачать Оператор, Відповідальний, Адмін; email всім цим
- Внутрішній: бачать Виконавці цієї категорії + Адмін; email без Оператора

### 5.5. Перепризначення (ADMIN)
- Старому виконавцю — лист «знято»; новому — «призначено»; лог в історії

### 5.6. Ескалація (SYSTEM via Celery beat)
- Щодня знаходить NEW > 3 днів
- Надсилає листи усім Виконавцям категорії + усім Адмінам
- Прапорець overdue у відповіді списку (UI підсвічує рядок)

---

## 6. Нотифікації (Celery)

Типи листів і одержувачі:
- NEW_CASE: усі EXECUTOR категорії
- STATUS_CHANGED: OPERATOR-автор
- COMMENT_PUBLIC: OPERATOR + EXECUTOR-responsible (або всі причетні?) — мінімум ці двоє
- COMMENT_INTERNAL: EXECUTOR тієї ж категорії + ADMIN
- REASSIGNED: попередній EXECUTOR + новий EXECUTOR
- ESCALATION: усі EXECUTOR категорії + усі ADMIN

Технічні деталі:
- Канал: SMTP, HTML-шаблони (Jinja2/Django Templates)
- Ретрай: експоненційна затримка, max_retries=5
- SLA: поставити таск в чергу ≤ 1 хвилини від події

---

## 7. Валідації та обмеження

- Файли: розмір ≤ 10MB, тип у білому списку
- Case: category, channel, summary — обов’язково; applicant_name — може бути «Відмова назвати»
- Унікальність `public_id` з БД-констрейнтом
- Users: унікальні username та email, пароль полісі
- Рольові перевірки на кожному ендпоінті

---

## 8. Безпека

- HTTPS скрізь (Nginx в prod)
- JWT: короткоживучий access (15-30 хв), refresh (7-30 днів)
- Зберігання у httpOnly-cookie (front) + CSRF-захист для POST з cookie (double submit token) або Bearer-токен підхід (API-клієнти)
- CORS: дозволені origin-и env-конфігом
- Паролі: PBKDF2/bcrypt (Django default ок)
- Аудит: логування входів, змін статусів, перепризначень

---

## 9. Продуктивність

- Індекси: по status, created_at, category, responsible, author
- Пагінація: за замовчуванням 20, до 100
- N+1: селективні prefetch/select_related у списках/деталях
- Кешування (Phase 2/3): агрегати для дашборду

---

## 10. Журналювання і моніторинг

- Структуровані логи (JSON) у stdout контейнерів
- Аудит-доги змін статусу/відповідального
- Healthcheck ендпоінти: `/healthz` (API), ping до Redis/DB у worker’і
- Метрики (Phase 2/3): прометей/графана (не в MVP)

---

## 11. Деплой та інфраструктура (docker-compose)

Сервіси:
- `api`: Django (Uvicorn)  
  ENV: DB_*, REDIS_*, SMTP_*, JWT_*, MEDIA_ROOT, ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS
- `worker`: Celery worker
- `beat`: Celery beat
- `redis`: Redis
- `db`: PostgreSQL  
  Volumes: дані БД
- `frontend`: Next.js build/serve (prod) або dev server (local)
- `nginx`: рев. проксі + TLS (prod); статика, медіа через upstream

Томи: 
- db-data, media, static (опц.)

Секрети: 
- .env файли (docker secrets у prod)

Міграції: 
- `api` запускає `manage.py migrate` на старті

---

## 12. Тестування

- Backend: pytest + pytest-django; фабрики (factory_boy); тести API (happy/edge), RBAC, генерація public_id, валідації файлів, Celery таски (unit + інтеграція з Redis, SMTP-моки)
- Frontend: Vitest/Jest + React Testing Library; перевірка Guard/ACL, форм, фільтрів
- E2E: Playwright/Cypress — smoke на основні флоу MVP
- Покриття: ціль ≥ 80% для MVP

---

## 13. CI/CD (орієнтир)

- Гілки: `main`, `develop`, feature/*
- Перевірки PR: лінти (flake8/ruff, eslint), тести бек/фронт, build контейнерів
- Артефакти: образи `api`, `worker`, `beat`, `frontend`
- Deploy: stage → manual approve → prod

---

## 14. Frontend структура (Next.js + RTK + AntD)

Пропонована структура:
- `/app` або `/pages` (за обраним маршрутизатором)
  - `/login`
  - `/cases`
    - список (для різних ролей — фільтри та колонки)
  - `/cases/[public_id]` (картка)
  - `/admin/users`
  - `/admin/categories`
  - `/admin/channels`
  - `/dashboard` (Phase 3)
- `/components`: форми, таблиці, фільтри, статус-бейджі
- `/store` (RTK): `authSlice`, `casesSlice`, `usersSlice`, `categoriesSlice`, `channelsSlice`
- `/services` (API клієнти, fetcher з токеном, обробка refresh)
- Guard/HOC для ролей; збереження фільтрів у URL/state; колір для overdue рядків

---

## 15. Шаблони email (заголовки з PRD)

- NEW_CASE: "Нове звернення [ID] в категорії [Назва]"
- STATUS_CHANGED: "Звернення [ID]: статус змінено на [Новий статус]"
- COMMENT: "Новий коментар до звернення [ID]" (тип позначити)
- REASSIGNED: повідомлення попередньому/новому виконавцю
- ESCALATION: "Нагадування: звернення [ID] очікує на опрацювання"

---

## 16. Міграції статусів (state machine)

- NEW -> IN_PROGRESS (take)
- IN_PROGRESS -> NEEDS_INFO | REJECTED | DONE (з коментарем)
- Блокування редагування після DONE/REJECTED (коментувати можна)

Перевірки: 
- Тільки відповідальний може змінювати статус у своїх кейсах
- Логи в CaseStatusHistory з автором і коментарем

---

## 17. Обробка вкладень

- Перевірка типів/розміру на бекенді
- Зберігання на файловій системі (MEDIA_ROOT) з унікальною ієрархією `/cases/{public_id}/...`
- Антивірус/сканер — поза MVP (Phase 2/3)

---

## 18. Конфігурація середовищ (приклад змінних)

- DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS
- REDIS_URL
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_USE_TLS
- JWT_ACCESS_TTL_MIN, JWT_REFRESH_TTL_DAYS, JWT_SECRET
- MEDIA_ROOT, MAX_UPLOAD_MB=10, ALLOWED_FILE_TYPES
- CORS_ALLOWED_ORIGINS, CSRF_TRUSTED_ORIGINS, ALLOWED_HOSTS

---

## 19. Декомпозиція задач (беклог для планування)

Позначення: BE-* (Backend), FE-* (Frontend), INF-* (Infra/DevOps), QA-* (Тестування).

### 19.1. Фаза 1 (MVP)

- BE-001: Ініціалізація Django-проєкту, кастомний User (AbstractUser) з `role`, `full_name`, унікальний email
- BE-002: JWT (ninja-jwt), login/refresh/logout, httpOnly-cookie опційно, CORS/CSRF налаштування
- BE-003: Моделі Category/Channel з CRUD (admin API), валідація унікальності, (де)активація
- BE-004: Модель Case + генератор унікального `public_id` (6-цифр) + індекси
- BE-005: Валідація файлів (типи/розмір), завантаження у MEDIA_ROOT, модель Attachment
- BE-006: Ендпоінт створення звернення (multipart), статус NEW, email-тригер Celery
- BE-007: Списки звернень з фільтрами (оператор — свої; виконавець — свої категорії; адмін — всі)
- BE-008: Детальна картка звернення з історією, коментарями, файлами (RBAC)
- BE-009: Взяття в роботу (take): статус -> IN_PROGRESS, responsible=current, історія, email оператору
- BE-010: Зміна статусу (IN_PROGRESS -> NEEDS_INFO|REJECTED|DONE), обов’язковий коментар, історія, email
- BE-011: Публічні/внутрішні коментарі, видимість за роллю, email-розсилка правил
- BE-012: Управління користувачами (ADMIN): create/update, reset password (temp), deactivate (перевірка активних кейсів)
- BE-013: Celery/Redis інтеграція: воркер + таски для email; ретраї; лог нотифікацій
- BE-014: SMTP інтеграція; шаблони HTML листів
- BE-015: Healthcheck `/healthz` (DB/Redis ping), базове логування

- FE-001: Скелет Next.js + AntD + RTK, базове темування, верстка лейауту
- FE-002: Аутентифікація: форма логіну, збереження токенів, guard’и за ролями
- FE-003: Створення звернення: форма з валідаціями, завантаження файлів
- FE-004: Список «Мої звернення» (оператор), сортування/пагінація/автообновлення статусу
- FE-005: Списки для виконавця (по категоріях), підсвітка overdue (блідо-червоний)
- FE-006: Детальна картка: поля, файли, історія, коментарі (з чекбоксом внутрішнього)
- FE-007: Дії виконавця: «Взяти в роботу», «Зміна статусу» з обов’язковим коментарем
- FE-008: Адмін розділ: користувачі (список, create/edit, deactivate, reset-password)
- FE-009: Адмін розділ: категорії/канали (CRUD, (де)активація)

- INF-001: docker-compose (api, worker, beat, redis, db, frontend, nginx), мережі та томи
- INF-002: Налаштування .env, секретів, volume для media/db
- INF-003: Nginx конфіг prod (HTTPS, проксі до API/FE), Let’s Encrypt інтеграція (опц.)

- QA-001: Тест-план MVP; чек-листи; покриття бек/фронт ≥80%
- QA-002: E2E smoke: логін → створення звернення → взяття → зміна статусу → коментар

### 19.2. Фаза 2

- BE-201: Фільтрація за всіма полями (AND), збереження вибору (сервер/клієнт)
- BE-202: Внутрішні коментарі — розсилки тільки виконавцям та адмінам
- BE-203: Перепризначення кейсу (ADMIN) + email old/new
- BE-204: Щоденна ескалація Celery beat (>3 днів у NEW), вибірка отримувачів
- BE-205: Нормалізація підкатегорій (окрема таблиця) — за потреби

- FE-201: UI фільтрів (AND), збереження стану між переходами
- FE-202: Перепризначення з автопідказкою по виконавцях категорії
- FE-203: Віджети помірної аналітики (прострочені на списках)

- INF-201: Логи у JSON, агрегація (ELK/EFK) — орієнтир
- QA-201: Розширені інтеграційні тести Celery/SMTP

### 19.3. Фаза 3 (дашборди)

- BE-301: Статистика/агрегати ендпоінтів дашборду, індексація/кеш
- FE-301: Дашборд: summary, status pie, overdue list, executors table, categories bar
- QA-301: Перф-тести списків (до 1000 записів ≤ 2 c), картки (≤1 c)

---

## 20. Критерії приймання технічної частини (green)

- API відповідає контрактам, валідації і RBAC працюють
- Черги email стабільні: ≤1 хв на постановку, ретраї виконуються
- Експорт/зберігання файлів з обмеженнями формату/розміру
- Показники продуктивності з PRD досягнені на обсязі 1000 записів (локально — орієнтовно)
- Тести (бек/фронт/E2E) ≥ 80% покриття для MVP

---

## 21. Додатки

- Словник статусів і їх локалізації (UA): NEW=«Нове», IN_PROGRESS=«В роботі», NEEDS_INFO=«Потребує уточнення», REJECTED=«Відхилено», DONE=«Завершено»
- Візуальні підказки UI: бейджі статусів, підсвітка overdue
- Майбутні інтеграції: S3, Prometheus/Grafana, SSO (не в MVP)
