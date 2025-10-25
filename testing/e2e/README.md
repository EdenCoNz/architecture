# End-to-End Tests (E2E)

## Overview

End-to-end tests validate complete user workflows from the browser perspective. These tests run against the full application stack (frontend + backend + database) and simulate real user interactions.

## Framework

- **Playwright** - Modern E2E testing framework with cross-browser support
- **@playwright/test** - Test runner with built-in assertions
- **@axe-core/playwright** - Accessibility testing integration

## Test Organization

```
e2e/
├── specs/
│   ├── auth/
│   │   ├── login.spec.ts
│   │   ├── logout.spec.ts
│   │   └── session.spec.ts
│   ├── onboarding/
│   │   ├── form-completion.spec.ts
│   │   └── form-validation.spec.ts
│   ├── assessment/
│   │   ├── submission.spec.ts
│   │   └── profile-creation.spec.ts
│   └── navigation/
│       └── app-navigation.spec.ts
├── fixtures/
│   ├── auth.ts
│   └── users.ts
├── page-objects/
│   ├── LoginPage.ts
│   ├── OnboardingPage.ts
│   └── DashboardPage.ts
├── playwright.config.ts
└── README.md
```

## Running E2E Tests

**All E2E tests:**
```bash
./testing/run-tests.sh --suite e2e
```

**Specific test file:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
    npx playwright test e2e/specs/auth/login.spec.ts
```

**Headed mode (visible browser):**
```bash
./testing/run-tests.sh --suite e2e --headed
```

**Debug mode (step-by-step):**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
    npx playwright test --debug e2e/specs/auth/login.spec.ts
```

**UI mode (interactive):**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
    npx playwright test --ui
```

## Writing E2E Tests

### Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('User Login Flow', () => {
  test('should login with valid credentials', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');

    // Fill in credentials
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');

    // Submit form
    await page.click('button[type="submit"]');

    // Verify redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toContainText('Dashboard');
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('[name="email"]', 'invalid@example.com');
    await page.fill('[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // Verify error message
    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page).toHaveURL('/login'); // Should stay on login page
  });
});
```

### Using Page Objects

```typescript
// page-objects/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.page.fill('[name="email"]', email);
    await this.page.fill('[name="password"]', password);
    await this.page.click('button[type="submit"]');
  }

  async getErrorMessage() {
    return this.page.locator('.error-message').textContent();
  }
}

// Usage in test
test('should login successfully', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('test@example.com', 'password123');
  await expect(page).toHaveURL('/dashboard');
});
```

### Using Fixtures

```typescript
// fixtures/auth.ts
import { test as base } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';

export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    // Login before each test
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('test@example.com', 'password123');
    await use(page);
  },
});

// Usage in test
import { test } from '../fixtures/auth';

test('should access dashboard when authenticated', async ({ authenticatedPage }) => {
  await expect(authenticatedPage).toHaveURL('/dashboard');
});
```

## Best Practices

### Locator Strategies

1. **Use data-testid attributes (preferred):**
   ```typescript
   await page.click('[data-testid="submit-button"]');
   ```

2. **Use semantic roles:**
   ```typescript
   await page.click('button:has-text("Submit")');
   await page.click('role=button[name="Submit"]');
   ```

3. **Avoid brittle selectors:**
   ```typescript
   // ❌ Bad - brittle
   await page.click('.btn.btn-primary.btn-lg');

   // ✅ Good - semantic
   await page.click('[data-testid="submit-button"]');
   ```

### Waiting Strategies

1. **Auto-waiting (preferred):**
   ```typescript
   // Playwright auto-waits for element to be visible and enabled
   await page.click('button');
   ```

2. **Explicit waits when needed:**
   ```typescript
   await page.waitForSelector('[data-testid="results"]');
   await page.waitForLoadState('networkidle');
   ```

3. **Avoid fixed timeouts:**
   ```typescript
   // ❌ Bad
   await page.waitForTimeout(5000);

   // ✅ Good
   await page.waitForSelector('[data-testid="loaded"]');
   ```

### Assertions

1. **Use Playwright assertions:**
   ```typescript
   await expect(page).toHaveURL('/dashboard');
   await expect(page.locator('h1')).toContainText('Welcome');
   await expect(page.locator('button')).toBeEnabled();
   ```

2. **Soft assertions for multiple checks:**
   ```typescript
   await expect.soft(page.locator('.title')).toBeVisible();
   await expect.soft(page.locator('.subtitle')).toBeVisible();
   await expect.soft(page.locator('.content')).toBeVisible();
   ```

## Debugging

### Screenshots on Failure

Screenshots are automatically captured on test failure and saved to `testing/reports/screenshots/`.

**Force screenshot:**
```typescript
await page.screenshot({ path: 'testing/reports/screenshots/debug.png' });
```

### Video Recording

Videos are automatically recorded for failed tests and saved to `testing/reports/videos/`.

### Trace Viewer

**Enable tracing:**
```typescript
await context.tracing.start({ screenshots: true, snapshots: true });
// ... test actions ...
await context.tracing.stop({ path: 'testing/reports/trace.zip' });
```

**View trace:**
```bash
npx playwright show-trace testing/reports/trace.zip
```

### Debug Mode

**Interactive debugging:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
    npx playwright test --debug
```

This opens Playwright Inspector for step-by-step debugging.

## Common Patterns

### Login Flow
See future test implementation in Story 13.3

### Form Validation
See future test implementation in Story 13.6

### Session Persistence
See future test implementation in Story 13.5

## Test Data

Test users and data are created via fixtures in `testing/fixtures/`. Tests should:

1. Use existing fixtures when possible
2. Create minimal test data needed for the test
3. Clean up data after test (if not using transactional database)

## CI/CD Integration

E2E tests run in CI/CD with:

- Headless mode enabled
- Video recording on failure
- Screenshot capture on failure
- Trace recording on failure
- HTML report generation

See `.github/workflows/` for CI/CD configuration (Story 13.12).
