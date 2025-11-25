# ⚡ ШВИДКІ КОМАНДИ ДЛЯ РОЗГОРТАННЯ

## 🚀 АВТОМАТИЧНЕ РОЗГОРТАННЯ

### З Windows (PowerShell):
```powershell
cd f:\ohmatdyt_crm
.\deploy-crm-ohmatdyt.ps1
```

### Або через меню:
```batch
deploy-menu.bat
```

---

## 📦 РУЧНЕ РОЗГОРТАННЯ НА СЕРВЕРІ

### 1. Підключення:
```bash
ssh root@crm.ohmatdyt.com.ua
```

### 2. Перехід в проект:
```bash
cd ~/ohmatdyt-crm
```

### 3. Створення volumes:
```bash
docker volume create ohmatdyt_crm_db-data
docker volume create ohmatdyt_crm_media
docker volume create ohmatdyt_crm_static
```

### 4. Налаштування SSL:
```bash
cd ~/ohmatdyt-crm/nginx
bash setup-letsencrypt.sh
# Ввести: crm.ohmatdyt.com.ua
# Ввести: ваш email
cd ..
```

### 5. Збірка та запуск:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
sleep 30
docker compose ps
```

### 6. Міграції:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec api alembic upgrade head
```

### 7. Створення адміністратора:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec api python -c "
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role

db = SessionLocal()
admin_role = db.query(Role).filter(Role.name == 'admin').first()
if not admin_role:
    admin_role = Role(name='admin', description='Administrator')
    db.add(admin_role)
    db.commit()
    db.refresh(admin_role)

admin = User(
    email='admin@ohmatdyt.com',
    username='admin',
    full_name='Administrator',
    hashed_password=get_password_hash('admin123'),
    is_active=True,
    role_id=admin_role.id
)
db.add(admin)
db.commit()
print('✅ Адміністратор створений')
db.close()
"
```

---

## 🔍 ПЕРЕВІРКА ПРАЦЕЗДАТНОСТІ

```bash
# Статус контейнерів
docker compose ps

# Перевірка frontend
curl https://crm.ohmatdyt.com.ua/health

# Перевірка API
curl https://crm.ohmatdyt.com.ua/api/healthz

# Логи
docker compose logs -f
```

---

## 📤 ЗАВАНТАЖЕННЯ .env.prod НА СЕРВЕР

### З Windows:
```powershell
scp f:\ohmatdyt_crm\ohmatdyt-crm\.env.prod root@crm.ohmatdyt.com.ua:~/ohmatdyt-crm/.env.prod
```

### Або створити вручну на сервері:
```bash
ssh root@crm.ohmatdyt.com.ua
cd ~/ohmatdyt-crm
nano .env.prod
# Вставити вміст з локального файлу
# Ctrl+X, Y, Enter для збереження
```

---

## 🔐 ГЕНЕРАЦІЯ СЕКРЕТІВ

### JWT Secret:
```bash
openssl rand -hex 32
```

### Або з Python:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Або з PowerShell:
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | % {[char]$_})
```

---

## 🛠️ КОРИСНІ КОМАНДИ

### Моніторинг:
```bash
# Статус всіх контейнерів
docker compose ps

# Логи всіх сервісів
docker compose logs -f

# Логи конкретного сервісу
docker compose logs -f api
docker compose logs -f nginx
docker compose logs -f db

# Використання ресурсів
docker stats

# Перевірка дискового простору
df -h
```

### Управління:
```bash
# Перезапуск всіх сервісів
docker compose restart

# Перезапуск конкретного сервісу
docker compose restart api
docker compose restart nginx

# Зупинка всіх сервісів
docker compose down

# Запуск всіх сервісів
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Перезбірка конкретного сервісу
docker compose build --no-cache api
docker compose up -d api
```

### База даних:
```bash
# Підключення до PostgreSQL
docker compose exec db psql -U ohm_user -d ohm_db

# Список таблиць
docker compose exec db psql -U ohm_user -d ohm_db -c "\dt"

# Розмір бази даних
docker compose exec db psql -U ohm_user -d ohm_db -c "SELECT pg_size_pretty(pg_database_size('ohm_db'));"

# Backup
docker compose exec db pg_dump -U ohm_user ohm_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
docker compose exec -T db psql -U ohm_user ohm_db < backup.sql
```

### Nginx:
```bash
# Перевірка конфігу
docker compose exec nginx nginx -t

# Reload без downtime
docker compose exec nginx nginx -s reload

# Перегляд конфігурації
docker compose exec nginx cat /etc/nginx/conf.d/default.conf
```

### SSL/Certbot:
```bash
# Оновити сертифікати вручну
docker compose run --rm certbot renew

# Перевірити сертифікати
docker compose run --rm certbot certificates

# Список сертифікатів
ls -la ~/ohmatdyt-crm/nginx/certbot/conf/live/
```

---

## 🔄 ОНОВЛЕННЯ ПРОЕКТУ

### Швидке оновлення:
```bash
cd ~/ohmatdyt-crm
git pull origin main
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker compose exec api alembic upgrade head
```

### Оновлення з backup:
```bash
# 1. Backup бази даних
docker compose exec db pg_dump -U ohm_user ohm_db > backup_before_update.sql

# 2. Оновлення коду
git pull origin main

# 3. Rebuild
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# 4. Restart
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 5. Міграції
docker compose exec api alembic upgrade head

# 6. Перевірка
docker compose ps
docker compose logs -f
```

---

## 🧹 ОЧИЩЕННЯ

### Видалити невикористовувані образи:
```bash
docker system prune -a
```

### Видалити volumes (ОБЕРЕЖНО!):
```bash
docker volume ls
docker volume rm ohmatdyt_crm_media
```

### Повне очищення Docker:
```bash
docker compose down
docker system prune -a --volumes
```

---

## 📊 TROUBLESHOOTING

### Контейнер не запускається:
```bash
# Перевірити логи
docker compose logs [service_name]

# Перезібрати без кешу
docker compose build --no-cache [service_name]

# Видалити контейнер і створити заново
docker compose rm -f [service_name]
docker compose up -d [service_name]
```

### API не відповідає:
```bash
# Перевірити що API запущено
docker compose ps api

# Логи API
docker compose logs -f api

# Перевірити всередині контейнера
docker compose exec api curl http://localhost:8000/healthz

# Перевірити змінні середовища
docker compose exec api env | grep -E 'POSTGRES|DATABASE'
```

### SSL не працює:
```bash
# Перевірити DNS
nslookup crm.ohmatdyt.com.ua

# Перевірити відкриті порти
sudo netstat -tulpn | grep -E ':(80|443)'

# Перевірити firewall
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Перезапустити nginx
docker compose restart nginx

# Перевірити логи nginx
docker compose logs nginx
```

### База даних не працює:
```bash
# Статус
docker compose ps db

# Логи
docker compose logs db

# Перезапуск
docker compose restart db

# Перевірка з'єднання
docker compose exec api python -c "from app.core.database import engine; engine.connect(); print('OK')"
```

---

## 🔗 URLS

- Frontend: https://crm.ohmatdyt.com.ua
- API: https://crm.ohmatdyt.com.ua/api/
- API Docs: https://crm.ohmatdyt.com.ua/api/docs
- Health: https://crm.ohmatdyt.com.ua/health

## 🔑 ТИМЧАСОВІ CREDENTIALS

- Email: admin@ohmatdyt.com
- Password: admin123
- ⚠️ Змінити після входу!

---

**Копіюйте та вставляйте команди за потребою! ⚡**
