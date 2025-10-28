"""
Tests for authentication endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app import crud, schemas, models


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """Create a test user"""
    db = TestingSessionLocal()
    user_data = schemas.UserCreate(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        password="Password123",
        role=models.UserRole.OPERATOR
    )
    
    # Create user synchronously for testing
    import asyncio
    user = asyncio.run(crud.create_user(db, user_data))
    db.close()
    return user


@pytest.fixture
def test_admin():
    """Create a test admin user"""
    db = TestingSessionLocal()
    admin_data = schemas.UserCreate(
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        password="Admin123",
        role=models.UserRole.ADMIN
    )
    
    import asyncio
    admin = asyncio.run(crud.create_user(db, admin_data))
    db.close()
    return admin


def test_login_success(test_user):
    """Test successful login"""
    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "Password123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data
    assert "user" in data
    assert data["user"]["username"] == "testuser"
    assert data["user"]["email"] == "test@example.com"


def test_login_wrong_password(test_user):
    """Test login with wrong password"""
    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "WrongPassword"
        }
    )
    
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_nonexistent_user():
    """Test login with non-existent user"""
    response = client.post(
        "/auth/login",
        json={
            "username": "nonexistent",
            "password": "Password123"
        }
    )
    
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_inactive_user():
    """Test login with inactive user"""
    # Create inactive user
    db = TestingSessionLocal()
    user_data = schemas.UserCreate(
        username="inactive",
        email="inactive@example.com",
        full_name="Inactive User",
        password="Password123",
        role=models.UserRole.OPERATOR
    )
    
    import asyncio
    user = asyncio.run(crud.create_user(db, user_data))
    asyncio.run(crud.deactivate_user(db, user.id))
    db.close()
    
    response = client.post(
        "/auth/login",
        json={
            "username": "inactive",
            "password": "Password123"
        }
    )
    
    assert response.status_code == 403
    assert "not active" in response.json()["detail"].lower()


def test_refresh_token_success(test_user):
    """Test successful token refresh"""
    # First login to get tokens
    login_response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "Password123"
        }
    )
    
    refresh_token = login_response.json()["refresh_token"]
    
    # Use refresh token to get new access token
    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


def test_refresh_token_invalid():
    """Test refresh with invalid token"""
    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": "invalid_token"
        }
    )
    
    assert response.status_code == 401


def test_get_current_user_success(test_user):
    """Test getting current user info with valid token"""
    # Login to get token
    login_response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "Password123"
        }
    )
    
    access_token = login_response.json()["access_token"]
    
    # Get current user info
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_get_current_user_no_token():
    """Test getting current user without token"""
    response = client.get("/auth/me")
    
    assert response.status_code == 401


def test_get_current_user_invalid_token():
    """Test getting current user with invalid token"""
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401


def test_logout_success(test_user):
    """Test logout with valid token"""
    # Login to get token
    login_response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "Password123"
        }
    )
    
    access_token = login_response.json()["access_token"]
    
    # Logout
    response = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 204


def test_protected_endpoint_with_token(test_admin):
    """Test accessing protected endpoint with valid token"""
    # Login as admin
    login_response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "Admin123"
        }
    )
    
    access_token = login_response.json()["access_token"]
    
    # Access protected endpoint
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200


def test_protected_endpoint_without_token():
    """Test accessing protected endpoint without token"""
    response = client.get("/api/users")
    
    assert response.status_code == 401


def test_admin_only_endpoint_as_non_admin(test_user):
    """Test accessing admin-only endpoint as non-admin user"""
    # Login as regular user
    login_response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "Password123"
        }
    )
    
    access_token = login_response.json()["access_token"]
    
    # Try to access admin-only endpoint
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 403
    assert "Admin" in response.json()["detail"]
