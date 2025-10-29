"""CRUD operations for database models."""

import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from app import models, schemas
from app.auth import hash_password

# Налаштування логування
logger = logging.getLogger(__name__)


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Create a new user.
    
    Args:
        db: Database session
        user: User creation schema with password
        
    Returns:
        Created user model
        
    Raises:
        ValueError: If username or email already exists
    """
    # Check if username exists
    existing = db.execute(
        select(models.User).where(models.User.username == user.username)
    ).scalar_one_or_none()
    if existing:
        raise ValueError(f"Username '{user.username}' already exists")
    
    # Check if email exists
    existing = db.execute(
        select(models.User).where(models.User.email == user.email)
    ).scalar_one_or_none()
    if existing:
        raise ValueError(f"Email '{user.email}' already exists")
    
    # Create user with hashed password
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        password_hash=hash_password(user.password),
        role=user.role,
        is_active=user.is_active if hasattr(user, 'is_active') else True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def get_user(db: Session, user_id: UUID) -> Optional[models.User]:
    """
    Get user by ID.
    
    Args:
        db: Database session
        user_id: User UUID
        
    Returns:
        User model or None if not found
    """
    return db.execute(
        select(models.User).where(models.User.id == user_id)
    ).scalar_one_or_none()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """
    Get user by username.
    
    Args:
        db: Database session
        username: Username string
        
    Returns:
        User model or None if not found
    """
    return db.execute(
        select(models.User).where(models.User.username == username)
    ).scalar_one_or_none()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Get user by email.
    
    Args:
        db: Database session
        email: Email string
        
    Returns:
        User model or None if not found
    """
    return db.execute(
        select(models.User).where(models.User.email == email)
    ).scalar_one_or_none()


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    role: Optional[models.UserRole] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    order_by: Optional[str] = "username"
) -> tuple[list[models.User], int]:
    """
    Get list of users with filtering, pagination, and sorting.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        role: Filter by user role
        is_active: Filter by active status
        search: Search by username, email, or full_name (case-insensitive)
        order_by: Sort field (prefix with - for descending, e.g., -created_at)
        
    Returns:
        Tuple of (list of users, total count)
    """
    from sqlalchemy import or_
    
    query = select(models.User)
    
    if role is not None:
        query = query.where(models.User.role == role)
    
    if is_active is not None:
        query = query.where(models.User.is_active == is_active)
    
    # Пошук за логіном, email або ПІБ (case-insensitive)
    if search:
        search_filter = or_(
            models.User.username.ilike(f"%{search}%"),
            models.User.email.ilike(f"%{search}%"),
            models.User.full_name.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    # Get total count
    from sqlalchemy import func
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0
    
    # Apply sorting
    if order_by:
        if order_by.startswith('-'):
            # Descending order
            field_name = order_by[1:]
            if hasattr(models.User, field_name):
                query = query.order_by(getattr(models.User, field_name).desc())
            else:
                query = query.order_by(models.User.username.asc())
        else:
            # Ascending order
            if hasattr(models.User, order_by):
                query = query.order_by(getattr(models.User, order_by).asc())
            else:
                query = query.order_by(models.User.username.asc())
    else:
        query = query.order_by(models.User.username.asc())
    
    query = query.offset(skip).limit(limit)
    
    return list(db.execute(query).scalars().all()), total


def update_user(
    db: Session,
    user_id: UUID,
    user_update: schemas.UserUpdate
) -> Optional[models.User]:
    """
    Update user information.
    
    Args:
        db: Database session
        user_id: User UUID
        user_update: User update schema with optional fields
        
    Returns:
        Updated user model or None if not found
        
    Raises:
        ValueError: If username or email already exists for another user
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Check username uniqueness if being updated
    if 'username' in update_data and update_data['username'] != db_user.username:
        existing = get_user_by_username(db, update_data['username'])
        if existing and existing.id != user_id:
            raise ValueError(f"Username '{update_data['username']}' already exists")
    
    # Check email uniqueness if being updated
    if 'email' in update_data and update_data['email'] != db_user.email:
        existing = get_user_by_email(db, update_data['email'])
        if existing and existing.id != user_id:
            raise ValueError(f"Email '{update_data['email']}' already exists")
    
    # Update fields
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


def update_user_password(
    db: Session,
    user_id: UUID,
    password_update: schemas.UserPasswordUpdate
) -> Optional[models.User]:
    """
    Update user password.
    
    Args:
        db: Database session
        user_id: User UUID
        password_update: Password update schema with new password
        
    Returns:
        Updated user model or None if not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.password_hash = hash_password(password_update.password)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


def delete_user(db: Session, user_id: UUID) -> bool:
    """
    Delete user by ID.
    
    Args:
        db: Database session
        user_id: User UUID
        
    Returns:
        True if user was deleted, False if not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    
    return True


def deactivate_user(db: Session, user_id: UUID) -> Optional[models.User]:
    """
    Deactivate user (soft delete).
    
    Args:
        db: Database session
        user_id: User UUID
        
    Returns:
        Updated user model or None if not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.is_active = False
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


def activate_user(db: Session, user_id: UUID) -> Optional[models.User]:
    """
    Activate user.
    
    Args:
        db: Database session
        user_id: User UUID
        
    Returns:
        Updated user model or None if not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.is_active = True
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


# ==================== Category CRUD Operations ====================

def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    """
    Create a new category.
    
    Args:
        db: Database session
        category: Category creation schema
        
    Returns:
        Created category model
        
    Raises:
        ValueError: If category name already exists
    """
    # Check if name exists
    existing = db.execute(
        select(models.Category).where(models.Category.name == category.name)
    ).scalar_one_or_none()
    if existing:
        raise ValueError(f"Category '{category.name}' already exists")
    
    db_category = models.Category(name=category.name)
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category


def get_category(db: Session, category_id: UUID) -> Optional[models.Category]:
    """
    Get category by ID.
    
    Args:
        db: Database session
        category_id: Category UUID
        
    Returns:
        Category model or None if not found
    """
    return db.execute(
        select(models.Category).where(models.Category.id == category_id)
    ).scalar_one_or_none()


def get_category_by_name(db: Session, name: str) -> Optional[models.Category]:
    """
    Get category by name.
    
    Args:
        db: Database session
        name: Category name
        
    Returns:
        Category model or None if not found
    """
    return db.execute(
        select(models.Category).where(models.Category.name == name)
    ).scalar_one_or_none()


def get_categories(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False
) -> list[models.Category]:
    """
    Get list of categories with optional filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_inactive: Include inactive categories
        
    Returns:
        List of category models
    """
    query = select(models.Category)
    
    if not include_inactive:
        query = query.where(models.Category.is_active == True)
    
    query = query.offset(skip).limit(limit).order_by(models.Category.name)
    
    return list(db.execute(query).scalars().all())


def update_category(
    db: Session,
    category_id: UUID,
    category_update: schemas.CategoryUpdate
) -> Optional[models.Category]:
    """
    Update category information.
    
    Args:
        db: Database session
        category_id: Category UUID
        category_update: Category update schema
        
    Returns:
        Updated category model or None if not found
        
    Raises:
        ValueError: If new name already exists for another category
    """
    db_category = get_category(db, category_id)
    if not db_category:
        return None
    
    update_data = category_update.model_dump(exclude_unset=True)
    
    # Check name uniqueness if being updated
    if 'name' in update_data and update_data['name'] != db_category.name:
        existing = get_category_by_name(db, update_data['name'])
        if existing and existing.id != category_id:
            raise ValueError(f"Category '{update_data['name']}' already exists")
    
    # Update fields
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    
    return db_category


def deactivate_category(db: Session, category_id: UUID) -> Optional[models.Category]:
    """
    Deactivate category.
    
    Args:
        db: Database session
        category_id: Category UUID
        
    Returns:
        Updated category model or None if not found
    """
    db_category = get_category(db, category_id)
    if not db_category:
        return None
    
    db_category.is_active = False
    
    db.commit()
    db.refresh(db_category)
    
    return db_category


def activate_category(db: Session, category_id: UUID) -> Optional[models.Category]:
    """
    Activate category.
    
    Args:
        db: Database session
        category_id: Category UUID
        
    Returns:
        Updated category model or None if not found
    """
    db_category = get_category(db, category_id)
    if not db_category:
        return None
    
    db_category.is_active = True
    
    db.commit()
    db.refresh(db_category)
    
    return db_category


# ==================== Channel CRUD Operations ====================

def create_channel(db: Session, channel: schemas.ChannelCreate) -> models.Channel:
    """
    Create a new channel.
    
    Args:
        db: Database session
        channel: Channel creation schema
        
    Returns:
        Created channel model
        
    Raises:
        ValueError: If channel name already exists
    """
    # Check if name exists
    existing = db.execute(
        select(models.Channel).where(models.Channel.name == channel.name)
    ).scalar_one_or_none()
    if existing:
        raise ValueError(f"Channel '{channel.name}' already exists")
    
    db_channel = models.Channel(name=channel.name)
    
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    
    return db_channel


def get_channel(db: Session, channel_id: UUID) -> Optional[models.Channel]:
    """
    Get channel by ID.
    
    Args:
        db: Database session
        channel_id: Channel UUID
        
    Returns:
        Channel model or None if not found
    """
    return db.execute(
        select(models.Channel).where(models.Channel.id == channel_id)
    ).scalar_one_or_none()


def get_channel_by_name(db: Session, name: str) -> Optional[models.Channel]:
    """
    Get channel by name.
    
    Args:
        db: Database session
        name: Channel name
        
    Returns:
        Channel model or None if not found
    """
    return db.execute(
        select(models.Channel).where(models.Channel.name == name)
    ).scalar_one_or_none()


def get_channels(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False
) -> list[models.Channel]:
    """
    Get list of channels with optional filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_inactive: Include inactive channels
        
    Returns:
        List of channel models
    """
    query = select(models.Channel)
    
    if not include_inactive:
        query = query.where(models.Channel.is_active == True)
    
    query = query.offset(skip).limit(limit).order_by(models.Channel.name)
    
    return list(db.execute(query).scalars().all())


def update_channel(
    db: Session,
    channel_id: UUID,
    channel_update: schemas.ChannelUpdate
) -> Optional[models.Channel]:
    """
    Update channel information.
    
    Args:
        db: Database session
        channel_id: Channel UUID
        channel_update: Channel update schema
        
    Returns:
        Updated channel model or None if not found
        
    Raises:
        ValueError: If new name already exists for another channel
    """
    db_channel = get_channel(db, channel_id)
    if not db_channel:
        return None
    
    update_data = channel_update.model_dump(exclude_unset=True)
    
    # Check name uniqueness if being updated
    if 'name' in update_data and update_data['name'] != db_channel.name:
        existing = get_channel_by_name(db, update_data['name'])
        if existing and existing.id != channel_id:
            raise ValueError(f"Channel '{update_data['name']}' already exists")
    
    # Update fields
    for field, value in update_data.items():
        setattr(db_channel, field, value)
    
    db.commit()
    db.refresh(db_channel)
    
    return db_channel


def deactivate_channel(db: Session, channel_id: UUID) -> Optional[models.Channel]:
    """
    Deactivate channel.
    
    Args:
        db: Database session
        channel_id: Channel UUID
        
    Returns:
        Updated channel model or None if not found
    """
    db_channel = get_channel(db, channel_id)
    if not db_channel:
        return None
    
    db_channel.is_active = False
    
    db.commit()
    db.refresh(db_channel)
    
    return db_channel


def activate_channel(db: Session, channel_id: UUID) -> Optional[models.Channel]:
    """
    Activate channel.
    
    Args:
        db: Database session
        channel_id: Channel UUID
        
    Returns:
        Updated channel model or None if not found
    """
    db_channel = get_channel(db, channel_id)
    if not db_channel:
        return None
    
    db_channel.is_active = True
    
    db.commit()
    db.refresh(db_channel)
    
    return db_channel


# ==================== Case CRUD Operations ====================

def create_case(
    db: Session, 
    case: schemas.CaseCreate, 
    author_id: UUID
) -> models.Case:
    """
    Create a new case with a unique 6-digit public_id.
    
    Args:
        db: Database session
        case: Case creation schema
        author_id: UUID of the user creating the case (OPERATOR)
        
    Returns:
        Created case model
        
    Raises:
        ValueError: If category, channel, or responsible user doesn't exist
    """
    from app.utils import generate_unique_public_id
    from uuid import UUID as parse_uuid
    
    # Validate category exists and is active
    category = get_category(db, parse_uuid(case.category_id))
    if not category:
        raise ValueError(f"Category with id '{case.category_id}' not found")
    if not category.is_active:
        raise ValueError(f"Category '{category.name}' is not active")
    
    # Validate channel exists and is active
    channel = get_channel(db, parse_uuid(case.channel_id))
    if not channel:
        raise ValueError(f"Channel with id '{case.channel_id}' not found")
    if not channel.is_active:
        raise ValueError(f"Channel '{channel.name}' is not active")
    
    # Validate responsible user if provided
    responsible_id_uuid = None
    if case.responsible_id:
        responsible = get_user(db, parse_uuid(case.responsible_id))
        if not responsible:
            raise ValueError(f"Responsible user with id '{case.responsible_id}' not found")
        if responsible.role not in [models.UserRole.EXECUTOR, models.UserRole.ADMIN]:
            raise ValueError(f"User '{responsible.username}' cannot be assigned as responsible (must be EXECUTOR or ADMIN)")
        if not responsible.is_active:
            raise ValueError(f"User '{responsible.username}' is not active")
        responsible_id_uuid = parse_uuid(case.responsible_id)
    
    # Generate unique public_id
    public_id = generate_unique_public_id(db)
    
    # Create case
    db_case = models.Case(
        public_id=public_id,
        category_id=parse_uuid(case.category_id),
        channel_id=parse_uuid(case.channel_id),
        subcategory=case.subcategory,
        applicant_name=case.applicant_name,
        applicant_phone=case.applicant_phone,
        applicant_email=case.applicant_email,
        summary=case.summary,
        status=models.CaseStatus.NEW,
        author_id=author_id,
        responsible_id=responsible_id_uuid
    )
    
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    
    # Create initial status history record
    create_status_history(
        db=db,
        case_id=db_case.id,
        old_status=None,
        new_status=models.CaseStatus.NEW,
        changed_by_id=author_id
    )
    
    return db_case


def get_case(db: Session, case_id: UUID) -> Optional[models.Case]:
    """
    Get case by UUID.
    
    Args:
        db: Database session
        case_id: Case UUID
        
    Returns:
        Case model or None if not found
    """
    result = db.execute(
        select(models.Case).where(models.Case.id == case_id)
    )
    return result.scalar_one_or_none()


def get_case_by_public_id(db: Session, public_id: int) -> Optional[models.Case]:
    """
    Get case by public_id (6-digit number).
    
    Args:
        db: Database session
        public_id: 6-digit case identifier
        
    Returns:
        Case model or None if not found
    """
    result = db.execute(
        select(models.Case).where(models.Case.public_id == public_id)
    )
    return result.scalar_one_or_none()


def get_all_cases(
    db: Session,
    status: Optional[models.CaseStatus] = None,
    category_id: Optional[UUID] = None,
    channel_id: Optional[UUID] = None,
    author_id: Optional[UUID] = None,
    responsible_id: Optional[UUID] = None,
    public_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    overdue: Optional[bool] = None,
    order_by: Optional[str] = "-created_at",
    skip: int = 0,
    limit: int = 50,
    # BE-201: Extended filters
    subcategory: Optional[str] = None,
    applicant_name: Optional[str] = None,
    applicant_phone: Optional[str] = None,
    applicant_email: Optional[str] = None,
    updated_date_from: Optional[str] = None,
    updated_date_to: Optional[str] = None,
    statuses: Optional[list[models.CaseStatus]] = None,
    category_ids: Optional[list[UUID]] = None,
    channel_ids: Optional[list[UUID]] = None
) -> tuple[list[models.Case], int]:
    """
    Get all cases with optional filtering and sorting.
    
    Args:
        db: Database session
        status: Filter by case status (deprecated, use statuses for multiple)
        category_id: Filter by category (deprecated, use category_ids for multiple)
        channel_id: Filter by channel (deprecated, use channel_ids for multiple)
        author_id: Filter by author
        responsible_id: Filter by responsible user
        public_id: Filter by 6-digit public ID
        date_from: Filter by created date from (ISO format)
        date_to: Filter by created date to (ISO format)
        overdue: Filter overdue cases (requires SLA field - placeholder)
        order_by: Sort field (prefix with - for descending, e.g., -created_at)
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        
        # BE-201: Extended filters (all use AND logic)
        subcategory: Filter by subcategory (exact match or LIKE if contains %)
        applicant_name: Filter by applicant name (LIKE search, case-insensitive)
        applicant_phone: Filter by applicant phone (LIKE search)
        applicant_email: Filter by applicant email (LIKE search, case-insensitive)
        updated_date_from: Filter by updated date from (ISO format)
        updated_date_to: Filter by updated date to (ISO format)
        statuses: Filter by multiple statuses (OR within, AND with others)
        category_ids: Filter by multiple categories (OR within, AND with others)
        channel_ids: Filter by multiple channels (OR within, AND with others)
        
    Returns:
        Tuple of (list of cases, total count)
    """
    from datetime import datetime
    
    query = select(models.Case).options(
        joinedload(models.Case.category),
        joinedload(models.Case.channel),
        joinedload(models.Case.responsible)
    )
    
    # Apply filters (AND logic)
    # Single value filters (backward compatibility)
    if status:
        query = query.where(models.Case.status == status)
    if category_id:
        query = query.where(models.Case.category_id == category_id)
    if channel_id:
        query = query.where(models.Case.channel_id == channel_id)
    if author_id:
        query = query.where(models.Case.author_id == author_id)
    if responsible_id:
        query = query.where(models.Case.responsible_id == responsible_id)
    if public_id:
        query = query.where(models.Case.public_id == public_id)
    
    # BE-201: Multiple value filters (OR within the list, AND with other filters)
    if statuses and len(statuses) > 0:
        query = query.where(models.Case.status.in_(statuses))
    if category_ids and len(category_ids) > 0:
        query = query.where(models.Case.category_id.in_(category_ids))
    if channel_ids and len(channel_ids) > 0:
        query = query.where(models.Case.channel_id.in_(channel_ids))
    
    # BE-201: Subcategory filter
    if subcategory:
        if '%' in subcategory:
            # LIKE search if contains wildcard
            query = query.where(models.Case.subcategory.like(subcategory))
        else:
            # Exact match
            query = query.where(models.Case.subcategory == subcategory)
    
    # BE-201: Applicant filters (LIKE search, case-insensitive)
    if applicant_name:
        query = query.where(models.Case.applicant_name.ilike(f"%{applicant_name}%"))
    if applicant_phone:
        query = query.where(models.Case.applicant_phone.like(f"%{applicant_phone}%"))
    if applicant_email:
        query = query.where(models.Case.applicant_email.ilike(f"%{applicant_email}%"))
    
    # Date range filters (created_at)
    if date_from:
        try:
            date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            query = query.where(models.Case.created_at >= date_from_dt)
        except ValueError:
            pass  # Invalid date format, skip filter
    
    if date_to:
        try:
            date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            query = query.where(models.Case.created_at <= date_to_dt)
        except ValueError:
            pass  # Invalid date format, skip filter
    
    # BE-201: Date range filters (updated_at)
    if updated_date_from:
        try:
            updated_from_dt = datetime.fromisoformat(updated_date_from.replace('Z', '+00:00'))
            query = query.where(models.Case.updated_at >= updated_from_dt)
        except ValueError:
            pass  # Invalid date format, skip filter
    
    if updated_date_to:
        try:
            updated_to_dt = datetime.fromisoformat(updated_date_to.replace('Z', '+00:00'))
            query = query.where(models.Case.updated_at <= updated_to_dt)
        except ValueError:
            pass  # Invalid date format, skip filter
    
    # Overdue filter (placeholder - will be implemented when SLA fields are added)
    # For now, we'll mark cases as overdue if they're in NEW or IN_PROGRESS status
    # and older than 7 days
    if overdue is not None:
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        if overdue:
            # Cases that are overdue: old and not resolved
            query = query.where(
                models.Case.created_at < seven_days_ago,
                models.Case.status.in_([models.CaseStatus.NEW, models.CaseStatus.IN_PROGRESS])
            )
        else:
            # Cases that are not overdue
            from sqlalchemy import or_
            query = query.where(
                or_(
                    models.Case.created_at >= seven_days_ago,
                    models.Case.status.in_([models.CaseStatus.DONE, models.CaseStatus.REJECTED])
                )
            )
    
    # Get total count BEFORE applying joins and pagination
    # Create a count query from the current filter conditions
    from sqlalchemy import func
    count_query = select(func.count()).select_from(models.Case)
    
    # Re-apply all the same filters for counting
    if status:
        count_query = count_query.where(models.Case.status == status)
    if category_id:
        count_query = count_query.where(models.Case.category_id == category_id)
    if channel_id:
        count_query = count_query.where(models.Case.channel_id == channel_id)
    if author_id:
        count_query = count_query.where(models.Case.author_id == author_id)
    if responsible_id:
        count_query = count_query.where(models.Case.responsible_id == responsible_id)
    if public_id:
        count_query = count_query.where(models.Case.public_id == public_id)
    
    # BE-201: Multiple value filters
    if statuses and len(statuses) > 0:
        count_query = count_query.where(models.Case.status.in_(statuses))
    if category_ids and len(category_ids) > 0:
        count_query = count_query.where(models.Case.category_id.in_(category_ids))
    if channel_ids and len(channel_ids) > 0:
        count_query = count_query.where(models.Case.channel_id.in_(channel_ids))
    
    # BE-201: Subcategory filter
    if subcategory:
        if '%' in subcategory:
            count_query = count_query.where(models.Case.subcategory.like(subcategory))
        else:
            count_query = count_query.where(models.Case.subcategory == subcategory)
    
    # BE-201: Applicant filters
    if applicant_name:
        count_query = count_query.where(models.Case.applicant_name.ilike(f"%{applicant_name}%"))
    if applicant_phone:
        count_query = count_query.where(models.Case.applicant_phone.like(f"%{applicant_phone}%"))
    if applicant_email:
        count_query = count_query.where(models.Case.applicant_email.ilike(f"%{applicant_email}%"))
    
    # Date range filters (created_at)
    if date_from:
        try:
            date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            count_query = count_query.where(models.Case.created_at >= date_from_dt)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            count_query = count_query.where(models.Case.created_at <= date_to_dt)
        except ValueError:
            pass
    
    # BE-201: Date range filters (updated_at)
    if updated_date_from:
        try:
            updated_from_dt = datetime.fromisoformat(updated_date_from.replace('Z', '+00:00'))
            count_query = count_query.where(models.Case.updated_at >= updated_from_dt)
        except ValueError:
            pass
    
    if updated_date_to:
        try:
            updated_to_dt = datetime.fromisoformat(updated_date_to.replace('Z', '+00:00'))
            count_query = count_query.where(models.Case.updated_at <= updated_to_dt)
        except ValueError:
            pass
    
    # Overdue filter
    if overdue is not None:
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        if overdue:
            count_query = count_query.where(
                models.Case.created_at < seven_days_ago,
                models.Case.status.in_([models.CaseStatus.NEW, models.CaseStatus.IN_PROGRESS])
            )
        else:
            from sqlalchemy import or_
            count_query = count_query.where(
                or_(
                    models.Case.created_at >= seven_days_ago,
                    models.Case.status.in_([models.CaseStatus.DONE, models.CaseStatus.REJECTED])
                )
            )
    
    # Execute count query
    total = db.execute(count_query).scalar() or 0
    
    # Apply sorting
    if order_by:
        if order_by.startswith('-'):
            # Descending order
            field_name = order_by[1:]
            if hasattr(models.Case, field_name):
                query = query.order_by(getattr(models.Case, field_name).desc())
            else:
                # Default to created_at descending
                query = query.order_by(models.Case.created_at.desc())
        else:
            # Ascending order
            if hasattr(models.Case, order_by):
                query = query.order_by(getattr(models.Case, order_by).asc())
            else:
                # Default to created_at descending
                query = query.order_by(models.Case.created_at.desc())
    else:
        # Default sorting
        query = query.order_by(models.Case.created_at.desc())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = db.execute(query)
    cases = result.scalars().all()
    
    return list(cases), total


def update_case(
    db: Session,
    case_id: UUID,
    case_update: schemas.CaseUpdate
) -> Optional[models.Case]:
    """
    Update case information.
    
    Args:
        db: Database session
        case_id: Case UUID
        case_update: Case update schema
        
    Returns:
        Updated case model or None if not found
        
    Raises:
        ValueError: If category, channel, or responsible user doesn't exist or is invalid
    """
    from uuid import UUID as parse_uuid
    
    db_case = get_case(db, case_id)
    if not db_case:
        return None
    
    # Update fields if provided
    if case_update.category_id is not None:
        category = get_category(db, parse_uuid(case_update.category_id))
        if not category:
            raise ValueError(f"Category with id '{case_update.category_id}' not found")
        if not category.is_active:
            raise ValueError(f"Category '{category.name}' is not active")
        db_case.category_id = parse_uuid(case_update.category_id)
    
    if case_update.channel_id is not None:
        channel = get_channel(db, parse_uuid(case_update.channel_id))
        if not channel:
            raise ValueError(f"Channel with id '{case_update.channel_id}' not found")
        if not channel.is_active:
            raise ValueError(f"Channel '{channel.name}' is not active")
        db_case.channel_id = parse_uuid(case_update.channel_id)
    
    if case_update.subcategory is not None:
        db_case.subcategory = case_update.subcategory
    
    if case_update.applicant_name is not None:
        db_case.applicant_name = case_update.applicant_name
    
    if case_update.applicant_phone is not None:
        db_case.applicant_phone = case_update.applicant_phone
    
    if case_update.applicant_email is not None:
        db_case.applicant_email = case_update.applicant_email
    
    if case_update.summary is not None:
        db_case.summary = case_update.summary
    
    if case_update.status is not None and case_update.status != db_case.status:
        # Log status change
        old_status = db_case.status
        db_case.status = case_update.status
        
        # Note: changed_by_id should be passed separately, using case author for now
        # This should be updated when we add user context to update operations
    
    if case_update.responsible_id is not None:
        if case_update.responsible_id == "":  # Allow clearing responsible
            db_case.responsible_id = None
        else:
            responsible = get_user(db, parse_uuid(case_update.responsible_id))
            if not responsible:
                raise ValueError(f"Responsible user with id '{case_update.responsible_id}' not found")
            if responsible.role not in [models.UserRole.EXECUTOR, models.UserRole.ADMIN]:
                raise ValueError(f"User '{responsible.username}' cannot be assigned as responsible (must be EXECUTOR or ADMIN)")
            if not responsible.is_active:
                raise ValueError(f"User '{responsible.username}' is not active")
            db_case.responsible_id = parse_uuid(case_update.responsible_id)
    
    db.commit()
    db.refresh(db_case)
    
    return db_case


def delete_case(db: Session, case_id: UUID) -> bool:
    """
    Delete case by ID (hard delete).
    
    Note: This will cascade delete all attachments.
    
    Args:
        db: Database session
        case_id: Case UUID
        
    Returns:
        True if case was deleted, False if not found
    """
    db_case = get_case(db, case_id)
    if not db_case:
        return False
    
    db.delete(db_case)
    db.commit()
    
    return True


def get_executors_for_category(
    db: Session,
    category_id: UUID
) -> list[models.User]:
    """
    Get all active executors (users with EXECUTOR or ADMIN role).
    
    Note: In the future, this can be enhanced to filter by category assignment.
    For now, returns all active executors.
    
    Args:
        db: Database session
        category_id: Category UUID (currently not used, for future enhancement)
        
    Returns:
        List of executor users
    """
    query = select(models.User).where(
        models.User.role.in_([models.UserRole.EXECUTOR, models.UserRole.ADMIN]),
        models.User.is_active == True
    )
    
    return list(db.execute(query).scalars().all())


# ==================== Attachment CRUD Operations ====================

def create_attachment(
    db: Session,
    case_id: UUID,
    file_path: str,
    original_name: str,
    size_bytes: int,
    mime_type: str,
    uploaded_by_id: UUID
) -> models.Attachment:
    """
    Create a new attachment record.
    
    Args:
        db: Database session
        case_id: UUID of the case
        file_path: Relative path from MEDIA_ROOT
        original_name: Original filename
        size_bytes: File size in bytes
        mime_type: MIME type
        uploaded_by_id: UUID of user uploading the file
        
    Returns:
        Created attachment model
        
    Raises:
        ValueError: If case doesn't exist
    """
    # Verify case exists
    case = get_case(db, case_id)
    if not case:
        raise ValueError(f"Case with id '{case_id}' not found")
    
    db_attachment = models.Attachment(
        case_id=case_id,
        file_path=file_path,
        original_name=original_name,
        size_bytes=size_bytes,
        mime_type=mime_type,
        uploaded_by_id=uploaded_by_id
    )
    
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    
    return db_attachment


def get_attachment(db: Session, attachment_id: UUID) -> Optional[models.Attachment]:
    """
    Get attachment by ID.
    
    Args:
        db: Database session
        attachment_id: Attachment UUID
        
    Returns:
        Attachment model or None if not found
    """
    return db.execute(
        select(models.Attachment).where(models.Attachment.id == attachment_id)
    ).scalar_one_or_none()


def get_case_attachments(
    db: Session,
    case_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> list[models.Attachment]:
    """
    Get all attachments for a specific case.
    
    Args:
        db: Database session
        case_id: Case UUID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of attachment models
    """
    query = select(models.Attachment).where(
        models.Attachment.case_id == case_id
    ).order_by(models.Attachment.created_at.desc()).offset(skip).limit(limit)
    
    return list(db.execute(query).scalars().all())


def delete_attachment(db: Session, attachment_id: UUID) -> bool:
    """
    Delete attachment record from database.
    
    Note: This does NOT delete the physical file. File deletion should be
    handled separately by the calling code.
    
    Args:
        db: Database session
        attachment_id: Attachment UUID
        
    Returns:
        True if attachment was deleted, False if not found
    """
    db_attachment = get_attachment(db, attachment_id)
    if not db_attachment:
        return False
    
    db.delete(db_attachment)
    db.commit()
    
    return True


# ==================== Comment CRUD Operations ====================

def get_case_comments(
    db: Session,
    case_id: UUID,
    include_internal: bool = False
) -> list[models.Comment]:
    """
    Get all comments for a specific case.
    
    Args:
        db: Database session
        case_id: Case UUID
        include_internal: Include internal comments (default: False)
        
    Returns:
        List of comment models
    """
    query = select(models.Comment).where(
        models.Comment.case_id == case_id
    )
    
    if not include_internal:
        query = query.where(models.Comment.is_internal == False)
    
    query = query.order_by(models.Comment.created_at.asc())
    
    return list(db.execute(query).scalars().all())


def has_access_to_internal_comments(
    db: Session,
    user: models.User,
    case: models.Case
) -> bool:
    """
    Check if user has access to internal comments for a case.
    
    Rules:
    - ADMIN: Always has access
    - EXECUTOR: Has access if they are executors (future: in case category)
    - OPERATOR: No access to internal comments
    
    Args:
        db: Database session
        user: User model
        case: Case model
        
    Returns:
        True if user has access to internal comments
    """
    # ADMIN always has access
    if user.role == models.UserRole.ADMIN:
        return True
    
    # EXECUTOR has access (future: only to their categories)
    if user.role == models.UserRole.EXECUTOR:
        return True
    
    # OPERATOR has no access
    return False


# ==================== Status History CRUD Operations ====================

def get_status_history(
    db: Session,
    case_id: UUID
) -> list[models.StatusHistory]:
    """
    Get status change history for a specific case.
    
    Args:
        db: Database session
        case_id: Case UUID
        
    Returns:
        List of status history records ordered by change time
    """
    query = select(models.StatusHistory).where(
        models.StatusHistory.case_id == case_id
    ).order_by(models.StatusHistory.changed_at.asc())
    
    return list(db.execute(query).scalars().all())


def create_status_history(
    db: Session,
    case_id: UUID,
    old_status: Optional[models.CaseStatus],
    new_status: models.CaseStatus,
    changed_by_id: UUID
) -> models.StatusHistory:
    """
    Create a status history record.
    
    Args:
        db: Database session
        case_id: Case UUID
        old_status: Previous status (None for initial status)
        new_status: New status
        changed_by_id: User who made the change
        
    Returns:
        Created status history model
    """
    db_history = models.StatusHistory(
        case_id=case_id,
        old_status=old_status,
        new_status=new_status,
        changed_by_id=changed_by_id
    )
    
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    
    return db_history


def take_case(
    db: Session,
    case_id: UUID,
    executor_id: UUID
) -> models.Case:
    """
    Take a case into work by an executor.
    
    Changes:
    - Sets responsible_id to current executor
    - Changes status from NEW to IN_PROGRESS
    - Creates status history record
    
    Args:
        db: Database session
        case_id: Case UUID
        executor_id: Executor user UUID
        
    Returns:
        Updated case model
        
    Raises:
        ValueError: If case not found, not in NEW status, or executor invalid
    """
    # Get case
    db_case = get_case(db, case_id)
    if not db_case:
        raise ValueError(f"Case with id '{case_id}' not found")
    
    # Validate status
    if db_case.status != models.CaseStatus.NEW:
        raise ValueError(f"Case can only be taken when status is NEW. Current status: {db_case.status.value}")
    
    # Validate executor
    executor = get_user(db, executor_id)
    if not executor:
        raise ValueError(f"Executor with id '{executor_id}' not found")
    
    if executor.role not in [models.UserRole.EXECUTOR, models.UserRole.ADMIN]:
        raise ValueError(f"User must be EXECUTOR or ADMIN to take cases. Current role: {executor.role.value}")
    
    if not executor.is_active:
        raise ValueError(f"Executor '{executor.username}' is not active")
    
    # Update case
    old_status = db_case.status
    db_case.status = models.CaseStatus.IN_PROGRESS
    db_case.responsible_id = executor_id
    
    db.commit()
    db.refresh(db_case)
    
    # Create status history record
    create_status_history(
        db=db,
        case_id=case_id,
        old_status=old_status,
        new_status=models.CaseStatus.IN_PROGRESS,
        changed_by_id=executor_id
    )
    
    return db_case


def change_case_status(
    db: Session,
    case_id: UUID,
    executor_id: UUID,
    to_status: models.CaseStatus,
    comment_text: str
) -> models.Case:
    """
    Change case status with mandatory comment.
    
    This function is used by the responsible executor to change case status
    from IN_PROGRESS to NEEDS_INFO, REJECTED, or DONE.
    
    Business rules:
    - Only responsible executor can change status
    - Comment is mandatory
    - Valid transitions from IN_PROGRESS:
        * IN_PROGRESS -> IN_PROGRESS (with comment)
        * IN_PROGRESS -> NEEDS_INFO (additional info required)
        * IN_PROGRESS -> REJECTED (case rejected)
        * IN_PROGRESS -> DONE (case completed)
    - Cases in DONE or REJECTED status cannot be edited (except comments)
    
    Args:
        db: Database session
        case_id: Case UUID
        executor_id: UUID of the executor changing status
        to_status: Target status
        comment_text: Mandatory comment explaining the change
        
    Returns:
        Updated case model with new status
        
    Raises:
        ValueError: If validation fails (case not found, not responsible, invalid transition, etc.)
    """
    # Get case
    db_case = get_case(db, case_id)
    if not db_case:
        raise ValueError(f"Case with id '{case_id}' not found")
    
    # Validate executor
    executor = get_user(db, executor_id)
    if not executor:
        raise ValueError(f"Executor with id '{executor_id}' not found")
    
    # Only responsible executor can change status
    if db_case.responsible_id != executor_id:
        raise ValueError(
            f"Only the responsible executor can change case status. "
            f"Current responsible: {db_case.responsible_id}, "
            f"Requesting user: {executor_id}"
        )
    
    # Validate executor role
    if executor.role not in [models.UserRole.EXECUTOR, models.UserRole.ADMIN]:
        raise ValueError(
            f"Only EXECUTOR or ADMIN can change case status. "
            f"Current role: {executor.role.value}"
        )
    
    # Validate status transition
    current_status = db_case.status
    
    # Define valid transitions
    valid_transitions = {
        models.CaseStatus.IN_PROGRESS: [
            models.CaseStatus.IN_PROGRESS,  # Allow staying in progress with comment
            models.CaseStatus.NEEDS_INFO,
            models.CaseStatus.REJECTED,
            models.CaseStatus.DONE
        ],
        # Allow changes from NEEDS_INFO back to IN_PROGRESS or to final states
        models.CaseStatus.NEEDS_INFO: [
            models.CaseStatus.IN_PROGRESS,
            models.CaseStatus.REJECTED,
            models.CaseStatus.DONE
        ]
    }
    
    # Check if current status allows transitions
    if current_status not in valid_transitions:
        raise ValueError(
            f"Cannot change status from {current_status.value}. "
            f"Status changes are only allowed from IN_PROGRESS or NEEDS_INFO."
        )
    
    # Check if target status is valid for current status
    if to_status not in valid_transitions[current_status]:
        allowed = ", ".join([s.value for s in valid_transitions[current_status]])
        raise ValueError(
            f"Invalid status transition: {current_status.value} -> {to_status.value}. "
            f"Allowed transitions: {allowed}"
        )
    
    # Validate comment
    if not comment_text or len(comment_text.strip()) < 10:
        raise ValueError("Comment is mandatory and must be at least 10 characters")
    
    # Update case status (only if it actually changes)
    old_status = db_case.status
    if old_status != to_status:
        db_case.status = to_status
        db.commit()
        db.refresh(db_case)
        
        # Create status history record
        create_status_history(
            db=db,
            case_id=case_id,
            old_status=old_status,
            new_status=to_status,
            changed_by_id=executor_id
        )
    
    # Create comment (internal comment visible to executors/admin)
    db_comment = models.Comment(
        case_id=case_id,
        author_id=executor_id,
        text=comment_text,
        is_internal=True  # Internal comment for status changes
    )
    
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    return db_case


# ==================== Comment CRUD ====================

def create_comment(
    db: Session,
    case_id: UUID,
    author_id: UUID,
    text: str,
    is_internal: bool = False
) -> models.Comment:
    """
    Створює новий коментар до звернення.
    
    Args:
        db: Database session
        case_id: UUID звернення
        author_id: UUID автора коментаря
        text: Текст коментаря
        is_internal: Чи є коментар внутрішнім (за замовчуванням False)
        
    Returns:
        Створений коментар
    """
    db_comment = models.Comment(
        case_id=case_id,
        author_id=author_id,
        text=text,
        is_internal=is_internal
    )
    
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    return db_comment


def get_comments_by_case(
    db: Session,
    case_id: UUID,
    user_role: models.UserRole,
    user_id: Optional[UUID] = None
) -> list[models.Comment]:
    """
    Отримує коментарі звернення з урахуванням RBAC.
    
    RBAC Rules:
    - OPERATOR: Бачить тільки публічні коментарі
    - EXECUTOR: Бачить всі коментарі (публічні + внутрішні)
    - ADMIN: Бачить всі коментарі
    
    Args:
        db: Database session
        case_id: UUID звернення
        user_role: Роль користувача
        user_id: UUID користувача (опціонально)
        
    Returns:
        Список коментарів з урахуванням прав доступу
    """
    query = select(models.Comment).where(models.Comment.case_id == case_id)
    
    # RBAC фільтрація
    if user_role == models.UserRole.OPERATOR:
        # OPERATOR бачить тільки публічні коментарі
        query = query.where(models.Comment.is_internal == False)
    # EXECUTOR та ADMIN бачать всі коментарі
    
    # Сортування за датою створення
    query = query.order_by(models.Comment.created_at.asc())
    
    comments = db.execute(query).scalars().all()
    return list(comments)


# ==================== User Management CRUD (ADMIN) ====================

def reset_user_password(
    db: Session,
    user_id: UUID,
    new_password: str
) -> Optional[models.User]:
    """
    Скидає пароль користувача на новий (тимчасовий).
    
    Args:
        db: Database session
        user_id: UUID користувача
        new_password: Новий пароль (буде захешований)
        
    Returns:
        Оновлену модель користувача або None якщо не знайдено
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.password_hash = hash_password(new_password)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


def get_user_active_cases(
    db: Session,
    user_id: UUID
) -> list[models.Case]:
    """
    Отримує список активних звернень користувача (як виконавця).
    
    Активні звернення: статус IN_PROGRESS або NEEDS_INFO
    
    Args:
        db: Database session
        user_id: UUID користувача (виконавця)
        
    Returns:
        Список активних звернень
    """
    query = select(models.Case).where(
        models.Case.responsible_id == user_id,
        models.Case.status.in_([models.CaseStatus.IN_PROGRESS, models.CaseStatus.NEEDS_INFO])
    )
    
    cases = db.execute(query).scalars().all()
    return list(cases)


def deactivate_user_with_check(
    db: Session,
    user_id: UUID,
    force: bool = False
) -> tuple[bool, Optional[str], Optional[list[str]]]:
    """
    Деактивує користувача з перевіркою активних звернень.
    
    Для EXECUTOR: перевіряє наявність активних звернень (IN_PROGRESS, NEEDS_INFO).
    Якщо є активні звернення і force=False, повертає помилку зі списком.
    
    Args:
        db: Database session
        user_id: UUID користувача
        force: Примусова деактивація (за замовчуванням False)
        
    Returns:
        Tuple (success, error_message, active_case_ids)
        - success: True якщо деактивовано успішно
        - error_message: Повідомлення про помилку (якщо є)
        - active_case_ids: Список UUID активних звернень (якщо є)
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return False, "User not found", None
    
    # Перевірка активних звернень для EXECUTOR
    if db_user.role == models.UserRole.EXECUTOR and not force:
        active_cases = get_user_active_cases(db, user_id)
        
        if active_cases:
            case_ids = [str(case.id) for case in active_cases]
            error_msg = (
                f"Cannot deactivate user '{db_user.username}': "
                f"{len(active_cases)} active case(s) found. "
                f"Please reassign or complete these cases first, or use force=true."
            )
            return False, error_msg, case_ids
    
    # Деактивація користувача
    db_user.is_active = False
    db.commit()
    db.refresh(db_user)
    
    return True, None, None


# ============================================================================
# Notification Log CRUD
# ============================================================================

def create_notification_log(
    db: Session,
    notification_type: models.NotificationType,
    recipient_email: str,
    subject: str,
    body_text: Optional[str] = None,
    body_html: Optional[str] = None,
    recipient_user_id: Optional[UUID] = None,
    related_case_id: Optional[UUID] = None,
    related_entity_id: Optional[str] = None,
    celery_task_id: Optional[str] = None,
) -> models.NotificationLog:
    """
    Створює запис в логу нотифікацій.
    
    Args:
        db: Database session
        notification_type: Тип нотифікації (NEW_CASE, CASE_TAKEN, etc.)
        recipient_email: Email отримувача
        subject: Тема листа
        body_text: Текстова версія листа
        body_html: HTML версія листа
        recipient_user_id: UUID отримувача (якщо є)
        related_case_id: UUID пов'язаного звернення
        related_entity_id: ID іншої пов'язаної сутності
        celery_task_id: ID Celery таски
        
    Returns:
        Created notification log entry
    """
    notification = models.NotificationLog(
        notification_type=notification_type,
        recipient_email=recipient_email,
        recipient_user_id=recipient_user_id,
        related_case_id=related_case_id,
        related_entity_id=related_entity_id,
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        status=models.NotificationStatus.PENDING,
        celery_task_id=celery_task_id,
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification


def update_notification_status(
    db: Session,
    notification_id: UUID,
    status: models.NotificationStatus,
    error_message: Optional[str] = None,
    error_details: Optional[str] = None,
) -> Optional[models.NotificationLog]:
    """
    Оновлює статус нотифікації.
    
    Args:
        db: Database session
        notification_id: UUID нотифікації
        status: Новий статус (SENT, FAILED, RETRYING)
        error_message: Повідомлення про помилку
        error_details: Детальна інформація про помилку
        
    Returns:
        Updated notification log or None if not found
    """
    notification = db.execute(
        select(models.NotificationLog).where(
            models.NotificationLog.id == notification_id
        )
    ).scalar_one_or_none()
    
    if not notification:
        return None
    
    notification.status = status
    
    if status == models.NotificationStatus.SENT:
        from datetime import datetime
        notification.sent_at = datetime.utcnow()
    elif status == models.NotificationStatus.FAILED:
        from datetime import datetime
        notification.failed_at = datetime.utcnow()
        if error_message:
            notification.last_error = error_message
        if error_details:
            notification.error_details = error_details
    elif status == models.NotificationStatus.RETRYING:
        notification.retry_count += 1
        if error_message:
            notification.last_error = error_message
    
    db.commit()
    db.refresh(notification)
    
    return notification


def get_pending_notifications(
    db: Session,
    limit: int = 100
) -> list[models.NotificationLog]:
    """
    Отримує нотифікації в статусі PENDING або RETRYING для повторної відправки.
    
    Args:
        db: Database session
        limit: Максимальна кількість записів
        
    Returns:
        List of pending notifications
    """
    from datetime import datetime
    
    query = select(models.NotificationLog).where(
        models.NotificationLog.status.in_([
            models.NotificationStatus.PENDING,
            models.NotificationStatus.RETRYING
        ]),
        models.NotificationLog.retry_count < models.NotificationLog.max_retries
    ).order_by(
        models.NotificationLog.created_at.asc()
    ).limit(limit)
    
    # Фільтр для ретраїв: тільки ті, у яких настав час next_retry_at
    query = query.where(
        (models.NotificationLog.next_retry_at.is_(None)) |
        (models.NotificationLog.next_retry_at <= datetime.utcnow())
    )
    
    notifications = db.execute(query).scalars().all()
    return list(notifications)


def get_notification_stats(db: Session) -> dict:
    """
    Отримує статистику по нотифікаціям.
    
    Returns:
        Dictionary with counts by status
    """
    from sqlalchemy import func
    
    stats = {}
    
    for status in models.NotificationStatus:
        count = db.execute(
            select(func.count(models.NotificationLog.id)).where(
                models.NotificationLog.status == status
            )
        ).scalar()
        stats[status.value] = count
    
    return stats


# ==================== BE-301: Dashboard Analytics Functions ====================

def get_dashboard_summary(
    db: Session,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> dict:
    """
    Отримує загальну статистику звернень для дашборду.
    
    Args:
        db: Database session
        date_from: Початок періоду (ISO format)
        date_to: Кінець періоду (ISO format)
        
    Returns:
        Dictionary with summary statistics
    """
    from sqlalchemy import func
    from datetime import datetime
    
    # Базовий запит
    query = select(models.Case)
    
    # Фільтрація по даті створення
    if date_from:
        date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        query = query.where(models.Case.created_at >= date_from_dt)
    
    if date_to:
        date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        query = query.where(models.Case.created_at <= date_to_dt)
    
    # Отримуємо загальну кількість
    total_cases = db.execute(
        select(func.count(models.Case.id)).select_from(query.subquery())
    ).scalar() or 0
    
    # Рахуємо по статусах
    status_counts = {}
    for status in models.CaseStatus:
        count_query = query.where(models.Case.status == status)
        count = db.execute(
            select(func.count(models.Case.id)).select_from(count_query.subquery())
        ).scalar() or 0
        status_counts[status.value] = count
    
    return {
        'total_cases': total_cases,
        'new_cases': status_counts.get('NEW', 0),
        'in_progress_cases': status_counts.get('IN_PROGRESS', 0),
        'needs_info_cases': status_counts.get('NEEDS_INFO', 0),
        'rejected_cases': status_counts.get('REJECTED', 0),
        'done_cases': status_counts.get('DONE', 0),
        'period_start': datetime.fromisoformat(date_from.replace('Z', '+00:00')) if date_from else None,
        'period_end': datetime.fromisoformat(date_to.replace('Z', '+00:00')) if date_to else None,
    }


def get_status_distribution(
    db: Session,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> dict:
    """
    Отримує розподіл звернень по статусах.
    
    Args:
        db: Database session
        date_from: Початок періоду (ISO format)
        date_to: Кінець періоду (ISO format)
        
    Returns:
        Dictionary with status distribution
    """
    from sqlalchemy import func
    from datetime import datetime
    
    # Базовий запит
    query = select(models.Case)
    
    # Фільтрація по даті
    if date_from:
        date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        query = query.where(models.Case.created_at >= date_from_dt)
    
    if date_to:
        date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        query = query.where(models.Case.created_at <= date_to_dt)
    
    # Загальна кількість
    total_cases = db.execute(
        select(func.count(models.Case.id)).select_from(query.subquery())
    ).scalar() or 0
    
    # Розподіл по статусах
    distribution = []
    for status in models.CaseStatus:
        count_query = query.where(models.Case.status == status)
        count = db.execute(
            select(func.count(models.Case.id)).select_from(count_query.subquery())
        ).scalar() or 0
        
        percentage = (count / total_cases * 100) if total_cases > 0 else 0.0
        
        distribution.append({
            'status': status,
            'count': count,
            'percentage': round(percentage, 2)
        })
    
    return {
        'total_cases': total_cases,
        'distribution': distribution,
        'period_start': datetime.fromisoformat(date_from.replace('Z', '+00:00')) if date_from else None,
        'period_end': datetime.fromisoformat(date_to.replace('Z', '+00:00')) if date_to else None,
    }


def get_overdue_cases(db: Session) -> dict:
    """
    Отримує список прострочених звернень (>3 днів в статусі NEW).
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with overdue cases list
    """
    from datetime import datetime, timedelta
    
    # Дата 3 дні тому
    three_days_ago = datetime.utcnow() - timedelta(days=3)
    
    # Запит прострочених звернень
    query = (
        select(models.Case)
        .options(joinedload(models.Case.category))
        .options(joinedload(models.Case.responsible))
        .where(models.Case.status == models.CaseStatus.NEW)
        .where(models.Case.created_at <= three_days_ago)
        .order_by(models.Case.created_at.asc())
    )
    
    overdue_cases = db.execute(query).scalars().all()
    
    # Формуємо список
    cases_list = []
    for case in overdue_cases:
        days_overdue = (datetime.utcnow() - case.created_at).days
        
        cases_list.append({
            'id': str(case.id),
            'public_id': case.public_id,
            'category_name': case.category.name if case.category else 'Unknown',
            'applicant_name': case.applicant_name,
            'created_at': case.created_at,
            'days_overdue': days_overdue,
            'responsible_id': str(case.responsible_id) if case.responsible_id else None,
            'responsible_name': case.responsible.full_name if case.responsible else None,
        })
    
    return {
        'total_overdue': len(cases_list),
        'cases': cases_list
    }


def get_executors_efficiency(
    db: Session,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> dict:
    """
    Отримує статистику ефективності виконавців.
    
    Args:
        db: Database session
        date_from: Початок періоду для підрахунку завершених (ISO format)
        date_to: Кінець періоду для підрахунку завершених (ISO format)
        
    Returns:
        Dictionary with executors efficiency data
    """
    from sqlalchemy import func, and_
    from datetime import datetime, timedelta
    
    # Отримуємо всіх виконавців
    executors = db.execute(
        select(models.User)
        .where(models.User.role == models.UserRole.EXECUTOR)
        .where(models.User.is_active == True)
    ).scalars().all()
    
    executors_data = []
    
    for executor in executors:
        # Отримуємо категорії виконавця
        executor_categories = db.execute(
            select(models.ExecutorCategory)
            .options(joinedload(models.ExecutorCategory.category))
            .where(models.ExecutorCategory.user_id == executor.id)
        ).scalars().all()
        
        category_names = [ec.category.name for ec in executor_categories if ec.category]
        
        # Кількість звернень в роботі зараз
        current_in_progress = db.execute(
            select(func.count(models.Case.id)).where(
                and_(
                    models.Case.responsible_id == executor.id,
                    models.Case.status == models.CaseStatus.IN_PROGRESS
                )
            )
        ).scalar() or 0
        
        # Завершені в періоді
        completed_query = select(func.count(models.Case.id)).where(
            and_(
                models.Case.responsible_id == executor.id,
                models.Case.status == models.CaseStatus.DONE
            )
        )
        
        if date_from:
            date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            completed_query = completed_query.where(models.Case.updated_at >= date_from_dt)
        
        if date_to:
            date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            completed_query = completed_query.where(models.Case.updated_at <= date_to_dt)
        
        completed_in_period = db.execute(completed_query).scalar() or 0
        
        # Середній час виконання (в днях) для завершених в періоді
        avg_completion_days = None
        if completed_in_period > 0:
            completed_cases_query = select(models.Case).where(
                and_(
                    models.Case.responsible_id == executor.id,
                    models.Case.status == models.CaseStatus.DONE
                )
            )
            
            if date_from:
                completed_cases_query = completed_cases_query.where(
                    models.Case.updated_at >= date_from_dt
                )
            
            if date_to:
                completed_cases_query = completed_cases_query.where(
                    models.Case.updated_at <= date_to_dt
                )
            
            completed_cases = db.execute(completed_cases_query).scalars().all()
            
            total_days = 0
            for case in completed_cases:
                # Різниця між created_at та updated_at
                delta = case.updated_at - case.created_at
                total_days += delta.days
            
            avg_completion_days = round(total_days / completed_in_period, 1) if completed_in_period > 0 else None
        
        # Прострочені (>3 днів в NEW) з відповідальним = executor
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        overdue_count = db.execute(
            select(func.count(models.Case.id)).where(
                and_(
                    models.Case.responsible_id == executor.id,
                    models.Case.status == models.CaseStatus.NEW,
                    models.Case.created_at <= three_days_ago
                )
            )
        ).scalar() or 0
        
        executors_data.append({
            'user_id': str(executor.id),
            'full_name': executor.full_name,
            'email': executor.email,
            'categories': category_names,
            'current_in_progress': current_in_progress,
            'completed_in_period': completed_in_period,
            'avg_completion_days': avg_completion_days,
            'overdue_count': overdue_count,
        })
    
    return {
        'period_start': datetime.fromisoformat(date_from.replace('Z', '+00:00')) if date_from else None,
        'period_end': datetime.fromisoformat(date_to.replace('Z', '+00:00')) if date_to else None,
        'executors': executors_data
    }


def get_top_categories(
    db: Session,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 5
) -> dict:
    """
    Отримує ТОП категорій по кількості звернень.
    
    Args:
        db: Database session
        date_from: Початок періоду (ISO format)
        date_to: Кінець періоду (ISO format)
        limit: Кількість категорій в топі (за замовчуванням 5)
        
    Returns:
        Dictionary with top categories
    """
    from sqlalchemy import func
    from datetime import datetime
    
    # Базовий запит
    query = select(models.Case)
    
    # Фільтрація по даті
    if date_from:
        date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        query = query.where(models.Case.created_at >= date_from_dt)
    
    if date_to:
        date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        query = query.where(models.Case.created_at <= date_to_dt)
    
    # Загальна кількість звернень
    total_cases_all = db.execute(
        select(func.count(models.Case.id)).select_from(query.subquery())
    ).scalar() or 0
    
    # Групуємо по категоріях та рахуємо
    category_stats_query = (
        select(
            models.Case.category_id,
            func.count(models.Case.id).label('total_count')
        )
        .select_from(query.subquery())
        .group_by(models.Case.category_id)
        .order_by(func.count(models.Case.id).desc())
        .limit(limit)
    )
    
    category_stats = db.execute(category_stats_query).all()
    
    # Формуємо детальну статистику для кожної категорії
    top_categories = []
    for category_id, total_count in category_stats:
        # Отримуємо категорію
        category = db.execute(
            select(models.Category).where(models.Category.id == category_id)
        ).scalar_one_or_none()
        
        if not category:
            continue
        
        # Рахуємо по статусах для цієї категорії
        category_query = query.where(models.Case.category_id == category_id)
        
        new_count = db.execute(
            select(func.count(models.Case.id))
            .select_from(category_query.where(models.Case.status == models.CaseStatus.NEW).subquery())
        ).scalar() or 0
        
        in_progress_count = db.execute(
            select(func.count(models.Case.id))
            .select_from(category_query.where(models.Case.status == models.CaseStatus.IN_PROGRESS).subquery())
        ).scalar() or 0
        
        completed_count = db.execute(
            select(func.count(models.Case.id))
            .select_from(category_query.where(models.Case.status == models.CaseStatus.DONE).subquery())
        ).scalar() or 0
        
        percentage = (total_count / total_cases_all * 100) if total_cases_all > 0 else 0.0
        
        top_categories.append({
            'category_id': str(category.id),
            'category_name': category.name,
            'total_cases': total_count,
            'new_cases': new_count,
            'in_progress_cases': in_progress_count,
            'completed_cases': completed_count,
            'percentage_of_total': round(percentage, 2)
        })
    
    return {
        'period_start': datetime.fromisoformat(date_from.replace('Z', '+00:00')) if date_from else None,
        'period_end': datetime.fromisoformat(date_to.replace('Z', '+00:00')) if date_to else None,
        'total_cases_all_categories': total_cases_all,
        'top_categories': top_categories,
        'limit': limit
    }
