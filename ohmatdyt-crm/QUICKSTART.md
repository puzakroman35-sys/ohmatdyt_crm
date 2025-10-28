# Ohmatdyt CRM - Quick Start Guide

## ✅ Status: Infrastructure Ready (INF-001 & INF-002 Completed)

All infrastructure is set up and tested. The project is ready for backend and frontend development.

## 🚀 Quick Start

### 1. Start the Project
```powershell
cd d:\AI_boost\ohmatdyt_crm\ohmatdyt-crm
docker compose --env-file .env up -d --build
```

### 2. Verify Everything Works
```powershell
# Check status
docker compose ps

# Run smoke tests
powershell -ExecutionPolicy Bypass -File .\scripts\smoke-test-simple.ps1
```

### 3. Access Services
- **API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000
- **Nginx (Proxy):** http://localhost:8080

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

### Backend Development (Фаза 1)
- BE-001: Database models & migrations
- BE-002: User authentication & JWT
- BE-003: Patient management API
- BE-004: Doctor management API

### Frontend Development (Фаза 1)
- FE-001: UI components & routing
- FE-002: Authentication pages
- FE-003: Patient management UI
- FE-004: Dashboard

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
