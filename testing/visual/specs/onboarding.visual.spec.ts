/**
 * Visual Regression Tests - Onboarding Page
 *
 * Story 13.9: Visual Regression Testing
 *
 * Tests the visual appearance of the Onboarding page including
 * multi-step form, different states, validation errors, and responsiveness.
 */

import { test, expect } from '@playwright/test';
import {
  preparePageForVisualTest,
  waitForMuiComponents,
  setThemeMode,
  VIEWPORTS,
  fillFieldForVisualTest,
  clickForVisualTest,
} from '../helpers/visual-test-helpers';

test.describe('Onboarding Page - Initial State', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/onboarding');
  });

  test('should match baseline - initial load desktop', async ({ page }) => {
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('onboarding-initial-desktop.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - initial load mobile', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.mobile);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('onboarding-initial-mobile.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - initial load tablet', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.tablet);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('onboarding-initial-tablet.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - dark mode', async ({ page }) => {
    await setThemeMode(page, 'dark');
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('onboarding-initial-dark.png', {
      maxDiffPixels: 100,
    });
  });
});

test.describe('Onboarding Page - Form States', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/onboarding');
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);
  });

  test('should match baseline - empty form validation errors', async ({ page }) => {
    // Try to submit empty form
    const submitButton = page.locator('button[type="submit"]');
    if ((await submitButton.count()) > 0) {
      await clickForVisualTest(page, 'button[type="submit"]');

      // Wait for validation errors to appear
      await page.waitForTimeout(500);

      await expect(page).toHaveScreenshot('onboarding-empty-validation.png', {
        maxDiffPixels: 150,
      });
    }
  });

  test('should match baseline - partially filled form', async ({ page }) => {
    // Fill some fields
    const ageInput = page.locator('[name="age"]');
    if ((await ageInput.count()) > 0) {
      await fillFieldForVisualTest(page, '[name="age"]', '25');
    }

    const sportSelect = page.locator('[name="sport"]');
    if ((await sportSelect.count()) > 0) {
      await sportSelect.click();
      await page.waitForTimeout(200);

      const firstOption = page.locator('[role="option"]').first();
      if ((await firstOption.count()) > 0) {
        await firstOption.click();
        await page.waitForTimeout(200);
      }
    }

    await expect(page).toHaveScreenshot('onboarding-partially-filled.png', {
      maxDiffPixels: 150,
    });
  });

  test('should match baseline - completely filled valid form', async ({ page }) => {
    // Fill all required fields
    const ageInput = page.locator('[name="age"]');
    if ((await ageInput.count()) > 0) {
      await fillFieldForVisualTest(page, '[name="age"]', '25');
    }

    // Select sport
    const sportSelect = page.locator('[name="sport"]');
    if ((await sportSelect.count()) > 0) {
      await sportSelect.click();
      await page.waitForTimeout(200);
      const firstOption = page.locator('[role="option"]').first();
      if ((await firstOption.count()) > 0) {
        await firstOption.click();
        await page.waitForTimeout(200);
      }
    }

    // Select level
    const levelSelect = page.locator('[name="level"]');
    if ((await levelSelect.count()) > 0) {
      await levelSelect.click();
      await page.waitForTimeout(200);
      const firstOption = page.locator('[role="option"]').first();
      if ((await firstOption.count()) > 0) {
        await firstOption.click();
        await page.waitForTimeout(200);
      }
    }

    // Select training days
    const trainingDaysSelect = page.locator('[name="trainingDays"]');
    if ((await trainingDaysSelect.count()) > 0) {
      await trainingDaysSelect.click();
      await page.waitForTimeout(200);
      const firstOption = page.locator('[role="option"]').first();
      if ((await firstOption.count()) > 0) {
        await firstOption.click();
        await page.waitForTimeout(200);
      }
    }

    await expect(page).toHaveScreenshot('onboarding-filled-valid.png', {
      maxDiffPixels: 150,
    });
  });

  test('should match baseline - invalid age validation', async ({ page }) => {
    // Enter invalid age (too young or too old)
    const ageInput = page.locator('[name="age"]');
    if ((await ageInput.count()) > 0) {
      await fillFieldForVisualTest(page, '[name="age"]', '10');

      // Trigger validation by clicking outside
      await page.click('body');
      await page.waitForTimeout(300);

      await expect(page).toHaveScreenshot('onboarding-invalid-age.png', {
        maxDiffPixels: 150,
      });
    }
  });
});

test.describe('Onboarding Page - Dropdown Interactions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/onboarding');
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);
  });

  test('should match baseline - sport dropdown open', async ({ page }) => {
    const sportSelect = page.locator('[name="sport"]');
    if ((await sportSelect.count()) > 0) {
      await sportSelect.click();
      await page.waitForTimeout(300);

      await expect(page).toHaveScreenshot('onboarding-sport-dropdown-open.png', {
        maxDiffPixels: 150,
      });
    }
  });

  test('should match baseline - level dropdown open', async ({ page }) => {
    const levelSelect = page.locator('[name="level"]');
    if ((await levelSelect.count()) > 0) {
      await levelSelect.click();
      await page.waitForTimeout(300);

      await expect(page).toHaveScreenshot('onboarding-level-dropdown-open.png', {
        maxDiffPixels: 150,
      });
    }
  });

  test('should match baseline - training days dropdown open', async ({ page }) => {
    const trainingDaysSelect = page.locator('[name="trainingDays"]');
    if ((await trainingDaysSelect.count()) > 0) {
      await trainingDaysSelect.click();
      await page.waitForTimeout(300);

      await expect(page).toHaveScreenshot('onboarding-training-days-dropdown-open.png', {
        maxDiffPixels: 150,
      });
    }
  });
});

test.describe('Onboarding Page - Responsive Layout', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/onboarding');
  });

  test('should match baseline - mobile small device', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.mobileSmall);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('onboarding-mobile-small.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - tablet landscape', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.tabletLandscape);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('onboarding-tablet-landscape.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - desktop HD', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.desktopHd);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('onboarding-desktop-hd.png', {
      maxDiffPixels: 100,
    });
  });
});

test.describe('Onboarding Page - Form Components', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/onboarding');
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);
  });

  test('should match baseline - focused age input', async ({ page }) => {
    const ageInput = page.locator('[name="age"]');
    if ((await ageInput.count()) > 0) {
      await ageInput.focus();
      await page.waitForTimeout(100);

      // Remove focus ring for consistent screenshot
      await preparePageForVisualTest(page);

      await expect(page).toHaveScreenshot('onboarding-age-focused.png', {
        maxDiffPixels: 100,
      });
    }
  });

  test('should match baseline - submit button hover', async ({ page }) => {
    const submitButton = page.locator('button[type="submit"]');
    if ((await submitButton.count()) > 0) {
      await submitButton.hover();
      await page.waitForTimeout(100);

      await expect(page).toHaveScreenshot('onboarding-submit-hover.png', {
        maxDiffPixels: 100,
      });
    }
  });
});
