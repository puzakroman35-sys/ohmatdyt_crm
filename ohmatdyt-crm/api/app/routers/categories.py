"""
Categories API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app import schemas, crud
from app.database import get_db
from app.dependencies import require_admin
from app.models import User

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=schemas.CategoryListResponse)
async def list_categories(
    include_inactive: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of categories.
    
    Query params:
    - include_inactive: Include inactive categories (default: false)
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100)
    
    Returns only active categories by default.
    """
    if limit > 100:
        limit = 100
    
    db_categories = await crud.get_categories(
        db, 
        skip=skip, 
        limit=limit,
        include_inactive=include_inactive
    )
    
    # Convert to response schemas
    categories = [
        schemas.CategoryResponse(
            id=str(cat.id),
            name=cat.name,
            is_active=cat.is_active,
            created_at=cat.created_at,
            updated_at=cat.updated_at
        )
        for cat in db_categories
    ]
    
    return {
        "categories": categories,
        "total": len(categories)
    }


@router.post("", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new category.
    
    Requires: Admin privileges
    
    Request:
    - name: Category name (unique, 1-200 characters)
    
    Returns created category.
    """
    try:
        db_category = await crud.create_category(db, category)
        
        return schemas.CategoryResponse(
            id=str(db_category.id),
            name=db_category.name,
            is_active=db_category.is_active,
            created_at=db_category.created_at,
            updated_at=db_category.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{category_id}", response_model=schemas.CategoryResponse)
async def get_category(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get category by ID.
    
    Returns category details.
    """
    db_category = await crud.get_category(db, category_id)
    
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return schemas.CategoryResponse(
        id=str(db_category.id),
        name=db_category.name,
        is_active=db_category.is_active,
        created_at=db_category.created_at,
        updated_at=db_category.updated_at
    )


@router.put("/{category_id}", response_model=schemas.CategoryResponse)
async def update_category(
    category_id: UUID,
    category_update: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update category.
    
    Requires: Admin privileges
    
    Request:
    - name: New category name (optional)
    
    Returns updated category.
    """
    try:
        db_category = await crud.update_category(db, category_id, category_update)
        
        if not db_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return schemas.CategoryResponse(
            id=str(db_category.id),
            name=db_category.name,
            is_active=db_category.is_active,
            created_at=db_category.created_at,
            updated_at=db_category.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{category_id}/deactivate", response_model=schemas.CategoryResponse)
async def deactivate_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Deactivate category.
    
    Requires: Admin privileges
    
    Deactivated categories will not be available for selection
    when creating new requests.
    
    Returns updated category.
    """
    db_category = await crud.deactivate_category(db, category_id)
    
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return schemas.CategoryResponse(
        id=str(db_category.id),
        name=db_category.name,
        is_active=db_category.is_active,
        created_at=db_category.created_at,
        updated_at=db_category.updated_at
    )


@router.post("/{category_id}/activate", response_model=schemas.CategoryResponse)
async def activate_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Activate category.
    
    Requires: Admin privileges
    
    Activated categories will be available for selection
    when creating new requests.
    
    Returns updated category.
    """
    db_category = await crud.activate_category(db, category_id)
    
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return schemas.CategoryResponse(
        id=str(db_category.id),
        name=db_category.name,
        is_active=db_category.is_active,
        created_at=db_category.created_at,
        updated_at=db_category.updated_at
    )
