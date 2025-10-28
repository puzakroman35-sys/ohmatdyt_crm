"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
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


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


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
    id: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


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
