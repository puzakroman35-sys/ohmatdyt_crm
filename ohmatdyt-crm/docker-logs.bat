@echo off
echo ==========================================
echo   Docker Logs (Follow Mode)
echo ==========================================
echo.
echo Press Ctrl+C to exit
echo.
cd /d "%~dp0"

if "%1"=="" (
    echo Showing all services logs...
    docker-compose logs -f
) else (
    echo Showing logs for: %1
    docker-compose logs -f %1
)
