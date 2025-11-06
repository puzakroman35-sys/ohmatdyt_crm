# Виправлення фільтра пошуку на сторінках користувачів та справ

## Проблема
На сторінках `http://localhost:3000/users` та `http://localhost:3000/cases` не працював фільтр пошуку.

## Причина
Проблема полягала в тому, що при введенні тексту в поле пошуку:
1. Значення зберігалося в `filters.search`
2. React не коректно відслідковував зміни об'єкта `filters` через референційну рівність
3. Не було debounce для оптимізації кількості запитів до API

## Виправлення

### Файл: `frontend/src/pages/users.tsx` та `frontend/src/pages/cases.tsx`

Виправлення застосовані до обох сторінок.

#### Для сторінки користувачів (`users.tsx`):

#### 1. Додано окремий стан для інпута з debounce

```tsx
// Локальний стан для пошуку (з debounce)
const [searchInput, setSearchInput] = useState('');
```

#### 2. Додано useEffect для debounce

```tsx
// Debounce для пошуку
useEffect(() => {
  const timer = setTimeout(() => {
    setFilters((prev) => ({ ...prev, search: searchInput }));
    // Скидаємо пагінацію при зміні пошуку
    if (searchInput !== filters.search) {
      setPagination((prev) => ({ ...prev, current: 1 }));
    }
  }, 500); // Затримка 500мс

  return () => clearTimeout(timer);
}, [searchInput]);
```

#### 3. Оновлено useEffect для завантаження даних

```tsx
// Завантаження при монтажі та зміні фільтрів
useEffect(() => {
  if (hasAccess) {
    loadUsers();
  }
}, [hasAccess, pagination.current, pagination.pageSize, sorter, filters.role, filters.is_active, filters.search]);
```

#### 4. Оновлено Input компонент

```tsx
<Input
  placeholder="Пошук за ПІБ, логіном або email..."
  prefix={<SearchOutlined />}
  value={searchInput}
  onChange={(e) => setSearchInput(e.target.value)}
  allowClear
  onClear={() => setSearchInput('')}
/>
```

#### 5. Додано скидання пагінації при зміні фільтрів

```tsx
// Для ролі
onChange={(value) => {
  setFilters((prev) => ({ ...prev, role: value }));
  setPagination((prev) => ({ ...prev, current: 1 }));
}}

// Для статусу
onChange={(value) => {
  setFilters((prev) => ({ ...prev, is_active: value }));
  setPagination((prev) => ({ ...prev, current: 1 }));
}}
```

#### 6. Оновлено кнопку очищення фільтрів

```tsx
<Button
  icon={<ReloadOutlined />}
  onClick={() => {
    setSearchInput('');
    setFilters({
      role: undefined,
      is_active: undefined,
      search: '',
    });
    setPagination((prev) => ({ ...prev, current: 1 }));
  }}
  block
>
  Очистити фільтри
</Button>
```

## Переваги нового рішення

1. **Debounce**: Запити до API відправляються лише через 500мс після останнього введення символу
2. **Оптимізація**: Зменшення кількості непотрібних запитів до сервера
3. **UX**: Плавніша робота інтерфейсу без підвисань
4. **Пагінація**: Автоматичне повернення до першої сторінки при зміні фільтрів
5. **Правильне відслідковування**: React коректно реагує на зміни фільтрів

## Тестування

### Запуск тестового скрипта

```bash
python test_users_search.py
```

### Ручне тестування

**Сторінка користувачів (`/users`):**

1. Відкрийте `http://localhost:3000/users`
2. Введіть текст у поле "Пошук за ПІБ, логіном або email..."
3. Почекайте 500мс - список користувачів має оновитися
4. Спробуйте різні пошукові терміни:
   - ПІБ користувача
   - Email
   - Логін (username)
5. Перевірте роботу з іншими фільтрами (роль, статус)
6. Натисніть "Очистити фільтри" - всі фільтри мають скинутися

**Сторінка справ (`/cases`):**

1. Відкрийте `http://localhost:3000/cases`
2. Введіть текст у поле "Пошук за іменем або ID..."
3. Почекайте 500мс - список справ має оновитися
4. Спробуйте різні пошукові терміни:
   - Ім'я заявника
   - ID справи
5. Перевірте роботу з іншими фільтрами (статус, категорія, дата)
6. Натисніть "Очистити" - всі фільтри мають скинутися

## Backend API

Backend вже підтримував параметр `search`:

```python
@router.get("", response_model=schemas.UserListResponse)
async def list_users(
    search: Optional[str] = Query(None, description="Search by username, email, or full_name"),
    # ... інші параметри
):
    # Пошук відбувається через CRUD функцію
    users, total = crud.get_users(
        db=db,
        search=search,
        # ... інші параметри
    )
```

CRUD функція виконує пошук (case-insensitive):

```python
if search:
    search_filter = or_(
        models.User.username.ilike(f"%{search}%"),
        models.User.email.ilike(f"%{search}%"),
        models.User.full_name.ilike(f"%{search}%")
    )
    query = query.where(search_filter)
```

## Дата виправлення
06.11.2025
