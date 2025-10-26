/**
 * Login Page Object Model
 *
 * Encapsulates all interactions with the login page for reusable,
 * maintainable E2E tests.
 *
 * Story 13.3: Test User Login Flow
 */

import { Page, Locator, expect } from '@playwright/test';

export class LoginPage {
  readonly page: Page;

  // Locators for login form elements
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;
  readonly successMessage: Locator;

  // Locators for form validation
  readonly emailError: Locator;
  readonly passwordError: Locator;

  // Locators for navigation
  readonly registerLink: Locator;
  readonly forgotPasswordLink: Locator;

  constructor(page: Page) {
    this.page = page;

    // Initialize locators using data-testid (preferred) or name attributes
    this.emailInput = page.locator('[data-testid="email-input"], [name="email"], input[type="email"]');
    this.passwordInput = page.locator('[data-testid="password-input"], [name="password"], input[type="password"]');
    this.submitButton = page.locator('[data-testid="submit-button"], button[type="submit"]');
    this.errorMessage = page.locator('[data-testid="error-message"], [role="alert"], .error-message, .alert-error');
    this.successMessage = page.locator('[data-testid="success-message"], .success-message, .alert-success');

    // Validation error locators
    this.emailError = page.locator('[data-testid="email-error"], #email-error, [aria-describedby*="email"]');
    this.passwordError = page.locator('[data-testid="password-error"], #password-error, [aria-describedby*="password"]');

    // Navigation links
    this.registerLink = page.locator('[data-testid="register-link"], a[href*="register"]');
    this.forgotPasswordLink = page.locator('[data-testid="forgot-password-link"], a[href*="forgot-password"]');
  }

  /**
   * Navigate to the login page
   */
  async goto() {
    await this.page.goto('/login');
    await this.waitForPageLoad();
  }

  /**
   * Wait for login page to be fully loaded
   */
  async waitForPageLoad() {
    // Wait for critical form elements to be visible
    await expect(this.emailInput).toBeVisible({ timeout: 10000 });
    await expect(this.passwordInput).toBeVisible({ timeout: 10000 });
    await expect(this.submitButton).toBeVisible({ timeout: 10000 });
  }

  /**
   * Fill in the email field
   */
  async fillEmail(email: string) {
    await this.emailInput.clear();
    await this.emailInput.fill(email);
  }

  /**
   * Fill in the password field
   */
  async fillPassword(password: string) {
    await this.passwordInput.clear();
    await this.passwordInput.fill(password);
  }

  /**
   * Click the submit button
   */
  async clickSubmit() {
    await this.submitButton.click();
  }

  /**
   * Complete login flow with provided credentials
   */
  async login(email: string, password: string) {
    await this.fillEmail(email);
    await this.fillPassword(password);
    await this.clickSubmit();
  }

  /**
   * Check if email input is present and visible
   */
  async hasEmailInput(): Promise<boolean> {
    return await this.emailInput.isVisible();
  }

  /**
   * Check if password input is present and visible
   */
  async hasPasswordInput(): Promise<boolean> {
    return await this.passwordInput.isVisible();
  }

  /**
   * Check if submit button is present and visible
   */
  async hasSubmitButton(): Promise<boolean> {
    return await this.submitButton.isVisible();
  }

  /**
   * Check if all required form fields are present
   */
  async hasAllRequiredFields(): Promise<boolean> {
    const hasEmail = await this.hasEmailInput();
    const hasPassword = await this.hasPasswordInput();
    const hasSubmit = await this.hasSubmitButton();
    return hasEmail && hasPassword && hasSubmit;
  }

  /**
   * Get the error message text
   */
  async getErrorMessage(): Promise<string | null> {
    try {
      await this.errorMessage.waitFor({ state: 'visible', timeout: 5000 });
      return await this.errorMessage.textContent();
    } catch {
      return null;
    }
  }

  /**
   * Check if an error message is displayed
   */
  async hasErrorMessage(): Promise<boolean> {
    try {
      await this.errorMessage.waitFor({ state: 'visible', timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Check if a success message is displayed
   */
  async hasSuccessMessage(): Promise<boolean> {
    try {
      await this.successMessage.waitFor({ state: 'visible', timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Wait for navigation away from login page (successful login)
   */
  async waitForSuccessfulLogin(expectedUrl: string = '/dashboard') {
    await this.page.waitForURL(expectedUrl, { timeout: 10000 });
  }

  /**
   * Check if user is on the login page
   */
  async isOnLoginPage(): Promise<boolean> {
    return this.page.url().includes('/login');
  }

  /**
   * Get current page URL
   */
  async getCurrentUrl(): Promise<string> {
    return this.page.url();
  }

  /**
   * Check form accessibility
   * Ensures proper ARIA labels and roles are present
   */
  async checkAccessibility() {
    // Email input should have label or aria-label
    const emailAccessible = await this.emailInput.evaluate((el) => {
      const hasLabel = el.labels && el.labels.length > 0;
      const hasAriaLabel = el.hasAttribute('aria-label') || el.hasAttribute('aria-labelledby');
      return hasLabel || hasAriaLabel;
    });

    // Password input should have label or aria-label
    const passwordAccessible = await this.passwordInput.evaluate((el) => {
      const hasLabel = el.labels && el.labels.length > 0;
      const hasAriaLabel = el.hasAttribute('aria-label') || el.hasAttribute('aria-labelledby');
      return hasLabel || hasAriaLabel;
    });

    // Submit button should have accessible text
    const submitAccessible = await this.submitButton.evaluate((el) => {
      const hasText = el.textContent && el.textContent.trim().length > 0;
      const hasAriaLabel = el.hasAttribute('aria-label');
      return hasText || hasAriaLabel;
    });

    return {
      emailAccessible,
      passwordAccessible,
      submitAccessible,
      allAccessible: emailAccessible && passwordAccessible && submitAccessible,
    };
  }

  /**
   * Check if submit button is disabled
   */
  async isSubmitDisabled(): Promise<boolean> {
    return await this.submitButton.isDisabled();
  }

  /**
   * Check if submit button is enabled
   */
  async isSubmitEnabled(): Promise<boolean> {
    return await this.submitButton.isEnabled();
  }

  /**
   * Press Enter key to submit form (keyboard accessibility)
   */
  async submitViaEnter() {
    await this.passwordInput.press('Enter');
  }

  /**
   * Navigate to register page
   */
  async goToRegister() {
    await this.registerLink.click();
  }

  /**
   * Navigate to forgot password page
   */
  async goToForgotPassword() {
    await this.forgotPasswordLink.click();
  }

  /**
   * Take a screenshot for debugging
   */
  async takeScreenshot(name: string) {
    await this.page.screenshot({
      path: `testing/reports/screenshots/${name}.png`,
      fullPage: true
    });
  }
}
