# Fix: Подвійний /api/api префікс в URL

## Проблема
На production сервері всі API запити отримували 404 через подвійний префікс `/api/api/`:
- ❌ `https://10.24.2.187/api/api/dashboard/summary`
- ❌ `https://10.24.2.187/api/api/categories`
- ❌ `https://10.24.2.187/api/api/cases`

## Причини

### 1. Frontend: відсутність NEXT_PUBLIC_API_URL
У `.env.prod` була тільки `NEXT_PUBLIC_API_BASE_URL=/api`, але не було `NEXT_PUBLIC_API_URL`.

В коді `login.tsx`:
```typescript
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const response = await fetch(`${apiUrl}/api/auth/login`, {
```

Без `NEXT_PUBLIC_API_URL` використовувався fallback `/api`, що створювало `/api/api/...`

### 2. Nginx: неправильна конфігурація proxy_pass
У `nginx/nginx.prod.conf`:
```nginx
location /api/ {
    proxy_pass http://api_backend/;  # ❌ Trailing slash видаляє /api/
}
```

Коли після `proxy_pass` стоїть trailing slash (`/`), nginx **видаляє** частину URL що співпала з location.
- Запит: `https://10.24.2.187/api/dashboard/summary`
- Nginx передає на backend: `http://api:8000/dashboard/summary` (БЕЗ /api/)

Але FastAPI роутери очікують `/api/`:
```python
router = APIRouter(prefix="/api/dashboard")
router = APIRouter(prefix="/api/categories")
router = APIRouter(prefix="/api/cases")
```

## Рішення

### 1. Додати NEXT_PUBLIC_API_URL в .env.prod
```bash
# Frontend
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://10.24.2.187  # ✅ Додано
NEXT_PUBLIC_API_BASE_URL=/api
```

### 2. Виправити nginx.prod.conf
```nginx
location /api/ {
    proxy_pass http://api_backend;  # ✅ Без trailing slash - зберігає /api/
}
```

## Застосування змін

### На production сервері (вже зроблено):
```bash
cd ~/ohmatdyt-crm/ohmatdyt-crm

# 1. Бекап
cp .env.prod .env.prod.backup
cp nginx/nginx.prod.conf nginx/nginx.prod.conf.backup

# 2. Додати NEXT_PUBLIC_API_URL
sed -i '/NEXT_PUBLIC_API_BASE_URL/i NEXT_PUBLIC_API_URL=https://10.24.2.187' .env.prod

# 3. Виправити nginx
sed -i 's|proxy_pass http://api_backend/;|proxy_pass http://api_backend;|g' nginx/nginx.prod.conf

# 4. Перезапустити
docker compose build frontend
docker compose up -d frontend
docker compose exec nginx nginx -s reload
```

### Локально (для наступних deployment):
✅ Зміни вже застосовані в:
- `ohmatdyt-crm/.env.prod` - додано `NEXT_PUBLIC_API_URL=https://10.24.2.187`
- `ohmatdyt-crm/nginx/nginx.prod.conf` - виправлено `proxy_pass`

## Перевірка

### Тепер працює:
✅ `https://10.24.2.187/api/auth/login`
✅ `https://10.24.2.187/api/dashboard/summary`
✅ `https://10.24.2.187/api/categories?is_active=true`
✅ `https://10.24.2.187/api/cases?skip=0&limit=20`

### Логи API показують правильні URL:
```
INFO: 172.18.0.8:12345 - "GET /api/dashboard/summary HTTP/1.1" 200 OK
INFO: 172.18.0.8:12346 - "GET /api/categories?is_active=true HTTP/1.1" 200 OK
```

## Важливо для наступних серверів

При deployment на новий сервер:
1. Оновити IP в `.env.prod`:
   - `NEXT_PUBLIC_API_URL=https://НОВИЙ_IP`
   - `NGINX_SERVER_NAME=НОВИЙ_IP`
   - `ALLOWED_HOSTS=НОВИЙ_IP,localhost,127.0.0.1`
   - `CORS_ORIGINS=http://НОВИЙ_IP,http://localhost`

2. Конфігурація nginx вже правильна ✅

## Дата виправлення
06.11.2025

## Файли змінені
- `ohmatdyt-crm/.env.prod` (НЕ КОМІТИТИ В GIT!)
- `ohmatdyt-crm/nginx/nginx.prod.conf` (комітити можна)
