# FE-001: Next.js Skeleton + Ant Design + Redux Toolkit

**Status:** ✅ COMPLETED  
**Date:** October 28, 2025

## Опис

Створено базовий скелет фронтенд-додатку з Next.js 14, Ant Design 5 і Redux Toolkit для глобального стейт-менеджменту.

## Створені компоненти

### 1. Redux Store

**`src/store/index.ts`**
- Налаштований Redux store з TypeScript
- Підключені reducers: auth, cases
- Експортовані типи RootState і AppDispatch

**`src/store/slices/authSlice.ts`**
- Управління станом автентифікації
- Actions: login, logout, updateTokens
- Стан: user, accessToken, refreshToken, isLoading, error

**`src/store/slices/casesSlice.ts`**
- Управління станом звернень
- Actions: fetchCases, fetchCase, createCase, updateCase
- Стан: cases, currentCase, pagination, loading, error

**`src/store/hooks.ts`**
- Typed hooks: useAppDispatch, useAppSelector

### 2. Theme & Config

**`src/config/theme.ts`**
- Кастомна тема Ant Design
- Українська локалізація (uk_UA)
- Темна тема для сайдбару
- Налаштування компонентів (Layout, Menu, Button, Input, etc.)

### 3. Layout

**`src/components/Layout/MainLayout.tsx`**
- Головний layout з sidebar, header, content
- Навігаційне меню:
  - Головна
  - Звернення
  - Адміністрування (користувачі, категорії, канали)
- Профіль користувача з dropdown меню
- Сповіщення (іконка)
- Згортання/розгортання sidebar

### 4. Pages

**`src/pages/_app.tsx`**
- Redux Provider
- Ant Design ConfigProvider
- Глобальні стилі

**`src/pages/login.tsx`**
- Форма входу (email + password)
- Валідація
- Інтеграція з API
- Error handling

**`src/pages/dashboard.tsx`**
- Головна панель
- Статистичні картки:
  - Всього звернень
  - В роботі
  - Потребують інформації
  - Завершено
- Останні звернення (TODO)

## Технологічний стек

- **Next.js:** 14.2.33
- **React:** 18.2.0
- **TypeScript:** 5.0
- **Ant Design:** 5.11.0
- **Redux Toolkit:** 1.9.7
- **React-Redux:** 8.1.3
- **Axios:** 1.6.0

## Структура файлів

```
frontend/
├── src/
│   ├── store/
│   │   ├── index.ts
│   │   ├── hooks.ts
│   │   └── slices/
│   │       ├── authSlice.ts
│   │       └── casesSlice.ts
│   ├── config/
│   │   └── theme.ts
│   ├── components/
│   │   └── Layout/
│   │       └── MainLayout.tsx
│   └── pages/
│       ├── _app.tsx
│       ├── index.tsx
│       ├── login.tsx
│       └── dashboard.tsx
├── package.json
├── tsconfig.json
└── next.config.js
```

## Налаштування

### Path Aliases

Налаштовано в `tsconfig.json`:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

Використання:

```typescript
import { useAppDispatch } from '@/store/hooks';
import MainLayout from '@/components/Layout/MainLayout';
```

### Theme Customization

Налаштування в `src/config/theme.ts`:

```typescript
export const theme: ThemeConfig = {
  token: {
    colorPrimary: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    fontSize: 14,
    borderRadius: 6,
  },
  components: {
    Layout: {
      headerBg: '#001529',
      siderBg: '#001529',
    },
    // ...
  },
};
```

## Запуск

### Встановлення залежностей

```bash
npm install
```

Або через батник (Windows):

```bash
install-frontend.bat
```

### Development Server

```bash
npm run dev
```

Сервер запуститься на http://localhost:3000

### Production Build

```bash
npm run build
npm start
```

Або через батник:

```bash
build-frontend.bat
```

## Redux State

### Auth State

```typescript
interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  error: string | null;
}
```

### Cases State

```typescript
interface CasesState {
  cases: Case[];
  currentCase: Case | null;
  isLoading: boolean;
  error: string | null;
  total: number;
  page: number;
  pageSize: number;
}
```

## API Integration

### Login Example

```typescript
const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    username: email,
    password: password,
  }),
});

const data = await response.json();

dispatch(
  loginSuccess({
    user: data.user,
    accessToken: data.access_token,
    refreshToken: data.refresh_token,
  })
);
```

## Використання Redux

### Typed Hooks

```typescript
import { useAppDispatch, useAppSelector } from '@/store/hooks';

// В компоненті
const dispatch = useAppDispatch();
const user = useAppSelector(selectUser);
const isAuthenticated = useAppSelector(selectIsAuthenticated);
```

### Actions

```typescript
// Login
dispatch(loginStart());
dispatch(loginSuccess({ user, accessToken, refreshToken }));
dispatch(loginFailure('Error message'));

// Logout
dispatch(logout());

// Cases
dispatch(fetchCasesSuccess({ cases, total, page, pageSize }));
dispatch(updateCaseSuccess(updatedCase));
```

## Компоненти

### MainLayout

```typescript
import MainLayout from '@/components/Layout/MainLayout';

const MyPage = () => {
  return (
    <MainLayout>
      <h1>My Page Content</h1>
    </MainLayout>
  );
};
```

Автоматично додає:
- Sidebar з навігацією
- Header з профілем і сповіщеннями
- Content area з білим фоном

### Login Page

Доступна за URL: `/login`

Функції:
- Форма входу
- Валідація email і пароля
- Loading стан
- Error handling
- Redirect на /dashboard після успішного входу

### Dashboard Page

Доступна за URL: `/dashboard`

Функції:
- Статистичні картки
- Responsive grid
- TODO: таблиця останніх звернень

## Маршрутизація

| URL | Компонент | Опис |
|-----|-----------|------|
| `/` | index.tsx | Головна (перенаправлення) |
| `/login` | login.tsx | Сторінка входу |
| `/dashboard` | dashboard.tsx | Головна панель |
| `/cases` | - | TODO: Список звернень |
| `/admin/users` | - | TODO: Користувачі |
| `/admin/categories` | - | TODO: Категорії |
| `/admin/channels` | - | TODO: Канали |

## Наступні кроки

1. **FE-002:** Cases List Page
   - Таблиця звернень
   - Фільтри і пошук
   - Пагінація

2. **FE-003:** Case Detail Page
   - Деталі звернення
   - Історія змін
   - Коментарі
   - Файли

3. **FE-004:** Create Case Form
   - Форма створення
   - Upload файлів
   - Валідація

4. **API Integration**
   - Axios instance
   - Interceptors для JWT refresh
   - Error handling

5. **Protected Routes**
   - Middleware для автентифікації
   - Перевірка ролей
   - Redirect на /login

## Notes

- Всі тексти українською мовою
- TypeScript everywhere для type safety
- Responsive design (xs, sm, lg breakpoints)
- Темна тема для сайдбару (#001529)
- TODO коментарі для майбутнього розвитку
- Використовується Pages Router (не App Router)
