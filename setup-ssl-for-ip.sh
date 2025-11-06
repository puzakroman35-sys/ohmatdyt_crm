#!/bin/bash

# Скрипт для створення self-signed SSL сертифіката з IP адресою
# Використання: ./setup-ssl-for-ip.sh

SERVER_IP="10.24.2.187"
CERT_DIR="/etc/nginx/ssl"
DAYS_VALID=365

echo "🔐 Створення SSL сертифіката для IP: $SERVER_IP"

# Створюємо директорію для сертифікатів
mkdir -p $CERT_DIR

# Створюємо конфігураційний файл для OpenSSL з SAN
cat > /tmp/openssl-san.cnf << EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=UA
ST=Kyiv
L=Kyiv
O=Ohmatdyt
OU=IT Department
CN=$SERVER_IP

[v3_req]
subjectAltName = @alt_names

[alt_names]
IP.1 = $SERVER_IP
DNS.1 = $SERVER_IP
EOF

echo "📝 Генерація приватного ключа та сертифіката..."

# Генеруємо приватний ключ та сертифікат
openssl req -x509 -nodes -days $DAYS_VALID -newkey rsa:2048 \
    -keyout $CERT_DIR/selfsigned.key \
    -out $CERT_DIR/selfsigned.crt \
    -config /tmp/openssl-san.cnf \
    -extensions v3_req

# Встановлюємо правильні права доступу
chmod 600 $CERT_DIR/selfsigned.key
chmod 644 $CERT_DIR/selfsigned.crt

echo "✅ Сертифікат створено:"
echo "   Ключ: $CERT_DIR/selfsigned.key"
echo "   Сертифікат: $CERT_DIR/selfsigned.crt"
echo "   Термін дії: $DAYS_VALID днів"

# Показуємо інформацію про сертифікат
echo ""
echo "📋 Інформація про сертифікат:"
openssl x509 -in $CERT_DIR/selfsigned.crt -text -noout | grep -A 2 "Subject Alternative Name"

# Очищуємо тимчасовий файл
rm /tmp/openssl-san.cnf

echo ""
echo "⚠️  ВАЖЛИВО:"
echo "   1. Це self-signed сертифікат - браузери будуть показувати попередження"
echo "   2. Для Chrome: натисніть 'Advanced' → 'Proceed to $SERVER_IP (unsafe)'"
echo "   3. Для Firefox: натисніть 'Advanced' → 'Accept the Risk and Continue'"
echo "   4. Для продакшену рекомендується використовувати Let's Encrypt з доменом"
echo ""
echo "🔄 Перезапускаємо nginx..."
systemctl reload nginx

echo "✅ Готово! Перейдіть за адресою https://$SERVER_IP"
