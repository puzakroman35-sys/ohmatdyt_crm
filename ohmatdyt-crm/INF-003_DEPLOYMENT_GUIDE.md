# INF-003 Deployment Guide
# Інструкція з розгортання Nginx HTTPS конфігурації на production

## Огляд

**Задача:** INF-003 - Nginx prod-конфіг + HTTPS (Let's Encrypt)  
**Статус:** Готово до розгортання  
## Налаштування

**Production сервер:** rpuzak@192.168.31.249  
**Директорія:** /home/rpuzak/ohmatdyt-crm/  

## Файли для розгортання

### Створені/Модифіковані файли (14):

1. **nginx/nginx.prod.conf** (350+ рядків)
   - Production конфігурація Nginx
   - HTTPS підтримка (порти 80/443)
   - HTTP → HTTPS redirect
   - Rate limiting (API: 10 req/s, Login: 5 req/min)
   - Security headers (HSTS, CSP, X-Frame-Options)
   - Gzip compression
   - Static/Media caching (30 днів)
   - WebSocket підтримка

2. **nginx/generate-ssl-certs.sh** (80 рядків)
   - Генерація self-signed SSL сертифікатів
   - RSA 2048-bit ключі
   - SAN підтримка для декількох доменів
   - 365 днів валідності

3. **nginx/setup-letsencrypt.sh** (160 рядків)
   - Автоматична установка Let's Encrypt
   - ACME challenge для валідації домену
   - Auto-renewal через cron
   - Backup старих сертифікатів

4. **nginx/README.md** (600+ рядків)
   - Повна документація Nginx конфігурації
   - Інструкції по SSL setup
   - Troubleshooting guide
   - Performance tuning

5. **docker-compose.prod.yml** (оновлено)
   - Додано порти 80/443
   - SSL volume mounts
   - Certbot service для Let's Encrypt
   - Auto-renewal конфігурація

6. **Документація** (4 файли, 1700+ рядків):
   - INF-003_README.md - основна документація
   - INF-003_IMPLEMENTATION_SUMMARY.md - деталі імплементації
   - INF-003_QUICKSTART.md - швидкий старт
   - INF-003_FINAL_SUMMARY.md - фінальний звіт

7. **Тестування:**
   - test_inf003.ps1 - 10 автоматичних тестів
   - setup-nginx-prod.ps1 - PowerShell setup script

8. **Git файли:**
   - .gitignore - виключення SSL сертифікатів
   - PROJECT_STATUS.md - оновлено статус INF-003

## Процес розгортання

### Метод 1: Автоматичний (Рекомендовано)

Використовуйте PowerShell скрипт:

```powershell
.\deploy-inf003.ps1
```

Скрипт виконає:
1. Перевірку локальних файлів
2. Копіювання через scp (запитає пароль для кожного файлу)
3. Відображення наступних кроків

**Пароль SSH:** cgf34R

### Метод 2: Ручний

#### Крок 1: Копіювання файлів

```bash
# З локальної машини (Windows PowerShell)
scp ohmatdyt-crm/nginx/nginx.prod.conf rpuzak@192.168.31.249:/home/rpuzak/ohmatdyt-crm/nginx/
scp ohmatdyt-crm/nginx/generate-ssl-certs.sh rpuzak@192.168.31.249:/home/rpuzak/ohmatdyt-crm/nginx/
scp ohmatdyt-crm/nginx/setup-letsencrypt.sh rpuzak@192.168.31.249:/home/rpuzak/ohmatdyt-crm/nginx/
scp ohmatdyt-crm/nginx/README.md rpuzak@192.168.31.249:/home/rpuzak/ohmatdyt-crm/nginx/
scp ohmatdyt-crm/docker-compose.prod.yml rpuzak@192.168.31.249:/home/rpuzak/ohmatdyt-crm/
```

#### Крок 2: Генерація SSL сертифікатів

```bash
# SSH на сервер
ssh rpuzak@192.168.31.249

# Перейти в nginx директорію
cd /home/rpuzak/ohmatdyt-crm/nginx

# Встановити права виконання
chmod +x generate-ssl-certs.sh setup-letsencrypt.sh

# Згенерувати self-signed сертифікати (для тесту)
./generate-ssl-certs.sh

# Перевірка
ls -la ssl/
# Повинні з'явитися: cert.pem, key.pem
```

#### Крок 3: Перезапуск Nginx з HTTPS

```bash
# Повернутись в корінь проекту
cd /home/rpuzak/ohmatdyt-crm

# Зупинити Nginx
docker compose -f docker-compose.yml -f docker-compose.prod.yml down nginx

# Запустити з production конфігом
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d nginx

# Перевірити статус
docker compose ps
docker logs ohmatdyt-crm-nginx-1
```

#### Крок 4: Перевірка HTTPS

```bash
# З сервера або локально
curl -k https://192.168.31.249/
curl -I https://192.168.31.249/api/health/

# Перевірка редіректу HTTP → HTTPS
curl -I http://192.168.31.249/
# Повинен повернути 301 redirect на https://
```

#### Крок 5 (Опціонально): Let's Encrypt

Якщо є публічний домен:

```bash
cd /home/rpuzak/ohmatdyt-crm/nginx
./setup-letsencrypt.sh yourdomain.com

# Перезапуск з Let's Encrypt сертифікатами
cd /home/rpuzak/ohmatdyt-crm
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart nginx
```

## Тестування після розгортання

### 1. HTTPS доступність

```bash
curl -k https://192.168.31.249/
```

Очікуваний результат: HTML головної сторінки

### 2. API endpoint

```bash
curl -I https://192.168.31.249/api/health/
```

Очікуваний результат: HTTP 200 OK

### 3. HTTP → HTTPS redirect

```bash
curl -I http://192.168.31.249/
```

Очікуваний результат: HTTP 301 Moved Permanently → https://

### 4. Security headers

```bash
curl -I https://192.168.31.249/ | grep -E "(Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options)"
```

Очікуваний результат:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
```

### 5. Gzip compression

```bash
curl -I -H "Accept-Encoding: gzip" https://192.168.31.249/
```

Очікуваний результат: `Content-Encoding: gzip`

### 6. Static files caching

```bash
curl -I https://192.168.31.249/static/test.css
```

Очікуваний результат: `Cache-Control: public, max-age=2592000`

### 7. Rate limiting (API)

```bash
# Виконати 15 запитів підряд
for i in {1..15}; do curl -I https://192.168.31.249/api/health/; done
```

Очікуваний результат: Після 10 запитів - HTTP 429 Too Many Requests

### 8. Docker контейнери

```bash
docker compose ps | grep nginx
docker logs ohmatdyt-crm-nginx-1 --tail 50
```

Очікуваний результат: Nginx працює, порти 80/443 прослуховуються

### 9. SSL сертифікат

```bash
openssl s_client -connect 192.168.31.249:443 -showcerts
```

Очікуваний результат: Деталі SSL сертифікату

### 10. WebSocket підтримка

```bash
curl -I -H "Connection: Upgrade" -H "Upgrade: websocket" https://192.168.31.249/ws/
```

## Перевірка Definition of Done (DoD)

### ✅ Функціональні вимоги:

- [x] Nginx reverse proxy налаштовано для production
- [x] HTTPS підтримка (порти 80/443)
- [x] HTTP → HTTPS автоматичний redirect
- [x] SSL/TLS certificates:
  - [x] Self-signed для dev/testing
  - [x] Let's Encrypt інтеграція для production
- [x] Security headers (HSTS, CSP, X-Frame-Options, etc.)
- [x] Rate limiting:
  - [x] API endpoints: 10 req/s
  - [x] Login endpoints: 5 req/min
- [x] Gzip compression
- [x] Static/Media files caching (30 днів)
- [x] WebSocket підтримка

### ✅ Технічні вимоги:

- [x] Docker Compose production конфігурація
- [x] SSL certificates volume mount
- [x] Certbot автоматичне оновлення
- [x] Proper logging (access/error logs)
- [x] .gitignore оновлено (SSL сертифікати виключені)

### ✅ Документація:

- [x] nginx/README.md - повна документація
- [x] INF-003_README.md - технічний опис
- [x] INF-003_QUICKSTART.md - швидкий старт
- [x] INF-003_IMPLEMENTATION_SUMMARY.md - деталі
- [x] INF-003_DEPLOYMENT_GUIDE.md - інструкція розгортання (цей файл)

### ✅ Тестування:

- [x] test_inf003.ps1 - 10 автоматичних тестів:
  1. SSL certificates generation
  2. HTTPS endpoint accessibility
  3. HTTP to HTTPS redirect
  4. Security headers (HSTS, CSP, X-Frame-Options)
  5. Gzip compression
  6. Static files caching
  7. API rate limiting
  8. Login rate limiting
  9. Nginx configuration syntax
  10. Docker Compose validation

### ✅ Git & Version Control:

- [x] Всі зміни закомічені (commit: e3da037)
- [x] Push на GitHub: https://github.com/puzakroman35-sys/ohmatdyt_crm.git
- [x] Push на Adelina git: http://git.adelina.com.ua/rpuzak/ohmatdyt.git
- [x] PROJECT_STATUS.md оновлено

### ✅ Deployment:

- [x] deploy-inf003.ps1 - PowerShell deployment script
- [x] Перевірка локальних файлів
- [x] SCP копіювання на production
- [x] SSH інструкції для setup
- [x] Інструкції для Let's Encrypt

## Troubleshooting

### Проблема: Nginx не стартує

**Перевірка:**
```bash
docker logs ohmatdyt-crm-nginx-1
nginx -t -c /etc/nginx/nginx.conf
```

**Рішення:** Перевірити синтаксис конфігурації

### Проблема: SSL сертифікати не знайдено

**Перевірка:**
```bash
ls -la /home/rpuzak/ohmatdyt-crm/nginx/ssl/
```

**Рішення:** Запустити `./generate-ssl-certs.sh`

### Проблема: HTTPS не працює

**Перевірка:**
```bash
docker compose ps | grep nginx
netstat -tulpn | grep :443
```

**Рішення:** Перевірити що порт 443 прослуховується

### Проблема: Let's Encrypt validation fails

**Перевірка:**
```bash
docker logs ohmatdyt-crm-certbot-1
```

**Рішення:** 
- Перевірити DNS записи домену
- Переконатись що порт 80 доступний зовні
- Перевірити .well-known/acme-challenge доступність

## Статистика імплементації

- **Створено файлів:** 14
- **Всього рядків коду/документації:** 3533+
- **Nginx конфігурація:** 350+ рядків
- **Bash скрипти:** 240 рядків
- **Документація:** 1700+ рядків
- **Тести:** 250+ рядків
- **PowerShell скрипти:** 450+ рядків

## Git коміти

**Основний коміт:**
```
commit e3da037...
Author: Puzak Roman <puzakroman35@gmail.com>
Date:   ...

INF-003: Nginx prod-конфіг + HTTPS (Let's Encrypt)

- Nginx production конфігурація (nginx.prod.conf)
- SSL/TLS підтримка (TLS 1.2+, modern ciphers)
- Self-signed certificate generation (generate-ssl-certs.sh)
- Let's Encrypt integration (setup-letsencrypt.sh)
- Security features (HSTS, CSP, rate limiting, DDoS protection)
- Performance optimization (Gzip, caching, keep-alive)
- Docker Compose production overlay
- Повна документація (4 MD файли, 1700+ рядків)
- Автоматичне тестування (10 тестів)
- Deployment scripts (PowerShell)

14 files changed, 3533 insertions(+)
```

**Repositories:**
- GitHub: https://github.com/puzakroman35-sys/ohmatdyt_crm.git
- Adelina Git: http://git.adelina.com.ua/rpuzak/ohmatdyt.git

## Наступні кроки

1. **Після успішного розгортання:**
   - Моніторинг логів Nginx
   - Перевірка метрик performance
   - Тестування під навантаженням

2. **Let's Encrypt setup (якщо потрібно):**
   - Налаштувати публічний домен
   - Запустити setup-letsencrypt.sh
   - Налаштувати auto-renewal

3. **Optimization:**
   - Тюнінг rate limiting
   - Налаштування caching policies
   - SSL performance tuning

## Контакти & Підтримка

**Production сервер:**
- IP: 192.168.31.249
- User: rpuzak
- Password: cgf34R
- Directory: /home/rpuzak/ohmatdyt-crm/

**Документація:**
- Nginx README: ohmatdyt-crm/nginx/README.md
- INF-003 README: INF-003_README.md
- Quick Start: INF-003_QUICKSTART.md

**Git репозиторії:**
- GitHub: https://github.com/puzakroman35-sys/ohmatdyt_crm.git
- Adelina: http://git.adelina.com.ua/rpuzak/ohmatdyt.git

---

**Дата створення:** 2024  
**Автор:** AI Assistant  
**Статус:** ✅ Ready for Production Deployment  
**Версія:** 1.0.0
