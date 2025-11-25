# 🚀 Швидкий старт розгортання на crm.ohmatdyt.com.ua

## ✅ Що вже зроблено:

1. ✅ Docker встановлено на сервері
2. ✅ Проект скопійовано з GitHub
3. ✅ Файл `.env.prod` створено з налаштуваннями для production
4. ✅ Deployment скрипти готові

## 🎯 Наступні кроки:

### Варіант 1: Автоматичний deployment з Windows (РЕКОМЕНДОВАНО)

Просто запустіть PowerShell скрипт:

```powershell
# З вашого Windows комп'ютера
cd f:\ohmatdyt_crm

# Запустити повний автоматичний deployment
.\deploy-crm-ohmatdyt.ps1

# Або з параметрами:
.\deploy-crm-ohmatdyt.ps1 -ServerUser root -ServerHost crm.ohmatdyt.com.ua
```

**Що зробить скрипт:**
1. Перевірить підключення до сервера
2. Завантажить `.env.prod` на сервер
3. Створить Docker volumes
4. Зберє Docker образи
5. Запустить всі сервіси
6. Виконає міграції бази даних
7. Створить адміністратора
8. Перевірить працездатність

---

### Варіант 2: Ручне розгортання на сервері

#### Крок 1: Підключитися до сервера

```bash
ssh root@crm.ohmatdyt.com.ua
# або
ssh user@crm.ohmatdyt.com.ua
```

#### Крок 2: Перейти в папку проекту

```bash
cd ~/ohmatdyt-crm
```

#### Крок 3: Завантажити .env.prod (якщо ще не зроблено)

З вашого Windows:
```powershell
scp f:\ohmatdyt_crm\ohmatdyt-crm\.env.prod root@crm.ohmatdyt.com.ua:~/ohmatdyt-crm/.env.prod
```

Або створити вручну на сервері:
```bash
nano .env.prod
# Скопіювати вміст з f:\ohmatdyt_crm\ohmatdyt-crm\.env.prod
```

#### Крок 4: ВАЖЛИВО! Оновити паролі

```bash
nano .env.prod
```

Змініть:
- `POSTGRES_PASSWORD` - пароль бази даних
- `JWT_SECRET` - секретний ключ для JWT
- `SMTP_PASSWORD` - пароль для email (якщо використовуєте)

#### Крок 5: Запустити deployment скрипт

```bash
# Завантажити скрипт (якщо потрібно)
# Або він вже є в проекті

chmod +x deploy-crm-ohmatdyt.sh
./deploy-crm-ohmatdyt.sh
```

---

### Варіант 3: Покрокове ручне розгортання

```bash
# 1. Створити volumes
docker volume create ohmatdyt_crm_db-data
docker volume create ohmatdyt_crm_media
docker volume create ohmatdyt_crm_static

# 2. Налаштувати SSL (якщо потрібно)
cd ~/ohmatdyt-crm/nginx
bash setup-letsencrypt.sh
# Введіть: crm.ohmatdyt.com.ua та ваш email
cd ..

# 3. Зібрати образи (10-15 хвилин)
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# 4. Запустити сервіси
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 5. Почекати запуску
sleep 30

# 6. Перевірити статус
docker compose ps

# 7. Виконати міграції
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec api alembic upgrade head

# 8. Створити адміністратора
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
print('Адміністратор створений')
db.close()
"

# 9. Перевірити
curl https://crm.ohmatdyt.com.ua/health
curl https://crm.ohmatdyt.com.ua/api/healthz
```

---

## 🌐 Доступ після розгортання

- **Frontend**: https://crm.ohmatdyt.com.ua
- **API**: https://crm.ohmatdyt.com.ua/api/
- **API Docs**: https://crm.ohmatdyt.com.ua/api/docs
- **Health**: https://crm.ohmatdyt.com.ua/health

**Логін (тимчасовий):**
- Email: `admin@ohmatdyt.com`
- Password: `admin123`

⚠️ **ВАЖЛИВО**: Змініть пароль одразу після входу!

---

## 📋 Перевірка роботи

```bash
# Статус контейнерів
docker compose ps

# Логи
docker compose logs -f

# Логи конкретного сервісу
docker compose logs -f api
docker compose logs -f nginx

# Перевірка endpoint'ів
curl https://crm.ohmatdyt.com.ua/health
curl https://crm.ohmatdyt.com.ua/api/healthz
```

---

## 🔄 Оновлення в майбутньому

```bash
cd ~/ohmatdyt-crm
git pull origin main
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec api alembic upgrade head
```

---

## 🐛 Troubleshooting

### Контейнер не запускається
```bash
docker compose logs [service_name]
docker compose restart [service_name]
```

### SSL не працює
```bash
# Перевірити DNS
nslookup crm.ohmatdyt.com.ua

# Перевірити порти
sudo netstat -tulpn | grep -E ':(80|443)'

# Перевірити логи nginx
docker compose logs nginx
```

### API не відповідає
```bash
# Перевірити що API запущено
docker compose ps api

# Логи API
docker compose logs -f api

# Перевірити всередині контейнера
docker compose exec api curl http://localhost:8000/healthz
```

---

## 📚 Детальна документація

Дивіться: `DEPLOYMENT_CRM_OHMATDYT_COM_UA.md`

---

**Готово! Виберіть варіант розгортання та починайте! 🚀**
