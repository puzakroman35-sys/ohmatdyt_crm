"""
Database configuration and session management
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://ohm_user:change_me@db:5432/ohm_db"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=5,
    max_overflow=10,
    echo=False,  # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    
    Usage:
        @app.get("/users/")
        def read_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    This should be called on application startup.
    """
    from app.models import Base
    Base.metadata.create_all(bind=engine)


def check_db_connection() -> bool:
    """
    Check if database connection is working.
    Returns True if connection is successful.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


def check_redis_connection(redis_url: str = None) -> bool:
    """
    BE-015: Check if Redis connection is working.
    
    Args:
        redis_url: Redis connection URL (default: from environment)
    
    Returns:
        True if connection is successful, False otherwise
    """
    import redis
    
    if redis_url is None:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    try:
        # Create Redis client
        redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Try to ping Redis
        redis_client.ping()
        
        # Close connection
        redis_client.close()
        
        return True
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False
