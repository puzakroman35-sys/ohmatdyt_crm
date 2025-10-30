#!/bin/bash
# INF-003: Script to generate self-signed SSL certificates for development/testing
# For production, use Let's Encrypt (see setup-letsencrypt.sh)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSL_DIR="${SCRIPT_DIR}/ssl"

echo "=================================================="
echo "  Generating Self-Signed SSL Certificates"
echo "=================================================="
echo ""

# Create SSL directory if it doesn't exist
mkdir -p "$SSL_DIR"

# Check if certificates already exist
if [ -f "$SSL_DIR/cert.pem" ] && [ -f "$SSL_DIR/key.pem" ]; then
    echo "⚠️  Certificates already exist in $SSL_DIR"
    read -p "Do you want to regenerate them? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing certificates."
        exit 0
    fi
fi

# Get domain name from environment or use default
DEFAULT_DOMAIN="localhost"
read -p "Enter domain name (default: $DEFAULT_DOMAIN): " DOMAIN
DOMAIN="${DOMAIN:-$DEFAULT_DOMAIN}"

echo ""
echo "Generating self-signed certificate for: $DOMAIN"
echo ""

# Generate private key and certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$SSL_DIR/key.pem" \
    -out "$SSL_DIR/cert.pem" \
    -subj "/C=UA/ST=Kyiv/L=Kyiv/O=Ohmatdyt CRM/CN=$DOMAIN" \
    -addext "subjectAltName=DNS:$DOMAIN,DNS:www.$DOMAIN,DNS:localhost,IP:127.0.0.1"

# Set appropriate permissions
chmod 600 "$SSL_DIR/key.pem"
chmod 644 "$SSL_DIR/cert.pem"

echo ""
echo "✅ Self-signed SSL certificates generated successfully!"
echo ""
echo "📁 Certificate location:"
echo "   Certificate: $SSL_DIR/cert.pem"
echo "   Private key: $SSL_DIR/key.pem"
echo ""
echo "⚠️  WARNING: Self-signed certificates should NOT be used in production!"
echo "   For production, use Let's Encrypt: ./setup-letsencrypt.sh"
echo ""
echo "Certificate details:"
openssl x509 -in "$SSL_DIR/cert.pem" -text -noout | grep -A 2 "Subject:"
echo ""
echo "Valid until:"
openssl x509 -in "$SSL_DIR/cert.pem" -enddate -noout
echo ""
echo "=================================================="
