# Nginx Configuration - INF-003

## Огляд

Nginx виступає як реверс-проксі для API та Frontend з підтримкою:
- ✅ HTTP to HTTPS redirect
- ✅ SSL/TLS termination
- ✅ Static/Media files serving with aggressive caching
- ✅ Rate limiting для захисту від DDoS
- ✅ Security headers (HSTS, X-Frame-Options, CSP, etc.)
- ✅ Gzip compression
- ✅ WebSocket support для Next.js HMR
- ✅ Health check endpoints
- ✅ Structured logging

## Файли конфігурації

```
nginx/
├── nginx.conf           # Dev configuration (HTTP only)
├── nginx.prod.conf      # Production configuration (HTTPS)
├── ssl/                 # SSL certificates directory
│   ├── cert.pem        # SSL certificate
│   └── key.pem         # Private key
├── generate-ssl-certs.sh    # Generate self-signed certificates
├── setup-letsencrypt.sh     # Setup Let's Encrypt certificates
└── README.md           # This file
```

## Режими роботи

### 1. Development (HTTP)

Використовується `nginx.conf` - базова конфігурація без HTTPS.

```bash
# docker-compose.yml
docker compose up nginx
```

**Особливості:**
- Слухає тільки порт 80
- Без SSL/TLS
- Без rate limiting
- Підходить для локальної розробки

### 2. Production (HTTPS) з Self-Signed сертифікатами

Для тестування production конфігурації локально.

**Крок 1: Генерація self-signed сертифікатів**

```bash
cd nginx
./generate-ssl-certs.sh
```

Скрипт створить:
- `ssl/cert.pem` - Self-signed сертифікат
- `ssl/key.pem` - Приватний ключ

**Крок 2: Запуск з production конфігом**

```bash
# Використовуємо nginx.prod.conf
docker compose -f docker-compose.yml -f docker-compose.prod.yml up nginx
```

**Важливо:** Self-signed сертифікати **НЕ ПІДХОДЯТЬ** для production! Браузер покаже попередження про небезпеку.

### 3. Production (HTTPS) з Let's Encrypt

Для production серверів з публічним доменом.

**Передумови:**
- Публічний домен (наприклад, `crm.example.com`)
- DNS A-запис вказує на IP сервера
- Порти 80 та 443 відкриті в firewall

**Крок 1: Налаштування домену**

Відредагуйте `.env.prod`:
```env
NGINX_SERVER_NAME=crm.example.com
```

**Крок 2: Запуск Let's Encrypt setup**

```bash
cd nginx
./setup-letsencrypt.sh
```

Скрипт:
1. Запитає домен та email
2. Запустить Nginx з HTTP
3. Отримає сертифікат від Let's Encrypt
4. Перезапустить Nginx з HTTPS
5. Налаштує auto-renewal

**Крок 3: Перевірка**

```bash
# Перевірка HTTPS
curl -I https://crm.example.com/health

# Перевірка редіректу HTTP → HTTPS
curl -I http://crm.example.com/health
```

**Крок 4: Auto-renewal**

Let's Encrypt сертифікати дійсні 90 днів. Auto-renewal через cron:

```bash
# Cron job додається автоматично setup-letsencrypt.sh
# Або додайте вручну:
crontab -e

# Додайте:
0 3 * * * cd /path/to/project && docker compose run --rm certbot renew && docker compose exec nginx nginx -s reload
```

## Конфігурація Nginx

### Основні параметри

```nginx
# nginx.prod.conf

events {
    worker_connections 2048;  # Максимум з'єднань на worker
    use epoll;                # Оптимізація для Linux
    multi_accept on;          # Приймати кілька з'єднань одночасно
}

http {
    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 100;
    
    # Security
    server_tokens off;        # Приховати версію Nginx
    client_max_body_size 100M; # Макс розмір файлу (uploads)
    
    # Compression
    gzip on;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json ...;
}
```

### Rate Limiting

Захист від DDoS та brute-force атак:

