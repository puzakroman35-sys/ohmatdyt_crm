# Check production frontend status after build completes

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "  Production Status Check" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1] Checking container status..." -ForegroundColor Yellow
ssh rpuzak@192.168.31.248 "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

Write-Host ""
Write-Host "[2] Frontend logs (last 50 lines)..." -ForegroundColor Yellow
ssh rpuzak@192.168.31.248 "docker logs ohmatdyt_crm-frontend-1 --tail 50"

Write-Host ""
Write-Host "[3] Testing HTTPS..." -ForegroundColor Yellow
ssh rpuzak@192.168.31.248 "curl -k -I https://192.168.31.248/ 2>&1 | head -20"

Write-Host ""
Write-Host "===================================" -ForegroundColor Green
Write-Host "  Open in browser:" -ForegroundColor Green
Write-Host "  https://192.168.31.248/" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Green
