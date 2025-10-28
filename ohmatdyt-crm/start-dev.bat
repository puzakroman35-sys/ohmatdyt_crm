@echo off
echo ==========================================
echo   Starting Ohmatdyt CRM (Full Stack)
echo ==========================================
echo.
echo Services: db, redis, api, worker, beat, frontend, nginx
echo.
echo Access URLs:
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo   - Nginx: http://localhost:80
echo.
cd /d "%~dp0"
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
