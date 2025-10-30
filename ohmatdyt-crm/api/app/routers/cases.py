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
from app import utils

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
    
    Any authenticated user can create cases.
    After creation, triggers email notification to executors of the category.
    
    Returns created case with status=NEW and unique 6-digit public_id.
    """
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
            is_valid_size, size_error = utils.validate_file_size(file_size)
            if not is_valid_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File '{file.filename}': {size_error}"
                )
            
            # Validate file type
            content_type = file.content_type or "application/octet-stream"
            is_valid_type, type_error = utils.validate_file_type(file.filename, content_type)
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
        
        db_case = crud.create_case(db, case_create, current_user.id)
        
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
            safe_filename = utils.sanitize_filename(file.filename)
            
            # Add UUID prefix to avoid name collisions
            unique_filename = f"{uuid_lib.uuid4().hex[:8]}_{safe_filename}"
            
            # Get relative path for storage
            relative_path = utils.get_file_storage_path(db_case.public_id, unique_filename)
            
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
                crud.delete_case(db, db_case.id)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to save file '{file.filename}': {str(e)}"
                )
            
            # Create database record for attachment
            try:
                db_attachment = crud.create_attachment(
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
    # BE-201: Extended filters
    subcategory: Optional[str] = None,
    applicant_name: Optional[str] = None,
    applicant_phone: Optional[str] = None,
    applicant_email: Optional[str] = None,
    updated_date_from: Optional[str] = None,
    updated_date_to: Optional[str] = None,
    statuses: Optional[str] = None,
    category_ids: Optional[str] = None,
    channel_ids: Optional[str] = None,
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
    
    BE-201: Extended filters (all use AND logic):
    - subcategory: Filter by subcategory (exact match or use % for LIKE search)
    - applicant_name: Search in applicant name (case-insensitive partial match)
    - applicant_phone: Search in applicant phone (partial match)
    - applicant_email: Search in applicant email (case-insensitive partial match)
    - updated_date_from: Filter by updated date from (ISO format)
    - updated_date_to: Filter by updated date to (ISO format)
    - statuses: Multiple statuses separated by comma (e.g., "NEW,IN_PROGRESS")
    - category_ids: Multiple category UUIDs separated by comma
    - channel_ids: Multiple channel UUIDs separated by comma
    
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
    
    # BE-201: Parse comma-separated lists
    parsed_statuses = None
    if statuses:
        try:
            parsed_statuses = [models.CaseStatus(s.strip()) for s in statuses.split(',') if s.strip()]
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status value in statuses parameter: {str(e)}"
            )
    
    parsed_category_ids = None
    if category_ids:
        try:
            parsed_category_ids = [UUID(cid.strip()) for cid in category_ids.split(',') if cid.strip()]
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid UUID in category_ids parameter: {str(e)}"
            )
    
    parsed_channel_ids = None
    if channel_ids:
        try:
            parsed_channel_ids = [UUID(chid.strip()) for chid in channel_ids.split(',') if chid.strip()]
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid UUID in channel_ids parameter: {str(e)}"
            )
    
    # Force author_id to current user
    cases, total = crud.get_all_cases(
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
        limit=limit,
        # BE-201: Extended filters
        subcategory=subcategory,
        applicant_name=applicant_name,
        applicant_phone=applicant_phone,
        applicant_email=applicant_email,
        updated_date_from=updated_date_from,
        updated_date_to=updated_date_to,
        statuses=parsed_statuses,
        category_ids=parsed_category_ids,
        channel_ids=parsed_channel_ids
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
            updated_at=case.updated_at,
            # Add nested objects for frontend
            category=schemas.CategoryResponse(
                id=str(case.category.id),
                name=case.category.name,
                is_active=case.category.is_active,
                created_at=case.category.created_at,
                updated_at=case.category.updated_at
            ) if case.category else None,
            channel=schemas.ChannelResponse(
                id=str(case.channel.id),
                name=case.channel.name,
                is_active=case.channel.is_active,
                created_at=case.channel.created_at,
                updated_at=case.channel.updated_at
            ) if case.channel else None,
            responsible=schemas.UserResponse(
                id=str(case.responsible.id),
                username=case.responsible.username,
                email=case.responsible.email,
                full_name=case.responsible.full_name,
                role=case.responsible.role,
                is_active=case.responsible.is_active,
                created_at=case.responsible.created_at,
                updated_at=case.responsible.updated_at
            ) if case.responsible else None
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
    # BE-201: Extended filters
    subcategory: Optional[str] = None,
    applicant_name: Optional[str] = None,
    applicant_phone: Optional[str] = None,
    applicant_email: Optional[str] = None,
    updated_date_from: Optional[str] = None,
    updated_date_to: Optional[str] = None,
    statuses: Optional[str] = None,
    category_ids: Optional[str] = None,
    channel_ids: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    List cases assigned to current EXECUTOR.
    
    BE-016: This endpoint shows cases according to executor visibility rules:
    - For EXECUTOR: All NEW cases (available to take) OR cases assigned to executor
    - For ADMIN: Only cases assigned to admin (can use /api/cases for all cases)
    
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
    
    BE-201: Extended filters (all use AND logic):
    - subcategory: Filter by subcategory (exact match or use % for LIKE search)
    - applicant_name: Search in applicant name (case-insensitive partial match)
    - applicant_phone: Search in applicant phone (partial match)
    - applicant_email: Search in applicant email (case-insensitive partial match)
    - updated_date_from: Filter by updated date from (ISO format)
    - updated_date_to: Filter by updated date to (ISO format)
    - statuses: Multiple statuses separated by comma (e.g., "NEW,IN_PROGRESS")
    - category_ids: Multiple category UUIDs separated by comma
    - channel_ids: Multiple channel UUIDs separated by comma
    
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
    
    # BE-201: Parse comma-separated lists
    parsed_statuses = None
    if statuses:
        try:
            parsed_statuses = [models.CaseStatus(s.strip()) for s in statuses.split(',') if s.strip()]
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status value in statuses parameter: {str(e)}"
            )
    
    parsed_category_ids = None
    if category_ids:
        try:
            parsed_category_ids = [UUID(cid.strip()) for cid in category_ids.split(',') if cid.strip()]
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid UUID in category_ids parameter: {str(e)}"
            )
    
    parsed_channel_ids = None
    if channel_ids:
        try:
            parsed_channel_ids = [UUID(chid.strip()) for chid in channel_ids.split(',') if chid.strip()]
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid UUID in channel_ids parameter: {str(e)}"
            )
    
    # BE-016: For EXECUTOR: show NEW cases OR assigned cases
    # For ADMIN: show all assigned to them
    if current_user.role == models.UserRole.EXECUTOR:
        # Use specialized function for executors (BE-016 rules)
        cases, total = crud.get_executor_cases(
            db=db,
            executor_id=current_user.id,
            status=status,
            category_id=category_id,
            channel_id=channel_id,
            public_id=public_id,
            date_from=date_from,
            date_to=date_to,
            overdue=overdue,
            order_by=order_by,
            skip=skip,
            limit=limit,
            # BE-201: Extended filters
            subcategory=subcategory,
            applicant_name=applicant_name,
            applicant_phone=applicant_phone,
            applicant_email=applicant_email,
            updated_date_from=updated_date_from,
            updated_date_to=updated_date_to,
            statuses=parsed_statuses,
            category_ids=parsed_category_ids,
            channel_ids=parsed_channel_ids
        )
    else:
        # For ADMIN: show assigned cases
        responsible_filter = current_user.id
        cases, total = crud.get_all_cases(
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
            limit=limit,
            # BE-201: Extended filters
            subcategory=subcategory,
            applicant_name=applicant_name,
            applicant_phone=applicant_phone,
            applicant_email=applicant_email,
            updated_date_from=updated_date_from,
            updated_date_to=updated_date_to,
            statuses=parsed_statuses,
            category_ids=parsed_category_ids,
            channel_ids=parsed_channel_ids
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
            updated_at=case.updated_at,
            # Add nested objects for frontend
            category=schemas.CategoryResponse(
                id=str(case.category.id),
                name=case.category.name,
                is_active=case.category.is_active,
                created_at=case.category.created_at,
                updated_at=case.category.updated_at
            ) if case.category else None,
            channel=schemas.ChannelResponse(
                id=str(case.channel.id),
                name=case.channel.name,
                is_active=case.channel.is_active,
                created_at=case.channel.created_at,
                updated_at=case.channel.updated_at
            ) if case.channel else None,
            responsible=schemas.UserResponse(
                id=str(case.responsible.id),
                username=case.responsible.username,
                email=case.responsible.email,
                full_name=case.responsible.full_name,
                role=case.responsible.role,
                is_active=case.responsible.is_active,
                created_at=case.responsible.created_at,
                updated_at=case.responsible.updated_at
            ) if case.responsible else None
        )
        for case in cases
    ]
    
    return {
        "cases": case_responses,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit
    }


@router.get("/{case_id}", response_model=schemas.CaseDetailResponse)
async def get_case(
    case_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get detailed case information by ID.
    
    Returns complete case information including:
    - Case details with category, channel, author, responsible
    - Status change history
    - Comments (filtered by visibility rules)
    - Attachments
    
    Comment visibility rules:
    - Public comments: Visible to case author (OPERATOR), responsible executor, and ADMIN
    - Internal comments: Visible only to EXECUTOR and ADMIN
    
    RBAC:
    - OPERATOR: can view own cases
    - EXECUTOR/ADMIN: can view all cases
    """
    db_case = crud.get_case(db, case_id)
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
    
    # Get category details
    category = crud.get_category(db, db_case.category_id)
    category_response = schemas.CategoryResponse(
        id=str(category.id),
        name=category.name,
        is_active=category.is_active,
        created_at=category.created_at,
        updated_at=category.updated_at
    )
    
    # Get channel details
    channel = crud.get_channel(db, db_case.channel_id)
    channel_response = schemas.ChannelResponse(
        id=str(channel.id),
        name=channel.name,
        is_active=channel.is_active,
        created_at=channel.created_at,
        updated_at=channel.updated_at
    )
    
    # Get author details
    author = crud.get_user(db, db_case.author_id)
    author_response = schemas.UserResponse(
        id=str(author.id),
        username=author.username,
        email=author.email,
        full_name=author.full_name,
        role=author.role,
        is_active=author.is_active,
        created_at=author.created_at,
        updated_at=author.updated_at
    )
    
    # Get responsible details (if assigned)
    responsible_response = None
    if db_case.responsible_id:
        responsible = crud.get_user(db, db_case.responsible_id)
        if responsible:
            responsible_response = schemas.UserResponse(
                id=str(responsible.id),
                username=responsible.username,
                email=responsible.email,
                full_name=responsible.full_name,
                role=responsible.role,
                is_active=responsible.is_active,
                created_at=responsible.created_at,
                updated_at=responsible.updated_at
            )
    
    # Get status history
    status_history = crud.get_status_history(db, db_case.id)
    status_history_responses = []
    for history in status_history:
        changed_by = crud.get_user(db, history.changed_by_id)
        changed_by_response = schemas.UserResponse(
            id=str(changed_by.id),
            username=changed_by.username,
            email=changed_by.email,
            full_name=changed_by.full_name,
            role=changed_by.role,
            is_active=changed_by.is_active,
            created_at=changed_by.created_at,
            updated_at=changed_by.updated_at
        )
        
        status_history_responses.append(schemas.StatusHistoryResponse(
            id=str(history.id),
            case_id=str(history.case_id),
            changed_by_id=str(history.changed_by_id),
            old_status=history.old_status,
            new_status=history.new_status,
            changed_at=history.changed_at,
            changed_by=changed_by_response
        ))
    
    # Get comments (filtered by visibility)
    has_internal_access = crud.has_access_to_internal_comments(db, current_user, db_case)
    comments = crud.get_case_comments(db, db_case.id, include_internal=has_internal_access)
    
    comment_responses = []
    for comment in comments:
        comment_author = crud.get_user(db, comment.author_id)
        comment_author_response = schemas.UserResponse(
            id=str(comment_author.id),
            username=comment_author.username,
            email=comment_author.email,
            full_name=comment_author.full_name,
            role=comment_author.role,
            is_active=comment_author.is_active,
            created_at=comment_author.created_at,
            updated_at=comment_author.updated_at
        )
        
        comment_responses.append(schemas.CommentResponse(
            id=str(comment.id),
            case_id=str(comment.case_id),
            author_id=str(comment.author_id),
            text=comment.text,
            is_internal=comment.is_internal,
            created_at=comment.created_at,
            author=comment_author_response
        ))
    
    # Get attachments
    attachments = crud.get_case_attachments(db, db_case.id)
    attachment_responses = []
    for attachment in attachments:
        uploaded_by = crud.get_user(db, attachment.uploaded_by_id)
        uploaded_by_response = schemas.UserResponse(
            id=str(uploaded_by.id),
            username=uploaded_by.username,
            email=uploaded_by.email,
            full_name=uploaded_by.full_name,
            role=uploaded_by.role,
            is_active=uploaded_by.is_active,
            created_at=uploaded_by.created_at,
            updated_at=uploaded_by.updated_at
        )
        
        attachment_responses.append(schemas.AttachmentResponse(
            id=str(attachment.id),
            case_id=str(attachment.case_id),
            file_path=attachment.file_path,
            original_name=attachment.original_name,
            size_bytes=attachment.size_bytes,
            mime_type=attachment.mime_type,
            uploaded_by_id=str(attachment.uploaded_by_id),
            created_at=attachment.created_at,
            uploaded_by=uploaded_by_response
        ))
    
    # Return detailed case response
    return schemas.CaseDetailResponse(
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
        updated_at=db_case.updated_at,
        category=category_response,
        channel=channel_response,
        author=author_response,
        responsible=responsible_response,
        status_history=status_history_responses,
        comments=comment_responses,
        attachments=attachment_responses
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
    # BE-201: Extended filters
    subcategory: Optional[str] = None,
    applicant_name: Optional[str] = None,
    applicant_phone: Optional[str] = None,
    applicant_email: Optional[str] = None,
    updated_date_from: Optional[str] = None,
    updated_date_to: Optional[str] = None,
    statuses: Optional[str] = None,  # Comma-separated list of statuses
    category_ids: Optional[str] = None,  # Comma-separated list of UUIDs
    channel_ids: Optional[str] = None,  # Comma-separated list of UUIDs
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
    
    BE-201: Extended filters (all use AND logic):
    - subcategory: Filter by subcategory (exact match or use % for LIKE search)
    - applicant_name: Search in applicant name (case-insensitive partial match)
    - applicant_phone: Search in applicant phone (partial match)
    - applicant_email: Search in applicant email (case-insensitive partial match)
    - updated_date_from: Filter by updated date from (ISO format)
    - updated_date_to: Filter by updated date to (ISO format)
    - statuses: Multiple statuses separated by comma (e.g., "NEW,IN_PROGRESS")
    - category_ids: Multiple category UUIDs separated by comma
    - channel_ids: Multiple channel UUIDs separated by comma
    
    All filters use AND logic. Multiple values within statuses/category_ids/channel_ids use OR logic.
    """
    if limit > 100:
        limit = 100
    
    # Apply RBAC: operators can only see own cases
    author_id = None
    if current_user.role == models.UserRole.OPERATOR:
        author_id = current_user.id
    
    # BE-201: Parse comma-separated lists
    parsed_statuses = None
    if statuses:
        try:
            parsed_statuses = [models.CaseStatus(s.strip()) for s in statuses.split(',') if s.strip()]
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status value in statuses parameter: {str(e)}"
            )
    
    parsed_category_ids = None
    if category_ids:
        try:
            parsed_category_ids = [UUID(cid.strip()) for cid in category_ids.split(',') if cid.strip()]
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid UUID in category_ids parameter: {str(e)}"
            )
    
    parsed_channel_ids = None
    if channel_ids:
        try:
            parsed_channel_ids = [UUID(chid.strip()) for chid in channel_ids.split(',') if chid.strip()]
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid UUID in channel_ids parameter: {str(e)}"
            )
    
    cases, total = crud.get_all_cases(
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
        limit=limit,
        # BE-201: Extended filters
        subcategory=subcategory,
        applicant_name=applicant_name,
        applicant_phone=applicant_phone,
        applicant_email=applicant_email,
        updated_date_from=updated_date_from,
        updated_date_to=updated_date_to,
        statuses=parsed_statuses,
        category_ids=parsed_category_ids,
        channel_ids=parsed_channel_ids
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
            updated_at=case.updated_at,
            # Add nested objects for frontend
            category=schemas.CategoryResponse(
                id=str(case.category.id),
                name=case.category.name,
                is_active=case.category.is_active,
                created_at=case.category.created_at,
                updated_at=case.category.updated_at
            ) if case.category else None,
            channel=schemas.ChannelResponse(
                id=str(case.channel.id),
                name=case.channel.name,
                is_active=case.channel.is_active,
                created_at=case.channel.created_at,
                updated_at=case.channel.updated_at
            ) if case.channel else None,
            responsible=schemas.UserResponse(
                id=str(case.responsible.id),
                username=case.responsible.username,
                email=case.responsible.email,
                full_name=case.responsible.full_name,
                role=case.responsible.role,
                is_active=case.responsible.is_active,
                created_at=case.responsible.created_at,
                updated_at=case.responsible.updated_at
            ) if case.responsible else None
        )
        for case in cases
    ]
    
    return {
        "cases": case_responses,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit
    }


@router.post("/{case_id}/take", response_model=schemas.CaseResponse)
async def take_case_into_work(
    case_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Take a case into work by an executor.
    
    This endpoint allows an EXECUTOR or ADMIN to:
    - Take ownership of a case in NEW status
    - Change status to IN_PROGRESS
    - Become the responsible executor
    
    Business rules:
    - Only cases with status=NEW can be taken
    - Only EXECUTOR or ADMIN roles can take cases
    - Sets responsible_id to current user
    - Changes status to IN_PROGRESS
    - Creates status history record (NEW -> IN_PROGRESS)
    - Triggers email notification to case author (OPERATOR)
    
    RBAC:
    - EXECUTOR: Can take any NEW case
    - ADMIN: Can take any NEW case
    - OPERATOR: Cannot take cases (403)
    
    Returns:
    - Updated case with status=IN_PROGRESS and responsible_id set
    
    Errors:
    - 400: Case is not in NEW status
    - 403: User is not EXECUTOR or ADMIN
    - 404: Case not found
    """
    # Check RBAC: Only EXECUTOR or ADMIN can take cases
    if current_user.role not in [models.UserRole.EXECUTOR, models.UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only EXECUTOR or ADMIN can take cases into work"
        )
    
    # Take case
    try:
        db_case = crud.take_case(
            db=db,
            case_id=case_id,
            executor_id=current_user.id
        )
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
    
    # Trigger email notification to case author
    try:
        from app.celery_app import send_case_taken_notification
        
        send_case_taken_notification.delay(
            case_id=str(db_case.id),
            case_public_id=db_case.public_id,
            executor_id=str(current_user.id),
            author_id=str(db_case.author_id)
        )
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Failed to queue case taken notification: {str(e)}")
    
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


@router.post("/{case_id}/status", response_model=schemas.CaseResponse)
async def change_case_status(
    case_id: UUID,
    status_change: schemas.CaseStatusChangeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Change case status with mandatory comment.
    
    This endpoint allows the responsible EXECUTOR to change case status
    from IN_PROGRESS to NEEDS_INFO, REJECTED, or DONE.
    
    Business rules:
    - Only responsible executor can change status
    - Comment is mandatory (minimum 10 characters)
    - Valid transitions from IN_PROGRESS:
        * IN_PROGRESS -> IN_PROGRESS (add comment without changing status)
        * IN_PROGRESS -> NEEDS_INFO (additional information required)
        * IN_PROGRESS -> REJECTED (case rejected)
        * IN_PROGRESS -> DONE (case completed)
    - Valid transitions from NEEDS_INFO:
        * NEEDS_INFO -> IN_PROGRESS (continue working after receiving info)
        * NEEDS_INFO -> REJECTED (case rejected)
        * NEEDS_INFO -> DONE (case completed)
    - Cases in DONE or REJECTED status cannot be edited (except comments)
    - Status change triggers email notification to case author (OPERATOR)
    
    Request body:
    - to_status: Target status (IN_PROGRESS, NEEDS_INFO, REJECTED, or DONE)
    - comment: Mandatory comment explaining the change (10-2000 characters)
    
    RBAC:
    - Only responsible EXECUTOR or ADMIN can change status
    - OPERATOR cannot change status (403)
    - Non-responsible executor cannot change status (403)
    
    Returns:
    - Updated case with new status
    
    Errors:
    - 400: Invalid status transition, missing comment, or validation error
    - 403: User is not responsible executor
    - 404: Case not found
    """
    # Take case
    try:
        db_case = crud.change_case_status(
            db=db,
            case_id=case_id,
            executor_id=current_user.id,
            to_status=status_change.to_status,
            comment_text=status_change.comment
        )
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        elif "responsible" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_msg
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
    
    # Trigger email notification to case author (only if status actually changed)
    try:
        from app.celery_app import send_case_status_changed_notification
        
        send_case_status_changed_notification.delay(
            case_id=str(db_case.id),
            case_public_id=db_case.public_id,
            new_status=db_case.status.value,
            executor_id=str(current_user.id),
            author_id=str(db_case.author_id),
            comment=status_change.comment
        )
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Failed to queue status change notification: {str(e)}")
    
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


# ==================== BE-017: Admin Case Management Endpoints ====================

@router.patch("/{case_id}/assign", response_model=schemas.CaseResponse)
async def assign_case_executor(
    case_id: UUID,
    assignment: schemas.CaseAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Assign or unassign executor to a case (ADMIN only).
    
    BE-017: This endpoint allows ADMIN to manage case assignments:
    - Assign executor: Sets responsible_id and changes status to IN_PROGRESS
    - Unassign executor: Clears responsible_id and changes status back to NEW
    
    Business rules:
    - Only ADMIN role has access
    - Assigned user must be EXECUTOR or ADMIN
    - Assigned user must be active
    - When assigning: status -> IN_PROGRESS (if not already)
    - When unassigning (null): status -> NEW
    - Assignment changes are logged in case history
    
    Request body:
    - assigned_to_id: UUID of executor to assign, or null to unassign
    
    RBAC:
    - ADMIN: Full access to assign/unassign any case
    - EXECUTOR/OPERATOR: 403 Forbidden
    
    Returns:
    - Updated case with new assignment and status
    
    Errors:
    - 400: Validation error (invalid user, not an executor, inactive user)
    - 403: User is not ADMIN
    - 404: Case not found
    """
    try:
        db_case = crud.assign_case_executor(
            db=db,
            case_id=case_id,
            executor_id=assignment.assigned_to_id,
            admin_id=current_user.id
        )
        
        if not db_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case with id '{case_id}' not found"
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
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{case_id}", response_model=schemas.CaseResponse)
async def update_case_fields(
    case_id: UUID,
    assignment: schemas.CaseAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Assign or unassign executor to a case (ADMIN only).
    
    BE-017: This endpoint allows ADMIN to manage case assignments:
    - Assign executor: Sets responsible_id and changes status to IN_PROGRESS
    - Unassign executor: Clears responsible_id and changes status back to NEW
    
    Business rules:
    - Only ADMIN role has access
    - Assigned user must be EXECUTOR or ADMIN
    - Assigned user must be active
    - When assigning: status -> IN_PROGRESS (if not already)
    - When unassigning (null): status -> NEW
    - Assignment changes are logged in case history
    
    Request body:
    - assigned_to_id: UUID of executor to assign, or null to unassign
    
    RBAC:
    - ADMIN: Full access to assign/unassign any case
    - EXECUTOR/OPERATOR: 403 Forbidden
    
    Returns:
    - Updated case with new assignment and status
    
    Errors:
    - 400: Validation error (invalid user, not an executor, inactive user)
    - 403: User is not ADMIN
    - 404: Case not found
    """
    try:
        db_case = crud.assign_case_executor(
            db=db,
            case_id=case_id,
            executor_id=assignment.assigned_to_id,
            admin_id=current_user.id
        )
        
        if not db_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case with id '{case_id}' not found"
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
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


