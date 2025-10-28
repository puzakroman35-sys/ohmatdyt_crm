# Ohmatdyt CRM - Quick Smoke Test
# Run: powershell -ExecutionPolicy Bypass -File .\scripts\smoke-test-simple.ps1

Write-Host "=== Ohmatdyt CRM Smoke Tests ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Container status
Write-Host "[1] Container Status" -ForegroundColor Yellow
docker compose ps
Write-Host ""

# Test 2: Environment variables
Write-Host "[2] Environment Variables" -ForegroundColor Yellow
Write-Host "DATABASE_URL:" -NoNewline
docker compose exec -T api sh -c 'echo $DATABASE_URL'
Write-Host "REDIS_URL:" -NoNewline
docker compose exec -T api sh -c 'echo $REDIS_URL'
Write-Host ""

# Test 3: Volumes
Write-Host "[3] Docker Volumes" -ForegroundColor Yellow
docker volume ls | Select-String "ohmatdyt_crm"
Write-Host ""

# Test 4: Volume accessibility
Write-Host "[4] Volume Paths" -ForegroundColor Yellow
docker compose exec -T api sh -c 'ls -la /var/app/media /var/app/static'
Write-Host ""

# Test 5: API Test
Write-Host "[5] API Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    Write-Host $response.Content -ForegroundColor Green
} catch {
    Write-Host "ERROR: API not accessible" -ForegroundColor Red
}
Write-Host ""

# Test 6: Frontend Test
Write-Host "[6] Frontend Check" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
    if ($response.Content -match "Ohmatdyt") {
        Write-Host "Frontend is running" -ForegroundColor Green
    }
} catch {
    Write-Host "ERROR: Frontend not accessible" -ForegroundColor Red
}
Write-Host ""

# Test 7: Nginx Test
Write-Host "[7] Nginx Proxy Check" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing
    Write-Host "Nginx is responding" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Nginx not accessible" -ForegroundColor Red
}
Write-Host ""

Write-Host "=== Services ===" -ForegroundColor Cyan
Write-Host "API:      http://localhost:8000" -ForegroundColor White
Write-Host "Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "Nginx:    http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "Run 'docker compose logs -f [service]' to view logs" -ForegroundColor Gray
