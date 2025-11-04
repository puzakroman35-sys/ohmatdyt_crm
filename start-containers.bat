@echo off
echo ========================================
echo Starting Docker Containers
echo ========================================
echo.

echo Stopping any running containers...
docker compose down

echo.
echo Building and starting containers...
docker compose up -d --build

echo.
echo Waiting for containers to start...
timeout /t 5 /nobreak >nul

echo.
echo Checking container status...
docker ps

echo.
echo ========================================
echo.
echo Containers should be running now.
echo Check logs with: docker compose logs -f
echo.
echo Press any key to exit...
pause >nul
