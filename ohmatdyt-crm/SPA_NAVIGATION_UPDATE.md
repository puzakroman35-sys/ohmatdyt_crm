# Оновлення навігації SPA (Single Page Application)

## Проблема
При переході між сторінками відбувалося повне перезавантаження вікна браузера замість плавного оновлення контенту всередині `main`.

## Рішення

### 1. Перенесення MainLayout в _app.tsx
**Файл:** `frontend/src/pages/_app.tsx`

**Зміни:**
- `MainLayout` перенесено з окремих сторінок в центральний компонент `_app.tsx`
- Додано логіку виключення сторінок, які не потребують layout (login, index)
- Тепер layout залишається незмінним при переході між сторінками

**Результат:**
```tsx
export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const isNoLayoutPage = noLayoutPages.includes(router.pathname);

  return (
    <Provider store={store}>
      <AuthProvider>
        <ConfigProvider theme={antdConfig.theme} locale={antdConfig.locale}>
          {isNoLayoutPage ? (
            <Component {...pageProps} />
          ) : (
            <MainLayout>
              <Component {...pageProps} />
            </MainLayout>
          )}
        </ConfigProvider>
      </AuthProvider>
    </Provider>
  );
}
```

### 2. Видалення MainLayout з окремих сторінок
**Оновлені файли:**
- `frontend/src/pages/dashboard.tsx`
- `frontend/src/pages/cases.tsx`
- `frontend/src/pages/users.tsx`
- `frontend/src/pages/cases/[id].tsx`
- `frontend/src/pages/cases/create.tsx`
- `frontend/src/pages/admin/categories.tsx`
- `frontend/src/pages/admin/channels.tsx`

**Зміни:**
- Видалено імпорт `MainLayout`
- Видалено обгортку `<MainLayout>` навколо контенту
- Залишено тільки `<AuthGuard>` для захисту маршрутів

### 3. Оптимізація навігації з Link компонентом
**Файл:** `frontend/src/components/Layout/MainLayout.tsx`

**Зміни:**
- Додано імпорт `Link` від Next.js
- Замінено `onClick` з `router.push()` на `<Link>` компоненти в меню
- Це забезпечує:
  - Prefetch сторінок при наведенні
  - Швидшу навігацію без перезавантаження
  - Краще SEO

**Приклад:**
```tsx
{
  key: '/cases',
  icon: <FileTextOutlined />,
  label: <Link href="/cases">Звернення</Link>,
}
```

### 4. Глобальні стилі для плавних переходів
**Новий файл:** `frontend/src/styles/globals.css`

**Особливості:**
- Анімація появи контенту (`fadeIn`)
- Відключення непотрібних переходів Ant Design
- Стилі для посилань (без підкреслення та синього кольору)

**Імпорт:** Додано в `_app.tsx`

## Переваги

### 1. Швидкість
- ✅ Немає повного перезавантаження сторінки
- ✅ Prefetch сторінок при наведенні на посилання
- ✅ Збереження стану Redux між переходами
- ✅ Збереження стану компонентів layout

### 2. Користувацький досвід
- ✅ Плавні переходи між сторінками
- ✅ Миттєва навігація
- ✅ Немає "мерехтіння" при переході
- ✅ Sidebar та header залишаються незмінними

### 3. Продуктивність
- ✅ Менше запитів до сервера
- ✅ Менше споживання пам'яті
- ✅ Кращий час завантаження
- ✅ Оптимізація Next.js працює коректно

### 4. SEO
- ✅ Використання нативного Next.js Link
- ✅ Правильна індексація посилань
- ✅ Семантична навігація

## Тестування

### Що перевірити:
1. **Навігація між сторінками:**
   - Dashboard → Cases → Users
   - Перевірити що sidebar не перезавантажується
   - URL правильно змінюється в браузері

2. **Збереження стану:**
   - Фільтри на сторінці Cases
   - Відкрита підменю в sidebar
   - Авторизаційні дані

3. **Продуктивність:**
   - Використати DevTools → Network
   - Перевірити що немає зайвих запитів при навігації
   - Transition має бути плавним

4. **Розділи доступу:**
   - ADMIN має доступ до всіх сторінок
   - EXECUTOR бачить тільки Cases
   - OPERATOR бачить тільки свої Cases

## Технічні деталі

### Next.js Router
- Використовується `useRouter()` hook для визначення активного роута
- `router.pathname` використовується для підсвітки активного пункту меню

### React Context
- Redux Provider обгортає весь додаток
- AuthProvider забезпечує авторизацію
- ConfigProvider налаштовує тему Ant Design

### Code Splitting
- Next.js автоматично розділяє код по сторінках
- Prefetch завантажує код сторінки при наведенні на Link
- Lazy loading компонентів працює коректно

## Важливі моменти

⚠️ **Сторінки без layout:**
- `/` (index) - головна landing сторінка
- `/login` - сторінка авторизації

⚠️ **Захист маршрутів:**
- Всі сторінки (крім login) обгорнуті в `<AuthGuard>`
- RoleGuard використовується всередині сторінок для RBAC

⚠️ **Стилі:**
- Глобальні стилі в `globals.css`
- Ant Design теми в `config/theme`
- Inline стилі для специфічних компонентів

## Подальші покращення

### Можливі оптимізації:
1. **React Suspense** для lazy loading компонентів
2. **Loading states** між переходами сторінок
3. **Error boundaries** для обробки помилок
4. **Page transitions** з react-transition-group
5. **Скелетони** замість спінерів

### Моніторинг:
- Додати аналітику переходів між сторінками
- Відслідковувати час навігації
- Логувати помилки при переходах

---

**Дата оновлення:** 29 жовтня 2025  
**Автор:** GitHub Copilot  
**Версія:** 1.0
