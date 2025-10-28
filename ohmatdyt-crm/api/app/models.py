"""
Database models for Ohmatdyt CRM
"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User role enumeration"""
    OPERATOR = "OPERATOR"
    EXECUTOR = "EXECUTOR"
    ADMIN = "ADMIN"


class CaseStatus(str, enum.Enum):
    """Case status enumeration"""
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    NEEDS_INFO = "NEEDS_INFO"
    REJECTED = "REJECTED"
    DONE = "DONE"


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


class Category(Base):
    """
    Request category directory (довідник категорій звернень)
    
    Used for classifying requests. Only active categories
    are available for selection when creating requests.
    """
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Category(name={self.name}, active={self.is_active})>"

    def to_dict(self):
        """Convert category to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Channel(Base):
    """
    Request channel directory (довідник каналів звернень)
    
    Represents the communication channel through which a request was received
    (e.g., Phone, Email, Web Form, In Person). Only active channels
    are available for selection when creating requests.
    """
    __tablename__ = "channels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Channel(name={self.name}, active={self.is_active})>"

    def to_dict(self):
        """Convert channel to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Case(Base):
    """
    Case (звернення) model
    
    Represents a citizen's request/case with a unique 6-digit public_id.
    Cases are created by operators and can be assigned to executors.
    
    Statuses:
    - NEW: Initial status when case is created
    - IN_PROGRESS: Case is being processed by an executor
    - NEEDS_INFO: Additional information required from applicant
    - REJECTED: Case was rejected
    - DONE: Case processing completed
    """
    __tablename__ = "cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    public_id = Column(Integer, unique=True, nullable=False, index=True)  # 6-digit unique ID (100000-999999)
    
    # Foreign keys
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("channels.id", ondelete="RESTRICT"), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    responsible_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Case details
    subcategory = Column(String(200), nullable=True)  # Optional subcategory
    applicant_name = Column(String(200), nullable=False)
    applicant_phone = Column(String(50), nullable=True)
    applicant_email = Column(String(100), nullable=True)
    summary = Column(Text, nullable=False)
    
    # Status
    status = Column(SQLEnum(CaseStatus), nullable=False, default=CaseStatus.NEW, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    category = relationship("Category", foreign_keys=[category_id])
    channel = relationship("Channel", foreign_keys=[channel_id])
    author = relationship("User", foreign_keys=[author_id])
    responsible = relationship("User", foreign_keys=[responsible_id])

    def __repr__(self):
        return f"<Case(public_id={self.public_id}, status={self.status.value}, category={self.category_id})>"

    def to_dict(self):
        """Convert case to dictionary"""
        return {
            "id": str(self.id),
            "public_id": self.public_id,
            "category_id": str(self.category_id),
            "channel_id": str(self.channel_id),
            "subcategory": self.subcategory,
            "applicant_name": self.applicant_name,
            "applicant_phone": self.applicant_phone,
            "applicant_email": self.applicant_email,
            "summary": self.summary,
            "status": self.status.value,
            "author_id": str(self.author_id),
            "responsible_id": str(self.responsible_id) if self.responsible_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
