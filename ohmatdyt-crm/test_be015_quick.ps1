#!/usr/bin/env pwsh
# BE-015: Quick healthcheck test

Write-Host "`n================================================================================" -ForegroundColor Blue
Write-Host "  BE-015: Healthcheck та базове логування - Quick Test" -ForegroundColor Blue
Write-Host "================================================================================" -ForegroundColor Blue

$API_URL = "http://localhost:8000"

Write-Host "`n[TEST 1] Перевірка /healthz endpoint..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$API_URL/healthz" -Method Get -Headers @{"X-Request-ID" = "test-123"}
    
    if ($response.status -eq "healthy") {
        Write-Host "✅ Status: $($response.status)" -ForegroundColor Green
        Write-Host "✅ Database: $($response.services.database)" -ForegroundColor Green
        Write-Host "✅ Redis: $($response.services.redis)" -ForegroundColor Green
        Write-Host "✅ Version: $($response.version)" -ForegroundColor Green
        Write-Host "✅ Timestamp: $($response.timestamp)" -ForegroundColor Green
    } else {
        Write-Host "❌ Unhealthy status!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Failed to connect to API: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n[TEST 2] Перевірка X-Request-ID middleware..." -ForegroundColor Yellow

try {
    $headers = Invoke-WebRequest -Uri "$API_URL/healthz" -Method Get -Headers @{"X-Request-ID" = "custom-test-id"} -UseBasicParsing
    
    if ($headers.Headers["x-request-id"]) {
        $requestId = $headers.Headers["x-request-id"]
        Write-Host "✅ X-Request-ID присутній: $requestId" -ForegroundColor Green
        
        if ($requestId -eq "custom-test-id") {
            Write-Host "✅ Custom Request-ID збережено" -ForegroundColor Green
        }
    } else {
        Write-Host "❌ X-Request-ID відсутній в headers!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n[TEST 3] Перевірка legacy /health endpoint..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$API_URL/health" -Method Get
    
    if ($response.status -eq "healthy") {
        Write-Host "✅ Legacy endpoint працює" -ForegroundColor Green
    } else {
        Write-Host "❌ Legacy endpoint не працює!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n[TEST 4] Перевірка root endpoint..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$API_URL/" -Method Get
    
    if ($response.message -eq "Ohmatdyt CRM API") {
        Write-Host "✅ Root endpoint працює" -ForegroundColor Green
        Write-Host "✅ Version: $($response.version)" -ForegroundColor Green
    } else {
        Write-Host "❌ Unexpected response!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n================================================================================
" -ForegroundColor Blue
Write-Host "ПІДСУМОК: Всі тести пройдено успішно! ✅" -ForegroundColor Green -BackgroundColor Black
Write-Host "BE-015 ГОТОВО ДО PRODUCTION ✅" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Blue

Write-Host "`nСтруктуровані логи можна побачити через:" -ForegroundColor Yellow
Write-Host "  docker logs ohmatdyt_crm-api-1 --tail=50`n" -ForegroundColor White

exit 0
