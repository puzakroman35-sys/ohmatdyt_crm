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


@celery.task(
    name="app.celery_app.send_new_case_notification",
    bind=True,
    max_retries=5,
    default_retry_delay=60  # 1 minute
)
def send_new_case_notification(self, case_id: str, case_public_id: int, category_id: str):
    """
    Send email notification to executors when a new case is created.
    
    This task is queued when an operator creates a new case.
    It retrieves all executors for the category and sends them an email notification.
    
    Args:
        case_id: UUID of the case (as string)
        case_public_id: 6-digit public ID of the case
        category_id: UUID of the category (as string)
        
    Note: This is a placeholder implementation. Full email functionality
    will be implemented in BE-013 and BE-014.
    """
    try:
        # Import here to avoid circular dependencies
        from uuid import UUID
        from app.database import SessionLocal
        from app import crud
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Get case details
            case = db.execute(
                f"SELECT * FROM cases WHERE id = '{case_id}'"
            ).first()
            
            if not case:
                print(f"Case {case_id} not found, skipping notification")
                return
            
            # Get category details
            category = db.execute(
                f"SELECT * FROM categories WHERE id = '{category_id}'"
            ).first()
            
            category_name = category.name if category else "Unknown"
            
            # Get executors (simplified - gets all active executors)
            executors = db.execute(
                "SELECT * FROM users WHERE role IN ('EXECUTOR', 'ADMIN') AND is_active = true"
            ).fetchall()
            
            # Log notification (placeholder for actual email sending)
            print(f"[NOTIFICATION] New case #{case_public_id} created in category '{category_name}'")
            print(f"[NOTIFICATION] Notifying {len(executors)} executor(s)")
            
            for executor in executors:
                # Placeholder for actual email sending (will be implemented in BE-014)
                print(f"[NOTIFICATION] Would send email to: {executor.email} ({executor.full_name})")
                # TODO: Call email sending service here
                # send_email(
                #     to=executor.email,
                #     subject=f"New case #{case_public_id}",
                #     template="new_case",
                #     context={...}
                # )
            
            return {
                "status": "success",
                "case_id": case_id,
                "public_id": case_public_id,
                "executors_notified": len(executors)
            }
            
        finally:
            db.close()
            
    except Exception as exc:
        # Retry with exponential backoff
        print(f"Error sending notification for case {case_public_id}: {exc}")
        
        # Calculate exponential backoff: 60s, 120s, 240s, 480s, 960s
        retry_delay = 60 * (2 ** self.request.retries)
        
        raise self.retry(exc=exc, countdown=retry_delay)


@celery.task(
    name="app.celery_app.send_case_taken_notification",
    bind=True,
    max_retries=5,
    default_retry_delay=60  # 1 minute
)
def send_case_taken_notification(
    self,
    case_id: str,
    case_public_id: int,
    executor_id: str,
    author_id: str
):
    """
    Send email notification to case author when executor takes case into work.
    
    This task is queued when an executor takes a NEW case into work.
    It notifies the operator who created the case that it's being processed.
    
    Args:
        case_id: UUID of the case (as string)
        case_public_id: 6-digit public ID of the case
        executor_id: UUID of the executor taking the case (as string)
        author_id: UUID of the case author/operator (as string)
        
    Note: This is a placeholder implementation. Full email functionality
    will be implemented in BE-014.
    """
    try:
        # Import here to avoid circular dependencies
        from app.database import SessionLocal
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Get executor details
            executor = db.execute(
                f"SELECT * FROM users WHERE id = '{executor_id}'"
            ).first()
            
            # Get author details
            author = db.execute(
                f"SELECT * FROM users WHERE id = '{author_id}'"
            ).first()
            
            if not author:
                print(f"Author {author_id} not found, skipping notification")
                return
            
            if not executor:
                print(f"Executor {executor_id} not found, skipping notification")
                return
            
            # Log notification (placeholder for actual email sending)
            print(f"[NOTIFICATION] Case #{case_public_id} taken into work")
            print(f"[NOTIFICATION] Executor: {executor.full_name} ({executor.email})")
            print(f"[NOTIFICATION] Notifying author: {author.full_name} ({author.email})")
            
            # Placeholder for actual email sending (will be implemented in BE-014)
            # TODO: Call email sending service here
            # send_email(
            #     to=author.email,
            #     subject=f"Case #{case_public_id} is being processed",
            #     template="case_taken",
            #     context={
            #         "case_public_id": case_public_id,
            #         "executor_name": executor.full_name,
            #         "author_name": author.full_name,
            #     }
            # )
            
            return {
                "status": "success",
                "case_id": case_id,
                "public_id": case_public_id,
                "executor": executor.email,
                "author_notified": author.email
            }
            
        finally:
            db.close()
            
    except Exception as exc:
        # Retry with exponential backoff
        print(f"Error sending case taken notification for case {case_public_id}: {exc}")
        
        # Calculate exponential backoff: 60s, 120s, 240s, 480s, 960s
        retry_delay = 60 * (2 ** self.request.retries)
        
        raise self.retry(exc=exc, countdown=retry_delay)


