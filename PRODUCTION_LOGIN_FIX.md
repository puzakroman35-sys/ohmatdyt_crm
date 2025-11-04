# Виправлення проблеми з логіном на продакшені

**Дата:** 31 жовтня 2025  
**Статус:** ✅ ВИРІШЕНО

## Проблема

На продакшен сервері (https://192.168.31.249) логін-форма надсилала запити на `http://localhost:8000/auth/login` замість правильного URL `https://192.168.31.249/api/auth/login`, що призводило до CORS помилок та неможливості увійти в систему.

## Причина

1. У `docker-compose.yml` була захардкоджена змінна середовища:
   ```yaml
   environment:
     - NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

2. Next.js вбудовує `NEXT_PUBLIC_*` змінні під час білду, а не під час запуску контейнера

3. У Dockerfile frontend не були налаштовані build arguments для передачі змінних середовища під час білду

## Рішення

### 1. Видалено захардкоджену змінну з docker-compose.yml
Замість фіксованого значення, тепер використовуються змінні з `.env` файлу через build args.

### 2. Оновлено frontend/Dockerfile
Додано ARG та ENV для build-time змінних:
```dockerfile
# Production build
FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Accept build arguments for Next.js public env vars
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL

RUN npm run build
```

### 3. Додано build args у docker-compose.yml
```yaml
frontend:
  build:
    context: ./frontend
    target: dev
    args:
      NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-http://localhost:8000}
      NEXT_PUBLIC_API_BASE_URL: ${NEXT_PUBLIC_API_BASE_URL:-http://localhost:8000/api}
```

### 4. Оновлено .env.prod на сервері
```bash
# Frontend
NODE_ENV=production
NEXT_PUBLIC_API_URL=/api
NEXT_PUBLIC_API_BASE_URL=/api
```

### 5. Налаштовано Git на продакшен сервері
Тепер можна використовувати `git pull` для оновлення коду замість копіювання файлів.

## Команди для деплою

```bash
# На продакшен сервері
cd ~/ohmatdyt-crm
git pull origin main

# Перебудувати frontend з правильними build args
docker compose -f docker-compose.yml -f docker-compose.prod.yml build \
  --no-cache \
  --build-arg NEXT_PUBLIC_API_URL=/api \
  --build-arg NEXT_PUBLIC_API_BASE_URL=/api \
  frontend

# Перезапустити frontend
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d frontend
```

## Перевірка

✅ Frontend тепер використовує `/api` для всіх API запитів  
✅ Nginx проксує `/api/*` на backend API  
✅ Логін працює коректно через https://192.168.31.249/login  
✅ Немає CORS помилок  
✅ JavaScript файли перебудовані з новими хешами (login-d0b1f404a5a19c48.js)

## Змінені файли

1. `ohmatdyt-crm/docker-compose.yml` - додано build args для frontend
2. `ohmatdyt-crm/frontend/Dockerfile` - додано ARG/ENV для NEXT_PUBLIC змінних
3. `ohmatdyt-crm/.env.prod` - оновлено змінні для frontend
4. `ohmatdyt-crm/docker-compose.prod.yml` - очищено volumes для production

## Коміти

- `53d6c25` - Fix: Remove hardcoded NEXT_PUBLIC_API_URL from docker-compose.yml
- `4686c3f` - Fix: Add build args for NEXT_PUBLIC env vars in frontend Dockerfile
- `69b4d42` - Add production deployment documentation and fix login API URL issue

## Важливо для майбутніх деплоїв

При деплої на продакшен **обов'язково** передавати build arguments:
```bash
--build-arg NEXT_PUBLIC_API_URL=/api
--build-arg NEXT_PUBLIC_API_BASE_URL=/api
```

Або переконатися, що ці змінні є в `.env.prod` файлі, який використовується під час білду.

---

**Результат:** Логін на продакшені працює коректно! 🎉
