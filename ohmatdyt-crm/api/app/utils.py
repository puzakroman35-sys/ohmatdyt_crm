"""
Utility functions for Ohmatdyt CRM
"""
import random
import os
import mimetypes
from typing import Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Case


async def generate_unique_public_id(db: Session, max_attempts: int = 10) -> int:
    """
    Generate a unique 6-digit public_id for a Case.
    
    The public_id is a random integer between 100000 and 999999 (inclusive).
    The function will retry up to max_attempts times if a collision occurs.
    
    Args:
        db: Database session
        max_attempts: Maximum number of attempts to generate a unique ID
        
    Returns:
        int: A unique 6-digit public_id
        
    Raises:
        RuntimeError: If unable to generate a unique ID after max_attempts
    """
    for attempt in range(max_attempts):
        # Generate a random 6-digit number (100000-999999)
        public_id = random.randint(100000, 999999)
        
        # Check if this public_id already exists (synchronous query)
        result = db.execute(
            select(Case).where(Case.public_id == public_id)
        )
        existing_case = result.scalar_one_or_none()
        
        if existing_case is None:
            # Unique ID found
            return public_id
    
    # If we get here, we failed to generate a unique ID
    raise RuntimeError(
        f"Failed to generate unique public_id after {max_attempts} attempts. "
        "This is highly unlikely and may indicate a database issue."
    )


# ==================== File Validation Utilities ====================

# Maximum file size: 10MB
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

# Allowed MIME types and extensions
ALLOWED_MIME_TYPES = {
    # Documents
    'application/pdf': ['.pdf'],
    'application/msword': ['.doc'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    'application/vnd.ms-excel': ['.xls'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    # Images
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
}

# Flatten to get all allowed extensions
ALLOWED_EXTENSIONS = set()
for extensions in ALLOWED_MIME_TYPES.values():
    ALLOWED_EXTENSIONS.update(extensions)


def validate_file_type(filename: str, content_type: str) -> Tuple[bool, str]:
    """
    Validate file type based on filename extension and MIME type.
    
    Args:
        filename: Original filename
        content_type: MIME type from upload
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Get file extension
    _, ext = os.path.splitext(filename.lower())
    
    if not ext:
        return False, "File has no extension"
    
    # Check if extension is allowed
    if ext not in ALLOWED_EXTENSIONS:
        allowed_ext_str = ', '.join(sorted(ALLOWED_EXTENSIONS))
        return False, f"File type '{ext}' not allowed. Allowed types: {allowed_ext_str}"
    
    # Check if MIME type is allowed
    if content_type not in ALLOWED_MIME_TYPES:
        # Try to guess MIME type from extension
        guessed_type, _ = mimetypes.guess_type(filename)
        if guessed_type and guessed_type in ALLOWED_MIME_TYPES:
            # Accept if guessed type matches allowed type
            return True, ""
        
        allowed_types_str = ', '.join(sorted(ALLOWED_MIME_TYPES.keys()))
        return False, f"MIME type '{content_type}' not allowed. Allowed types: {allowed_types_str}"
    
    # Verify that extension matches MIME type
    allowed_exts_for_mime = ALLOWED_MIME_TYPES.get(content_type, [])
    if ext not in allowed_exts_for_mime:
        return False, f"File extension '{ext}' does not match MIME type '{content_type}'"
    
    return True, ""


def validate_file_size(file_size: int) -> Tuple[bool, str]:
    """
    Validate file size.
    
    Args:
        file_size: File size in bytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if file_size <= 0:
        return False, "File is empty"
    
    if file_size > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        actual_mb = file_size / (1024 * 1024)
        return False, f"File size ({actual_mb:.2f}MB) exceeds maximum allowed size ({max_mb:.0f}MB)"
    
    return True, ""


def get_file_storage_path(case_public_id: int, filename: str) -> str:
    """
    Generate storage path for attachment file.
    
    Path structure: /cases/{public_id}/{filename}
    
    Args:
        case_public_id: 6-digit case public ID
        filename: Original or sanitized filename
        
    Returns:
        Relative path from MEDIA_ROOT
    """
    return f"cases/{case_public_id}/{filename}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent security issues.
    
    - Remove path separators
    - Limit length
    - Keep only safe characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove any path components
    filename = os.path.basename(filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove or replace unsafe characters
    safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-')
    filename = ''.join(c if c in safe_chars else '_' for c in filename)
    
    # Limit length (keep extension)
    max_length = 255
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        max_name_length = max_length - len(ext)
        filename = name[:max_name_length] + ext
    
    return filename

