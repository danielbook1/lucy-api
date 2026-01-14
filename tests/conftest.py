import asyncio
import uuid
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.database import Base
from app.auth.schemas import UserCreate
from app.auth.services import create_user, create_access_token
from datetime import timedelta


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"timeout": 10},
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(
        bind=engine, expire_on_commit=False
    )
    
    async with SessionLocal() as session:
        yield session
        await session.close()

    await engine.dispose()


@pytest.fixture
async def test_user(test_db):
    """Create a test user in the database."""
    user_data = UserCreate(username="testuser", password="testpass123")
    return await create_user(test_db, user_data)


@pytest.fixture
async def test_user_token(test_user):
    """Create a valid JWT token for the test user."""
    access_token_expires = timedelta(minutes=30)
    token = create_access_token(
        data={"sub": str(test_user.id)},
        expires_delta=access_token_expires,
    )
    return token
