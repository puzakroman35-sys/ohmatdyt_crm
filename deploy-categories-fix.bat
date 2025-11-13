@echo off
echo === Deploying categories search fix to production ===

echo.
echo 1. Pulling latest code...
ssh rpadmin@10.24.2.187 "cd ohmatdyt-crm/ohmatdyt-crm && git pull"

echo.
echo 2. Building API container...
ssh rpadmin@10.24.2.187 "cd ohmatdyt-crm/ohmatdyt-crm && docker compose -f docker-compose.yml -f docker-compose.prod.yml build api"

echo.
echo 3. Restarting API...
ssh rpadmin@10.24.2.187 "cd ohmatdyt-crm/ohmatdyt-crm && docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d api"

echo.
echo === Deployment complete! ===
pause
