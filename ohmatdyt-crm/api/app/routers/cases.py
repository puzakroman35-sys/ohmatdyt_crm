"""
Case API endpoints with multipart support for file uploads
"""
import os
import uuid as uuid_lib
from typing import Optional, List
from uuid import UUID
from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    status, 
    UploadFile, 
    File, 
    Form
)
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.database import get_db
from app.dependencies import get_current_active_user, require_admin
from app.utils import (
    validate_file_type,
    validate_file_size,
    get_file_storage_path,
    sanitize_filename,
)

router = APIRouter(
    prefix="/api/cases",
    tags=["cases"]
)


def get_media_root() -> str:
    """Get MEDIA_ROOT from environment or use default"""
    return os.getenv("MEDIA_ROOT", "/var/app/media")


@router.post("", response_model=schemas.CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case_with_attachments(
    # Required fields
    category_id: str = Form(..., description="UUID of the category"),
    channel_id: str = Form(..., description="UUID of the channel"),
    applicant_name: str = Form(..., min_length=1, max_length=200, description="Name of the applicant"),
    summary: str = Form(..., min_length=1, description="Case summary/description"),
    
    # Optional fields
    subcategory: Optional[str] = Form(None, max_length=200, description="Optional subcategory"),
    applicant_phone: Optional[str] = Form(None, max_length=50, description="Phone number of the applicant"),
    applicant_email: Optional[str] = Form(None, description="Email of the applicant"),
    
    # File uploads
    files: List[UploadFile] = File(default=[], description="Attachments (optional)"),
    
    # Dependencies
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new case with optional file attachments.
    
    This endpoint accepts multipart/form-data with:
    - Required: category_id, channel_id, applicant_name, summary
    - Optional: subcategory, applicant_phone, applicant_email, files[]
    
    Files:
    - Allowed types: pdf, doc, docx, xls, xlsx, jpg, jpeg, png
    - Maximum size per file: 10MB
    - Files are stored in: MEDIA_ROOT/cases/{public_id}/
    
    Only OPERATOR role can create cases.
    After creation, triggers email notification to executors of the category.
    
    Returns created case with status=NEW and unique 6-digit public_id.
    """
    # Check RBAC: Only OPERATOR can create cases
    if current_user.role != models.UserRole.OPERATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only operators can create cases"
        )
    
    # Validate file uploads (if any)
    validated_files = []
    if files:
        for file in files:
            # Skip empty files
            if not file.filename:
                continue
                
            # Read file content to validate size
            file_content = await file.read()
            file_size = len(file_content)
            
            # Reset file pointer for later use
            await file.seek(0)
            
            # Validate file size
            is_valid_size, size_error = validate_file_size(file_size)
            if not is_valid_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File '{file.filename}': {size_error}"
                )
            
            # Validate file type
            content_type = file.content_type or "application/octet-stream"
            is_valid_type, type_error = validate_file_type(file.filename, content_type)
            if not is_valid_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File '{file.filename}': {type_error}"
                )
            
            validated_files.append({
                'file': file,
                'content': file_content,
                'size': file_size,
                'mime_type': content_type
            })
    
    # Create case using existing CRUD
    try:
        case_create = schemas.CaseCreate(
            category_id=category_id,
            channel_id=channel_id,
            subcategory=subcategory,
            applicant_name=applicant_name,
            applicant_phone=applicant_phone,
            applicant_email=applicant_email,
            summary=summary,
            responsible_id=None  # Will be assigned later
        )
        
        db_case = await crud.create_case(db, case_create, current_user.id)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Save and attach files to the case
    attachment_responses = []
    if validated_files:
        media_root = get_media_root()
        
        for file_data in validated_files:
            file = file_data['file']
            file_content = file_data['content']
            file_size = file_data['size']
            mime_type = file_data['mime_type']
            
            # Sanitize filename and generate storage path
            safe_filename = sanitize_filename(file.filename)
            
            # Add UUID prefix to avoid name collisions
            unique_filename = f"{uuid_lib.uuid4().hex[:8]}_{safe_filename}"
            
            # Get relative path for storage
            relative_path = get_file_storage_path(db_case.public_id, unique_filename)
            
            # Create full path
            full_path = os.path.join(media_root, relative_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Save file to disk
            try:
                with open(full_path, "wb") as f:
                    f.write(file_content)
            except Exception as e:
                # Rollback: delete case if file save fails
                await crud.delete_case(db, db_case.id)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to save file '{file.filename}': {str(e)}"
                )
            
            # Create database record for attachment
            try:
                db_attachment = await crud.create_attachment(
                    db=db,
                    case_id=db_case.id,
                    file_path=relative_path,
                    original_name=file.filename,
                    size_bytes=file_size,
                    mime_type=mime_type,
                    uploaded_by_id=current_user.id
                )
                
                attachment_responses.append(db_attachment)
                
            except ValueError as e:
                # Clean up file if database record creation fails
                if os.path.exists(full_path):
                    os.remove(full_path)
                # Continue with other files, but log error
                print(f"Warning: Failed to create attachment record for '{file.filename}': {str(e)}")
    
    # Trigger email notification to executors (async via Celery)
    try:
        from app.celery_app import send_new_case_notification
        
        # Queue notification task
        send_new_case_notification.delay(
            case_id=str(db_case.id),
            case_public_id=db_case.public_id,
            category_id=str(db_case.category_id)
        )
        
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Failed to queue notification task: {str(e)}")
    
    # Return created case
    return schemas.CaseResponse(
        id=str(db_case.id),
        public_id=db_case.public_id,
        category_id=str(db_case.category_id),
        channel_id=str(db_case.channel_id),
        subcategory=db_case.subcategory,
        applicant_name=db_case.applicant_name,
        applicant_phone=db_case.applicant_phone,
        applicant_email=db_case.applicant_email,
        summary=db_case.summary,
        status=db_case.status,
        author_id=str(db_case.author_id),
        responsible_id=str(db_case.responsible_id) if db_case.responsible_id else None,
        created_at=db_case.created_at,
        updated_at=db_case.updated_at
    )


@router.get("/my", response_model=schemas.CaseListResponse)
async def list_my_cases(
    skip: int = 0,
    limit: int = 50,
    status: Optional[models.CaseStatus] = None,
    category_id: Optional[UUID] = None,
    channel_id: Optional[UUID] = None,
    public_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    overdue: Optional[bool] = None,
    order_by: Optional[str] = "-created_at",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    List cases created by current OPERATOR.
    
    This endpoint is specifically for OPERATOR role to see their own cases.
    
    Query params:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 50, max: 100)
    - status: Filter by case status
    - category_id: Filter by category
    - channel_id: Filter by channel
    - public_id: Filter by 6-digit public ID
    - date_from: Filter by created date from (ISO format)
    - date_to: Filter by created date to (ISO format)
    - overdue: Filter overdue cases (true/false)
    - order_by: Sort field (prefix with - for descending, e.g., -created_at)
    
    RBAC: OPERATOR only (shows own cases)
    """
    # Only OPERATOR can use this endpoint
    if current_user.role != models.UserRole.OPERATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only for OPERATOR role. Use /api/cases or /api/cases/assigned instead."
        )
    
    if limit > 100:
        limit = 100
    
    # Force author_id to current user
    cases, total = await crud.get_all_cases(
        db=db,
        status=status,
        category_id=category_id,
        channel_id=channel_id,
        author_id=current_user.id,  # Always filter by current user
        public_id=public_id,
        date_from=date_from,
        date_to=date_to,
        overdue=overdue,
        order_by=order_by,
        skip=skip,
        limit=limit
    )
    
    # Convert to response schemas
    case_responses = [
        schemas.CaseResponse(
            id=str(case.id),
            public_id=case.public_id,
            category_id=str(case.category_id),
            channel_id=str(case.channel_id),
            subcategory=case.subcategory,
            applicant_name=case.applicant_name,
            applicant_phone=case.applicant_phone,
            applicant_email=case.applicant_email,
            summary=case.summary,
            status=case.status,
            author_id=str(case.author_id),
            responsible_id=str(case.responsible_id) if case.responsible_id else None,
            created_at=case.created_at,
            updated_at=case.updated_at
        )
        for case in cases
    ]
    
    return {
        "cases": case_responses,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit
    }


@router.get("/assigned", response_model=schemas.CaseListResponse)
async def list_assigned_cases(
    skip: int = 0,
    limit: int = 50,
    status: Optional[models.CaseStatus] = None,
    category_id: Optional[UUID] = None,
    channel_id: Optional[UUID] = None,
    public_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    overdue: Optional[bool] = None,
    order_by: Optional[str] = "-created_at",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    List cases assigned to current EXECUTOR.
    
    This endpoint shows cases that are:
    - Assigned to current executor (responsible_id = current_user)
    - Or cases in categories where executor has access (future enhancement)
    
    Query params:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 50, max: 100)
    - status: Filter by case status
    - category_id: Filter by category
    - channel_id: Filter by channel
    - public_id: Filter by 6-digit public ID
    - date_from: Filter by created date from (ISO format)
    - date_to: Filter by created date to (ISO format)
    - overdue: Filter overdue cases (true/false)
    - order_by: Sort field (prefix with - for descending, e.g., -created_at)
    
    RBAC: EXECUTOR/ADMIN only
    """
    # Only EXECUTOR and ADMIN can use this endpoint
    if current_user.role not in [models.UserRole.EXECUTOR, models.UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only for EXECUTOR or ADMIN roles."
        )
    
    if limit > 100:
        limit = 100
    
    # For EXECUTOR: show only assigned cases
    # For ADMIN: show all assigned to them (or could show all - configurable)
    responsible_filter = current_user.id if current_user.role == models.UserRole.EXECUTOR else None
    
    cases, total = await crud.get_all_cases(
        db=db,
        status=status,
        category_id=category_id,
        channel_id=channel_id,
        responsible_id=responsible_filter,
        public_id=public_id,
        date_from=date_from,
        date_to=date_to,
        overdue=overdue,
        order_by=order_by,
        skip=skip,
        limit=limit
    )
    
    # Convert to response schemas
    case_responses = [
        schemas.CaseResponse(
            id=str(case.id),
            public_id=case.public_id,
            category_id=str(case.category_id),
            channel_id=str(case.channel_id),
            subcategory=case.subcategory,
            applicant_name=case.applicant_name,
            applicant_phone=case.applicant_phone,
            applicant_email=case.applicant_email,
            summary=case.summary,
            status=case.status,
            author_id=str(case.author_id),
            responsible_id=str(case.responsible_id) if case.responsible_id else None,
            created_at=case.created_at,
            updated_at=case.updated_at
        )
        for case in cases
    ]
    
    return {
        "cases": case_responses,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit
    }


@router.get("/{case_id}", response_model=schemas.CaseResponse)
async def get_case(
    case_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get case by ID.
    
    RBAC:
    - OPERATOR: can view own cases
    - EXECUTOR/ADMIN: can view all cases
    """
    db_case = await crud.get_case(db, case_id)
    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with id '{case_id}' not found"
        )
    
    # Check RBAC permissions
    if current_user.role == models.UserRole.OPERATOR and db_case.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this case"
        )
    
    return schemas.CaseResponse(
        id=str(db_case.id),
        public_id=db_case.public_id,
        category_id=str(db_case.category_id),
        channel_id=str(db_case.channel_id),
        subcategory=db_case.subcategory,
        applicant_name=db_case.applicant_name,
        applicant_phone=db_case.applicant_phone,
        applicant_email=db_case.applicant_email,
        summary=db_case.summary,
        status=db_case.status,
        author_id=str(db_case.author_id),
        responsible_id=str(db_case.responsible_id) if db_case.responsible_id else None,
        created_at=db_case.created_at,
        updated_at=db_case.updated_at
    )


