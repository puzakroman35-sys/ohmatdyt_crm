@echo off
echo ========================================
echo Detailed BE-018 Check
echo ========================================
echo.

echo 1. Checking if category-access routes exist in container...
docker exec ohmatdyt_crm-api-1 grep -c "category-access" /app/app/routers/users.py

echo.
echo 2. Checking actual endpoint definitions...
docker exec ohmatdyt_crm-api-1 grep -A 2 "@router" /app/app/routers/users.py | grep -B 1 "category-access"

echo.
echo 3. Checking UserCategoryAccess model in container...
docker exec ohmatdyt_crm-api-1 grep -c "class UserCategoryAccess" /app/app/models.py

echo.
echo 4. Checking last modification time of users.py in container...
docker exec ohmatdyt_crm-api-1 ls -lh /app/app/routers/users.py

echo.
echo ========================================
echo.
echo If count is 4+ and model exists, BE-018 is deployed.
echo.
echo Press any key to exit...
pause >nul
