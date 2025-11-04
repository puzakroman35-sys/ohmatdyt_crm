# INF-003 Deployment to Production Server
# Author: AI Assistant
# Date: 2024
# Description: Розгортання Nginx production конфігурації з HTTPS на production сервер

param(
    [string]$Server = "rpuzak@192.168.31.248",
    [string]$RemoteDir = "/home/rpuzak/ohmatdyt-crm"
)

Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         INF-003 Production Deployment Script                ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"

# Список файлів для копіювання
$filesToDeploy = @{
    "ohmatdyt-crm/nginx/nginx.prod.conf" = "nginx/nginx.prod.conf"
    "ohmatdyt-crm/nginx/generate-ssl-certs.sh" = "nginx/generate-ssl-certs.sh"
    "ohmatdyt-crm/nginx/setup-letsencrypt.sh" = "nginx/setup-letsencrypt.sh"
    "ohmatdyt-crm/nginx/README.md" = "nginx/README.md"
    "ohmatdyt-crm/docker-compose.prod.yml" = "docker-compose.prod.yml"
    "ohmatdyt-crm/.gitignore" = ".gitignore"
}

Write-Host "[INFO] Сервер: $Server" -ForegroundColor Yellow
Write-Host "[INFO] Директорія: $RemoteDir" -ForegroundColor Yellow
Write-Host "[INFO] Файлів для копіювання: $($filesToDeploy.Count)`n" -ForegroundColor Yellow

# Перевірка наявності локальних файлів
Write-Host "[STEP 1] Перевірка локальних файлів..." -ForegroundColor Cyan
$missingFiles = @()
foreach ($localFile in $filesToDeploy.Keys) {
    if (Test-Path $localFile) {
        Write-Host "  ✓ $localFile" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $localFile - ВІДСУТНІЙ!" -ForegroundColor Red
        $missingFiles += $localFile
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "`n[ERROR] Відсутні файли: $($missingFiles.Count)" -ForegroundColor Red
    exit 1
}

Write-Host "`n[STEP 2] Створення backup на сервері..." -ForegroundColor Cyan
Write-Host "[INFO] Виконайте команду вручну з паролем: cgf34R" -ForegroundColor Yellow
Write-Host "ssh $Server" -ForegroundColor White
Write-Host "  mkdir -p $RemoteDir/backup_inf003" -ForegroundColor White
Write-Host "  cp -r $RemoteDir/nginx $RemoteDir/backup_inf003/`n" -ForegroundColor White

# Копіювання файлів через scp
Write-Host "[STEP 3] Копіювання файлів на сервер..." -ForegroundColor Cyan
Write-Host "[INFO] Для кожного файлу введіть пароль: cgf34R`n" -ForegroundColor Yellow

$copySuccess = @()
$copyFailed = @()

foreach ($entry in $filesToDeploy.GetEnumerator()) {
    $localPath = $entry.Key
    $remotePath = "$RemoteDir/$($entry.Value)"
    
    Write-Host "  Копіювання: $localPath -> $remotePath" -ForegroundColor Gray
    
    # Створюємо директорію на сервері (якщо потрібна)
    $remoteDir = Split-Path -Parent $entry.Value
    if ($remoteDir) {
        Write-Host "    → Створення директорії: $remoteDir" -ForegroundColor DarkGray
        ssh $Server "mkdir -p $RemoteDir/$remoteDir"
    }
    
    # Копіюємо файл
    $scpCommand = "scp `"$localPath`" `"${Server}:$remotePath`""
    Write-Host "    → $scpCommand" -ForegroundColor DarkGray
    
    try {
        Invoke-Expression $scpCommand
        if ($LASTEXITCODE -eq 0) {
            $copySuccess += $localPath
            Write-Host "    ✓ Успішно скопійовано" -ForegroundColor Green
        } else {
            $copyFailed += $localPath
            Write-Host "    ✗ Помилка копіювання (код: $LASTEXITCODE)" -ForegroundColor Red
        }
    } catch {
        $copyFailed += $localPath
        Write-Host "    ✗ Виключення: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Результати копіювання
Write-Host "`n[STEP 4] Результати копіювання:" -ForegroundColor Cyan
Write-Host "  Успішно: $($copySuccess.Count)" -ForegroundColor Green
Write-Host "  Помилки: $($copyFailed.Count)" -ForegroundColor $(if ($copyFailed.Count -gt 0) { "Red" } else { "Green" })

if ($copyFailed.Count -gt 0) {
    Write-Host "`n  Файли з помилками:" -ForegroundColor Red
    $copyFailed | ForEach-Object { Write-Host "    - $_" -ForegroundColor Red }
}

# Встановлення прав на скрипти
Write-Host "`n[STEP 5] Встановлення прав виконання..." -ForegroundColor Cyan
Write-Host "[INFO] Виконайте команду з паролем: cgf34R" -ForegroundColor Yellow
Write-Host "ssh $Server" -ForegroundColor White
Write-Host "  cd $RemoteDir" -ForegroundColor White
Write-Host "  chmod +x nginx/generate-ssl-certs.sh nginx/setup-letsencrypt.sh`n" -ForegroundColor White

# Перевірка Docker Compose
Write-Host "`n[STEP 6] Перевірка Docker Compose конфігурації..." -ForegroundColor Cyan
Write-Host "[INFO] Виконайте команду з паролем: cgf34R" -ForegroundColor Yellow
Write-Host "ssh $Server" -ForegroundColor White
Write-Host "  cd $RemoteDir" -ForegroundColor White
Write-Host "  docker compose -f docker-compose.yml -f docker-compose.prod.yml config --services`n" -ForegroundColor White

# Інструкції для перезапуску
Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║              НАСТУПНІ КРОКИ (вручну)                         ║" -ForegroundColor Yellow
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Yellow

Write-Host "1. Встановіть права на скрипти:" -ForegroundColor Cyan
Write-Host "   ssh $Server" -ForegroundColor White
Write-Host "   cd $RemoteDir" -ForegroundColor White
Write-Host "   chmod +x nginx/generate-ssl-certs.sh nginx/setup-letsencrypt.sh`n" -ForegroundColor White

Write-Host "2. Згенеруйте SSL сертифікати (self-signed для тесту):" -ForegroundColor Cyan
Write-Host "   cd nginx" -ForegroundColor White
Write-Host "   ./generate-ssl-certs.sh`n" -ForegroundColor White

Write-Host "3. Перезапустіть Nginx:" -ForegroundColor Cyan
Write-Host "   cd $RemoteDir" -ForegroundColor White
Write-Host "   docker compose -f docker-compose.yml -f docker-compose.prod.yml down nginx" -ForegroundColor White
Write-Host "   docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d nginx`n" -ForegroundColor White

Write-Host "4. Перевірте HTTPS:" -ForegroundColor Cyan
Write-Host "   curl -k https://192.168.31.248/" -ForegroundColor White
Write-Host "   curl -I https://192.168.31.248/api/health/`n" -ForegroundColor White

Write-Host "5. (Опціонально) Встановіть Let's Encrypt:" -ForegroundColor Cyan
Write-Host "   cd nginx" -ForegroundColor White
Write-Host "   ./setup-letsencrypt.sh yourdomain.com`n" -ForegroundColor White

Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              Deployment Script Completed                     ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "[INFO] Пароль для SSH: cgf34R" -ForegroundColor Yellow
Write-Host "[INFO] Скрипт завершено. Виконайте наступні кроки вручну.`n" -ForegroundColor Yellow
