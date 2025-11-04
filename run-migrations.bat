@echo off
echo ========================================
echo Running Database Migrations
echo ========================================
echo.

echo Running alembic upgrade head...
docker exec ohmatdyt_crm-api-1 alembic upgrade head

echo.
echo ========================================
echo.
echo Checking if executor_category_access table exists...
docker exec ohmatdyt_crm-db-1 psql -U postgres -d ohmatdyt_crm -c "\dt executor_category_access"

echo.
echo ========================================
echo.
echo Migration completed!
echo.
echo Press any key to exit...
pause >nul
