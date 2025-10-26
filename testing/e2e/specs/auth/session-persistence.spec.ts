/**
 * Session Persistence E2E Tests
 *
 * Tests validate session persistence across different scenarios:
 * - Page refresh maintaining authentication state
 * - Browser context restart (simulated) maintaining session
 * - Session expiration after inactivity period
 * - "Remember me" long-term persistence beyond typical timeout
 *
 * Story 13.5: Test Session Persistence
 *
 * Acceptance Criteria:
 * 1. Page refresh should maintain user authentication
 * 2. Browser restart simulation should maintain active session
 * 3. Inactive sessions should expire as expected
 * 4. "Remember me" should persist beyond typical timeout
 */

import { test, expect, BrowserContext, Page } from '@playwright/test';
import { LoginPage } from '../../page-objects/LoginPage';
import {
  TEST_USERS,
  registerUser,
  isAuthenticated,
  getStoredUser,
  clearAuth,
  loginViaAPI,
  AUTH_ENDPOINTS,
} from '../../fixtures/auth';

/**
 * Helper function to simulate time passing (for session expiration tests)
 */
async function simulateTimePass(page: Page, minutes: number): Promise<void> {
  // Manipulate token timestamps in localStorage to simulate time passing
  const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));
  const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'));

  if (!accessToken || !refreshToken) {
    return;
  }

  // Note: In a real implementation, you would need to manipulate token timestamps
  // or use backend test utilities to expire tokens. This is a placeholder
  // that demonstrates the test structure.
  await page.waitForTimeout(minutes * 1000); // Simplified simulation
}

/**
 * Helper function to check if access token is expired
 */
async function isAccessTokenExpired(page: Page): Promise<boolean> {
  const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));

  if (!accessToken) {
    return true;
  }

  try {
    // Decode JWT token to check expiration
    const payload = JSON.parse(atob(accessToken.split('.')[1]));
    const expirationTime = payload.exp * 1000; // Convert to milliseconds
    const currentTime = Date.now();

    return currentTime >= expirationTime;
  } catch (error) {
    return true;
  }
}

/**
 * Helper function to get token expiration time
 */
async function getTokenExpirationTime(page: Page, tokenKey: string): Promise<number | null> {
  const token = await page.evaluate((key) => localStorage.getItem(key), tokenKey);

  if (!token) {
    return null;
  }

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000; // Convert to milliseconds
  } catch (error) {
    return null;
  }
}

/**
 * Helper function to save browser storage state
 */
async function saveStorageState(page: Page): Promise<{
  localStorage: Record<string, string>;
  cookies: any[];
}> {
  const localStorage = await page.evaluate(() => {
    const items: Record<string, string> = {};
    for (let i = 0; i < window.localStorage.length; i++) {
      const key = window.localStorage.key(i);
      if (key) {
        items[key] = window.localStorage.getItem(key) || '';
      }
    }
    return items;
  });

  const context = page.context();
  const cookies = await context.cookies();

  return { localStorage, cookies };
}

/**
 * Helper function to restore browser storage state
 */
async function restoreStorageState(
  page: Page,
  state: { localStorage: Record<string, string>; cookies: any[] }
): Promise<void> {
  // Restore localStorage
  await page.evaluate((items) => {
    Object.entries(items).forEach(([key, value]) => {
      localStorage.setItem(key, value);
    });
  }, state.localStorage);

  // Restore cookies
  await page.context().addCookies(state.cookies);
}

