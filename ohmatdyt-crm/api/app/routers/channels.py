"""
Channels API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app import schemas, crud
from app.database import get_db
from app.dependencies import require_admin
from app.models import User

router = APIRouter(prefix="/channels", tags=["Channels"])


@router.get("", response_model=schemas.ChannelListResponse)
async def list_channels(
    include_inactive: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of channels.
    
    Query params:
    - include_inactive: Include inactive channels (default: false)
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100)
    
    Returns only active channels by default.
    """
    if limit > 100:
        limit = 100
    
    db_channels = await crud.get_channels(
        db, 
        skip=skip, 
        limit=limit,
        include_inactive=include_inactive
    )
    
    # Convert to response schemas
    channels = [
        schemas.ChannelResponse(
            id=str(ch.id),
            name=ch.name,
            is_active=ch.is_active,
            created_at=ch.created_at,
            updated_at=ch.updated_at
        )
        for ch in db_channels
    ]
    
    return {
        "channels": channels,
        "total": len(channels)
    }


@router.post("", response_model=schemas.ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel: schemas.ChannelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new channel.
    
    Requires: Admin privileges
    
    Request:
    - name: Channel name (unique, 1-200 characters)
    
    Returns created channel.
    """
    try:
        db_channel = await crud.create_channel(db, channel)
        
        return schemas.ChannelResponse(
            id=str(db_channel.id),
            name=db_channel.name,
            is_active=db_channel.is_active,
            created_at=db_channel.created_at,
            updated_at=db_channel.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{channel_id}", response_model=schemas.ChannelResponse)
async def get_channel(
    channel_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get channel by ID.
    
    Returns channel details.
    """
    db_channel = await crud.get_channel(db, channel_id)
    
    if not db_channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    return schemas.ChannelResponse(
        id=str(db_channel.id),
        name=db_channel.name,
        is_active=db_channel.is_active,
        created_at=db_channel.created_at,
        updated_at=db_channel.updated_at
    )


@router.put("/{channel_id}", response_model=schemas.ChannelResponse)
async def update_channel(
    channel_id: UUID,
    channel_update: schemas.ChannelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update channel.
    
    Requires: Admin privileges
    
    Request:
    - name: New channel name (optional)
    
    Returns updated channel.
    """
    try:
        db_channel = await crud.update_channel(db, channel_id, channel_update)
        
        if not db_channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )
        
        return schemas.ChannelResponse(
            id=str(db_channel.id),
            name=db_channel.name,
            is_active=db_channel.is_active,
            created_at=db_channel.created_at,
            updated_at=db_channel.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{channel_id}/deactivate", response_model=schemas.ChannelResponse)
async def deactivate_channel(
    channel_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Deactivate channel.
    
    Requires: Admin privileges
    
    Deactivated channels will not be available for selection
    when creating new requests.
    
    Returns updated channel.
    """
    db_channel = await crud.deactivate_channel(db, channel_id)
    
    if not db_channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    return schemas.ChannelResponse(
        id=str(db_channel.id),
        name=db_channel.name,
        is_active=db_channel.is_active,
        created_at=db_channel.created_at,
        updated_at=db_channel.updated_at
    )


@router.post("/{channel_id}/activate", response_model=schemas.ChannelResponse)
async def activate_channel(
    channel_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Activate channel.
    
    Requires: Admin privileges
    
    Activated channels will be available for selection
    when creating new requests.
    
    Returns updated channel.
    """
    db_channel = await crud.activate_channel(db, channel_id)
    
    if not db_channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    return schemas.ChannelResponse(
        id=str(db_channel.id),
        name=db_channel.name,
        is_active=db_channel.is_active,
        created_at=db_channel.created_at,
        updated_at=db_channel.updated_at
    )
