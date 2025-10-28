import os
from uuid import UUID
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.database import get_db, check_db_connection
from app.auth import verify_password

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
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    
    Requires: username, email, full_name, password, role
    """
    try:
        db_user = await crud.create_user(db, user)
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/api/users/me", response_model=schemas.UserResponse)
async def get_current_user(
    current_user_id: UUID,  # TODO: Get from JWT token
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user.
    
    TODO: Implement JWT authentication
    """
    db_user = await crud.get_user(db, current_user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


@app.get("/api/users/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: UUID, db: Session = Depends(get_db)):
    """
    Get user by ID.
    
    TODO: Add permission check (admin or self)
    """
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
    db: Session = Depends(get_db)
):
    """
    List users with filtering and pagination.
    
    TODO: Add permission check (admin only)
    
    Query params:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 100)
    - role: Filter by role (OPERATOR, EXECUTOR, ADMIN)
    - is_active: Filter by active status
    """
    if limit > 100:
        limit = 100
    
    users = await crud.get_users(db, skip=skip, limit=limit, role=role, is_active=is_active)
    total = len(users)  # TODO: Add proper count query
    
    return {
        "users": users,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@app.put("/api/users/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: UUID,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user information.
    
    TODO: Add permission check (admin or self)
    """
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
    db: Session = Depends(get_db)
):
    """
    Update user password.
    
    TODO: Add permission check (admin or self with old password verification)
    """
    db_user = await crud.update_user_password(db, user_id, password_update)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    """
    Delete user (hard delete).
    
    TODO: Add permission check (admin only)
    """
    deleted = await crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return None


@app.post("/api/users/{user_id}/deactivate", response_model=schemas.UserResponse)
async def deactivate_user(user_id: UUID, db: Session = Depends(get_db)):
    """
    Deactivate user (soft delete).
    
    TODO: Add permission check (admin only)
    """
    db_user = await crud.deactivate_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


@app.post("/api/users/{user_id}/activate", response_model=schemas.UserResponse)
async def activate_user(user_id: UUID, db: Session = Depends(get_db)):
    """
    Activate user.
    
    TODO: Add permission check (admin only)
    """
    db_user = await crud.activate_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


# Additional routes will be added here as the project develops