# 🚀 РОЗГОРТАННЯ НА PRODUCTION СЕРВЕРІ crm.ohmatdyt.com.ua

## ✅ Статус підготовки: ГОТОВО

Всі необхідні файли створено та налаштовано для розгортання на production сервері.

---

## 📁 Створені файли:

### Конфігурація:
- ✅ `ohmatdyt-crm\.env.prod` - Production environment змінні

### Скрипти розгортання:
- ✅ `deploy-crm-ohmatdyt.ps1` - Автоматичний deployment з Windows
- ✅ `ohmatdyt-crm\deploy-crm-ohmatdyt.sh` - Deployment скрипт для сервера
- ✅ `deploy-menu.bat` - Інтерактивне меню для Windows

### Документація:
- ✅ `DEPLOYMENT_SUMMARY.md` - Короткий опис підготовки
- ✅ `DEPLOYMENT_CRM_OHMATDYT_COM_UA.md` - Детальна покрокова інструкція
- ✅ `QUICKSTART_CRM_OHMATDYT.md` - Швидкий старт (3 варіанти)
- ✅ `DEPLOYMENT_CHECKLIST.txt` - Контрольний список з 11 фаз
- ✅ `README_DEPLOYMENT.md` - Цей файл

---

## 🎯 ЯК ПОЧАТИ РОЗГОРТАННЯ?

### 🔥 Найшвидший спосіб:

```batch
REM Запустити інтерактивне меню
deploy-menu.bat
```

Або напряму:

```powershell
REM Автоматичне розгортання з Windows
.\deploy-crm-ohmatdyt.ps1
```

### 📖 Варіанти розгортання:

#### Варіант 1: Автоматично з Windows (5 хвилин)
```powershell
cd f:\ohmatdyt_crm
.\deploy-crm-ohmatdyt.ps1
```

**Що робить:**
- Підключається до сервера
- Завантажує конфігурацію
- Створює volumes
- Збирає образи
- Запускає сервіси
- Виконує міграції
- Створює адміністратора

#### Варіант 2: Вручну на сервері (10 хвилин)
```bash
# 1. Підключитися
ssh root@crm.ohmatdyt.com.ua

# 2. Перейти в проект
cd ~/ohmatdyt-crm

# 3. Запустити скрипт
chmod +x deploy-crm-ohmatdyt.sh
./deploy-crm-ohmatdyt.sh
```

#### Варіант 3: Покроково (15-20 хвилин)
Дивіться детальну інструкцію в `DEPLOYMENT_CRM_OHMATDYT_COM_UA.md`

---

## ⚠️ ВАЖЛИВО перед розгортанням!

### Оновити в `.env.prod`:

1. **Database Password** (рекомендовано):
   ```env
   POSTGRES_PASSWORD=ВашСкладнийПароль123!
   DATABASE_URL=postgresql+psycopg://ohm_user:ВашСкладнийПароль123!@db:5432/ohm_db
   ```

2. **JWT Secret** (рекомендовано):
   ```bash
   # Згенерувати новий:
   openssl rand -hex 32
   # Або:
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **SMTP Password** (якщо використовуєте email):
   ```env
   SMTP_PASSWORD=ВашGmailAppPassword
   ```

---

## 🌐 Що буде після розгортання:

**URLs:**
- Frontend: `https://crm.ohmatdyt.com.ua`
- API: `https://crm.ohmatdyt.com.ua/api/`
- API Docs: `https://crm.ohmatdyt.com.ua/api/docs`
- Health: `https://crm.ohmatdyt.com.ua/health`

**Тимчасові облікові дані:**
- Email: `admin@ohmatdyt.com`
- Password: `admin123`
- ⚠️ **Змініть одразу після входу!**

---

## 📚 Документація:

| Файл | Опис | Коли використовувати |
|------|------|---------------------|
| `QUICKSTART_CRM_OHMATDYT.md` | Швидкий старт | Хочу швидко почати |
| `DEPLOYMENT_CRM_OHMATDYT_COM_UA.md` | Повна інструкція | Потрібні деталі |
| `DEPLOYMENT_CHECKLIST.txt` | Контрольний список | Слідкувати за прогресом |
| `DEPLOYMENT_SUMMARY.md` | Резюме підготовки | Що вже зроблено |

---

## 🛠️ Корисні команди:

### На сервері:

```bash
# Статус
docker compose ps

# Логи
docker compose logs -f
docker compose logs -f api
docker compose logs -f nginx

# Перезапуск
docker compose restart api
docker compose restart nginx

# Оновлення
cd ~/ohmatdyt-crm
git pull origin main
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker compose exec api alembic upgrade head

# Backup бази даних
docker compose exec db pg_dump -U ohm_user ohm_db > backup_$(date +%Y%m%d).sql
```

### З Windows:

```powershell
# Підключитися до сервера
ssh root@crm.ohmatdyt.com.ua

# Скопіювати файл на сервер
scp file.txt root@crm.ohmatdyt.com.ua:~/

# Переглянути логи
ssh root@crm.ohmatdyt.com.ua "cd ~/ohmatdyt-crm && docker compose logs -f"
```

---

## 🐛 Troubleshooting:

### Проблема: Не можу підключитися до сервера
```powershell
# Перевірити підключення
ping crm.ohmatdyt.com.ua
ssh -v root@crm.ohmatdyt.com.ua
```

### Проблема: Docker контейнер не запускається
```bash
# Перевірити логи
docker compose logs [service_name]

# Перезібрати
docker compose build --no-cache [service_name]

# Перезапустити
docker compose restart [service_name]
```

### Проблема: SSL не працює
```bash
# Перевірити DNS
nslookup crm.ohmatdyt.com.ua

# Перевірити порти
sudo netstat -tulpn | grep -E ':(80|443)'

# Перезапустити Let's Encrypt
cd ~/ohmatdyt-crm/nginx
bash setup-letsencrypt.sh
```

### Більше troubleshooting:
Дивіться розділ "Troubleshooting" в `DEPLOYMENT_CRM_OHMATDYT_COM_UA.md`

---

## ✅ Checklist швидкої перевірки:

Перед розгортанням:
- [ ] Docker встановлено на сервері
- [ ] Проект клоновано з GitHub
- [ ] DNS налаштовано (crm.ohmatdyt.com.ua → IP сервера)
- [ ] Порти 80 і 443 відкриті
- [ ] `.env.prod` створено
- [ ] Паролі оновлено в `.env.prod`

Після розгортання:
- [ ] Всі контейнери запущені (`docker compose ps`)
- [ ] Frontend доступний (https://crm.ohmatdyt.com.ua)
- [ ] API відповідає (https://crm.ohmatdyt.com.ua/api/healthz)
- [ ] SSL працює (замок в браузері)
- [ ] Можна увійти (admin@ohmatdyt.com / admin123)
- [ ] Пароль адміністратора змінено

---

## 🚀 ГОТОВО ДО РОЗГОРТАННЯ!

**Запустити зараз:**

```batch
deploy-menu.bat
```

або

```powershell
.\deploy-crm-ohmatdyt.ps1
```

---

**Успішного розгортання! 🎉**

*Якщо виникли питання - дивіться документацію або пишіть в підтримку.*
