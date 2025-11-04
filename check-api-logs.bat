@echo off
echo ========================================
echo Checking API Container Logs
echo ========================================
echo.

docker compose logs api --tail=100

echo.
echo ========================================
echo Press any key to exit...
pause >nul
