/**
 * Authentication fixtures for Playwright tests
 *
 * Provides reusable test credentials, authentication helpers,
 * and authenticated context fixtures for E2E testing.
 *
 * Story 13.3: Test User Login Flow
 * Story 13.5: Test Session Persistence
 */

import { test as base, Page } from '@playwright/test';

/**
 * Test user credentials
 * These users should be created in the test database before tests run
 */
export const TEST_USERS = {
  validUser: {
    email: 'test@example.com',
    password: 'TestPassword123!',
    firstName: 'Test',
    lastName: 'User',
  },
  invalidUser: {
    email: 'invalid@example.com',
    password: 'WrongPassword123!',
  },
  inactiveUser: {
    email: 'inactive@example.com',
    password: 'InactivePassword123!',
  },
} as const;

/**
 * API endpoints for authentication
 */
export const AUTH_ENDPOINTS = {
  register: '/api/v1/auth/register/',
  login: '/api/v1/auth/login/',
  logout: '/api/v1/auth/logout/',
  me: '/api/v1/auth/me/',
  refresh: '/api/v1/auth/token/refresh/',
} as const;

/**
 * Authentication storage keys
 */
export const AUTH_STORAGE_KEYS = {
  accessToken: 'access_token',
  refreshToken: 'refresh_token',
  user: 'user',
} as const;

/**
 * Helper function to register a test user via API
 */
export async function registerUser(
  page: Page,
  email: string,
  password: string,
  firstName: string = 'Test',
  lastName: string = 'User'
): Promise<{ success: boolean; error?: string }> {
  try {
    const response = await page.request.post(AUTH_ENDPOINTS.register, {
      data: {
        email,
        password,
        password_confirm: password,
        first_name: firstName,
        last_name: lastName,
      },
    });

    if (!response.ok()) {
      const error = await response.json();
      return { success: false, error: JSON.stringify(error) };
    }

    return { success: true };
  } catch (error) {
    return { success: false, error: String(error) };
  }
}

/**
 * Helper function to login via API and store tokens
 */
export async function loginViaAPI(
  page: Page,
  email: string,
  password: string
): Promise<{ success: boolean; tokens?: { access: string; refresh: string }; error?: string }> {
  try {
    const response = await page.request.post(AUTH_ENDPOINTS.login, {
      data: {
        email,
        password,
      },
    });

    if (!response.ok()) {
      const error = await response.json();
      return { success: false, error: JSON.stringify(error) };
    }

    const data = await response.json();

    // Store tokens in localStorage
    await page.evaluate(
      ({ access, refresh, user }) => {
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
        localStorage.setItem('user', JSON.stringify(user));
      },
      {
        access: data.access,
        refresh: data.refresh,
        user: data.user,
      }
    );

    return {
      success: true,
      tokens: {
        access: data.access,
        refresh: data.refresh,
      },
    };
  } catch (error) {
    return { success: false, error: String(error) };
  }
}

/**
 * Helper function to logout via API
 */
export async function logoutViaAPI(page: Page, refreshToken: string): Promise<{ success: boolean; error?: string }> {
  try {
    const response = await page.request.post(AUTH_ENDPOINTS.logout, {
      data: {
        refresh: refreshToken,
      },
      headers: {
        Authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('access_token'))}`,
      },
    });

    if (!response.ok()) {
      const error = await response.json();
      return { success: false, error: JSON.stringify(error) };
    }

    // Clear tokens from localStorage
    await page.evaluate(() => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    });

    return { success: true };
  } catch (error) {
    return { success: false, error: String(error) };
  }
}

/**
 * Helper function to check if user is authenticated
 */
export async function isAuthenticated(page: Page): Promise<boolean> {
  const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));
  return accessToken !== null;
}

/**
 * Helper function to get stored user data
 */
export async function getStoredUser(page: Page): Promise<any | null> {
  const userJson = await page.evaluate(() => localStorage.getItem('user'));
  return userJson ? JSON.parse(userJson) : null;
}

/**
 * Helper function to clear authentication state
 */
export async function clearAuth(page: Page): Promise<void> {
  await page.evaluate(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  });
}

/**
 * Helper function to get token expiration time
 * Story 13.5: Session Persistence Testing
 */
export async function getTokenExpiration(page: Page, tokenKey: string): Promise<number | null> {
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
 * Helper function to check if a token is expired
 * Story 13.5: Session Persistence Testing
 */
export async function isTokenExpired(page: Page, tokenKey: string): Promise<boolean> {
  const expirationTime = await getTokenExpiration(page, tokenKey);

  if (!expirationTime) {
    return true;
  }

  return Date.now() >= expirationTime;
}

/**
 * Helper function to refresh authentication tokens
 * Story 13.5: Session Persistence Testing
 */
export async function refreshTokens(page: Page): Promise<{ success: boolean; tokens?: { access: string; refresh: string }; error?: string }> {
  try {
    const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'));

    if (!refreshToken) {
      return { success: false, error: 'No refresh token found' };
    }

    const response = await page.request.post(AUTH_ENDPOINTS.refresh, {
      data: {
        refresh: refreshToken,
      },
    });

    if (!response.ok()) {
      const error = await response.json();
      return { success: false, error: JSON.stringify(error) };
    }

    const data = await response.json();

    // Update tokens in localStorage
    await page.evaluate(
      ({ access, refresh }) => {
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
      },
      {
        access: data.access,
        refresh: data.refresh,
      }
    );

    return {
      success: true,
      tokens: {
        access: data.access,
        refresh: data.refresh,
      },
    };
  } catch (error) {
    return { success: false, error: String(error) };
  }
}

/**
 * Helper function to get all stored tokens
 * Story 13.5: Session Persistence Testing
 */
export async function getStoredTokens(page: Page): Promise<{ accessToken: string | null; refreshToken: string | null }> {
  return await page.evaluate(() => ({
    accessToken: localStorage.getItem('access_token'),
    refreshToken: localStorage.getItem('refresh_token'),
  }));
}

/**
 * Helper function to verify token is valid by making authenticated API call
 * Story 13.5: Session Persistence Testing
 */
export async function verifyTokenValidity(page: Page): Promise<boolean> {
  try {
    const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));

    if (!accessToken) {
      return false;
    }

    const response = await page.request.get(AUTH_ENDPOINTS.me, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    return response.ok();
  } catch (error) {
    return false;
  }
}

/**
 * Extended test fixture with authenticated page context
 *
 * Usage:
 * ```typescript
 * import { test } from '../fixtures/auth';
 *
 * test('should access protected route', async ({ authenticatedPage }) => {
 *   await authenticatedPage.goto('/dashboard');
 *   // User is already logged in
 * });
 * ```
 */
export const test = base.extend<{
  authenticatedPage: Page;
}>({
  authenticatedPage: async ({ page }, use) => {
    // Register and login before test
    const { email, password, firstName, lastName } = TEST_USERS.validUser;

    // Register user (may fail if already exists, that's ok)
    await registerUser(page, email, password, firstName, lastName);

    // Login to get tokens
    const loginResult = await loginViaAPI(page, email, password);

    if (!loginResult.success) {
      throw new Error(`Failed to authenticate: ${loginResult.error}`);
    }

    // Provide authenticated page to test
    await use(page);

    // Cleanup: logout after test
    if (loginResult.tokens) {
      await logoutViaAPI(page, loginResult.tokens.refresh);
    }
  },
});

export { expect } from '@playwright/test';
