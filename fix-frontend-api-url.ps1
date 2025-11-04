# Fix Frontend API URL on Production
# This script deploys the fix for hardcoded localhost:8000 issue

Write-Host "=== Fixing Frontend API URL Configuration ===" -ForegroundColor Cyan

# Step 1: Commit changes locally
Write-Host "`n[1/4] Committing changes locally..." -ForegroundColor Yellow
git add ohmatdyt-crm/.env.prod ohmatdyt-crm/docker-compose.yml
git commit -m "Fix: Remove hardcoded NEXT_PUBLIC_API_URL from docker-compose.yml"
git push origin main

# Step 2: SSH to server and pull changes
Write-Host "`n[2/4] Pulling changes on production server..." -ForegroundColor Yellow
ssh rpuzak@192.168.31.249 "cd ~/ohmatdyt_crm && git pull origin main"

# Step 3: Rebuild and restart frontend container
Write-Host "`n[3/4] Rebuilding frontend container..." -ForegroundColor Yellow
ssh rpuzak@192.168.31.249 "cd ~/ohmatdyt_crm/ohmatdyt-crm && docker compose -f docker-compose.yml -f docker-compose.prod.yml build frontend"

Write-Host "`n[4/4] Restarting frontend container..." -ForegroundColor Yellow
ssh rpuzak@192.168.31.249 "cd ~/ohmatdyt_crm/ohmatdyt-crm && docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d frontend"

# Step 4: Verify
Write-Host "`n=== Verification ===" -ForegroundColor Cyan
Write-Host "Check the following:" -ForegroundColor Green
Write-Host "1. Frontend logs: ssh rpuzak@192.168.31.249 'cd ~/ohmatdyt_crm/ohmatdyt-crm && docker compose logs frontend | tail -20'" -ForegroundColor White
Write-Host "2. Try login at: https://192.168.31.249/login" -ForegroundColor White
Write-Host "3. Check browser console for API requests (should go to http://192.168.31.249/api)" -ForegroundColor White

Write-Host "`n=== Done! ===" -ForegroundColor Green
