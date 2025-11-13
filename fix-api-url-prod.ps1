# Fix NEXT_PUBLIC_API_URL on Production Server
# This script fixes the double /api/api issue

$SERVER = "rpadmin@10.24.2.187"

Write-Host "=== Fixing API URL on Production ===" -ForegroundColor Green

# Простіший підхід - виконуємо команди окремо
Write-Host "Step 1: Backing up current .env..." -ForegroundColor Yellow
ssh $SERVER "cd ~/ohmatdyt_crm && cp .env .env.backup"

Write-Host "Step 2: Updating NEXT_PUBLIC_API_URL..." -ForegroundColor Yellow
ssh $SERVER "cd ~/ohmatdyt_crm && sed -i 's|NEXT_PUBLIC_API_URL=/api|NEXT_PUBLIC_API_URL=https://10.24.2.187|g' .env"

Write-Host "Step 3: Verifying changes..." -ForegroundColor Yellow
ssh $SERVER "cd ~/ohmatdyt_crm && grep 'NEXT_PUBLIC_API_URL' .env"

Write-Host "Step 4: Rebuilding frontend..." -ForegroundColor Yellow
ssh $SERVER "cd ~/ohmatdyt_crm && docker-compose build frontend"

Write-Host "Step 5: Restarting frontend..." -ForegroundColor Yellow
ssh $SERVER "cd ~/ohmatdyt_crm && docker-compose up -d frontend"

Write-Host "Step 6: Checking status..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
ssh $SERVER "cd ~/ohmatdyt_crm && docker-compose ps frontend"

Write-Host "`n=== Done! ===" -ForegroundColor Green
Write-Host "Login should now work correctly at https://10.24.2.187" -ForegroundColor Cyan
Write-Host "Backup saved as .env.backup" -ForegroundColor Gray
