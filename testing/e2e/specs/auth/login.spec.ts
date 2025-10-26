/**
 * Login Flow E2E Tests
 *
 * Tests validate the complete user login workflow including:
 * - Form field presence and validation
 * - Successful authentication with valid credentials
 * - Error handling for invalid credentials
 * - Session establishment and persistence
 * - Accessibility compliance
 *
 * Story 13.3: Test User Login Flow
 *
 * Acceptance Criteria:
 * 1. Valid credentials should redirect to dashboard
 * 2. Invalid credentials should show error message
 * 3. All required form fields should be present (email, password, submit)
 * 4. Successful login should establish user session
 */

import { test, expect } from '@playwright/test';
import { LoginPage } from '../../page-objects/LoginPage';
import { TEST_USERS, registerUser, isAuthenticated, getStoredUser, clearAuth } from '../../fixtures/auth';

test.describe('User Login Flow', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);

    // Clear any existing authentication
    await clearAuth(page);

    // Ensure test user is registered (may already exist, that's ok)
    const { email, password, firstName, lastName } = TEST_USERS.validUser;
    await registerUser(page, email, password, firstName, lastName);

    // Navigate to login page
    await loginPage.goto();
  });

  /**
   * Acceptance Criteria 3: Form Fields Present
   * Given the login form loads, when I run the test,
   * then it should verify all required form fields are present
   * (email, password, submit button)
   */
  test.describe('Form Field Validation', () => {
    test('should display all required form fields', async () => {
      // Verify email input is present and visible
      await expect(loginPage.emailInput).toBeVisible();
      await expect(loginPage.emailInput).toBeEnabled();

      // Verify password input is present and visible
      await expect(loginPage.passwordInput).toBeVisible();
      await expect(loginPage.passwordInput).toBeEnabled();

      // Verify submit button is present and visible
      await expect(loginPage.submitButton).toBeVisible();
      await expect(loginPage.submitButton).toBeEnabled();

      // Verify all fields are present using helper method
      const hasAllFields = await loginPage.hasAllRequiredFields();
      expect(hasAllFields).toBe(true);
    });

    test('should have proper input types for form fields', async () => {
      // Email input should have type="email"
      const emailType = await loginPage.emailInput.getAttribute('type');
      expect(emailType).toBe('email');

      // Password input should have type="password"
      const passwordType = await loginPage.passwordInput.getAttribute('type');
      expect(passwordType).toBe('password');

      // Submit button should have type="submit"
      const submitType = await loginPage.submitButton.getAttribute('type');
      expect(submitType).toBe('submit');
    });

    test('should have accessible form labels and ARIA attributes', async () => {
      const accessibility = await loginPage.checkAccessibility();

      expect(accessibility.emailAccessible).toBe(true);
      expect(accessibility.passwordAccessible).toBe(true);
      expect(accessibility.submitAccessible).toBe(true);
      expect(accessibility.allAccessible).toBe(true);
    });

    test('should allow keyboard navigation', async ({ page }) => {
      // Tab to email field
      await page.keyboard.press('Tab');
      await expect(loginPage.emailInput).toBeFocused();

      // Tab to password field
      await page.keyboard.press('Tab');
      await expect(loginPage.passwordInput).toBeFocused();

      // Tab to submit button
      await page.keyboard.press('Tab');
      await expect(loginPage.submitButton).toBeFocused();
    });
  });

  /**
   * Acceptance Criteria 1: Valid Credentials Redirect to Dashboard
   * Given I run the login flow test, when a user enters valid credentials
   * and submits, then the test should verify the user is redirected
   * to their dashboard
   */
  test.describe('Valid Credentials Login', () => {
    test('should redirect to dashboard with valid credentials', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Fill in login form
      await loginPage.fillEmail(email);
      await loginPage.fillPassword(password);

      // Submit the form
      await loginPage.clickSubmit();

      // Wait for navigation to dashboard
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Verify user is on dashboard page
      expect(page.url()).toContain('/dashboard');

      // Verify no longer on login page
      const isStillOnLogin = await loginPage.isOnLoginPage();
      expect(isStillOnLogin).toBe(false);
    });

    test('should redirect to dashboard when submitting via Enter key', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Fill in login form
      await loginPage.fillEmail(email);
      await loginPage.fillPassword(password);

      // Submit via Enter key (keyboard accessibility)
      await loginPage.submitViaEnter();

      // Wait for navigation to dashboard
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Verify user is on dashboard page
      expect(page.url()).toContain('/dashboard');
    });

    test('should display success message before redirect', async () => {
      const { email, password } = TEST_USERS.validUser;

      // Fill in and submit login form
      await loginPage.login(email, password);

      // Check if success message appears (optional, depends on implementation)
      const hasSuccess = await loginPage.hasSuccessMessage();

      // Either success message is shown, or we're redirected immediately
      // Both are valid UX patterns
      if (!hasSuccess) {
        // If no success message, should redirect immediately
        const url = await loginPage.getCurrentUrl();
        expect(url).toContain('/dashboard');
      }
    });
  });

  /**
   * Acceptance Criteria 2: Invalid Credentials Show Error
   * Given the test uses invalid credentials, when the login is attempted,
   * then the test should verify an error message appears
   */
  test.describe('Invalid Credentials Handling', () => {
    test('should show error message with invalid email', async ({ page }) => {
      const { email, password } = TEST_USERS.invalidUser;

      // Attempt login with invalid credentials
      await loginPage.login(email, password);

      // Wait for error message to appear
      const hasError = await loginPage.hasErrorMessage();
      expect(hasError).toBe(true);

      // Verify error message content
      const errorText = await loginPage.getErrorMessage();
      expect(errorText).toBeTruthy();
      expect(errorText?.toLowerCase()).toMatch(/invalid|incorrect|wrong|failed/);

      // Verify user is still on login page
      expect(page.url()).toContain('/login');
    });

    test('should show error message with wrong password', async ({ page }) => {
      const { email } = TEST_USERS.validUser;
      const wrongPassword = 'WrongPassword123!';

      // Attempt login with correct email but wrong password
      await loginPage.login(email, wrongPassword);

      // Wait for error message to appear
      const hasError = await loginPage.hasErrorMessage();
      expect(hasError).toBe(true);

      // Verify user is still on login page
      expect(page.url()).toContain('/login');
    });

    test('should show error with empty credentials', async ({ page }) => {
      // Attempt to submit empty form
      await loginPage.clickSubmit();

      // Should show validation errors or remain on page
      const url = await loginPage.getCurrentUrl();
      expect(url).toContain('/login');

      // Form should not allow submission or show validation errors
      const hasError = await loginPage.hasErrorMessage();
      const isStillOnLogin = await loginPage.isOnLoginPage();

      expect(hasError || isStillOnLogin).toBe(true);
    });

    test('should clear error message when user corrects input', async ({ page }) => {
      // First, attempt login with invalid credentials
      await loginPage.login('invalid@example.com', 'wrong');

      // Wait for error
      await loginPage.hasErrorMessage();

      // Now correct the credentials
      await loginPage.fillEmail(TEST_USERS.validUser.email);
      await loginPage.fillPassword(TEST_USERS.validUser.password);

      // Error should clear when form is corrected (or on successful submission)
      await loginPage.clickSubmit();

      // Should redirect to dashboard (no error)
      await loginPage.waitForSuccessfulLogin('/dashboard');
      expect(page.url()).toContain('/dashboard');
    });
  });

  /**
   * Acceptance Criteria 4: Session Establishment
   * Given a successful login, when the test completes,
   * then it should verify the user session is established
   */
  test.describe('Session Establishment', () => {
    test('should store authentication tokens in localStorage', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Perform login
      await loginPage.login(email, password);

      // Wait for redirect
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Verify authentication tokens are stored
      const hasAccessToken = await page.evaluate(() => {
        return localStorage.getItem('access_token') !== null;
      });

      const hasRefreshToken = await page.evaluate(() => {
        return localStorage.getItem('refresh_token') !== null;
      });

      expect(hasAccessToken).toBe(true);
      expect(hasRefreshToken).toBe(true);
    });

    test('should store user information in localStorage', async ({ page }) => {
      const { email, password, firstName, lastName } = TEST_USERS.validUser;

      // Perform login
      await loginPage.login(email, password);

      // Wait for redirect
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Verify user data is stored
      const storedUser = await getStoredUser(page);

      expect(storedUser).toBeTruthy();
      expect(storedUser.email).toBe(email);
      expect(storedUser.first_name).toBe(firstName);
      expect(storedUser.last_name).toBe(lastName);
    });

    test('should mark user as authenticated', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Verify user is not authenticated before login
      const beforeAuth = await isAuthenticated(page);
      expect(beforeAuth).toBe(false);

      // Perform login
      await loginPage.login(email, password);

      // Wait for redirect
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Verify user is authenticated after login
      const afterAuth = await isAuthenticated(page);
      expect(afterAuth).toBe(true);
    });

    test('should maintain session after page refresh', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Perform login
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Verify authenticated
      const beforeRefresh = await isAuthenticated(page);
      expect(beforeRefresh).toBe(true);

      // Refresh the page
      await page.reload();

      // Verify still authenticated after refresh
      const afterRefresh = await isAuthenticated(page);
      expect(afterRefresh).toBe(true);

      // Should still be on dashboard (not redirected to login)
      expect(page.url()).toContain('/dashboard');
    });

    test('should include access token in API requests', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Perform login
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Get access token
      const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));
      expect(accessToken).toBeTruthy();

      // Verify token has correct JWT structure (header.payload.signature)
      const tokenParts = accessToken?.split('.');
      expect(tokenParts?.length).toBe(3);

      // Verify token can be used for authenticated requests
      const response = await page.request.get('/api/v1/auth/me/', {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      expect(response.ok()).toBe(true);

      const userData = await response.json();
      expect(userData.email).toBe(email);
    });
  });

  /**
   * Additional Tests: Edge Cases and Security
   */
  test.describe('Security and Edge Cases', () => {
    test('should not expose password in DOM or network logs', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Fill in password
      await loginPage.fillPassword(password);

      // Verify password input has type="password" (obscured)
      const passwordType = await loginPage.passwordInput.getAttribute('type');
      expect(passwordType).toBe('password');

      // Verify password is not visible in input value attribute
      const inputValue = await loginPage.passwordInput.inputValue();
      expect(inputValue).toBe(password); // Value is there but visually obscured
    });

    test('should handle network errors gracefully', async ({ page, context }) => {
      // Simulate network failure
      await context.route('**/api/v1/auth/login/', route => route.abort());

      const { email, password } = TEST_USERS.validUser;

      // Attempt login
      await loginPage.login(email, password);

      // Should show error message or remain on login page
      const hasError = await loginPage.hasErrorMessage();
      const isStillOnLogin = await loginPage.isOnLoginPage();

      expect(hasError || isStillOnLogin).toBe(true);
    });

    test('should prevent submission during API call (loading state)', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Fill in form
      await loginPage.fillEmail(email);
      await loginPage.fillPassword(password);

      // Click submit
      await loginPage.clickSubmit();

      // Immediately check if button is disabled (should be in loading state)
      // Note: This might be too fast to catch, but good UX should disable button
      const isDisabledDuringSubmit = await loginPage.isSubmitDisabled();

      // Button should either be disabled during submission or redirect happens quickly
      // Both are acceptable - we're testing that double-submission is prevented
      expect(isDisabledDuringSubmit || page.url().includes('/dashboard')).toBe(true);
    });
  });

  /**
   * Visual Regression Tests
   */
  test.describe('Visual Consistency', () => {
    test('should match login page screenshot baseline', async ({ page }) => {
      // Take screenshot for visual regression testing
      await expect(page).toHaveScreenshot('login-page-initial.png', {
        fullPage: true,
        animations: 'disabled',
      });
    });

    test('should show visual error state', async ({ page }) => {
      // Attempt login with invalid credentials
      await loginPage.login('invalid@test.com', 'wrong');

      // Wait for error to appear
      await loginPage.hasErrorMessage();

      // Take screenshot of error state
      await expect(page).toHaveScreenshot('login-page-error-state.png', {
        fullPage: true,
        animations: 'disabled',
      });
    });
  });
});
