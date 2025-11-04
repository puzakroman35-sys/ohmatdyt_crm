@echo off
echo ========================================
echo Checking Migration History
echo ========================================
echo.

echo Current migrations in alembic_version table:
docker exec ohmatdyt_crm-db-1 psql -U crm_user -d ohmatdyt_crm -c "SELECT * FROM alembic_version;"

echo.
echo Available migration files:
dir /B "ohmatdyt-crm\api\alembic\versions\*.py"

echo.
echo ========================================
echo Press any key to exit...
pause >nul
