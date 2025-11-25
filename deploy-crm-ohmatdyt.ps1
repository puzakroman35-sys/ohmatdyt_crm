# ============================================================================
# Remote Deployment Script for crm.ohmatdyt.com.ua
# ============================================================================

param(
    [string]$ServerHost = "crm.ohmatdyt.com.ua",
    [string]$ServerUser = "crm",
    [int]$ServerPort = 54965,
    [string]$ProjectDir = "~/ohmatdyt-crm/ohmatdyt-crm",
    [switch]$SkipEnvUpload,
    [switch]$SkipSSLSetup,
    [switch]$QuickDeploy
)

$SERVER = "${ServerUser}@${ServerHost}"
$SSH_OPTS = "-p $ServerPort"
$SCP_OPTS = "-P $ServerPort"
$LOCAL_ENV_FILE = "f:\ohmatdyt_crm\ohmatdyt-crm\.env.prod"

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
    Write-Host "`n[STEP $StepNumber] $Message" -ForegroundColor $ColorStep
    Write-Host "$('-'*80)" -ForegroundColor DarkGray
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor $ColorSuccess
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $ColorWarning
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $ColorError
}

function Invoke-SSHCommand {
    param(
        [string]$Command,
        [string]$Description = ""
    )
    
    if ($Description) {
        Write-Host ">> $Description" -ForegroundColor Gray
    }
    
    ssh $SSH_OPTS $SERVER "$Command"
    
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Command failed with exit code $LASTEXITCODE"
        return $false
    }
    return $true
}

# ============================================================================
# MAIN DEPLOYMENT PROCESS
# ============================================================================

Write-Header "Ohmatdyt CRM - Remote Production Deployment"

Write-Host "Deployment Configuration:" -ForegroundColor $ColorInfo
Write-Host "   Server:     $SERVER" -ForegroundColor White
Write-Host "   Port:       $ServerPort" -ForegroundColor White
Write-Host "   Project:    $ProjectDir" -ForegroundColor White
Write-Host "   Domain:     crm.ohmatdyt.com.ua" -ForegroundColor White
Write-Host ""

# ============================================================================
# STEP 0: Connection Test
# ============================================================================

Write-Step "0" "Connection Test"

Write-Host "Testing SSH connection..." -ForegroundColor Gray
$testResult = ssh $SSH_OPTS -o ConnectTimeout=10 $SERVER "echo 'Connection OK'" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Cannot connect to server!"
    Write-Host "Error: $testResult" -ForegroundColor Red
    Write-Host "`nPlease check:" -ForegroundColor Yellow
    Write-Host "  1. Server address: $SERVER" -ForegroundColor Yellow
    Write-Host "  2. SSH service is running" -ForegroundColor Yellow
    Write-Host "  3. SSH keys are correct" -ForegroundColor Yellow
    exit 1
}

Write-Success "Connected to server successfully"

# ============================================================================
# STEP 1: Upload .env.prod
# ============================================================================

if (-not $SkipEnvUpload) {
    Write-Step "1" "Uploading .env.prod to server"
    
    if (-not (Test-Path $LOCAL_ENV_FILE)) {
        Write-ErrorMsg ".env.prod file not found: $LOCAL_ENV_FILE"
        exit 1
    }
    
    Write-Host "Uploading file to server..." -ForegroundColor Gray
    scp $SCP_OPTS $LOCAL_ENV_FILE "${SERVER}:~/ohmatdyt-crm/ohmatdyt-crm/.env.prod"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success ".env.prod uploaded"
    } else {
        Write-ErrorMsg "Failed to upload .env.prod"
        exit 1
    }
} else {
    Write-Warning "Skipping .env.prod upload"
}

# ============================================================================
# STEP 2: Upload deployment script
# ============================================================================

Write-Step "2" "Uploading deployment script"

$LOCAL_DEPLOY_SCRIPT = "f:\ohmatdyt_crm\ohmatdyt-crm\deploy-crm-ohmatdyt.sh"

if (Test-Path $LOCAL_DEPLOY_SCRIPT) {
    scp $SCP_OPTS $LOCAL_DEPLOY_SCRIPT "${SERVER}:~/ohmatdyt-crm/ohmatdyt-crm/deploy-crm-ohmatdyt.sh"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Deployment script uploaded"
        
        # Make script executable
        Invoke-SSHCommand -Command "chmod +x ${ProjectDir}/deploy-crm-ohmatdyt.sh" -Description "Setting execute permissions"
    } else {
        Write-Warning "Failed to upload deployment script"
        $QuickDeploy = $false
    }
} else {
    Write-Warning "Deployment script not found locally"
    $QuickDeploy = $false
}

# ============================================================================
# STEP 3: Run deployment
# ============================================================================

