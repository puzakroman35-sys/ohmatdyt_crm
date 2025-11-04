@echo off
echo ========================================
echo Testing Category Access Endpoint
echo ========================================
echo.

set USER_ID=abc61c5f-1658-4a10-87de-3e7056f60c69
set API_URL=http://localhost:8000/api/users/%USER_ID%/category-access

echo Testing GET %API_URL%
echo.

curl -X GET "%API_URL%" ^
  -H "Content-Type: application/json" ^
  -v

echo.
echo ========================================
echo Press any key to exit...
pause >nul
