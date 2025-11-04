"""
User management endpoints (ADMIN only)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app import schemas, crud, models
from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.auth import generate_temp_password

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("", response_model=schemas.UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    role: Optional[models.UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by username, email, or full_name"),
    order_by: Optional[str] = Query("username", description="Sort field"),
    order: Optional[str] = Query("asc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Отримати список користувачів з фільтрацією та пагінацією (ADMIN тільки).
    
    **Query Parameters:**
    - skip: Кількість записів для пропуску (пагінація)
    - limit: Максимальна кількість записів (1-100)
    - role: Фільтр за роллю (OPERATOR, EXECUTOR, ADMIN)
    - is_active: Фільтр за статусом активності
    - search: Пошук за логіном, email або ПІБ (case-insensitive)
    - order_by: Поле сортування (username, created_at, email, full_name)
    - order: Порядок сортування (asc, desc)
    
    **Response:**
    - users: Список користувачів
    - total: Загальна кількість
    - page: Номер сторінки
    - page_size: Розмір сторінки
    
    **Errors:**
    - 401: Не авторизований
    - 403: Недостатньо прав (потрібен ADMIN)
    """
    # Формуємо order_by з префіксом для descending
    order_by_param = f"-{order_by}" if order == "desc" else order_by
    
    users, total = crud.get_users(
        db=db,
        skip=skip,
        limit=limit,
        role=role,
        is_active=is_active,
        search=search,
        order_by=order_by_param
    )
    
    user_responses = [
        schemas.UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        for user in users
    ]
    
    page = (skip // limit) + 1 if limit > 0 else 1
    
    return {
        "users": user_responses,
        "total": total,
        "page": page,
        "page_size": limit
    }


@router.post("", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Створити нового користувача (ADMIN тільки).
    
    **Request Body:**
    - username: Ім'я користувача (унікальне, 3-50 символів)
    - email: Email (унікальний)
    - full_name: Повне ім'я
    - password: Пароль (мінімум 8 символів, має містити літери, цифри, спецсимволи)
    - role: Роль (OPERATOR, EXECUTOR, ADMIN)
    - executor_category_ids: Список UUID категорій (тільки для EXECUTOR)
    
    **Response:**
    - Створений користувач (без пароля)
    
    **Errors:**
    - 400: Невалідні дані (username/email вже існує)
    - 401: Не авторизований
    - 403: Недостатньо прав (потрібен ADMIN)
    - 422: Помилка валідації
    """
    try:
        # TODO: Implement executor_category_ids support (BE-013, BE-014)
        # For now, we'll ignore executor_category_ids as the table doesn't exist yet
        
        db_user = crud.create_user(db=db, user=user_data)
        
        # Manually create response with UUID conversion
        return schemas.UserResponse(
            id=str(db_user.id),
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            role=db_user.role,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(
    current_user: models.User = Depends(get_current_user)
):
    """
    Отримати інформацію про поточного користувача.
    
    **Response:**
    - Інформація про поточного авторизованого користувача
    
    **Errors:**
    - 401: Не авторизований
    """
    # Return current user with UUID converted to string
    return schemas.UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Отримати інформацію про користувача за ID (ADMIN тільки).
    
    **Path Parameters:**
    - user_id: UUID користувача
    
    **Response:**
    - Інформація про користувача (без пароля)
    
    **Errors:**
    - 401: Не авторизований
    - 403: Недостатньо прав (потрібен ADMIN)
    - 404: Користувача не знайдено
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    db_user = crud.get_user(db, user_uuid)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found"
        )
    
    return schemas.UserResponse(
        id=str(db_user.id),
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        role=db_user.role,
        is_active=db_user.is_active,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at
    )


@router.put("/{user_id}", response_model=schemas.UserResponse)
@router.patch("/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: str,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Оновити інформацію про користувача (ADMIN тільки).
    
    **Path Parameters:**
    - user_id: UUID користувача
    
    **Request Body:**
    - full_name: Повне ім'я (опціонально)
    - email: Email (опціонально, унікальний)
    - role: Роль (опціонально)
    - executor_category_ids: Список UUID категорій (опціонально, тільки для EXECUTOR)
    
    **Response:**
    - Оновлений користувач
    
    **Errors:**
    - 400: Невалідні дані (email вже існує)
    - 401: Не авторизований
    - 403: Недостатньо прав (потрібен ADMIN)
    - 404: Користувача не знайдено
    - 422: Помилка валідації
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    try:
        # TODO: Implement executor_category_ids support (BE-013, BE-014)
        # For now, we'll ignore executor_category_ids as the table doesn't exist yet
        
        db_user = crud.update_user(db=db, user_id=user_uuid, user_update=user_update)
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{user_id}' not found"
            )
        
        return schemas.UserResponse(
            id=str(db_user.id),
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            role=db_user.role,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{user_id}/reset-password", response_model=schemas.ResetPasswordResponse)
async def reset_user_password(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Скинути пароль користувача та згенерувати тимчасовий (ADMIN тільки).
    
    **Path Parameters:**
    - user_id: UUID користувача
    
    **Response:**
    - message: Повідомлення про успіх
    - temp_password: Тимчасовий пароль (відправляється через email в продакшені)
    
    **Errors:**
    - 401: Не авторизований
    - 403: Недостатньо прав (потрібен ADMIN)
    - 404: Користувача не знайдено
    
    **Note:**
    В продакшні тимчасовий пароль має відправлятися через Celery task на email користувача.
    Зараз повертається в response для тестування.
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    db_user = crud.get_user(db, user_uuid)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found"
        )
    
    # Генеруємо тимчасовий пароль
    temp_password = generate_temp_password()
    
    # Оновлюємо пароль в БД
    crud.reset_user_password(db=db, user_id=user_uuid, new_password=temp_password)
    
    # TODO: Відправити email через Celery task (BE-013)
    # from app.tasks import send_password_reset_email
    # send_password_reset_email.delay(db_user.email, db_user.username, temp_password)
    
    return {
        "message": f"Password reset successfully for user '{db_user.username}'. Temporary password sent to email.",
        "temp_password": temp_password  # В продакшні НЕ повертати в response!
    }


@router.post("/{user_id}/deactivate", response_model=schemas.DeactivateUserResponse)
async def deactivate_user(
    user_id: str,
    force: bool = Query(False, description="Force deactivation even if user has active cases"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Деактивувати користувача з перевіркою активних звернень (ADMIN тільки).
    
    **Path Parameters:**
    - user_id: UUID користувача
    
    **Query Parameters:**
    - force: Примусова деактивація навіть при наявності активних звернень (за замовчуванням False)
    
    **Response:**
    - message: Повідомлення про результат
    - user_id: UUID користувача
    - active_cases: Список UUID активних звернень (якщо деактивація заблокована)
    
    **Errors:**
    - 401: Не авторизований
    - 403: Недостатньо прав (потрібен ADMIN)
    - 404: Користувача не знайдено
    - 409: Користувач має активні звернення (якщо force=false)
    
    **Business Rules:**
    - EXECUTOR з активними зверненнями (IN_PROGRESS, NEEDS_INFO) не може бути деактивований без force=true
    - OPERATOR та ADMIN можуть бути деактивовані без перевірок
    - При force=true деактивація відбувається навіть при наявності активних звернень
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    success, error_msg, active_case_ids = crud.deactivate_user_with_check(
        db=db,
        user_id=user_uuid,
        force=force
    )
    
    if not success:
        if error_msg == "User not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        else:
            # Конфлікт через активні звернення
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg,
                headers={"X-Active-Cases": ",".join(active_case_ids or [])}
            )
    
    db_user = crud.get_user(db, user_uuid)
    
    return {
        "message": f"User '{db_user.username}' deactivated successfully",
        "user_id": str(user_uuid),
        "active_cases": None
    }


@router.post("/{user_id}/activate", response_model=schemas.UserResponse)
async def activate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Активувати користувача (ADMIN тільки).
    
    **Path Parameters:**
    - user_id: UUID користувача
    
    **Response:**
    - Оновлений користувач з is_active=True
    
    **Errors:**
    - 401: Не авторизований
    - 403: Недостатньо прав (потрібен ADMIN)
    - 404: Користувача не знайдено
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    db_user = crud.activate_user(db, user_uuid)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found"
        )
    
    return schemas.UserResponse(
        id=str(db_user.id),
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        role=db_user.role,
        is_active=db_user.is_active,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at
    )


@router.get("/{user_id}/active-cases", response_model=schemas.ActiveCasesResponse)
async def get_user_active_cases(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Отримати список активних звернень користувача (ADMIN тільки).
    
    **Path Parameters:**
    - user_id: UUID користувача
    
    **Response:**
    - user_id: UUID користувача
    - username: Ім'я користувача
    - active_cases_count: Кількість активних звернень
    - case_ids: Список UUID активних звернень
    
    **Errors:**
    - 401: Не авторизований
    - 403: Недостатньо прав (потрібен ADMIN)
    - 404: Користувача не знайдено
    
    **Note:**
    Активні звернення: статус IN_PROGRESS або NEEDS_INFO
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    db_user = crud.get_user(db, user_uuid)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found"
        )
    
    active_cases = crud.get_user_active_cases(db=db, user_id=user_uuid)
    
    return {
        "user_id": str(user_uuid),
        "username": db_user.username,
        "active_cases_count": len(active_cases),
        "case_ids": [str(case.id) for case in active_cases]
    }


# ============================================================================
# BE-018: Executor Category Access Management (ADMIN only)
# ============================================================================

@router.get("/{user_id}/category-access", response_model=schemas.ExecutorCategoriesListResponse)
async def get_executor_category_access(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    BE-018: Отримати список категорій до яких має доступ виконавець (ADMIN тільки).
    
    **Path Parameters:**
    - user_id: UUID користувача (має бути EXECUTOR)
    
    **Response:**
    - executor_id: UUID виконавця
    - executor_username: Ім'я користувача
    - total: Загальна кількість категорій з доступом
    - categories: Список категорій з деталями доступу
    
    **Errors:**
    - 400: Невалідний UUID формат
    - 401: Не авторизований
    - 403: Недостатньо прав (потрібен ADMIN)
    - 404: Користувача не знайдено
    
    **Note:**
    Повертає тільки категорії до яких виконавець має явний доступ.
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Перевірка що користувач існує
    db_user = crud.get_user(db, user_uuid)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found"
        )
    
    # Отримання доступів
    access_records = crud.get_executor_category_access(db=db, executor_id=user_uuid)
    
    # Формування відповіді
    categories_response = []
    for access in access_records:
        categories_response.append(schemas.CategoryAccessResponse(
            id=str(access.id),
            executor_id=str(access.executor_id),
            category_id=str(access.category_id),
            category_name=access.category.name if access.category else None,
            created_at=access.created_at,
            updated_at=access.updated_at
        ))
    
    return {
        "executor_id": str(user_uuid),
        "executor_username": db_user.username,
        "total": len(categories_response),
        "categories": categories_response
    }


@router.post("/{user_id}/category-access", response_model=schemas.ExecutorCategoriesListResponse, status_code=status.HTTP_201_CREATED)
async def add_executor_category_access(
    user_id: str,
    access_data: schemas.CategoryAccessCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    BE-018: Додати доступ виконавцю до категорій (ADMIN тільки).
    
    **Path Parameters:**
    - user_id: UUID користувача (має бути EXECUTOR)
    
    **Request Body:**
    - category_ids: Список UUID категорій для надання доступу
    
    **Response:**
    - executor_id: UUID виконавця
    - executor_username: Ім'я користувача
    - total: Загальна кількість категорій з доступом (після додавання)
    - categories: Оновлений список категорій з доступом
    
    **Errors:**
    - 400: Невалідний UUID або користувач не EXECUTOR
    - 401: Не авторизований
    - 403: Недостатньо прав (потрібен ADMIN)
    - 404: Користувача або категорію не знайдено
    - 422: Помилка валідації
    
    **Note:**
    - Масове додавання: можна додати кілька категорій одночасно
    - Якщо доступ вже існує, він буде пропущений (не помилка)
    - Транзакційність: всі або нічого
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Конвертація category_ids в UUID
    category_uuids = []
    for cat_id in access_data.category_ids:
        try:
            category_uuids.append(UUID(cat_id))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category ID format: {cat_id}"
            )
    
    try:
        # Додавання доступів
        created_records, error_messages = crud.add_executor_category_access(
            db=db,
            executor_id=user_uuid,
            category_ids=category_uuids
        )
        
        # Отримання оновленого списку всіх доступів
        all_access = crud.get_executor_category_access(db=db, executor_id=user_uuid)
        
        # Отримання інформації про користувача
        db_user = crud.get_user(db, user_uuid)
        
        # Формування відповіді
        categories_response = []
        for access in all_access:
            categories_response.append(schemas.CategoryAccessResponse(
                id=str(access.id),
                executor_id=str(access.executor_id),
                category_id=str(access.category_id),
                category_name=access.category.name if access.category else None,
                created_at=access.created_at,
                updated_at=access.updated_at
            ))
        
        return {
            "executor_id": str(user_uuid),
            "executor_username": db_user.username,
            "total": len(categories_response),
            "categories": categories_response
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}/category-access/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_executor_category_access(
    user_id: str,
    category_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    BE-018: Видалити доступ виконавця до конкретної категорії (ADMIN тільки).
    
    **Path Parameters:**
    - user_id: UUID користувача
    - category_id: UUID категорії
    
    **Response:**
    - 204 No Content (успішне видалення)
    
    **Errors:**
    - 400: Невалідний UUID формат
    - 401: Не авторизований
    - 403: Недостатньо прав (потрібен ADMIN)
    - 404: Доступ не знайдено
    
    **Note:**
    Якщо доступ не існував, повертає 404.
    """
    try:
        user_uuid = UUID(user_id)
        category_uuid = UUID(category_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID or category ID format"
        )
    
    # Видалення доступу
    success = crud.remove_executor_category_access(
        db=db,
        executor_id=user_uuid,
        category_id=category_uuid
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category access not found for user '{user_id}' and category '{category_id}'"
        )
    
    return None  # 204 No Content


@router.put("/{user_id}/category-access", response_model=schemas.ExecutorCategoriesListResponse)
async def replace_executor_category_access(
    user_id: str,
    access_data: schemas.CategoryAccessUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    BE-018: Замінити всі доступи виконавця новим списком категорій (ADMIN тільки).
    
    **Path Parameters:**
    - user_id: UUID користувача (має бути EXECUTOR)
    
    **Request Body:**
    - category_ids: Новий список UUID категорій (замінює всі існуючі)
    
    **Response:**
    - executor_id: UUID виконавця
    - executor_username: Ім'я користувача
    - total: Загальна кількість категорій з доступом (після заміни)
    - categories: Новий список категорій з доступом
    
    **Errors:**
    - 400: Невалідний UUID або користувач не EXECUTOR
    - 401: Не авторизований
    - 403: Недостатньо прав (потрібен ADMIN)
    - 404: Користувача або категорію не знайдено
    - 422: Помилка валідації
    
    **Note:**
    - Видаляє ВСІ існуючі доступи та створює нові
    - Транзакційність: всі або нічого
    - Якщо category_ids порожній список, видаляє всі доступи
    """
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Конвертація category_ids в UUID
    category_uuids = []
    for cat_id in access_data.category_ids:
        try:
            category_uuids.append(UUID(cat_id))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category ID format: {cat_id}"
            )
    
    try:
        # Заміна всіх доступів
        new_records, deleted_count = crud.replace_executor_category_access(
            db=db,
            executor_id=user_uuid,
            category_ids=category_uuids
        )
        
        # Отримання інформації про користувача
        db_user = crud.get_user(db, user_uuid)
        
        # Формування відповіді
        categories_response = []
        for access in new_records:
            # Завантаження category для отримання назви
            access_with_category = crud.get_executor_category_access(db=db, executor_id=user_uuid)
            for acc in access_with_category:
                if acc.id == access.id:
                    categories_response.append(schemas.CategoryAccessResponse(
                        id=str(acc.id),
                        executor_id=str(acc.executor_id),
                        category_id=str(acc.category_id),
                        category_name=acc.category.name if acc.category else None,
                        created_at=acc.created_at,
                        updated_at=acc.updated_at
                    ))
                    break
        
        return {
            "executor_id": str(user_uuid),
            "executor_username": db_user.username,
            "total": len(categories_response),
            "categories": categories_response
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
