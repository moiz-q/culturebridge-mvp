"""
Smoke tests for critical user journeys.
These tests verify that core functionality works end-to-end.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.utils.jwt_utils import hash_password
import uuid


client = TestClient(app)


@pytest.fixture
def db_session():
    """Create a database session for tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_client_user(db_session):
    """Create a test client user."""
    user = User(
        id=uuid.uuid4(),
        email=f"client_{uuid.uuid4()}@test.com",
        password_hash=hash_password("TestPassword123!"),
        role="client",
        is_active=True,
        email_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_coach_user(db_session):
    """Create a test coach user."""
    user = User(
        id=uuid.uuid4(),
        email=f"coach_{uuid.uuid4()}@test.com",
        password_hash=hash_password("TestPassword123!"),
        role="coach",
        is_active=True,
        email_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin_user(db_session):
    """Create a test admin user."""
    user = User(
        id=uuid.uuid4(),
        email=f"admin_{uuid.uuid4()}@test.com",
        password_hash=hash_password("TestPassword123!"),
        role="admin",
        is_active=True,
        email_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_endpoint(self):
        """Test that health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "database" in data


class TestAuthenticationFlow:
    """Test complete authentication flow."""
    
    def test_signup_and_login(self):
        """Test user can sign up and log in."""
        # Sign up
        email = f"newuser_{uuid.uuid4()}@test.com"
        signup_data = {
            "email": email,
            "password": "TestPassword123!",
            "role": "client"
        }
        response = client.post("/auth/signup", json=signup_data)
        assert response.status_code == 201
        user_data = response.json()
        assert user_data["email"] == email
        assert user_data["role"] == "client"
        
        # Login
        login_data = {
            "email": email,
            "password": "TestPassword123!"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert token_data["token_type"] == "bearer"
    
    def test_login_with_invalid_credentials(self):
        """Test login fails with invalid credentials."""
        login_data = {
            "email": "nonexistent@test.com",
            "password": "WrongPassword123!"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401


class TestProfileManagement:
    """Test profile management functionality."""
    
    def test_get_profile_requires_auth(self):
        """Test that getting profile requires authentication."""
        response = client.get("/profile")
        assert response.status_code == 401
    
    def test_client_can_access_profile(self, test_client_user):
        """Test client can access their profile."""
        # Login
        login_data = {
            "email": test_client_user.email,
            "password": "TestPassword123!"
        }
        response = client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]
        
        # Get profile
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/profile", headers=headers)
        assert response.status_code in [200, 404]  # 404 if profile not created yet


class TestCoachDiscovery:
    """Test coach discovery functionality."""
    
    def test_list_coaches_requires_auth(self):
        """Test that listing coaches requires authentication."""
        response = client.get("/coaches")
        assert response.status_code == 401
    
    def test_client_can_list_coaches(self, test_client_user):
        """Test client can list coaches."""
        # Login
        login_data = {
            "email": test_client_user.email,
            "password": "TestPassword123!"
        }
        response = client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]
        
        # List coaches
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/coaches", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


class TestBookingFlow:
    """Test booking creation flow."""
    
    def test_create_booking_requires_auth(self):
        """Test that creating booking requires authentication."""
        booking_data = {
            "coach_id": str(uuid.uuid4()),
            "session_datetime": "2025-12-01T14:00:00Z",
            "duration_minutes": 60
        }
        response = client.post("/booking", json=booking_data)
        assert response.status_code == 401


class TestCommunityFeatures:
    """Test community features."""
    
    def test_list_posts_requires_auth(self):
        """Test that listing posts requires authentication."""
        response = client.get("/community/posts")
        assert response.status_code == 401
    
    def test_authenticated_user_can_list_posts(self, test_client_user):
        """Test authenticated user can list posts."""
        # Login
        login_data = {
            "email": test_client_user.email,
            "password": "TestPassword123!"
        }
        response = client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]
        
        # List posts
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/community/posts", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data


class TestAdminAccess:
    """Test admin-only functionality."""
    
    def test_admin_metrics_requires_admin_role(self, test_client_user):
        """Test that admin endpoints require admin role."""
        # Login as client
        login_data = {
            "email": test_client_user.email,
            "password": "TestPassword123!"
        }
        response = client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]
        
        # Try to access admin endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/admin/metrics", headers=headers)
        assert response.status_code == 403
    
    def test_admin_can_access_metrics(self, test_admin_user):
        """Test admin can access metrics."""
        # Login as admin
        login_data = {
            "email": test_admin_user.email,
            "password": "TestPassword123!"
        }
        response = client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]
        
        # Access admin endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/admin/metrics", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "bookings" in data
        assert "revenue" in data


class TestAPIDocumentation:
    """Test API documentation endpoints."""
    
    def test_openapi_json_accessible(self):
        """Test OpenAPI JSON is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
    
    def test_swagger_ui_accessible(self):
        """Test Swagger UI is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_accessible(self):
        """Test ReDoc is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
