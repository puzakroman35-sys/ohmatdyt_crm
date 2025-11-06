@echo off
REM Commit changes to git for new production server IP

cd /d d:\AI_boost\ohmatdyt_crm\ohmatdyt-crm

echo ========================================
echo Git Commit - New Production Server IP
echo ========================================
echo.

echo Checking git status...
git status
echo.

echo Staging changes...
git add .env.prod docker-compose.prod.yml
echo.

echo Committing changes...
git commit -m "Update IP addresses for new production server 10.24.2.187"
echo.

echo Pushing to GitHub...
git push origin main
echo.

echo ========================================
echo Done!
echo ========================================
pause
