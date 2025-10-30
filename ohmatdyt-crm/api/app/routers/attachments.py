"""
Attachment API endpoints
"""
import os
import uuid as uuid_lib
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.database import get_db
from app.dependencies import get_current_active_user, require_admin
from app import utils

router = APIRouter(
    prefix="/api/attachments",
    tags=["attachments"]
)


def get_media_root() -> str:
    """Get MEDIA_ROOT from environment or use default"""
    return os.getenv("MEDIA_ROOT", "/var/app/media")


@router.post("/cases/{case_id}/upload", response_model=schemas.AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    case_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Upload an attachment to a case.
    
    Allowed file types: pdf, doc, docx, xls, xlsx, jpg, jpeg, png
    Maximum file size: 10MB
    
    Files are stored in: MEDIA_ROOT/cases/{case_public_id}/
    
    Requires authentication.
    """
    # Verify case exists
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with id '{case_id}' not found"
        )
    
    # Check RBAC permissions
    # OPERATOR: can upload to own cases
    # EXECUTOR/ADMIN: can upload to any case
    if current_user.role == models.UserRole.OPERATOR and case.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload attachments to this case"
        )
    
    # Read file content to validate size
    file_content = await file.read()
    file_size = len(file_content)
    
    # Validate file size
    is_valid_size, size_error = utils.validate_file_size(file_size)
    if not is_valid_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=size_error
        )
    
    # Validate file type
    content_type = file.content_type or "application/octet-stream"
    is_valid_type, type_error = utils.validate_file_type(file.filename, content_type)
    if not is_valid_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=type_error
        )
    
    # Sanitize filename and generate storage path
    safe_filename = utils.sanitize_filename(file.filename)
    
    # Add UUID prefix to avoid name collisions
    unique_filename = f"{uuid_lib.uuid4().hex[:8]}_{safe_filename}"
    
    # Get relative path for storage
    relative_path = utils.get_file_storage_path(case.public_id, unique_filename)
    
    # Create full path
    media_root = get_media_root()
    full_path = os.path.join(media_root, relative_path)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    # Save file to disk
    try:
        with open(full_path, "wb") as f:
            f.write(file_content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Create database record
    try:
        db_attachment = crud.create_attachment(
            db=db,
            case_id=case_id,
            file_path=relative_path,
            original_name=file.filename,
            size_bytes=file_size,
            mime_type=content_type,
            uploaded_by_id=current_user.id
        )
        
        return db_attachment
    except ValueError as e:
        # Clean up file if database record creation fails
        if os.path.exists(full_path):
            os.remove(full_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/cases/{case_id}", response_model=schemas.AttachmentListResponse)
async def list_case_attachments(
    case_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get all attachments for a specific case.
    
    RBAC:
    - OPERATOR: can view attachments for own cases
    - EXECUTOR/ADMIN: can view attachments for all cases
    """
    # Verify case exists
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with id '{case_id}' not found"
        )
    
    # Check RBAC permissions
    if current_user.role == models.UserRole.OPERATOR and case.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view attachments for this case"
        )
    
    attachments = crud.get_case_attachments(db, case_id, skip=skip, limit=limit)
    
    # Convert to response models
    attachment_responses = [
        schemas.AttachmentResponse(
            id=str(att.id),
            case_id=str(att.case_id),
            file_path=att.file_path,
            original_name=att.original_name,
            size_bytes=att.size_bytes,
            mime_type=att.mime_type,
            uploaded_by_id=str(att.uploaded_by_id),
            created_at=att.created_at
        )
        for att in attachments
    ]
    
    return {
        "attachments": attachment_responses,
        "total": len(attachment_responses)
    }


@router.get("/{attachment_id}/download")
async def download_attachment(
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Download an attachment file.
    
    RBAC:
    - OPERATOR: can download attachments from own cases
    - EXECUTOR/ADMIN: can download all attachments
    """
    # Get attachment
    attachment = crud.get_attachment(db, attachment_id)
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attachment with id '{attachment_id}' not found"
        )
    
    # Get associated case for permission check
    case = crud.get_case(db, attachment.case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated case not found"
        )
    
    # Check RBAC permissions
    if current_user.role == models.UserRole.OPERATOR and case.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to download this attachment"
        )
    
    # Get full file path
    media_root = get_media_root()
    full_path = os.path.join(media_root, attachment.file_path)
    
    # Check if file exists
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    # Return file
    return FileResponse(
        path=full_path,
        filename=attachment.original_name,
        media_type=attachment.mime_type
    )


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Delete an attachment (both file and database record).
    
    RBAC:
    - OPERATOR: can delete attachments from own cases
    - ADMIN: can delete any attachment
    - EXECUTOR: cannot delete attachments
    """
    # Get attachment
    attachment = crud.get_attachment(db, attachment_id)
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attachment with id '{attachment_id}' not found"
        )
    
    # Get associated case for permission check
    case = crud.get_case(db, attachment.case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated case not found"
        )
    
    # Check RBAC permissions
    if current_user.role == models.UserRole.EXECUTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Executors cannot delete attachments"
        )
    
    if current_user.role == models.UserRole.OPERATOR and case.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this attachment"
        )
    
    # Delete file from disk
    media_root = get_media_root()
    full_path = os.path.join(media_root, attachment.file_path)
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
        except Exception as e:
            # Log error but continue with database deletion
            print(f"Warning: Failed to delete file {full_path}: {str(e)}")
    
    # Delete database record
    deleted = crud.delete_attachment(db, attachment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    return None
