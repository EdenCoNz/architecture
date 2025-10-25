# Session Persistence Testing

## Overview

This document describes the automated E2E tests for session persistence functionality (Story 13.5). These tests validate that user sessions remain active across page refreshes, browser restarts, and throughout the token lifecycle.

## Test Coverage

### 1. Page Refresh Persistence

**Purpose**: Validate that authentication state persists across page refreshes.

**Test Cases**:
- Single page refresh maintains authentication
- Multiple consecutive page refreshes maintain authentication
- Authentication persists when navigating between pages
- Session preserved across hard navigation (full page reload)

**Key Validations**:
- Access and refresh tokens remain in localStorage
- User data persists across refreshes
- User stays on protected pages (not redirected to login)
- Authenticated API calls continue to work

### 2. Browser Restart Simulation

**Purpose**: Validate that sessions persist when the browser is closed and reopened (within token lifetime).

**Test Cases**:
- Session persists after browser context restart (manual storage state save/restore)
- Session persists using Playwright's storageState API
- Missing storage state correctly redirects to login

**Key Validations**:
- Tokens restore correctly in new browser context
- User can access protected resources immediately
- Refresh token remains valid after browser restart
- Authentication state fully restores

### 3. Session Expiration

**Purpose**: Validate that sessions expire correctly according to token lifetime configuration.

**Test Cases**:
- Access token expiration time is correctly set (15 minutes per backend config)
- Token refresh works before access token expiration
- Blacklisted refresh tokens are rejected
- Expired/missing tokens result in unauthenticated state

**Key Validations**:
- Access token lifetime: 15 minutes
- Refresh token lifetime: 7 days
- Token refresh generates new tokens
- Old refresh tokens are invalidated after refresh
- Invalid tokens return 401 Unauthorized

### 4. "Remember Me" Long-term Persistence

**Purpose**: Validate that refresh tokens enable long-term session persistence (7 days).

**Test Cases**:
- Refresh token has significantly longer lifetime than access token
- Multiple token refreshes maintain session (simulating 7-day usage)
- Session persists across browser restart within refresh token lifetime
- Users can manually extend session before expiration

**Key Validations**:
- Refresh token expiration is approximately 7 days from issue
- Token rotation works correctly (new refresh token on each refresh)
- Session can be extended multiple times within 7-day window
- Each refresh provides new access + refresh tokens

### 5. Security and Edge Cases

**Purpose**: Validate security measures and edge case handling.

**Test Cases**:
- Session does not persist after explicit logout
- Tampered tokens are rejected
- Missing tokens handled gracefully
- Session fixation attacks prevented

**Key Validations**:
- Logout blacklists refresh token
- Modified tokens return 401 Unauthorized
- Protected pages redirect to login when unauthenticated
- Login overwrites any pre-existing tokens

## Technical Implementation

### Token Structure

Tokens are JWT (JSON Web Tokens) with the following structure:
```
header.payload.signature
```

The payload includes:
- `exp`: Expiration timestamp (Unix time)
- `user_id`: User identifier
- `token_type`: "access" or "refresh"

### Token Storage

Tokens are stored in browser localStorage:
- `access_token`: Short-lived access token (15 minutes)
- `refresh_token`: Long-lived refresh token (7 days)
- `user`: User profile data (JSON string)

### Token Lifecycle

```
Login
  ↓
Issue: access (15min) + refresh (7 days)
  ↓
Access token expires (15 min)
  ↓
Client refreshes using refresh token
  ↓
New access token issued
New refresh token issued (rotated)
Old refresh token blacklisted
  ↓
Repeat until refresh token expires (7 days)
  ↓
User must re-authenticate
```

## Test Utilities

### Helper Functions

Located in `/testing/fixtures/auth.ts`:

**Session State**:
- `isAuthenticated(page)`: Check if user has valid access token
- `getStoredUser(page)`: Retrieve stored user profile data
- `getStoredTokens(page)`: Get both access and refresh tokens
- `clearAuth(page)`: Clear all authentication data

**Token Management**:
- `getTokenExpiration(page, tokenKey)`: Get token expiration timestamp
- `isTokenExpired(page, tokenKey)`: Check if token is expired
- `refreshTokens(page)`: Refresh access token using refresh token
- `verifyTokenValidity(page)`: Test token by making authenticated API call

**Authentication**:
- `registerUser(page, email, password, firstName, lastName)`: Create test user
- `loginViaAPI(page, email, password)`: Login and store tokens
- `logoutViaAPI(page, refreshToken)`: Logout and blacklist refresh token

### Test-Specific Helpers

Located in the test spec file:

**Storage State**:
- `saveStorageState(page)`: Save localStorage and cookies
- `restoreStorageState(page, state)`: Restore localStorage and cookies

