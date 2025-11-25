# 🚀 Розгортання CRM на crm.ohmatdyt.com.ua

## Інформація про сервер
- **Домен**: `crm.ohmatdyt.com.ua`
- **Проект**: Ohmatdyt CRM
- **Тип розгортання**: Production

---

## ✅ Передумови (вже виконано)

- ✅ Docker встановлено
- ✅ Проект скопійовано з GitHub
- ✅ DNS налаштовано (crm.ohmatdyt.com.ua → IP сервера)

---

## 📋 Кроки розгортання

### Крок 1: Налаштування .env.prod файлу

Файл `.env.prod` вже створено з такими налаштуваннями:

**Основні параметри:**
- `APP_ENV=production`
- `NGINX_SERVER_NAME=crm.ohmatdyt.com.ua`
- `ALLOWED_HOSTS=crm.ohmatdyt.com.ua,localhost,127.0.0.1,nginx`
- `CORS_ORIGINS=https://crm.ohmatdyt.com.ua,http://localhost`

**База даних:**
- `POSTGRES_PASSWORD=OhmProd2024SecurePass!` ⚠️ (можна змінити на більш складний)

**JWT Secret:**
- `JWT_SECRET=OhmProd2024JWT_Secret_Key_Very_Long_And_Secure_String_12345`

**Email налаштування:**
- `SMTP_HOST=smtp.gmail.com`
- `SMTP_USER=noreply@ohmatdyt.com`
- `SMTP_PASSWORD=REPLACE_WITH_GMAIL_APP_PASSWORD` ⚠️ (потрібно замінити)

**CRM URL:**
- `CRM_URL=https://crm.ohmatdyt.com.ua`

---

### Крок 2: Скопіювати .env.prod на сервер

На вашому локальному комп'ютері виконайте:

```powershell
# Завантажити .env.prod на сервер
scp f:\ohmatdyt_crm\ohmatdyt-crm\.env.prod user@crm.ohmatdyt.com.ua:~/ohmatdyt-crm/.env.prod
```

Або підключіться до сервера і створіть файл вручну:

```bash
ssh user@crm.ohmatdyt.com.ua
cd ~/ohmatdyt-crm
nano .env.prod
```

---

### Крок 3: Оновити параметри безпеки (ВАЖЛИВО!)

Підключіться до сервера:

```bash
ssh user@crm.ohmatdyt.com.ua
cd ~/ohmatdyt-crm
```

Відредагуйте `.env.prod` і змініть:

1. **SMTP Password** - якщо використовуєте Gmail:
   ```
   SMTP_PASSWORD=your_gmail_app_password
   ```
   
2. **Database Password** (опціонально):
   ```
   POSTGRES_PASSWORD=YourStrongPasswordHere123!
   DATABASE_URL=postgresql+psycopg://ohm_user:YourStrongPasswordHere123!@db:5432/ohm_db
   ```

3. **JWT Secret** (опціонально):
   ```bash
   # Генерувати новий JWT secret:
   openssl rand -hex 32
   # Або
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

---

### Крок 4: Створити Docker volumes

```bash
cd ~/ohmatdyt-crm

docker volume create ohmatdyt_crm_db-data
docker volume create ohmatdyt_crm_media
docker volume create ohmatdyt_crm_static
```

---

### Крок 5: Налаштувати Nginx для HTTPS (Let's Encrypt)

Перевірте, що порти 80 та 443 відкриті:

```bash
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

Запустіть setup Let's Encrypt:

```bash
cd ~/ohmatdyt-crm/nginx
bash setup-letsencrypt.sh
```

Введіть:
- **Домен**: `crm.ohmatdyt.com.ua`
- **Email**: ваш email для повідомлень від Let's Encrypt

---

### Крок 6: Зібрати Docker образи

```bash
cd ~/ohmatdyt-crm

# Збірка може зайняти 10-15 хвилин
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
```

---

### Крок 7: Запустити сервіси

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Почекати поки сервіси запустяться
sleep 30

# Перевірити статус
docker compose ps
```

Очікуваний результат - всі контейнери в статусі `running`:
- `db` (PostgreSQL)
- `redis`
- `api` (FastAPI)
- `frontend` (Next.js)
- `worker` (Celery Worker)
- `beat` (Celery Beat)
- `nginx`

---

### Крок 8: Виконати міграції бази даних

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec api alembic upgrade head
```

