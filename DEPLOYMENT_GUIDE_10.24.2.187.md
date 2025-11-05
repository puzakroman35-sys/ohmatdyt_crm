# 🚀 Deployment Guide - New Production Server

## Server Information
- **IP Address**: `10.24.2.187`
- **User**: `rpadmin`
- **Project Directory**: `~/ohmatdyt-crm`

---

## 📋 Prerequisites

### On Your Local Machine
- PowerShell (Windows)
- SSH client configured
- Access to the server

### On the Server
- Ubuntu/Debian Linux
- sudo privileges
- SSH access enabled

---

## 🎯 Deployment Options

### Option 1: Automated Deployment from Local Machine (Recommended)

This option runs everything from your Windows machine and sets up the server automatically.

```powershell
# Run the full automated deployment script
.\deploy-new-prod-server.ps1

# Or with parameters:
.\deploy-new-prod-server.ps1 -ServerIP "10.24.2.187" -ServerUser "rpadmin"

# Skip server setup if already done:
.\deploy-new-prod-server.ps1 -SkipServerSetup

# Skip Docker installation if already installed:
.\deploy-new-prod-server.ps1 -SkipDockerInstall
```

**What this script does:**
1. ✅ Tests SSH connection
2. ✅ Updates server packages
3. ✅ Installs Docker and Docker Compose
4. ✅ Clones the repository
5. ✅ Configures environment files
6. ✅ Creates Docker volumes
7. ✅ Builds Docker images
8. ✅ Starts all services
9. ✅ Runs database migrations
10. ✅ Performs health checks

---

### Option 2: Manual Deployment on Server

If you prefer to work directly on the server:

#### Step 1: Connect to Server
```bash
ssh rpadmin@10.24.2.187
```

#### Step 2: Install Docker (if not installed)
```bash
# Remove old versions
sudo apt-get remove docker docker-engine docker.io containerd runc

# Update packages
sudo apt-get update

# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

#### Step 3: Clone Repository
```bash
cd ~
git clone https://github.com/puzakroman35-sys/ohmatdyt_crm.git ohmatdyt-crm
cd ohmatdyt-crm/ohmatdyt-crm
```

#### Step 4: Run Server-Side Deployment Script
```bash
# Make script executable
chmod +x deploy-server-side.sh

# Run deployment
./deploy-server-side.sh
```

Or follow manual steps below...

#### Step 5: Configure Environment (Manual)
```bash
# Copy and edit .env.prod
cp .env.example .env.prod
nano .env.prod

# Update these values:
# - ALLOWED_HOSTS=10.24.2.187,localhost,127.0.0.1
# - CORS_ORIGINS=http://10.24.2.187,http://localhost
# - NGINX_SERVER_NAME=10.24.2.187
# - POSTGRES_PASSWORD=<strong-password>
# - JWT_SECRET=<strong-secret>
```

#### Step 6: Create Docker Volumes
```bash
docker volume create ohmatdyt_crm_db-data
docker volume create ohmatdyt_crm_media
docker volume create ohmatdyt_crm_static
```

#### Step 7: Build and Start
```bash
# Build images (10-15 minutes)
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Wait for services to start
sleep 20

# Check status
docker compose ps
```

#### Step 8: Run Migrations
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T api alembic upgrade head
```

---

## 🔄 Updates and Maintenance

### Quick Update Script

For subsequent updates after initial deployment:

```powershell
# From your local machine
.\update-prod-10.24.2.187.ps1
```

This script will:
- Fetch latest changes from git
- Show what will be updated
- Pull changes
- Rebuild images (optional)
- Restart services
- Run migrations

### Manual Update on Server

```bash
ssh rpadmin@10.24.2.187
cd ~/ohmatdyt-crm/ohmatdyt-crm

# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Run migrations
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T api alembic upgrade head
```

---

## 🌐 Access URLs

After successful deployment:

- **Frontend**: http://10.24.2.187
- **API Documentation**: http://10.24.2.187/api/docs
- **API Direct**: http://10.24.2.187:8000

---

## 🔧 Useful Commands

### On the Server

```bash
# Navigate to project
cd ~/ohmatdyt-crm/ohmatdyt-crm

# View all containers
docker compose ps

# View logs
docker compose logs -f                # All services
docker compose logs -f api           # API only
docker compose logs -f frontend      # Frontend only
docker compose logs -f nginx         # Nginx only

# Restart services
docker compose restart               # All services
docker compose restart api          # Specific service

# Stop everything
docker compose down

# Start everything
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Execute commands in containers
docker compose exec api bash        # API shell
docker compose exec db psql -U ohm_user -d ohm_db  # Database shell

# View resource usage
docker stats

# Clean up unused resources
docker system prune -a
```

### Create Superuser

```bash
cd ~/ohmatdyt-crm/ohmatdyt-crm
docker compose exec api python -m app.scripts.create_superuser
```

### Database Backup

```bash
# Backup
docker compose exec db pg_dump -U ohm_user ohm_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
docker compose exec -T db psql -U ohm_user ohm_db < backup_file.sql
```

---

## 🔒 Security Checklist

- [ ] Change default passwords in `.env.prod`
- [ ] Update `JWT_SECRET` to a strong random value
- [ ] Configure firewall (ufw)
- [ ] Setup SSL/HTTPS certificates
- [ ] Configure regular backups
- [ ] Setup monitoring and logging
- [ ] Restrict SSH access (disable password auth, use keys)
- [ ] Keep Docker and system packages updated

### Basic Firewall Setup

```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

---

## 🐛 Troubleshooting

### Services won't start
```bash
# Check logs
docker compose logs

# Check if ports are available
sudo netstat -tulpn | grep -E '(80|443|8000|3000|5432|6379)'

# Restart Docker daemon
sudo systemctl restart docker
```

### Database connection issues
```bash
# Check database logs
docker compose logs db

# Test database connection
docker compose exec api python -c "from app.core.database import engine; print(engine.connect())"
```

### Frontend not accessible
```bash
# Check nginx logs
docker compose logs nginx

# Check frontend logs
docker compose logs frontend

# Verify nginx config
docker compose exec nginx nginx -t
```

### Out of disk space
```bash
# Check disk usage
df -h

# Clean Docker resources
docker system prune -a --volumes

# Remove old images
docker image prune -a
```

---

## 📞 Support

If you encounter issues:

1. Check the logs: `docker compose logs -f`
2. Verify all services are running: `docker compose ps`
3. Check environment configuration: `cat .env.prod`
4. Review this documentation
5. Check GitHub issues

---

## 📝 Notes

- **First deployment** takes 10-15 minutes due to image building
- **Updates** are much faster (1-2 minutes)
- Database data persists in Docker volumes
- Media files are stored in persistent volumes
- Regular backups are recommended

---

## 🎉 Quick Start Summary

```powershell
# From your Windows machine, run:
.\deploy-new-prod-server.ps1

# Then access:
# http://10.24.2.187
```

That's it! The script handles everything automatically.

---

**Last Updated**: 2025-11-05
**Server**: rpadmin@10.24.2.187
**Project**: Ohmatdyt CRM
