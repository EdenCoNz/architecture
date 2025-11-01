# API Contract: Basic Login Functionality

## Overview
This API contract defines the endpoints for basic login functionality that allows users to authenticate using only their name and email address, without password authentication. This provides a low-friction entry point for users while maintaining user identification capabilities.

**Feature ID**: 20
**Contract Version**: 1.0
**Date Created**: 2025-11-02
**Related User Stories**: 20.1, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8, 20.9

## Design Principles

This API contract follows these key principles:
- **Simplicity**: Only name and email required for login
- **Consistency**: Follows existing Django REST Framework patterns in the codebase
- **Security**: Input sanitization, rate limiting, and session management
- **Extensibility**: Designed to work alongside existing JWT-based authentication
- **Developer-Friendly**: Clear validation rules and comprehensive error messages

## Assumptions and Constraints

### Assumptions
1. Users can log in with just name and email (no password verification)
2. Email addresses are unique and serve as the primary user identifier
3. Returning users can update their name by logging in with the same email
4. Sessions persist across browser sessions and page refreshes
5. The system uses JWT tokens for session management (consistent with existing auth)

### Constraints
1. Must follow existing Django REST Framework patterns
2. Must use existing User model structure
3. Must sanitize inputs to prevent XSS attacks (consistent with existing serializers)
4. Must implement rate limiting to prevent abuse
5. Response format must match existing API conventions

## Authentication Flow

```
┌─────────┐                    ┌─────────┐                    ┌──────────┐
│ Frontend│                    │ Backend │                    │ Database │
└────┬────┘                    └────┬────┘                    └────┬─────┘
     │                              │                              │
     │ POST /api/v1/auth/basic/     │                              │
     │ { name, email }              │                              │
     ├─────────────────────────────>│                              │
     │                              │                              │
     │                              │ Check if email exists        │
     │                              ├─────────────────────────────>│
     │                              │                              │
     │                              │ Create or update user        │
     │                              │<─────────────────────────────┤
     │                              │                              │
     │                              │ Generate JWT tokens          │
     │                              │                              │
     │ { user, access, refresh }    │                              │
     │<─────────────────────────────┤                              │
     │                              │                              │
     │ Store tokens in localStorage │                              │
     │                              │                              │
```

---

## Endpoints

### 1. Basic Login

**Method:** POST
**Path:** `/api/v1/auth/basic/`
**Description:** Authenticate or register a user using only their name and email address. If the email exists, the user's name is updated. If the email is new, a new user account is created.

**Authentication:** Not required (AllowAny)
**Rate Limiting:** 10 requests per minute per IP address

#### Request

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```typescript
interface BasicLoginRequest {
  name: string;      // User's full name (required, max 255 chars)
  email: string;     // User's email address (required, valid email format)
}
```

**Validation Rules:**
- `name`: Required, non-empty string, max length 255 characters, HTML/script tags sanitized
- `email`: Required, valid email format (RFC 5322), max length 254 characters, case-insensitive

