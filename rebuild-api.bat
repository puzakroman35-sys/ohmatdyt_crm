@echo off
REM BE-018 + FE-012: Check and rebuild API with category-access endpoints

echo ========================================
echo Checking API Code and Rebuilding
echo ========================================

cd /d d:\AI_boost\ohmatdyt_crm\ohmatdyt-crm

echo.
echo [CHECK] Verifying category-access endpoints exist in code...
findstr /C:"category-access" api\app\routers\users.py
if %ERRORLEVEL% EQU 0 (
    echo ✓ category-access endpoints found in code
) else (
    echo ✗ category-access endpoints NOT found in code
    echo ERROR: Code may be outdated!
    pause
    exit /b 1
)

echo.
echo [1/4] Building API image...
docker compose build api

echo.
echo [2/4] Stopping API container...
docker compose stop api

echo.
echo [3/4] Starting API container...
docker compose up -d api

echo.
echo [4/4] Waiting for API to be healthy...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo Checking API Health
echo ========================================
docker compose ps api

echo.
echo Testing category-access endpoint...
echo URL: http://localhost:8000/api/users/{user_id}/category-access
echo.
echo Try this curl command:
echo curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/users/abc61c5f-1658-4a10-87de-3e7056f60c69/category-access
echo.
pause
