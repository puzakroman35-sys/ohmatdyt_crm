"""
BE-301: Dashboard Analytics API Endpoints

Provides statistics and aggregated data for admin dashboard:
- Summary statistics
- Status distribution
- Overdue cases list
- Executors efficiency metrics
- Top categories by case count

All endpoints are ADMIN-only (RBAC enforced).
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.database import get_db
from app.dependencies import get_current_active_user

router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"]
)


def require_admin(current_user: models.User = Depends(get_current_active_user)) -> models.User:
    """
    Dependency для перевірки що користувач має роль ADMIN.
    
    Raises:
        HTTPException: 403 якщо користувач не є адміністратором
    """
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only administrators can access dashboard analytics."
        )
    return current_user


@router.get("/summary", response_model=schemas.DashboardSummaryResponse)
async def get_dashboard_summary(
    date_from: Optional[str] = Query(
        None,
        description="Start date for filtering (ISO format, e.g., 2025-01-01T00:00:00)"
    ),
    date_to: Optional[str] = Query(
        None,
        description="End date for filtering (ISO format, e.g., 2025-12-31T23:59:59)"
    ),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Отримати загальну статистику звернень для дашборду.
    
    **Доступ:** Тільки ADMIN
    
    **Повертає:**
    - Загальну кількість звернень
    - Кількість по кожному статусу (NEW, IN_PROGRESS, NEEDS_INFO, REJECTED, DONE)
    - Період фільтрації (якщо вказаний)
    
    **Параметри:**
    - `date_from`: Початок періоду (необов'язково)
    - `date_to`: Кінець періоду (необов'язково)
    
    Якщо період не вказано - рахує всі звернення в системі.
    """
    try:
        summary = crud.get_dashboard_summary(
            db=db,
            date_from=date_from,
            date_to=date_to
        )
        return summary
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard summary: {str(e)}"
        )


@router.get("/status-distribution", response_model=schemas.StatusDistributionResponse)
async def get_status_distribution(
    date_from: Optional[str] = Query(
        None,
        description="Start date for filtering (ISO format)"
    ),
    date_to: Optional[str] = Query(
        None,
        description="End date for filtering (ISO format)"
    ),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Отримати розподіл звернень по статусах.
    
    **Доступ:** Тільки ADMIN
    
    **Повертає:**
    - Загальну кількість звернень
    - Розподіл по статусах з кількістю та відсотками
    - Період фільтрації
    
    **Використання:**
    Дані ідеально підходять для pie chart (кругова діаграма) або bar chart.
    """
    try:
        distribution = crud.get_status_distribution(
            db=db,
            date_from=date_from,
            date_to=date_to
        )
        return distribution
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status distribution: {str(e)}"
        )


@router.get("/overdue-cases", response_model=schemas.OverdueCasesResponse)
async def get_overdue_cases(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Отримати список прострочених звернень.
    
    **Доступ:** Тільки ADMIN
    
    **Критерій прострочення:**
    Звернення в статусі NEW більше 3 календарних днів.
    
    **Повертає:**
    - Загальну кількість прострочених звернень
    - Детальний список з інформацією:
      - ID та public_id звернення
      - Категорія
      - Ім'я заявника
      - Дата створення
      - Кількість днів прострочення
      - Відповідальний виконавець (якщо призначений)
    
    **Сортування:** За датою створення (від найстаріших до найновіших)
    
    **Використання:**
    Для виджету "Прострочені звернення" на дашборді адміністратора.
    """
    try:
        overdue = crud.get_overdue_cases(db=db)
        return overdue
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get overdue cases: {str(e)}"
        )


@router.get("/executors-efficiency", response_model=schemas.ExecutorEfficiencyResponse)
async def get_executors_efficiency(
    date_from: Optional[str] = Query(
        None,
        description="Start date for completed cases filtering (ISO format)"
    ),
    date_to: Optional[str] = Query(
        None,
        description="End date for completed cases filtering (ISO format)"
    ),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Отримати статистику ефективності виконавців.
    
    **Доступ:** Тільки ADMIN
    
    **Повертає для кожного виконавця:**
    - ПІБ та email
    - Список категорій, до яких має доступ
    - Кількість звернень в роботі зараз (статус IN_PROGRESS)
    - Кількість завершених звернень в періоді
    - Середній час виконання звернення (в днях)
    - Кількість прострочених звернень (>3 днів в NEW)
    
    **Параметри:**
    - `date_from`, `date_to`: Період для підрахунку завершених звернень
    
    **Використання:**
    Для таблиці "Ефективність виконавців" на дашборді.
    Можна сортувати за будь-якою колонкою на фронтенді.
    """
    try:
        efficiency = crud.get_executors_efficiency(
            db=db,
            date_from=date_from,
            date_to=date_to
        )
        return efficiency
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get executors efficiency: {str(e)}"
        )


@router.get("/categories-top", response_model=schemas.CategoriesTopResponse)
async def get_top_categories(
    date_from: Optional[str] = Query(
        None,
        description="Start date for filtering (ISO format)"
    ),
    date_to: Optional[str] = Query(
        None,
        description="End date for filtering (ISO format)"
    ),
    limit: int = Query(
        5,
        ge=1,
        le=20,
        description="Number of top categories to return (1-20, default 5)"
    ),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Отримати ТОП категорій по кількості звернень.
    
    **Доступ:** Тільки ADMIN
    
    **Повертає для кожної категорії в ТОП:**
    - Назва категорії
    - Загальна кількість звернень
    - Кількість нових (NEW)
    - Кількість в роботі (IN_PROGRESS)
    - Кількість завершених (DONE)
    - Відсоток від загальної кількості звернень
    
    **Параметри:**
    - `limit`: Кількість категорій в топі (1-20, за замовчуванням 5)
    - `date_from`, `date_to`: Період для фільтрації
    
    **Сортування:** За кількістю звернень (від більшого до меншого)
    
    **Використання:**
    Для віджету "Розподіл звернень за категоріями" (bar chart).
    """
    try:
        top_categories = crud.get_top_categories(
            db=db,
            date_from=date_from,
            date_to=date_to,
            limit=limit
        )
        return top_categories
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameters: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top categories: {str(e)}"
        )
