# BE-006 Test Runner Script
# Quick test for case creation with file attachments

Write-Host "================================" -ForegroundColor Cyan
Write-Host "BE-006: Case Creation with Files" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if API is running
Write-Host "Checking API availability..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ API is running" -ForegroundColor Green
} catch {
    Write-Host "✗ API is not accessible at http://localhost:8000" -ForegroundColor Red
    Write-Host "Please start the API server first:" -ForegroundColor Yellow
    Write-Host "  cd ohmatdyt-crm" -ForegroundColor White
    Write-Host "  docker-compose up" -ForegroundColor White
    exit 1
}

Write-Host ""

# Run Python test
Write-Host "Running BE-006 test suite..." -ForegroundColor Yellow
Write-Host ""

$apiPath = "ohmatdyt-crm\api"
if (Test-Path $apiPath) {
    Set-Location $apiPath
    python test_be006.py
    $exitCode = $LASTEXITCODE
    Set-Location ..\..
    
    if ($exitCode -eq 0) {
        Write-Host ""
        Write-Host "================================" -ForegroundColor Green
        Write-Host "✓ All tests completed" -ForegroundColor Green
        Write-Host "================================" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "================================" -ForegroundColor Red
        Write-Host "✗ Tests failed" -ForegroundColor Red
        Write-Host "================================" -ForegroundColor Red
        exit $exitCode
    }
} else {
    Write-Host "✗ Cannot find API directory at: $apiPath" -ForegroundColor Red
    exit 1
}
