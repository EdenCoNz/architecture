# Authentication System Documentation

## Overview

The authentication system implements secure JWT-based authentication using Django REST Framework and Simple JWT. The system uses email as the primary identifier instead of username and provides comprehensive authentication functionality including registration, login, logout, token refresh, and password management.

## Architecture

### Technology Stack

- **Django REST Framework**: API framework
- **Simple JWT**: JWT token generation and validation
- **Token Blacklist**: Secure logout by blacklisting refresh tokens
- **Custom User Model**: Email-based authentication
- **Argon2**: Secure password hashing

### User Model

**Location**: `apps/users/models.py`

The custom User model extends Django's `AbstractUser` and makes the following changes:
- Removes the `username` field
- Uses `email` as the `USERNAME_FIELD`
- Implements custom `UserManager` for user creation
- Uses email normalization for consistency

**Fields**:
- `email`: Unique email address (required)
- `first_name`: User's first name (optional)
- `last_name`: User's last name (optional)
- `is_active`: Account activation status
- `is_staff`: Staff status for admin access
- `is_superuser`: Superuser status
- `date_joined`: Registration timestamp
- `last_login`: Last login timestamp

### Token Configuration

**Access Token**:
- Lifetime: 15 minutes
- Used for API authentication
- Short-lived for security

**Refresh Token**:
- Lifetime: 7 days
- Used to obtain new access tokens
- Rotated on refresh
- Blacklisted on logout

## API Endpoints

### 1. User Registration

**Endpoint**: `POST /api/v1/auth/register/`

**Authentication**: None required

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

**Response** (201 Created):
```json
{
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "date_joined": "2025-01-15T10:30:00Z"
  }
}
```

**Validation**:
- Email must be unique and valid
- Passwords must match
- Password must meet Django's validation requirements (min 8 characters, not common, not numeric only)

### 2. User Login

**Endpoint**: `POST /api/v1/auth/login/`

**Authentication**: None required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "message": "Login successful.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "date_joined": "2025-01-15T10:30:00Z"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Response** (400 Bad Request):
```json
{
  "non_field_errors": ["Invalid credentials. Please try again."]
}
```

### 3. Token Refresh

**Endpoint**: `POST /api/v1/auth/token/refresh/`

**Authentication**: None required

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Notes**:
- Returns a new access token and rotated refresh token
- Old refresh token is automatically blacklisted
- Invalid or expired refresh tokens return 401

### 4. User Logout

**Endpoint**: `POST /api/v1/auth/logout/`

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response** (200 OK):
```json
{
  "message": "Logout successful."
}
```

**Notes**:
- Blacklists the provided refresh token
- After logout, the refresh token cannot be used to obtain new access tokens
- Access token remains valid until expiration (implement client-side token clearing)

### 5. Get Current User

**Endpoint**: `GET /api/v1/auth/me/`

**Authentication**: Required (Bearer token)

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "date_joined": "2025-01-15T10:30:00Z"
}
```

### 6. Change Password

**Endpoint**: `POST /api/v1/auth/change-password/`

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "old_password": "SecurePass123!",
  "new_password": "NewSecurePass456!",
  "new_password_confirm": "NewSecurePass456!"
}
```

**Response** (200 OK):
```json
{
  "message": "Password changed successfully."
}
```

**Validation**:
- Old password must be correct
- New passwords must match
- New password must meet validation requirements

## Authentication Flow

### Registration Flow
1. User submits registration form
2. System validates email uniqueness and password strength
3. User account is created with hashed password
4. User can then login with credentials

### Login Flow
1. User submits email and password
2. System validates credentials
3. If valid, generates JWT access and refresh tokens
4. Client stores both tokens
5. Client uses access token for API requests

### Token Refresh Flow
1. When access token expires (15 minutes)
2. Client sends refresh token to refresh endpoint
3. System validates refresh token
4. Returns new access token and rotated refresh token
5. Old refresh token is blacklisted

### Logout Flow
1. Client sends refresh token to logout endpoint
2. System blacklists the refresh token
3. Client clears stored tokens
4. User must login again to get new tokens

### Protected Resource Access
1. Client includes access token in Authorization header
2. System validates token signature and expiration
3. If valid, identifies user and processes request
4. If invalid/expired, returns 401 Unauthorized

## Security Features

### Password Security
- **Hashing**: Uses Argon2 algorithm (industry standard)
- **Validation**: Enforces minimum length, complexity requirements
- **No Plain Text**: Passwords never stored in plain text

