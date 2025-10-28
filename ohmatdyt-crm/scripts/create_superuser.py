#!/usr/bin/env python3
"""
Script to create a superuser (admin) for the Ohmatdyt CRM system.

Usage:
    python create_superuser.py
    
Or in Docker:
    docker compose exec api python /app/scripts/create_superuser.py
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


def create_superuser():
    """Create a superuser interactively."""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql+psycopg://ohm_user:change_me@db:5432/ohm_db')
    
    print("=" * 60)
    print("Ohmatdyt CRM - Create Superuser")
    print("=" * 60)
    print()
    
    # Create database session
    engine = create_engine(database_url)
    db = Session(engine)
    
    try:
        # Get user input
        print("Enter superuser details:")
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        full_name = input("Full name: ").strip()
        password = input("Password: ").strip()
        password_confirm = input("Confirm password: ").strip()
        
        # Validate input
        if not username:
            print("❌ Username is required")
            return
        
        if not email:
            print("❌ Email is required")
            return
        
        if not full_name:
            print("❌ Full name is required")
            return
        
        if not password:
            print("❌ Password is required")
            return
        
        if password != password_confirm:
            print("❌ Passwords do not match")
            return
        
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
        print()
        print("Creating superuser...")
        
        user = asyncio.run(crud.create_user(db, user_data))
        
        print()
        print("✅ Superuser created successfully!")
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
        print(f"❌ Error: {e}")
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
    create_superuser()
