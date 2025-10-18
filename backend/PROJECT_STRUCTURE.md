# Backend Project Structure - FastAPI

This document outlines the directory organization for the FastAPI backend application. The structure follows industry best practices for scalable, maintainable, production-ready APIs based on the technology stack selected in Feature #3 Story #1.

## Selected Technology Stack

- **Framework**: FastAPI 0.115+ (Python 3.12+)
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0 (async)
- **Cache/Sessions**: Redis 7.2
- **Authentication**: FastAPI Security + PyJWT
- **Testing**: pytest + httpx
- **Migrations**: Alembic
- **ASGI Server**: Uvicorn

## Directory Overview

```
backend/
├── app/                      # Application code
│   ├── api/                 # API endpoints
│   │   └── v1/             # API version 1
│   ├── core/               # Core functionality
│   ├── models/             # SQLAlchemy database models
│   ├── schemas/            # Pydantic schemas (request/response)
│   └── services/           # Business logic layer
├── alembic/                 # Database migrations
│   ├── versions/           # Migration files
│   ├── env.py              # Alembic environment config
│   └── script.py.mako      # Migration template
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── requirements/            # Python dependencies
│   ├── base.txt            # Core dependencies
│   ├── development.txt     # Development tools
│   ├── production.txt      # Production dependencies
│   └── test.txt            # Testing dependencies
├── main.py                  # Application entry point
├── .env                     # Environment variables (not committed)
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore patterns
├── pyproject.toml           # Python project configuration (Black, Ruff, mypy, pytest)
├── alembic.ini              # Alembic configuration
├── README.md                # Project documentation
└── PROJECT_STRUCTURE.md    # This file
```

## Directory Details

### app/

Main application package containing all application code organized by responsibility.

#### app/api/

API endpoints organized by version. This allows for API versioning and gradual migration to new API versions without breaking existing clients.

**Structure:**
```
app/api/
├── __init__.py
└── v1/
    ├── __init__.py
    ├── router.py           # Main API v1 router
    ├── endpoints/
    │   ├── __init__.py
    │   ├── auth.py         # Authentication endpoints
    │   ├── users.py        # User management endpoints
    │   └── health.py       # Health check endpoint
    └── dependencies.py     # API-level dependencies (auth, pagination, etc.)
```

**Key Principles:**
- Each endpoint module focuses on a specific domain or feature
- Use FastAPI `APIRouter` for modular route organization
- Keep endpoints thin - delegate business logic to services
- Version APIs using path prefixes (`/api/v1/`, `/api/v2/`)

**Example endpoint structure:**
```python
# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends()
):
    """Create a new user."""
    return await user_service.create_user(user_data)
```

#### app/core/

Core application functionality including configuration, security, database connections, and shared utilities.

**Expected structure:**
```
app/core/
├── __init__.py
├── config.py               # Pydantic settings
├── security.py             # JWT, password hashing, authentication
├── database.py             # Database session management
├── redis.py                # Redis connection and caching utilities
└── exceptions.py           # Custom exception classes
```

**Configuration (config.py):**
- Uses Pydantic Settings for type-safe configuration
- Loads from environment variables or `.env` file
- Validates all settings at startup
- Provides environment-specific configuration (development, staging, production)

**Security (security.py):**
- JWT token creation and validation
- Password hashing with bcrypt
- OAuth2 password bearer for FastAPI
- Security dependencies for protected routes

**Database (database.py):**
- Async SQLAlchemy engine and session factory
- Connection pooling configuration
- Session dependency for dependency injection
- Transaction management utilities

#### app/models/

SQLAlchemy ORM models representing database tables.

**Structure:**
```
app/models/
├── __init__.py
├── base.py                 # Base model with common fields (id, created_at, updated_at)
├── user.py                 # User model
├── session.py              # Session model (if using database sessions)
└── mixins.py               # Reusable model mixins
```

**Key Principles:**
- Use SQLAlchemy 2.0 syntax with type annotations
- Inherit from declarative base
- Define relationships using SQLAlchemy relationships
- Include common fields in base model (timestamps, soft delete)
- Keep models focused on data representation
- Business logic belongs in services, not models

**Example model:**
```python
# app/models/user.py
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
```

#### app/schemas/

Pydantic schemas for request validation and response serialization.

**Structure:**
```
app/schemas/
├── __init__.py
├── user.py                 # User schemas (UserCreate, UserUpdate, UserResponse)
├── auth.py                 # Auth schemas (Token, TokenPayload, LoginRequest)
└── common.py               # Common schemas (Pagination, ErrorResponse)
```

