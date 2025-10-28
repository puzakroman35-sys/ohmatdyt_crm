"""
Utility functions for Ohmatdyt CRM
"""
import random
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Case


async def generate_unique_public_id(db: Session, max_attempts: int = 10) -> int:
    """
    Generate a unique 6-digit public_id for a Case.
    
    The public_id is a random integer between 100000 and 999999 (inclusive).
    The function will retry up to max_attempts times if a collision occurs.
    
    Args:
        db: Database session
        max_attempts: Maximum number of attempts to generate a unique ID
        
    Returns:
        int: A unique 6-digit public_id
        
    Raises:
        RuntimeError: If unable to generate a unique ID after max_attempts
    """
    for attempt in range(max_attempts):
        # Generate a random 6-digit number (100000-999999)
        public_id = random.randint(100000, 999999)
        
        # Check if this public_id already exists (synchronous query)
        result = db.execute(
            select(Case).where(Case.public_id == public_id)
        )
        existing_case = result.scalar_one_or_none()
        
        if existing_case is None:
            # Unique ID found
            return public_id
    
    # If we get here, we failed to generate a unique ID
    raise RuntimeError(
        f"Failed to generate unique public_id after {max_attempts} attempts. "
        "This is highly unlikely and may indicate a database issue."
    )
