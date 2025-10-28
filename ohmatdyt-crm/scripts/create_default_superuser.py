#!/usr/bin/env python3
"""
Script to create a default superuser for development/testing.

Usage:
    docker compose exec api python /app/scripts/create_default_superuser.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os

from app.models import User, UserRole
from app.schemas import UserCreate
from app import crud


def create_default_superuser():
    """Create a default superuser for development."""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql+psycopg://ohm_user:change_me@db:5432/ohm_db')
    
    print("=" * 60)
    print("Ohmatdyt CRM - Create Default Superuser")
    print("=" * 60)
    print()
    
    # Create database session
    engine = create_engine(database_url)
    db = Session(engine)
    
    try:
        # Default credentials
        username = "admin"
        email = "admin@example.com"
        full_name = "System Administrator"
        password = "Admin123!"
        
        # Create user schema
        user_data = UserCreate(
            username=username,
            email=email,
            full_name=full_name,
            password=password,
            role=UserRole.ADMIN,
            is_active=True
        )
        
        # Create user
        print("Creating default superuser...")
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print()
        
        user = asyncio.run(crud.create_user(db, user_data))
        
        print("✅ Default superuser created successfully!")
        print()
        print("⚠️  SECURITY WARNING: Change this password in production!")
        print()
        print("User details:")
        print(f"  ID: {user.id}")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Full name: {user.full_name}")
        print(f"  Role: {user.role.value}")
        print(f"  Active: {user.is_active}")
        print(f"  Created: {user.created_at}")
        print()
        
    except ValueError as e:
        print()
        print(f"ℹ️  User may already exist: {e}")
        print()
    except Exception as e:
        print()
        print(f"❌ Unexpected error: {e}")
        print()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_default_superuser()
