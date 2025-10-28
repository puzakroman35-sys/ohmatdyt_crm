# Ohmatdyt CRM - Infrastructure

## Project Overview
The `ohmatdyt-crm` is a comprehensive CRM application with microservices architecture including API (FastAPI), background workers (Celery), frontend (Next.js), PostgreSQL database, Redis cache, and Nginx reverse proxy.

## Services
- **API**: FastAPI with Uvicorn for REST API endpoints
- **Worker**: Celery worker for async background tasks
- **Beat**: Celery beat scheduler for periodic tasks
- **Redis**: Message broker and cache
- **Database**: PostgreSQL 16 for data persistence
- **Frontend**: Next.js React application
- **Nginx**: Reverse proxy and static file server

## Environment Configuration (INF-002)

### Setup .env file
Copy `.env.example` to `.env` for local development:
```bash
cp .env.example .env
```

For production, copy `.env.prod.example` to `.env.prod` and **replace all placeholder secrets**.

### Key Environment Variables

**Database (DB_*)**
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `DATABASE_URL`: Full PostgreSQL connection string

**Redis (REDIS_*)**
- `REDIS_HOST`: Redis hostname (default: redis)
- `REDIS_PORT`: Redis port (default: 6379)
- `REDIS_URL`: Full Redis connection string

**SMTP / Email (SMTP_*)**
- `SMTP_HOST`: SMTP server hostname
- `SMTP_PORT`: SMTP port (usually 587 for TLS)
- `SMTP_USER`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `SMTP_TLS`: Enable TLS (true/false)
- `EMAILS_FROM_EMAIL`: Sender email address

**JWT / Auth (JWT_*)**
- `JWT_SECRET`: Secret key for JWT signing (MUST be changed in production!)
- `JWT_ALGORITHM`: Algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token lifetime
- `REFRESH_TOKEN_EXPIRE_MINUTES`: Refresh token lifetime

**CORS & Security**
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `CORS_ORIGINS`: Comma-separated list of allowed CORS origins

**Volumes & Paths**
- `MEDIA_ROOT`: Container path for uploaded media files
- `STATIC_ROOT`: Container path for static files

## Docker Volumes
- `db-data`: PostgreSQL data persistence
- `media`: User-uploaded files (accessible across api/worker/beat)
- `static`: Collected static files (served by nginx)

## Getting Started

### Prerequisites
- Docker 24+
- Docker Compose 2.20+

### Local Development
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ohmatdyt-crm
   ```

2. Setup environment:
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

3. Start all services:
   ```bash
   docker compose up -d --build
   ```

4. Access services:
   - API: http://localhost:8000
   - Frontend: http://localhost:3000
   - Nginx (proxy): http://localhost:8080

### Production Deployment
1. Setup production environment:
   ```bash
   cp .env.prod.example .env.prod
   # Edit .env.prod - REPLACE ALL SECRETS!
   ```

2. Deploy with production overlay:
   ```bash
   docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up -d --build
   ```

## Smoke Tests (INF-002 DoD)

### Test environment variables loading
```bash
docker compose exec api sh -c 'echo $DATABASE_URL'
docker compose exec api sh -c 'echo $REDIS_URL'
```

### Test volume accessibility
```bash
docker compose exec api sh -c 'ls -la $MEDIA_ROOT $STATIC_ROOT'
docker compose exec worker sh -c 'ls -la $MEDIA_ROOT'
```

### Check volume persistence
```bash
docker volume ls | findstr ohmatdyt_crm
```

### Test file upload to media volume
```bash
docker compose exec api sh -c 'echo "test" > $MEDIA_ROOT/test.txt && cat $MEDIA_ROOT/test.txt'
```

## Health Checks
Services include health checks for reliability:
- **db**: `pg_isready` check every 5s
- **redis**: `redis-cli ping` every 5s
- **api**: Directory existence check for volumes

## Directory Structure
```
ohmatdyt-crm/
├── docker-compose.yml          # Main compose file
├── docker-compose.prod.yml     # Production overrides
├── .env.example                # Development env template
├── .env.prod.example           # Production env template
├── api/                        # FastAPI application
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
├── worker/                     # Celery worker
│   ├── Dockerfile
│   └── entrypoint.sh
├── beat/                       # Celery beat
│   ├── Dockerfile
│   └── entrypoint.sh
├── frontend/                   # Next.js app
│   ├── Dockerfile
│   ├── package.json
│   └── src/
├── nginx/                      # Nginx config
│   └── nginx.conf
├── db/                         # Database initialization
│   └── init.sql
├── redis/                      # Redis config
│   └── redis.conf
└── scripts/                    # Utility scripts
    ├── healthcheck.sh
    └── wait-for.sh
```

## Useful Commands

### View logs
```bash
docker compose logs -f api
docker compose logs -f worker
docker compose logs -f frontend
```

### Restart a service
```bash
docker compose restart api
```

### Execute commands in container
```bash
docker compose exec api sh
docker compose exec db psql -U $POSTGRES_USER -d $POSTGRES_DB
```

### Clean up
```bash
docker compose down
docker compose down -v  # Also remove volumes
```

## Contributing
Please follow the task-based workflow defined in the `/tasks` directory.

## License
This project is licensed under the MIT License.