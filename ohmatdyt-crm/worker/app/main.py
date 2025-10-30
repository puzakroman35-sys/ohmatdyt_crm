"""
BE-015: Celery Worker application

This is a placeholder for Celery worker configuration.
The actual worker is started via Celery CLI, not FastAPI.
"""
import os
import logging
import json
from datetime import datetime
from typing import Any

# BE-015: Simple structured logging for worker
class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)


# Setup logging
logger = logging.getLogger("ohmatdyt_worker")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.propagate = False


def check_redis_connection(redis_url: str) -> bool:
    """
    BE-015: Check Redis connection for worker.
    
    Args:
        redis_url: Redis connection URL
    
    Returns:
        True if connection successful, False otherwise
    """
    import redis
    
    try:
        redis_client = redis.from_url(redis_url, decode_responses=True)
        redis_client.ping()
        redis_client.close()
        return True
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return False


# BE-015: Check Redis on worker startup
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

logger.info(
    "Worker initializing",
    extra={'redis_url': REDIS_URL}
)

redis_ok = check_redis_connection(REDIS_URL)
if redis_ok:
    logger.info("Redis connection established")
else:
    logger.error("Redis connection failed - worker may not function properly")

logger.info("Worker initialized")


# This file is loaded by Celery worker
# Actual Celery configuration should be in celery.py or similar