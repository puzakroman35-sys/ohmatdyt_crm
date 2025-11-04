@echo off
echo ========================================
echo Creating executor_category_access Table Manually
echo ========================================
echo.

echo Creating table via SQL...
docker exec ohmatdyt_crm-db-1 psql -U crm_user -d ohmatdyt_crm -c "CREATE TABLE IF NOT EXISTS executor_category_access (id UUID PRIMARY KEY, executor_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE, category_id UUID NOT NULL REFERENCES categories(id) ON DELETE CASCADE, created_at TIMESTAMP NOT NULL DEFAULT NOW(), updated_at TIMESTAMP NOT NULL DEFAULT NOW(), UNIQUE(executor_id, category_id)); CREATE INDEX IF NOT EXISTS ix_executor_category_access_executor_id ON executor_category_access(executor_id); CREATE INDEX IF NOT EXISTS ix_executor_category_access_category_id ON executor_category_access(category_id);"

echo.
echo Checking table...
docker exec ohmatdyt_crm-db-1 psql -U crm_user -d ohmatdyt_crm -c "\d executor_category_access"

echo.
echo ========================================
echo.
echo Table created successfully!
echo.
echo Press any key to exit...
pause >nul
