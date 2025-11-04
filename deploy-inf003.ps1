# INF-003 Deployment to Production
# Simple deployment script without special characters

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  INF-003 Production Deployment Script" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Variables
$server = "rpuzak@192.168.31.249"
$remoteDir = "/home/rpuzak/ohmatdyt-crm"

Write-Host "[INFO] Server: $server" -ForegroundColor Yellow
Write-Host "[INFO] Remote directory: $remoteDir" -ForegroundColor Yellow
Write-Host "[INFO] Password: cgf34R`n" -ForegroundColor Yellow

# Check local files
Write-Host "[STEP 1] Checking local files..." -ForegroundColor Cyan
$files = @(
    "ohmatdyt-crm/nginx/nginx.prod.conf",
    "ohmatdyt-crm/nginx/generate-ssl-certs.sh",
    "ohmatdyt-crm/nginx/setup-letsencrypt.sh",
    "ohmatdyt-crm/nginx/README.md",
    "ohmatdyt-crm/docker-compose.prod.yml"
)

$allExist = $true
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  OK: $file" -ForegroundColor Green
    } else {
        Write-Host "  MISSING: $file" -ForegroundColor Red
        $allExist = $false
    }
}

if (-not $allExist) {
    Write-Host "`n[ERROR] Some files are missing!" -ForegroundColor Red
    exit 1
}

Write-Host "`n[STEP 2] Manual commands to execute..." -ForegroundColor Cyan
Write-Host "Copy these commands one by one (password: cgf34R):`n" -ForegroundColor Yellow

Write-Host "# 1. Copy files to server" -ForegroundColor Gray
Write-Host "scp ohmatdyt-crm/nginx/nginx.prod.conf ${server}:${remoteDir}/nginx/" -ForegroundColor White
Write-Host "scp ohmatdyt-crm/nginx/generate-ssl-certs.sh ${server}:${remoteDir}/nginx/" -ForegroundColor White
Write-Host "scp ohmatdyt-crm/nginx/setup-letsencrypt.sh ${server}:${remoteDir}/nginx/" -ForegroundColor White
Write-Host "scp ohmatdyt-crm/nginx/README.md ${server}:${remoteDir}/nginx/" -ForegroundColor White
Write-Host "scp ohmatdyt-crm/docker-compose.prod.yml ${server}:${remoteDir}/" -ForegroundColor White
Write-Host ""

Write-Host "# 2. SSH to server and generate certificates" -ForegroundColor Gray
Write-Host "ssh ${server}" -ForegroundColor White
Write-Host "cd ${remoteDir}/nginx" -ForegroundColor White
Write-Host "chmod +x generate-ssl-certs.sh setup-letsencrypt.sh" -ForegroundColor White
Write-Host "./generate-ssl-certs.sh" -ForegroundColor White
Write-Host "ls -la ssl/" -ForegroundColor White
Write-Host ""

Write-Host "# 3. Restart Nginx with HTTPS" -ForegroundColor Gray
Write-Host "cd ${remoteDir}" -ForegroundColor White
Write-Host "docker compose -f docker-compose.yml -f docker-compose.prod.yml down nginx" -ForegroundColor White
Write-Host "docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d nginx" -ForegroundColor White
Write-Host "docker compose ps" -ForegroundColor White
Write-Host "exit" -ForegroundColor White
Write-Host ""

Write-Host "# 4. Test HTTPS" -ForegroundColor Gray
Write-Host "curl -k https://192.168.31.249/" -ForegroundColor White
Write-Host "curl -I https://192.168.31.249/api/health/" -ForegroundColor White
Write-Host ""

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  Ready for deployment!" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Choose an option:" -ForegroundColor Yellow
Write-Host "  1 - Copy files automatically (you will enter password for each file)" -ForegroundColor White
Write-Host "  2 - Show manual commands only" -ForegroundColor White
$choice = Read-Host "`nYour choice (1 or 2)"

if ($choice -eq "1") {
    Write-Host "`nCopying files... Enter password cgf34R for each file`n" -ForegroundColor Cyan
    
    scp ohmatdyt-crm/nginx/nginx.prod.conf ${server}:${remoteDir}/nginx/
    Write-Host "1/5 nginx.prod.conf copied" -ForegroundColor Green
    
    scp ohmatdyt-crm/nginx/generate-ssl-certs.sh ${server}:${remoteDir}/nginx/
    Write-Host "2/5 generate-ssl-certs.sh copied" -ForegroundColor Green
    
    scp ohmatdyt-crm/nginx/setup-letsencrypt.sh ${server}:${remoteDir}/nginx/
    Write-Host "3/5 setup-letsencrypt.sh copied" -ForegroundColor Green
    
    scp ohmatdyt-crm/nginx/README.md ${server}:${remoteDir}/nginx/
    Write-Host "4/5 README.md copied" -ForegroundColor Green
    
    scp ohmatdyt-crm/docker-compose.prod.yml ${server}:${remoteDir}/
    Write-Host "5/5 docker-compose.prod.yml copied" -ForegroundColor Green
    
    Write-Host "`n[SUCCESS] Files copied to server!" -ForegroundColor Green
    Write-Host "Now execute steps 2-4 manually (see commands above)" -ForegroundColor Yellow
} else {
    Write-Host "`nExecute commands manually (see above)" -ForegroundColor Yellow
}

Write-Host "`n[DONE] Deployment script completed`n" -ForegroundColor Green