@celery.task(
    name="app.celery_app.send_case_status_changed_notification",
    bind=True,
    max_retries=5,
    default_retry_delay=60  # 1 minute
)
def send_case_status_changed_notification(
    self,
    case_id: str,
    case_public_id: int,
    new_status: str,
    executor_id: str,
    author_id: str,
    comment: str
):
    """
    Send email notification to case author when executor changes case status.
    
    This task is queued when an executor changes case status from IN_PROGRESS
    to NEEDS_INFO, REJECTED, or DONE.
    
    Args:
        case_id: UUID of the case (as string)
        case_public_id: 6-digit public ID of the case
        new_status: New case status (NEEDS_INFO, REJECTED, or DONE)
        executor_id: UUID of the executor changing status (as string)
        author_id: UUID of the case author/operator (as string)
        comment: Comment explaining the status change
        
    Note: This is a placeholder implementation. Full email functionality
    will be implemented in BE-014.
    """
    try:
        # Import here to avoid circular dependencies
        from app.database import SessionLocal
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Get executor details
            executor = db.execute(
                f"SELECT * FROM users WHERE id = '{executor_id}'"
            ).first()
            
            # Get author details
            author = db.execute(
                f"SELECT * FROM users WHERE id = '{author_id}'"
            ).first()
            
            if not author:
                print(f"Author {author_id} not found, skipping notification")
                return
            
            if not executor:
                print(f"Executor {executor_id} not found, skipping notification")
                return
            
            # Translate status to Ukrainian for user-friendly messages
            status_translations = {
                "NEEDS_INFO": "Потрібна додаткова інформація",
                "REJECTED": "Відхилено",
                "DONE": "Виконано",
                "IN_PROGRESS": "В роботі"
            }
            
            status_ua = status_translations.get(new_status, new_status)
            
            # Log notification (placeholder for actual email sending)
            print(f"[NOTIFICATION] Case #{case_public_id} status changed to {new_status}")
            print(f"[NOTIFICATION] Executor: {executor.full_name} ({executor.email})")
            print(f"[NOTIFICATION] Notifying author: {author.full_name} ({author.email})")
            print(f"[NOTIFICATION] Comment: {comment[:100]}...")
            
            # Placeholder for actual email sending (will be implemented in BE-014)
            # TODO: Call email sending service here
            # send_email(
            #     to=author.email,
            #     subject=f"Case #{case_public_id} status: {status_ua}",
            #     template="case_status_changed",
            #     context={
            #         "case_public_id": case_public_id,
            #         "new_status": new_status,
            #         "status_ua": status_ua,
            #         "executor_name": executor.full_name,
            #         "author_name": author.full_name,
            #         "comment": comment,
            #     }
            # )
            
            return {
                "status": "success",
                "case_id": case_id,
                "public_id": case_public_id,
                "new_status": new_status,
                "executor": executor.email,
                "author_notified": author.email
            }
            
        finally:
            db.close()
            
    except Exception as exc:
        # Retry with exponential backoff
        print(f"Error sending status change notification for case {case_public_id}: {exc}")
        
        # Calculate exponential backoff: 60s, 120s, 240s, 480s, 960s
        retry_delay = 60 * (2 ** self.request.retries)
        
        raise self.retry(exc=exc, countdown=retry_delay)



# Auto-discover tasks from other modules (will be added later)
# celery.autodiscover_tasks(['app.tasks'])

if __name__ == "__main__":
    celery.start()