# ============================================================================
# Production Deployment Script for 10.24.2.187
# ============================================================================
# Server: rpadmin@10.24.2.187
# Project: Ohmatdyt CRM
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
$REPO_URL = "https://github.com/puzakroman35-sys/ohmatdyt_crm.git"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Production Server Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server:     $SERVER" -ForegroundColor Yellow
Write-Host "Directory:  $REMOTE_DIR" -ForegroundColor Yellow
Write-Host "Project:    $PROJECT_NAME" -ForegroundColor Yellow
Write-Host ""

# Test connection
Write-Host "[STEP 0] Testing SSH connection..." -ForegroundColor Magenta
$testResult = ssh -o ConnectTimeout=5 $SERVER "echo 'OK'" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Cannot connect to $SERVER" -ForegroundColor Red
    exit 1
}

Write-Host "Connection OK!" -ForegroundColor Green
Write-Host ""

# ============================================================================
# STEP 1: Server Setup
# ============================================================================

if (-not $SkipServerSetup) {
    Write-Host "[STEP 1] Server preparation..." -ForegroundColor Magenta
    
    Write-Host "Updating system packages..." -ForegroundColor Gray
    ssh $SERVER "sudo apt-get update"
    
    Write-Host "Installing required packages..." -ForegroundColor Gray
    ssh $SERVER "sudo apt-get install -y git curl wget nano htop"
    
    Write-Host "Server preparation completed" -ForegroundColor Green
} else {
    Write-Host "[STEP 1] Skipped (SkipServerSetup)" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# STEP 2: Docker Installation
# ============================================================================

if (-not $SkipDockerInstall) {
    Write-Host "[STEP 2] Docker installation..." -ForegroundColor Magenta
    
    Write-Host "Checking Docker..." -ForegroundColor Gray
    $dockerCheck = ssh $SERVER "command -v docker" 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing Docker..." -ForegroundColor Yellow
        
        $dockerScript = @'
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
sudo apt-get install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker rpadmin
sudo systemctl enable docker
sudo systemctl start docker
'@
        
        ssh $SERVER "$dockerScript"
        Write-Host "Docker installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Docker already installed" -ForegroundColor Green
    }
    
    ssh $SERVER "docker compose version"
    
} else {
    Write-Host "[STEP 2] Skipped (SkipDockerInstall)" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# STEP 3: Clone Repository
# ============================================================================

Write-Host "[STEP 3] Repository setup..." -ForegroundColor Magenta

$dirCheck = ssh $SERVER "test -d $REMOTE_DIR && echo 'exists' || echo 'not_exists'" 2>&1

if ($dirCheck -match "exists") {
    Write-Host "Directory exists. Remove and clone again? (y/N): " -ForegroundColor Yellow -NoNewline
    $response = Read-Host
    
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "Removing old directory..." -ForegroundColor Gray
        ssh $SERVER "rm -rf $REMOTE_DIR"
        $shouldClone = $true
    } else {
        $shouldClone = $false
    }
} else {
    $shouldClone = $true
}

if ($shouldClone) {
    Write-Host "Cloning repository..." -ForegroundColor Gray
    ssh $SERVER "git clone $REPO_URL $REMOTE_DIR"
    Write-Host "Repository cloned!" -ForegroundColor Green
} else {
    Write-Host "Using existing directory" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# STEP 4: Environment Configuration
# ============================================================================

Write-Host "[STEP 4] Environment configuration..." -ForegroundColor Magenta

$envScript = @"
cd $REMOTE_DIR/ohmatdyt-crm
if [ ! -f .env.prod ]; then
    cp .env.example .env.prod
    echo 'Created .env.prod'
fi
sed -i 's/192\.168\.31\.248/10.24.2.187/g' .env.prod
sed -i 's/192\.168\.31\.249/10.24.2.187/g' .env.prod
echo 'Environment configured'
ls -la .env*
"@

ssh $SERVER "$envScript"
Write-Host "Environment files ready" -ForegroundColor Green
Write-Host ""

# ============================================================================
# STEP 5: Docker Volumes
# ============================================================================

Write-Host "[STEP 5] Creating Docker volumes..." -ForegroundColor Magenta

$volumeScript = @"
docker volume create ${PROJECT_NAME}_db-data 2>/dev/null || echo 'db-data exists'
docker volume create ${PROJECT_NAME}_media 2>/dev/null || echo 'media exists'
docker volume create ${PROJECT_NAME}_static 2>/dev/null || echo 'static exists'
docker volume ls | grep $PROJECT_NAME
"@

ssh $SERVER "$volumeScript"
Write-Host "Volumes created" -ForegroundColor Green
Write-Host ""

# ============================================================================
# STEP 6: Build Images
# ============================================================================

Write-Host "[STEP 6] Building Docker images (10-15 min)..." -ForegroundColor Magenta

$buildScript = @"
cd $REMOTE_DIR/ohmatdyt-crm
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
"@

ssh $SERVER "$buildScript"
Write-Host "Images built successfully" -ForegroundColor Green
Write-Host ""

# ============================================================================
# STEP 7: Start Services
# ============================================================================

Write-Host "[STEP 7] Starting services..." -ForegroundColor Magenta

$startScript = @"
cd $REMOTE_DIR/ohmatdyt-crm
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
sleep 20
docker compose ps
"@

ssh $SERVER "$startScript"
Write-Host "Services started" -ForegroundColor Green
Write-Host ""

# ============================================================================
# STEP 8: Database Migrations
# ============================================================================

Write-Host "[STEP 8] Running database migrations..." -ForegroundColor Magenta

$migrateScript = @"
cd $REMOTE_DIR/ohmatdyt-crm
sleep 10
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T api alembic upgrade head
"@

ssh $SERVER "$migrateScript"
Write-Host "Migrations completed" -ForegroundColor Green
Write-Host ""

# ============================================================================
# STEP 9: Health Check
# ============================================================================

Write-Host "[STEP 9] Health check..." -ForegroundColor Magenta

$healthScript = @"
cd $REMOTE_DIR/ohmatdyt-crm
echo '=== Container Status ==='
docker compose ps
echo ''
echo '=== Recent Logs ==='
docker compose logs --tail=20
"@

ssh $SERVER "$healthScript"
Write-Host ""

# ============================================================================
# COMPLETION
# ============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deployment Completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "  Frontend:   http://$ServerIP" -ForegroundColor White
Write-Host "  API Docs:   http://$ServerIP/api/docs" -ForegroundColor White
Write-Host "  API Direct: http://$ServerIP:8000" -ForegroundColor White
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Update passwords in .env.prod" -ForegroundColor Gray
Write-Host "     ssh $SERVER" -ForegroundColor Gray
Write-Host "     nano $REMOTE_DIR/ohmatdyt-crm/.env.prod" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Create superuser" -ForegroundColor Gray
Write-Host "     docker compose exec api python -m app.scripts.create_superuser" -ForegroundColor Gray
Write-Host ""

Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  docker compose logs -f          # View logs" -ForegroundColor Gray
Write-Host "  docker compose ps               # Status" -ForegroundColor Gray
Write-Host "  docker compose restart          # Restart" -ForegroundColor Gray
Write-Host ""
