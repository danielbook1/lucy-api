import pytest
from fastapi import status


class TestRegisterEndpoint:
    """Test user registration endpoint."""

    def test_register_user_success(self, client_with_auth):
        """Test successful user registration."""
        response = client_with_auth.post(
            "/auth/register",
            json={"username": "newuser", "password": "secure123"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "newuser"
        assert "id" in data
        assert "password" not in data

    def test_register_duplicate_username(self, client_with_auth):
        """Test that registering duplicate username returns 400."""
        # Create first user
        client_with_auth.post(
            "/auth/register",
            json={"username": "duplicate", "password": "pass123"},
        )
        
        # Try to create duplicate
        response = client_with_auth.post(
            "/auth/register",
            json={"username": "duplicate", "password": "newpass123"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]

    def test_register_missing_username(self, client_with_auth):
        """Test that missing username returns 422."""
        response = client_with_auth.post(
            "/auth/register",
            json={"password": "secure123"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_missing_password(self, client_with_auth):
        """Test that missing password returns 422."""
        response = client_with_auth.post(
            "/auth/register",
            json={"username": "newuser"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLoginEndpoint:
    """Test user login endpoint."""

    def test_login_success(self, client_with_auth):
        """Test successful login."""
        # Create user first
        client_with_auth.post(
            "/auth/register",
            json={"username": "testuser", "password": "testpass123"},
        )
        
        response = client_with_auth.post(
            "/auth/token",
            data={"username": "testuser", "password": "testpass123"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Logged in"
        assert "access_token" in response.cookies

    def test_login_invalid_username(self, client_with_auth):
        """Test login with invalid username."""
        response = client_with_auth.post(
            "/auth/token",
            data={"username": "nonexistent", "password": "anypass"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_invalid_password(self, client_with_auth):
        """Test login with invalid password."""
        # Create user first
        client_with_auth.post(
            "/auth/register",
            json={"username": "testuser", "password": "testpass123"},
        )

        response = client_with_auth.post(
            "/auth/token",
            data={"username": "testuser", "password": "wrongpassword"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_cookie_attributes(self, client_with_auth):
        """Test that login cookie has correct security attributes."""
        # Create user first
        client_with_auth.post(
            "/auth/register",
            json={"username": "testuser", "password": "testpass123"},
        )

        response = client_with_auth.post(
            "/auth/token",
            data={"username": "testuser", "password": "testpass123"},
        )

        assert response.status_code == status.HTTP_200_OK
        
        # Verify cookie attributes via Set-Cookie header
        set_cookie_header = response.headers.get("set-cookie", "")
        assert "HttpOnly" in set_cookie_header
        assert "SameSite" in set_cookie_header  # Can be SameSite=strict or SameSite=Strict


class TestGetMeEndpoint:
    """Test get current user endpoint."""

    def test_get_me_success(self, client_with_auth):
        """Test retrieving current user data."""
        # Create user and login
        client_with_auth.post(
            "/auth/register",
            json={"username": "testuser", "password": "testpass123"},
        )
        
        client_with_auth.post(
            "/auth/token",
            data={"username": "testuser", "password": "testpass123"},
        )
        
        # Get me with token from cookies
        response = client_with_auth.get("/auth/me")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "testuser"

    def test_get_me_no_token(self, client_with_auth):
        """Test that get me without token returns 401."""
        response = client_with_auth.get("/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in response.json()["detail"]

    def test_get_me_invalid_token(self, client_with_auth):
        """Test that get me with invalid token returns 401."""
        response = client_with_auth.get(
            "/auth/me",
            cookies={"access_token": "invalid.token.here"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogoutEndpoint:
    """Test logout endpoint."""

    def test_logout_success(self, client_with_auth):
        """Test successful logout clears the cookie."""
        # First login
        client_with_auth.post(
            "/auth/register",
            json={"username": "testuser", "password": "testpass123"},
        )
        
        login_response = client_with_auth.post(
            "/auth/token",
            data={"username": "testuser", "password": "testpass123"},
        )
        
        # Verify we have a token
        assert "access_token" in login_response.cookies
        
        # Logout
        logout_response = client_with_auth.post("/auth/logout")
        
        assert logout_response.status_code == status.HTTP_200_OK
        assert logout_response.json()["message"] == "Logged out successfully"
        
        # Verify cookie is deleted (max-age=0 or expires in past)
        set_cookie_header = logout_response.headers.get("set-cookie", "")
        assert "access_token" in set_cookie_header
        assert ("Max-Age=0" in set_cookie_header or "max-age=0" in set_cookie_header)

    def test_logout_without_login(self, client_with_auth):
        """Test that logout works even without being logged in."""
        # Logout without logging in first
        response = client_with_auth.post("/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Logged out successfully"
