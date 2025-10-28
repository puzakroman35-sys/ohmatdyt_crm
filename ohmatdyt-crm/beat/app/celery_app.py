import os
from celery import Celery

# Load configuration from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

# Initialize Celery
celery = Celery(
    "ohmatdyt_crm",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# Celery configuration
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Kyiv",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Example task
@celery.task(name="app.celery_app.hello")
def hello():
    """Simple test task"""
    return "Hello from Celery!"

@celery.task(name="app.celery_app.test_task")
def test_task(x, y):
    """Test task with parameters"""
    return x + y

# Auto-discover tasks from other modules (will be added later)
# celery.autodiscover_tasks(['app.tasks'])

if __name__ == "__main__":
    celery.start()