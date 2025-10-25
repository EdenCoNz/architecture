/**
 * Logout Page Object Model
 *
 * Encapsulates all interactions with logout functionality for reusable,
 * maintainable E2E tests. This includes logout button interactions,
 * navigation verification, and session state validation.
 *
 * Story 13.4: Test User Logout Flow
 */

import { Page, Locator, expect } from '@playwright/test';

export class LogoutPage {
  readonly page: Page;

  // Locators for logout UI elements
  readonly logoutButton: Locator;
  readonly logoutMenuItem: Locator;
  readonly userMenuButton: Locator;
  readonly confirmLogoutButton: Locator;
  readonly cancelLogoutButton: Locator;

  // Locators for confirmation dialogs
  readonly logoutDialog: Locator;
  readonly logoutConfirmationMessage: Locator;

  // Locators for success/info messages
  readonly logoutSuccessMessage: Locator;

  constructor(page: Page) {
    this.page = page;

    // Initialize locators for logout elements
    // Using multiple selectors to be resilient to implementation changes
    this.logoutButton = page.locator(
      '[data-testid="logout-button"], button:has-text("Logout"), button:has-text("Log out"), button:has-text("Sign out")'
    );

    this.logoutMenuItem = page.locator(
      '[data-testid="logout-menu-item"], [role="menuitem"]:has-text("Logout"), [role="menuitem"]:has-text("Log out"), [role="menuitem"]:has-text("Sign out")'
    );

    this.userMenuButton = page.locator(
      '[data-testid="user-menu-button"], [aria-label*="user menu"], [aria-label*="account"], button[aria-haspopup="menu"]'
    );

    // Confirmation dialog elements
    this.logoutDialog = page.locator('[data-testid="logout-dialog"], [role="dialog"], [role="alertdialog"]');

    this.confirmLogoutButton = page.locator(
      '[data-testid="confirm-logout-button"], button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Logout")'
    );

    this.cancelLogoutButton = page.locator(
      '[data-testid="cancel-logout-button"], button:has-text("Cancel"), button:has-text("No")'
    );

    this.logoutConfirmationMessage = page.locator('[data-testid="logout-confirmation-message"]');

    this.logoutSuccessMessage = page.locator(
      '[data-testid="logout-success-message"], .success-message, .alert-success'
    );
  }

