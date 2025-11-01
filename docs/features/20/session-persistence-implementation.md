# Session Persistence Implementation (Story 20.8)

## Overview

This document describes how login session persistence is implemented for Feature 20 (Basic Login Functionality). The implementation uses JWT (JSON Web Tokens) to maintain user sessions across page refreshes, browser sessions, and navigation.

## Implementation Details

### JWT Token-Based Sessions

The application uses **JWT tokens** for stateless session management with the following characteristics:

1. **Access Token**: Short-lived token for API authentication
   - **Lifetime**: 15 minutes
   - **Purpose**: Authenticates API requests
   - **Storage**: Frontend localStorage
   - **Format**: `Bearer <access_token>` in Authorization header

2. **Refresh Token**: Long-lived token for obtaining new access tokens
   - **Lifetime**: 7 days
   - **Purpose**: Obtain new access tokens without re-authentication
   - **Storage**: Frontend localStorage
   - **Security**: Blacklisted on logout and rotation

### Configuration

All JWT settings are configured in `/backend/config/settings/base.py`:

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,           # Generate new refresh token on each refresh
    "BLACKLIST_AFTER_ROTATION": True,        # Blacklist old refresh token
    "UPDATE_LAST_LOGIN": True,               # Track user activity
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
}
```

### Session Persistence Behavior

#### 1. Page Refresh Persistence

**Acceptance Criteria**: Given I successfully log in, when I refresh the page, then I should remain logged in.

**Implementation**:
- Access and refresh tokens are stored in browser's `localStorage`
- On page load, frontend checks for valid access token
- If access token exists and is valid, user remains authenticated
- If access token expired but refresh token valid, frontend automatically refreshes
- **Backend**: No action required; tokens are stateless

**Flow**:
```
Page Refresh → Check localStorage → Access token valid? → Use it
                                  ↓
                          Access token expired?
                                  ↓
                     Refresh token valid? → Refresh tokens → Use new access token
                                  ↓
                          All tokens invalid → Redirect to login
```

#### 2. Browser Session Persistence

**Acceptance Criteria**: Given I successfully log in, when I close and reopen the browser, then I should remain logged in.

**Implementation**:
- `localStorage` persists across browser sessions (unlike `sessionStorage`)
- Refresh token remains valid for 7 days after last use
- Frontend checks for tokens on app initialization
- **Backend**: Validates refresh token and issues new access token

**Flow**:
```
Browser Reopened → Check localStorage → Tokens exist?
                                       ↓
                           Refresh token valid? → Refresh tokens → Authenticated
                                       ↓
                              Invalid/Expired → Redirect to login
```

#### 3. Navigation Persistence

**Acceptance Criteria**: Given I'm logged in, when I navigate to different pages, then my session should persist.

**Implementation**:
- Access token included in Authorization header for all authenticated API requests
- Single-Page Application (SPA) keeps tokens in memory and localStorage
- No backend session required; JWT is stateless
- **Backend**: Validates JWT on each request via `JWTAuthentication`

**Flow**:
```
Navigation → API Request → Include Authorization: Bearer <token>
                        ↓
                Backend validates token → Request processed
```

#### 4. Inactivity Handling

**Acceptance Criteria**: Given I've been inactive for an extended period, when I return, then I should either remain logged in or be prompted to log in again with clear messaging.

**Implementation**:

**Short Inactivity (<15 minutes)**:
- Access token still valid → User remains logged in
- No action required

**Medium Inactivity (15 minutes - 7 days)**:
- Access token expired → Frontend automatically refreshes using refresh token
- User remains logged in seamlessly (transparent token refresh)
- New tokens issued with extended expiration

**Extended Inactivity (>7 days)**:
- Both tokens expired → User must log in again
- Frontend detects expired refresh token (401 response)
- User redirected to login with message: "Your session has expired. Please log in again."

**Flow**:
```
User Returns → Access token expired? → Use refresh token
                                    ↓
                      Refresh token expired? → Redirect to login
                                             → Show "Session expired" message
