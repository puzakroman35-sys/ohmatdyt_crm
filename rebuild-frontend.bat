@echo off
REM FE-012: Rebuild frontend with new CategorySelector component

echo ========================================
echo Rebuilding Frontend Docker Image
echo ========================================

cd /d d:\AI_boost\ohmatdyt_crm\ohmatdyt-crm

echo.
echo [1/3] Building frontend image...
docker compose build frontend

echo.
echo [2/3] Stopping frontend container...
docker compose stop frontend

echo.
echo [3/3] Starting frontend container...
docker compose up -d frontend

echo.
echo ========================================
echo Frontend rebuild complete!
echo ========================================
echo.
echo Check status:
docker compose ps frontend

echo.
echo Frontend available at: http://localhost:3000
echo.
pause