@router.get("", response_model=schemas.CaseListResponse)
async def list_cases(
    skip: int = 0,
    limit: int = 50,
    status: Optional[models.CaseStatus] = None,
    category_id: Optional[UUID] = None,
    channel_id: Optional[UUID] = None,
    responsible_id: Optional[UUID] = None,
    public_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    overdue: Optional[bool] = None,
    order_by: Optional[str] = "-created_at",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    List all cases with filtering and pagination.
    
    RBAC:
    - OPERATOR: can list only own cases (redirected to /my)
    - EXECUTOR: can list assigned cases (consider using /assigned)
    - ADMIN: can list all cases
    
    Query params:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 50, max: 100)
    - status: Filter by case status (NEW, IN_PROGRESS, NEEDS_INFO, REJECTED, DONE)
    - category_id: Filter by category UUID
    - channel_id: Filter by channel UUID
    - responsible_id: Filter by responsible executor UUID
    - public_id: Filter by 6-digit public ID
    - date_from: Filter by created date from (ISO format: 2025-10-28T00:00:00)
    - date_to: Filter by created date to (ISO format: 2025-10-28T23:59:59)
    - overdue: Filter overdue cases (true/false, based on 7-day threshold)
    - order_by: Sort field (prefix with - for descending)
                Supported: created_at, updated_at, public_id, status
                Examples: -created_at (newest first), created_at (oldest first)
    
    All filters use AND logic.
    """
    if limit > 100:
        limit = 100
    
    # Apply RBAC: operators can only see own cases
    author_id = None
    if current_user.role == models.UserRole.OPERATOR:
        author_id = current_user.id
    
    cases, total = await crud.get_all_cases(
        db=db,
        status=status,
        category_id=category_id,
        channel_id=channel_id,
        author_id=author_id,
        responsible_id=responsible_id,
        public_id=public_id,
        date_from=date_from,
        date_to=date_to,
        overdue=overdue,
        order_by=order_by,
        skip=skip,
        limit=limit
    )
    
    # Convert to response schemas
    case_responses = [
        schemas.CaseResponse(
            id=str(case.id),
            public_id=case.public_id,
            category_id=str(case.category_id),
            channel_id=str(case.channel_id),
            subcategory=case.subcategory,
            applicant_name=case.applicant_name,
            applicant_phone=case.applicant_phone,
            applicant_email=case.applicant_email,
            summary=case.summary,
            status=case.status,
            author_id=str(case.author_id),
            responsible_id=str(case.responsible_id) if case.responsible_id else None,
            created_at=case.created_at,
            updated_at=case.updated_at
        )
        for case in cases
    ]
    
    return {
        "cases": case_responses,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit
    }