if ($QuickDeploy -and (Test-Path $LOCAL_DEPLOY_SCRIPT)) {
    Write-Step "3" "Running automatic deployment"
    
    Invoke-SSHCommand -Command "cd ${ProjectDir}; bash deploy-crm-ohmatdyt.sh" -Description "Executing deployment script"
    
} else {
    Write-Step "3" "Manual deployment"
    
    # Create volumes
    Write-Host "`nCreating Docker volumes..." -ForegroundColor Gray
    Invoke-SSHCommand -Command "docker volume create ohmatdyt_crm_db-data 2>/dev/null || true"
    Invoke-SSHCommand -Command "docker volume create ohmatdyt_crm_media 2>/dev/null || true"
    Invoke-SSHCommand -Command "docker volume create ohmatdyt_crm_static 2>/dev/null || true"
    Write-Success "Volumes created"
    
    # Setup SSL if needed
    if (-not $SkipSSLSetup) {
        Write-Host "`nSSL Setup..." -ForegroundColor Gray
        Write-Warning "If Let's Encrypt is not configured yet, run setup-letsencrypt.sh manually"
    }
    
    # Build images
    Write-Host "`nBuilding Docker images (this may take 10-15 minutes)..." -ForegroundColor Gray
    Invoke-SSHCommand -Command "cd ${ProjectDir}; docker compose -f docker-compose.yml -f docker-compose.prod.yml build" -Description "Building images"
    Write-Success "Images built"
    
    # Start services
    Write-Host "`nStarting services..." -ForegroundColor Gray
    Invoke-SSHCommand -Command "cd ${ProjectDir}; docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d" -Description "Starting containers"
    Write-Success "Services started"
    
    Write-Host "`nWaiting for services to start..." -ForegroundColor Gray
    Start-Sleep -Seconds 30
    
    # Check status
    Write-Host "`nServices status:" -ForegroundColor Gray
    Invoke-SSHCommand -Command "cd ${ProjectDir}; docker compose ps"
    
    # Run migrations
    Write-Host "`nRunning migrations..." -ForegroundColor Gray
    Invoke-SSHCommand -Command "cd ${ProjectDir}; docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T api alembic upgrade head" -Description "Database migrations"
    Write-Success "Migrations completed"
    
    # Create admin
    Write-Host "`nCreating administrator..." -ForegroundColor Gray
    
    $pythonScript = @'
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role
try:
    db = SessionLocal()
    admin = db.query(User).filter(User.email == "admin@ohmatdyt.com").first()
    if admin:
        print("Admin already exists")
    else:
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
        admin = User(email="admin@ohmatdyt.com", username="admin", full_name="Administrator", hashed_password=get_password_hash("admin123"), is_active=True, role_id=admin_role.id)
        db.add(admin)
        db.commit()
        print("Admin created successfully")
    db.close()
except Exception as e:
    print(f"Error: {e}")
'@
    
    $encodedScript = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($pythonScript))
    Invoke-SSHCommand -Command "cd ${ProjectDir}; echo '$encodedScript' | base64 -d | docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T api python"
}

# ============================================================================
# STEP 4: Health checks
# ============================================================================

Write-Step "4" "Health checks"

Start-Sleep -Seconds 5

Write-Host "Checking frontend..." -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "https://crm.ohmatdyt.com.ua/health" -SkipCertificateCheck -TimeoutSec 10 -ErrorAction Stop
    Write-Success "Frontend is accessible"
} catch {
    Write-Warning "Frontend is not accessible yet or SSL issues"
}

Write-Host "Checking API..." -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "https://crm.ohmatdyt.com.ua/api/healthz" -SkipCertificateCheck -TimeoutSec 10 -ErrorAction Stop
    Write-Success "API is accessible"
} catch {
    Write-Warning "API is not accessible yet"
}

# ============================================================================
# Final summary
# ============================================================================

Write-Header "Deployment completed!"

Write-Host "Services:" -ForegroundColor $ColorSuccess
Write-Host "   Frontend:  https://crm.ohmatdyt.com.ua" -ForegroundColor Cyan
Write-Host "   API:       https://crm.ohmatdyt.com.ua/api/" -ForegroundColor Cyan
Write-Host "   API Docs:  https://crm.ohmatdyt.com.ua/api/docs" -ForegroundColor Cyan
Write-Host "   Health:    https://crm.ohmatdyt.com.ua/health" -ForegroundColor Cyan

Write-Host "`nTemporary credentials:" -ForegroundColor $ColorWarning
Write-Host "   Email:     admin@ohmatdyt.com" -ForegroundColor White
Write-Host "   Password:  admin123" -ForegroundColor White
Write-Host "   IMPORTANT: Change password after first login!" -ForegroundColor Red

Write-Host "`nUseful commands:" -ForegroundColor $ColorInfo
Write-Host "   Logs:      ssh $SSH_OPTS $SERVER `"cd $ProjectDir; docker compose logs -f`"" -ForegroundColor Gray
Write-Host "   Status:    ssh $SSH_OPTS $SERVER `"cd $ProjectDir; docker compose ps`"" -ForegroundColor Gray
Write-Host "   Restart:   ssh $SSH_OPTS $SERVER `"cd $ProjectDir; docker compose restart`"" -ForegroundColor Gray

Write-Success "`nDone!"
Write-Host "`nDetailed documentation: DEPLOYMENT_CRM_OHMATDYT_COM_UA.md" -ForegroundColor Gray
