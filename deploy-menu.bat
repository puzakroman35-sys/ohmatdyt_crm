@echo off
REM ============================================================================
REM Quick Deploy для crm.ohmatdyt.com.ua
REM ============================================================================

echo.
echo ============================================================================
echo   OHMATDYT CRM - PRODUCTION DEPLOYMENT
echo ============================================================================
echo.

echo Виберіть варіант розгортання:
echo.
echo   1. Автоматичне розгортання з Windows (PowerShell)
echo   2. Показати інструкції для ручного розгортання
echo   3. Відкрити детальну документацію
echo   4. Вийти
echo.

choice /C 1234 /N /M "Ваш вибір (1-4): "

if errorlevel 4 goto :end
if errorlevel 3 goto :documentation
if errorlevel 2 goto :manual
if errorlevel 1 goto :automatic

:automatic
echo.
echo ============================================================================
echo   Запуск автоматичного розгортання...
echo ============================================================================
echo.
powershell -ExecutionPolicy Bypass -File ".\deploy-crm-ohmatdyt.ps1"
goto :end

:manual
echo.
echo ============================================================================
echo   РУЧНЕ РОЗГОРТАННЯ
echo ============================================================================
echo.
echo Крок 1: Підключитися до сервера
echo    ssh root@crm.ohmatdyt.com.ua
echo.
echo Крок 2: Перейти в папку проекту
echo    cd ~/ohmatdyt-crm
echo.
echo Крок 3: Завантажити .env.prod на сервер
echo    З Windows: scp f:\ohmatdyt_crm\ohmatdyt-crm\.env.prod root@crm.ohmatdyt.com.ua:~/ohmatdyt-crm/.env.prod
echo.
echo Крок 4: Запустити deployment скрипт на сервері
echo    chmod +x deploy-crm-ohmatdyt.sh
echo    ./deploy-crm-ohmatdyt.sh
echo.
echo Детальні інструкції: DEPLOYMENT_CRM_OHMATDYT_COM_UA.md
echo.
pause
goto :end

:documentation
echo.
echo ============================================================================
echo   ДОКУМЕНТАЦІЯ
echo ============================================================================
echo.
echo Доступні файли документації:
echo.
echo   1. QUICKSTART_CRM_OHMATDYT.md          - Швидкий старт
echo   2. DEPLOYMENT_CRM_OHMATDYT_COM_UA.md   - Детальна інструкція
echo   3. DEPLOYMENT_CHECKLIST.txt            - Контрольний список
echo   4. DEPLOYMENT_SUMMARY.md               - Резюме підготовки
echo.

choice /C 1234 /N /M "Відкрити файл (1-4): "

if errorlevel 4 start notepad DEPLOYMENT_SUMMARY.md
if errorlevel 3 start notepad DEPLOYMENT_CHECKLIST.txt
if errorlevel 2 start notepad DEPLOYMENT_CRM_OHMATDYT_COM_UA.md
if errorlevel 1 start notepad QUICKSTART_CRM_OHMATDYT.md

goto :end

:end
echo.
echo Дякую за використання!
echo.
pause