```nginx
# Зони rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;
limit_conn_zone $binary_remote_addr zone=addr:10m;

# Застосування
location /api/auth/login {
    limit_req zone=login_limit burst=2 nodelay;
    # Макс 5 запитів на хвилину + burst 2
}

location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    # Макс 10 запитів на секунду + burst 20
}
```

### SSL/TLS Configuration

Сучасна конфігурація з високим рівнем безпеки:

```nginx
server {
    listen 443 ssl http2;
    
    # Certificates
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # Protocols and ciphers (Mozilla Modern)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:...';
    ssl_prefer_server_ciphers off;
    
    # Session cache
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
}
```

### Security Headers

```nginx
# HSTS - Force HTTPS for 1 year
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# Prevent clickjacking
add_header X-Frame-Options "SAMEORIGIN" always;

# Prevent MIME sniffing
add_header X-Content-Type-Options "nosniff" always;

# XSS Protection
add_header X-XSS-Protection "1; mode=block" always;

# Referrer policy
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Permissions policy
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

### Caching Strategy

```nginx
# Static files - агресивне кешування (1 рік)
location /static/ {
    alias /var/app/static/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Media files - помірне кешування (30 днів)
location /media/ {
    alias /var/app/media/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# Next.js static - агресивне кешування
location /_next/static/ {
    proxy_pass http://frontend_backend;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Proxy Configuration

```nginx
# API Backend
upstream api_backend {
    server api:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;  # Keep-alive з'єднання
}

location /api/ {
    proxy_pass http://api_backend/;
    
    # Headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Request-ID $request_id;
    
    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    
    # WebSocket support
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

## Логування

### Access Log

```nginx
log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                '$status $body_bytes_sent "$http_referer" '
                '"$http_user_agent" "$http_x_forwarded_for" '
                'rt=$request_time uct="$upstream_connect_time" '
                'uht="$upstream_header_time" urt="$upstream_response_time"';

access_log /var/log/nginx/access.log main;
```

**Метрики:**
- `rt` - request time (повний час запиту)
- `uct` - upstream connect time (час підключення до backend)
- `uht` - upstream header time (час отримання headers)
- `urt` - upstream response time (час відповіді backend)

### JSON Logging (опціонально)

```nginx
log_format json_combined escape=json
'{'
    '"time_local":"$time_local",'
    '"remote_addr":"$remote_addr",'
    '"request":"$request",'
    '"status": "$status",'
    '"body_bytes_sent":"$body_bytes_sent",'
    '"request_time":"$request_time"'
'}';
```

Використовується для централізованого логування (ELK stack, Loki, etc.).

## Моніторинг

### Health Check

```bash
# HTTP health check
curl http://localhost/health

# HTTPS health check
curl https://crm.example.com/health

# Очікувана відповідь: "healthy"
```

### Nginx Status

```nginx
location /nginx_status {
    stub_status on;
    access_log off;
    allow 127.0.0.1;
    allow 172.16.0.0/12; # Docker networks
    deny all;
}
```

```bash
# Перевірка статусу
curl http://localhost/nginx_status

# Output:
# Active connections: 2
# server accepts handled requests
#  10 10 15
# Reading: 0 Writing: 1 Waiting: 1
```

### SSL Certificate Info

```bash
# Перевірка сертифікату
openssl s_client -connect crm.example.com:443 -servername crm.example.com < /dev/null 2>/dev/null | openssl x509 -text -noout

# Перевірка терміну дії
openssl s_client -connect crm.example.com:443 -servername crm.example.com < /dev/null 2>/dev/null | openssl x509 -enddate -noout
```

## Troubleshooting

### Проблема: 502 Bad Gateway

**Причини:**
- Backend (API/Frontend) не запущені
- Неправильні upstream адреси
- Проблеми з мережею Docker

**Перевірка:**
```bash
# Перевірка що backend працюють
docker compose ps

# Перевірка логів Nginx
docker compose logs nginx

# Перевірка логів API
docker compose logs api

# Тест підключення до backend з Nginx контейнера
docker compose exec nginx wget -O- http://api:8000/healthz
```

### Проблема: SSL handshake failed

**Причини:**
- Сертифікати не знайдені або невалідні
- Неправильні права доступу до приватного ключа
- Застаріла версія SSL/TLS

**Перевірка:**
```bash
# Перевірка що сертифікати існують
ls -la nginx/ssl/

# Перевірка сертифікату
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Перевірка приватного ключа
openssl rsa -in nginx/ssl/key.pem -check

# Логи Nginx
docker compose logs nginx | grep -i ssl
```

### Проблема: Too Many Requests (429)

**Причина:** Rate limiting спрацював

**Рішення:**
- Зменшити частоту запитів
- Налаштувати burst параметр
- Виключити rate limiting для певних IP (allow list)

```nginx
# Збільшити burst
location /api/ {
    limit_req zone=api_limit burst=50 nodelay; # було 20
}

# Або виключити для певних IP
geo $limit {
    default 1;
    10.0.0.0/8 0;  # Internal network
    192.168.0.0/16 0;
}

map $limit $limit_key {
    0 "";
    1 $binary_remote_addr;
}

limit_req_zone $limit_key zone=api_limit:10m rate=10r/s;
```

### Проблема: Let's Encrypt challenge failed

**Причини:**
- Домен не вказує на сервер
- Порт 80 недоступний
- Firewall блокує HTTP

**Перевірка:**
```bash
# Перевірка DNS
nslookup crm.example.com

# Перевірка доступності порту 80 ззовні
curl -I http://crm.example.com/.well-known/acme-challenge/test

# Перевірка firewall
sudo ufw status
```

## Best Practices

### 1. Безпека

- ✅ Використовуйте HTTPS в production
- ✅ Приховуйте версію Nginx (`server_tokens off`)
- ✅ Налаштуйте security headers
- ✅ Використовуйте rate limiting
- ✅ Регулярно оновлюйте сертифікати
- ✅ Обмежте доступ до sensitive endpoints

### 2. Продуктивність

- ✅ Увімкніть gzip compression
- ✅ Налаштуйте агресивне кешування для static files
- ✅ Використовуйте keepalive з'єднання
- ✅ Налаштуйте proxy buffering
- ✅ Моніторте метрики (request_time, upstream_time)

### 3. Доступність

- ✅ Налаштуйте health checks
- ✅ Використовуйте upstream з кількома серверами (optional)
- ✅ Налаштуйте auto-restart (`restart: unless-stopped`)
- ✅ Логуйте все важливе

### 4. Моніторинг

- ✅ Використовуйте structured logging
- ✅ Налаштуйте alerting на помилки 5xx
- ✅ Моніторте SSL certificate expiration
- ✅ Відстежуйте rate limiting events

## Корисні команди

```bash
# Перезавантаження конфігурації без downtime
docker compose exec nginx nginx -s reload

# Перевірка синтаксису конфігу
docker compose exec nginx nginx -t

# Перегляд логів в реальному часі
docker compose logs -f nginx

# Перегляд access log
docker compose exec nginx tail -f /var/log/nginx/access.log

# Перегляд error log
docker compose exec nginx tail -f /var/log/nginx/error.log

# Статистика помилок
docker compose exec nginx grep "error" /var/log/nginx/error.log | tail -20

# Top endpoints by request count
docker compose exec nginx awk '{print $7}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20
```

## Додаткові ресурси

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Nginx Rate Limiting](https://www.nginx.com/blog/rate-limiting-nginx/)
- [Security Headers](https://securityheaders.com/)

## Підтримка

При виникненні проблем:
1. Перевірте логи: `docker compose logs nginx`
2. Перевірте конфігурацію: `docker compose exec nginx nginx -t`
3. Перевірте статус backend: `docker compose ps`
4. Зверніться до Troubleshooting розділу вище
