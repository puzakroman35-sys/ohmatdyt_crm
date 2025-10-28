@echo off
echo ==========================================
echo   Stopping Ohmatdyt CRM
echo ==========================================
echo.
cd /d "%~dp0"
docker-compose down
echo.
echo All services stopped.
pause
