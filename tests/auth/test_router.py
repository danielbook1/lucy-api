import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import app
from app.database import Base, get_db
from app.auth.schemas import UserCreate
from app.auth.services import create_user, create_access_token
from datetime import timedelta


def get_test_client_with_db():
    """Create a TestClient with an in-memory database override."""
    import asyncio
    
    async def setup_test_db():
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
            connect_args={"timeout": 10},
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
        async with SessionLocal() as session:
            return session, engine
    
    # Run async setup
    session, engine = asyncio.run(setup_test_db())
    
    def override_get_db():
        return session
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    
    return client, session, engine


class TestRegisterEndpoint:
    """Test user registration endpoint."""

    def test_register_user_success(self):
        """Test successful user registration."""
        client, session, engine = get_test_client_with_db()
        
        response = client.post(
            "/auth/register",
            json={"username": "newuser", "password": "secure123"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "newuser"
        assert "id" in data
        assert "password" not in data

        app.dependency_overrides.clear()

    def test_register_duplicate_username(self):
        """Test that registering duplicate username returns 400."""
        client, session, engine = get_test_client_with_db()
        
        # Create first user
        client.post(
            "/auth/register",
            json={"username": "duplicate", "password": "pass123"},
        )
        
        # Try to create duplicate
        response = client.post(
            "/auth/register",
            json={"username": "duplicate", "password": "newpass123"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_register_missing_username(self):
        """Test that missing username returns 422."""
        client, session, engine = get_test_client_with_db()

        response = client.post(
            "/auth/register",
            json={"password": "secure123"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        app.dependency_overrides.clear()

    def test_register_missing_password(self):
        """Test that missing password returns 422."""
        client, session, engine = get_test_client_with_db()

        response = client.post(
            "/auth/register",
            json={"username": "newuser"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        app.dependency_overrides.clear()


class TestLoginEndpoint:
    """Test user login endpoint."""

    def test_login_success(self):
        """Test successful login."""
        client, session, engine = get_test_client_with_db()
        
        # Create user first
        client.post(
            "/auth/register",
            json={"username": "testuser", "password": "testpass123"},
        )
        
        response = client.post(
            "/auth/token",
            data={"username": "testuser", "password": "testpass123"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Logged in"
        assert "access_token" in response.cookies

        app.dependency_overrides.clear()

    def test_login_invalid_username(self):
        """Test login with invalid username."""
        client, session, engine = get_test_client_with_db()

        response = client.post(
            "/auth/token",
            data={"username": "nonexistent", "password": "anypass"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_login_invalid_password(self):
        """Test login with invalid password."""
        client, session, engine = get_test_client_with_db()
        
        # Create user first
        client.post(
            "/auth/register",
            json={"username": "testuser", "password": "testpass123"},
        )

        response = client.post(
            "/auth/token",
            data={"username": "testuser", "password": "wrongpassword"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_login_cookie_attributes(self):
        """Test that login cookie has correct security attributes."""
        client, session, engine = get_test_client_with_db()
        
        # Create user first
        client.post(
            "/auth/register",
            json={"username": "testuser", "password": "testpass123"},
        )

        response = client.post(
            "/auth/token",
            data={"username": "testuser", "password": "testpass123"},
        )

        assert response.status_code == status.HTTP_200_OK
        
        # Verify cookie attributes via Set-Cookie header
        set_cookie_header = response.headers.get("set-cookie", "")
        assert "HttpOnly" in set_cookie_header
        assert "SameSite" in set_cookie_header  # Can be SameSite=strict or SameSite=Strict

        app.dependency_overrides.clear()


class TestGetMeEndpoint:
    """Test get current user endpoint."""

    def test_get_me_success(self):
        """Test retrieving current user data."""
        client, session, engine = get_test_client_with_db()
        
        # Create user and login
        client.post(
            "/auth/register",
            json={"username": "testuser", "password": "testpass123"},
        )
        
        login_response = client.post(
            "/auth/token",
            data={"username": "testuser", "password": "testpass123"},
        )
        
        # Get me with token from cookies
        response = client.get("/auth/me")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "testuser"

        app.dependency_overrides.clear()

    def test_get_me_no_token(self):
        """Test that get me without token returns 401."""
        client, session, engine = get_test_client_with_db()

        response = client.get("/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_get_me_invalid_token(self):
        """Test that get me with invalid token returns 401."""
        client, session, engine = get_test_client_with_db()

        response = client.get(
            "/auth/me",
            cookies={"access_token": "invalid.token.here"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        app.dependency_overrides.clear()
