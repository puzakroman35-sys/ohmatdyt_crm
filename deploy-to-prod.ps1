# INF-003: Production Deployment Script
# Deploy to production server: rpuzak@192.168.31.248
# Password: cgf34R

$SERVER = "rpuzak@192.168.31.248"
$REMOTE_DIR = "ohmatdyt"
$PASSWORD = "cgf34R"

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "  🚀 Production Deployment - INF-003" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📡 Target Server: $SERVER" -ForegroundColor Yellow
Write-Host "📁 Remote Directory: $REMOTE_DIR" -ForegroundColor Yellow
Write-Host "🔑 Password: ******" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  ВАЖЛИВО: Введіть пароль вручну при запиті SSH" -ForegroundColor Red
Write-Host "   Password: cgf34R" -ForegroundColor Gray
Write-Host ""

# Step 1: Check git status on remote
Write-Host "[КРОК 1] Перевірка поточного стану на сервері..." -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

$statusCmd = "cd $REMOTE_DIR && git status --short"
Write-Host "Executing: ssh $SERVER `"$statusCmd`"" -ForegroundColor Gray
ssh $SERVER $statusCmd

Write-Host ""

# Step 2: Fetch latest changes
Write-Host "[КРОК 2] Завантаження останніх змін з git..." -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

$fetchCmd = "cd $REMOTE_DIR && git fetch origin"
Write-Host "Executing: ssh $SERVER `"$fetchCmd`"" -ForegroundColor Gray
ssh $SERVER $fetchCmd

Write-Host ""

# Step 3: Show diff
Write-Host "[КРОК 3] Перегляд змін..." -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

$diffCmd = "cd $REMOTE_DIR && git log HEAD..origin/main --oneline"
Write-Host "Executing: ssh $SERVER `"$diffCmd`"" -ForegroundColor Gray
ssh $SERVER $diffCmd

Write-Host ""

# Step 4: Pull changes
Write-Host "[КРОК 4] Застосування змін (git pull)..." -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

$pullCmd = "cd $REMOTE_DIR && git pull origin main"
Write-Host "Executing: ssh $SERVER `"$pullCmd`"" -ForegroundColor Gray
ssh $SERVER $pullCmd

Write-Host ""

# Step 5: Restart services if needed
Write-Host "[КРОК 5] Перезапуск сервісів (опціонально)..." -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

$confirm = Read-Host "Перезапустити Docker сервіси? (y/N)"
if ($confirm -eq "y" -or $confirm -eq "Y") {
    $restartCmd = "cd $REMOTE_DIR && docker compose -f docker-compose.yml -f docker-compose.prod.yml restart nginx"
    Write-Host "Executing: ssh $SERVER `"$restartCmd`"" -ForegroundColor Gray
    ssh $SERVER $restartCmd
    
    Write-Host ""
    Write-Host "✅ Nginx перезапущено" -ForegroundColor Green
} else {
    Write-Host "⏭️  Пропущено" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  ✅ Deployment завершено!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Show final status
Write-Host "Фінальний статус:" -ForegroundColor Yellow
$finalStatusCmd = "cd $REMOTE_DIR && git log -1 --oneline && echo '' && git status --short"
ssh $SERVER $finalStatusCmd

Write-Host ""
