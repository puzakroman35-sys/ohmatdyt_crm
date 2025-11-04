# INF-003 Simple Deployment Script
# Простий скрипт розгортання для production сервера

Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         INF-003 Production Deployment (Simple)              ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$server = "rpuzak@192.168.31.248"
$password = "cgf34R"

Write-Host "[INFO] Сервер: $server" -ForegroundColor Yellow
Write-Host "[INFO] Пароль: $password" -ForegroundColor Yellow
Write-Host "[INFO] Для кожної команди вводьте пароль вручну`n" -ForegroundColor Yellow

# Крок 1: Перевірка локальних файлів
Write-Host "[STEP 1] Перевірка локальних файлів..." -ForegroundColor Cyan
$files = @(
    "ohmatdyt-crm/nginx/nginx.prod.conf",
    "ohmatdyt-crm/nginx/generate-ssl-certs.sh",
    "ohmatdyt-crm/nginx/setup-letsencrypt.sh",
    "ohmatdyt-crm/nginx/README.md",
    "ohmatdyt-crm/docker-compose.prod.yml",
    "ohmatdyt-crm/.gitignore"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file - ВІДСУТНІЙ!" -ForegroundColor Red
    }
}

# Крок 2: Копіювання файлів
Write-Host "`n[STEP 2] Копіювання файлів на сервер..." -ForegroundColor Cyan
Write-Host "Виконуйте команди по черзі, вводячи пароль: $password`n" -ForegroundColor Yellow

Write-Host "# Створення backup" -ForegroundColor Gray
Write-Host "ssh $server" -ForegroundColor White
Write-Host '  mkdir -p /home/rpuzak/ohmatdyt-crm/backup_inf003' -ForegroundColor White
Write-Host '  cp -r /home/rpuzak/ohmatdyt-crm/nginx /home/rpuzak/ohmatdyt-crm/backup_inf003/ 2>/dev/null' -ForegroundColor White
Write-Host '  exit' -ForegroundColor White
Write-Host ""

Write-Host "# Копіювання файлів через scp" -ForegroundColor Gray
Write-Host "scp ohmatdyt-crm/nginx/nginx.prod.conf ${server}:/home/rpuzak/ohmatdyt-crm/nginx/" -ForegroundColor White
Write-Host "scp ohmatdyt-crm/nginx/generate-ssl-certs.sh ${server}:/home/rpuzak/ohmatdyt-crm/nginx/" -ForegroundColor White
Write-Host "scp ohmatdyt-crm/nginx/setup-letsencrypt.sh ${server}:/home/rpuzak/ohmatdyt-crm/nginx/" -ForegroundColor White
Write-Host "scp ohmatdyt-crm/nginx/README.md ${server}:/home/rpuzak/ohmatdyt-crm/nginx/" -ForegroundColor White
Write-Host "scp ohmatdyt-crm/docker-compose.prod.yml ${server}:/home/rpuzak/ohmatdyt-crm/" -ForegroundColor White
Write-Host "scp ohmatdyt-crm/.gitignore ${server}:/home/rpuzak/ohmatdyt-crm/" -ForegroundColor White
Write-Host ""

Write-Host "# Встановлення прав виконання" -ForegroundColor Gray
Write-Host "ssh $server" -ForegroundColor White
Write-Host '  cd /home/rpuzak/ohmatdyt-crm' -ForegroundColor White
Write-Host '  chmod +x nginx/generate-ssl-certs.sh nginx/setup-letsencrypt.sh' -ForegroundColor White
Write-Host '  exit' -ForegroundColor White
Write-Host ""

# Крок 3: Генерація сертифікатів
Write-Host "`n[STEP 3] Генерація SSL сертифікатів..." -ForegroundColor Cyan
Write-Host "ssh $server" -ForegroundColor White
Write-Host '  cd /home/rpuzak/ohmatdyt-crm/nginx' -ForegroundColor White
Write-Host '  ./generate-ssl-certs.sh' -ForegroundColor White
Write-Host '  ls -la ssl/' -ForegroundColor White
Write-Host '  exit' -ForegroundColor White
Write-Host ""

# Крок 4: Перезапуск Nginx
Write-Host "`n[STEP 4] Перезапуск Nginx з HTTPS..." -ForegroundColor Cyan
Write-Host "ssh $server" -ForegroundColor White
Write-Host '  cd /home/rpuzak/ohmatdyt-crm' -ForegroundColor White
Write-Host '  docker compose -f docker-compose.yml -f docker-compose.prod.yml down nginx' -ForegroundColor White
Write-Host '  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d nginx' -ForegroundColor White
Write-Host '  docker compose -f docker-compose.yml -f docker-compose.prod.yml ps' -ForegroundColor White
Write-Host '  exit' -ForegroundColor White
Write-Host ""

# Крок 5: Перевірка
Write-Host "`n[STEP 5] Перевірка HTTPS..." -ForegroundColor Cyan
Write-Host "curl -k https://192.168.31.248/" -ForegroundColor White
Write-Host "curl -I https://192.168.31.248/api/health/" -ForegroundColor White
Write-Host ""

# Автоматичне копіювання (якщо потрібно)
Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║              АВТОМАТИЧНЕ КОПІЮВАННЯ                          ║" -ForegroundColor Yellow
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Yellow

$answer = Read-Host "Виконати автоматичне копіювання файлів? (y/n)"
if ($answer -eq "y") {
    Write-Host "`nКопіювання файлів... Вводьте пароль: $password`n" -ForegroundColor Cyan
    
    scp ohmatdyt-crm/nginx/nginx.prod.conf ${server}:/home/rpuzak/ohmatdyt-crm/nginx/
    scp ohmatdyt-crm/nginx/generate-ssl-certs.sh ${server}:/home/rpuzak/ohmatdyt-crm/nginx/
    scp ohmatdyt-crm/nginx/setup-letsencrypt.sh ${server}:/home/rpuzak/ohmatdyt-crm/nginx/
    scp ohmatdyt-crm/nginx/README.md ${server}:/home/rpuzak/ohmatdyt-crm/nginx/
    scp ohmatdyt-crm/docker-compose.prod.yml ${server}:/home/rpuzak/ohmatdyt-crm/
    scp ohmatdyt-crm/.gitignore ${server}:/home/rpuzak/ohmatdyt-crm/
    
    Write-Host "`n✓ Копіювання завершено!" -ForegroundColor Green
    Write-Host "Тепер виконайте кроки 3-5 вручну (SSH команди вище)" -ForegroundColor Yellow
} else {
    Write-Host "`nВиконуйте команди вручну (див. вище)" -ForegroundColor Yellow
}

Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              Script Completed                                ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green
