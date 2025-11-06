"""
Authentication endpoints: login, refresh, logout
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, crud
from app.database import get_db
from app.auth import (
    verify_password, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    auth_settings
)
from app.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=schemas.TokenResponse)
async def login(
    credentials: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens.
    
    **Request:**
    - username: User's username
    - password: User's password
    
    **Response:**
    - access_token: JWT access token (valid for 30 minutes by default)
    - refresh_token: JWT refresh token (valid for 7 days by default)
    - token_type: "bearer"
    - expires_in: Access token expiration in seconds
    - user: User information
    
    **Errors:**
    - 401: Invalid credentials
    - 403: User is not active
    """
    # Find user by username
    user = crud.get_user_by_username(db, credentials.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    
    # Create tokens
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role.value
    }
    
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Convert user to response schema
    user_response = schemas.UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user_response
    }


@router.post("/refresh", response_model=schemas.AccessTokenResponse)
async def refresh_access_token(
    refresh_request: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    **Request:**
    - refresh_token: Valid JWT refresh token
    
    **Response:**
    - access_token: New JWT access token
    - token_type: "bearer"
    - expires_in: Access token expiration in seconds
    
    **Errors:**
    - 401: Invalid or expired refresh token
    - 403: User is not active
    - 404: User not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify refresh token
    payload = verify_token(refresh_request.refresh_token, token_type="refresh")
    
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    try:
        from uuid import UUID
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception
    
    user = crud.get_user(db, user_uuid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    
    # Create new access token
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role.value
    }
    
    access_token = create_access_token(data=token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user.
    
    Note: Since we're using stateless JWT tokens, actual logout is handled
    client-side by removing the tokens. This endpoint validates the token
    and can be used for logging purposes.
    
    **Headers:**
    - Authorization: Bearer {access_token}
    
    **Response:**
    - 204: Successfully logged out
    
    **Errors:**
    - 401: Invalid or expired access token
    """
    # In a production system, you might want to:
    # 1. Add token to a blacklist (Redis)
    # 2. Log the logout event
    # 3. Trigger any cleanup tasks
    
    # For now, just return success
    return None


@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    **Headers:**
    - Authorization: Bearer {access_token}
    
    **Response:**
    - User information
    
    **Errors:**
    - 401: Invalid or expired access token
    """
    return schemas.UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.post("/change-password", response_model=schemas.ChangePasswordResponse)
async def change_password(
    password_data: schemas.ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password (BE-020).
    
    **Headers:**
    - Authorization: Bearer {access_token}
    
    **Request:**
    - current_password: Current password for verification
    - new_password: New password (min 8 chars, uppercase, lowercase, digit)
    - confirm_password: Confirm new password (must match new_password)
    
    **Response:**
    - message: Success message
    - changed_at: Timestamp of password change
    
    **Errors:**
    - 401: Current password is incorrect or user not authenticated
    - 400: Validation errors (passwords don't match, weak password)
    - 422: New password is the same as current password
    """
    # Verify current password
    if not crud.verify_user_password(db, current_user, password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Check if new password is different from current
    if crud.verify_user_password(db, current_user, password_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New password cannot be the same as current password"
        )
    
    # Change password
    from datetime import datetime
    changed_at = datetime.utcnow()
    crud.change_user_password(db, current_user, password_data.new_password)
    
    return schemas.ChangePasswordResponse(
        message="Password changed successfully",
        changed_at=changed_at
    )

