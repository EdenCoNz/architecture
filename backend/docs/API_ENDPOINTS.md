# API Endpoints Documentation

## Base URL
- Development: `http://localhost:8000`
- Production: TBD

## Health & Monitoring

### Health Check
Check server health status.

**Endpoint:** `GET /health/`

**Authentication:** Not required

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-19T12:00:00.000000Z",
  "service": "backend-api",
  "version": "0.1.0",
  "database": "connected",
  "debug_mode": false
}
```

**Status Codes:**
- `200 OK` - Server is healthy
- `503 Service Unavailable` - Server is unhealthy

**Example:**
```bash
curl -X GET http://localhost:8000/health/
```

---

## Documentation

### OpenAPI Schema
Get the OpenAPI schema for the API.

**Endpoint:** `GET /api/schema/`

**Authentication:** Not required

**Response:** OpenAPI 3.0 schema (JSON)

**Example:**
```bash
curl -X GET http://localhost:8000/api/schema/
```

---

### Swagger UI
Interactive API documentation.

**Endpoint:** `GET /api/docs/`

**Authentication:** Not required

**Description:** Browser-based interactive API documentation

**URL:** http://localhost:8000/api/docs/

---

### ReDoc
Alternative API documentation viewer.

**Endpoint:** `GET /api/redoc/`

**Authentication:** Not required

**Description:** Clean, responsive API documentation

**URL:** http://localhost:8000/api/redoc/

---

## Admin Interface

### Django Admin
Access Django admin interface.

**Endpoint:** `GET /admin/`

**Authentication:** Admin credentials required

**URL:** http://localhost:8000/admin/

---

## Error Responses

All error responses follow a consistent JSON format:

### 400 Bad Request
```json
{
  "error": "Validation Error",
  "message": "The request contains invalid data",
  "errors": {
    "field_name": ["Error message for this field"]
  },
  "path": "/api/endpoint/"
}
```

### 401 Unauthorized
```json
{
  "error": "Not Authenticated",
  "message": "Authentication credentials were not provided",
  "path": "/api/endpoint/"
}
```

### 403 Forbidden
```json
{
  "error": "Permission Denied",
  "message": "You do not have permission to access this resource",
  "path": "/api/endpoint/"
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "The requested resource was not found",
  "path": "/api/endpoint/"
}
```

### 500 Internal Server Error

**Production (DEBUG=False):**
```json
{
  "error": "Internal Server Error",
  "message": "An internal server error occurred. Please try again later.",
  "path": "/api/endpoint/"
}
```

**Development (DEBUG=True):**
```json
{
  "error": "Internal Server Error",
  "message": "Detailed error message",
  "exception_type": "ExceptionClassName",
  "path": "/api/endpoint/",
  "traceback": ["..."]
}
```

---

## Common Headers

### Request Headers
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer <token>  # For authenticated endpoints
```

### Response Headers
```
Content-Type: application/json
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
```

---

## Rate Limiting
TBD - Rate limiting will be implemented in future stories

---

## Authentication
TBD - Authentication endpoints will be implemented in future stories

---

## Pagination
All list endpoints use pagination:

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

**Response Format:**
```json
{
  "count": 100,
  "next": "http://api.example.com/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Testing Endpoints

### Using cURL

```bash
# Health check
curl -X GET http://localhost:8000/health/

# Get API schema
curl -X GET http://localhost:8000/api/schema/

# POST request with JSON data
curl -X POST http://localhost:8000/api/endpoint/ \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'

# Authenticated request
curl -X GET http://localhost:8000/api/protected/ \
  -H "Authorization: Bearer <token>"
```

### Using HTTPie

```bash
# Health check
http GET http://localhost:8000/health/

# POST request with JSON data
http POST http://localhost:8000/api/endpoint/ key=value

# Authenticated request
http GET http://localhost:8000/api/protected/ \
  Authorization:"Bearer <token>"
```

### Using Python Requests

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health/")
print(response.json())

# POST request
response = requests.post(
    "http://localhost:8000/api/endpoint/",
    json={"key": "value"},
    headers={"Content-Type": "application/json"}
)

# Authenticated request
response = requests.get(
    "http://localhost:8000/api/protected/",
    headers={"Authorization": "Bearer <token>"}
)
```

---

## Development Tools

### Debug Toolbar
Available in development mode at: `/__debug__/`

Only visible when:
- `DEBUG=True`
- Request is from `127.0.0.1` or `localhost`

---

## API Versioning
TBD - API versioning strategy will be defined in future stories

---

## CORS Policy

### Allowed Origins (Development)
- `http://localhost:5173`
- `http://127.0.0.1:5173`

### Allowed Origins (Production)
Configured via `CORS_ALLOWED_ORIGINS` environment variable

### Allowed Methods
- GET
- POST
- PUT
- PATCH
- DELETE
- OPTIONS

### Credentials
Cookies and authorization headers are allowed (`CORS_ALLOW_CREDENTIALS=True`)

---

## Future Endpoints

The following endpoints will be added in future stories:

- `/api/v1/auth/login/` - User login
- `/api/v1/auth/logout/` - User logout
- `/api/v1/auth/register/` - User registration
- `/api/v1/auth/refresh/` - Token refresh
- `/api/v1/users/` - User management
- `/api/v1/users/me/` - Current user profile

---

## Changelog

### 2025-10-19 - Initial Release
- Added health check endpoint
- Added API documentation endpoints
- Configured error response format
- Implemented request logging
- Implemented global error handling
