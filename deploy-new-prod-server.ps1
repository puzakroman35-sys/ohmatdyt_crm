# ============================================================================
# Deployment Script for New Production Server
# ============================================================================
# Server: rpadmin@10.24.2.187
# Description: Complete deployment setup for Ohmatdyt CRM on fresh server
# ============================================================================

param(
    [string]$ServerIP = "10.24.2.187",
    [string]$ServerUser = "rpadmin",
    [switch]$SkipServerSetup,
    [switch]$SkipDockerInstall
)

$SERVER = "${ServerUser}@${ServerIP}"
$REMOTE_DIR = "ohmatdyt-crm"
$PROJECT_NAME = "ohmatdyt_crm"

# Colors
$ColorInfo = "Cyan"
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorStep = "Magenta"

function Write-Header {
    param([string]$Message)
    Write-Host "`n$('='*80)" -ForegroundColor $ColorInfo
    Write-Host "  $Message" -ForegroundColor $ColorInfo
    Write-Host "$('='*80)`n" -ForegroundColor $ColorInfo
}

function Write-Step {
    param([string]$StepNumber, [string]$Message)
    Write-Host "`n[КРОК $StepNumber] $Message" -ForegroundColor $ColorStep
    Write-Host "$('-'*80)" -ForegroundColor DarkGray
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $ColorSuccess
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $ColorWarning
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $ColorError
}

function Invoke-SSHCommand {
    param(
        [string]$Command,
        [string]$Description = "",
        [switch]$IgnoreErrors
    )
    
    if ($Description) {
        Write-Host "📡 $Description" -ForegroundColor Gray
    }
    
    Write-Host "   Executing: $Command" -ForegroundColor DarkGray
    
    if ($IgnoreErrors) {
        ssh $SERVER "$Command" 2>&1 | Out-Null
    } else {
        ssh $SERVER "$Command"
        if ($LASTEXITCODE -ne 0 -and -not $IgnoreErrors) {
            Write-ErrorMsg "Command failed with exit code $LASTEXITCODE"
            return $false
        }
    }
    return $true
}

# ============================================================================
# MAIN DEPLOYMENT PROCESS
# ============================================================================

Write-Header "🚀 Ohmatdyt CRM - Production Server Deployment"

Write-Host "📋 Deployment Configuration:" -ForegroundColor $ColorInfo
Write-Host "   Server:           $SERVER" -ForegroundColor White
Write-Host "   Remote Directory: $REMOTE_DIR" -ForegroundColor White
Write-Host "   Project Name:     $PROJECT_NAME" -ForegroundColor White
Write-Host ""

# ============================================================================
# STEP 0: Connection Test
# ============================================================================

Write-Step "0" "Перевірка підключення до сервера"

Write-Host "Тестуємо SSH підключення..." -ForegroundColor Gray
$testResult = ssh -o ConnectTimeout=5 $SERVER "echo 'Connection OK'" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Не вдалося підключитися до сервера $SERVER"
    Write-Host "Перевірте:" -ForegroundColor Yellow
    Write-Host "  1. IP адресу та логін" -ForegroundColor Yellow
    Write-Host "  2. SSH доступ" -ForegroundColor Yellow
    Write-Host "  3. Налаштування мережі" -ForegroundColor Yellow
    exit 1
}

Write-Success "З'єднання успішне!"

# ============================================================================
# STEP 1: Server Setup (if needed)
# ============================================================================

if (-not $SkipServerSetup) {
    Write-Step "1" "Підготовка сервера"
    
    Write-Host "Оновлюємо систему..." -ForegroundColor Gray
    Invoke-SSHCommand -Command "sudo apt-get update" -Description "Оновлення списку пакетів"
    
    Write-Host "`nВстановлюємо необхідні пакети..." -ForegroundColor Gray
    Invoke-SSHCommand -Command "sudo apt-get install -y git curl wget nano htop net-tools" -Description "Встановлення базових утиліт"
    
    Write-Success "Сервер підготовлено"
} else {
    Write-Warning "Підготовка сервера пропущена (--SkipServerSetup)"
}

# ============================================================================
# STEP 2: Docker Installation
# ============================================================================

