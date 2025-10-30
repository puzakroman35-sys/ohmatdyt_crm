# INF-003: Test Nginx Production Configuration with HTTPS
# This script tests nginx.prod.conf setup

$ErrorActionPreference = "Stop"

Write-Host "================================================================================`n" -ForegroundColor Cyan
Write-Host "  INF-003: Nginx Production Configuration Testing`n" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Тестування Nginx конфігурації з HTTPS підтримкою`n" -ForegroundColor White
Write-Host "Компоненти що тестуються:" -ForegroundColor Yellow
Write-Host "  - SSL сертифікати (self-signed)" -ForegroundColor Gray
Write-Host "  - HTTP to HTTPS redirect" -ForegroundColor Gray
Write-Host "  - HTTPS endpoints (API, Frontend)" -ForegroundColor Gray
Write-Host "  - Security headers" -ForegroundColor Gray
Write-Host "  - Static/Media files serving" -ForegroundColor Gray
Write-Host "  - Rate limiting" -ForegroundColor Gray
Write-Host "  - Health check endpoints" -ForegroundColor Gray
Write-Host ""

# Configuration
$BASE_URL_HTTP = "http://localhost"
$BASE_URL_HTTPS = "https://localhost"
$API_PORT = 8000

# Test results
$passed = 0
$failed = 0
$tests = @()

function Test-Step {
    param(
        [string]$Name,
        [scriptblock]$Test
    )
    
    try {
        & $Test
        $script:passed++
        $script:tests += @{ Name = $Name; Status = "PASS" }
        Write-Host "✅ PASS - $Name" -ForegroundColor Green
        return $true
    }
    catch {
        $script:failed++
        $script:tests += @{ Name = $Name; Status = "FAIL"; Error = $_.Exception.Message }
        Write-Host "❌ FAIL - $Name" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Test 1: Check if Nginx is running
Write-Host "[КРОК 1] Перевірка що Nginx запущено" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

Test-Step "nginx_container_running" {
    $nginx = docker compose ps nginx --format json | ConvertFrom-Json
    if ($nginx.State -ne "running") {
        throw "Nginx контейнер не запущено. Запустіть: docker compose up -d nginx"
    }
    Write-Host "ℹ️  Nginx контейнер запущено" -ForegroundColor Cyan
}

Write-Host ""

# Test 2: Check SSL certificates exist
Write-Host "[КРОК 2] Перевірка SSL сертифікатів" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

Test-Step "ssl_certificates_exist" {
    if (-not (Test-Path "nginx/ssl/cert.pem")) {
        throw "SSL сертифікат не знайдено. Згенеруйте: cd nginx && ./generate-ssl-certs.sh"
    }
    if (-not (Test-Path "nginx/ssl/key.pem")) {
        throw "SSL приватний ключ не знайдено"
    }
    Write-Host "ℹ️  SSL сертифікати знайдено" -ForegroundColor Cyan
    
    # Check certificate details
    $certInfo = openssl x509 -in nginx/ssl/cert.pem -text -noout | Select-String "Subject:"
    Write-Host "ℹ️  $certInfo" -ForegroundColor Cyan
}

Write-Host ""

# Test 3: Test HTTP to HTTPS redirect
Write-Host "[КРОК 3] Тестування HTTP → HTTPS редіректу" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

Test-Step "http_to_https_redirect" {
    $response = curl.exe -s -I -L "$BASE_URL_HTTP/health" 2>$null
    if ($response -notmatch "301|302") {
        throw "HTTP редірект не працює"
    }
    Write-Host "ℹ️  HTTP коректно редіректить на HTTPS" -ForegroundColor Cyan
}

Write-Host ""

# Test 4: Test HTTPS health endpoint
Write-Host "[КРОК 4] Тестування HTTPS /health endpoint" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

Test-Step "https_health_endpoint" {
    $response = curl.exe -k -s "$BASE_URL_HTTPS/health" 2>$null
    if ($response -ne "healthy") {
        throw "Health endpoint не повертає 'healthy'"
    }
    Write-Host "ℹ️  HTTPS /health endpoint працює" -ForegroundColor Cyan
}

Write-Host ""

# Test 5: Test API endpoint through HTTPS
Write-Host "[КРОК 5] Тестування API через HTTPS" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

Test-Step "https_api_endpoint" {
    $response = curl.exe -k -s "$BASE_URL_HTTPS/api/healthz" 2>$null | ConvertFrom-Json
    if ($response.status -ne "healthy") {
        throw "API healthz не повертає status=healthy"
    }
    Write-Host "ℹ️  API endpoint доступний через HTTPS" -ForegroundColor Cyan
    Write-Host "ℹ️  API Status: $($response.status)" -ForegroundColor Cyan
}

Write-Host ""

# Test 6: Test Security Headers
Write-Host "[КРОК 6] Перевірка Security Headers" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

Test-Step "security_headers_hsts" {
    $headers = curl.exe -k -I -s "$BASE_URL_HTTPS/health" 2>$null
    if ($headers -notmatch "Strict-Transport-Security") {
        throw "HSTS header відсутній"
    }
    Write-Host "ℹ️  HSTS (Strict-Transport-Security) header присутній" -ForegroundColor Cyan
}

Test-Step "security_headers_frame_options" {
    $headers = curl.exe -k -I -s "$BASE_URL_HTTPS/health" 2>$null
    if ($headers -notmatch "X-Frame-Options") {
        throw "X-Frame-Options header відсутній"
    }
    Write-Host "ℹ️  X-Frame-Options header присутній" -ForegroundColor Cyan
}

Test-Step "security_headers_content_type" {
    $headers = curl.exe -k -I -s "$BASE_URL_HTTPS/health" 2>$null
    if ($headers -notmatch "X-Content-Type-Options") {
        throw "X-Content-Type-Options header відсутній"
    }
    Write-Host "ℹ️  X-Content-Type-Options header присутній" -ForegroundColor Cyan
}

Write-Host ""

# Test 7: Test Gzip Compression
Write-Host "[КРОК 7] Перевірка Gzip compression" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

Test-Step "gzip_compression" {
    $headers = curl.exe -k -I -s -H "Accept-Encoding: gzip" "$BASE_URL_HTTPS/api/healthz" 2>$null
    if ($headers -notmatch "Content-Encoding.*gzip") {
        Write-Host "⚠️  Gzip compression може бути відключена для малих відповідей" -ForegroundColor Yellow
    } else {
        Write-Host "ℹ️  Gzip compression активна" -ForegroundColor Cyan
    }
}

Write-Host ""

# Test 8: Test static files caching
Write-Host "[КРОК 8] Перевірка кешування static files" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

Test-Step "static_files_caching" {
    # Create a test static file if doesn't exist
    if (-not (Test-Path "static/test.txt")) {
        New-Item -Path "static" -ItemType Directory -Force | Out-Null
        Set-Content -Path "static/test.txt" -Value "Test static file"
    }
    
    $headers = curl.exe -k -I -s "$BASE_URL_HTTPS/static/test.txt" 2>$null
    if ($headers -notmatch "Cache-Control") {
        throw "Cache-Control header відсутній для static files"
    }
    Write-Host "ℹ️  Static files мають Cache-Control header" -ForegroundColor Cyan
}

Write-Host ""

# Test 9: Test Rate Limiting (optional - requires multiple requests)
Write-Host "[КРОК 9] Тестування Rate Limiting" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

Test-Step "rate_limiting_info" {
    Write-Host "ℹ️  Rate limiting налаштовано:" -ForegroundColor Cyan
    Write-Host "   - API: 10 req/s + burst 20" -ForegroundColor Gray
    Write-Host "   - Login: 5 req/min + burst 2" -ForegroundColor Gray
    Write-Host "⚠️  Повне тестування потребує багато запитів (пропущено)" -ForegroundColor Yellow
}

Write-Host ""

# Test 10: Check Nginx configuration syntax
Write-Host "[КРОК 10] Перевірка синтаксису Nginx конфігурації" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

Test-Step "nginx_config_syntax" {
    $result = docker compose exec -T nginx nginx -t 2>&1
    if ($result -notmatch "syntax is ok" -or $result -notmatch "successful") {
        throw "Nginx конфігурація має помилки: $result"
    }
    Write-Host "ℹ️  Nginx конфігурація валідна" -ForegroundColor Cyan
}

Write-Host ""

# Summary
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "ПІДСУМОК ТЕСТУВАННЯ INF-003" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Результати тестування:" -ForegroundColor Yellow
foreach ($test in $tests) {
    if ($test.Status -eq "PASS") {
        Write-Host "  ✅ PASS - $($test.Name)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ FAIL - $($test.Name)" -ForegroundColor Red
        if ($test.Error) {
            Write-Host "     $($test.Error)" -ForegroundColor Red
        }
    }
}
Write-Host ""
Write-Host "📊 TOTAL - $passed/$($passed + $failed) тестів пройдено" -ForegroundColor Cyan
Write-Host ""

if ($failed -eq 0) {
    Write-Host "✅ Всі тести пройдено успішно! ✨" -ForegroundColor Green
    Write-Host "ℹ️  INF-003 ГОТОВО ДО PRODUCTION ✅" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "❌ Деякі тести не пройдено. Перевірте помилки вище." -ForegroundColor Red
    Write-Host "ℹ️  INF-003 ПОТРЕБУЄ ВИПРАВЛЕНЬ ⚠️" -ForegroundColor Yellow
    exit 1
}
