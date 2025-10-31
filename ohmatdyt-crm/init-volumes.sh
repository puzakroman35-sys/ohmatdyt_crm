#!/bin/bash
# Скрипт для створення external volumes
# Ці volumes не будуть видалені при docker compose down -v

echo "🔧 Створення external volumes для production..."

# Створюємо volumes якщо їх ще немає
docker volume create ohmatdyt_crm_db-data
docker volume create ohmatdyt_crm_media
docker volume create ohmatdyt_crm_static

echo "✅ Volumes створено:"
docker volume ls | grep ohmatdyt_crm

echo ""
echo "📊 Інформація про volumes:"
echo "db-data:"
docker volume inspect ohmatdyt_crm_db-data --format '{{.Mountpoint}}'
echo "media:"
docker volume inspect ohmatdyt_crm_media --format '{{.Mountpoint}}'
echo "static:"
docker volume inspect ohmatdyt_crm_static --format '{{.Mountpoint}}'

echo ""
echo "✅ Готово! Тепер ці volumes будуть збережені навіть після 'docker compose down -v'"
