@echo off
echo === Copying production config ===
scp ohmatdyt-crm/.env.prod rpuzak@192.168.31.248:~/ohmatdyt-crm/.env

echo.
echo === Connecting to server and deploying ===
ssh rpuzak@192.168.31.248 "cd ~/ohmatdyt-crm && echo '=== Checking Docker ===' && docker --version && docker-compose --version && echo '=== Stopping old containers ===' && docker-compose -f docker-compose.yml -f docker-compose.prod.yml down 2>nul || echo 'No containers to stop' && echo '=== Building images ===' && docker-compose -f docker-compose.yml -f docker-compose.prod.yml build && echo '=== Starting containers ===' && docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d && echo '=== Waiting for services ===' && timeout /t 20 /nobreak && echo '=== Running migrations ===' && docker-compose exec -T api alembic upgrade head && echo '=== Container status ===' && docker-compose ps && echo. && echo '=== DEPLOYMENT COMPLETE ===' && echo 'URL: http://192.168.31.248' && echo 'API: http://192.168.31.248/api/docs'"

echo.
echo Done!
