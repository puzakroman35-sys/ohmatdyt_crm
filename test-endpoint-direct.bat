@echo off
echo ========================================
echo Testing Category Access Endpoint
echo ========================================
echo.

set USER_ID=abc61c5f-1658-4a10-87de-3e7056f60c69

echo Testing: GET /api/users/%USER_ID%/category-access
echo.

curl -v http://localhost:8000/api/users/%USER_ID%/category-access 2>&1

echo.
echo ========================================
echo Press any key to exit...
pause >nul
