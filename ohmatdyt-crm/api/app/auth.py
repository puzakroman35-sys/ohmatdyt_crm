"""
Password hashing and verification utilities
"""
from passlib.context import CryptContext
import re

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
