@echo off
echo ==========================================
echo   Starting Frontend (Development Mode)
echo ==========================================
echo.
echo Services: db, redis, api, frontend
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo.
cd /d "%~dp0"
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build db redis api frontend
