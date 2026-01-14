# Lucy API - AI Agent Instructions

## Architecture Overview

Lucy API is a FastAPI-based task/project management backend with JWT authentication. The architecture follows a modular, domain-driven design with three core modules: **auth**, **clients**, and **projects**.

### Key Components
- **Framework**: FastAPI 0.116 with async SQLAlchemy 2.0 and SQLite
- **Database**: SQLite with async driver (aiosqlite), auto-created at startup via lifespan context
- **Auth**: JWT tokens via PyJWT + PassLib bcrypt, with cookie-based session storage (httponly, strict SameSite)
- **Modules**: Auth (User management), Clients (project clients), Projects (projects/tasks)

### Data Model Relationships
```
User (root entity)
├── Clients (many, cascade delete)
├── Projects (many, cascade delete)
└── Tasks (many, cascade delete)

Client
└── Projects (many, cascade delete)

Project
└── Tasks (many, cascade delete)
```

## Development Workflow

**Start server**: `fastapi run main.py` (auto-reloads)
**Environment**: `.env` file required with `DATABASE_URL`, `EXPIRE_TIME`, `ALGORITHM`, `SECRET_KEY`

## Code Patterns & Conventions

### Module Structure (Auth, Clients, Projects)
Each module contains:
- `models.py` - SQLAlchemy ORM models with UUID primary keys and relationships
- `router.py` - FastAPI APIRouter with endpoint definitions
- `schemas.py` - Pydantic V2 models with `ConfigDict(from_attributes=True)` for ORM serialization
- `services.py` - Business logic (async functions for DB operations)

### Router Pattern
Routes use dependency injection:
```python
@router.post("/endpoint", response_model=SomeSchema)
async def handler(data: InputSchema, db: AsyncSession = Depends(get_db)):
    return await service_function(db, data)
```

### Service Pattern (see `auth/services.py`)
- Async functions accepting `AsyncSession` as first parameter
- Use `select()` queries with `.where()` filters, then `.scalar_one_or_none()` or `.all()`
- Manual `db.add()`, `db.commit()`, `db.refresh()` for mutations
- Raise `HTTPException(status_code=..., detail="...")` for errors

### Schema Pattern
- Separate `*Base`, `*Create`, `*Read`, `*InDB` schemas
- Use `ConfigDict(from_attributes=True)` to allow ORM model hydration
- Use `TYPE_CHECKING` imports for forward references to avoid circular imports

### Authentication
- `OAuth2PasswordBearer` token URL points to `/auth/token`
- JWT tokens created with expiration in UTC timezone
- Tokens stored in httponly cookies (not Authorization headers)
- Get current user via `Depends(get_current_user)` in protected routes

### Database Operations
- Always use async/await with `AsyncSession` and `async with` contexts
- Configure in [app/database.py](app/database.py): SQLite URL format is `sqlite+aiosqlite:///` + path
- Base ORM models inherit from `Base` (declarative_base instance)
- Models use `UUID` columns with `default=uuid.uuid4` for IDs

### CORS
Configured in [app/main.py](app/main.py) for localhost:3000 (frontend dev server)

## Critical Files by Purpose
- **Entry point**: [app/main.py](app/main.py) - FastAPI app setup, routers, middleware, lifespan
- **Config**: [app/config.py](app/config.py) - Environment variable loading
- **Database setup**: [app/database.py](app/database.py) - Engine, session, Base
- **Auth logic**: [app/auth/services.py](app/auth/services.py) - Hashing, JWT, user creation
- **Data models**: [app/auth/models.py](app/auth/models.py), [app/clients/models.py](app/clients/models.py), [app/projects/models.py](app/projects/models.py)

## Important Conventions
1. **No generic exception handling** - Use typed HTTPException with status codes
2. **Explicit field nullability** - Models use `nullable=True/False` consistently
3. **Cascade deletes** - Child records auto-delete when parent is deleted
4. **User context** - All projects/tasks/clients tied to `user_id` (multi-tenant at user level)
5. **Token expiration** - JWT_EXP is in minutes, user configurable via `.env` EXPIRE_TIME (in seconds)

## Testing

### Test Structure
```
tests/
├── conftest.py          # Shared fixtures for all tests
├── auth/
│   ├── test_services.py # Unit tests for auth logic
│   └── test_router.py   # Integration tests for API endpoints
└── clients/ & projects/ # Follow same structure
```

### Key Fixtures (conftest.py)
- `test_db` - In-memory SQLite session for isolated tests
- `test_user` - Pre-created test user in database
- `test_user_token` - Valid JWT token for test user
- `override_get_db` - Override FastAPI's dependency for testing

### Running Tests
```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/auth/ -v

# Single test file
pytest tests/auth/test_services.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Patterns
- **Service tests** (`test_services.py`): Test business logic directly, use `@pytest.mark.asyncio`
- **Router tests** (`test_router.py`): Use `TestClient` with `app.dependency_overrides[get_db]`
- **Error cases**: Always test HTTPException scenarios (400, 401, 422 status codes)
- **Auth tests**: Verify token generation, validation, expired tokens, deleted users

### Required Dependencies
Add to requirements-dev.txt:
```
pytest==7.4.0
pytest-asyncio==0.21.0
httpx==0.24.0
```

## Debugging
- Check `.env` file exists with all required keys: `DATABASE_URL`, `EXPIRE_TIME`, `ALGORITHM`, `SECRET_KEY`
- Database auto-migrates on startup via SQLAlchemy metadata.create_all()
- Use FastAPI's auto-generated `/docs` endpoint for API exploration