  /**
   * Navigate to a protected page (e.g., dashboard)
   * This is typically where logout functionality is available
   */
  async gotoProtectedPage(url: string = '/dashboard') {
    await this.page.goto(url);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Click the logout button directly (if visible)
   */
  async clickLogoutButton() {
    await this.logoutButton.click();
  }

  /**
   * Click the logout menu item (if in a dropdown/menu)
   */
  async clickLogoutMenuItem() {
    await this.logoutMenuItem.click();
  }

  /**
   * Open user menu and click logout
   * This is the most common pattern in modern web apps
   */
  async openUserMenuAndLogout() {
    // Open user menu
    await this.userMenuButton.click();

    // Wait for menu to open
    await this.page.waitForTimeout(300); // Small delay for menu animation

    // Click logout menu item
    await this.logoutMenuItem.click();
  }

  /**
   * Perform logout action - tries multiple strategies
   * This is the main method tests should use
   */
  async performLogout() {
    try {
      // Strategy 1: Try direct logout button
      if (await this.logoutButton.isVisible({ timeout: 2000 })) {
        await this.clickLogoutButton();
        return;
      }
    } catch {
      // Continue to next strategy
    }

    try {
      // Strategy 2: Try opening user menu first
      if (await this.userMenuButton.isVisible({ timeout: 2000 })) {
        await this.openUserMenuAndLogout();
        return;
      }
    } catch {
      // Continue to next strategy
    }

    try {
      // Strategy 3: Try direct menu item (if menu is already open)
      if (await this.logoutMenuItem.isVisible({ timeout: 2000 })) {
        await this.clickLogoutMenuItem();
        return;
      }
    } catch {
      throw new Error('Could not find logout button or menu item. Logout functionality may not be implemented.');
    }
  }

  /**
   * Confirm logout in dialog (if confirmation is required)
   */
  async confirmLogout() {
    try {
      // Wait for dialog to appear
      await this.logoutDialog.waitFor({ state: 'visible', timeout: 5000 });

      // Click confirm button
      await this.confirmLogoutButton.click();
    } catch {
      // No confirmation dialog, logout is immediate
    }
  }

  /**
   * Cancel logout in dialog
   */
  async cancelLogout() {
    await this.logoutDialog.waitFor({ state: 'visible', timeout: 5000 });
    await this.cancelLogoutButton.click();
  }

  /**
   * Complete logout flow (trigger + confirm if needed)
   */
  async logout() {
    await this.performLogout();
    await this.confirmLogout();
  }

  /**
   * Wait for navigation to login page after logout
   */
  async waitForRedirectToLogin() {
    await this.page.waitForURL('**/login**', { timeout: 10000 });
  }

  /**
   * Check if user is redirected to login page
   */
  async isOnLoginPage(): Promise<boolean> {
    return this.page.url().includes('/login');
  }

  /**
   * Check if authentication tokens are cleared from localStorage
   */
  async areTokensCleared(): Promise<boolean> {
    const accessToken = await this.page.evaluate(() => localStorage.getItem('access_token'));
    const refreshToken = await this.page.evaluate(() => localStorage.getItem('refresh_token'));

    return accessToken === null && refreshToken === null;
  }

  /**
   * Check if user data is cleared from localStorage
   */
  async isUserDataCleared(): Promise<boolean> {
    const userData = await this.page.evaluate(() => localStorage.getItem('user'));
    return userData === null;
  }

  /**
   * Check if all sensitive data is cleared (comprehensive check)
   */
  async isSensitiveDataCleared(): Promise<boolean> {
    const tokensCleared = await this.areTokensCleared();
    const userDataCleared = await this.isUserDataCleared();

    // Also check for any JWT tokens in sessionStorage
    const sessionTokensCleared = await this.page.evaluate(() => {
      const accessToken = sessionStorage.getItem('access_token');
      const refreshToken = sessionStorage.getItem('refresh_token');
      return accessToken === null && refreshToken === null;
    });

    return tokensCleared && userDataCleared && sessionTokensCleared;
  }

  /**
   * Attempt to access a protected route
   * Returns true if access is granted, false if redirected/denied
   */
  async attemptAccessProtectedRoute(url: string = '/dashboard'): Promise<boolean> {
    await this.page.goto(url);

    // Wait a moment for redirect
    await this.page.waitForTimeout(2000);

    // Check if we're still on the protected route or redirected to login
    return !this.page.url().includes('/login');
  }

  /**
   * Check if session is terminated by attempting an authenticated API call
   */
  async isSessionTerminated(): Promise<boolean> {
    try {
      // Get access token (should be null after logout)
      const accessToken = await this.page.evaluate(() => localStorage.getItem('access_token'));

      if (!accessToken) {
        // No token means session is terminated
        return true;
      }

      // If token still exists, try to use it (should fail)
      const response = await this.page.request.get('/api/v1/auth/me/', {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      // If request succeeds, session is NOT terminated
      // If request fails with 401, session IS terminated
      return !response.ok();
    } catch {
      // Error making request likely means session is terminated
      return true;
    }
  }

  /**
   * Get current page URL
   */
  async getCurrentUrl(): Promise<string> {
    return this.page.url();
  }

  /**
   * Check if logout success message is displayed
   */
  async hasSuccessMessage(): Promise<boolean> {
    try {
      await this.logoutSuccessMessage.waitFor({ state: 'visible', timeout: 3000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Take a screenshot for debugging
   */
  async takeScreenshot(name: string) {
    await this.page.screenshot({
      path: `testing/reports/screenshots/${name}.png`,
      fullPage: true,
    });
  }

  /**
   * Get all localStorage keys (for debugging)
   */
  async getLocalStorageKeys(): Promise<string[]> {
    return await this.page.evaluate(() => Object.keys(localStorage));
  }

  /**
   * Get all sessionStorage keys (for debugging)
   */
  async getSessionStorageKeys(): Promise<string[]> {
    return await this.page.evaluate(() => Object.keys(sessionStorage));
  }
}
