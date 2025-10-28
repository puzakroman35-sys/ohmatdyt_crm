"""
Create test executor user for FE-005 testing
"""
from app.database import SessionLocal
from app import crud, models, schemas, auth

def create_executor():
    db = SessionLocal()
    try:
        # Check if user exists
        existing = db.query(models.User).filter(
            models.User.username == "executor1"
        ).first()
        
        if existing:
            print(f"User already exists: {existing.username} ({existing.role.value})")
            return
        
        # Create user
        user = schemas.UserCreate(
            username="executor1",
            email="executor1@example.com",
            full_name="Test Executor 1",
            password="Executor123!",
            role=models.UserRole.EXECUTOR
        )
        
        db_user = crud.create_user(db, user)
        print(f"✅ Created: {db_user.username} ({db_user.role.value})")
        print(f"   Email: {db_user.email}")
        print(f"   Full name: {db_user.full_name}")
        
    finally:
        db.close()

if __name__ == "__main__":
    create_executor()
