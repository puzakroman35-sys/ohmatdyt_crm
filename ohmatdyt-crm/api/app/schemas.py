"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, ConfigDict
from typing import Optional, Any
from datetime import datetime
from uuid import UUID
from app.models import UserRole, CaseStatus


class UserBase(BaseModel):
    """Base user schema with common fields"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=200)


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.OPERATOR
    executor_category_ids: Optional[list[str]] = Field(None, description="List of category UUIDs for EXECUTOR role")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        from app.auth import validate_password_strength
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return v.lower()
    
    @field_validator('executor_category_ids')
    @classmethod
    def validate_executor_categories(cls, v: Optional[list[str]], info) -> Optional[list[str]]:
        """Validate that executor_category_ids is only provided for EXECUTOR role"""
        role = info.data.get('role')
        if v and role != UserRole.EXECUTOR:
            raise ValueError("executor_category_ids can only be set for EXECUTOR role")
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    executor_category_ids: Optional[list[str]] = Field(None, description="List of category UUIDs for EXECUTOR role")
    
    @field_validator('executor_category_ids')
    @classmethod
    def validate_executor_categories(cls, v: Optional[list[str]], info) -> Optional[list[str]]:
        """Validate that executor_category_ids is only provided for EXECUTOR role"""
        role = info.data.get('role')
        if v and role and role != UserRole.EXECUTOR:
            raise ValueError("executor_category_ids can only be set for EXECUTOR role")
        return v


class UserPasswordUpdate(BaseModel):
    """Schema for password update"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        from app.auth import validate_password_strength
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v


class UserResponse(UserBase):
    """Schema for user response (excludes password)"""
    id: str  # UUID converted to string
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
    @model_validator(mode='before')
    @classmethod
    def convert_uuid_fields(cls, data):
        """Convert UUID fields to string before validation"""
        if hasattr(data, 'id') and isinstance(data.id, UUID):
            # SQLAlchemy model - convert in place
            return {
                'id': str(data.id),
                'username': data.username,
                'email': data.email,
                'full_name': data.full_name,
                'role': data.role,
                'is_active': data.is_active,
                'created_at': data.created_at,
                'updated_at': data.updated_at,
            }
        elif isinstance(data, dict) and 'id' in data and isinstance(data['id'], UUID):
            # Dict - convert UUID to string
            data['id'] = str(data['id'])
        return data


class UserListResponse(BaseModel):
    """Schema for paginated user list"""
    users: list[UserResponse]
    total: int
    page: int
    page_size: int


# ==================== Authentication Schemas ====================

class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


class AccessTokenResponse(BaseModel):
    """Schema for access token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires


# ==================== Category Schemas ====================

class CategoryBase(BaseModel):
    """Base category schema"""
    name: str = Field(..., min_length=1, max_length=200)


class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating category"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)


class CategoryResponse(CategoryBase):
    """Schema for category response"""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Schema for category list"""
    categories: list[CategoryResponse]
    total: int


# ==================== Channel Schemas ====================

class ChannelBase(BaseModel):
    """Base channel schema"""
    name: str = Field(..., min_length=1, max_length=200)


class ChannelCreate(ChannelBase):
    """Schema for creating a new channel"""
    pass


class ChannelUpdate(BaseModel):
    """Schema for updating channel"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)


class ChannelResponse(ChannelBase):
    """Schema for channel response"""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChannelListResponse(BaseModel):
    """Schema for channel list"""
    channels: list[ChannelResponse]
    total: int


# ==================== Case Schemas ====================

class CaseBase(BaseModel):
    """Base case schema"""
    category_id: str = Field(..., description="UUID of the category")
    channel_id: str = Field(..., description="UUID of the channel")
    subcategory: Optional[str] = Field(None, max_length=200, description="Optional subcategory")
    applicant_name: str = Field(..., min_length=1, max_length=200, description="Name of the applicant")
    applicant_phone: Optional[str] = Field(None, max_length=50, description="Phone number of the applicant")
    applicant_email: Optional[EmailStr] = Field(None, description="Email of the applicant")
    summary: str = Field(..., min_length=1, description="Case summary/description")


class CaseCreate(CaseBase):
    """Schema for creating a new case"""
    responsible_id: Optional[str] = Field(None, description="UUID of the responsible executor (optional)")
    
    @field_validator('applicant_phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format (basic validation)"""
        if v is not None and v.strip():
            # Remove common formatting characters
            cleaned = v.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')
            if not cleaned.isdigit() or len(cleaned) < 9:
                raise ValueError("Phone number must contain at least 9 digits")
            return v.strip()
        return None


