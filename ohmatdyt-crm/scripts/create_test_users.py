"""
Create test users (operator and executor) for FE-011 testing
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from app import crud, schemas, models


async def create_test_users():
    """Create test operator and executor users"""
    async with async_session_maker() as session:
        # Create OPERATOR
        operator_data = schemas.UserCreate(
            username="operator",
            email="operator@ohmatdyt.com",
            full_name="Test Operator",
            password="Operator123!",
            role=models.UserRole.OPERATOR
        )
        
        try:
            operator = await crud.create_user(session, operator_data)
            print(f"✓ Created OPERATOR: {operator.username} ({operator.email})")
        except Exception as e:
            print(f"OPERATOR already exists or error: {e}")
        
        # Create EXECUTOR
        executor_data = schemas.UserCreate(
            username="executor",
            email="executor@ohmatdyt.com",
            full_name="Test Executor",
            password="Executor123!",
            role=models.UserRole.EXECUTOR
        )
        
        try:
            executor = await crud.create_user(session, executor_data)
            print(f"✓ Created EXECUTOR: {executor.username} ({executor.email})")
        except Exception as e:
            print(f"EXECUTOR already exists or error: {e}")
        
        await session.commit()
        print("\n✓ Test users created successfully!")


if __name__ == "__main__":
    asyncio.run(create_test_users())
