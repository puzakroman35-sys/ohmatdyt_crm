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
