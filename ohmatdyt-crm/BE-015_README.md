# BE-015: Healthcheck та базове логування

## Огляд

BE-015 додає до Ohmatdyt CRM:
- ✅ Structured JSON logging
- ✅ Request tracking з унікальними ID
- ✅ Comprehensive healthcheck endpoint
- ✅ Redis та Database connection monitoring

## Quick Start

### Запуск API з логуванням

```bash
cd ohmatdyt-crm
docker-compose up api
```

Логи будуть виводитися в JSON форматі:
```json
{
  "timestamp": "2025-10-30T12:00:00.000Z",
  "level": "INFO",
  "logger": "ohmatdyt_crm",
  "message": "Application starting",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Перевірка healthcheck

```bash
curl http://localhost:8000/healthz
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-30T12:00:00.000Z",
  "version": "0.1.0",
  "services": {
    "database": "connected",
    "redis": "connected"
  },
  "filesystem": {
    "media_path": true,
    "static_path": true
  }
}
```

### Запуск тестів

```bash
cd ohmatdyt-crm
python test_be015.py
```

## Компоненти

### 1. Structured Logging

**Файл:** `api/app/utils/logging_config.py`

```python
from app.utils.logging_config import setup_logging, get_logger

# Налаштування при старті
logger = setup_logging(level="INFO")

# Використання в коді
logger = get_logger(__name__)
logger.info("User logged in", extra={'extra_fields': {'user_id': '123'}})
```

**Features:**
- JSON формат логів
- Автоматичний request-id
- Exception tracking
- Configurable log levels

### 2. Request Tracking

**Файл:** `api/app/middleware.py`

Middleware автоматично додається до кожного запиту:
```python
app.add_middleware(RequestTrackingMiddleware)
```

**Features:**
- Унікальний UUID для кожного запиту
- X-Request-ID в headers
- Process time вимірювання
- Автоматичне логування

### 3. Healthcheck

**Endpoint:** `GET /healthz`

**Features:**
- Real database ping (SELECT 1)
- Real Redis ping (PING)
- Filesystem paths check
- Overall health status
- Timestamp та version

**Legacy:** `GET /health` - backward compatible

### 4. Redis Connection

**Функція:** `check_redis_connection()`

```python
from app.database import check_redis_connection

if check_redis_connection():
    print("Redis OK")
else:
    print("Redis FAIL")
```

## Конфігурація

### Environment Variables

```bash
# Рівень логування
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Redis URL
REDIS_URL=redis://redis:6379/0
```

### Log Levels

- `DEBUG` - детальна інформація для debugging
- `INFO` - загальна інформація про роботу (default)
- `WARNING` - попередження про потенційні проблеми
- `ERROR` - помилки що потребують уваги
- `CRITICAL` - критичні помилки

## Моніторинг

### Kubernetes Health Probes

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /healthz
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Docker Healthcheck

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl --fail http://localhost:8000/healthz || exit 1
```

### Prometheus Metrics

Можна додати metrics scraper для логів:
```python
# Приклад метрик з process_time
request_duration_seconds{method="GET",path="/api/cases",status="200"} 0.123
```

## Log Aggregation

### ELK Stack Integration

```ruby
# Logstash config
input {
  file {
    path => "/var/log/api/*.log"
    codec => "json"
  }
}

filter {
  if [request_id] {
    mutate {
      add_field => { "trace_id" => "%{request_id}" }
    }
  }
}
```

### Grafana Loki

```yaml
# Promtail config
scrape_configs:
  - job_name: ohmatdyt-api
    static_configs:
      - targets:
          - localhost
        labels:
          job: ohmatdyt-api
          __path__: /var/log/api/*.log
```

## Тестування

### Automated Tests

```bash
python test_be015.py
```

**Тести:**
1. `/healthz` endpoint structure
2. X-Request-ID middleware
3. Legacy `/health` compatibility
4. Request logging
5. Unique request IDs

### Manual Testing

```bash
# Healthcheck
curl http://localhost:8000/healthz | jq

# Custom request ID
curl -H "X-Request-ID: my-test-123" http://localhost:8000/

# Check response headers
curl -I http://localhost:8000/healthz
```

## Troubleshooting

### Логи не в JSON форматі

**Проблема:** Старий формат логів  
**Рішення:** Перезапустити API після імплементації BE-015

### Request-ID не додається

**Проблема:** Middleware не активований  
**Рішення:** Перевірити що `app.add_middleware(RequestTrackingMiddleware)` викликано

### Healthcheck завжди unhealthy

**Проблема:** DB або Redis недоступні  
**Рішення:** 
```bash
# Перевірити DB
docker-compose ps db

# Перевірити Redis
docker-compose ps redis

# Перевірити логи
docker-compose logs api
```

## Production Recommendations

1. **Log Level:** Використовувати `WARNING` або `ERROR` в production
2. **Log Rotation:** Налаштувати logrotate або streaming
3. **Monitoring:** Додати alerts на healthcheck failures
4. **Request ID:** Передавати через headers між мікросервісами
5. **Metrics:** Інтегрувати з Prometheus для метрик

## Файли

```
ohmatdyt-crm/
├── api/app/
│   ├── utils/
│   │   └── logging_config.py          # Structured logging
│   ├── middleware.py                  # Request tracking
│   ├── database.py                    # +check_redis_connection
│   └── main.py                        # +healthz, +logging, +middleware
├── worker/app/
│   └── main.py                        # Worker logging
├── test_be015.py                      # Test suite
├── BE-015_IMPLEMENTATION_SUMMARY.md   # Full documentation
└── BE-015_README.md                   # This file
```

## Links

- **Task:** `tasks/BE-015.md`
- **Implementation:** `BE-015_IMPLEMENTATION_SUMMARY.md`
- **Status:** `PROJECT_STATUS.md`
- **Tests:** `test_be015.py`

## Status

✅ **PRODUCTION READY**

- Structured logging: ✅
- Request tracking: ✅
- Healthcheck: ✅
- Redis monitoring: ✅
- Tests: 5/5 passed ✅
- Documentation: Complete ✅

---

**Last Updated:** October 30, 2025  
**Version:** 0.1.0
