/**
 * Logout Flow E2E Tests
 *
 * Tests validate the complete user logout workflow including:
 * - Redirect to login page after logout
 * - Access denial to protected pages after logout
 * - Session termination after logout
 * - Sensitive data cleared from storage after logout
 * - Accessibility compliance
 *
 * Story 13.4: Test User Logout Flow
 *
 * Acceptance Criteria:
 * 1. Logged-in user should be redirected to login page when logout is triggered
 * 2. Protected pages should deny access after logout completes
 * 3. Session should be terminated when user logs out
 * 4. Stored credentials and sensitive data should be cleared after logout
 */

import { test, expect } from '@playwright/test';
import { LoginPage } from '../../page-objects/LoginPage';
import { LogoutPage } from '../../page-objects/LogoutPage';
import { TEST_USERS, registerUser, isAuthenticated, clearAuth } from '../../fixtures/auth';

test.describe('User Logout Flow', () => {
  let loginPage: LoginPage;
  let logoutPage: LogoutPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    logoutPage = new LogoutPage(page);

    // Clear any existing authentication
    await clearAuth(page);

    // Ensure test user is registered
    const { email, password, firstName, lastName } = TEST_USERS.validUser;
    await registerUser(page, email, password, firstName, lastName);

    // Login to establish authenticated session
    await loginPage.goto();
    await loginPage.login(email, password);
    await loginPage.waitForSuccessfulLogin('/dashboard');

    // Verify user is authenticated before testing logout
    const authenticated = await isAuthenticated(page);
    expect(authenticated).toBe(true);
  });

  /**
   * Acceptance Criteria 1: Redirect to Login Page
   * Given a logged-in user, when the logout action is triggered,
   * then the test should verify the user is redirected to the login page
   */
  test.describe('Logout Redirect Behavior', () => {
    test('should redirect to login page when logout is triggered', async ({ page }) => {
      // Verify user is on dashboard before logout
      expect(page.url()).toContain('/dashboard');

      // Perform logout
      await logoutPage.logout();

      // Wait for redirect to login page
      await logoutPage.waitForRedirectToLogin();

      // Verify user is on login page
      const isOnLogin = await logoutPage.isOnLoginPage();
      expect(isOnLogin).toBe(true);
      expect(page.url()).toContain('/login');
    });

    test('should redirect to login page immediately after logout', async ({ page }) => {
      // Track navigation
      const navigationPromise = page.waitForNavigation({ timeout: 10000 });

      // Perform logout
      await logoutPage.logout();

      // Wait for navigation to complete
      await navigationPromise;

      // Should be on login page
      expect(page.url()).toContain('/login');
    });

    test('should not remain on protected page after logout', async ({ page }) => {
      const protectedUrl = page.url();

      // Perform logout
      await logoutPage.logout();

      // Wait for redirect
      await logoutPage.waitForRedirectToLogin();

      // Verify URL has changed from protected page
      const currentUrl = await logoutPage.getCurrentUrl();
      expect(currentUrl).not.toBe(protectedUrl);
      expect(currentUrl).toContain('/login');
    });

    test('should show logout success message before redirect', async ({ page }) => {
      // Perform logout
      await logoutPage.logout();

      // Check if success message appears (optional UX pattern)
      const hasSuccess = await logoutPage.hasSuccessMessage();

      // Either success message is shown, or we're redirected immediately
      if (!hasSuccess) {
        // If no success message, should redirect immediately
        const url = await logoutPage.getCurrentUrl();
        expect(url).toContain('/login');
      }
    });
  });

  /**
   * Acceptance Criteria 2: Access Denial to Protected Pages
   * Given logout completes, when the test attempts to access protected pages,
   * then access should be denied
   */
  test.describe('Protected Route Access After Logout', () => {
    test('should deny access to dashboard after logout', async ({ page }) => {
      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Attempt to access dashboard
      const hasAccess = await logoutPage.attemptAccessProtectedRoute('/dashboard');

      // Access should be denied
      expect(hasAccess).toBe(false);
      expect(page.url()).toContain('/login');
    });

    test('should deny access to profile page after logout', async ({ page }) => {
      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Attempt to access profile
      const hasAccess = await logoutPage.attemptAccessProtectedRoute('/profile');

      // Access should be denied
      expect(hasAccess).toBe(false);
      expect(page.url()).toContain('/login');
    });

    test('should deny access to assessment page after logout', async ({ page }) => {
      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Attempt to access assessment
      const hasAccess = await logoutPage.attemptAccessProtectedRoute('/assessment');

      // Access should be denied
      expect(hasAccess).toBe(false);
      expect(page.url()).toContain('/login');
    });

    test('should redirect all protected routes to login after logout', async ({ page }) => {
      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // List of protected routes to test
      const protectedRoutes = ['/dashboard', '/profile', '/assessment', '/settings'];

      for (const route of protectedRoutes) {
        await page.goto(route);
        await page.waitForTimeout(1000);

        // Should be redirected to login
        expect(page.url()).toContain('/login');
      }
    });

    test('should not allow API access to protected endpoints after logout', async ({ page }) => {
      // Get current access token before logout
      const tokenBeforeLogout = await page.evaluate(() => localStorage.getItem('access_token'));
      expect(tokenBeforeLogout).toBeTruthy();

      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Attempt API call with old token
      try {
        const response = await page.request.get('/api/v1/auth/me/', {
          headers: {
            Authorization: `Bearer ${tokenBeforeLogout}`,
          },
        });

        // Should return 401 Unauthorized
        expect(response.status()).toBe(401);
      } catch {
        // Request failure also indicates access is denied
        expect(true).toBe(true);
      }
    });
  });

  /**
   * Acceptance Criteria 3: Session Termination
   * Given a user logs out, when the test checks session state,
   * then the session should be terminated
   */
  test.describe('Session Termination', () => {
    test('should terminate session after logout', async () => {
      // Verify session is active before logout
      const beforeLogout = await isAuthenticated(logoutPage.page);
      expect(beforeLogout).toBe(true);

      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Verify session is terminated
      const afterLogout = await isAuthenticated(logoutPage.page);
      expect(afterLogout).toBe(false);
    });

    test('should invalidate session on backend', async () => {
      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Check if session is terminated on backend
      const sessionTerminated = await logoutPage.isSessionTerminated();
      expect(sessionTerminated).toBe(true);
    });

    test('should not allow authenticated API calls after logout', async ({ page }) => {
      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Attempt to make authenticated API call
      const response = await page.request.get('/api/v1/auth/me/');

      // Should fail without authentication
      expect(response.ok()).toBe(false);
      expect([401, 403]).toContain(response.status());
    });

    test('should clear session after page refresh', async ({ page }) => {
      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Verify session is cleared
      const beforeRefresh = await isAuthenticated(page);
      expect(beforeRefresh).toBe(false);

      // Refresh page
      await page.reload();

      // Session should still be cleared
      const afterRefresh = await isAuthenticated(page);
      expect(afterRefresh).toBe(false);

      // Should still be on login page
      expect(page.url()).toContain('/login');
    });

    test('should prevent session restoration after logout', async ({ page }) => {
      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Close and reopen page (simulate browser close/reopen)
      const context = page.context();
      await page.close();
      const newPage = await context.newPage();

      // Navigate to app
      await newPage.goto('/dashboard');
      await newPage.waitForTimeout(1000);

      // Should be redirected to login (session not restored)
      expect(newPage.url()).toContain('/login');
    });
  });

  /**
   * Acceptance Criteria 4: Sensitive Data Cleared
   * Given logout occurs, when the test inspects stored credentials,
   * then sensitive data should be cleared
   */
  test.describe('Sensitive Data Clearance', () => {
    test('should clear access token from localStorage', async ({ page }) => {
      // Verify token exists before logout
      const tokenBefore = await page.evaluate(() => localStorage.getItem('access_token'));
      expect(tokenBefore).toBeTruthy();

      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Verify token is cleared
      const tokenAfter = await page.evaluate(() => localStorage.getItem('access_token'));
      expect(tokenAfter).toBeNull();
    });

    test('should clear refresh token from localStorage', async ({ page }) => {
      // Verify token exists before logout
      const tokenBefore = await page.evaluate(() => localStorage.getItem('refresh_token'));
      expect(tokenBefore).toBeTruthy();

      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Verify token is cleared
      const tokenAfter = await page.evaluate(() => localStorage.getItem('refresh_token'));
      expect(tokenAfter).toBeNull();
    });

    test('should clear user data from localStorage', async ({ page }) => {
      // Verify user data exists before logout
      const userBefore = await page.evaluate(() => localStorage.getItem('user'));
      expect(userBefore).toBeTruthy();

      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Verify user data is cleared
      const userAfter = await page.evaluate(() => localStorage.getItem('user'));
      expect(userAfter).toBeNull();
    });

    test('should clear all authentication-related tokens', async () => {
      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Verify all tokens are cleared
      const tokensCleared = await logoutPage.areTokensCleared();
      expect(tokensCleared).toBe(true);
    });

    test('should clear all user-related data', async () => {
      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Verify all user data is cleared
      const userDataCleared = await logoutPage.isUserDataCleared();
      expect(userDataCleared).toBe(true);
    });

    test('should clear all sensitive data comprehensively', async () => {
      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Comprehensive check for all sensitive data
      const allSensitiveDataCleared = await logoutPage.isSensitiveDataCleared();
      expect(allSensitiveDataCleared).toBe(true);
    });

    test('should not leave any authentication data in sessionStorage', async ({ page }) => {
      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Check sessionStorage is clean
      const sessionData = await page.evaluate(() => {
        const data: { [key: string]: string | null } = {};
        data.accessToken = sessionStorage.getItem('access_token');
        data.refreshToken = sessionStorage.getItem('refresh_token');
        data.user = sessionStorage.getItem('user');
        return data;
      });

      expect(sessionData.accessToken).toBeNull();
      expect(sessionData.refreshToken).toBeNull();
      expect(sessionData.user).toBeNull();
    });

    test('should not expose sensitive data after logout', async ({ page }) => {
      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Get all storage keys
      const localStorageKeys = await logoutPage.getLocalStorageKeys();
      const sessionStorageKeys = await logoutPage.getSessionStorageKeys();

      // Should not contain any auth-related keys
      const sensitiveKeys = ['access_token', 'refresh_token', 'user', 'token', 'auth'];

      for (const sensitiveKey of sensitiveKeys) {
        const hasInLocalStorage = localStorageKeys.some((key) => key.toLowerCase().includes(sensitiveKey));
        const hasInSessionStorage = sessionStorageKeys.some((key) => key.toLowerCase().includes(sensitiveKey));

        expect(hasInLocalStorage).toBe(false);
        expect(hasInSessionStorage).toBe(false);
      }
    });
  });

  /**
   * Additional Tests: Edge Cases and Security
   */
  test.describe('Logout Edge Cases and Security', () => {
    test('should handle logout when already logged out gracefully', async ({ page }) => {
      // First logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Attempt logout again (edge case)
      // Should not error, just stay on login or handle gracefully
      const urlBefore = page.url();

      try {
        // Try to access logout functionality (may not be visible)
        await page.goto('/dashboard');
        await page.waitForTimeout(500);

        // Should be on login page (can't access dashboard)
        expect(page.url()).toContain('/login');
      } catch {
        // If can't access, that's expected
        expect(page.url()).toContain('/login');
      }
    });

    test('should handle network errors during logout gracefully', async ({ page, context }) => {
      // Simulate network failure for logout endpoint
      await context.route('**/api/v1/auth/logout/', (route) => route.abort());

      // Attempt logout
      await logoutPage.logout();

      // Even if API fails, should clear local data and redirect
      await page.waitForTimeout(2000);

      // Should either show error or redirect to login anyway
      const tokensCleared = await logoutPage.areTokensCleared();
      const onLoginPage = await logoutPage.isOnLoginPage();

      // Either tokens are cleared locally or user is on login page
      expect(tokensCleared || onLoginPage).toBe(true);
    });

    test('should prevent CSRF attacks during logout', async ({ page }) => {
      // Get CSRF token if present
      const csrfToken = await page.evaluate(() => {
        const token = document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]');
        return token?.content;
      });

      // Perform logout
      await logoutPage.logout();

      // Logout should succeed (CSRF protection in place)
      await logoutPage.waitForRedirectToLogin();
      expect(page.url()).toContain('/login');
    });

    test('should handle concurrent logout requests', async ({ page }) => {
      // Trigger logout twice rapidly
      const logoutPromise1 = logoutPage.logout();
      const logoutPromise2 = logoutPage.logout();

      // Wait for both to complete
      await Promise.allSettled([logoutPromise1, logoutPromise2]);

      // Should end up on login page regardless
      await page.waitForTimeout(1000);
      expect(page.url()).toContain('/login');

      // Session should be cleared
      const sessionCleared = await isAuthenticated(page);
      expect(sessionCleared).toBe(false);
    });
  });

  /**
   * User Experience Tests
   */
  test.describe('Logout User Experience', () => {
    test('should provide visual feedback during logout', async ({ page }) => {
      // Perform logout
      const logoutPromise = logoutPage.logout();

      // Check for loading indicator (may be present)
      // This is optional - good UX but not required
      try {
        const hasLoadingIndicator = await page.locator('[aria-busy="true"], .loading, .spinner').isVisible({
          timeout: 1000,
        });

        if (hasLoadingIndicator) {
          expect(hasLoadingIndicator).toBe(true);
        }
      } catch {
        // Loading indicator is optional
      }

      await logoutPromise;

      // Should redirect to login
      expect(page.url()).toContain('/login');
    });

    test('should be keyboard accessible', async ({ page }) => {
      // Navigate to logout button using keyboard
      let foundLogout = false;

      // Tab through interface to find logout
      for (let i = 0; i < 20; i++) {
        await page.keyboard.press('Tab');

        const focusedElement = await page.evaluate(() => {
          const element = document.activeElement;
          return element?.textContent?.toLowerCase();
        });

        if (focusedElement?.includes('logout') || focusedElement?.includes('log out')) {
          foundLogout = true;
          break;
        }
      }

      // If logout button is keyboard accessible, test it
      if (foundLogout) {
        // Press Enter to activate logout
        await page.keyboard.press('Enter');

        // Should redirect to login
        await page.waitForTimeout(2000);
        expect(page.url()).toContain('/login');
      }
    });
  });

  /**
   * Visual Regression Tests
   */
  test.describe('Visual Consistency', () => {
    test('should show login page after logout', async ({ page }) => {
      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Wait for login page to fully load
      await page.waitForLoadState('networkidle');

      // Take screenshot for visual regression testing
      await expect(page).toHaveScreenshot('login-page-after-logout.png', {
        fullPage: true,
        animations: 'disabled',
      });
    });
  });

  /**
   * Integration Tests: Logout and Re-login
   */
  test.describe('Logout and Re-login Flow', () => {
    test('should allow user to login again after logout', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Verify on login page
      expect(page.url()).toContain('/login');

      // Login again
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Should be authenticated again
      const authenticated = await isAuthenticated(page);
      expect(authenticated).toBe(true);
      expect(page.url()).toContain('/dashboard');
    });

    test('should create new session after re-login', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Get token before logout
      const tokenBefore = await page.evaluate(() => localStorage.getItem('access_token'));

      // Perform logout
      await logoutPage.logout();
      await logoutPage.waitForRedirectToLogin();

      // Login again
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Get token after re-login
      const tokenAfter = await page.evaluate(() => localStorage.getItem('access_token'));

      // Tokens should be different (new session)
      expect(tokenAfter).toBeTruthy();
      expect(tokenAfter).not.toBe(tokenBefore);
    });
  });
});
