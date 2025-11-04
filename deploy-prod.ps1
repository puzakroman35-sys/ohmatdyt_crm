# Скрипт для розгортання на продакшн сервер
$SERVER = "rpuzak@192.168.31.249"
$PROJECT_DIR = "~/ohmatdyt_crm"

Write-Host "=== Розгортання Ohmatdyt CRM на продакшн ===" -ForegroundColor Green

# 1. Створюємо tar архів проекту (виключаючи непотрібні файли)
Write-Host "`n[1/8] Створення архіву проекту..." -ForegroundColor Yellow
$excludeFiles = @(
    "node_modules",
    ".git",
    "__pycache__",
    "*.pyc",
    ".env",
    ".env.example",
    "db-data",
    "media",
    "static",
    ".vscode"
)

cd ohmatdyt-crm
tar -czf ../ohmatdyt-crm.tar.gz --exclude-from=<(echo "node_modules`n.git`n__pycache__`n*.pyc`n.env`n.env.example`ndb-data`nmedia`nstatic") .
cd ..

# 2. Копіюємо архів на сервер
Write-Host "`n[2/8] Копіювання проекту на сервер..." -ForegroundColor Yellow
scp ohmatdyt-crm.tar.gz ${SERVER}:~/

# 3. Копіюємо production .env
Write-Host "`n[3/8] Копіювання production конфігурації..." -ForegroundColor Yellow
scp ohmatdyt-crm/.env.prod ${SERVER}:~/env.prod

# 4. Підключаємось до сервера та розгортаємо
Write-Host "`n[4/8] Підключення до сервера..." -ForegroundColor Yellow

$commands = @"
echo '=== Встановлення на сервері ==='
cd ~

# Створюємо директорію проекту
mkdir -p ohmatdyt_crm
cd ohmatdyt_crm

# Розпаковуємо архів
echo '[5/8] Розпакування проекту...'
tar -xzf ~/ohmatdyt-crm.tar.gz
mv ~/env.prod .env

# Створюємо необхідні директорії
echo '[6/8] Створення директорій...'
mkdir -p media static db redis

# Перевірка Docker
echo '[7/8] Перевірка Docker...'
if ! command -v docker &> /dev/null; then
    echo 'Docker не встановлено. Встановлюємо...'
    sudo apt update
    sudo apt install -y docker.io docker-compose
    sudo usermod -aG docker \$USER
fi

# Запуск контейнерів
echo '[8/8] Запуск Docker контейнерів...'
docker-compose down 2>/dev/null || true
docker-compose build
docker-compose up -d

# Очікуємо запуску
sleep 10

# Виконуємо міграції
echo 'Виконання міграцій бази даних...'
docker-compose exec -T api alembic upgrade head || echo 'Міграції можуть вимагати додаткової настройки'

# Перевірка статусу
echo ''
echo '=== Статус контейнерів ==='
docker-compose ps

echo ''
echo '=== Розгортання завершено! ==='
echo 'Доступ до додатку: http://192.168.31.249'
echo 'API документація: http://192.168.31.249/api/docs'
echo ''
echo 'Корисні команди:'
echo '  docker-compose logs -f      # Перегляд логів'
echo '  docker-compose restart      # Перезапуск'
echo '  docker-compose down         # Зупинка'
"@

ssh $SERVER $commands

# Видаляємо локальний архів
Remove-Item ohmatdyt-crm.tar.gz -ErrorAction SilentlyContinue

Write-Host "`n=== Готово! ===" -ForegroundColor Green
Write-Host "Проект розгорнуто на http://192.168.31.249" -ForegroundColor Cyan
