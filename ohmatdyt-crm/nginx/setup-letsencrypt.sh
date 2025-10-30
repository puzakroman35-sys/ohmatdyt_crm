#!/bin/bash
# INF-003: Setup Let's Encrypt SSL certificates using Certbot
# This script helps configure automated SSL certificate issuance and renewal

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSL_DIR="${SCRIPT_DIR}/ssl"
CERTBOT_DIR="${SCRIPT_DIR}/../certbot"
WEBROOT_DIR="${SCRIPT_DIR}/../certbot/www"

echo "=================================================="
echo "  Let's Encrypt SSL Certificate Setup"
echo "=================================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "⚠️  Please do not run this script as root"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker compose &> /dev/null; then
    echo "❌ docker compose not found. Please install Docker Compose."
    exit 1
fi

# Get domain name
read -p "Enter your domain name (e.g., example.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo "❌ Domain name is required!"
    exit 1
fi

# Get email for Let's Encrypt notifications
read -p "Enter your email for Let's Encrypt notifications: " EMAIL
if [ -z "$EMAIL" ]; then
    echo "❌ Email is required!"
    exit 1
fi

# Confirm settings
echo ""
echo "Configuration:"
echo "  Domain: $DOMAIN"
echo "  Email: $EMAIL"
echo ""
read -p "Is this correct? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Create necessary directories
mkdir -p "$CERTBOT_DIR/conf"
mkdir -p "$CERTBOT_DIR/www"
mkdir -p "$SSL_DIR"

echo ""
echo "=================================================="
echo "Step 1: Starting Nginx with HTTP-only configuration"
echo "=================================================="
echo ""

# Check if Nginx is running
if docker compose ps nginx | grep -q "Up"; then
    echo "Stopping current Nginx container..."
    docker compose stop nginx
fi

echo "Starting Nginx for ACME challenge..."
docker compose up -d nginx

echo "Waiting for Nginx to be ready..."
sleep 5

echo ""
echo "=================================================="
echo "Step 2: Obtaining SSL certificate from Let's Encrypt"
echo "=================================================="
echo ""

# Run Certbot in standalone mode or webroot mode
docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

CERT_STATUS=$?

if [ $CERT_STATUS -ne 0 ]; then
    echo "❌ Failed to obtain certificate!"
    echo ""
    echo "Common issues:"
    echo "  1. Domain DNS not pointing to this server"
    echo "  2. Port 80 not accessible from internet"
    echo "  3. Firewall blocking HTTP traffic"
    echo ""
    echo "Please check and try again."
    exit 1
fi

echo ""
echo "=================================================="
echo "Step 3: Copying certificates to nginx/ssl directory"
echo "=================================================="
echo ""

# Copy certificates to nginx ssl directory
docker compose exec nginx cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" /etc/nginx/ssl/cert.pem
docker compose exec nginx cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" /etc/nginx/ssl/key.pem

echo "Certificates copied successfully!"

echo ""
echo "=================================================="
echo "Step 4: Restarting Nginx with HTTPS configuration"
echo "=================================================="
echo ""

docker compose restart nginx

echo "Waiting for Nginx to restart..."
sleep 3

# Test HTTPS
if curl -k -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/health" | grep -q "200"; then
    echo "✅ HTTPS is working!"
else
    echo "⚠️  HTTPS check failed. Please verify manually."
fi

echo ""
echo "=================================================="
echo "Step 5: Setting up automatic renewal"
echo "=================================================="
echo ""

# Create renewal cron job
CRON_CMD="0 3 * * * cd $(dirname $SCRIPT_DIR) && docker compose run --rm certbot renew && docker compose exec nginx nginx -s reload"

echo "To enable automatic renewal, add this to your crontab:"
echo ""
echo "$CRON_CMD"
echo ""
read -p "Would you like to add this to crontab now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "✅ Cron job added successfully!"
else
    echo "Skipping cron job setup. You can add it manually later."
fi

echo ""
echo "=================================================="
echo "✅ Let's Encrypt SSL Setup Complete!"
echo "=================================================="
echo ""
echo "Certificate details:"
echo "  Domain: $DOMAIN"
echo "  Certificate: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
echo "  Private key: /etc/letsencrypt/live/$DOMAIN/privkey.pem"
echo ""
echo "Certificate is valid for 90 days and will auto-renew if cron job is configured."
echo ""
echo "To manually renew:"
echo "  docker compose run --rm certbot renew"
echo "  docker compose exec nginx nginx -s reload"
echo ""
echo "=================================================="