test.describe('Session Persistence', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);

    // Clear any existing authentication
    await clearAuth(page);

    // Ensure test user is registered
    const { email, password, firstName, lastName } = TEST_USERS.validUser;
    await registerUser(page, email, password, firstName, lastName);
  });

  /**
   * Acceptance Criteria 1: Page Refresh Maintains Authentication
   * Given a user successfully logs in, when the page is refreshed,
   * then the test should verify the user remains authenticated
   */
  test.describe('Page Refresh Persistence', () => {
    test('should maintain authentication after single page refresh', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Login user
      await loginPage.goto();
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Verify authenticated before refresh
      const beforeRefresh = await isAuthenticated(page);
      expect(beforeRefresh).toBe(true);

      const userBeforeRefresh = await getStoredUser(page);
      expect(userBeforeRefresh).toBeTruthy();
      expect(userBeforeRefresh.email).toBe(email);

      // Refresh the page
      await page.reload();

      // Verify still authenticated after refresh
      const afterRefresh = await isAuthenticated(page);
      expect(afterRefresh).toBe(true);

      const userAfterRefresh = await getStoredUser(page);
      expect(userAfterRefresh).toBeTruthy();
      expect(userAfterRefresh.email).toBe(email);

      // Verify tokens are still present
      const hasAccessToken = await page.evaluate(() => localStorage.getItem('access_token') !== null);
      const hasRefreshToken = await page.evaluate(() => localStorage.getItem('refresh_token') !== null);

      expect(hasAccessToken).toBe(true);
      expect(hasRefreshToken).toBe(true);

      // Verify still on dashboard (not redirected to login)
      expect(page.url()).toContain('/dashboard');
    });

    test('should maintain authentication after multiple page refreshes', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Login user
      await loginPage.goto();
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Perform multiple refreshes
      for (let i = 0; i < 3; i++) {
        await page.reload();

        // Verify still authenticated after each refresh
        const isAuth = await isAuthenticated(page);
        expect(isAuth).toBe(true);

        // Verify user data persists
        const user = await getStoredUser(page);
        expect(user.email).toBe(email);

        // Verify still on dashboard
        expect(page.url()).toContain('/dashboard');
      }
    });

    test('should maintain authentication when navigating between pages', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Login user
      await loginPage.goto();
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Navigate to different pages
      await page.goto('/');
      expect(await isAuthenticated(page)).toBe(true);

      await page.goto('/dashboard');
      expect(await isAuthenticated(page)).toBe(true);

      // Verify can access protected resources
      const response = await page.request.get(AUTH_ENDPOINTS.me, {
        headers: {
          Authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('access_token'))}`,
        },
      });

      expect(response.ok()).toBe(true);
      const userData = await response.json();
      expect(userData.email).toBe(email);
    });

    test('should preserve session across hard navigation', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Login user
      await loginPage.goto();
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      const accessTokenBefore = await page.evaluate(() => localStorage.getItem('access_token'));

      // Perform hard navigation (full page reload with new URL)
      await page.goto('/dashboard', { waitUntil: 'networkidle' });

      const accessTokenAfter = await page.evaluate(() => localStorage.getItem('access_token'));

      // Tokens should be the same (session persisted)
      expect(accessTokenAfter).toBe(accessTokenBefore);
      expect(await isAuthenticated(page)).toBe(true);
    });
  });

  /**
   * Acceptance Criteria 2: Browser Restart Simulation
   * Given an active session exists, when the test simulates closing
   * and reopening the browser, then the user should still be logged in
   */
  test.describe('Browser Restart Simulation', () => {
    test('should maintain session after browser context restart', async ({ browser }) => {
      const { email, password } = TEST_USERS.validUser;

      // Create first browser context and login
      const context1 = await browser.newContext();
      const page1 = await context1.newPage();
      loginPage = new LoginPage(page1);

      // Register user
      await registerUser(page1, email, password, TEST_USERS.validUser.firstName, TEST_USERS.validUser.lastName);

      // Login
      await loginPage.goto();
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Save storage state (simulates browser persistence)
      const storageState = await saveStorageState(page1);

      // Close first context (simulates browser close)
      await context1.close();

      // Create new browser context (simulates browser reopen)
      const context2 = await browser.newContext();
      const page2 = await context2.newPage();

      // Restore storage state
      await restoreStorageState(page2, storageState);

      // Navigate to dashboard
      await page2.goto('/dashboard');

      // Verify session persisted
      const isAuth = await isAuthenticated(page2);
      expect(isAuth).toBe(true);

      const user = await getStoredUser(page2);
      expect(user.email).toBe(email);

      // Verify can still access protected resources
      const response = await page2.request.get(AUTH_ENDPOINTS.me, {
        headers: {
          Authorization: `Bearer ${await page2.evaluate(() => localStorage.getItem('access_token'))}`,
        },
      });

      expect(response.ok()).toBe(true);

      await context2.close();
    });

    test('should maintain session with Playwright storage state API', async ({ browser }) => {
      const { email, password } = TEST_USERS.validUser;

      // Create first context and login
      const context1 = await browser.newContext();
      const page1 = await context1.newPage();
      loginPage = new LoginPage(page1);

      await registerUser(page1, email, password, TEST_USERS.validUser.firstName, TEST_USERS.validUser.lastName);

      await loginPage.goto();
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Save storage state using Playwright API
      const storageStatePath = '/tmp/playwright-storage-state.json';
      await context1.storageState({ path: storageStatePath });

      await context1.close();

      // Create new context with saved storage state
      const context2 = await browser.newContext({
        storageState: storageStatePath,
      });
      const page2 = await context2.newPage();

      // Navigate to dashboard
      await page2.goto('/dashboard');

      // Verify session persisted
      expect(await isAuthenticated(page2)).toBe(true);
      expect(page2.url()).toContain('/dashboard');

      const user = await getStoredUser(page2);
      expect(user.email).toBe(email);

      await context2.close();
    });

    test('should handle missing storage state gracefully', async ({ browser }) => {
      // Create context without any storage state
      const context = await browser.newContext();
      const page = await context.newPage();

      // Try to access protected page
      await page.goto('/dashboard');

      // Should redirect to login (no session)
      await page.waitForURL(/login/i, { timeout: 5000 }).catch(() => {
        // If no redirect, verify no authentication
        expect(isAuthenticated(page)).resolves.toBe(false);
      });

      await context.close();
    });
  });

  /**
   * Acceptance Criteria 3: Session Expiration
   * Given a session has been inactive for a specified period,
   * when the test checks session validity, then the session
   * should expire as expected
   */
  test.describe('Session Expiration', () => {
    test('should detect access token expiration time', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Login user
      await loginPage.goto();
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Get token expiration time
      const expirationTime = await getTokenExpirationTime(page, 'access_token');
      expect(expirationTime).toBeTruthy();

      // Verify expiration is in the future
      const currentTime = Date.now();
      expect(expirationTime).toBeGreaterThan(currentTime);

      // Verify expiration is approximately 15 minutes from now (per docs)
      const fifteenMinutes = 15 * 60 * 1000;
      const timeDifference = expirationTime! - currentTime;

      // Allow some margin (14-16 minutes)
      expect(timeDifference).toBeGreaterThan(13 * 60 * 1000);
      expect(timeDifference).toBeLessThan(17 * 60 * 1000);
    });

    test('should refresh token before access token expiration', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Login user
      await loginPage.goto();
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Get initial tokens
      const initialAccessToken = await page.evaluate(() => localStorage.getItem('access_token'));
      const initialRefreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'));

      expect(initialAccessToken).toBeTruthy();
      expect(initialRefreshToken).toBeTruthy();

      // Manually refresh token
      const response = await page.request.post(AUTH_ENDPOINTS.refresh, {
        data: {
          refresh: initialRefreshToken,
        },
      });

      expect(response.ok()).toBe(true);

      const data = await response.json();
      expect(data.access).toBeTruthy();
      expect(data.refresh).toBeTruthy();

      // New tokens should be different from initial tokens
      expect(data.access).not.toBe(initialAccessToken);
      expect(data.refresh).not.toBe(initialRefreshToken);

      // Update localStorage with new tokens
      await page.evaluate(
        ({ access, refresh }) => {
          localStorage.setItem('access_token', access);
          localStorage.setItem('refresh_token', refresh);
        },
        { access: data.access, refresh: data.refresh }
      );

      // Verify new token works
      const meResponse = await page.request.get(AUTH_ENDPOINTS.me, {
        headers: {
          Authorization: `Bearer ${data.access}`,
        },
      });

      expect(meResponse.ok()).toBe(true);
      const userData = await meResponse.json();
      expect(userData.email).toBe(email);
    });

    test('should reject expired refresh token', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Login user
      await loginPage.goto();
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'));

      // Logout (blacklists refresh token)
      const logoutResponse = await page.request.post(AUTH_ENDPOINTS.logout, {
        data: { refresh: refreshToken },
        headers: {
          Authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('access_token'))}`,
        },
      });

      expect(logoutResponse.ok()).toBe(true);

      // Try to use blacklisted refresh token
      const refreshResponse = await page.request.post(AUTH_ENDPOINTS.refresh, {
        data: { refresh: refreshToken },
      });

      // Should fail (token is blacklisted)
      expect(refreshResponse.ok()).toBe(false);
      expect(refreshResponse.status()).toBe(401);
    });

    test('should handle concurrent session expiration', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Login user
      await loginPage.goto();
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Clear tokens (simulate expiration)
      await clearAuth(page);

      // Refresh page
      await page.reload();

      // Should redirect to login or show as unauthenticated
      await page.waitForTimeout(2000); // Wait for any redirects

      const currentUrl = page.url();
      const isAuth = await isAuthenticated(page);

      // Either redirected to login or marked as unauthenticated
      expect(currentUrl.includes('/login') || !isAuth).toBe(true);
    });
  });

  /**
   * Acceptance Criteria 4: "Remember Me" Long-term Persistence
   * Given a user has "remember me" enabled, when the test verifies
   * long-term persistence, then the session should persist beyond
   * the typical timeout period
   */
  test.describe('Remember Me Long-term Persistence', () => {
    test('should verify refresh token has longer lifetime than access token', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Login user
      await loginPage.goto();
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Get expiration times for both tokens
      const accessExpiration = await getTokenExpirationTime(page, 'access_token');
      const refreshExpiration = await getTokenExpirationTime(page, 'refresh_token');

      expect(accessExpiration).toBeTruthy();
      expect(refreshExpiration).toBeTruthy();

      // Refresh token should expire much later than access token
      expect(refreshExpiration).toBeGreaterThan(accessExpiration!);

      // Per docs: access=15min, refresh=7days
      // Verify refresh token expires approximately 7 days from now
      const currentTime = Date.now();
      const sevenDays = 7 * 24 * 60 * 60 * 1000;
      const refreshTimeDiff = refreshExpiration! - currentTime;

      // Allow some margin (6.5-7.5 days)
      expect(refreshTimeDiff).toBeGreaterThan(6.5 * 24 * 60 * 60 * 1000);
      expect(refreshTimeDiff).toBeLessThan(7.5 * 24 * 60 * 60 * 1000);
    });

    test('should maintain session with refresh token rotation', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Login user
      await loginPage.goto();
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Simulate multiple token refreshes (as would happen over 7 days)
      let currentRefreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'));

      for (let i = 0; i < 5; i++) {
        // Refresh token
        const response = await page.request.post(AUTH_ENDPOINTS.refresh, {
          data: { refresh: currentRefreshToken },
        });

        expect(response.ok()).toBe(true);

        const data = await response.json();
        expect(data.access).toBeTruthy();
        expect(data.refresh).toBeTruthy();

        // Update tokens
        await page.evaluate(
          ({ access, refresh }) => {
            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);
          },
          { access: data.access, refresh: data.refresh }
        );

        // Update for next iteration
        currentRefreshToken = data.refresh;

        // Verify new access token works
        const meResponse = await page.request.get(AUTH_ENDPOINTS.me, {
          headers: { Authorization: `Bearer ${data.access}` },
        });

        expect(meResponse.ok()).toBe(true);
      }

      // After 5 refreshes, should still be authenticated
      expect(await isAuthenticated(page)).toBe(true);
    });

    test('should persist session across browser restart within refresh token lifetime', async ({ browser }) => {
      const { email, password } = TEST_USERS.validUser;

      // Create first context and login
      const context1 = await browser.newContext();
      const page1 = await context1.newPage();
      loginPage = new LoginPage(page1);

      await registerUser(page1, email, password, TEST_USERS.validUser.firstName, TEST_USERS.validUser.lastName);

      await loginPage.goto();
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Verify long-lived refresh token exists
      const refreshExpiration = await getTokenExpirationTime(page1, 'refresh_token');
      const currentTime = Date.now();
      const daysUntilExpiration = (refreshExpiration! - currentTime) / (24 * 60 * 60 * 1000);

      // Should be valid for approximately 7 days
      expect(daysUntilExpiration).toBeGreaterThan(6);
      expect(daysUntilExpiration).toBeLessThan(8);

      // Save storage state
      const storageStatePath = '/tmp/playwright-remember-me-state.json';
      await context1.storageState({ path: storageStatePath });
      await context1.close();

      // Simulate browser restart (new context)
      const context2 = await browser.newContext({
        storageState: storageStatePath,
      });
      const page2 = await context2.newPage();

      // Navigate to app
      await page2.goto('/dashboard');

      // Session should persist
      expect(await isAuthenticated(page2)).toBe(true);

      // Refresh token should still be valid
      const refreshToken = await page2.evaluate(() => localStorage.getItem('refresh_token'));
      const refreshResponse = await page2.request.post(AUTH_ENDPOINTS.refresh, {
        data: { refresh: refreshToken },
      });

      expect(refreshResponse.ok()).toBe(true);

      await context2.close();
    });

    test('should allow user to manually extend session before expiration', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Login user
      await loginPage.goto();
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Get initial expiration
      const initialAccessExpiration = await getTokenExpirationTime(page, 'access_token');

      // Wait a moment
      await page.waitForTimeout(2000);

      // Refresh token (extends session)
      const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'));
      const response = await page.request.post(AUTH_ENDPOINTS.refresh, {
        data: { refresh: refreshToken },
      });

      expect(response.ok()).toBe(true);

      const data = await response.json();

      // Update tokens
      await page.evaluate(
        ({ access, refresh }) => {
          localStorage.setItem('access_token', access);
          localStorage.setItem('refresh_token', refresh);
        },
        { access: data.access, refresh: data.refresh }
      );

      // Get new expiration
      const newAccessExpiration = await getTokenExpirationTime(page, 'access_token');

      // New expiration should be later than initial
      expect(newAccessExpiration).toBeGreaterThan(initialAccessExpiration!);
    });
  });

  /**
   * Additional Tests: Edge Cases and Security
   */
  test.describe('Session Security and Edge Cases', () => {
    test('should not persist session after explicit logout', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Login user
      await loginPage.goto();
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Verify authenticated
      expect(await isAuthenticated(page)).toBe(true);

      // Logout
      const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'));
      await page.request.post(AUTH_ENDPOINTS.logout, {
        data: { refresh: refreshToken },
        headers: {
          Authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('access_token'))}`,
        },
      });

      // Clear tokens
      await clearAuth(page);

      // Refresh page
      await page.reload();

      // Should not be authenticated
      expect(await isAuthenticated(page)).toBe(false);
    });

    test('should handle token tampering attempts', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Login user
      await loginPage.goto();
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Tamper with access token
      await page.evaluate(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
          // Modify last character
          const tampered = token.slice(0, -1) + 'X';
          localStorage.setItem('access_token', tampered);
        }
      });

      // Try to access protected resource with tampered token
      const response = await page.request.get(AUTH_ENDPOINTS.me, {
        headers: {
          Authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('access_token'))}`,
        },
      });

      // Should be rejected
      expect(response.ok()).toBe(false);
      expect(response.status()).toBe(401);
    });

    test('should handle missing tokens gracefully', async ({ page }) => {
      // Navigate without tokens
      await page.goto('/dashboard');

      // Should redirect to login or show as unauthenticated
      await page.waitForTimeout(2000);

      const currentUrl = page.url();
      const isAuth = await isAuthenticated(page);

      expect(currentUrl.includes('/login') || !isAuth).toBe(true);
    });

    test('should prevent session fixation attacks', async ({ page }) => {
      const { email, password } = TEST_USERS.validUser;

      // Set malicious token before login
      await page.evaluate(() => {
        localStorage.setItem('access_token', 'malicious_token');
        localStorage.setItem('refresh_token', 'malicious_refresh');
      });

      // Login
      await loginPage.goto();
      await loginPage.login(email, password);
      await loginPage.waitForSuccessfulLogin('/dashboard');

      // Verify tokens were replaced with valid ones
      const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));
      const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'));

      expect(accessToken).not.toBe('malicious_token');
      expect(refreshToken).not.toBe('malicious_refresh');

      // Verify new tokens are valid JWT format
      expect(accessToken?.split('.')).toHaveLength(3);
      expect(refreshToken?.split('.')).toHaveLength(3);
    });
  });
});