class CaseUpdate(BaseModel):
    """Schema for updating case information"""
    category_id: Optional[str] = None
    channel_id: Optional[str] = None
    subcategory: Optional[str] = Field(None, max_length=200)
    applicant_name: Optional[str] = Field(None, min_length=1, max_length=200)
    applicant_phone: Optional[str] = Field(None, max_length=50)
    applicant_email: Optional[EmailStr] = None
    summary: Optional[str] = Field(None, min_length=1)
    status: Optional[CaseStatus] = None
    responsible_id: Optional[str] = None
    
    @field_validator('applicant_phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format (basic validation)"""
        if v is not None and v.strip():
            # Remove common formatting characters
            cleaned = v.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')
            if not cleaned.isdigit() or len(cleaned) < 9:
                raise ValueError("Phone number must contain at least 9 digits")
            return v.strip()
        return None


class CaseResponse(CaseBase):
    """Schema for case response"""
    id: str
    public_id: int
    status: CaseStatus
    author_id: str
    responsible_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Optional nested objects (can be populated with joins)
    category: Optional[CategoryResponse] = None
    channel: Optional[ChannelResponse] = None
    author: Optional[UserResponse] = None
    responsible: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class CaseListResponse(BaseModel):
    """Schema for case list"""
    cases: list[CaseResponse]
    total: int
    page: Optional[int] = 1
    page_size: Optional[int] = 50


# ==================== Attachment Schemas ====================

class AttachmentBase(BaseModel):
    """Base attachment schema"""
    original_name: str = Field(..., description="Original filename")
    size_bytes: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")


class AttachmentResponse(AttachmentBase):
    """Schema for attachment response"""
    id: str
    case_id: str
    file_path: str
    uploaded_by_id: str
    created_at: datetime
    
    # Optional nested objects
    uploaded_by: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class AttachmentListResponse(BaseModel):
    """Schema for attachment list"""
    attachments: list[AttachmentResponse]
    total: int


# ==================== Comment Schemas ====================

class CommentCreate(BaseModel):
    """Schema for creating a new comment"""
    text: str
    is_internal: bool = False
    
    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """Schema for comment response"""
    id: str
    case_id: str
    author_id: str
    text: str
    is_internal: bool
    created_at: datetime
    
    # Optional nested objects
    author: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    """Schema for comment list"""
    comments: list[CommentResponse]
    total: int


# ==================== Status History Schemas ====================

class StatusHistoryResponse(BaseModel):
    """Schema for status history response"""
    id: str
    case_id: str
    changed_by_id: str
    old_status: Optional[CaseStatus]
    new_status: CaseStatus
    changed_at: datetime
    
    # Optional nested objects
    changed_by: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class StatusHistoryListResponse(BaseModel):
    """Schema for status history list"""
    history: list[StatusHistoryResponse]
    total: int


# ==================== Case Detail Schema ====================

class CaseDetailResponse(CaseResponse):
    """
    Schema for detailed case response with nested data.
    
    Includes:
    - All case fields from CaseResponse
    - Category and channel details
    - Author and responsible user details
    - Status change history
    - Comments (filtered by visibility rules)
    - Attachments
    """
    # Override optional fields to always be populated
    category: CategoryResponse
    channel: ChannelResponse
    author: UserResponse
    responsible: Optional[UserResponse] = None
    
    # Additional nested data
    status_history: list[StatusHistoryResponse] = []
    comments: list[CommentResponse] = []
    attachments: list[AttachmentResponse] = []

    class Config:
        from_attributes = True


# ==================== Case Status Change Schema ====================

class CaseStatusChangeRequest(BaseModel):
    """
    Schema for changing case status.
    
    Used by responsible executor to change case status with mandatory comment.
    Valid transitions from IN_PROGRESS:
    - IN_PROGRESS -> NEEDS_INFO (additional information required)
    - IN_PROGRESS -> REJECTED (case rejected)
    - IN_PROGRESS -> DONE (case completed)
    """
    to_status: CaseStatus = Field(
        ..., 
        description="Target status (NEEDS_INFO, REJECTED, or DONE)"
    )
    comment: str = Field(
        ..., 
        min_length=10,
        max_length=2000,
        description="Mandatory comment explaining the status change"
    )
    
    @field_validator('to_status')
    @classmethod
    def validate_target_status(cls, v: CaseStatus) -> CaseStatus:
        """Validate that target status is one of the allowed statuses"""
        allowed_statuses = [
            CaseStatus.IN_PROGRESS,
            CaseStatus.NEEDS_INFO,
            CaseStatus.REJECTED,
            CaseStatus.DONE
        ]
        if v not in allowed_statuses:
            raise ValueError(
                f"Invalid target status. Allowed: IN_PROGRESS, NEEDS_INFO, REJECTED, DONE"
            )
        return v


# ==================== User Management Schemas (ADMIN) ====================

class ResetPasswordResponse(BaseModel):
    """Schema for reset password response"""
    message: str
    temp_password: str


class DeactivateUserRequest(BaseModel):
    """Schema for deactivate user request (optional validation)"""
    force: bool = Field(False, description="Force deactivation even if user has active cases")


class DeactivateUserResponse(BaseModel):
    """Schema for deactivate user response"""
    message: str
    user_id: str
    active_cases: Optional[list[str]] = Field(None, description="List of active case IDs if deactivation was blocked")


class ActiveCasesResponse(BaseModel):
    """Schema for active cases response"""
    user_id: str
    username: str
    active_cases_count: int
    case_ids: list[str]
