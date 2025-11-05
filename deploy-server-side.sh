#!/bin/bash
# ============================================================================
# Server-side deployment script for Ohmatdyt CRM
# ============================================================================
# Run this script directly on the server after cloning the repository
# Usage: ./deploy-server-side.sh
# ============================================================================

set -e

PROJECT_DIR="$HOME/ohmatdyt-crm/ohmatdyt-crm"
PROJECT_NAME="ohmatdyt_crm"
SERVER_IP="10.24.2.187"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

function print_header() {
    echo -e "\n${CYAN}================================================================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}================================================================================${NC}\n"
}

function print_step() {
    echo -e "\n${MAGENTA}[КРОК $1] $2${NC}"
    echo -e "${BLUE}--------------------------------------------------------------------------------${NC}"
}

function print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

function print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

function print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ============================================================================
# MAIN DEPLOYMENT
# ============================================================================

print_header "🚀 Ohmatdyt CRM - Server-Side Deployment"

echo -e "${BLUE}Configuration:${NC}"
echo -e "  Project Directory: ${WHITE}$PROJECT_DIR${NC}"
echo -e "  Project Name:      ${WHITE}$PROJECT_NAME${NC}"
echo -e "  Server IP:         ${WHITE}$SERVER_IP${NC}"
echo ""

# ============================================================================
# STEP 1: Check Prerequisites
# ============================================================================

print_step "1" "Перевірка необхідних компонентів"

# Check if we're in the right directory
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Project directory not found: $PROJECT_DIR"
    echo "Please clone the repository first:"
    echo "  git clone https://github.com/puzakroman35-sys/ohmatdyt_crm.git ~/ohmatdyt-crm"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    echo "Install Docker using:"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sudo sh get-docker.sh"
    exit 1
fi
print_success "Docker is installed: $(docker --version)"

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    print_error "Docker Compose plugin is not installed"
    exit 1
fi
print_success "Docker Compose is installed: $(docker compose version)"

# Check if user is in docker group
if ! groups | grep -q docker; then
    print_warning "Current user is not in docker group"
    echo "Add user to docker group:"
    echo "  sudo usermod -aG docker \$USER"
    echo "  newgrp docker"
    echo ""
    read -p "Continue anyway? (y/N): " continue
    if [ "$continue" != "y" ] && [ "$continue" != "Y" ]; then
        exit 1
    fi
fi

# ============================================================================
# STEP 2: Prepare Environment Files
# ============================================================================

print_step "2" "Підготовка конфігураційних файлів"

cd "$PROJECT_DIR"

# Create .env.prod if not exists
if [ ! -f .env.prod ]; then
    print_warning ".env.prod not found, creating from template..."
    if [ -f .env.example ]; then
        cp .env.example .env.prod
        print_success "Created .env.prod from .env.example"
    else
        print_error ".env.example not found"
        exit 1
    fi
fi

# Update IP addresses in .env.prod
echo "Updating server IP in .env.prod..."
sed -i.bak "s/192\.168\.31\.248/$SERVER_IP/g" .env.prod
sed -i.bak "s/192\.168\.31\.249/$SERVER_IP/g" .env.prod

# Check for default passwords
if grep -q "change_me" .env.prod; then
    print_warning "Default passwords found in .env.prod"
    echo ""
    read -p "Would you like to generate random passwords? (Y/n): " generate_passwords
    
    if [ "$generate_passwords" != "n" ] && [ "$generate_passwords" != "N" ]; then
        # Generate random passwords
        POSTGRES_PASS=$(openssl rand -base64 24)
        JWT_SECRET=$(openssl rand -base64 48)
        
        sed -i.bak "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASS/" .env.prod
        sed -i.bak "s/JWT_SECRET=.*/JWT_SECRET=$JWT_SECRET/" .env.prod
        sed -i.bak "s|DATABASE_URL=postgresql+psycopg://ohm_user:.*@db:5432/ohm_db|DATABASE_URL=postgresql+psycopg://ohm_user:$POSTGRES_PASS@db:5432/ohm_db|" .env.prod
        
        print_success "Random passwords generated and updated in .env.prod"
        echo ""
        echo "IMPORTANT: Save these credentials!"
        echo "  POSTGRES_PASSWORD: $POSTGRES_PASS"
        echo "  JWT_SECRET: $JWT_SECRET"
        echo ""
        read -p "Press Enter to continue..."
    fi