### Token Security
- **Short-lived Access Tokens**: 15-minute expiration reduces exposure window
- **Rotating Refresh Tokens**: New refresh token issued on each refresh
- **Token Blacklist**: Prevents reuse of logged-out refresh tokens
- **Signature Verification**: Prevents token tampering

### Error Messages
- **Generic Errors**: Authentication failures don't reveal if email exists
- **No Information Leakage**: Errors are user-friendly but not revealing
- **Rate Limiting**: Configured in DRF settings (100/hour for anonymous, 1000/hour for authenticated)

### Additional Security
- **HTTPS Required**: Production should enforce HTTPS
- **CORS Configuration**: Restricts cross-origin requests
- **CSRF Protection**: Django middleware enabled
- **Security Headers**: XSS filter, content type nosniff enabled

## Client Implementation Guide

### Storing Tokens

```javascript
// Store tokens after login
localStorage.setItem('access_token', response.data.access);
localStorage.setItem('refresh_token', response.data.refresh);

// Or use more secure httpOnly cookies (recommended)
```

### Making Authenticated Requests

```javascript
// Include access token in Authorization header
const config = {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
};

axios.get('/api/v1/auth/me/', config);
```

### Handling Token Expiration

```javascript
// Intercept 401 responses
axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Attempt to refresh token
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post('/api/v1/auth/token/refresh/', {
          refresh: refreshToken
        });

        // Update stored tokens
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);

        // Retry original request with new token
        originalRequest.headers['Authorization'] = `Bearer ${response.data.access}`;
        return axios(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

### Logout

```javascript
// Logout and clear tokens
const refreshToken = localStorage.getItem('refresh_token');
const accessToken = localStorage.getItem('access_token');

await axios.post(
  '/api/v1/auth/logout/',
  { refresh: refreshToken },
  { headers: { 'Authorization': `Bearer ${accessToken}` } }
);

// Clear stored tokens
localStorage.removeItem('access_token');
localStorage.removeItem('refresh_token');

// Redirect to login
window.location.href = '/login';
```

## Testing

### Running Tests

```bash
# Run all authentication tests
pytest tests/unit/test_user_model.py
pytest tests/unit/test_auth_serializers.py
pytest tests/integration/test_auth_endpoints.py
pytest tests/acceptance/test_story_6_authentication.py

# Or run all tests
pytest
```

### Test Coverage

The authentication system includes comprehensive tests:

**Unit Tests**:
- User model creation and validation
- Password hashing and verification
- Email normalization
- Serializer validation

**Integration Tests**:
- Registration endpoint
- Login endpoint
- Token refresh endpoint
- Logout endpoint
- Protected endpoint access
- Password change endpoint

**Acceptance Tests**:
- Valid credential authentication
- Invalid credential handling
- Token-based resource access
- Token expiration handling

## Configuration

### Environment Variables

```env
# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Security
SECRET_KEY=your-secret-key-here
```

### Django Settings

See `config/settings/base.py` for:
- `AUTH_USER_MODEL`: Set to `'users.User'`
- `SIMPLE_JWT`: JWT configuration
- `REST_FRAMEWORK`: DRF authentication classes
- `PASSWORD_VALIDATORS`: Password strength requirements

## Troubleshooting

### Common Issues

**Issue**: 401 Unauthorized on all requests
- **Solution**: Verify token is included in Authorization header with 'Bearer ' prefix

**Issue**: Token expired
- **Solution**: Implement token refresh logic on client side

**Issue**: Cannot login after logout
- **Solution**: Ensure refresh token is blacklisted and client clears all tokens

**Issue**: Email already exists error
- **Solution**: Email must be unique, user may need to use password reset flow

### Debug Mode

Enable detailed error messages in development:

```python
# settings/development.py
DEBUG = True
REST_FRAMEWORK['EXCEPTION_HANDLER'] = None  # Show full stack traces
```

## Best Practices

1. **Always use HTTPS in production**
2. **Implement token refresh before expiration**
3. **Clear tokens on logout client-side**
4. **Never expose tokens in URLs or logs**
5. **Rotate refresh tokens on each use**
6. **Use httpOnly cookies when possible**
7. **Implement rate limiting**
8. **Monitor failed authentication attempts**
9. **Regularly audit security settings**
10. **Keep dependencies updated**

## Future Enhancements

Potential improvements for future iterations:

- Email verification on registration
- Password reset via email
- Two-factor authentication (2FA)
- OAuth2 integration (Google, GitHub, etc.)
- Session management dashboard
- Failed login attempt tracking
- Account lockout after multiple failures
- Password history to prevent reuse
- Security event logging
- Admin dashboard for user management
