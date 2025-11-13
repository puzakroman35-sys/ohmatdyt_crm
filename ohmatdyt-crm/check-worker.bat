@echo off
cd /d d:\AI_boost\ohmatdyt_crm\ohmatdyt-crm
echo ========================================
echo Checking Worker Logs
echo ========================================
echo.

docker compose logs worker --tail=50

echo.
echo ========================================
echo Checking notification_logs table
echo ========================================
echo.

docker exec -it ohmatdyt_crm-db-1 psql -U ohm_user -d ohm_db -c "SELECT notification_type, recipient_email, status, subject, created_at FROM notification_logs ORDER BY created_at DESC LIMIT 10;"

echo.
echo Press any key to exit...
pause >nul
