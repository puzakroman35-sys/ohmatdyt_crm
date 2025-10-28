"""CRUD operations for database models."""

from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app import models, schemas
from app.auth import hash_password


async def create_user(db: Session, user: schemas.UserCreate) -> models.User:
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


async def get_user(db: Session, user_id: UUID) -> Optional[models.User]:
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


async def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
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


async def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
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


async def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    role: Optional[models.UserRole] = None,
    is_active: Optional[bool] = None
) -> list[models.User]:
    """
    Get list of users with filtering and pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        role: Filter by user role
        is_active: Filter by active status
        
    Returns:
        List of user models
    """
    query = select(models.User)
    
    if role is not None:
        query = query.where(models.User.role == role)
    
    if is_active is not None:
        query = query.where(models.User.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    
    return list(db.execute(query).scalars().all())


async def update_user(
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
    db_user = await get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Check username uniqueness if being updated
    if 'username' in update_data and update_data['username'] != db_user.username:
        existing = await get_user_by_username(db, update_data['username'])
        if existing and existing.id != user_id:
            raise ValueError(f"Username '{update_data['username']}' already exists")
    
    # Check email uniqueness if being updated
    if 'email' in update_data and update_data['email'] != db_user.email:
        existing = await get_user_by_email(db, update_data['email'])
        if existing and existing.id != user_id:
            raise ValueError(f"Email '{update_data['email']}' already exists")
    
    # Update fields
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


async def update_user_password(
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
    db_user = await get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.password_hash = hash_password(password_update.password)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


async def delete_user(db: Session, user_id: UUID) -> bool:
    """
    Delete user by ID.
    
    Args:
        db: Database session
        user_id: User UUID
        
    Returns:
        True if user was deleted, False if not found
    """
    db_user = await get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    
    return True


async def deactivate_user(db: Session, user_id: UUID) -> Optional[models.User]:
    """
    Deactivate user (soft delete).
    
    Args:
        db: Database session
        user_id: User UUID
        
    Returns:
        Updated user model or None if not found
    """
    db_user = await get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.is_active = False
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


async def activate_user(db: Session, user_id: UUID) -> Optional[models.User]:
    """
    Activate user.
    
    Args:
        db: Database session
        user_id: User UUID
        
    Returns:
        Updated user model or None if not found
    """
    db_user = await get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.is_active = True
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


# ==================== Category CRUD Operations ====================

async def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
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


async def get_category(db: Session, category_id: UUID) -> Optional[models.Category]:
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


async def get_category_by_name(db: Session, name: str) -> Optional[models.Category]:
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


async def get_categories(
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


async def update_category(
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
    db_category = await get_category(db, category_id)
    if not db_category:
        return None
    
    update_data = category_update.model_dump(exclude_unset=True)
    
    # Check name uniqueness if being updated
    if 'name' in update_data and update_data['name'] != db_category.name:
        existing = await get_category_by_name(db, update_data['name'])
        if existing and existing.id != category_id:
            raise ValueError(f"Category '{update_data['name']}' already exists")
    
    # Update fields
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    
    return db_category


async def deactivate_category(db: Session, category_id: UUID) -> Optional[models.Category]:
    """
    Deactivate category.
    
    Args:
        db: Database session
        category_id: Category UUID
        
    Returns:
        Updated category model or None if not found
    """
    db_category = await get_category(db, category_id)
    if not db_category:
        return None
    
    db_category.is_active = False
    
    db.commit()
    db.refresh(db_category)
    
    return db_category


async def activate_category(db: Session, category_id: UUID) -> Optional[models.Category]:
    """
    Activate category.
    
    Args:
        db: Database session
        category_id: Category UUID
        
    Returns:
        Updated category model or None if not found
    """
    db_category = await get_category(db, category_id)
    if not db_category:
        return None
    
    db_category.is_active = True
    
    db.commit()
    db.refresh(db_category)
    
    return db_category


# ==================== Channel CRUD Operations ====================

async def create_channel(db: Session, channel: schemas.ChannelCreate) -> models.Channel:
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


async def get_channel(db: Session, channel_id: UUID) -> Optional[models.Channel]:
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


async def get_channel_by_name(db: Session, name: str) -> Optional[models.Channel]:
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


async def get_channels(
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


async def update_channel(
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
    db_channel = await get_channel(db, channel_id)
    if not db_channel:
        return None
    
    update_data = channel_update.model_dump(exclude_unset=True)
    
    # Check name uniqueness if being updated
    if 'name' in update_data and update_data['name'] != db_channel.name:
        existing = await get_channel_by_name(db, update_data['name'])
        if existing and existing.id != channel_id:
            raise ValueError(f"Channel '{update_data['name']}' already exists")
    
    # Update fields
    for field, value in update_data.items():
        setattr(db_channel, field, value)
    
    db.commit()
    db.refresh(db_channel)
    
    return db_channel


async def deactivate_channel(db: Session, channel_id: UUID) -> Optional[models.Channel]:
    """
    Deactivate channel.
    
    Args:
        db: Database session
        channel_id: Channel UUID
        
    Returns:
        Updated channel model or None if not found
    """
    db_channel = await get_channel(db, channel_id)
    if not db_channel:
        return None
    
    db_channel.is_active = False
    
    db.commit()
    db.refresh(db_channel)
    
    return db_channel


async def activate_channel(db: Session, channel_id: UUID) -> Optional[models.Channel]:
    """
    Activate channel.
    
    Args:
        db: Database session
        channel_id: Channel UUID
        
    Returns:
        Updated channel model or None if not found
    """
    db_channel = await get_channel(db, channel_id)
    if not db_channel:
        return None
    
    db_channel.is_active = True
    
    db.commit()
    db.refresh(db_channel)
    
    return db_channel


# ==================== Case CRUD Operations ====================

async def create_case(
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
    category = await get_category(db, parse_uuid(case.category_id))
    if not category:
        raise ValueError(f"Category with id '{case.category_id}' not found")
    if not category.is_active:
        raise ValueError(f"Category '{category.name}' is not active")
    
    # Validate channel exists and is active
    channel = await get_channel(db, parse_uuid(case.channel_id))
    if not channel:
        raise ValueError(f"Channel with id '{case.channel_id}' not found")
    if not channel.is_active:
        raise ValueError(f"Channel '{channel.name}' is not active")
    
    # Validate responsible user if provided
    responsible_id_uuid = None
    if case.responsible_id:
        responsible = await get_user(db, parse_uuid(case.responsible_id))
        if not responsible:
            raise ValueError(f"Responsible user with id '{case.responsible_id}' not found")
        if responsible.role not in [models.UserRole.EXECUTOR, models.UserRole.ADMIN]:
            raise ValueError(f"User '{responsible.username}' cannot be assigned as responsible (must be EXECUTOR or ADMIN)")
        if not responsible.is_active:
            raise ValueError(f"User '{responsible.username}' is not active")
        responsible_id_uuid = parse_uuid(case.responsible_id)
    
    # Generate unique public_id
    public_id = await generate_unique_public_id(db)
    
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
    
    return db_case


async def get_case(db: Session, case_id: UUID) -> Optional[models.Case]:
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


async def get_case_by_public_id(db: Session, public_id: int) -> Optional[models.Case]:
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


async def get_all_cases(
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
    limit: int = 50
) -> tuple[list[models.Case], int]:
    """
    Get all cases with optional filtering and sorting.
    
    Args:
        db: Database session
        status: Filter by case status
        category_id: Filter by category
        channel_id: Filter by channel
        author_id: Filter by author
        responsible_id: Filter by responsible user
        public_id: Filter by 6-digit public ID
        date_from: Filter by created date from (ISO format)
        date_to: Filter by created date to (ISO format)
        overdue: Filter overdue cases (requires SLA field - placeholder)
        order_by: Sort field (prefix with - for descending, e.g., -created_at)
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        
    Returns:
        Tuple of (list of cases, total count)
    """
    from datetime import datetime
    
    query = select(models.Case)
    
    # Apply filters (AND logic)
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
    
    # Date range filters
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
    
    # Get total count
    count_result = db.execute(
        select(models.Case.id).select_from(query.subquery())
    )
    total = len(count_result.all())
    
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


async def update_case(
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
    
    db_case = await get_case(db, case_id)
    if not db_case:
        return None
    
    # Update fields if provided
    if case_update.category_id is not None:
        category = await get_category(db, parse_uuid(case_update.category_id))
        if not category:
            raise ValueError(f"Category with id '{case_update.category_id}' not found")
        if not category.is_active:
            raise ValueError(f"Category '{category.name}' is not active")
        db_case.category_id = parse_uuid(case_update.category_id)
    
    if case_update.channel_id is not None:
        channel = await get_channel(db, parse_uuid(case_update.channel_id))
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
    
    if case_update.status is not None:
        db_case.status = case_update.status
    
    if case_update.responsible_id is not None:
        if case_update.responsible_id == "":  # Allow clearing responsible
            db_case.responsible_id = None
        else:
            responsible = await get_user(db, parse_uuid(case_update.responsible_id))
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


async def delete_case(db: Session, case_id: UUID) -> bool:
    """
    Delete case by ID (hard delete).
    
    Note: This will cascade delete all attachments.
    
    Args:
        db: Database session
        case_id: Case UUID
        
    Returns:
        True if case was deleted, False if not found
    """
    db_case = await get_case(db, case_id)
    if not db_case:
        return False
    
    db.delete(db_case)
    db.commit()
    
    return True


async def get_executors_for_category(
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

async def create_attachment(
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
    case = await get_case(db, case_id)
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


async def get_attachment(db: Session, attachment_id: UUID) -> Optional[models.Attachment]:
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


async def get_case_attachments(
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


async def delete_attachment(db: Session, attachment_id: UUID) -> bool:
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
    db_attachment = await get_attachment(db, attachment_id)
    if not db_attachment:
        return False
    
    db.delete(db_attachment)
    db.commit()
    
    return True

