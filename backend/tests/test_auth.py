"""
Integration tests for authentication endpoints.

Requirements: 1.1, 1.2, 1.3
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import UserRole

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
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


def test_signup_success():
    """Test successful user signup"""
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "client"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["role"] == "client"
    assert data["token_type"] == "bearer"


def test_signup_duplicate_email():
    """Test signup with duplicate email"""
    # First signup
    client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "client"
        }
    )
    
    # Second signup with same email
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "coach"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_signup_invalid_password():
    """Test signup with short password"""
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "short",
            "role": "client"
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_login_success():
    """Test successful login"""
    # First signup
    client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "client"
        }
    )
    
    # Then login
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "test@example.com"


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_login_wrong_password():
    """Test login with wrong password"""
    # First signup
    client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "client"
        }
    )
    
    # Login with wrong password
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401


def test_refresh_token():
    """Test token refresh"""
    # Signup to get tokens
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "client"
        }
    )
    
    refresh_token = signup_response.json()["refresh_token"]
    
    # Refresh token
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_current_user():
    """Test getting current user info"""
    # Signup to get token
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "client"
        }
    )
    
    access_token = signup_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "client"


def test_get_current_user_unauthorized():
    """Test getting current user without token"""
    response = client.get("/auth/me")
    
    assert response.status_code == 403  # No credentials provided


def test_password_reset_request():
    """Test password reset request"""
    # Signup first
    client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "client"
        }
    )
    
    # Request password reset
    response = client.post(
        "/auth/reset-password",
        json={"email": "test@example.com"}
    )
    
    assert response.status_code == 200
    assert "message" in response.json()


def test_password_reset_confirm():
    """Test password reset confirmation"""
    # Signup first
    client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "client"
        }
    )
    
    # Request password reset
    reset_response = client.post(
        "/auth/reset-password",
        json={"email": "test@example.com"}
    )
    
    # Get reset token (only available in development)
    reset_token = reset_response.json().get("reset_token")
    
    if reset_token:
        # Confirm password reset
        response = client.post(
            "/auth/reset-password/confirm",
            json={
                "token": reset_token,
                "new_password": "newpassword123"
            }
        )
        
        assert response.status_code == 200
        
        # Try logging in with new password
        login_response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "newpassword123"
            }
        )
        
        assert login_response.status_code == 200


def test_change_password():
    """Test password change for authenticated user"""
    # Signup to get token
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "role": "client"
        }
    )
    
    access_token = signup_response.json()["access_token"]
    
    # Change password
    response = client.post(
        "/auth/change-password",
        json={
            "current_password": "testpassword123",
            "new_password": "newpassword123"
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    
    # Try logging in with new password
    login_response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "newpassword123"
        }
    )
    
    assert login_response.status_code == 200
