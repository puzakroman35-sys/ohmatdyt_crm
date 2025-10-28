# Ohmatdyt CRM - Docker Development Guide

## Швидкий старт

### Запуск всього проекту (Backend + Frontend)

```bash
# Windows
start-dev.bat

# Linux/Mac
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Доступ:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Nginx (reverse proxy):** http://localhost:80

### Запуск тільки Frontend

```bash
# Windows
start-frontend-docker.bat

# Linux/Mac
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build frontend
```

⚠️ **Увага:** Для роботи фронтенду потрібен запущений backend API!

### Зупинка всіх сервісів

```bash
docker-compose down
```

Або з видаленням volumes:

```bash
docker-compose down -v
```

## Структура Docker сервісів

```
┌─────────────────────────────────────────────┐
│              Nginx (Port 80)                │
│         Reverse Proxy / Static Files        │
└───────────┬────────────────────┬────────────┘
            │                    │
            ▼                    ▼
    ┌───────────────┐    ┌──────────────┐
    │   Frontend    │    │     API      │
    │  (Next.js)    │    │  (FastAPI)   │
    │   Port 3000   │    │  Port 8000   │
    └───────┬───────┘    └──────┬───────┘
            │                   │
            └───────┬───────────┘
                    ▼
            ┌───────────────┐
            │   PostgreSQL  │
            │     Redis     │
            │   Worker      │
            │     Beat      │
            └───────────────┘
```

## Docker Compose файли

### docker-compose.yml (Base)
- Базова конфігурація всіх сервісів
- Production-ready налаштування
- Використовується для production deployment

### docker-compose.dev.yml (Development Override)
- Override для development режиму
- Live reload для фронтенду
- Volume mounting для hot reload
- Використовується разом з docker-compose.yml

### docker-compose.prod.yml (Production)
- Production оптимізації
- Build для production
- Без volume mounting

## Environment Variables

Налаштування в `.env` файлі:

```env
# Порти
API_PORT=8000
FRONTEND_PORT=3000
NGINX_PORT=80

# Database
POSTGRES_DB=ohmatdyt_crm
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# API URL для фронтенду
NEXT_PUBLIC_API_BASE_URL=http://api:8000
```

## Frontend Docker конфігурація

### Dockerfile (Multi-stage build)

```dockerfile
# Development stage
FROM node:20-alpine AS dev
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

# Production stage
FROM node:20-alpine AS prod
# ... production build
```

### Volumes (Development)

```yaml
volumes:
  - ./frontend/src:/app/src              # Live reload
  - ./frontend/public:/app/public        # Static files
  - ./frontend/package.json:/app/package.json
  - ./frontend/tsconfig.json:/app/tsconfig.json
  - /app/node_modules                    # Exclude from mount
  - /app/.next                           # Exclude from mount
```

## Корисні команди

### Логи

```bash
# Всі сервіси
docker-compose logs -f

# Тільки frontend
docker-compose logs -f frontend

# Тільки API
docker-compose logs -f api
```

### Перебудова образів

```bash
# Перебудова всіх сервісів
docker-compose build

# Перебудова тільки frontend
docker-compose build frontend

# Перебудова з очищенням кешу
docker-compose build --no-cache frontend
```

### Виконання команд всередині контейнера

```bash
# Відкрити shell в frontend контейнері
docker-compose exec frontend sh

# Встановити npm пакет
docker-compose exec frontend npm install package-name

# Запустити npm команду
docker-compose exec frontend npm run build
```

### Перезапуск сервісів

```bash
# Перезапуск frontend
docker-compose restart frontend

# Перезапуск всіх сервісів
docker-compose restart
```

### Очистка

```bash
# Видалити зупинені контейнери
docker-compose rm -f

# Видалити невикористовувані образи
docker image prune

# Видалити все (volumes, networks, images)
docker-compose down -v --rmi all
```

## Розробка з Live Reload

### Hot Module Replacement (HMR)

Frontend в Docker підтримує HMR:

1. Змініть файл в `frontend/src/`
2. Зміни автоматично відобразяться в браузері
3. Не потрібно перезапускати контейнер

### Встановлення нових npm пакетів

**Варіант 1: Всередині контейнера**
```bash
docker-compose exec frontend npm install package-name
```

**Варіант 2: Локально + rebuild**
```bash
cd frontend
npm install package-name
cd ..
docker-compose up --build frontend
```

### TypeScript та ESLint

TypeScript перевірка працює автоматично при збереженні файлів.

Ручна перевірка:
```bash
docker-compose exec frontend npm run lint
```

## Налагодження (Debugging)

### VS Code DevContainer

Можна налаштувати VS Code для розробки всередині контейнера.

Створіть `.devcontainer/devcontainer.json`:

```json
{
  "name": "Ohmatdyt CRM Frontend",
  "dockerComposeFile": ["../docker-compose.yml", "../docker-compose.dev.yml"],
  "service": "frontend",
  "workspaceFolder": "/app",
  "customizations": {
    "vscode": {
      "extensions": [
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode"
      ]
    }
  }
}
```

### Доступ до контейнера

```bash
# Відкрити shell
docker-compose exec frontend sh

# Перевірити файли
docker-compose exec frontend ls -la /app/src

# Перевірити node_modules
docker-compose exec frontend npm list
```

## Production Deployment

### Build для production

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build frontend
```

### Запуск production

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Nginx Reverse Proxy

Nginx налаштований як reverse proxy:

```
http://localhost:80/      -> Frontend (Next.js)
http://localhost:80/api/  -> Backend API
```

## Проблеми та вирішення

### Frontend не запускається

1. Перевірте логи:
   ```bash
   docker-compose logs frontend
   ```

2. Перебудуйте контейнер:
   ```bash
   docker-compose build --no-cache frontend
   docker-compose up frontend
   ```

### Зміни не відображаються (HMR не працює)

1. Перевірте volumes в docker-compose.dev.yml
2. Переконайтесь, що WATCHPACK_POLLING=true
3. Перезапустіть контейнер:
   ```bash
   docker-compose restart frontend
   ```

### Port already in use

Якщо порт 3000 зайнятий:

1. Змініть FRONTEND_PORT в .env
2. Перезапустіть:
   ```bash
   docker-compose down
   docker-compose up
   ```

### Module not found errors

Перебудуйте з чистими node_modules:

```bash
docker-compose down
docker-compose build --no-cache frontend
docker-compose up
```

## Корисні посилання

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Next.js Docker Documentation](https://nextjs.org/docs/deployment#docker-image)
- [Node.js Docker Best Practices](https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md)

## Автори

Ohmatdyt CRM Development Team