```

## API Endpoints

### 1. Login (Get Tokens)
```
POST /api/v1/auth/basic/
Request: { "name": "John Doe", "email": "john@example.com" }
Response: {
  "access": "eyJ0eXAi...",
  "refresh": "eyJ0eXAi...",
  "user": {...},
  "is_new_user": false
}
```

### 2. Refresh Access Token
```
POST /api/v1/auth/token/refresh/
Request: { "refresh": "eyJ0eXAi..." }
Response: {
  "access": "eyJ0eXAi...",
  "refresh": "eyJ0eXAi..."  # New refresh token (rotation enabled)
}
```

### 3. Get Current User (Verify Session)
```
GET /api/v1/auth/me/
Headers: Authorization: Bearer <access_token>
Response: {
  "id": 1,
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "date_joined": "2025-11-02T10:00:00Z"
}
```

### 4. Logout (Invalidate Session)
```
POST /api/v1/auth/logout/
Headers: Authorization: Bearer <access_token>
Request: { "refresh": "eyJ0eXAi..." }
Response: { "message": "Logout successful." }
```

## Security Features

### 1. Token Rotation
- **Enabled**: `ROTATE_REFRESH_TOKENS = True`
- **Behavior**: Each token refresh generates a new refresh token
- **Benefit**: Limits damage if refresh token is compromised

### 2. Token Blacklisting
- **Enabled**: `BLACKLIST_AFTER_ROTATION = True`
- **Behavior**: Old refresh tokens are blacklisted after rotation
- **Benefit**: Prevents replay attacks with old tokens
- **Implementation**: Uses `rest_framework_simplejwt.token_blacklist` app

### 3. Token Expiration
- **Access Token**: 15 minutes (short-lived for security)
- **Refresh Token**: 7 days (balance between security and UX)
- **Benefit**: Limits exposure window for compromised tokens

### 4. Inactive Account Handling
- **Check**: Performed on every login and token refresh
- **Behavior**: Returns 403 Forbidden for inactive accounts
- **Message**: "This account has been deactivated. Please contact support."

### 5. HTTPS Enforcement
- **Production**: All tokens transmitted over HTTPS only
- **Configuration**: `SECURE_SSL_REDIRECT = True` in production
- **Benefit**: Prevents token interception

## Frontend Integration Guidelines

### Token Storage
```typescript
// Store tokens after login
localStorage.setItem('access_token', response.data.access);
localStorage.setItem('refresh_token', response.data.refresh);

// Retrieve tokens
const accessToken = localStorage.getItem('access_token');
const refreshToken = localStorage.getItem('refresh_token');

// Clear tokens on logout
localStorage.removeItem('access_token');
localStorage.removeItem('refresh_token');
```

### Making Authenticated Requests
```typescript
// Add Authorization header
const response = await fetch('/api/v1/auth/me/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  },
});
```

### Automatic Token Refresh
```typescript
// Axios interceptor example
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post('/api/v1/auth/token/refresh/', {
          refresh: refreshToken,
        });

        const { access, refresh } = response.data;
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);

        // Retry original request with new token
        originalRequest.headers['Authorization'] = `Bearer ${access}`;
        return axios(originalRequest);
      } catch (refreshError) {
        // Refresh failed - redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);
```

### Session Initialization
```typescript
// On app load
const initializeSession = async () => {
  const accessToken = localStorage.getItem('access_token');
  const refreshToken = localStorage.getItem('refresh_token');

  if (!accessToken || !refreshToken) {
    // No tokens - redirect to login
    return null;
  }

  try {
    // Try to get current user (validates access token)
    const response = await fetch('/api/v1/auth/me/', {
      headers: { 'Authorization': `Bearer ${accessToken}` },
    });

    if (response.ok) {
      return await response.json();
    }

    // Access token expired - try to refresh
    const refreshResponse = await fetch('/api/v1/auth/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (refreshResponse.ok) {
      const { access, refresh } = await refreshResponse.json();
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);

      // Retry getting current user
      const userResponse = await fetch('/api/v1/auth/me/', {
        headers: { 'Authorization': `Bearer ${access}` },
      });

      return await userResponse.json();
    }

    // Refresh failed - clear tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    return null;
  } catch (error) {
    console.error('Session initialization failed:', error);
    return null;
  }
};
```

## Testing

### Test Coverage

Session persistence is tested in `/backend/apps/users/test_session_persistence.py`:

1. **test_session_persists_across_requests**: Verifies tokens work for multiple requests
2. **test_session_persists_with_valid_access_token**: Verifies page refresh persistence
3. **test_session_persists_across_browser_sessions_with_refresh_token**: Verifies browser close/reopen
4. **test_expired_access_token_can_be_refreshed**: Verifies inactivity <7 days
5. **test_expired_refresh_token_requires_relogin**: Verifies inactivity >7 days
6. **test_token_refresh_rotates_tokens**: Verifies token rotation security
7. **test_blacklisted_token_cannot_be_reused**: Verifies token blacklisting
8. **test_logout_blacklists_refresh_token**: Verifies logout invalidation
9. **test_inactive_user_cannot_authenticate**: Verifies inactive account handling
10. **test_token_lifetime_configuration**: Verifies JWT configuration
11. **test_multiple_concurrent_sessions**: Verifies multi-device support

### Running Tests

```bash
# Run all session persistence tests
python manage.py test apps.users.test_session_persistence

# Run specific test
python manage.py test apps.users.test_session_persistence.SessionPersistenceTests.test_session_persists_across_browser_sessions_with_refresh_token

