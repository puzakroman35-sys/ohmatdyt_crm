"""
Create test admin user for JWT authentication testing
Run: docker compose exec api python scripts/create_test_admin.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app import crud, schemas, models


async def create_test_admin():
    """Create test admin user if not exists"""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = await crud.get_user_by_username(db, "admin")
        
        if existing_admin:
            print("✅ Admin user already exists!")
            print(f"   Username: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            print(f"   Role: {existing_admin.role.value}")
            return
        
        # Create admin user
        admin_data = schemas.UserCreate(
            username="admin",
            email="admin@ohmatdyt.com",
            full_name="System Administrator",
            password="Admin123!",
            role=models.UserRole.ADMIN
        )
        
        admin = await crud.create_user(db, admin_data)
        
        print("✅ Test admin user created successfully!")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Password: Admin123!")
        print(f"   Role: {admin.role.value}")
        print("\n⚠️  Please change the password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()


async def create_test_users():
    """Create additional test users for different roles"""
    db = SessionLocal()
    
    test_users = [
        {
            "username": "operator1",
            "email": "operator1@ohmatdyt.com",
            "full_name": "Test Operator",
            "password": "Operator123!",
            "role": models.UserRole.OPERATOR
        },
        {
            "username": "executor1",
            "email": "executor1@ohmatdyt.com",
            "full_name": "Test Executor",
            "password": "Executor123!",
            "role": models.UserRole.EXECUTOR
        }
    ]
    
    try:
        for user_dict in test_users:
            # Check if user exists
            existing = await crud.get_user_by_username(db, user_dict["username"])
            
            if existing:
                print(f"⚠️  User {user_dict['username']} already exists, skipping...")
                continue
            
            # Create user
            user_data = schemas.UserCreate(**user_dict)
            user = await crud.create_user(db, user_data)
            
            print(f"✅ Created user: {user.username} ({user.role.value})")
        
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Creating test users for JWT authentication")
    print("=" * 60)
    print()
    
    # Create admin
    asyncio.run(create_test_admin())
    print()
    
    # Create other test users
    print("Creating additional test users...")
    asyncio.run(create_test_users())
    
    print()
    print("=" * 60)
    print("Test users created successfully!")
    print("=" * 60)
    print("\nYou can now test authentication with:")
    print("  - admin / Admin123!")
    print("  - operator1 / Operator123!")
    print("  - executor1 / Executor123!")
