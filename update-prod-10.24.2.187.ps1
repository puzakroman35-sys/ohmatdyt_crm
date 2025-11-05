# ============================================================================
# Quick Update Script for Production Server
# ============================================================================
# Server: rpadmin@10.24.2.187
# Use this script for quick updates after initial deployment
# ============================================================================

$SERVER = "rpadmin@10.24.2.187"
$REMOTE_DIR = "rpadmin"

Write-Host "`n$('='*80)" -ForegroundColor Cyan
Write-Host "  🔄 Quick Production Update - 10.24.2.187" -ForegroundColor Cyan
Write-Host "$('='*80)`n" -ForegroundColor Cyan

Write-Host "📡 Server: $SERVER" -ForegroundColor Yellow
Write-Host "📁 Directory: $REMOTE_DIR" -ForegroundColor Yellow
Write-Host ""

# Check current status
Write-Host "[КРОК 1/6] Поточний статус..." -ForegroundColor Yellow
Write-Host "$('-'*80)" -ForegroundColor DarkGray
ssh $SERVER "cd $REMOTE_DIR/ohmatdyt-crm && git status --short && git log -1 --oneline"
Write-Host ""

# Fetch changes
Write-Host "[КРОК 2/6] Завантаження змін..." -ForegroundColor Yellow
Write-Host "$('-'*80)" -ForegroundColor DarkGray
ssh $SERVER "cd $REMOTE_DIR/ohmatdyt-crm && git fetch origin"
Write-Host ""

# Show what will be updated
Write-Host "[КРОК 3/6] Нові коміти:" -ForegroundColor Yellow
Write-Host "$('-'*80)" -ForegroundColor DarkGray
ssh $SERVER "cd $REMOTE_DIR/ohmatdyt-crm && git log HEAD..origin/main --oneline"
Write-Host ""

# Pull changes
Write-Host "[КРОК 4/6] Застосування змін..." -ForegroundColor Yellow
Write-Host "$('-'*80)" -ForegroundColor DarkGray
$confirm = Read-Host "Продовжити з git pull? (Y/n)"
if ($confirm -ne "n" -and $confirm -ne "N") {
    ssh $SERVER "cd $REMOTE_DIR/ohmatdyt-crm && git pull origin main"
    Write-Host "✅ Зміни застосовано" -ForegroundColor Green
} else {
    Write-Host "⏭️  Пропущено" -ForegroundColor Yellow
    exit 0
}
Write-Host ""

# Rebuild and restart
Write-Host "[КРОК 5/6] Перезбірка та перезапуск..." -ForegroundColor Yellow
Write-Host "$('-'*80)" -ForegroundColor DarkGray
$rebuild = Read-Host "Перезібрати образи? (y/N)"

$restartScript = @"
cd $REMOTE_DIR/ohmatdyt-crm

if [ "$rebuild" = "y" ] || [ "$rebuild" = "Y" ]; then
    echo "Rebuilding images..."
    docker compose -f docker-compose.yml -f docker-compose.prod.yml build
fi

echo "Restarting services..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

echo "Waiting 15 seconds..."
sleep 15

echo "Running migrations..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T api alembic upgrade head

echo ""
echo "Services status:"
docker compose ps
"@

ssh $SERVER $restartScript
Write-Host ""

# Show logs
Write-Host "[КРОК 6/6] Останні логи:" -ForegroundColor Yellow
Write-Host "$('-'*80)" -ForegroundColor DarkGray
ssh $SERVER "cd $REMOTE_DIR/ohmatdyt-crm && docker compose logs --tail=30"
Write-Host ""

Write-Host "$('='*80)" -ForegroundColor Cyan
Write-Host "  ✅ Оновлення завершено!" -ForegroundColor Green
Write-Host "$('='*80)`n" -ForegroundColor Cyan

Write-Host "🌐 URLs:" -ForegroundColor Yellow
Write-Host "   http://10.24.2.187" -ForegroundColor White
Write-Host "   http://10.24.2.187/api/docs" -ForegroundColor White
Write-Host ""
