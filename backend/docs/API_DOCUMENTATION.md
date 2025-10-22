# API Documentation Guide

## Overview

This document provides a comprehensive guide to the Backend API documentation system. The API uses OpenAPI 3.0 specification (formerly Swagger) with automatic documentation generation powered by drf-spectacular.

## Accessing the Documentation

The API documentation is available through multiple interfaces:

### Swagger UI (Interactive)
- **URL**: `http://localhost:8000/api/v1/docs/`
- **Features**:
  - Interactive API explorer
  - Try out API endpoints directly from the browser
  - View request/response examples
  - Test authentication flows
  - Copy example requests

### ReDoc (Readable)
- **URL**: `http://localhost:8000/api/v1/redoc/`
- **Features**:
  - Clean, readable documentation interface
  - Three-column layout for easy navigation
  - Code samples in multiple languages
  - Detailed schema documentation
  - Downloadable as PDF

### OpenAPI Schema (Raw)
- **URL**: `http://localhost:8000/api/v1/schema/`
- **Format**: JSON
- **Usage**:
  - Import into API clients (Postman, Insomnia, etc.)
  - Generate client SDKs
  - Automated testing tools
  - CI/CD integration

## Documentation Features

### 1. Endpoint Organization

All endpoints are organized by tags:

- **Health**: System health and monitoring endpoints
- **Authentication**: User registration, login, logout, token management
- **Users**: User profile and account management

### 2. Authentication Documentation

The documentation includes comprehensive JWT authentication information:

- How to obtain access and refresh tokens
- Token expiration times (access: 15 minutes, refresh: 7 days)
- How to use Bearer tokens in requests
- Token refresh flow
- Logout and token blacklisting

### 3. Request/Response Examples

Every endpoint includes:

- Example request payloads
- Example success responses
- Example error responses
- Field descriptions and validation rules
- Required vs optional parameters

### 4. Schema Definitions

All data models are fully documented with:

- Field types and formats
- Validation constraints
- Read-only vs writable fields
- Nested object structures

## Available Endpoints

### Health Endpoints

#### GET /api/v1/health/
Basic health check endpoint for monitoring.

**Response**: 200 OK (healthy) or 503 Service Unavailable (unhealthy)

#### GET /api/v1/status/
Detailed system status with version, uptime, memory usage, and database status.

**Response**: Always 200 OK with detailed information

#### GET /api/v1/health/ready/
Kubernetes readiness probe - checks if service is ready to accept traffic.

**Response**: 200 OK (ready) or 503 Service Unavailable (not ready)

#### GET /api/v1/health/live/
Kubernetes liveness probe - checks if service is alive and responsive.

**Response**: Always 200 OK if server is running

### Authentication Endpoints

#### POST /api/v1/auth/register/
Register a new user account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response**: 201 Created with user data

#### POST /api/v1/auth/login/
Authenticate user and receive JWT tokens.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response**: 200 OK with access and refresh tokens

#### POST /api/v1/auth/logout/
Logout user by blacklisting refresh token.

**Requires**: Authentication (Bearer token)

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response**: 200 OK

#### POST /api/v1/auth/token/refresh/
Obtain new access token using refresh token.

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response**: 200 OK with new access token (and potentially new refresh token)

### User Profile Endpoints

#### GET /api/v1/auth/me/
Get current authenticated user's profile.

**Requires**: Authentication (Bearer token)

**Response**: 200 OK with user data

#### POST /api/v1/auth/change-password/
Change authenticated user's password.

**Requires**: Authentication (Bearer token)

**Request Body**:
```json
{
  "old_password": "OldPass123!",
  "new_password": "NewSecurePass456!",
  "new_password_confirm": "NewSecurePass456!"
}
```

**Response**: 200 OK

## Authentication Flow

### 1. Register a New User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 2. Login to Get Tokens

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

Save the `access` and `refresh` tokens from the response.

### 3. Use Access Token for Authenticated Requests

```bash
curl -X GET http://localhost:8000/api/v1/auth/me/ \
  -H "Authorization: Bearer <access_token>"
```

### 4. Refresh Access Token When Expired

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<refresh_token>"
  }'
```

### 5. Logout (Optional)

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<refresh_token>"
  }'
```

## Error Responses

