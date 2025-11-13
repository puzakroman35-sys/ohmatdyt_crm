#!/bin/bash

# Деплой виправлення Auth Endpoints на Production
# Дата: 2025-11-06
# Коміт: ddf2f4f

set -e  # Зупинка при помилці

echo "🚀 Починаємо деплой Auth Endpoints Fix..."
echo ""

# Кольори для виводу
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Перевірка поточної директорії
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Помилка: docker-compose.yml не знайдено${NC}"
    echo "Переконайтесь що ви в директорії проекту"
    exit 1
fi

echo -e "${YELLOW}📍 Поточна директорія:${NC} $(pwd)"
echo ""

# Крок 1: Зупинка контейнерів
echo -e "${YELLOW}⏸️  Крок 1: Зупинка контейнерів...${NC}"
docker compose down
echo -e "${GREEN}✅ Контейнери зупинено${NC}"
echo ""

# Крок 2: Оновлення коду з Git
echo -e "${YELLOW}📥 Крок 2: Оновлення коду з Git...${NC}"
git pull origin main
echo -e "${GREEN}✅ Код оновлено${NC}"
echo ""

# Крок 3: Перебудова образів
echo -e "${YELLOW}🔨 Крок 3: Перебудова образів API та Frontend...${NC}"
docker compose build api frontend
echo -e "${GREEN}✅ Образи перебудовано${NC}"
echo ""

# Крок 4: Запуск контейнерів
echo -e "${YELLOW}▶️  Крок 4: Запуск контейнерів...${NC}"
docker compose up -d
echo -e "${GREEN}✅ Контейнери запущено${NC}"
echo ""

# Крок 5: Очікування запуску сервісів
echo -e "${YELLOW}⏳ Крок 5: Очікування запуску сервісів (10 секунд)...${NC}"
sleep 10
echo ""

# Крок 6: Перевірка статусу
echo -e "${YELLOW}📊 Крок 6: Перевірка статусу контейнерів...${NC}"
docker compose ps
echo ""

# Крок 7: Перевірка auth endpoint
echo -e "${YELLOW}🔍 Крок 7: Перевірка auth endpoint...${NC}"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' || echo "ERROR")

if echo "$RESPONSE" | grep -q "detail"; then
    echo -e "${GREEN}✅ Auth endpoint працює (отримано відповідь від API)${NC}"
else
    echo -e "${RED}⚠️  Попередження: Можливо API ще не готовий${NC}"
    echo "Відповідь: $RESPONSE"
fi
echo ""

# Крок 8: Перевірка routes
echo -e "${YELLOW}🛣️  Крок 8: Перевірка зареєстрованих auth routes...${NC}"
docker exec ohmatdyt_crm-api-1 python -c "from app.main import app; routes = [r.path for r in app.routes if hasattr(r, 'methods') and 'api/auth' in r.path]; print('\n'.join(sorted(routes)))" || echo -e "${RED}⚠️  Не вдалося перевірити routes${NC}"
echo ""

# Фінальне повідомлення
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 Деплой завершено!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}📋 Перевірте наступне:${NC}"
echo "  ✓ Логін через браузер: http://10.24.2.187:3000/login"
echo "  ✓ API endpoint: http://localhost:8000/api/auth/login"
echo "  ✓ Зміна пароля: http://10.24.2.187:3000/profile"
echo ""
echo -e "${YELLOW}📝 Для перегляду логів:${NC}"
echo "  docker compose logs -f api"
echo "  docker compose logs -f frontend"
echo ""
