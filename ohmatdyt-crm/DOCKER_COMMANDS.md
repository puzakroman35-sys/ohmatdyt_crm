# Docker Commands - Quick Reference

## Батники (Windows)

| Команда | Що робить |
|---------|-----------|
| `start-dev.bat` | 🚀 Запуск всього проекту (Full Stack - 7 сервісів) |
| `docker-frontend.bat` | 🎨 Запуск Frontend + Backend API (мінімальна конфігурація) |
| `docker-stop.bat` | ⏹️ Зупинка всіх сервісів |
| `docker-logs.bat [service]` | 📋 Перегляд логів (всіх або конкретного сервісу) |
| `docker-rebuild.bat` | 🔄 Повна перебудова проекту (clean build) |

## Linux/Mac

```bash
# Запуск всього проекту
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Тільки Frontend + Backend
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build db redis api frontend

# Зупинка
docker-compose down

# Логи
docker-compose logs -f
docker-compose logs -f frontend

# Перебудова
docker-compose build --no-cache
```

## Приклади використання

### Звичайна розробка

```bash
# 1. Запустити проект
start-dev.bat

# 2. Дочекатись повного запуску (логи покажуть "Ready")

# 3. Відкрити в браузері
# http://localhost:3000 - Frontend
# http://localhost:8000/docs - API Docs
```

### Дивитись логи

```bash
# Всі сервіси
docker-logs.bat

# Тільки frontend
docker-logs.bat frontend

# Тільки API
docker-logs.bat api
```

### Після змін в коді

- **Frontend:** Зміни застосуються автоматично (HMR)
- **Backend:** Uvicorn перезавантажиться автоматично
- **Docker configs:** Потрібна перебудова - `docker-rebuild.bat`

### Якщо щось зламалось

```bash
# 1. Зупинити все
docker-stop.bat

# 2. Повна перебудова
docker-rebuild.bat

# 3. Запустити знову
start-dev.bat
```

## URL адреси

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **API Docs (ReDoc):** http://localhost:8000/redoc
- **Nginx (Reverse Proxy):** http://localhost:80

## Детальна документація

📖 [DOCKER_SCRIPTS.md](./DOCKER_SCRIPTS.md) - Повний опис всіх команд  
📖 [DOCKER_GUIDE.md](./DOCKER_GUIDE.md) - Гід по Docker розробці  
📖 [QUICKSTART.md](./QUICKSTART.md) - Швидкий старт
