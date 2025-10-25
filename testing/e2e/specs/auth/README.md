# Authentication E2E Tests

## Overview

This directory contains end-to-end tests for user authentication workflows including login, logout, registration, and session management.

## Test Files

### `login.spec.ts` (Story 13.3)

Tests for the user login workflow.

**Test Suites:**
1. **Form Field Validation** - Verifies all required form fields are present and accessible
2. **Valid Credentials Login** - Tests successful authentication and redirect
3. **Invalid Credentials Handling** - Tests error handling for failed login attempts
4. **Session Establishment** - Verifies JWT tokens and session state
5. **Security and Edge Cases** - Tests security features and error handling
6. **Visual Consistency** - Visual regression tests for login UI

**Acceptance Criteria Covered:**
- ✅ AC1: Valid credentials redirect to dashboard
- ✅ AC2: Invalid credentials show error message
- ✅ AC3: All required form fields present (email, password, submit)
- ✅ AC4: Successful login establishes user session

**Key Features Tested:**
- Form field presence and validation
- Email and password input types
- Accessible labels and ARIA attributes
- Keyboard navigation (Tab key, Enter key submission)
- Successful login with redirect to dashboard
- Error messages for invalid credentials
- Empty form validation
- JWT token storage in localStorage
- User data storage
- Session persistence after page refresh
- Access token usage in API requests
- Password obscuring (type="password")
- Network error handling
- Loading state (button disabled during submission)
- Visual regression testing

**Running Tests:**

```bash
# Run all login tests
npm run test:e2e:login

# Run with visible browser (debugging)
npm run test:e2e:login -- --headed

# Run specific test
npm run test:e2e -- -g "should redirect to dashboard with valid credentials"

# Debug mode (step-by-step)
npm run test:e2e:login -- --debug

# Run on specific browser
npm run test:e2e:login -- --project=chromium
npm run test:e2e:login -- --project=firefox
npm run test:e2e:login -- --project=webkit
```

## Test Data

Tests use fixtures from `testing/fixtures/auth.ts`:

```typescript
TEST_USERS = {
  validUser: {
    email: 'test@example.com',
    password: 'TestPassword123!',
  },
  invalidUser: {
    email: 'invalid@example.com',
    password: 'WrongPassword123!',
  },
}
```

## Page Objects

Tests use the `LoginPage` page object model from `testing/e2e/page-objects/LoginPage.ts` which provides:

- Element locators (email, password, submit button, error messages)
- Interaction methods (fillEmail, fillPassword, clickSubmit, login)
- Validation methods (hasAllRequiredFields, hasErrorMessage)
- Navigation helpers (goto, waitForSuccessfulLogin)
- Accessibility checks (checkAccessibility)

## Test Structure

```typescript
test.describe('Test Suite Name', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    // Setup: Create page object, clear auth, register user
    loginPage = new LoginPage(page);
    await clearAuth(page);
    await registerUser(page, ...);
    await loginPage.goto();
  });

  test('test name', async ({ page }) => {
    // Test implementation
  });
});
```

## Dependencies

- `@playwright/test` - Test framework
- `LoginPage` - Page object model
- `auth.ts` - Test fixtures and helpers

## Integration with CI/CD

These tests are designed to run in CI/CD pipelines:

- Headless mode by default
- Retry on failure (2 retries in CI)
- Screenshot capture on failure
- Video recording on failure
- HTML and JSON reports generated
- JUnit XML for CI/CD integration

### `logout.spec.ts` (Story 13.4)

Tests for the user logout workflow.

**Test Suites:**
1. **User Logout Redirect** - Verifies redirect to login after logout
2. **Session Termination** - Verifies session and tokens are cleared
3. **Protected Route Access** - Verifies logged-out users cannot access protected pages
4. **API Logout** - Tests logout via API endpoints

**Running Tests:**
```bash
npm run test:e2e:logout
```

### `session-persistence.spec.ts` (Story 13.5)

Tests for session persistence across refreshes, browser restarts, and token lifecycle.

**Test Suites:**
1. **Page Refresh Persistence** - Session maintains after page refresh
2. **Browser Restart Simulation** - Session persists across browser restart (within token lifetime)
3. **Session Expiration** - Tokens expire correctly per configuration (15min access, 7 day refresh)
4. **Remember Me Long-term Persistence** - Refresh tokens enable 7-day sessions
5. **Session Security and Edge Cases** - Token tampering, logout, security measures

**Acceptance Criteria Covered:**
- ✅ AC1: Page refresh maintains authentication
- ✅ AC2: Browser restart maintains session
- ✅ AC3: Inactive sessions expire as expected
- ✅ AC4: "Remember me" persists beyond typical timeout

**Key Features Tested:**
- Single and multiple page refresh persistence
- Navigation between pages maintains session
- Browser context restart with storage state
- Access token expiration (15 minutes)
- Refresh token expiration (7 days)
- Token refresh and rotation
- Blacklisted token rejection
- Long-term session with multiple refreshes
- Session security (tampering, logout)

**Running Tests:**
```bash
# Run all session persistence tests
npm run test:e2e:session

# Run specific test suite
npm run test:e2e:session -- -g "Page Refresh"
npm run test:e2e:session -- -g "Browser Restart"
npm run test:e2e:session -- -g "Session Expiration"
npm run test:e2e:session -- -g "Remember Me"

# Debug mode
npm run test:e2e:session -- --debug
```

See [SESSION_PERSISTENCE.md](./SESSION_PERSISTENCE.md) for detailed documentation.

## Future Tests (Planned)

- `registration.spec.ts` - User registration workflow
- `password-reset.spec.ts` - Password reset workflow

## Best Practices

1. **Use Page Objects** - All UI interactions through page objects
2. **Test Isolation** - Each test is independent, clears state before running
3. **Realistic Test Data** - Use realistic user credentials and scenarios
4. **Accessibility First** - Tests verify WCAG compliance
5. **Visual Testing** - Screenshot comparisons for UI consistency
6. **Security Focused** - Tests verify password obscuring, token security
7. **Error Scenarios** - Tests cover both happy path and error cases

## Troubleshooting

### Tests Fail on Login Page Not Found

If login page (`/login`) doesn't exist yet:
- Tests are written to be implementation-ready
- Create login page UI matching the expected selectors
- Or update LoginPage.ts locators to match actual implementation

### Authentication Tokens Not Stored

Verify:
- Backend API returns `access` and `refresh` tokens
- Frontend stores tokens in localStorage
- Check browser console for errors

### Network Errors

Ensure test environment is running:
```bash
docker compose -f compose.yml -f compose.test.yml up -d
```

### Visual Regression Failures

Update baselines if UI intentionally changed:
```bash
npm run test:e2e:login -- --update-snapshots
```