---

### Крок 9: Створити суперюзера (адміністратора)

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec api python -c "
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role

db = SessionLocal()

# Створити роль адміністратора якщо не існує
admin_role = db.query(Role).filter(Role.name == 'admin').first()
if not admin_role:
    admin_role = Role(name='admin', description='Administrator')
    db.add(admin_role)
    db.commit()
    db.refresh(admin_role)

# Створити адміністратора
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
print('✅ Адміністратор створений: admin@ohmatdyt.com / admin123')
db.close()
"
```

⚠️ **ВАЖЛИВО**: Після входу змініть пароль адміністратора!

---

### Крок 10: Перевірка роботи

```bash
# Перевірка health endpoint
curl https://crm.ohmatdyt.com.ua/health

# Перевірка API
curl https://crm.ohmatdyt.com.ua/api/healthz

# Перегляд логів
docker compose logs -f --tail=50
```

---

## 🌐 Доступ до системи

Після успішного розгортання:

- **Frontend**: https://crm.ohmatdyt.com.ua
- **API**: https://crm.ohmatdyt.com.ua/api/
- **API Docs**: https://crm.ohmatdyt.com.ua/api/docs
- **Health**: https://crm.ohmatdyt.com.ua/health

**Credentials (тимчасові):**
- Email: `admin@ohmatdyt.com`
- Password: `admin123`

---

## 🔄 Оновлення проекту

Для оновлення проекту в майбутньому:

```bash
cd ~/ohmatdyt-crm

# Отримати останні зміни
git pull origin main

# Перезібрати образи
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Перезапустити сервіси
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Виконати міграції
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec api alembic upgrade head
```

---

## 🛠️ Корисні команди

### Моніторинг

```bash
# Статус контейнерів
docker compose ps

# Логи всіх сервісів
docker compose logs -f

# Логи конкретного сервісу
docker compose logs -f api
docker compose logs -f nginx
docker compose logs -f frontend

# Використання ресурсів
docker stats
```

### Управління

```bash
# Зупинити всі сервіси
docker compose -f docker-compose.yml -f docker-compose.prod.yml down

# Запустити всі сервіси
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Перезапустити конкретний сервіс
docker compose restart api
docker compose restart nginx

# Виконати команду в контейнері
docker compose exec api bash
docker compose exec db psql -U ohm_user -d ohm_db
```

### Backup

```bash
# Backup бази даних
docker compose exec db pg_dump -U ohm_user ohm_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup медіафайлів
docker run --rm -v ohmatdyt_crm_media:/data -v $(pwd):/backup alpine tar czf /backup/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

---

## 🐛 Troubleshooting

### Проблема: Контейнер не запускається

```bash
# Перевірити логи
docker compose logs [service_name]

# Перевірити конфігурацію
docker compose config

# Перезібрати без кешу
docker compose build --no-cache [service_name]
```

### Проблема: SSL сертифікат не створився

```bash
# Перевірити логи nginx
docker compose logs nginx

# Перевірити DNS
nslookup crm.ohmatdyt.com.ua

# Перевірити доступність портів
sudo netstat -tulpn | grep -E ':(80|443)'
```

### Проблема: API не відповідає

```bash
# Перевірити що API запущено
docker compose ps api

# Перевірити логи API
docker compose logs -f api

# Перевірити health endpoint всередині контейнера
docker compose exec api curl http://localhost:8000/healthz
```

---

## 📞 Підтримка

Якщо виникли проблеми:

1. Перевірте логи: `docker compose logs -f`
2. Перевірте статус: `docker compose ps`
3. Перегляньте документацію в `TECHNICAL_DOCUMENTATION.md`
4. Перегляньте troubleshooting гайди в папці `docs/`

---

## ✅ Checklist розгортання

- [ ] Docker встановлено
- [ ] Проект скопійовано з GitHub
- [ ] `.env.prod` створено та налаштовано
- [ ] Паролі та секрети оновлено
- [ ] Docker volumes створено
- [ ] Let's Encrypt налаштовано
- [ ] Docker образи зібрано
- [ ] Сервіси запущено
- [ ] Міграції виконано
- [ ] Адміністратор створений
- [ ] Доступ до https://crm.ohmatdyt.com.ua працює
- [ ] API відповідає
- [ ] Пароль адміністратора змінено

---

**Успішного розгортання! 🚀**