if (-not $SkipDockerInstall) {
    Write-Step "2" "Встановлення Docker"
    
    Write-Host "Перевіряємо наявність Docker..." -ForegroundColor Gray
    $dockerCheck = ssh $SERVER "command -v docker" 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker не встановлено. Встановлюємо..." -ForegroundColor Yellow
        
        # Install Docker
        $dockerInstallScript = @"
# Remove old versions
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo "deb [arch=`$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu `$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $ServerUser

# Start Docker
sudo systemctl enable docker
sudo systemctl start docker

echo "Docker installed successfully"
"@
        
        ssh $SERVER $dockerInstallScript
        
        Write-Success "Docker встановлено"
        Write-Warning "Увага: Можливо знадобиться перелогінитися для застосування групи docker"
    } else {
        Write-Success "Docker вже встановлено"
    }
    
    # Check Docker Compose
    Write-Host "`nПеревіряємо Docker Compose..." -ForegroundColor Gray
    ssh $SERVER "docker compose version"
    
} else {
    Write-Warning "Installation of Docker skipped (--SkipDockerInstall)"
}

# ============================================================================
# STEP 3: Clone Repository
# ============================================================================

Write-Step "3" "Клонування репозиторію"

Write-Host "Перевіряємо наявність директорії проекту..." -ForegroundColor Gray
$dirExists = ssh $SERVER "test -d $REMOTE_DIR && echo 'exists' || echo 'not_exists'" 2>&1

if ($dirExists -match "exists") {
    Write-Warning "Директорія $REMOTE_DIR вже існує"
    $overwrite = Read-Host "Видалити та клонувати заново? (y/N)"
    
    if ($overwrite -eq "y" -or $overwrite -eq "Y") {
        Write-Host "Видаляємо стару директорію..." -ForegroundColor Yellow
        Invoke-SSHCommand -Command "rm -rf $REMOTE_DIR" -Description "Видалення старої директорії"
        $shouldClone = $true
    } else {
        Write-Host "Використовуємо існуючу директорію" -ForegroundColor Yellow
        $shouldClone = $false
    }
} else {
    $shouldClone = $true
}

if ($shouldClone) {
    Write-Host "Введіть URL репозиторію (або Enter для https://github.com/puzakroman35-sys/ohmatdyt_crm.git):" -ForegroundColor Yellow
    $repoUrl = Read-Host
    if ([string]::IsNullOrWhiteSpace($repoUrl)) {
        $repoUrl = "https://github.com/puzakroman35-sys/ohmatdyt_crm.git"
    }
    
    Write-Host "Клонуємо репозиторій..." -ForegroundColor Gray
    Invoke-SSHCommand -Command "git clone $repoUrl $REMOTE_DIR" -Description "Клонування репозиторію"
    
    Write-Success "Репозиторій склоновано"
}

# ============================================================================
# STEP 4: Environment Configuration
# ============================================================================

Write-Step "4" "Налаштування середовища (.env файлів)"

Write-Host "Переходимо в директорію проекту..." -ForegroundColor Gray

# Create .env.prod if not exists
$envSetupScript = @"
cd $REMOTE_DIR/ohmatdyt-crm

# Check if .env.prod exists
if [ ! -f .env.prod ]; then
    echo "Creating .env.prod from template..."
    if [ -f .env.example ]; then
        cp .env.example .env.prod
    else
        echo "Warning: .env.example not found"
    fi
fi

# Update .env.prod with new server IP
sed -i 's/192\.168\.31\.248/10.24.2.187/g' .env.prod
sed -i 's/192\.168\.31\.249/10.24.2.187/g' .env.prod

# Generate random passwords if needed
if grep -q "change_me" .env.prod; then
    echo "Warning: Default passwords found in .env.prod"
    echo "Please update manually after deployment"
fi

echo "Environment files configured"
ls -la .env*
"@

ssh $SERVER "$envSetupScript"

Write-Success "Environment файли налаштовано"
Write-Warning "Рекомендується перевірити та оновити паролі в .env.prod вручну!"

# ============================================================================
# STEP 5: Create Docker Volumes
# ============================================================================

Write-Step "5" "Створення Docker volumes"

$volumesScript = @"
cd $REMOTE_DIR/ohmatdyt-crm

echo "Creating Docker volumes..."
docker volume create ${PROJECT_NAME}_db-data 2>/dev/null || echo "Volume db-data already exists"
docker volume create ${PROJECT_NAME}_media 2>/dev/null || echo "Volume media already exists"
docker volume create ${PROJECT_NAME}_static 2>/dev/null || echo "Volume static already exists"

echo ""
echo "Docker volumes:"
docker volume ls | grep $PROJECT_NAME
"@

ssh $SERVER "$volumesScript"

Write-Success "Docker volumes створено"

# ============================================================================
# STEP 6: Build Docker Images
# ============================================================================

Write-Step "6" "Збірка Docker образів"

Write-Warning "Це може зайняти 10-15 хвилин..."

