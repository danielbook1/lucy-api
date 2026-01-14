import pytest
from fastapi import status, HTTPException
from app.auth.services import (
    verify_password,
    hash_password,
)


class TestHashPassword:
    """Test password hashing and verification."""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a hashed string."""
        password = "mypassword123"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert hashed != password

    def test_verify_password_success(self):
        """Test that verify_password correctly validates a matching password."""
        password = "mypassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """Test that verify_password rejects an incorrect password."""
        password = "mypassword123"
        hashed = hash_password(password)
        assert verify_password("wrongpassword", hashed) is False

    def test_hash_password_produces_different_hashes(self):
        """Test that the same password produces different hashes (salt randomization)."""
        password = "mypassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2


class TestGetCurrentUser:
    """Test current user retrieval from token."""

    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, test_db):
        """Test that missing token raises HTTPException."""
        from app.auth.services import get_current_user
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(access_token=None, db=test_db)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, test_db):
        """Test that invalid token raises HTTPException."""
        from app.auth.services import get_current_user
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(access_token="invalid.token.here", db=test_db)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(self, test_db):
        """Test that expired token raises HTTPException."""
        from datetime import timedelta
        from app.auth.services import create_access_token, get_current_user

        # Create a token with negative expiration (already expired)
        expired_token = create_access_token(
            data={"sub": "some-user-id"},
            expires_delta=timedelta(minutes=-1),
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(access_token=expired_token, db=test_db)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
