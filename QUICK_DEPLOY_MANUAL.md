# Quick Manual Deployment Guide
# Server: rpadmin@10.24.2.187

## Step-by-Step Instructions

### 1. Connect to Server
```bash
ssh rpadmin@10.24.2.187
```

### 2. Install Docker (if not installed)
```bash
# Quick Docker installation
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker

# Verify
docker --version
docker compose version
```

### 3. Clone Repository
```bash
cd ~
git clone https://github.com/puzakroman35-sys/ohmatdyt_crm.git ohmatdyt-crm
cd ohmatdyt-crm/ohmatdyt-crm
```

### 4. Prepare Environment
```bash
# Copy environment file
cp .env.example .env.prod

# Update IP addresses
sed -i 's/192\.168\.31\.248/10.24.2.187/g' .env.prod
sed -i 's/192\.168\.31\.249/10.24.2.187/g' .env.prod

# IMPORTANT: Edit and update passwords!
nano .env.prod
# Change:
# - POSTGRES_PASSWORD
# - JWT_SECRET
# - SMTP settings if needed
```

### 5. Create Docker Volumes
```bash
docker volume create ohmatdyt_crm_db-data
docker volume create ohmatdyt_crm_media
docker volume create ohmatdyt_crm_static

# Verify
docker volume ls | grep ohmatdyt_crm
```

### 6. Build and Start
```bash
# Build images (takes 10-15 minutes)
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Wait for startup
sleep 20

# Check status
docker compose ps
```

### 7. Run Database Migrations
```bash
# Wait a bit more for DB to be ready
sleep 10

# Run migrations
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T api alembic upgrade head
```

### 8. Verify Deployment
```bash
# Check all containers are running
docker compose ps

# View logs
docker compose logs --tail=50

# Test API
curl http://localhost/api/docs
curl http://localhost
```

## Access URLs

- Frontend: http://10.24.2.187
- API Docs: http://10.24.2.187/api/docs
- API Direct: http://10.24.2.187:8000

## Post-Deployment

### Create Superuser
```bash
cd ~/ohmatdyt-crm/ohmatdyt-crm
docker compose exec api python -m app.scripts.create_superuser
```

### View Logs
```bash
# All logs
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f frontend
docker compose logs -f nginx
```

### Restart Services
```bash
# All services
docker compose restart

# Specific service
docker compose restart api
```

### Stop/Start
```bash
# Stop
docker compose down

# Start
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Troubleshooting

### If containers won't start:
```bash
# Check logs
docker compose logs

# Check available ports
sudo netstat -tulpn | grep -E '(80|443|8000|3000)'

# Restart Docker
sudo systemctl restart docker
```

### If you need to rebuild:
```bash
# Stop everything
docker compose down

# Remove volumes (CAUTION: This deletes data!)
# docker volume rm ohmatdyt_crm_db-data
# docker volume rm ohmatdyt_crm_media
# docker volume rm ohmatdyt_crm_static

# Rebuild
docker compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache

# Start
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Backup Database

```bash
# Create backup
docker compose exec db pg_dump -U ohm_user ohm_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker compose exec -T db psql -U ohm_user ohm_db < backup_file.sql
```

## Update Application

```bash
cd ~/ohmatdyt-crm/ohmatdyt-crm

# Pull latest changes
git pull origin main

# Rebuild (if code changed)
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Restart
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Run migrations
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T api alembic upgrade head
```

## ONE-LINE DEPLOYMENT COMMAND

After connecting to server via SSH, you can use this single command:

```bash
cd ~ && \
git clone https://github.com/puzakroman35-sys/ohmatdyt_crm.git ohmatdyt-crm && \
cd ohmatdyt-crm/ohmatdyt-crm && \
cp .env.example .env.prod && \
sed -i 's/192\.168\.31\.248/10.24.2.187/g' .env.prod && \
sed -i 's/192\.168\.31\.249/10.24.2.187/g' .env.prod && \
docker volume create ohmatdyt_crm_db-data && \
docker volume create ohmatdyt_crm_media && \
docker volume create ohmatdyt_crm_static && \
docker compose -f docker-compose.yml -f docker-compose.prod.yml build && \
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d && \
sleep 30 && \
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T api alembic upgrade head && \
docker compose ps
```

**Note**: After running this, you still need to:
1. Edit `.env.prod` to update passwords
2. Restart services: `docker compose restart`
3. Create superuser if needed

---

That's it! Your application should now be running on http://10.24.2.187
