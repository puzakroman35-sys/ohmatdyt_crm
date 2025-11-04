# Захист даних від випадкового видалення

## Проблема
За замовчуванням команда `docker compose down -v` видаляє всі volumes, включно з базою даних.

## Рішення: External Volumes

Volumes позначені як `external: true` не видаляються при `docker compose down -v`.

## Налаштування

### 1. Створіть external volumes (ОДИН РАЗ при першому розгортанні)

**Linux/Mac:**
```bash
chmod +x init-volumes.sh
./init-volumes.sh
```

**Windows PowerShell:**
```powershell
.\init-volumes.ps1
```

**Або вручну:**
```bash
docker volume create ohmatdyt_crm_db-data
docker volume create ohmatdyt_crm_media
docker volume create ohmatdyt_crm_static
```

### 2. Запустіть додаток
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Тепер безпечно!

✅ **Безпечні команди:**
```bash
# Видалить контейнери, але НЕ видалить дані
docker compose down -v

# Повний перезапуск з rebuild
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
docker compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

❌ **Єдиний спосіб видалити дані (якщо потрібно):**
```bash
# Спочатку зупиніть додаток
docker compose down

# Потім видаліть volumes вручну
docker volume rm ohmatdyt_crm_db-data
docker volume rm ohmatdyt_crm_media
docker volume rm ohmatdyt_crm_static
```

## Перевірка статусу volumes

```bash
# Список всіх volumes проєкту
docker volume ls | grep ohmatdyt_crm

# Детальна інформація про volume бази даних
docker volume inspect ohmatdyt_crm_db-data

# Розмір даних у volume
docker system df -v | grep ohmatdyt_crm
```

## Backup бази даних

```bash
# Створити backup
docker compose exec db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backup_$(date +%Y%m%d_%H%M%S).sql

# Або з compression
docker compose exec db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Відновити з backup
docker compose exec -T db psql -U ${POSTGRES_USER} ${POSTGRES_DB} < backup_file.sql
```

## Міграція даних на новий сервер

```bash
# На старому сервері
docker volume inspect ohmatdyt_crm_db-data --format '{{.Mountpoint}}'
# Скопіюйте шлях, наприклад: /var/lib/docker/volumes/ohmatdyt_crm_db-data/_data

# Створіть архів
sudo tar -czf db-data-backup.tar.gz -C /var/lib/docker/volumes/ohmatdyt_crm_db-data/_data .

# На новому сервері
# 1. Створіть volume
docker volume create ohmatdyt_crm_db-data

# 2. Розпакуйте дані
docker run --rm -v ohmatdyt_crm_db-data:/data -v $(pwd):/backup alpine tar -xzf /backup/db-data-backup.tar.gz -C /data
```

## Переваги external volumes

✅ Захист від випадкового видалення  
✅ Можливість backup/restore незалежно від контейнерів  
✅ Легка міграція між серверами  
✅ Можливість використання одного volume кількома compose проєктами  

## Недоліки

⚠️ Потрібно створювати volumes вручну перед першим запуском  
⚠️ Потрібно видаляти вручну при повному видаленні проєкту
