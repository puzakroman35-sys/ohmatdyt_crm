# ============================================================================
# Скрипт для зміни пароля admin на продакшн сервері
# ============================================================================

$SERVER = "rpadmin@10.24.2.187"
$REMOTE_DIR = "rpadmin/ohmatdyt-crm"

Write-Host "`n$('='*80)" -ForegroundColor Cyan
Write-Host "  🔐 Зміна пароля admin на продакшн сервері" -ForegroundColor Cyan
Write-Host "$('='*80)`n" -ForegroundColor Cyan

Write-Host "📡 Server: $SERVER" -ForegroundColor Yellow
Write-Host "📁 Directory: $REMOTE_DIR" -ForegroundColor Yellow
Write-Host "🔑 Новий пароль: Admin123!" -ForegroundColor Yellow
Write-Host ""

# Підтвердження
$confirm = Read-Host "Продовжити зміну пароля? (Y/n)"
if ($confirm -eq "n" -or $confirm -eq "N") {
    Write-Host "❌ Скасовано" -ForegroundColor Red
    exit 0
}

Write-Host "`n[1/3] Копіювання скрипта на сервер..." -ForegroundColor Yellow
scp change_admin_password.py ${SERVER}:~/${REMOTE_DIR}/

Write-Host "`n[2/3] Виконання зміни пароля через Docker..." -ForegroundColor Yellow
ssh $SERVER "cd $REMOTE_DIR && docker compose exec -T api python change_admin_password.py"

Write-Host "`n[3/3] Видалення скрипта з сервера..." -ForegroundColor Yellow
ssh $SERVER "rm ~/${REMOTE_DIR}/change_admin_password.py"

Write-Host "`n$('='*80)" -ForegroundColor Cyan
Write-Host "  ✅ Готово!" -ForegroundColor Green
Write-Host "$('='*80)`n" -ForegroundColor Cyan

Write-Host "Тепер можете увійти з:" -ForegroundColor Yellow
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: Admin123!" -ForegroundColor White
Write-Host ""
