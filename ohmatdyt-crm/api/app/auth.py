"""
Authentication utilities: password hashing, JWT tokens
"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic_settings import BaseSettings
import re


class AuthSettings(BaseSettings):
    """JWT authentication settings"""
    SECRET_KEY: str = "change-me-in-production-please-use-strong-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Map JWT_SECRET to SECRET_KEY
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use JWT_SECRET from env if available, otherwise use SECRET_KEY
        import os
        jwt_secret = os.getenv('JWT_SECRET')
        if jwt_secret:
            self.SECRET_KEY = jwt_secret
    
    class Config:
        env_file = ".env"
        case_sensitive = True


auth_settings = AuthSettings()

# Configure password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength according to requirements:
    - Minimum 8 characters
    - Must contain letters and digits
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[a-zA-Z]", password):
        return False, "Password must contain at least one letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    
    return True, ""


def generate_temp_password(length: int = 12) -> str:
    """
    Generate a temporary password for password reset.
    
    Args:
        length: Length of generated password
        
    Returns:
        Generated password string
    """
    import secrets
    import string
    
    # Ensure password contains letters and digits
    alphabet = string.ascii_letters + string.digits
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        is_valid, _ = validate_password_strength(password)
        if is_valid:
            return password


# ==================== JWT Token Functions ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Dictionary containing user information (sub, role, etc.)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, auth_settings.SECRET_KEY, algorithm=auth_settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT refresh token.
    
    Args:
        data: Dictionary containing user information (sub)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=auth_settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, auth_settings.SECRET_KEY, algorithm=auth_settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")
        
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, auth_settings.SECRET_KEY, algorithms=[auth_settings.ALGORITHM])
        
        # Verify token type
        if payload.get("type") != token_type:
            return None
        
        return payload
    except JWTError:
        return None


def decode_token(token: str) -> Optional[dict]:
    """
    Decode JWT token without verification (for debugging).
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
    """
    try:
        return jwt.decode(token, auth_settings.SECRET_KEY, algorithms=[auth_settings.ALGORITHM], options={"verify_signature": False})
    except JWTError:
        return None