**Example Request:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com"
}
```

#### Response

**Success (200 OK)** - Existing user logged in:
```typescript
interface BasicLoginSuccessResponse {
  message: string;           // Success message
  user: {
    id: number;              // User's database ID
    email: string;           // User's email address
    first_name: string;      // User's first name (extracted from name)
    last_name: string;       // User's last name (extracted from name)
    is_active: boolean;      // Account active status
    date_joined: string;     // ISO 8601 datetime of account creation
  };
  access: string;            // JWT access token (valid for 15 minutes)
  refresh: string;           // JWT refresh token (valid for 7 days)
  is_new_user: boolean;      // false for existing users
}
```

**Success (201 Created)** - New user created and logged in:
```typescript
interface BasicLoginCreatedResponse {
  message: string;           // Success message
  user: {
    id: number;              // User's database ID
    email: string;           // User's email address
    first_name: string;      // User's first name (extracted from name)
    last_name: string;       // User's last name (extracted from name)
    is_active: boolean;      // Account active status (always true)
    date_joined: string;     // ISO 8601 datetime of account creation
  };
  access: string;            // JWT access token (valid for 15 minutes)
  refresh: string;           // JWT refresh token (valid for 7 days)
  is_new_user: boolean;      // true for new users
}
```

**Example Success Response (200 OK):**
```json
{
  "message": "Login successful.",
  "user": {
    "id": 42,
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "date_joined": "2025-10-15T14:30:00Z"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk4MzM2MDAwLCJpYXQiOjE2OTgzMzUxMDAsImp0aSI6ImFiYzEyMyIsInVzZXJfaWQiOjQyfQ.xyz789",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5ODk0MDcwMCwiaWF0IjoxNjk4MzM1MTAwLCJqdGkiOiJkZWY0NTYiLCJ1c2VyX2lkIjo0Mn0.abc123",
  "is_new_user": false
}
```

**Example Success Response (201 Created):**
```json
{
  "message": "Account created successfully.",
  "user": {
    "id": 43,
    "email": "jane.smith@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "is_active": true,
    "date_joined": "2025-11-02T10:30:00Z"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk4MzM2MDAwLCJpYXQiOjE2OTgzMzUxMDAsImp0aSI6ImFiYzEyMyIsInVzZXJfaWQiOjQzfQ.xyz789",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5ODk0MDcwMCwiaWF0IjoxNjk4MzM1MTAwLCJqdGkiOiJkZWY0NTYiLCJ1c2VyX2lkIjo0M30.abc123",
  "is_new_user": true
}
```

#### Validation Rules

**Name Validation:**
- Required field
- Must not be empty or whitespace only
- Maximum length: 255 characters
- HTML tags and script content are stripped (XSS prevention)
- Special characters and numbers are allowed
- Name is split on first space to populate first_name and last_name
  - If no space: first_name = full name, last_name = empty string
  - If space(s): first_name = first word, last_name = remaining words

**Email Validation:**
- Required field
- Must be valid email format (RFC 5322)
- Maximum length: 254 characters
- Converted to lowercase for storage and comparison
- Must be unique (enforced at database level)

#### Error Responses

**400 Bad Request** - Validation errors:
```typescript
interface ValidationErrorResponse {
  [field: string]: string[];  // Field-specific error messages
}
```

**Example - Missing required fields:**
```json
{
  "name": ["This field is required."],
  "email": ["This field is required."]
}
```

**Example - Invalid email format:**
```json
{
  "email": ["Enter a valid email address."]
}
```

**Example - Name too long:**
```json
{
  "name": ["Ensure this field has no more than 255 characters."]
}
```

**Example - Empty name:**
```json
{
  "name": ["This field may not be blank."]
}
```

**403 Forbidden** - Inactive account (rare case):
```json
{
  "error": "This account has been deactivated. Please contact support."
}
```

**429 Too Many Requests** - Rate limit exceeded:
```json
{
  "error": "Too many login attempts. Please try again later."
}
```

**500 Internal Server Error** - Server error:
```json
{
  "error": "An unexpected error occurred. Please try again later."
}
```

**503 Service Unavailable** - Service temporarily unavailable:
```json
{
  "error": "Service temporarily unavailable. Please try again later."
}
```

---

### 2. Get Current User

**Method:** GET
**Path:** `/api/v1/auth/me/`
**Description:** Retrieve the currently authenticated user's profile information.

**Authentication:** Required (JWT access token)
**Rate Limiting:** None (already authenticated)

#### Request

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:** None (GET request)

#### Response

**Success (200 OK):**
```typescript
interface CurrentUserResponse {
  id: number;              // User's database ID
  email: string;           // User's email address
  first_name: string;      // User's first name
  last_name: string;       // User's last name
  is_active: boolean;      // Account active status
  date_joined: string;     // ISO 8601 datetime of account creation
}
```

**Example Response:**
```json
{
  "id": 42,
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "date_joined": "2025-10-15T14:30:00Z"
}
```

#### Error Responses

**401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

---

### 3. Refresh Access Token

**Method:** POST
**Path:** `/api/v1/auth/token/refresh/`
**Description:** Obtain a new access token using a valid refresh token. This allows maintaining user sessions without requiring re-authentication.

**Authentication:** Not required (uses refresh token)
**Rate Limiting:** None (token-based)

**Note:** This endpoint already exists in the codebase. It is documented here for completeness of the login flow.

#### Request

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```typescript
interface TokenRefreshRequest {
  refresh: string;  // Valid refresh token from login response
}
```

**Example Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5ODk0MDcwMCwiaWF0IjoxNjk4MzM1MTAwLCJqdGkiOiJkZWY0NTYiLCJ1c2VyX2lkIjo0Mn0.abc123"
}
```

#### Response

**Success (200 OK):**
```typescript
interface TokenRefreshResponse {
  access: string;   // New JWT access token (valid for 15 minutes)
  refresh: string;  // New refresh token (if rotation is enabled)
}
```

**Example Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk4MzM2OTAwLCJpYXQiOjE2OTgzMzYwMDAsImp0aSI6ImdoaTc4OSIsInVzZXJfaWQiOjQyfQ.new789",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5ODk0MTYwMCwiaWF0IjoxNjk4MzM2MDAwLCJqdGkiOiJqa2w5MTIiLCJ1c2VyX2lkIjo0Mn0.new123"
}
```

#### Error Responses

**401 Unauthorized** - Invalid or expired refresh token:
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

---

### 4. Logout

**Method:** POST
**Path:** `/api/v1/auth/logout/`
**Description:** Logout the current user by blacklisting their refresh token, preventing it from being used to obtain new access tokens.

**Authentication:** Required (JWT access token)
**Rate Limiting:** None

**Note:** This endpoint already exists in the codebase. It is documented here for completeness of the login flow.

#### Request

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```typescript
interface LogoutRequest {
  refresh: string;  // The refresh token to blacklist
}
```

**Example Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5ODk0MDcwMCwiaWF0IjoxNjk4MzM1MTAwLCJqdGkiOiJkZWY0NTYiLCJ1c2VyX2lkIjo0Mn0.abc123"
}
```

#### Response

**Success (200 OK):**
```typescript
interface LogoutResponse {
  message: string;  // Success message
}
```

**Example Response:**
```json
{
  "message": "Logout successful."
}
```

#### Error Responses

**400 Bad Request** - Missing or invalid refresh token:
```json
{
  "error": "Refresh token is required."
}
```

```json
{
  "error": "Invalid token or token already blacklisted."
}
```

**401 Unauthorized** - Authentication required:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Shared Types and Constants

### TypeScript Type Definitions

```typescript
// ============================================================================
// Request Types
// ============================================================================

/**
 * Request payload for basic login/registration
 */
export interface BasicLoginRequest {
  /** User's full name (first and last name) */
  name: string;
  /** User's email address (unique identifier) */
  email: string;
}

/**
 * Request payload for token refresh
 */
export interface TokenRefreshRequest {
  /** Valid refresh token from login response */
  refresh: string;
}

/**
 * Request payload for logout
 */
export interface LogoutRequest {
  /** Refresh token to blacklist */
  refresh: string;
}

// ============================================================================
// Response Types
// ============================================================================

/**
 * User profile information
 */
export interface UserProfile {
  /** User's database ID */
  id: number;
  /** User's email address */
  email: string;
  /** User's first name */
  first_name: string;
  /** User's last name */
  last_name: string;
  /** Whether the account is active */
  is_active: boolean;
  /** ISO 8601 datetime when the account was created */
  date_joined: string;
}

/**
 * JWT token pair returned from authentication
 */
export interface JWTTokens {
  /** Access token (valid for 15 minutes) */
  access: string;
  /** Refresh token (valid for 7 days) */
  refresh: string;
}

/**
 * Response from successful basic login (existing user)
 */
export interface BasicLoginSuccessResponse {
  /** Success message */
  message: string;
  /** User profile information */
  user: UserProfile;
  /** JWT access token */
  access: string;
  /** JWT refresh token */
  refresh: string;
  /** Indicates if this is a new user */
  is_new_user: boolean;
}

/**
 * Response from successful basic login (new user)
 */
export interface BasicLoginCreatedResponse {
  /** Success message */
  message: string;
  /** User profile information */
  user: UserProfile;
  /** JWT access token */
  access: string;
  /** JWT refresh token */
  refresh: string;
  /** Indicates if this is a new user */
  is_new_user: boolean;
}

/**
 * Union type for basic login responses
 */
export type BasicLoginResponse = BasicLoginSuccessResponse | BasicLoginCreatedResponse;

/**
 * Response from token refresh
 */
export interface TokenRefreshResponse {
  /** New access token */
  access: string;
  /** New refresh token (if rotation enabled) */
  refresh: string;
}

/**
 * Response from successful logout
 */
export interface LogoutResponse {
  /** Success message */
  message: string;
}

/**
 * Response from get current user endpoint
 */
export type CurrentUserResponse = UserProfile;

// ============================================================================
// Error Types
// ============================================================================

/**
 * Validation error response with field-specific errors
 */
export interface ValidationErrorResponse {
  /** Field name mapped to array of error messages */
  [field: string]: string[];
}

/**
 * Generic error response
 */
export interface ErrorResponse {
  /** Error message */
  error: string;
  /** Optional error details */
  details?: string;
}

/**
 * JWT token error response
 */
export interface TokenErrorResponse {
  /** Error description */
  detail: string;
  /** Error code */
  code: string;
  /** Additional error messages */
  messages?: Array<{
    token_class: string;
    token_type: string;
    message: string;
  }>;
}

// ============================================================================
// Enums and Constants
// ============================================================================

/**
 * HTTP status codes used in the API
 */
export enum HttpStatus {
  OK = 200,
  CREATED = 201,
  BAD_REQUEST = 400,
  UNAUTHORIZED = 401,
  FORBIDDEN = 403,
  NOT_FOUND = 404,
  TOO_MANY_REQUESTS = 429,
  INTERNAL_SERVER_ERROR = 500,
  SERVICE_UNAVAILABLE = 503,
}

/**
 * API endpoints
 */
export const API_ENDPOINTS = {
  BASIC_LOGIN: '/api/v1/auth/basic/',
  CURRENT_USER: '/api/v1/auth/me/',
  TOKEN_REFRESH: '/api/v1/auth/token/refresh/',
  LOGOUT: '/api/v1/auth/logout/',
} as const;

/**
 * Token expiration times
 */
export const TOKEN_EXPIRY = {
  ACCESS_TOKEN_MINUTES: 15,
  REFRESH_TOKEN_DAYS: 7,
} as const;

/**
 * Field validation constraints
 */
export const VALIDATION_CONSTRAINTS = {
  NAME_MAX_LENGTH: 255,
  EMAIL_MAX_LENGTH: 254,
} as const;

/**
 * Rate limits
 */
export const RATE_LIMITS = {
  BASIC_LOGIN_PER_MINUTE: 10,
} as const;
```

---

## Integration Notes

### Authentication Flow

1. **Initial Login:**
   - User submits name and email via POST to `/api/v1/auth/basic/`
   - Backend creates or retrieves user account
   - Backend generates JWT tokens and returns them with user profile
   - Frontend stores tokens in localStorage

2. **Maintaining Session:**
   - Frontend includes access token in Authorization header for authenticated requests
   - When access token expires (15 minutes), frontend uses refresh token to get new access token
   - Refresh token is valid for 7 days

3. **Session Persistence:**
   - Tokens stored in localStorage persist across browser sessions
   - On app load, frontend checks for valid tokens
   - If access token expired but refresh token valid, refresh automatically
   - If both tokens expired/invalid, redirect to login

4. **Logout:**
   - User initiates logout
   - Frontend sends refresh token to `/api/v1/auth/logout/`
   - Backend blacklists the refresh token
   - Frontend clears tokens from localStorage

### Security Considerations

1. **Rate Limiting:**
   - Basic login endpoint limited to 10 requests per minute per IP
   - Prevents brute force attempts and abuse

2. **Input Sanitization:**
   - Name field sanitized to remove HTML/script tags (XSS prevention)
   - Email normalized to lowercase for consistency

3. **Token Security:**
   - Access tokens short-lived (15 minutes) to limit exposure
   - Refresh tokens can be blacklisted on logout
   - JWT tokens signed and verified server-side

4. **HTTPS Required:**
   - All API endpoints must be accessed over HTTPS in production
   - Tokens transmitted securely

### Frontend Implementation Guidelines

**Token Storage:**
```typescript
// Store tokens after successful login
const storeTokens = (access: string, refresh: string) => {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
};

// Retrieve tokens
const getAccessToken = (): string | null => {
  return localStorage.getItem('access_token');
};

const getRefreshToken = (): string | null => {
  return localStorage.getItem('refresh_token');
};

// Clear tokens on logout
const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};
```

**Making Authenticated Requests:**
```typescript
// Add Authorization header to requests
const makeAuthenticatedRequest = async (url: string, options: RequestInit = {}) => {
  const accessToken = getAccessToken();

  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  };

  return fetch(url, { ...options, headers });
};
```

**Token Refresh Logic:**
```typescript
// Refresh access token when it expires
const refreshAccessToken = async (): Promise<boolean> => {
  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    return false;
  }

  try {
    const response = await fetch(API_ENDPOINTS.TOKEN_REFRESH, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (response.ok) {
      const data: TokenRefreshResponse = await response.json();
      storeTokens(data.access, data.refresh);
      return true;
    }

    // Refresh token invalid/expired - redirect to login
    clearTokens();
    return false;
  } catch (error) {
    console.error('Token refresh failed:', error);
    return false;
  }
};
```

**Handling 401 Errors:**
```typescript
// Axios interceptor example
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshed = await refreshAccessToken();
      if (refreshed) {
        // Retry original request with new token
        const accessToken = getAccessToken();
        originalRequest.headers['Authorization'] = `Bearer ${accessToken}`;
        return axios(originalRequest);
      }

      // Refresh failed - redirect to login
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);
```

### Backend Implementation Guidelines

**Name Parsing:**
```python
def parse_name(full_name: str) -> tuple[str, str]:
    """
    Split full name into first and last name.

    Args:
        full_name: User's full name

    Returns:
        Tuple of (first_name, last_name)
    """
    full_name = full_name.strip()
    parts = full_name.split(' ', 1)

    if len(parts) == 1:
        return parts[0], ''

    return parts[0], parts[1]
```

**User Creation/Update Logic:**
```python
def basic_login(name: str, email: str) -> tuple[User, bool]:
    """
    Create or update user for basic login.

    Args:
        name: User's full name
        email: User's email address

    Returns:
        Tuple of (user, is_new_user)
    """
    email = email.lower()
    first_name, last_name = parse_name(name)

    # Sanitize name fields
    first_name = sanitize_html_input(first_name)
    last_name = sanitize_html_input(last_name)

    # Check if user exists
    try:
        user = User.objects.get(email=email)
        # Update name if changed
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        is_new_user = False
    except User.DoesNotExist:
        # Create new user without password
        user = User.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )
        is_new_user = True

    return user, is_new_user
```

**Rate Limiting:**
```python
@method_decorator(
    ratelimit(key='ip', rate='10/m', method='POST'),
    name='dispatch'
)
class BasicLoginView(APIView):
    permission_classes = [AllowAny]
    # ... implementation
```

**Error Handling:**
```python
# Handle inactive accounts
if not user.is_active:
    return Response(
        {"error": "This account has been deactivated. Please contact support."},
        status=status.HTTP_403_FORBIDDEN
    )

# Handle rate limit (django-ratelimit)
# Automatically returns 429 when rate limit exceeded
```

---

## Testing Considerations

### Frontend Testing

**Test Cases:**
1. Successful login with new user (201 Created)
2. Successful login with existing user (200 OK)
3. Validation error - missing name
4. Validation error - missing email
5. Validation error - invalid email format
6. Rate limit error (429)
7. Network error handling
8. Token storage after successful login
9. Token refresh on 401 error
10. Redirect to login when refresh fails

**Mock Responses:**
```typescript
// Mock successful login (new user)
const mockLoginNewUser: BasicLoginCreatedResponse = {
  message: "Account created successfully.",
  user: {
    id: 1,
    email: "test@example.com",
    first_name: "Test",
    last_name: "User",
    is_active: true,
    date_joined: "2025-11-02T10:00:00Z"
  },
  access: "mock.access.token",
  refresh: "mock.refresh.token",
  is_new_user: true
};

// Mock validation error
const mockValidationError: ValidationErrorResponse = {
  email: ["Enter a valid email address."]
};
```

### Backend Testing

**Test Cases:**
1. Create new user with valid name and email
2. Update existing user's name
3. Reject empty name
4. Reject empty email
5. Reject invalid email format
6. Sanitize HTML tags in name
7. Generate JWT tokens on success
8. Return 201 for new users
9. Return 200 for existing users
10. Enforce rate limiting
11. Handle inactive accounts (403)
12. Email case-insensitivity (test@example.com = TEST@EXAMPLE.COM)

**Test Example:**
```python
def test_basic_login_new_user(self):
    """Test basic login creates new user and returns tokens."""
    response = self.client.post(
        '/api/v1/auth/basic/',
        data={'name': 'John Doe', 'email': 'john@example.com'},
        format='json'
    )

    self.assertEqual(response.status_code, 201)
    self.assertEqual(response.data['message'], 'Account created successfully.')
    self.assertEqual(response.data['user']['email'], 'john@example.com')
    self.assertEqual(response.data['user']['first_name'], 'John')
    self.assertEqual(response.data['user']['last_name'], 'Doe')
    self.assertTrue(response.data['is_new_user'])
    self.assertIn('access', response.data)
    self.assertIn('refresh', response.data)
```

---

## Migration from Password-Based Login

This basic login API is designed to work alongside the existing password-based authentication system. The two systems can coexist:

1. **Separate Endpoints:**
   - Basic login: `/api/v1/auth/basic/`
   - Password login: `/api/v1/auth/login/`

2. **Shared User Model:**
   - Both systems use the same User model
   - Users created via basic login have no password set
   - These users can later set a password to enable password-based login

3. **Compatible Token System:**
   - Both systems use JWT tokens with same structure
   - Frontend token handling logic works for both
   - Token refresh and logout endpoints are shared

---

## Summary

### Endpoints Defined
1. **POST /api/v1/auth/basic/** - Basic login/registration (NEW)
2. **GET /api/v1/auth/me/** - Get current user (EXISTING)
3. **POST /api/v1/auth/token/refresh/** - Refresh access token (EXISTING)
4. **POST /api/v1/auth/logout/** - Logout (EXISTING)

### Key Features
- **Passwordless authentication** using only name and email
- **Automatic user creation** for new email addresses
- **Name updates** for returning users
- **JWT token-based sessions** compatible with existing auth
- **Rate limiting** to prevent abuse
- **Input sanitization** for security
- **Comprehensive error handling** with clear messages
- **Session persistence** across browser sessions

### Implementation Checklist

**Backend:**
- [ ] Create BasicLoginSerializer with name and email fields
- [ ] Implement name parsing and sanitization logic
- [ ] Create BasicLoginView with create-or-update user logic
- [ ] Add rate limiting to BasicLoginView
- [ ] Add URL route for /api/v1/auth/basic/
- [ ] Write comprehensive tests for all scenarios
- [ ] Update API documentation (drf-spectacular)

**Frontend:**
- [ ] Create BasicLoginForm component
- [ ] Implement token storage in localStorage
- [ ] Implement API client for basic login endpoint
- [ ] Add token refresh logic for 401 errors
- [ ] Add loading states during submission
- [ ] Display validation errors from API
- [ ] Handle success (redirect to app)
- [ ] Handle network errors gracefully
- [ ] Write component tests with mocked API
- [ ] Write integration tests with real API

### Next Steps
1. **Backend implementation** (Story 20.6) can begin using this contract
2. **Frontend implementation** (Stories 20.3, 20.4, 20.5) can begin using this contract
3. Both teams can work **in parallel** without coordination
4. Integration testing should verify contract compliance on both sides

---

**Contract Status:** ✅ Complete and ready for implementation
**Last Updated:** 2025-11-02
**Version:** 1.0
