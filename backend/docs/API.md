# API Documentation

This document covers the API architecture, documentation approach, and best practices for the FastAPI backend application.

## Table of Contents

- [Overview](#overview)
- [API Documentation Tools](#api-documentation-tools)
- [API Versioning](#api-versioning)
- [Authentication](#authentication)
- [Request/Response Format](#requestresponse-format)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Available Endpoints](#available-endpoints)
- [OpenAPI Schema](#openapi-schema)
- [Testing APIs](#testing-apis)
- [Best Practices](#best-practices)

## Overview

The backend API is built with FastAPI, which provides automatic API documentation generation using the OpenAPI (Swagger) standard. This means documentation is always in sync with the code.

### Key Features

- **Automatic Documentation**: OpenAPI/Swagger docs auto-generated from code
- **Interactive Testing**: Swagger UI allows testing endpoints directly in browser
- **Type Safety**: Pydantic schemas ensure request/response validation
- **Versioning**: API versioning via URL path (`/api/v1/`)
- **Standards Compliant**: Follows REST and OpenAPI 3.1 specifications

## API Documentation Tools

### Swagger UI (Interactive)

Access interactive API documentation at:

```
http://localhost:8000/docs
```

**Features:**
- Try out API endpoints directly in browser
- View request/response schemas
- See example values
- Test authentication
- Download OpenAPI JSON schema

### ReDoc (Clean Documentation)

Access clean, readable documentation at:

```
http://localhost:8000/redoc
```

**Features:**
- Clean, professional layout
- Better for reading and sharing
- Search functionality
- Code samples in multiple languages
- Print-friendly

### OpenAPI JSON Schema

Download the raw OpenAPI schema at:

```
http://localhost:8000/openapi.json
```

**Use Cases:**
- Generate client SDKs
- Import into API testing tools (Postman, Insomnia)
- Generate TypeScript types for frontend
- API contract testing
- Documentation generation in other formats

## API Versioning

### Current Version: v1

All API endpoints are versioned using URL path prefixing:

```
/api/v1/users
/api/v1/auth/login
/api/v1/posts
```

### Version Strategy

- **Path-based versioning**: `/api/v1/`, `/api/v2/`
- **No breaking changes** within a version
- **Deprecation warnings** before version sunset
- **Migration guides** for version upgrades

### Example: Version Migration

```python
# Old v1 endpoint (deprecated)
GET /api/v1/users/{id}

# New v2 endpoint (with additional fields)
GET /api/v2/users/{id}
```

Both versions run simultaneously during transition period.

## Authentication

### JWT Token Authentication

The API uses JWT (JSON Web Token) for stateless authentication.

#### Login Flow

```bash
# 1. Login to get access token
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Using Access Token

```bash
# 2. Use access token in Authorization header
GET /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Details

- **Access Token Expiry**: 30 minutes
- **Token Type**: Bearer
- **Algorithm**: HS256 (HMAC SHA-256)
- **Storage**: Client-side (localStorage or httpOnly cookie)

### Protected Endpoints

Protected endpoints require valid JWT token:

```python
# In Swagger UI, click "Authorize" button
# Enter: Bearer <your_token>
# All subsequent requests will include the token
```

## Request/Response Format

### Request Format

All requests use JSON format:

```bash
POST /api/v1/users
Content-Type: application/json

{
  "email": "new@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Response Format

All responses follow consistent JSON structure:

#### Success Response

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "new@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-10-18T12:00:00Z",
  "updated_at": "2025-10-18T12:00:00Z"
}
```

#### Error Response

```json
{
  "detail": "Email already registered",
  "type": "validation_error",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### HTTP Status Codes

| Status Code | Meaning | Usage |
|-------------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Server unavailable (maintenance, overload) |

## Error Handling

### Error Response Structure

All errors return consistent JSON format:

```json
{
  "detail": "Human-readable error message",
  "type": "error_type",
  "request_id": "uuid-for-tracking",
  "errors": [
    {
      "field": "email",
      "message": "Email already registered"
    }
  ]
}
```

### Validation Errors (422)

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    },
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ],
  "type": "validation_error"
}
```

### Error Types

- `validation_error`: Request validation failed
- `authentication_error`: Authentication failed or missing
- `authorization_error`: Not authorized for this action
- `not_found`: Resource not found
- `conflict_error`: Resource conflict (duplicate email, etc.)
- `rate_limit_error`: Too many requests
- `server_error`: Internal server error

## Rate Limiting

Rate limiting prevents API abuse and ensures fair usage.

### Rate Limits

| Endpoint Type | Rate Limit | Window |
|--------------|------------|--------|
| Authentication | 10 requests | 15 minutes |
| Read Operations | 100 requests | 1 minute |
| Write Operations | 30 requests | 1 minute |
| File Uploads | 10 requests | 1 hour |

### Rate Limit Headers

Response includes rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1634567890
```

### Rate Limit Exceeded

```json
HTTP/1.1 429 Too Many Requests
Retry-After: 60

{
  "detail": "Rate limit exceeded. Please try again in 60 seconds.",
  "type": "rate_limit_error"
}
```

## Available Endpoints

### Health Check Endpoints

#### GET /health

Comprehensive health check including database status.

```bash
GET /health

Response (200 OK):
{
  "status": "healthy",
  "environment": "development",
  "version": "0.1.0",
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 5.2
    }
  }
}
```

#### GET /health/live

Liveness probe for Kubernetes.

```bash
GET /health/live

Response (200 OK):
{
  "status": "alive"
}
```

#### GET /health/ready

Readiness probe for Kubernetes.

```bash
GET /health/ready

Response (200 OK):
{
  "status": "ready",
  "checks": {
    "database": "ready"
  }
}
```

### Authentication Endpoints

#### POST /api/v1/auth/login

User login with email and password.

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST /api/v1/auth/register

User registration.

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "new@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}

Response (201 Created):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "new@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false
}
```

#### POST /api/v1/auth/logout

User logout (invalidate token).

```bash
POST /api/v1/auth/logout
Authorization: Bearer <token>

Response (204 No Content)
```

### User Endpoints

#### GET /api/v1/users/me

Get current user profile.

```bash
GET /api/v1/users/me
Authorization: Bearer <token>

Response (200 OK):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": true,
  "last_login": "2025-10-18T12:00:00Z"
}
```

#### PATCH /api/v1/users/me

Update current user profile.

```bash
PATCH /api/v1/users/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith"
}

Response (200 OK):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "full_name": "Jane Smith"
}
```

#### GET /api/v1/users/{user_id}

Get user by ID (admin only).

```bash
GET /api/v1/users/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <admin_token>

Response (200 OK):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true
}
```

## OpenAPI Schema

### Generating Client SDKs

Use the OpenAPI schema to generate type-safe client libraries:

#### TypeScript Client

```bash
# Install openapi-typescript-codegen
npm install -g openapi-typescript-codegen

# Generate TypeScript client
openapi --input http://localhost:8000/openapi.json --output ./src/api-client
```

#### Python Client

```bash
# Install openapi-python-client
pip install openapi-python-client

# Generate Python client
openapi-python-client generate --url http://localhost:8000/openapi.json
```

### Schema Customization

Customize OpenAPI schema in `main.py`:

```python
app = FastAPI(
    title="Backend API",
    description="Production-ready FastAPI backend",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
```

## Testing APIs

### Using Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter: `Bearer <your_token>`
4. Click endpoint to expand
5. Click "Try it out"
6. Fill in parameters
7. Click "Execute"
8. View response

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePassword123!"}'

# Get current user (with token)
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Using httpx (Python)

```python
import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Login
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "user@example.com",
            "password": "SecurePassword123!"
        })
        token = login_response.json()["access_token"]

        # Get current user
        headers = {"Authorization": f"Bearer {token}"}
        user_response = await client.get("/api/v1/users/me", headers=headers)
        print(user_response.json())

asyncio.run(test_api())
```

### Using Postman

1. Import OpenAPI schema: File → Import → http://localhost:8000/openapi.json
2. Set environment variable for base URL: `http://localhost:8000`
3. Set authorization type: Bearer Token
4. Use `{{access_token}}` variable in headers
5. Create requests and save to collection

## Best Practices

### API Design

1. **Use Proper HTTP Methods**
   - GET: Retrieve resources (idempotent, cacheable)
   - POST: Create resources
   - PUT: Replace entire resource (idempotent)
   - PATCH: Partial update
   - DELETE: Remove resource (idempotent)

2. **Use Plural Nouns for Resources**
   - ✓ `/api/v1/users`
   - ✗ `/api/v1/user`

3. **Use HTTP Status Codes Correctly**
   - 2xx: Success
   - 4xx: Client errors
   - 5xx: Server errors

4. **Version Your API**
   - Use path versioning: `/api/v1/`
   - Plan for backward compatibility
   - Document breaking changes

### Request/Response Design

1. **Use Pydantic Schemas**
   ```python
   class UserCreate(BaseModel):
       email: EmailStr
       password: str = Field(min_length=8)
       first_name: str
       last_name: Optional[str] = None
   ```

2. **Validate All Inputs**
   - Email format validation
   - Password strength requirements
   - String length limits
   - Required vs optional fields

3. **Return Appropriate Status Codes**
   ```python
   @router.post("/users", status_code=201)
   async def create_user(user: UserCreate):
       # Returns 201 Created
       pass
   ```

4. **Include Timestamps**
   - `created_at`: When resource was created
   - `updated_at`: When resource was last modified

### Security

1. **Never Return Sensitive Data**
   ```python
   class UserResponse(BaseModel):
       email: str
       # Don't include hashed_password!
   ```

2. **Use HTTPS in Production**
   - Encrypt all traffic
   - Set secure headers

3. **Implement Rate Limiting**
   - Prevent abuse
   - Protect against DDoS

4. **Validate Authorization**
   - Check user permissions
   - Don't rely on client-side validation

### Documentation

1. **Add Docstrings to Endpoints**
   ```python
   @router.get("/users/{user_id}")
   async def get_user(user_id: UUID):
       """
       Get user by ID.

       Requires admin permissions.
       """
       pass
   ```

2. **Use OpenAPI Tags**
   ```python
   router = APIRouter(prefix="/users", tags=["users"])
   ```

3. **Provide Example Values**
   ```python
   class UserCreate(BaseModel):
       email: EmailStr = Field(example="user@example.com")
   ```

4. **Document Error Responses**
   ```python
   @router.get("/users/{user_id}", responses={
       404: {"description": "User not found"},
       403: {"description": "Not authorized"}
   })
   ```

### Performance

1. **Use Async Endpoints**
   ```python
   @router.get("/users")
   async def get_users():  # async for I/O operations
       pass
   ```

2. **Implement Pagination**
   ```python
   @router.get("/users")
   async def get_users(skip: int = 0, limit: int = 100):
       pass
   ```

3. **Use Database Indexes**
   - Index frequently queried fields
   - Composite indexes for common queries

4. **Cache Responses**
   - Use Redis for expensive queries
   - Set appropriate TTL

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [REST API Best Practices](https://restfulapi.net/)
- [HTTP Status Codes](https://httpstatuses.com/)
- [JWT Introduction](https://jwt.io/introduction)

## Support

For API issues or questions:
1. Check this documentation
2. Review interactive Swagger docs at `/docs`
3. Check application logs
4. Review FastAPI documentation
5. Contact the development team
