# Ohmatdyt CRM - Smoke Tests
# Run this script to verify the infrastructure is working correctly

Write-Host "=== Ohmatdyt CRM Infrastructure Smoke Tests ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check if all containers are running
Write-Host "[Test 1] Checking container status..." -ForegroundColor Yellow
$containers = docker compose ps --format json | ConvertFrom-Json
$allHealthy = $true

foreach ($container in $containers) {
    $status = $container.State
    $name = $container.Service
    
    if ($status -match "running") {
        Write-Host "  ✓ $name is running" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $name is $status" -ForegroundColor Red
        $allHealthy = $false
    }
}

if (-not $allHealthy) {
    Write-Host "`n❌ Some containers are not running!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 2: Check environment variables
Write-Host "[Test 2] Checking environment variables..." -ForegroundColor Yellow
$dbUrl = docker compose exec -T api sh -c 'echo $DATABASE_URL' 2>$null
$redisUrl = docker compose exec -T api sh -c 'echo $REDIS_URL' 2>$null

if ($dbUrl -match "postgresql") {
    Write-Host "  ✓ DATABASE_URL is configured" -ForegroundColor Green
} else {
    Write-Host "  ✗ DATABASE_URL is not configured" -ForegroundColor Red
    $allHealthy = $false
}

if ($redisUrl -match "redis") {
    Write-Host "  ✓ REDIS_URL is configured" -ForegroundColor Green
} else {
    Write-Host "  ✗ REDIS_URL is not configured" -ForegroundColor Red
    $allHealthy = $false
}

Write-Host ""

# Test 3: Check volumes
Write-Host "[Test 3] Checking Docker volumes..." -ForegroundColor Yellow
$volumes = docker volume ls | Select-String "ohmatdyt_crm"

$requiredVolumes = @("db-data", "media", "static")
foreach ($vol in $requiredVolumes) {
    if ($volumes -match $vol) {
        Write-Host "  ✓ Volume ohmatdyt_crm_$vol exists" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Volume ohmatdyt_crm_$vol is missing" -ForegroundColor Red
        $allHealthy = $false
    }
}

Write-Host ""

# Test 4: Check volume accessibility
Write-Host "[Test 4] Checking volume accessibility..." -ForegroundColor Yellow
$mediaCheck = docker compose exec -T api sh -c 'ls -d /var/app/media' 2>$null
$staticCheck = docker compose exec -T api sh -c 'ls -d /var/app/static' 2>$null

if ($mediaCheck -match "media") {
    Write-Host "  ✓ Media volume is accessible" -ForegroundColor Green
} else {
    Write-Host "  ✗ Media volume is not accessible" -ForegroundColor Red
    $allHealthy = $false
}

if ($staticCheck -match "static") {
    Write-Host "  ✓ Static volume is accessible" -ForegroundColor Green
} else {
    Write-Host "  ✗ Static volume is not accessible" -ForegroundColor Red
    $allHealthy = $false
}

Write-Host ""

# Test 5: Check file write to volume
Write-Host "[Test 5] Testing file write to media volume..." -ForegroundColor Yellow
$testWrite = docker compose exec -T api sh -c 'echo "smoke_test" > /var/app/media/smoke_test.txt && cat /var/app/media/smoke_test.txt' 2>$null

if ($testWrite -match "smoke_test") {
    Write-Host "  ✓ Can write to media volume" -ForegroundColor Green
    docker compose exec -T api sh -c 'rm /var/app/media/smoke_test.txt' 2>$null | Out-Null
} else {
    Write-Host "  ✗ Cannot write to media volume" -ForegroundColor Red
    $allHealthy = $false
}

Write-Host ""

# Test 6: Check API endpoints
Write-Host "[Test 6] Checking API endpoints..." -ForegroundColor Yellow

try {
    $apiRoot = Invoke-WebRequest -Uri "http://localhost:8000" -UseBasicParsing -TimeoutSec 5
    if ($apiRoot.Content -match "Ohmatdyt CRM API") {
        Write-Host "  ✓ API root endpoint responding" -ForegroundColor Green
    } else {
        Write-Host "  ✗ API root endpoint invalid response" -ForegroundColor Red
        $allHealthy = $false
    }
} catch {
    Write-Host "  ✗ API root endpoint not accessible" -ForegroundColor Red
    $allHealthy = $false
}

try {
    $apiHealth = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    $healthData = $apiHealth.Content | ConvertFrom-Json
    
    if ($healthData.status -eq "healthy") {
        Write-Host "  ✓ API health endpoint reports healthy" -ForegroundColor Green
    } else {
        Write-Host "  ✗ API health endpoint reports unhealthy" -ForegroundColor Red
        $allHealthy = $false
    }
} catch {
    Write-Host "  ✗ API health endpoint not accessible" -ForegroundColor Red
    $allHealthy = $false
}

Write-Host ""

# Test 7: Check Frontend
Write-Host "[Test 7] Checking Frontend..." -ForegroundColor Yellow

try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    if ($frontend.Content -match "Ohmatdyt") {
        Write-Host "  ✓ Frontend is responding" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Frontend invalid response" -ForegroundColor Red
        $allHealthy = $false
    }
} catch {
    Write-Host "  ✗ Frontend not accessible" -ForegroundColor Red
    $allHealthy = $false
}

Write-Host ""

# Test 8: Check Nginx
Write-Host "[Test 8] Checking Nginx proxy..." -ForegroundColor Yellow

try {
    $nginx = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing -TimeoutSec 5
    if ($nginx.Content -match "healthy") {
        Write-Host "  ✓ Nginx proxy is responding" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Nginx proxy invalid response" -ForegroundColor Red
        $allHealthy = $false
    }
} catch {
    Write-Host "  ✗ Nginx proxy not accessible" -ForegroundColor Red
    $allHealthy = $false
}

Write-Host ""

# Test 9: Check Celery Worker
Write-Host "[Test 9] Checking Celery Worker..." -ForegroundColor Yellow
$workerLogs = docker compose logs worker --tail=5 2>$null

if ($workerLogs -match "ready" -or $workerLogs -match "Connected to redis") {
    Write-Host "  ✓ Celery Worker is running" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Celery Worker status unclear (check logs)" -ForegroundColor Yellow
}

Write-Host ""

# Test 10: Check Celery Beat
Write-Host "[Test 10] Checking Celery Beat..." -ForegroundColor Yellow
$beatLogs = docker compose logs beat --tail=5 2>$null

if ($beatLogs -match "Starting" -or $beatLogs -match "beat:") {
    Write-Host "  ✓ Celery Beat is running" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Celery Beat status unclear (check logs)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan

if ($allHealthy) {
    Write-Host "✅ All smoke tests PASSED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Services are available at:" -ForegroundColor Cyan
    Write-Host "  - API:      http://localhost:8000" -ForegroundColor White
    Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  - Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "  - Nginx:    http://localhost:8080" -ForegroundColor White
    exit 0
} else {
    Write-Host "❌ Some smoke tests FAILED!" -ForegroundColor Red
    Write-Host "Please check the logs: docker compose logs" -ForegroundColor Yellow
    exit 1
}
