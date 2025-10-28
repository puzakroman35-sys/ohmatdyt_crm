import os
from uuid import UUID
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.database import get_db, check_db_connection
from app.dependencies import get_current_user, require_admin, get_current_active_user
from app.routers import auth, categories, channels, attachments

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    APP_ENV: str = "development"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    CORS_ORIGINS: str = "http://localhost:3000"
    DATABASE_URL: str = "postgresql+psycopg://ohm_user:change_me@db:5432/ohm_db"
    REDIS_URL: str = "redis://redis:6379/0"
    MEDIA_ROOT: str = "/var/app/media"
    STATIC_ROOT: str = "/var/app/static"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

app = FastAPI(
    title="Ohmatdyt CRM API",
    description="CRM system for Ohmatdyt hospital",
    version="0.1.0",
    docs_url="/docs" if settings.APP_ENV == "development" else None,
    redoc_url="/redoc" if settings.APP_ENV == "development" else None,
)

# CORS configuration
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(channels.router)
app.include_router(attachments.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ohmatdyt CRM API",
        "version": "0.1.0",
        "environment": settings.APP_ENV
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    db_status = "connected" if check_db_connection() else "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "redis": "connected",  # TODO: Add actual Redis check
        "media_path": os.path.exists(settings.MEDIA_ROOT),
        "static_path": os.path.exists(settings.STATIC_ROOT),
    }

@app.get("/config")
async def config_check():
    """Configuration check endpoint (dev only)"""
    if settings.APP_ENV != "development":
        return {"error": "Not available in production"}
    
    return {
        "APP_ENV": settings.APP_ENV,
        "DATABASE_URL": settings.DATABASE_URL[:30] + "...",  # Truncate for security
        "REDIS_URL": settings.REDIS_URL,
        "MEDIA_ROOT": settings.MEDIA_ROOT,
        "STATIC_ROOT": settings.STATIC_ROOT,
        "CORS_ORIGINS": settings.CORS_ORIGINS,
        "ALLOWED_HOSTS": settings.ALLOWED_HOSTS,
    }


# ==================== User Management Endpoints ====================

@app.post("/api/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Create a new user.
    
    Requires: username, email, full_name, password, role
    Requires: Admin privileges
    """
    try:
        db_user = await crud.create_user(db, user)
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/api/users/me", response_model=schemas.UserResponse)
async def get_current_user_endpoint(
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Get current authenticated user.
    
    Requires valid JWT access token in Authorization header.
    """
    return current_user


@app.get("/api/users/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get user by ID.
    
    Admin can view any user, others can only view themselves.
    """
    # Check permissions: admin or self
    if current_user.role != models.UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    db_user = await crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


@app.get("/api/users", response_model=schemas.UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[models.UserRole] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    List users with filtering and pagination.
    
    Requires: Admin privileges
    
    Query params:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 100)
    - role: Filter by role (OPERATOR, EXECUTOR, ADMIN)
    - is_active: Filter by active status
    """
    if limit > 100:
        limit = 100
    
    db_users = await crud.get_users(db, skip=skip, limit=limit, role=role, is_active=is_active)
    total = len(db_users)  # TODO: Add proper count query
    
    # Convert User models to UserResponse schemas
    users = [
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
        for user in db_users
    ]
    
    return {
        "users": users,
        "total": total,
        "page": skip // limit if limit > 0 else 0,
        "page_size": limit
    }


@app.put("/api/users/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: UUID,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Update user information.
    
    Admin can update any user, others can only update themselves (limited fields).
    """
    # Check permissions: admin or self
    if current_user.role != models.UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    # Non-admin users can only update limited fields
    if current_user.role != models.UserRole.ADMIN:
        # Prevent role change by non-admin
        if user_update.role is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to change user role"
            )
        # Prevent is_active change by non-admin
        if user_update.is_active is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to change user active status"
            )
    
    try:
        db_user = await crud.update_user(db, user_id, user_update)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.put("/api/users/{user_id}/password", response_model=schemas.UserResponse)
async def update_user_password(
    user_id: UUID,
    password_update: schemas.UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Update user password.
    
    Admin can update any user's password, others can only update their own.
    """
    # Check permissions: admin or self
    if current_user.role != models.UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's password"
        )
    
    db_user = await crud.update_user_password(db, user_id, password_update)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Delete user (hard delete).
    
    Requires: Admin privileges
    """
    deleted = await crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return None


@app.post("/api/users/{user_id}/deactivate", response_model=schemas.UserResponse)
async def deactivate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Deactivate user (soft delete).
    
    Requires: Admin privileges
    """
    db_user = await crud.deactivate_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


@app.post("/api/users/{user_id}/activate", response_model=schemas.UserResponse)
async def activate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Activate user.
    
    Requires: Admin privileges
    """
    db_user = await crud.activate_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


# Additional routes will be added here as the project develops