$buildScript = @"
cd $REMOTE_DIR/ohmatdyt-crm

echo "Building Docker images for production..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

echo ""
echo "Build completed!"
"@

ssh $SERVER "$buildScript"

Write-Success "Docker образи зібрано"

# ============================================================================
# STEP 7: Start Services
# ============================================================================

Write-Step "7" "Запуск сервісів"

$startScript = @"
cd $REMOTE_DIR/ohmatdyt-crm

echo "Starting services..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

echo ""
echo "Waiting for services to start (20 seconds)..."
sleep 20

echo ""
echo "Services status:"
docker compose ps
"@

ssh $SERVER "$startScript"

Write-Success "Сервіси запущено"

# ============================================================================
# STEP 8: Database Migrations
# ============================================================================

Write-Step "8" "Міграції бази даних"

$migrationsScript = @"
cd $REMOTE_DIR/ohmatdyt-crm

echo "Waiting for database to be ready..."
sleep 10

echo "Running database migrations..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T api alembic upgrade head

if [ $? -eq 0 ]; then
    echo "Migrations completed successfully"
else
    echo "Warning: Migrations may have failed. Check logs."
fi
"@

ssh $SERVER "$migrationsScript"

Write-Success "Міграції виконано"

# ============================================================================
# STEP 9: Health Check
# ============================================================================

Write-Step "9" "Перевірка стану системи"

$healthCheckScript = @"
cd $REMOTE_DIR/ohmatdyt-crm

echo "=== Container Status ==="
docker compose ps

echo ""
echo "=== Recent Logs (last 20 lines) ==="
docker compose logs --tail=20

echo ""
echo "=== Volume Status ==="
docker volume ls | grep $PROJECT_NAME

echo ""
echo "=== Disk Usage ==="
df -h | grep -E '(Filesystem|/$)'
"@

ssh $SERVER "$healthCheckScript"

# ============================================================================
# COMPLETION
# ============================================================================

Write-Header "✅ Deployment Completed Successfully!"

Write-Host "🌐 Application URLs:" -ForegroundColor $ColorSuccess
Write-Host "   Frontend:        http://$ServerIP" -ForegroundColor White
Write-Host "   API Docs:        http://$ServerIP/api/docs" -ForegroundColor White
Write-Host "   API Direct:      http://$ServerIP:8000" -ForegroundColor White
Write-Host ""

Write-Host "📝 Next Steps:" -ForegroundColor $ColorInfo
Write-Host "   1. Перевірте .env.prod та оновіть паролі:" -ForegroundColor Yellow
Write-Host "      ssh $SERVER" -ForegroundColor Gray
Write-Host "      nano $REMOTE_DIR/ohmatdyt-crm/.env.prod" -ForegroundColor Gray
Write-Host ""
Write-Host "   2. Створіть суперюзера (якщо потрібно):" -ForegroundColor Yellow
Write-Host "      ssh $SERVER" -ForegroundColor Gray
Write-Host "      cd $REMOTE_DIR/ohmatdyt-crm" -ForegroundColor Gray
Write-Host "      docker compose exec api python -m app.scripts.create_superuser" -ForegroundColor Gray
Write-Host ""
Write-Host "   3. Налаштуйте SSL/HTTPS (опціонально):" -ForegroundColor Yellow
Write-Host "      - Додайте домен" -ForegroundColor Gray
Write-Host "      - Налаштуйте Let's Encrypt" -ForegroundColor Gray
Write-Host ""

Write-Host "🔧 Корисні команди:" -ForegroundColor $ColorInfo
Write-Host "   # Підключення до сервера" -ForegroundColor Gray
Write-Host "   ssh $SERVER" -ForegroundColor White
Write-Host ""
Write-Host "   # Перегляд логів" -ForegroundColor Gray
Write-Host "   docker compose logs -f" -ForegroundColor White
Write-Host "   docker compose logs -f api" -ForegroundColor White
Write-Host "   docker compose logs -f frontend" -ForegroundColor White
Write-Host ""
Write-Host "   # Управління сервісами" -ForegroundColor Gray
Write-Host "   docker compose ps" -ForegroundColor White
Write-Host "   docker compose restart" -ForegroundColor White
Write-Host "   docker compose down" -ForegroundColor White
Write-Host "   docker compose up -d" -ForegroundColor White
Write-Host ""

Write-Host "$('='*80)" -ForegroundColor $ColorInfo
Write-Host "Deployment script created by: deployment automation" -ForegroundColor DarkGray
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor DarkGray
Write-Host "$('='*80)`n" -ForegroundColor $ColorInfo
