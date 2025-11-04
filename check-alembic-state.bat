@echo off
echo ========================================
echo Checking Current Migration State
echo ========================================
echo.

echo 1. Current version in database:
docker exec ohmatdyt_crm-db-1 psql -U crm_user -d ohmatdyt_crm -c "SELECT version_num FROM alembic_version;"

echo.
echo 2. Alembic current state:
docker exec ohmatdyt_crm-api-1 alembic current

echo.
echo 3. Alembic history:
docker exec ohmatdyt_crm-api-1 alembic history

echo.
echo ========================================
echo Press any key to exit...
pause >nul
