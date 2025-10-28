# Ohmatdyt CRM - Quick Start Guide

## ✅ Status: Infrastructure Ready (INF-001 & INF-002 Completed)

All infrastructure is set up and tested. The project is ready for backend and frontend development.

## 🚀 Quick Start

### Запуск через Docker 🐳

**Весь проект (Full Stack):**
```bash
start-dev.bat
```

**Тільки Frontend + Backend:**
```bash
docker-frontend.bat
```

**Зупинка:**
```bash
docker-stop.bat
```

**Логи:**
```bash
docker-logs.bat          # Всі сервіси
docker-logs.bat frontend # Тільки frontend
docker-logs.bat api      # Тільки API
```

**Доступ до сервісів:**
- **Frontend:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Nginx:** http://localhost:80

### Корисні команди

```bash
# Статус сервісів
docker-compose ps

# Shell в контейнері
docker-compose exec frontend sh
docker-compose exec api sh

# Перезапуск сервісу
docker-compose restart frontend

# Повна перебудова
docker-rebuild.bat
```

### Перевірка роботи

```powershell
# Check status
docker-compose ps

# Run smoke tests
powershell -ExecutionPolicy Bypass -File .\scripts\smoke-test-simple.ps1
```

## 📋 Common Commands

### Container Management
```powershell
# View logs
docker compose logs -f api
docker compose logs -f frontend
docker compose logs -f worker

# Restart service
docker compose restart api

# Stop all services
docker compose down

# Stop and remove volumes (fresh start)
docker compose down -v
```

### Development
```powershell
# Execute commands in API container
docker compose exec api sh

# Connect to database
docker compose exec db psql -U ohm_user -d ohm_db

# Check environment variables
docker compose exec api sh -c 'printenv | grep DATABASE'

# Test file upload to media
docker compose exec api sh -c 'echo "test" > /var/app/media/test.txt'
```

### Database
```powershell
# Access PostgreSQL shell
docker compose exec db psql -U ohm_user -d ohm_db

# Run migrations (once implemented)
docker compose exec api alembic upgrade head
```

## 📁 Project Structure

```
ohmatdyt-crm/
├── api/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py        # API entry point
│   │   └── celery_app.py  # Celery configuration
│   └── Dockerfile
├── worker/                 # Celery worker
├── beat/                   # Celery beat scheduler
├── frontend/               # Next.js frontend
│   ├── src/pages/
│   └── Dockerfile
├── nginx/                  # Nginx reverse proxy
│   └── nginx.conf
├── db/                     # Database initialization
│   └── init.sql
├── redis/                  # Redis configuration
│   └── redis.conf
├── scripts/                # Utility scripts
│   └── smoke-test-simple.ps1
├── docker-compose.yml      # Main compose file
├── .env                    # Environment variables
└── README.md              # Full documentation
```

## 🔧 Environment Configuration

All environment variables are in `.env` file. Key variables:

- **Database:** `DATABASE_URL`, `POSTGRES_*`
- **Redis:** `REDIS_URL`
- **SMTP:** `SMTP_*` (for email)
- **JWT:** `JWT_SECRET`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- **CORS:** `CORS_ORIGINS`, `ALLOWED_HOSTS`

## 🧪 Testing

### Health Checks
```powershell
# API health
Invoke-WebRequest http://localhost:8000/health

# Nginx health
Invoke-WebRequest http://localhost:8080/health
```

### Backend Tests
```powershell
# Test BE-006 (Case creation with files)
.\scripts\test-be006.ps1

# Test BE-005 (Attachments)
cd api
python test_be005.py
cd ..

# Test BE-004 (Cases CRUD)
cd api
python test_be004.py
cd ..
```

### Verify Volumes
```powershell
docker volume ls | findstr ohmatdyt_crm
docker compose exec api ls -la /var/app/media /var/app/static
```

## 🐛 Troubleshooting

### Services won't start
```powershell
# Check logs for errors
docker compose logs

# Rebuild from scratch
docker compose down -v
docker compose --env-file .env up -d --build
```

