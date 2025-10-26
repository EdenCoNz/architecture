/**
 * Visual Regression Tests - Dashboard/Main Application Pages
 *
 * Story 13.9: Visual Regression Testing
 *
 * Tests the visual appearance of dashboard and main application pages.
 * Note: This file tests the Home page which serves as the dashboard
 * until authentication is implemented.
 */

import { test, expect } from '@playwright/test';
import {
  preparePageForVisualTest,
  waitForMuiComponents,
  setThemeMode,
  VIEWPORTS,
} from '../helpers/visual-test-helpers';

test.describe('Dashboard - Main View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should match baseline - dashboard desktop view', async ({ page }) => {
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('dashboard-desktop.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - dashboard mobile view', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.mobile);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('dashboard-mobile.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - dashboard tablet view', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.tablet);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('dashboard-tablet.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - dashboard dark mode', async ({ page }) => {
    await setThemeMode(page, 'dark');
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('dashboard-dark.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - dashboard full page', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.desktop);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    // Scroll to ensure all content is loaded
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(500);
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(100);

    await expect(page).toHaveScreenshot('dashboard-full-page.png', {
      fullPage: true,
      maxDiffPixels: 150,
    });
  });
});

test.describe('Dashboard - Navigation States', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);
  });

  test('should match baseline - navigation visible', async ({ page }) => {
    const nav = page.locator('nav');
    if ((await nav.count()) > 0) {
      await expect(nav).toHaveScreenshot('dashboard-navigation.png', {
        maxDiffPixels: 50,
      });
    }
  });

  test('should match baseline - header component', async ({ page }) => {
    const header = page.locator('header');
    await expect(header).toHaveScreenshot('dashboard-header.png', {
      maxDiffPixels: 50,
    });
  });

  test('should match baseline - main content area', async ({ page }) => {
    const mainContent = page.locator('main');
    await expect(mainContent).toHaveScreenshot('dashboard-main-content.png', {
      maxDiffPixels: 100,
    });
  });
});

test.describe('Dashboard - Responsive Breakpoints', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should match baseline - desktop HD (1920x1080)', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.desktopHd);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('dashboard-1920x1080.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - tablet landscape', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.tabletLandscape);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('dashboard-tablet-landscape.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - mobile landscape', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.mobileLandscape);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('dashboard-mobile-landscape.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - small mobile (320px)', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.mobileSmall);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('dashboard-320px.png', {
      maxDiffPixels: 100,
    });
  });
});

test.describe('Dashboard - Theme Variations', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should match baseline - light mode desktop', async ({ page }) => {
    await setThemeMode(page, 'light');
    await page.setViewportSize(VIEWPORTS.desktop);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('dashboard-light-desktop.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - dark mode desktop', async ({ page }) => {
    await setThemeMode(page, 'dark');
    await page.setViewportSize(VIEWPORTS.desktop);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('dashboard-dark-desktop.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - light mode mobile', async ({ page }) => {
    await setThemeMode(page, 'light');
    await page.setViewportSize(VIEWPORTS.mobile);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('dashboard-light-mobile.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - dark mode mobile', async ({ page }) => {
    await setThemeMode(page, 'dark');
    await page.setViewportSize(VIEWPORTS.mobile);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('dashboard-dark-mobile.png', {
      maxDiffPixels: 100,
    });
  });
});

test.describe('Dashboard - Interactive Elements', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);
  });

  test('should match baseline - theme toggle button', async ({ page }) => {
    const themeToggle = page.locator('[data-testid="theme-toggle"]');
    if ((await themeToggle.count()) > 0) {
      await expect(themeToggle).toHaveScreenshot('dashboard-theme-toggle.png', {
        maxDiffPixels: 30,
      });
    }
  });

  test('should match baseline - navigation links', async ({ page }) => {
    const navLinks = page.locator('nav a');
    const count = await navLinks.count();

    if (count > 0) {
      for (let i = 0; i < Math.min(count, 3); i++) {
        const link = navLinks.nth(i);
        await expect(link).toHaveScreenshot(`dashboard-nav-link-${i}.png`, {
          maxDiffPixels: 30,
        });
      }
    }
  });

  test('should match baseline - buttons hover state', async ({ page }) => {
    const buttons = page.locator('button');
    const count = await buttons.count();

    if (count > 0) {
      const firstButton = buttons.first();
      await firstButton.hover();
      await page.waitForTimeout(100);

      // Remove focus for consistent screenshot
      await preparePageForVisualTest(page);

      await expect(firstButton).toHaveScreenshot('dashboard-button-hover.png', {
        maxDiffPixels: 50,
      });
    }
  });
});

test.describe('Dashboard - Layout Components', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);
  });

  test('should match baseline - page title area', async ({ page }) => {
    const title = page.locator('h1').first();
    if ((await title.count()) > 0) {
      await expect(title).toHaveScreenshot('dashboard-page-title.png', {
        maxDiffPixels: 50,
      });
    }
  });

  test('should match baseline - content cards', async ({ page }) => {
    const cards = page.locator('[class*="MuiCard"]');
    const count = await cards.count();

    if (count > 0) {
      await expect(cards.first()).toHaveScreenshot('dashboard-content-card.png', {
        maxDiffPixels: 50,
      });
    }
  });

  test('should match baseline - footer area', async ({ page }) => {
    const footer = page.locator('footer');
    if ((await footer.count()) > 0) {
      await expect(footer).toHaveScreenshot('dashboard-footer.png', {
        maxDiffPixels: 50,
      });
    }
  });
});
