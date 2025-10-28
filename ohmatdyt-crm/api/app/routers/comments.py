"""
Comment API endpoints for cases
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.database import get_db
from app.dependencies import get_current_active_user

router = APIRouter(
    prefix="/api/cases",
    tags=["comments"]
)


@router.post("/{case_id}/comments", response_model=schemas.CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment_on_case(
    case_id: UUID,
    comment: schemas.CommentCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Додає коментар до звернення.
    
    RBAC:
    - Публічні коментарі (is_internal=False): Всі авторизовані користувачі
    - Внутрішні коментарі (is_internal=True): Тільки EXECUTOR та ADMIN
    
    Email нотифікації:
    - Публічні коментарі → автор звернення + відповідальний
    - Внутрішні коментарі → виконавці категорії + адміни (БЕЗ автора-оператора)
    """
    # Перевірка існування звернення
    db_case = crud.get_case(db, case_id)
    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with id {case_id} not found"
        )
    
    # RBAC: Тільки EXECUTOR та ADMIN можуть створювати внутрішні коментарі
    if comment.is_internal and current_user.role == models.UserRole.OPERATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="OPERATOR cannot create internal comments. Only EXECUTOR and ADMIN roles are allowed."
        )
    
    # Валідація тексту коментаря
    if not comment.text or len(comment.text.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment text must be at least 5 characters"
        )
    
    if len(comment.text) > 5000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment text must not exceed 5000 characters"
        )
    
    # Створення коментаря
    db_comment = crud.create_comment(
        db=db,
        case_id=case_id,
        author_id=current_user.id,
        text=comment.text.strip(),
        is_internal=comment.is_internal
    )
    
    # Email нотифікації (async через Celery)
    try:
        from app.celery_app import send_comment_notification
        
        send_comment_notification.delay(
            case_id=str(db_case.id),
            case_public_id=db_case.public_id,
            comment_id=str(db_comment.id),
            comment_text=db_comment.text,
            is_internal=db_comment.is_internal,
            author_id=str(current_user.id),
            author_name=current_user.full_name,
            case_author_id=str(db_case.author_id),
            responsible_id=str(db_case.responsible_id) if db_case.responsible_id else None,
            category_id=str(db_case.category_id)
        )
    except Exception as e:
        # Логування помилки, але не падаємо
        print(f"Warning: Failed to queue comment notification: {str(e)}")
    
    # Завантаження author для відповіді
    db.refresh(db_comment)
    
    return schemas.CommentResponse(
        id=str(db_comment.id),
        case_id=str(db_comment.case_id),
        author_id=str(db_comment.author_id),
        text=db_comment.text,
        is_internal=db_comment.is_internal,
        created_at=db_comment.created_at,
        author=schemas.UserResponse(
            id=str(current_user.id),
            username=current_user.username,
            email=current_user.email,
            full_name=current_user.full_name,
            role=current_user.role,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        )
    )


@router.get("/{case_id}/comments", response_model=schemas.CommentListResponse)
def get_case_comments(
    case_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Отримує коментарі звернення з урахуванням RBAC.
    
    RBAC правила видимості:
    - OPERATOR: Бачить тільки публічні коментарі (is_internal=False)
    - EXECUTOR: Бачить всі коментарі (публічні + внутрішні)
    - ADMIN: Бачить всі коментарі
    """
    # Перевірка існування звернення
    db_case = crud.get_case(db, case_id)
    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with id {case_id} not found"
        )
    
    # RBAC: Перевірка доступу до звернення
    # OPERATOR може бачити тільки свої звернення
    if current_user.role == models.UserRole.OPERATOR and db_case.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this case"
        )
    
    # Отримання коментарів з RBAC фільтрацією
    comments = crud.get_comments_by_case(
        db=db,
        case_id=case_id,
        user_role=current_user.role,
        user_id=current_user.id
    )
    
    # Формування відповіді з авторами
    comment_responses = []
    for comment in comments:
        comment_responses.append(
            schemas.CommentResponse(
                id=str(comment.id),
                case_id=str(comment.case_id),
                author_id=str(comment.author_id),
                text=comment.text,
                is_internal=comment.is_internal,
                created_at=comment.created_at,
                author=schemas.UserResponse(
                    id=str(comment.author.id),
                    username=comment.author.username,
                    email=comment.author.email,
                    full_name=comment.author.full_name,
                    role=comment.author.role,
                    is_active=comment.author.is_active,
                    created_at=comment.author.created_at,
                    updated_at=comment.author.updated_at
                )
            )
        )
    
    return schemas.CommentListResponse(
        comments=comment_responses,
        total=len(comment_responses)
    )