**Key Principles:**
- Separate schemas for create, update, and response
- Use Pydantic v2 for validation
- Include example data in schema for OpenAPI docs
- Implement field validation with Pydantic validators
- Keep schemas focused on data structure, not business logic

**Example schemas:**
```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8)

class UserResponse(UserBase):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}
```

#### app/services/

Business logic layer containing service classes that encapsulate complex operations.

**Structure:**
```
app/services/
├── __init__.py
├── user_service.py         # User-related business logic
├── auth_service.py         # Authentication business logic
├── cache_service.py        # Caching operations
└── email_service.py        # Email sending (if applicable)
```

**Key Principles:**
- Services handle business logic and orchestration
- Services interact with database via repository pattern (optional)
- Keep endpoints thin - delegate to services
- Services are reusable across different endpoints
- Use dependency injection for testability

**Example service:**
```python
# app/services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with hashed password."""
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            hashed_password=hashed_password
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
```

### alembic/

Database migration management using Alembic.

**Structure:**
```
alembic/
├── versions/               # Migration files (auto-generated)
│   └── [timestamp]_description.py
├── env.py                  # Alembic environment (async support)
└── script.py.mako          # Migration template
```

**Migration Workflow:**
1. Make model changes in `app/models/`
2. Generate migration: `alembic revision --autogenerate -m "Description"`
3. Review generated migration file
4. Apply migration: `alembic upgrade head`
5. Commit migration file to version control

**Key Configuration:**
- Configured for async SQLAlchemy (see `alembic/env.py`)
- Reads database URL from application settings
- Supports autogenerate from SQLAlchemy models
- Migrations are reversible (upgrade/downgrade)

### tests/

Comprehensive test suite organized by test type.

#### tests/unit/

Unit tests for isolated component testing. Fast execution, no external dependencies.

**Characteristics:**
- Test individual functions, classes, methods
- No database or network calls
- Use mocks and stubs for dependencies
- Focus on business logic and utilities

**Example:**
```python
# tests/unit/test_security.py
from app.core.security import verify_password, get_password_hash

def test_password_hashing():
    password = "test_password123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)
```

#### tests/integration/

Integration tests verifying component interactions, database operations, and API endpoints.

**Characteristics:**
- Test database interactions with test database
- Verify ORM operations and queries
- Test API endpoint responses
- Verify authentication and authorization

**Example:**
```python
# tests/integration/test_users.py
from httpx import AsyncClient
from app.main import app

async def test_create_user(client: AsyncClient):
    response = await client.post("/api/v1/users", json={
        "email": "test@example.com",
        "password": "secure_password123"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
```

#### tests/e2e/

End-to-end tests simulating real user workflows across the application.

**Characteristics:**
- Test complete user journeys
- Verify multi-step workflows (register → login → access protected resource)
- Test external integrations
- Slower but high confidence

### requirements/

Python dependencies organized by environment.

**Files:**

- **base.txt**: Core dependencies needed in all environments
  - FastAPI, Uvicorn, Pydantic, SQLAlchemy, Alembic, PostgreSQL drivers, Redis, JWT libraries

- **development.txt**: Development tools (includes base.txt)
  - ipython, ipdb, Black, Ruff, mypy, pre-commit

- **production.txt**: Production dependencies (includes base.txt)
  - Gunicorn, Sentry SDK, enhanced cryptography

- **test.txt**: Testing tools (includes base.txt)
  - pytest, pytest-asyncio, pytest-cov, httpx, Faker

**Usage:**
```bash
# Development (default)
pip install -r requirements.txt

# Production
pip install -r requirements/production.txt

# Testing
pip install -r requirements/test.txt
```

### Root Files

#### main.py

Application entry point that creates and configures the FastAPI application.

**Responsibilities:**
- Initialize FastAPI app with metadata
- Configure CORS middleware
- Register API routers
- Define startup/shutdown events
- Configure exception handlers
- Enable logging

**Can be run directly:**
```bash
python main.py
# or
uvicorn main:app --reload
```

#### .env and .env.example

Environment variable configuration.

- `.env`: Local environment variables (not committed to git)
- `.env.example`: Template showing all required variables (committed to git)

**Key variables:**
- `ENVIRONMENT`: development/staging/production
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key (min 32 chars)
- `CORS_ORIGINS`: Allowed CORS origins

#### pyproject.toml

Python project configuration for tooling.