**Token Analysis**:
- `getTokenExpirationTime(page, tokenKey)`: Extract expiration from JWT
- `isAccessTokenExpired(page)`: Check if access token is expired

## Running the Tests

### Run All Session Persistence Tests
```bash
cd testing
npm run test:e2e -- session-persistence.spec.ts
```

### Run Specific Test Suites
```bash
# Page refresh tests only
npm run test:e2e -- session-persistence.spec.ts -g "Page Refresh"

# Browser restart tests only
npm run test:e2e -- session-persistence.spec.ts -g "Browser Restart"

# Session expiration tests only
npm run test:e2e -- session-persistence.spec.ts -g "Session Expiration"

# Remember me tests only
npm run test:e2e -- session-persistence.spec.ts -g "Remember Me"
```

### Run in Different Browsers
```bash
# Chromium
npm run test:e2e -- session-persistence.spec.ts --project=chromium

# Firefox
npm run test:e2e -- session-persistence.spec.ts --project=firefox

# WebKit (Safari)
npm run test:e2e -- session-persistence.spec.ts --project=webkit

# All browsers
npm run test:e2e -- session-persistence.spec.ts
```

### Debug Mode
```bash
# Run with Playwright inspector
npm run test:e2e -- session-persistence.spec.ts --debug

# Run headed (see browser)
npm run test:e2e -- session-persistence.spec.ts --headed
```

## Expected Behavior

### Successful Scenarios

1. **Page Refresh**: User remains logged in, stays on current page
2. **Browser Restart**: User can resume session within 7 days
3. **Token Refresh**: New tokens issued before access token expires
4. **Long Session**: User can maintain session for up to 7 days with activity

### Failure Scenarios

1. **Expired Access Token**: 401 Unauthorized, client should refresh
2. **Expired Refresh Token**: User must re-authenticate
3. **Invalid Token**: 401 Unauthorized, clear storage and redirect to login
4. **Tampered Token**: 401 Unauthorized, signature verification fails
5. **Logged Out**: Session cleared, refresh token blacklisted

## Configuration

### Backend Configuration

Token lifetimes are configured in backend settings:
```python
# config/settings/base.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### Test Configuration

Test environment is configured in:
- `/testing/e2e/playwright.config.ts`: Playwright settings
- `/testing/.env.test`: Test environment variables

## Troubleshooting

### Tests Failing

**Token expiration checks failing**:
- Ensure backend is using correct token lifetime configuration
- Verify system clocks are synchronized
- Check token payload in browser DevTools

**Browser restart tests failing**:
- Ensure temp directory `/tmp` is writable
- Check Playwright version compatibility
- Verify storage state is being saved correctly

**Token refresh failing**:
- Verify backend refresh endpoint is working
- Check that old refresh tokens are being blacklisted
- Ensure token rotation is enabled in backend

### Common Issues

**Issue**: Tests pass locally but fail in CI
- **Solution**: Ensure test database is properly initialized, check token lifetimes

**Issue**: Intermittent failures on browser restart tests
- **Solution**: Add explicit waits for storage state operations, increase timeouts

**Issue**: Token expiration tests are flaky
- **Solution**: Use backend test utilities to manipulate token timestamps instead of relying on real-time delays

## Acceptance Criteria Mapping

| Criterion | Test Coverage |
|-----------|---------------|
| AC1: Page refresh maintains authentication | ✅ Page Refresh Persistence suite (4 tests) |
| AC2: Browser restart maintains session | ✅ Browser Restart Simulation suite (3 tests) |
| AC3: Inactive sessions expire correctly | ✅ Session Expiration suite (4 tests) |
| AC4: "Remember me" enables long-term persistence | ✅ Remember Me Long-term Persistence suite (4 tests) |

**Total Tests**: 19 test cases covering all acceptance criteria

## Future Enhancements

Potential improvements for future iterations:

1. **Backend Time Manipulation**: Add backend test utilities to manipulate token timestamps for more reliable expiration testing
2. **Session Monitoring**: Add tests for session activity monitoring and automatic refresh
3. **Multi-Device Testing**: Test session behavior across multiple devices/contexts
4. **Token Revocation**: Test admin-initiated token revocation scenarios
5. **Concurrent Session Limits**: Test enforcement of maximum concurrent sessions per user
6. **Session Analytics**: Test session tracking and analytics functionality

## Related Documentation

- [Backend Authentication Documentation](/backend/docs/AUTHENTICATION.md)
- [Login Flow Tests](./login.spec.ts)
- [Logout Flow Tests](./logout.spec.ts)
- [Test Fixtures](../../fixtures/auth.ts)
- [Playwright Configuration](../../playwright.config.ts)