fi

print_success "Environment files prepared"
echo ""
echo "Current .env.prod settings:"
grep -E "^(APP_ENV|POSTGRES_DB|POSTGRES_USER|ALLOWED_HOSTS|NGINX_SERVER_NAME)=" .env.prod || true

# ============================================================================
# STEP 3: Create Docker Volumes
# ============================================================================

print_step "3" "Створення Docker volumes"

echo "Creating Docker volumes..."
docker volume create ${PROJECT_NAME}_db-data 2>/dev/null || print_warning "Volume db-data already exists"
docker volume create ${PROJECT_NAME}_media 2>/dev/null || print_warning "Volume media already exists"
docker volume create ${PROJECT_NAME}_static 2>/dev/null || print_warning "Volume static already exists"

echo ""
echo "Docker volumes:"
docker volume ls | grep $PROJECT_NAME

print_success "Docker volumes ready"

# ============================================================================
# STEP 4: Build Docker Images
# ============================================================================

print_step "4" "Збірка Docker образів"

print_warning "This will take 10-15 minutes..."
echo ""

docker compose -f docker-compose.yml -f docker-compose.prod.yml build

print_success "Docker images built successfully"

# ============================================================================
# STEP 5: Start Services
# ============================================================================

print_step "5" "Запуск сервісів"

echo "Starting all services..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

echo ""
echo "Waiting for services to start (20 seconds)..."
sleep 20

echo ""
echo "Services status:"
docker compose ps

print_success "Services started"

# ============================================================================
# STEP 6: Database Migrations
# ============================================================================

print_step "6" "Міграції бази даних"

echo "Waiting for database to be ready..."
sleep 10

echo "Running database migrations..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T api alembic upgrade head

if [ $? -eq 0 ]; then
    print_success "Database migrations completed"
else
    print_error "Migration failed - check logs above"
fi

# ============================================================================
# STEP 7: Health Check
# ============================================================================

print_step "7" "Перевірка стану системи"

echo ""
echo "=== Container Status ==="
docker compose ps

echo ""
echo "=== Recent Logs ==="
docker compose logs --tail=20

echo ""
echo "=== Health Check ==="
sleep 5
curl -s http://localhost/api/docs > /dev/null && print_success "API is responding" || print_warning "API may not be ready yet"
curl -s http://localhost > /dev/null && print_success "Frontend is responding" || print_warning "Frontend may not be ready yet"

# ============================================================================
# COMPLETION
# ============================================================================

print_header "✅ Deployment Completed Successfully!"

echo -e "${GREEN}🌐 Application URLs:${NC}"
echo -e "   Frontend:        ${WHITE}http://$SERVER_IP${NC}"
echo -e "   API Docs:        ${WHITE}http://$SERVER_IP/api/docs${NC}"
echo -e "   API Direct:      ${WHITE}http://$SERVER_IP:8000${NC}"
echo ""

echo -e "${CYAN}📝 Next Steps:${NC}"
echo -e "   ${YELLOW}1. Create superuser (if needed):${NC}"
echo -e "      ${WHITE}docker compose exec api python -m app.scripts.create_superuser${NC}"
echo ""
echo -e "   ${YELLOW}2. Check logs:${NC}"
echo -e "      ${WHITE}docker compose logs -f${NC}"
echo ""
echo -e "   ${YELLOW}3. Setup SSL/HTTPS (optional):${NC}"
echo -e "      - Configure domain name"
echo -e "      - Setup Let's Encrypt certificates"
echo ""

echo -e "${CYAN}🔧 Useful Commands:${NC}"
echo -e "   ${WHITE}docker compose ps${NC}              # Service status"
echo -e "   ${WHITE}docker compose logs -f${NC}         # View logs"
echo -e "   ${WHITE}docker compose restart${NC}         # Restart services"
echo -e "   ${WHITE}docker compose down${NC}            # Stop all services"
echo -e "   ${WHITE}docker compose up -d${NC}           # Start services"
echo ""

echo -e "${BLUE}================================================================================${NC}"
echo -e "${BLUE}Deployment completed at: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${BLUE}================================================================================${NC}\n"
