@echo off
REM FE-012: Complete rebuild of API and Frontend with category-access feature

echo ========================================
echo FE-012: Rebuilding API + Frontend
echo Category Access Management
echo ========================================

cd /d d:\AI_boost\ohmatdyt_crm\ohmatdyt-crm

echo.
echo [1/6] Building API image...
docker compose build api

echo.
echo [2/6] Building Frontend image...
docker compose build frontend

echo.
echo [3/6] Stopping old containers...
docker compose stop api frontend

echo.
echo [4/6] Starting API container...
docker compose up -d api

echo.
echo [5/6] Waiting for API to be ready...
timeout /t 5 /nobreak >nul

echo.
echo [6/6] Starting Frontend container...
docker compose up -d frontend

echo.
echo ========================================
echo Rebuild Complete!
echo ========================================

echo.
echo Checking container status...
docker compose ps api frontend

echo.
echo ========================================
echo URLs:
echo ========================================
echo Frontend: http://localhost:3000
echo API:      http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo ========================================
echo Testing category-access endpoint:
echo ========================================
echo.
echo First, login to get token:
echo   POST http://localhost:8000/api/auth/login
echo   Body: {"username": "admin", "password": "admin123"}
echo.
echo Then test category-access:
echo   GET http://localhost:8000/api/users/{user_id}/category-access
echo   Header: Authorization: Bearer {token}
echo.
pause
