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


@pytest.fixture
def client_with_auth():
    """Create a TestClient with an authenticated user (for router tests).
    
    This is a synchronous fixture for use with TestClient, which runs
    HTTP requests synchronously. It sets up:
    - In-memory SQLite database
    - Test user with username="testuser", password="testpass123"
    - Valid JWT token stored in httponly cookie
    - Dependency override so FastAPI uses our test database
    
    The fixture exposes the test user and token via attributes:
    - client.test_user: The test User object
    - client.test_token: Valid JWT token string
    
    Usage in tests:
        def test_something(self, client_with_auth):
            response = client_with_auth.post("/endpoint", json={"key": "value"})
            assert response.status_code == 200
    """
    from app.database import get_db
    from app.main import app
    from fastapi.testclient import TestClient
    
    async def setup_test_db_and_user():
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
            connect_args={"timeout": 10},
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
        async with SessionLocal() as session:
            # Create a test user
            user_data = UserCreate(username="testuser", password="testpass123")
            user = await create_user(session, user_data)
            
            # Create a token for the user
            access_token_expires = timedelta(minutes=30)
            token = create_access_token(
                data={"sub": str(user.id)},
                expires_delta=access_token_expires,
            )
            
            return session, engine, user, token
    
    # Run async setup
    session, engine, user, token = asyncio.run(setup_test_db_and_user())
    
    def override_get_db():
        return session
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    
    # Store auth info on client for easy access
    client.test_user = user
    client.test_token = token
    
    yield client
    
    # Cleanup
    app.dependency_overrides.clear()
