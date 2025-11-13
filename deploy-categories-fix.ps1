# Deploy categories search fix to production
Write-Host "=== Deploying categories search fix to production ===" -ForegroundColor Green

$server = "rpadmin@10.24.2.187"
$remoteDir = "ohmatdyt-crm/ohmatdyt-crm"

# Step 1: Pull latest code
Write-Host "`n1. Pulling latest code..." -ForegroundColor Cyan
ssh $server "cd $remoteDir && git pull"

# Step 2: Build API
Write-Host "`n2. Building API container..." -ForegroundColor Cyan
ssh $server "cd $remoteDir && docker compose -f docker-compose.yml -f docker-compose.prod.yml build api"

# Step 3: Restart API
Write-Host "`n3. Restarting API..." -ForegroundColor Cyan
ssh $server "cd $remoteDir && docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d api"

Write-Host "`n=== Deployment complete! ===" -ForegroundColor Green
