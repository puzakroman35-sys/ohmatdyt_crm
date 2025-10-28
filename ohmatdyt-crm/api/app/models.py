"""
Database models for Ohmatdyt CRM
"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User role enumeration"""
    OPERATOR = "OPERATOR"
    EXECUTOR = "EXECUTOR"
    ADMIN = "ADMIN"


class User(Base):
    """
    Custom User model with role-based access control
    
    Roles:
    - OPERATOR: Can create and view own requests
    - EXECUTOR: Can view and process requests in assigned categories
    - ADMIN: Full system access
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.OPERATOR, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role.value}, active={self.is_active})>"

    def to_dict(self):
        """Convert user to dictionary (exclude password_hash)"""
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
