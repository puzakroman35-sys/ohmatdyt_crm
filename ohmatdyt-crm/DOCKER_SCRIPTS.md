# Docker Scripts - Ohmatdyt CRM

Всі команди для роботи з проектом через Docker.

## 🚀 Основні команди

### Запуск проекту

```bash
# Запуск всього проекту (Full Stack)
start-dev.bat

# Запуск тільки Frontend + Backend API
docker-frontend.bat
```

### Зупинка

```bash
# Зупинити всі сервіси
docker-stop.bat

# Або через docker-compose
docker-compose down

# Зупинити + видалити volumes
docker-compose down -v
```

### Логи

```bash
# Всі сервіси
docker-logs.bat

# Конкретний сервіс
docker-logs.bat frontend
docker-logs.bat api
docker-logs.bat worker
```

### Перебудова

```bash
# Повна перебудова (clean build)
docker-rebuild.bat

# Швидка перебудова
docker-compose build
```

## 📋 Доступні скрипти

| Файл | Опис |
|------|------|
| `start-dev.bat` | Запуск всього проекту (7 сервісів) |
| `docker-frontend.bat` | Запуск Frontend + необхідні залежності |
| `docker-stop.bat` | Зупинка всіх сервісів |
| `docker-logs.bat` | Перегляд логів |
| `docker-rebuild.bat` | Повна перебудова проекту |

## 🔧 Сервіси

При запуску `start-dev.bat` стартують:

1. **db** - PostgreSQL база даних
2. **redis** - Redis для черг і кешу
3. **api** - FastAPI backend
4. **worker** - Celery worker
5. **beat** - Celery beat scheduler
6. **frontend** - Next.js frontend
7. **nginx** - Reverse proxy

## 🌐 Порти

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Nginx:** http://localhost:80

## 💡 Корисні команди

### Shell в контейнері

```bash
# Frontend
docker-compose exec frontend sh

# API
docker-compose exec api sh

# Database
docker-compose exec db psql -U ohm_user -d ohm_db
```

### Встановлення npm пакетів

```bash
docker-compose exec frontend npm install package-name
```

### Міграції (Alembic)

```bash
# Застосувати міграції
docker-compose exec api alembic upgrade head

# Створити міграцію
docker-compose exec api alembic revision --autogenerate -m "description"
```

### Перезапуск сервісу

```bash
docker-compose restart frontend
docker-compose restart api
```

### Статус сервісів

```bash
docker-compose ps
```

## 🐛 Troubleshooting

### Порти зайняті

Змініть порти в `.env`:

```env
API_PORT=8001
FRONTEND_PORT=3001
NGINX_PORT=8080
```

### Зміни не відображаються

```bash
# Перезапустіть сервіс
docker-compose restart frontend

# Або повна перебудова
docker-rebuild.bat
```

### Помилки при білді

```bash
# Повна очистка + перебудова
docker-compose down -v --rmi all
docker-rebuild.bat
```

## 📖 Детальна документація

- [Docker Guide](./DOCKER_GUIDE.md) - Повна документація
- [Quick Start](./QUICKSTART.md) - Швидкий старт
- [Frontend README](./FE-001_README.md) - Frontend документація

---

**Примітка:** Всі локальні батники (npm install, npm run dev) видалені. Працюємо тільки через Docker! 🐳
