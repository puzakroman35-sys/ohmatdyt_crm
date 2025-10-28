"""
Test script for BE-004: Case model and public_id generation
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.database import SessionLocal
from app.utils import generate_unique_public_id
from app.models import Case, User, Category, Channel, UserRole, CaseStatus
from sqlalchemy import select


async def test_public_id_generation():
    """Test that public_id generation works and produces unique 6-digit IDs"""
    print("=" * 60)
    print("TEST: public_id Generation")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Generate 10 unique public_ids
        ids = set()
        for i in range(10):
            public_id = await generate_unique_public_id(db)
            if public_id in ids:
                print(f"❌ FAIL: Duplicate public_id {public_id} generated!")
                return False
            ids.add(public_id)
            print(f"  ✅ Generated unique public_id: {public_id}")
        
        # Verify all IDs are 6 digits (100000-999999)
        for pid in ids:
            if pid < 100000 or pid > 999999:
                print(f"❌ FAIL: public_id {pid} is not 6 digits!")
                return False
        
        print(f"\n✅ SUCCESS: Generated {len(ids)} unique 6-digit IDs")
        print(f"   Range: {min(ids)} - {max(ids)}")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False
    finally:
        db.close()


async def test_case_creation():
    """Test creating a case with all required fields"""
    print("\n" + "=" * 60)
    print("TEST: Case Creation")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Get a category
        result = db.execute(select(Category).where(Category.is_active == True).limit(1))
        category = result.scalar_one_or_none()
        if not category:
            print("❌ FAIL: No active categories found")
            return False
        print(f"  Using category: {category.name} ({category.id})")
        
        # Get a channel
        result = db.execute(select(Channel).where(Channel.is_active == True).limit(1))
        channel = result.scalar_one_or_none()
        if not channel:
            print("❌ FAIL: No active channels found")
            return False
        print(f"  Using channel: {channel.name} ({channel.id})")
        
        # Get an admin user as author
        result = db.execute(select(User).where(User.role == UserRole.ADMIN).limit(1))
        author = result.scalar_one_or_none()
        if not author:
            print("❌ FAIL: No admin users found")
            return False
        print(f"  Using author: {author.username} ({author.id})")
        
        # Generate public_id
        public_id = await generate_unique_public_id(db)
        print(f"  Generated public_id: {public_id}")
        
        # Create a test case
        test_case = Case(
            public_id=public_id,
            category_id=category.id,
            channel_id=channel.id,
            subcategory="Test Subcategory",
            applicant_name="John Doe",
            applicant_phone="+380501234567",
            applicant_email="john.doe@example.com",
            summary="This is a test case for BE-004 implementation",
            status=CaseStatus.NEW,
            author_id=author.id,
            responsible_id=None
        )
        
        db.add(test_case)
        db.commit()
        db.refresh(test_case)
        
        print(f"\n✅ SUCCESS: Case created with ID: {test_case.id}")
        print(f"   Public ID: {test_case.public_id}")
        print(f"   Status: {test_case.status.value}")
        print(f"   Applicant: {test_case.applicant_name}")
        print(f"   Summary: {test_case.summary[:50]}...")
        
        # Verify we can retrieve it
        result = db.execute(select(Case).where(Case.public_id == public_id))
        retrieved_case = result.scalar_one_or_none()
        if not retrieved_case:
            print("❌ FAIL: Could not retrieve created case")
            return False
        
        print(f"  ✅ Case successfully retrieved by public_id")
        
        # Clean up
        db.delete(test_case)
        db.commit()
        print(f"  ✅ Test case cleaned up")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


async def test_public_id_uniqueness_constraint():
    """Test that database enforces public_id uniqueness"""
    print("\n" + "=" * 60)
    print("TEST: public_id Uniqueness Constraint")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Get required entities
        result = db.execute(select(Category).where(Category.is_active == True).limit(1))
        category = result.scalar_one_or_none()
        
        result = db.execute(select(Channel).where(Channel.is_active == True).limit(1))
        channel = result.scalar_one_or_none()
        
        result = db.execute(select(User).where(User.role == UserRole.ADMIN).limit(1))
        author = result.scalar_one_or_none()
        
        if not (category and channel and author):
            print("❌ FAIL: Required entities not found")
            return False
        
        # Generate a public_id
        public_id = await generate_unique_public_id(db)
        print(f"  Using public_id: {public_id}")
        
        # Create first case
        case1 = Case(
            public_id=public_id,
            category_id=category.id,
            channel_id=channel.id,
            applicant_name="Test User 1",
            summary="First case",
            status=CaseStatus.NEW,
            author_id=author.id
        )
        db.add(case1)
        db.commit()
        print(f"  ✅ First case created with public_id {public_id}")
        
        # Try to create second case with same public_id (should fail)
        try:
            case2 = Case(
                public_id=public_id,  # Same public_id!
                category_id=category.id,
                channel_id=channel.id,
                applicant_name="Test User 2",
                summary="Second case (should fail)",
                status=CaseStatus.NEW,
                author_id=author.id
            )
            db.add(case2)
            db.commit()
            print(f"❌ FAIL: Database allowed duplicate public_id!")
            return False
        except Exception as e:
            db.rollback()
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                print(f"  ✅ Database correctly rejected duplicate public_id")
                print(f"     Error: {str(e)[:100]}...")
            else:
                print(f"❌ FAIL: Unexpected error: {e}")
                return False
        
        # Clean up
        db.delete(case1)
        db.commit()
        print(f"  ✅ Test case cleaned up")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("BE-004: Case Model and public_id Generator Tests")
    print("=" * 60 + "\n")
    
    results = []
    
    # Test 1: public_id generation
    results.append(await test_public_id_generation())
    
    # Test 2: Case creation
    results.append(await test_case_creation())
    
    # Test 3: Uniqueness constraint
    results.append(await test_public_id_uniqueness_constraint())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"  Passed: {passed}/{total}")
    print(f"  Failed: {total - passed}/{total}")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
