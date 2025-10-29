import os
from celery import Celery
from typing import Optional

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
    # Explicitly include task modules
    imports=(
        'app.celery_app',
    ),
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
    
    Improvements in BE-013:
    - Logs notifications to notification_logs table
    - Proper exponential backoff retry
    - Email sending через email_service module
    
    Args:
        case_id: UUID of the case (as string)
        case_public_id: 6-digit public ID of the case
        category_id: UUID of the category (as string)
    """
    from uuid import UUID
    from app.database import SessionLocal
    from app import models, crud
    from app.email_service import send_email, render_template
    from datetime import datetime, timedelta
    
    db = SessionLocal()
    
    try:
        # Get case details
        case = db.execute(
            f"SELECT * FROM cases WHERE id = '{case_id}'"
        ).first()
        
        if not case:
            print(f"[NOTIFICATION] Case {case_id} not found, skipping")
            return {"status": "skipped", "reason": "case_not_found"}
        
        # Get category details
        category = db.execute(
            f"SELECT * FROM categories WHERE id = '{category_id}'"
        ).first()
        
        category_name = category.name if category else "Unknown"
        
        # Get executors (simplified - gets all active executors)
        executors = db.execute(
            "SELECT * FROM users WHERE role IN ('EXECUTOR', 'ADMIN') AND is_active = true"
        ).fetchall()
        
        print(f"[BE-013] Sending notifications for new case #{case_public_id}")
        print(f"[BE-013] Category: {category_name}")
        print(f"[BE-013] Executors to notify: {len(executors)}")
        
        sent_count = 0
        failed_count = 0
        
        for executor in executors:
            # Render email template
            text_body, html_body = render_template("new_case", {
                "public_id": case_public_id,
                "category": category_name,
                "channel": "Email",  # TODO: get from case
                "applicant_name": case.applicant_name,
                "summary": case.summary[:200] + "..." if len(case.summary) > 200 else case.summary,
            })
            
            # Create notification log entry
            notification = crud.create_notification_log(
                db=db,
                notification_type=models.NotificationType.NEW_CASE,
                recipient_email=executor.email,
                recipient_user_id=UUID(executor.id),
                related_case_id=UUID(case_id),
                subject=f"Нове звернення #{case_public_id}",
                body_text=text_body,
                body_html=html_body,
                celery_task_id=self.request.id,
            )
            
            # Send email
            success = send_email(
                to=executor.email,
                subject=f"Нове звернення #{case_public_id}",
                body_text=text_body,
                body_html=html_body,
                notification_log_id=notification.id,
            )
            
            # Update notification status
            if success:
                crud.update_notification_status(
                    db=db,
                    notification_id=notification.id,
                    status=models.NotificationStatus.SENT,
                )
                sent_count += 1
            else:
                crud.update_notification_status(
                    db=db,
                    notification_id=notification.id,
                    status=models.NotificationStatus.FAILED,
                    error_message="SMTP send failed (placeholder)",
                )
                failed_count += 1
        
        print(f"[BE-013] Sent: {sent_count}, Failed: {failed_count}")
        
        return {
            "status": "completed",
            "case_id": case_id,
            "public_id": case_public_id,
            "sent": sent_count,
            "failed": failed_count,
        }
        
    except Exception as exc:
        # Log error
        print(f"[BE-013] Error in send_new_case_notification: {exc}")
        
        # Exponential backoff: 60s, 120s, 240s, 480s, 960s
        retry_delay = 60 * (2 ** self.request.retries)
        
        raise self.retry(exc=exc, countdown=retry_delay, max_retries=5)
        
    finally:
        db.close()


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


@celery.task(
    name="app.celery_app.send_comment_notification",
    bind=True,
    max_retries=5,
    default_retry_delay=60  # 1 minute
)
def send_comment_notification(
    self,
    case_id: str,
    case_public_id: int,
    comment_id: str,
    comment_text: str,
    is_internal: bool,
    author_id: str,
    author_name: str,
    case_author_id: str,
    responsible_id: str | None,
    category_id: str
):
    """
    Send email notification when comment is added to case.
    
    Email розсилка згідно правил:
    - Публічні коментарі → автор звернення + відповідальний виконавець
    - Внутрішні коментарі → виконавці категорії + адміни (БЕЗ автора-оператора)
    
    Args:
        case_id: UUID звернення
        case_public_id: 6-значний публічний ID
        comment_id: UUID коментаря
        comment_text: Текст коментаря
        is_internal: Чи є коментар внутрішнім
        author_id: UUID автора коментаря
        author_name: Повне ім'я автора
        case_author_id: UUID автора звернення (оператора)
        responsible_id: UUID відповідального виконавця (може бути None)
        category_id: UUID категорії звернення
    
    Note: Placeholder implementation. Full email functionality in BE-014.
    """
    try:
        from app.database import SessionLocal
        
        db = SessionLocal()
        
        try:
            recipients = []
            
            if is_internal:
                # Внутрішній коментар: відправляємо виконавцям категорії + адмінам
                # БЕЗ автора звернення (оператора)
                print(f"[NOTIFICATION] Internal comment on case #{case_public_id}")
                
                # Отримати всіх EXECUTOR та ADMIN (пізніше буде фільтр по категорії)
                executors_admins = db.execute(
                    "SELECT * FROM users WHERE role IN ('EXECUTOR', 'ADMIN') AND is_active = true"
                ).fetchall()
                
                for user in executors_admins:
                    if user.id != author_id:  # Не надсилати автору коментаря
                        recipients.append({
                            "email": user.email,
                            "full_name": user.full_name,
                            "role": user.role
                        })
                
                print(f"[NOTIFICATION] Notifying {len(recipients)} executor(s)/admin(s)")
                
            else:
                # Публічний коментар: відправляємо автору звернення + відповідальному
                print(f"[NOTIFICATION] Public comment on case #{case_public_id}")
                
                # Автор звернення (OPERATOR)
                case_author = db.execute(
                    f"SELECT * FROM users WHERE id = '{case_author_id}'"
                ).first()
                
                if case_author and case_author.id != author_id:
                    recipients.append({
                        "email": case_author.email,
                        "full_name": case_author.full_name,
                        "role": "Case Author"
                    })
                
                # Відповідальний виконавець
                if responsible_id:
                    responsible = db.execute(
                        f"SELECT * FROM users WHERE id = '{responsible_id}'"
                    ).first()
                    
                    if responsible and responsible.id != author_id:
                        recipients.append({
                            "email": responsible.email,
                            "full_name": responsible.full_name,
                            "role": "Responsible"
                        })
                
                print(f"[NOTIFICATION] Notifying {len(recipients)} user(s)")
            
            # Log recipients (placeholder for actual email sending)
            print(f"[NOTIFICATION] Comment by: {author_name}")
            print(f"[NOTIFICATION] Comment type: {'Internal' if is_internal else 'Public'}")
            print(f"[NOTIFICATION] Comment preview: {comment_text[:100]}...")
            
            for recipient in recipients:
                print(f"[NOTIFICATION] Would send email to: {recipient['email']} ({recipient['full_name']}) - {recipient['role']}")
                # TODO: Implement actual email sending in BE-014
                # send_email(
                #     to=recipient["email"],
                #     subject=f"New comment on case #{case_public_id}",
                #     template="new_comment",
                #     context={
                #         "case_public_id": case_public_id,
                #         "comment_text": comment_text,
                #         "is_internal": is_internal,
                #         "author_name": author_name,
                #         "recipient_name": recipient["full_name"],
                #     }
                # )
            
            return {
                "status": "success",
                "case_id": case_id,
                "public_id": case_public_id,
                "comment_id": comment_id,
                "is_internal": is_internal,
                "recipients_notified": len(recipients)
            }
            
        finally:
            db.close()
            
    except Exception as exc:
        print(f"Error sending comment notification for case {case_public_id}: {exc}")
        
        # Exponential backoff retry
        retry_delay = 60 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=retry_delay)


# Auto-discover tasks from this module
celery.autodiscover_tasks(['app.celery_app'], related_name='', force=True)

# Auto-discover tasks from other modules (will be added later)
# celery.autodiscover_tasks(['app.tasks'])

if __name__ == "__main__":
    celery.start()