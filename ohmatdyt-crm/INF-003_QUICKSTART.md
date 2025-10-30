# INF-003: Quick Start Guide

## Налаштування Nginx Production з HTTPS

### Передумови

- Docker та Docker Compose встановлені
- OpenSSL встановлено (для self-signed certificates)
- Bash shell доступний (для Let's Encrypt)

### Режими роботи

INF-003 підтримує три режими роботи:

1. **Development (HTTP)** - без HTTPS, для локальної розробки
2. **Production Testing (Self-Signed)** - HTTPS з самопідписаними сертифікатами
3. **Production (Let's Encrypt)** - HTTPS з валідними сертифікатами

---

## Швидкий старт

### 1. Development Mode (HTTP Only)

**Найпростіший варіант для локальної розробки:**

```powershell
# Запуск
.\setup-nginx-prod.ps1 -Mode dev

# Або напряму через docker compose
docker compose up -d nginx
```

**Доступ:**
- Frontend: http://localhost
- API: http://localhost/api/
- Health: http://localhost/health

---

### 2. Production Testing (Self-Signed HTTPS)

**Для тестування HTTPS локально:**

```powershell
# Автоматичний setup з генерацією сертифікатів
.\setup-nginx-prod.ps1 -Mode self-signed -Domain localhost

# Або вручну:

# Крок 1: Генерація сертифікатів
cd ohmatdyt-crm\nginx
bash generate-ssl-certs.sh

# Крок 2: Запуск Nginx
cd ..\..
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d nginx

# Крок 3: Тестування
.\test_inf003.ps1
```

**Доступ:**
- Frontend: https://localhost (⚠️ Certificate Warning)
- API: https://localhost/api/
- Health: https://localhost/health

**Примітка:** Браузер покаже попередження про небезпечний сертифікат. Це нормально для self-signed certificates. Натисніть "Advanced" → "Proceed to localhost".

---

### 3. Production (Let's Encrypt)

**Для production серверів з публічним доменом:**

#### Передумови:
- ✅ Публічний домен (наприклад, `crm.example.com`)
- ✅ DNS A-record вказує на IP сервера
- ✅ Порти 80 та 443 відкриті в firewall
- ✅ Сервер доступний з інтернету

#### Setup:

```powershell
# Автоматичний setup
.\setup-nginx-prod.ps1 -Mode letsencrypt -Domain crm.example.com -Email admin@example.com

# Або вручну:

# Крок 1: Налаштуйте домен в .env.prod
# NGINX_SERVER_NAME=crm.example.com

# Крок 2: Запустіть Let's Encrypt setup
cd ohmatdyt-crm\nginx
bash setup-letsencrypt.sh
# Введіть домен та email

# Крок 3: Запустіть Nginx
cd ..\..
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d nginx

# Крок 4 (опціонально): Активуйте auto-renewal
docker compose --profile letsencrypt up -d certbot
```

**Доступ:**
- Frontend: https://crm.example.com
- API: https://crm.example.com/api/
- Health: https://crm.example.com/health

**Auto-renewal:**
Certbot автоматично оновлюватиме сертифікати кожні 12 годин.

---

## Перевірка конфігурації

### Тестування

```powershell
# Запустіть повний test suite
.\test_inf003.ps1

# Очікуваний результат: 10/10 тестів пройдено
```

### Ручна перевірка

```powershell
# Перевірка що Nginx запущено
docker compose ps nginx

# Перевірка логів
docker compose logs nginx

# Перевірка health endpoint
curl http://localhost/health
# або
curl -k https://localhost/health

# Перевірка API
curl -k https://localhost/api/healthz

# Перевірка синтаксису конфігу
docker compose exec nginx nginx -t

# Reload конфігурації без downtime
docker compose exec nginx nginx -s reload
```

### Перевірка SSL сертифікатів

```powershell
# Перегляд деталей сертифікату
openssl x509 -in ohmatdyt-crm/nginx/ssl/cert.pem -text -noout

# Перевірка терміну дії
openssl x509 -in ohmatdyt-crm/nginx/ssl/cert.pem -enddate -noout

# Перевірка через браузер
# Відкрийте https://localhost і натисніть на іконку замка → Certificate
```

---

## Troubleshooting

### Проблема: 502 Bad Gateway

**Причина:** Backend (API/Frontend) не запущені

**Рішення:**
```powershell
# Перевірте статус всіх сервісів
docker compose ps

# Запустіть backend якщо потрібно
docker compose up -d api frontend

# Перевірте логи
docker compose logs api
docker compose logs frontend
```

---

### Проблема: SSL Certificate Warning (Self-Signed)

**Причина:** Браузер не довіряє самопідписаним сертифікатам

**Рішення:**
1. У Chrome/Edge: натисніть "Advanced" → "Proceed to localhost (unsafe)"
2. У Firefox: "Advanced" → "Accept the Risk and Continue"
3. Або використовуйте `curl -k` для bypass SSL verification

**Для production:** використовуйте Let's Encrypt, а не self-signed certificates.

---

### Проблема: Let's Encrypt Challenge Failed

**Можливі причини:**
- DNS не вказує на сервер
- Порт 80 недоступний з інтернету
- Firewall блокує трафік

**Рішення:**
```powershell
# Перевірте DNS
nslookup crm.example.com

# Перевірте доступність з інтернету
curl http://crm.example.com/.well-known/acme-challenge/test

# Перевірте firewall
# Windows: перевірте Windows Defender Firewall
# Linux: sudo ufw status

# Перегляньте логи Certbot
docker compose logs certbot
```

---

### Проблема: 429 Too Many Requests

**Причина:** Rate limiting спрацював

**Рішення:**
- Зменшіть частоту запитів
- Для тестування можете тимчасово збільшити burst в `nginx.prod.conf`:

```nginx
location /api/ {
    limit_req zone=api_limit burst=50 nodelay; # було 20
}
```

Після зміни:
```powershell
docker compose exec nginx nginx -s reload
```

---

## Корисні команди

### Управління Nginx

```powershell
# Запуск
docker compose up -d nginx

# Зупинка
docker compose stop nginx

# Рестарт
docker compose restart nginx

# Reload конфігурації (без downtime)
docker compose exec nginx nginx -s reload

# Перегляд логів
docker compose logs -f nginx

# Перевірка синтаксису
docker compose exec nginx nginx -t
```

### Управління сертифікатами

```powershell
# Ручне оновлення Let's Encrypt
docker compose run --rm certbot renew
docker compose exec nginx nginx -s reload

# Перегляд всіх сертифікатів
docker compose run --rm certbot certificates

# Видалення сертифікату
docker compose run --rm certbot delete --cert-name crm.example.com
```

### Моніторинг

```powershell
# Access log (останні 100 рядків)
docker compose exec nginx tail -100 /var/log/nginx/access.log

# Error log
docker compose exec nginx tail -100 /var/log/nginx/error.log

# Real-time логи
docker compose exec nginx tail -f /var/log/nginx/access.log

# Nginx статистика
curl http://127.0.0.1/nginx_status
```

---

## Структура файлів

```
ohmatdyt-crm/
├── nginx/
│   ├── nginx.conf                    # Dev config (HTTP)
│   ├── nginx.prod.conf              # Production config (HTTPS)
│   ├── ssl/                         # SSL certificates
│   │   ├── cert.pem                # Certificate
│   │   └── key.pem                 # Private key
│   ├── generate-ssl-certs.sh       # Generate self-signed
│   ├── setup-letsencrypt.sh        # Setup Let's Encrypt
│   └── README.md                   # Detailed documentation
├── certbot/                         # Let's Encrypt data
│   ├── conf/                       # Certificates
│   └── www/                        # ACME challenge
├── docker-compose.yml              # Dev compose
├── docker-compose.prod.yml         # Production compose
├── setup-nginx-prod.ps1            # Quick setup script
└── test_inf003.ps1                 # Test suite
```

---

## Конфігурація

### Environment Variables (.env.prod)

```env
# Nginx Configuration
NGINX_SERVER_NAME=crm.example.com    # Ваш домен
NGINX_PORT=80                         # HTTP port (опціонально)
```

### Основні налаштування (nginx.prod.conf)

**Performance:**
- Worker connections: 2048
- Keepalive: 65s, 100 requests
- Gzip: level 6

**Security:**
- Rate limiting: API 10r/s, Login 5r/m
- HSTS: 1 year
- Security headers enabled

**Caching:**
- Static files: 1 year
- Media files: 30 days

**Timeouts:**
- Client: 60s
- Upstream: 60s

---

## Best Practices

### Для Development:
✅ Використовуйте dev mode (HTTP)
✅ Не генеруйте зайві SSL сертифікати

### Для Staging/Testing:
✅ Використовуйте self-signed certificates
✅ Тестуйте повну конфігурацію перед production
✅ Запускайте test suite регулярно

### Для Production:
✅ Завжди використовуйте Let's Encrypt
✅ Активуйте certbot для auto-renewal
✅ Налаштуйте firewall правильно
✅ Моніторте expiration сертифікатів
✅ Регулярно перевіряйте логи
✅ Налаштуйте alerting на помилки

---

## Додаткові ресурси

- [Детальна документація](ohmatdyt-crm/nginx/README.md)
- [Implementation Summary](ohmatdyt-crm/INF-003_IMPLEMENTATION_SUMMARY.md)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Mozilla SSL Config Generator](https://ssl-config.mozilla.org/)

---

## Підтримка

При виникненні проблем:

1. Перевірте логи: `docker compose logs nginx`
2. Перевірте конфігурацію: `docker compose exec nginx nginx -t`
3. Запустіть тести: `.\test_inf003.ps1`
4. Перегляньте [Troubleshooting](#troubleshooting) секцію
5. Перегляньте детальну документацію в `nginx/README.md`

---

**Status:** ✅ Production Ready  
**Version:** 1.0.0  
**Last Updated:** October 30, 2025