### Environment variables not loaded
```powershell
# Make sure .env file exists
Get-Content .env | Select-Object -First 10

# Use explicit env file flag
docker compose --env-file .env up -d
```

### Port conflicts
```powershell
# Change ports in .env
# API_PORT=8001
# FRONTEND_PORT=3001
# NGINX_PORT=8081
```

## 📚 Next Steps

### 📜 Docker Scripts
- 🚀 `start-dev.bat` - Запуск всього проекту
- 🎨 `docker-frontend.bat` - Тільки Frontend + API
- ⏹️ `docker-stop.bat` - Зупинка сервісів
- 📋 `docker-logs.bat [service]` - Перегляд логів
- 🔄 `docker-rebuild.bat` - Повна перебудова

Детальніше: [Docker Scripts Guide](./DOCKER_SCRIPTS.md)

### Quick Links
- 📖 [Docker Guide](./DOCKER_GUIDE.md) - Повна документація по Docker
- 📖 [Docker Scripts](./DOCKER_SCRIPTS.md) - Опис всіх батників
- 📖 [FE-001 README](./FE-001_README.md) - Документація фронтенду
- 📖 [Full README](./README.md) - Complete documentation
- 📖 [Implementation Status](./IMPLEMENTATION_STATUS.md) - Detailed status
- 📖 [Project Status](../PROJECT_STATUS.md) - Загальний статус проекту

### ✅ Completed Backend Features (Фаза 1)
- ✅ BE-001: User Model & Authentication
- ✅ BE-002: JWT Authentication
- ✅ BE-003: Categories & Channels (Directories)
- ✅ BE-004: Cases Model & CRUD
- ✅ BE-005: Attachments (File Upload)
- ✅ BE-006: Create Case (multipart) + Email Trigger
- ✅ BE-007: Case Filtering & Search
- ✅ BE-008: Case Detail (History, Comments, Files)
- ✅ BE-009: Take Case Into Work (EXECUTOR)
- ✅ BE-010: Change Case Status (IN_PROGRESS -> NEEDS_INFO|REJECTED|DONE)

### ✅ Completed Frontend Features (Фаза 1)
- ✅ FE-001: Next.js Skeleton + Ant Design + Redux Toolkit
  - Redux store з auth і cases slices
  - Ant Design тема з українською локалізацією
  - MainLayout з навігацією
  - Сторінка входу (login)
  - Dashboard з статистикою
  - Docker integration з HMR

### 🔄 Pending Backend Features (Фаза 1)
- BE-011: Email Notifications (повна реалізація)
- BE-012: Case Assignment to Executor
- BE-013: Case Status Workflow
- BE-014: Internal/Public Comments
- BE-015: Case History & Audit Log

### 🔄 Pending Frontend Features (Фаза 1)
- FE-002: Cases List Page (таблиця, фільтри, пошук)
- FE-003: Case Detail Page (перегляд, коментарі, файли)
- FE-004: Create Case Form (форма створення + upload)
- FE-005: Case Actions (взяти в роботу, зміна статусу)
- FE-006: User Management (CRUD користувачів)

### Infrastructure (Фаза 2)
- INF-003: CI/CD pipeline
- Automated backups
- Monitoring & logging
- SSL/TLS certificates

## 📖 Documentation

- [Full README](./README.md) - Complete documentation
- [Implementation Status](./IMPLEMENTATION_STATUS.md) - Detailed status
- [Task Definitions](../tasks/) - All development tasks

## ✅ Verified Features

- ✅ All 7 services running (api, worker, beat, db, redis, frontend, nginx)
- ✅ Health checks passing
- ✅ Environment variables configured
- ✅ Volumes created and accessible
- ✅ File persistence working
- ✅ Inter-service communication
- ✅ API endpoints responding
- ✅ Frontend rendering
- ✅ Nginx proxy working

---

**Status:** Ready for application development 🚀