**Configures:**
- **Black**: Code formatter (line length: 88, Python 3.12)
- **Ruff**: Fast Python linter (replaces Flake8, isort)
- **mypy**: Static type checker with strict settings
- **pytest**: Test configuration, markers, asyncio mode
- **Coverage**: Coverage reporting configuration

#### alembic.ini

Alembic migration configuration.

- Script location: `alembic/`
- Database URL: Read from application settings
- Logging configuration for migrations

## FastAPI Best Practices

### Dependency Injection

Use FastAPI's dependency injection for:
- Database sessions
- Current user authentication
- Service instances
- Pagination parameters

```python
from fastapi import Depends
from app.core.database import get_db

@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    # db session injected automatically
    pass
```

### Async/Await

- Use `async def` for all endpoints and database operations
- SQLAlchemy sessions are async (`AsyncSession`)
- Await all async operations
- Don't mix sync and async database drivers

### Response Models

Define response models for type safety and automatic documentation:

```python
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    # Response automatically validated and serialized
    pass
```

### Error Handling

Use HTTPException for API errors:

```python
from fastapi import HTTPException, status

if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )
```

### Type Hints

Use type hints everywhere for:
- Better IDE support
- Automatic validation
- Clear documentation
- mypy type checking

## Security Considerations

### Authentication

- JWT tokens for stateless authentication
- Access tokens: 30 minutes expiry
- Refresh tokens: 7 days expiry
- Secure password hashing with bcrypt

### Input Validation

- All inputs validated by Pydantic schemas
- Email validation with `EmailStr`
- Password strength requirements
- SQL injection prevention via SQLAlchemy parameterized queries

### Environment-Specific Security

**Development:**
- DEBUG=true
- API docs enabled at `/docs` and `/redoc`
- Permissive CORS for localhost

**Production:**
- DEBUG=false
- API docs disabled
- Restricted CORS to production domains
- HTTPS enforced
- Strong SECRET_KEY (32+ chars)

### File Permissions

- `.env` file: 600 (read/write owner only)
- Application code: 644
- Scripts: 755
- Never commit `.env` to version control

## Configuration Management

### Pydantic Settings

Configuration loaded from environment with validation:

```python
from app.core import settings

# Type-safe access
database_url = settings.database_url
is_prod = settings.is_production
```

### Environment Variables

Load from `.env` file in development:
```bash
# .env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
SECRET_KEY=your-secret-key-min-32-chars
```

Use environment variables in production (Kubernetes, Docker, etc.)

## Testing Best Practices

### Test Structure

- Mirror app structure in tests
- Use fixtures for common setup
- Separate test database from development
- Use pytest-asyncio for async tests

### Coverage Target

- Aim for 80%+ coverage on business-critical code
- 100% coverage on security-related code
- Lower coverage acceptable for boilerplate

### Test Database

- Use in-memory SQLite for fast unit tests
- Use PostgreSQL for integration tests (identical to production)
- Reset database between tests

## Development Workflow

### Initial Setup

1. Clone repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure
6. Run migrations: `alembic upgrade head`
7. Start server: `python main.py`

### Daily Development

1. Activate virtual environment
2. Pull latest changes
3. Install new dependencies if needed
4. Run migrations: `alembic upgrade head`
5. Start dev server with hot-reload
6. Write tests (TDD approach)
7. Format and lint before commit

### Pre-Commit

Run before committing:
```bash
black .                  # Format code
ruff check .             # Lint code
mypy app/                # Type check
pytest                   # Run tests
```

## Production Deployment

### Environment Setup

- Set `ENVIRONMENT=production`
- Set `DEBUG=false`
- Generate strong `SECRET_KEY` (32+ characters)
- Configure production database URL
- Configure production Redis URL
- Set restricted `CORS_ORIGINS`

### Application Server

Use Gunicorn with Uvicorn workers:
```bash
gunicorn main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Deployment Checklist

- [ ] Dependencies installed from `requirements/production.txt`
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Static files served (if any)
- [ ] HTTPS enabled via reverse proxy
- [ ] Error tracking configured (Sentry)
- [ ] Logging configured with appropriate levels
- [ ] Health check endpoint monitored
- [ ] Database backups automated
- [ ] Redis configured with persistence

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy 2.0 Documentation**: https://docs.sqlalchemy.org/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Alembic Documentation**: https://alembic.sqlalchemy.org/
- **pytest Documentation**: https://docs.pytest.org/
- **Technology Stack Analysis**: `docs/features/3/backend-technology-stack-analysis.md`
- **Stack Decision**: `docs/features/3/STACK-DECISION.md`
