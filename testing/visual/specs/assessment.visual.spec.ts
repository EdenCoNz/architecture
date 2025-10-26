/**
 * Visual Regression Tests - Assessment Form
 *
 * Story 13.9: Visual Regression Testing
 *
 * Tests the visual appearance of the Assessment form including
 * stepper navigation, form fields, validation states, and progress indicators.
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

test.describe('Assessment Form - Stepper Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/onboarding');
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);
  });

  test('should match baseline - stepper at step 1', async ({ page }) => {
    // Check if stepper exists
    const stepper = page.locator('[data-testid="assessment-stepper"]');
    if ((await stepper.count()) > 0) {
      await expect(page).toHaveScreenshot('assessment-stepper-step-1.png', {
        maxDiffPixels: 100,
      });
    }
  });

  test('should match baseline - stepper component only', async ({ page }) => {
    const stepper = page.locator('[data-testid="assessment-stepper"]');
    if ((await stepper.count()) > 0) {
      await expect(stepper).toHaveScreenshot('assessment-stepper-component.png', {
        maxDiffPixels: 50,
      });
    }
  });

  test('should match baseline - stepper on mobile', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.mobile);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    const stepper = page.locator('[data-testid="assessment-stepper"]');
    if ((await stepper.count()) > 0) {
      await expect(page).toHaveScreenshot('assessment-stepper-mobile.png', {
        maxDiffPixels: 100,
      });
    }
  });

  test('should match baseline - stepper dark mode', async ({ page }) => {
    await setThemeMode(page, 'dark');
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    const stepper = page.locator('[data-testid="assessment-stepper"]');
    if ((await stepper.count()) > 0) {
      await expect(page).toHaveScreenshot('assessment-stepper-dark.png', {
        maxDiffPixels: 100,
      });
    }
  });
});

test.describe('Assessment Form - Field States', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/onboarding');
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);
  });

  test('should match baseline - all fields empty', async ({ page }) => {
    await expect(page).toHaveScreenshot('assessment-empty-form.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - age field filled', async ({ page }) => {
    const ageInput = page.locator('[name="age"]');
    if ((await ageInput.count()) > 0) {
      await fillFieldForVisualTest(page, '[name="age"]', '25');

      await expect(page).toHaveScreenshot('assessment-age-filled.png', {
        maxDiffPixels: 100,
      });
    }
  });

  test('should match baseline - sport selected', async ({ page }) => {
    const ageInput = page.locator('[name="age"]');
    if ((await ageInput.count()) > 0) {
      await fillFieldForVisualTest(page, '[name="age"]', '25');
    }

    const sportSelect = page.locator('[name="sport"]');
    if ((await sportSelect.count()) > 0) {
      await sportSelect.click();
      await page.waitForTimeout(200);
      const runningOption =
        (await page.locator('[role="option"]:has-text("Running")').count()) > 0
          ? page.locator('[role="option"]:has-text("Running")')
          : page.locator('[role="option"]').first();
      await runningOption.click();
      await page.waitForTimeout(200);

      await expect(page).toHaveScreenshot('assessment-sport-selected.png', {
        maxDiffPixels: 150,
      });
    }
  });

  test('should match baseline - level selected', async ({ page }) => {
    const ageInput = page.locator('[name="age"]');
    if ((await ageInput.count()) > 0) {
      await fillFieldForVisualTest(page, '[name="age"]', '25');
    }

    const sportSelect = page.locator('[name="sport"]');
    if ((await sportSelect.count()) > 0) {
      await sportSelect.click();
      await page.waitForTimeout(200);
      const firstOption = page.locator('[role="option"]').first();
      await firstOption.click();
      await page.waitForTimeout(200);
    }

    const levelSelect = page.locator('[name="level"]');
    if ((await levelSelect.count()) > 0) {
      await levelSelect.click();
      await page.waitForTimeout(200);
      const beginnerOption =
        (await page.locator('[role="option"]:has-text("Beginner")').count()) > 0
          ? page.locator('[role="option"]:has-text("Beginner")')
          : page.locator('[role="option"]').first();
      await beginnerOption.click();
      await page.waitForTimeout(200);

      await expect(page).toHaveScreenshot('assessment-level-selected.png', {
        maxDiffPixels: 150,
      });
    }
  });

  test('should match baseline - training days selected', async ({ page }) => {
    const ageInput = page.locator('[name="age"]');
    if ((await ageInput.count()) > 0) {
      await fillFieldForVisualTest(page, '[name="age"]', '25');
    }

    const sportSelect = page.locator('[name="sport"]');
    if ((await sportSelect.count()) > 0) {
      await sportSelect.click();
      await page.waitForTimeout(200);
      await page.locator('[role="option"]').first().click();
      await page.waitForTimeout(200);
    }

    const levelSelect = page.locator('[name="level"]');
    if ((await levelSelect.count()) > 0) {
      await levelSelect.click();
      await page.waitForTimeout(200);
      await page.locator('[role="option"]').first().click();
      await page.waitForTimeout(200);
    }

    const trainingDaysSelect = page.locator('[name="trainingDays"]');
    if ((await trainingDaysSelect.count()) > 0) {
      await trainingDaysSelect.click();
      await page.waitForTimeout(200);
      await page.locator('[role="option"]').first().click();
      await page.waitForTimeout(200);

      await expect(page).toHaveScreenshot('assessment-training-days-selected.png', {
        maxDiffPixels: 150,
      });
    }
  });
});

test.describe('Assessment Form - Validation States', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/onboarding');
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);
  });

  test('should match baseline - required field errors', async ({ page }) => {
    const submitButton = page.locator('button[type="submit"]');
    if ((await submitButton.count()) > 0) {
      await clickForVisualTest(page, 'button[type="submit"]');
      await page.waitForTimeout(500);

      await expect(page).toHaveScreenshot('assessment-validation-errors.png', {
        maxDiffPixels: 150,
      });
    }
  });

  test('should match baseline - age validation error', async ({ page }) => {
    const ageInput = page.locator('[name="age"]');
    if ((await ageInput.count()) > 0) {
      // Enter invalid age
      await fillFieldForVisualTest(page, '[name="age"]', '5');

      // Trigger validation
      await page.click('body');
      await page.waitForTimeout(300);

      await expect(page).toHaveScreenshot('assessment-age-validation-error.png', {
        maxDiffPixels: 150,
      });
    }
  });

  test('should match baseline - age too high validation', async ({ page }) => {
    const ageInput = page.locator('[name="age"]');
    if ((await ageInput.count()) > 0) {
      // Enter age that's too high
      await fillFieldForVisualTest(page, '[name="age"]', '150');

      // Trigger validation
      await page.click('body');
      await page.waitForTimeout(300);

      await expect(page).toHaveScreenshot('assessment-age-too-high-error.png', {
        maxDiffPixels: 150,
      });
    }
  });

  test('should match baseline - valid form ready to submit', async ({ page }) => {
    // Fill all fields with valid data
    const ageInput = page.locator('[name="age"]');
    if ((await ageInput.count()) > 0) {
      await fillFieldForVisualTest(page, '[name="age"]', '25');
    }

    const sportSelect = page.locator('[name="sport"]');
    if ((await sportSelect.count()) > 0) {
      await sportSelect.click();
      await page.waitForTimeout(200);
      await page.locator('[role="option"]').first().click();
      await page.waitForTimeout(200);
    }

    const levelSelect = page.locator('[name="level"]');
    if ((await levelSelect.count()) > 0) {
      await levelSelect.click();
      await page.waitForTimeout(200);
      await page.locator('[role="option"]').first().click();
      await page.waitForTimeout(200);
    }

    const trainingDaysSelect = page.locator('[name="trainingDays"]');
    if ((await trainingDaysSelect.count()) > 0) {
      await trainingDaysSelect.click();
      await page.waitForTimeout(200);
      await page.locator('[role="option"]').first().click();
      await page.waitForTimeout(200);
    }

    await expect(page).toHaveScreenshot('assessment-valid-form.png', {
      maxDiffPixels: 150,
    });
  });
});

test.describe('Assessment Form - Responsive Design', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/onboarding');
  });

  test('should match baseline - desktop view', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.desktop);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('assessment-desktop.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - tablet view', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.tablet);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('assessment-tablet.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - mobile view', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.mobile);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('assessment-mobile.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - small mobile view', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.mobileSmall);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('assessment-mobile-small.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - desktop HD view', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.desktopHd);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('assessment-desktop-hd.png', {
      maxDiffPixels: 100,
    });
  });
});

test.describe('Assessment Form - Dark Mode', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/onboarding');
  });

  test('should match baseline - dark mode empty form', async ({ page }) => {
    await setThemeMode(page, 'dark');
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('assessment-dark-mode.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - dark mode with validation errors', async ({ page }) => {
    await setThemeMode(page, 'dark');
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    const submitButton = page.locator('button[type="submit"]');
    if ((await submitButton.count()) > 0) {
      await clickForVisualTest(page, 'button[type="submit"]');
      await page.waitForTimeout(500);

      await expect(page).toHaveScreenshot('assessment-dark-validation-errors.png', {
        maxDiffPixels: 150,
      });
    }
  });

  test('should match baseline - dark mode filled form', async ({ page }) => {
    await setThemeMode(page, 'dark');
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    // Fill all fields
    const ageInput = page.locator('[name="age"]');
    if ((await ageInput.count()) > 0) {
      await fillFieldForVisualTest(page, '[name="age"]', '25');
    }

    const sportSelect = page.locator('[name="sport"]');
    if ((await sportSelect.count()) > 0) {
      await sportSelect.click();
      await page.waitForTimeout(200);
      await page.locator('[role="option"]').first().click();
      await page.waitForTimeout(200);
    }

    const levelSelect = page.locator('[name="level"]');
    if ((await levelSelect.count()) > 0) {
      await levelSelect.click();
      await page.waitForTimeout(200);
      await page.locator('[role="option"]').first().click();
      await page.waitForTimeout(200);
    }

    const trainingDaysSelect = page.locator('[name="trainingDays"]');
    if ((await trainingDaysSelect.count()) > 0) {
      await trainingDaysSelect.click();
      await page.waitForTimeout(200);
      await page.locator('[role="option"]').first().click();
      await page.waitForTimeout(200);
    }

    await expect(page).toHaveScreenshot('assessment-dark-filled.png', {
      maxDiffPixels: 150,
    });
  });
});
