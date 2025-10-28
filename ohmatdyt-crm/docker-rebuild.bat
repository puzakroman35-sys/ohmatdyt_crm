@echo off
echo ==========================================
echo   Rebuilding Ohmatdyt CRM (Clean Build)
echo ==========================================
echo.
echo This will:
echo   - Stop all services
echo   - Remove containers and images
echo   - Rebuild everything from scratch
echo.
pause
echo.
cd /d "%~dp0"
echo Stopping services...
docker-compose down
echo.
echo Removing old images...
docker-compose down --rmi all
echo.
echo Rebuilding with no cache...
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache
echo.
echo Done! Use start-dev.bat to start services.
pause
