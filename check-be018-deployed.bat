@echo off
echo ========================================
echo Checking if API container has BE-018 code
echo ========================================
echo.

echo Checking users.py for category-access endpoints...
docker exec ohmatdyt_crm-api-1 grep -n "category-access" /app/app/routers/users.py

echo.
echo ========================================
echo.
echo If you see 4 endpoints above, BE-018 is deployed.
echo If you see "No such file" or nothing, need to rebuild API.
echo.
echo Press any key to exit...
pause >nul
