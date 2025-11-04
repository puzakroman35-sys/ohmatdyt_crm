@echo off
echo ========================================
echo API Logs - Last 100 lines
echo ========================================
echo.

docker logs ohmatdyt_crm-api-1 --tail=100

echo.
echo ========================================
echo.
echo Look for errors related to category-access endpoint above
echo.
echo Press any key to exit...
pause >nul
