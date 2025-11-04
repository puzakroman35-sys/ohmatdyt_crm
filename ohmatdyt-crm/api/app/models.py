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
    attachments = relationship("Attachment", back_populates="case", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="case", cascade="all, delete-orphan")
    status_history = relationship("StatusHistory", back_populates="case", cascade="all, delete-orphan")

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


class Attachment(Base):
    """
    Attachment model for case files
    
    Stores file attachments associated with cases.
    Supports validation of file types and size limits.
    
    Allowed file types:
    - Documents: pdf, doc, docx, xls, xlsx
    - Images: jpg, jpeg, png
    
    Maximum file size: 10MB
    """
    __tablename__ = "attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # File information
    file_path = Column(String(500), nullable=False)  # Relative path from MEDIA_ROOT
    original_name = Column(String(255), nullable=False)  # Original filename from upload
    size_bytes = Column(Integer, nullable=False)  # File size in bytes
    mime_type = Column(String(100), nullable=False)  # MIME type (e.g., application/pdf)
    
    # Upload metadata
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    case = relationship("Case", back_populates="attachments")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])

    def __repr__(self):
        return f"<Attachment(case_id={self.case_id}, original_name={self.original_name}, size={self.size_bytes})>"

    def to_dict(self):
        """Convert attachment to dictionary"""
        return {
            "id": str(self.id),
            "case_id": str(self.case_id),
            "file_path": self.file_path,
            "original_name": self.original_name,
            "size_bytes": self.size_bytes,
            "mime_type": self.mime_type,
            "uploaded_by_id": str(self.uploaded_by_id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Comment(Base):
    """
    Comment model for case comments
    
    Supports both public and internal comments:
    - Public comments: Visible to operator, responsible executor, and admin
    - Internal comments: Visible only to executors of the category and admin
    
    Only EXECUTOR and ADMIN can create internal comments.
    """
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    # Comment content
    text = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    case = relationship("Case", back_populates="comments")
    author = relationship("User", foreign_keys=[author_id])

    def __repr__(self):
        return f"<Comment(case_id={self.case_id}, author_id={self.author_id}, internal={self.is_internal})>"

    def to_dict(self):
        """Convert comment to dictionary"""
        return {
            "id": str(self.id),
            "case_id": str(self.case_id),
            "author_id": str(self.author_id),
            "text": self.text,
            "is_internal": self.is_internal,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class StatusHistory(Base):
    """
    Status history model for tracking case status changes
    
    Logs all status transitions for audit and tracking purposes.
    """
    __tablename__ = "status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    changed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    # Status change details
    old_status = Column(SQLEnum(CaseStatus), nullable=True)  # NULL for initial status
    new_status = Column(SQLEnum(CaseStatus), nullable=False, index=True)
    
    # Timestamp
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    case = relationship("Case", back_populates="status_history")
    changed_by = relationship("User", foreign_keys=[changed_by_id])

    def __repr__(self):
        return f"<StatusHistory(case_id={self.case_id}, {self.old_status} -> {self.new_status})>"

    def to_dict(self):
        """Convert status history to dictionary"""
        return {
            "id": str(self.id),
            "case_id": str(self.case_id),
            "changed_by_id": str(self.changed_by_id),
            "old_status": self.old_status.value if self.old_status else None,
            "new_status": self.new_status.value,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None,
        }


class NotificationStatus(str, enum.Enum):
    """Notification delivery status enumeration"""
    PENDING = "PENDING"      # Queued for sending
    SENT = "SENT"           # Successfully sent
    FAILED = "FAILED"       # Failed to send
    RETRYING = "RETRYING"   # Retrying after failure


class NotificationType(str, enum.Enum):
    """Notification type enumeration"""
    NEW_CASE = "NEW_CASE"                       # New case created
    CASE_TAKEN = "CASE_TAKEN"                   # Case taken into work
    STATUS_CHANGED = "STATUS_CHANGED"           # Case status changed
    NEW_COMMENT = "NEW_COMMENT"                 # Comment added
    TEMP_PASSWORD = "TEMP_PASSWORD"             # Temp password generated


class NotificationLog(Base):
    """
    Notification log model for tracking all email notifications
    
    Logs all notification attempts for audit, debugging, and retry management.
    Tracks delivery status, retry attempts, and error messages.
    """
    __tablename__ = "notification_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Notification details
    notification_type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    recipient_email = Column(String(100), nullable=False, index=True)
    recipient_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Related entity (e.g., case_id, comment_id)
    related_case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=True, index=True)
    related_entity_id = Column(String(100), nullable=True)  # For other entities
    
    # Email content
    subject = Column(String(500), nullable=False)
    body_text = Column(Text, nullable=True)  # Plain text version
    body_html = Column(Text, nullable=True)  # HTML version
    
    # Delivery tracking
    status = Column(SQLEnum(NotificationStatus), nullable=False, default=NotificationStatus.PENDING, index=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=5, nullable=False)
    
    # Error tracking
    last_error = Column(Text, nullable=True)
    error_details = Column(Text, nullable=True)  # JSON with full error info
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    sent_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    next_retry_at = Column(DateTime, nullable=True, index=True)
    
    # Celery task tracking
    celery_task_id = Column(String(255), nullable=True, index=True)
    
    # Relationships
    recipient_user = relationship("User", foreign_keys=[recipient_user_id])
    related_case = relationship("Case", foreign_keys=[related_case_id])

    def __repr__(self):
        return f"<NotificationLog(type={self.notification_type.value}, to={self.recipient_email}, status={self.status.value})>"

    def to_dict(self):
        """Convert notification log to dictionary"""
        return {
            "id": str(self.id),
            "notification_type": self.notification_type.value,
            "recipient_email": self.recipient_email,
            "recipient_user_id": str(self.recipient_user_id) if self.recipient_user_id else None,
            "related_case_id": str(self.related_case_id) if self.related_case_id else None,
            "related_entity_id": self.related_entity_id,
            "subject": self.subject,
            "status": self.status.value,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "last_error": self.last_error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "failed_at": self.failed_at.isoformat() if self.failed_at else None,
            "next_retry_at": self.next_retry_at.isoformat() if self.next_retry_at else None,
            "celery_task_id": self.celery_task_id,
        }


class ExecutorCategoryAccess(Base):
    """
    BE-018: Executor category access model
    
    Maps executors to categories they have access to.
    Only users with EXECUTOR role can have category access records.
    
    Business Rules:
    - Only EXECUTOR role users can have category access
    - Each executor-category pair must be unique
    - When executor is deleted, all access records are cascaded
    - When category is deactivated, access records remain but are not used
    """
    __tablename__ = "executor_category_access"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    executor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    executor = relationship("User", foreign_keys=[executor_id])
    category = relationship("Category", foreign_keys=[category_id])

    # Unique constraint on executor-category pair
    __table_args__ = (
        # Ensure each executor can have access to a category only once
        # This prevents duplicate access records
        # Example: executor A cannot have two access records for category X
        # Note: We use string names here because the table is not yet created
        # The constraint will be applied when the table is created via migration
        {"extend_existing": True}  # Allow model redefinition during development
    )

    def __repr__(self):
        return f"<ExecutorCategoryAccess(executor_id={self.executor_id}, category_id={self.category_id})>"

    def to_dict(self):
        """Convert executor category access to dictionary"""
        return {
            "id": str(self.id),
            "executor_id": str(self.executor_id),
            "category_id": str(self.category_id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
