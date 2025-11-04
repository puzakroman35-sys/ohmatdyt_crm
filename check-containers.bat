@echo off
echo ========================================
echo Checking Running Docker Containers
echo ========================================
echo.

docker ps -a

echo.
echo ========================================
echo Press any key to exit...
pause >nul
