#!/bin/bash
# Deployment script for 10.24.2.187
# Run this on the server after SSH connection

set -e

echo "========================================="
echo "  Ohmatdyt CRM Deployment"
echo "========================================="
echo ""

# Step 1: Check Docker
echo "[1/9] Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "Docker installed. Please logout and login again, then re-run this script."
    exit 0
else
    echo "Docker found: $(docker --version)"
fi

# Step 2: Navigate to home
echo ""
echo "[2/9] Setting up directory..."
cd ~
pwd

# Step 3: Clone or update repository
echo ""
echo "[3/9] Repository setup..."
if [ -d "ohmatdyt-crm" ]; then
    echo "Directory exists. Remove? (y/N)"
    read -r response
    if [ "$response" = "y" ]; then
        rm -rf ohmatdyt-crm
        git clone https://github.com/puzakroman35-sys/ohmatdyt_crm.git ohmatdyt-crm
    fi
else
    git clone https://github.com/puzakroman35-sys/ohmatdyt_crm.git ohmatdyt-crm
fi

# Step 4: Enter project directory
echo ""
echo "[4/9] Entering project directory..."
cd ohmatdyt-crm/ohmatdyt-crm
pwd

# Step 5: Setup environment
echo ""
echo "[5/9] Setting up environment..."
if [ ! -f .env.prod ]; then
    cp .env.example .env.prod
    echo "Created .env.prod"
fi
sed -i 's/192\.168\.31\.248/10.24.2.187/g' .env.prod
sed -i 's/192\.168\.31\.249/10.24.2.187/g' .env.prod
echo "Environment configured"

# Step 6: Create volumes
echo ""
echo "[6/9] Creating Docker volumes..."
docker volume create ohmatdyt_crm_db-data 2>/dev/null || echo "db-data exists"
docker volume create ohmatdyt_crm_media 2>/dev/null || echo "media exists"
docker volume create ohmatdyt_crm_static 2>/dev/null || echo "static exists"
echo "Volumes ready"

# Step 7: Build images
echo ""
echo "[7/9] Building Docker images (this takes 10-15 minutes)..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Step 8: Start services
echo ""
echo "[8/9] Starting services..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
echo "Waiting for services to start..."
sleep 30

# Step 9: Run migrations
echo ""
echo "[9/9] Running database migrations..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T api alembic upgrade head

# Status
echo ""
echo "========================================="
echo "  Deployment Complete!"
echo "========================================="
echo ""
docker compose ps
echo ""
echo "URLs:"
echo "  Frontend: http://10.24.2.187"
echo "  API Docs: http://10.24.2.187/api/docs"
echo ""
echo "Next steps:"
echo "  1. Edit .env.prod to update passwords"
echo "  2. docker compose restart"
echo "  3. Create superuser:"
echo "     docker compose exec api python -m app.scripts.create_superuser"
echo ""
