/**
 * Visual Regression Tests - Home Page
 *
 * Story 13.9: Visual Regression Testing
 *
 * Tests the visual appearance of the Home page across
 * different viewports, themes, and states.
 */

import { test, expect } from '@playwright/test';
import {
  preparePageForVisualTest,
  waitForMuiComponents,
  setThemeMode,
  VIEWPORTS,
} from '../helpers/visual-test-helpers';

test.describe('Home Page - Visual Regression', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home page
    await page.goto('/');
  });

  test('should match baseline - desktop light mode', async ({ page }) => {
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('home-desktop-light.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - desktop dark mode', async ({ page }) => {
    await setThemeMode(page, 'dark');
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('home-desktop-dark.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - tablet viewport', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.tablet);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('home-tablet.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - mobile viewport', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.mobile);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('home-mobile.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - header component', async ({ page }) => {
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    // Screenshot just the header
    const header = page.locator('header');
    await expect(header).toHaveScreenshot('home-header.png', {
      maxDiffPixels: 50,
    });
  });

  test('should match baseline - theme toggle interaction', async ({ page }) => {
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    // Find theme toggle button
    const themeToggle = page.locator('[data-testid="theme-toggle"]');

    // Take screenshot with toggle visible
    await expect(page).toHaveScreenshot('home-with-theme-toggle.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - full page scroll', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.desktop);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    // Scroll to bottom and back to top to ensure all content is loaded
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(500);
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(100);

    await expect(page).toHaveScreenshot('home-full-page.png', {
      fullPage: true,
      maxDiffPixels: 150,
    });
  });

  test('should match baseline - mobile landscape', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.mobileLandscape);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('home-mobile-landscape.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - small mobile device', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.mobileSmall);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('home-mobile-small.png', {
      maxDiffPixels: 100,
    });
  });
});

test.describe('Home Page - Navigation Links', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should match baseline - navigation hover states', async ({ page }) => {
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    // Hover over navigation links
    const navLinks = page.locator('nav a');
    const count = await navLinks.count();

    if (count > 0) {
      await navLinks.first().hover();
      await page.waitForTimeout(100);

      await expect(page).toHaveScreenshot('home-nav-hover.png', {
        maxDiffPixels: 100,
      });
    }
  });
});
