@echo off
echo ==========================================
echo   Rebuilding API Container
echo ==========================================
cd /d "%~dp0"
echo Stopping API...
docker-compose stop api
echo.
echo Rebuilding API...
docker-compose build api
echo.
echo Starting API...
docker-compose up -d api
echo.
echo Done! API has been rebuilt and restarted.
echo.
echo Checking logs...
timeout /t 3 >nul
docker logs ohmatdyt_crm-api-1 --tail 10
pause
