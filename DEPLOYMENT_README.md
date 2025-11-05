# Deployment Files Summary

## Server Information
- **IP**: 10.24.2.187
- **User**: rpadmin  
- **Project**: Ohmatdyt CRM

## Available Deployment Options

### 📄 Files Created

1. **deploy-prod-simple.ps1** - Automated PowerShell deployment script
   - Runs from Windows machine
   - Automates full deployment process
   - Requires SSH access

2. **deploy-server-side.sh** - Bash script to run on server
   - Upload to server and execute
   - Interactive prompts for passwords
   - Full automation on Linux side

3. **update-prod-10.24.2.187.ps1** - Quick update script
   - For subsequent updates after initial deployment
   - Fast git pull and restart

4. **DEPLOYMENT_GUIDE_10.24.2.187.md** - Complete deployment guide
   - Detailed instructions
   - Troubleshooting
   - Security checklist

5. **QUICK_DEPLOY_MANUAL.md** - Quick manual deployment
   - Step-by-step commands
   - One-line deployment option
   - Best for SSH-only deployment

## Recommended Deployment Method

### Option A: Automated from Windows (Recommended)

```powershell
# From your Windows machine
powershell -ExecutionPolicy Bypass -File .\deploy-prod-simple.ps1
```

This will:
- Install Docker on server
- Clone repository
- Configure environment
- Build and start services
- Run migrations

### Option B: Manual SSH Deployment (Fastest)

1. **Connect to server:**
```bash
ssh rpadmin@10.24.2.187
```

2. **Run one-line deployment:**
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
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T api alembic upgrade head
```

3. **Update passwords (IMPORTANT!):**
```bash
nano .env.prod
# Change POSTGRES_PASSWORD and JWT_SECRET
docker compose restart
```

4. **Create superuser:**
```bash
docker compose exec api python -m app.scripts.create_superuser
```

### Option C: Upload and Run Server Script

1. **Upload script to server:**
```powershell
# From Windows
scp deploy-server-side.sh rpadmin@10.24.2.187:~/
```

2. **SSH to server and run:**
```bash
ssh rpadmin@10.24.2.187
chmod +x ~/deploy-server-side.sh
./deploy-server-side.sh
```

## After Deployment

### Access Application
- Frontend: http://10.24.2.187
- API Docs: http://10.24.2.187/api/docs
- API Direct: http://10.24.2.187:8000

### Check Status
```bash
ssh rpadmin@10.24.2.187
cd ~/ohmatdyt-crm/ohmatdyt-crm
docker compose ps
docker compose logs -f
```

### Update Later
```powershell
# From Windows
.\update-prod-10.24.2.187.ps1
```

Or on server:
```bash
cd ~/ohmatdyt-crm/ohmatdyt-crm
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker compose exec -T api alembic upgrade head
```

## Important Notes

1. **Change default passwords** in .env.prod after deployment!
2. **Backup database** regularly
3. **Monitor logs** for errors: `docker compose logs -f`
4. **Setup firewall** if needed
5. **Configure SSL/HTTPS** for production use

## Troubleshooting

### Services won't start
```bash
docker compose logs
docker compose restart
```

### Database connection errors
```bash
docker compose logs db
docker compose restart db api
```

### Need to rebuild everything
```bash
docker compose down
docker compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Support

For detailed information, see:
- DEPLOYMENT_GUIDE_10.24.2.187.md - Full guide
- QUICK_DEPLOY_MANUAL.md - Quick reference

---

**Quick Start**: Use Option B (one-line deployment) for fastest setup!
