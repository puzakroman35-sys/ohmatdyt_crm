#!/bin/bash
# Quick production update script

echo "================================"
echo " Production Update"
echo "================================"
echo ""

cd ohmatdyt-crm

echo "[1/7] Current status..."
git status --short
git log -1 --oneline
echo ""

echo "[2/7] Fetching changes..."
git fetch origin
echo ""

echo "[3/7] New commits:"
git log HEAD..origin/main --oneline
echo ""

echo "[4/7] Pulling changes..."
git pull origin main
echo ""

echo "[5/7] Rebuilding and restarting..."
cd ohmatdyt-crm
docker compose -f docker-compose.yml -f docker-compose.prod.yml build api frontend
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
echo ""

echo "[6/7] Waiting for services to start..."
sleep 15
echo ""

echo "[7/7] Running migrations..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T api alembic upgrade head
echo ""

echo "================================"
echo " Container Status"
echo "================================"
docker compose ps
echo ""

echo "================================"
echo " Update Complete!"
echo "================================"
echo "URLs:"
echo "  http://10.24.2.187"
echo "  http://10.24.2.187/api/docs"
echo ""