# Run with coverage
coverage run --source='apps.users' manage.py test apps.users.test_session_persistence
coverage report
```

## Environment Variables

No additional environment variables are required for session persistence. The JWT configuration uses these existing variables:

- `SECRET_KEY`: Used to sign JWT tokens (required)
- `CORS_ALLOWED_ORIGINS`: Frontend origins allowed to access API (required)
- `CSRF_TRUSTED_ORIGINS`: Trusted origins for CSRF (required)

## Monitoring and Logging

### Token Operations Logged

The application logs these token-related events:

1. **Login**: User authentication and token generation
2. **Token Refresh**: Refresh token usage and rotation
3. **Logout**: Token blacklisting
4. **Failed Authentication**: Invalid or expired tokens
5. **Inactive Account Access**: Attempts to use deactivated accounts

### Log Locations

- **General logs**: `/backend/logs/general.log`
- **Error logs**: `/backend/logs/errors.log`
- **Request logs**: `/backend/logs/requests.log`

### Example Log Entries

```json
{
  "timestamp": "2025-11-02T10:30:00Z",
  "level": "INFO",
  "logger": "apps.users",
  "message": "User authenticated successfully",
  "user_id": 42,
  "email": "john@example.com",
  "is_new_user": false
}
```

```json
{
  "timestamp": "2025-11-02T10:45:00Z",
  "level": "INFO",
  "logger": "apps.users",
  "message": "Token refreshed successfully",
  "user_id": 42
}
```

```json
{
  "timestamp": "2025-11-02T11:00:00Z",
  "level": "WARNING",
  "logger": "apps.users",
  "message": "Inactive account login attempt",
  "user_id": 42,
  "email": "john@example.com"
}
```

## Troubleshooting

### Common Issues

#### 1. Session Lost After Page Refresh

**Symptom**: User logged out after refreshing page
**Possible Causes**:
- Tokens not stored in localStorage
- Frontend checking sessionStorage instead
- CORS issues preventing token storage

**Solution**:
- Verify tokens are stored in localStorage (not sessionStorage)
- Check browser console for CORS errors
- Verify `CORS_ALLOWED_ORIGINS` includes frontend domain

#### 2. "Token is invalid or expired" Error

**Symptom**: 401 error when using access token
**Possible Causes**:
- Access token expired (>15 minutes old)
- System clock mismatch between client and server
- Token corrupted during storage/retrieval

**Solution**:
- Implement automatic token refresh on 401
- Verify system clocks are synchronized
- Check token is stored/retrieved correctly

#### 3. Refresh Token Always Fails

**Symptom**: Refresh endpoint returns 401
**Possible Causes**:
- Refresh token expired (>7 days)
- Refresh token was blacklisted
- Token was manually invalidated

**Solution**:
- Check refresh token expiration
- Verify token hasn't been blacklisted
- User must log in again if token is invalid

#### 4. Multiple Device Sessions Conflict

**Symptom**: Logging in on one device logs out another
**Possible Causes**:
- Frontend clearing all tokens on login
- Backend configured to limit concurrent sessions

**Solution**:
- JWT tokens support multiple concurrent sessions by default
- Ensure frontend doesn't clear tokens unnecessarily
- Each device should maintain its own token pair

## Security Considerations

### Best Practices

1. **Always Use HTTPS in Production**
   - Prevents token interception
   - Enforced via `SECURE_SSL_REDIRECT = True`

2. **Store Tokens Securely**
   - Use localStorage (not cookies) to avoid CSRF
   - Never expose tokens in URLs or logs

3. **Implement Token Refresh**
   - Automatically refresh expired access tokens
   - Improves UX while maintaining security

4. **Handle Token Expiration Gracefully**
   - Show clear messaging when session expires
   - Redirect to login smoothly

5. **Validate Tokens on Every Request**
   - Backend validates signature and expiration
   - Check user account status (is_active)

### Attack Mitigation

1. **XSS Protection**
   - Name fields sanitized to prevent script injection
   - Tokens in localStorage not accessible via XSS (same-origin policy)

2. **Token Replay Attacks**
   - Refresh token rotation prevents reuse
   - Old tokens blacklisted after rotation

3. **Token Theft**
   - Short access token lifetime (15 min) limits exposure
   - HTTPS prevents man-in-the-middle attacks

4. **Brute Force Attacks**
   - Rate limiting on login endpoint (10 req/min)
   - Account lockout via is_active flag

## Compliance and Standards

### JWT Standards

- **RFC 7519**: JSON Web Token standard
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Claims**: Standard claims (exp, iat, jti, user_id)

### API Standards

- **RESTful**: Following REST principles
- **OpenAPI 3.0**: Documented via drf-spectacular
- **HTTP Status Codes**: Standard codes for all responses

## Related Documentation

- **API Contract**: `/docs/features/20/api-contract.md`
- **User Stories**: `/docs/features/20/user-stories.md`
- **Configuration**: `/docs/context/devops/configuration.md`
- **Django Settings**: `/backend/config/settings/base.py`

## Version History

| Version | Date       | Changes                                      |
|---------|------------|----------------------------------------------|
| 1.0     | 2025-11-02 | Initial implementation with JWT token-based  |
|         |            | session persistence                          |

## Support

For issues or questions regarding session persistence:

1. Check the troubleshooting section above
2. Review test cases in `test_session_persistence.py`
3. Check application logs for error details
4. Consult API contract for expected behavior