All endpoints follow consistent error response formats:

### 400 Bad Request
Validation errors or malformed requests.

```json
{
  "field_name": ["Error message describing the issue."]
}
```

### 401 Unauthorized
Authentication required or invalid/expired token.

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
Authenticated but lacking permission.

```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
Resource not found.

```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
Server error (should be rare in production).

```json
{
  "detail": "An error occurred processing your request."
}
```

## Updating Documentation

The API documentation is automatically generated from the code. When you add or modify endpoints:

### 1. Add Schema Documentation to Views

Use the `@extend_schema` decorator from drf-spectacular:

```python
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

class MyView(APIView):
    @extend_schema(
        summary="Brief endpoint description",
        description="Detailed description of what this endpoint does",
        request=MyRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=MyResponseSerializer,
                description="Success response description",
                examples=[
                    OpenApiExample(
                        'Example Name',
                        value={'key': 'value'},
                        response_only=True,
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Error description"
            )
        },
        tags=['Category']
    )
    def post(self, request):
        # Implementation
        pass
```

### 2. Document Serializer Fields

Add help_text and descriptions to serializer fields:

```python
class MySerializer(serializers.Serializer):
    email = serializers.EmailField(
        help_text='User email address',
        required=True
    )
    name = serializers.CharField(
        help_text='User full name',
        max_length=100
    )
```

### 3. Update Settings (if needed)

Modify `SPECTACULAR_SETTINGS` in `config/settings/base.py` to:
- Add new tags
- Update API version
- Modify UI settings
- Add custom schema hooks

### 4. Generate Updated Schema

The schema is automatically generated when you access the documentation URLs. To manually generate and save the schema:

```bash
python manage.py spectacular --file schema.yml
```

## Testing with Documentation

### Using Swagger UI

1. Navigate to `http://localhost:8000/api/v1/docs/`
2. Click on an endpoint to expand it
3. Click "Try it out"
4. Fill in the request parameters
5. For authenticated endpoints:
   - Click "Authorize" button at the top
   - Enter: `Bearer <your_access_token>`
   - Click "Authorize"
6. Click "Execute" to send the request
7. View the response below

### Using Postman

1. Download the schema: `http://localhost:8000/api/v1/schema/`
2. In Postman: File > Import > Paste the schema URL
3. All endpoints will be imported with examples
4. Set up environment variables for tokens
5. Test the API

### Using cURL

See the "Authentication Flow" section above for example cURL commands.

## Best Practices

### 1. Keep Documentation Up-to-Date

- Add schema decorators to new endpoints immediately
- Update examples when response formats change
- Document all required and optional parameters
- Include realistic example values

### 2. Provide Clear Descriptions

- Explain what the endpoint does, not just what it returns
- Document side effects (e.g., "sends email", "creates audit log")
- Mention authentication requirements
- Note any rate limits or special considerations

### 3. Include Multiple Examples

- Show successful request/response
- Show common error cases
- Demonstrate optional parameters
- Provide realistic data values

### 4. Tag Endpoints Appropriately

- Group related endpoints together
- Use consistent tag names
- Update SPECTACULAR_SETTINGS when adding new tags
- Provide tag descriptions

### 5. Version Your API

- Use URL versioning (/api/v1/, /api/v2/)
- Document breaking changes
- Maintain backward compatibility when possible
- Clearly mark deprecated endpoints

## Troubleshooting

### Documentation Not Updating

1. Restart the development server
2. Clear browser cache
3. Check for syntax errors in decorators
4. Verify SPECTACULAR_SETTINGS configuration

### Missing Endpoints

1. Ensure views are registered in urls.py
2. Check that views have proper decorators
3. Verify DEFAULT_SCHEMA_CLASS in REST_FRAMEWORK settings
4. Check for exclude patterns in SPECTACULAR_SETTINGS

### Incorrect Schema Generation

1. Verify serializer field types
2. Check for custom serializer methods
3. Review inline_serializer usage
4. Test with manual schema generation

## Additional Resources

- [drf-spectacular Documentation](https://drf-spectacular.readthedocs.io/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [JWT Authentication](https://jwt.io/)

## Support

For issues or questions about the API documentation:
- Review this guide
- Check the drf-spectacular documentation
- Contact the development team
- Submit an issue in the project repository
