# Простий скрипт розгортання
$SERVER = "rpuzak@192.168.31.249"

Write-Host "=== Розгортання Ohmatdyt CRM ===" -ForegroundColor Green

# Копіюємо проект на сервер (використовуємо scp рекурсивно)
Write-Host "`n[1/3] Копіювання файлів на сервер..." -ForegroundColor Yellow
Write-Host "Це може зайняти деякий час..." -ForegroundColor Gray

scp -r ohmatdyt-crm ${SERVER}:~/

Write-Host "`n[2/3] Копіювання production конфігурації..." -ForegroundColor Yellow
scp ohmatdyt-crm/.env.prod ${SERVER}:~/ohmatdyt-crm/.env

Write-Host "`n[3/3] Запуск на сервері..." -ForegroundColor Yellow

# Виконуємо команди на сервері
ssh $SERVER @"
cd ~/ohmatdyt-crm

# Перевірка та встановлення Docker
if ! command -v docker &> /dev/null; then
    echo 'Встановлення Docker...'
    sudo apt update
    sudo apt install -y docker.io docker-compose
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker \`$USER
fi

# Зупиняємо старі контейнери якщо є
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down 2>/dev/null || true

# Збираємо та запускаємо
echo 'Збірка Docker образів...'
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

echo 'Запуск контейнерів...'
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Чекаємо запуску
sleep 15

# Міграції БД
echo 'Виконання міграцій...'
docker-compose exec -T api alembic upgrade head 2>/dev/null || echo 'Міграції потребують перевірки'

# Статус
echo ''
echo '=== Статус сервісів ==='
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

echo ''
echo '✓ Розгортання завершено!'
echo '  URL: http://192.168.31.249'
echo '  API Docs: http://192.168.31.249/api/docs'
"@

Write-Host "`n=== Готово! ===" -ForegroundColor Green
