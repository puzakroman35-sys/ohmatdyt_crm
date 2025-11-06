# PowerShell скрипт для налаштування SSL сертифіката на сервері з IP адресою
# Використання: .\setup-ssl-for-ip.ps1

$SERVER_IP = "10.24.2.187"
$SSH_USER = "root"

Write-Host "🔐 Налаштування SSL сертифіката для IP: $SERVER_IP" -ForegroundColor Green

# Копіюємо скрипт на сервер
Write-Host "`n📤 Копіювання скрипта на сервер..." -ForegroundColor Cyan
scp setup-ssl-for-ip.sh ${SSH_USER}@${SERVER_IP}:/tmp/

# Виконуємо скрипт на сервері
Write-Host "`n🚀 Виконання скрипта на сервері..." -ForegroundColor Cyan
ssh ${SSH_USER}@${SERVER_IP} "chmod +x /tmp/setup-ssl-for-ip.sh && /tmp/setup-ssl-for-ip.sh"

Write-Host "`n✅ Налаштування завершено!" -ForegroundColor Green
Write-Host "`n📌 Наступні кроки:" -ForegroundColor Yellow
Write-Host "   1. Відкрийте браузер та перейдіть: https://$SERVER_IP" -ForegroundColor White
Write-Host "   2. Натисніть 'Advanced' або 'Додатково'" -ForegroundColor White
Write-Host "   3. Натисніть 'Proceed' або 'Продовжити'" -ForegroundColor White
Write-Host "`n⚠️  Self-signed сертифікати завжди показують попередження" -ForegroundColor Yellow
Write-Host "   Для повного усунення попередження потрібен домен та Let's Encrypt" -ForegroundColor Yellow
