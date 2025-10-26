/**
 * Visual Testing Helper Utilities
 *
 * Story 13.9: Visual Regression Testing
 *
 * Common utilities for visual regression tests including
 * page stabilization, animation disabling, and screenshot helpers.
 */

import { Page } from '@playwright/test';

/**
 * Screenshot options for consistent visual testing
 */
export interface ScreenshotOptions {
  /**
   * Maximum number of pixels that can differ from baseline
   * @default 100
   */
  maxDiffPixels?: number;

  /**
   * Pixel color difference threshold (0-1)
   * @default 0.2
   */
  threshold?: number;

  /**
   * Elements to mask in the screenshot (for dynamic content)
   */
  mask?: Array<any>;

  /**
   * Whether to capture the full page (scroll entire page)
   * @default false
   */
  fullPage?: boolean;
}

/**
 * Prepares a page for stable visual testing by:
 * - Waiting for network to be idle
 * - Waiting for fonts to load
 * - Disabling animations and transitions
 * - Removing focus rings
 */
export async function preparePageForVisualTest(page: Page): Promise<void> {
  // Wait for page to be fully loaded
  await page.waitForLoadState('networkidle');

  // Wait for fonts to load
  await page.waitForFunction(() => document.fonts.ready);

  // Disable animations, transitions, and other dynamic effects
  await page.addStyleTag({
    content: `
      *,
      *::before,
      *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
        scroll-behavior: auto !important;
      }

      /* Remove focus rings for screenshots */
      *:focus {
        outline: none !important;
        box-shadow: none !important;
      }

      /* Disable smooth scrolling */
      html {
        scroll-behavior: auto !important;
      }
    `,
  });

  // Small delay to ensure styles are applied
  await page.waitForTimeout(100);
}

/**
 * Hides dynamic content that changes between test runs
 */
export async function hideDynamicContent(page: Page): Promise<void> {
  await page.addStyleTag({
    content: `
      .timestamp,
      .date-time,
      [data-testid*="timestamp"],
      [data-testid*="time"],
      [class*="timestamp"],
      [class*="datetime"] {
        visibility: hidden !important;
      }
    `,
  });
}

/**
 * Waits for Material UI components to finish rendering
 */
export async function waitForMuiComponents(page: Page): Promise<void> {
  // Wait for MUI styles to be injected
  await page.waitForSelector('style[data-emotion]', { timeout: 5000 }).catch(() => {
    // It's okay if emotion styles aren't found, not all pages may use them
  });

  // Wait for any ripple effects to complete
  await page.waitForTimeout(100);
}

/**
 * Sets the theme mode for visual testing
 */
export async function setThemeMode(page: Page, mode: 'light' | 'dark'): Promise<void> {
  // Set the color scheme
  await page.emulateMedia({ colorScheme: mode });

  // If the app has a theme toggle, try to set it
  const themeToggle = page.locator('[data-testid="theme-toggle"]');
  const exists = await themeToggle.count();

  if (exists > 0) {
    // Get current theme state
    const isDarkMode = await page.evaluate(() => {
      return document.documentElement.classList.contains('dark');
    });

    // Toggle if needed
    if ((mode === 'dark' && !isDarkMode) || (mode === 'light' && isDarkMode)) {
      await themeToggle.click();
      await page.waitForTimeout(300); // Wait for theme transition
    }
  }
}

/**
 * Captures a full page screenshot with scrolling
 */
export async function captureFullPageScreenshot(
  page: Page,
  name: string,
  options?: ScreenshotOptions
): Promise<void> {
  await preparePageForVisualTest(page);

  // Scroll to ensure lazy-loaded content is rendered
  await page.evaluate(() => {
    window.scrollTo(0, document.body.scrollHeight);
  });
  await page.waitForTimeout(500);

  // Scroll back to top
  await page.evaluate(() => {
    window.scrollTo(0, 0);
  });
  await page.waitForTimeout(100);

  // Take screenshot
  await page.screenshot({
    path: name,
    fullPage: true,
    ...options,
  });
}

/**
 * Common viewport sizes for responsive testing
 */
export const VIEWPORTS = {
  // Desktop
  desktop: { width: 1280, height: 720 },
  desktopHd: { width: 1920, height: 1080 },

  // Tablet
  tablet: { width: 768, height: 1024 },
  tabletLandscape: { width: 1024, height: 768 },

  // Mobile
  mobile: { width: 375, height: 667 },
  mobileLandscape: { width: 667, height: 375 },
  mobileSmall: { width: 320, height: 568 },
} as const;

/**
 * Waits for a specific element to be stable (not moving)
 */
export async function waitForElementStable(
  page: Page,
  selector: string,
  timeoutMs: number = 1000
): Promise<void> {
  const element = page.locator(selector);
  await element.waitFor({ state: 'visible' });

  // Wait for element position to stabilize
  let previousBox: any = null;
  const startTime = Date.now();

  while (Date.now() - startTime < timeoutMs) {
    const box = await element.boundingBox();

    if (previousBox && box) {
      if (
        Math.abs(box.x - previousBox.x) < 1 &&
        Math.abs(box.y - previousBox.y) < 1 &&
        Math.abs(box.width - previousBox.width) < 1 &&
        Math.abs(box.height - previousBox.height) < 1
      ) {
        // Element is stable
        return;
      }
    }

    previousBox = box;
    await page.waitForTimeout(50);
  }
}

/**
 * Fills a form field and waits for it to stabilize
 */
export async function fillFieldForVisualTest(
  page: Page,
  selector: string,
  value: string
): Promise<void> {
  await page.fill(selector, value);
  await page.waitForTimeout(100); // Wait for any validation or state updates
}

/**
 * Clicks an element and waits for visual changes to complete
 */
export async function clickForVisualTest(page: Page, selector: string): Promise<void> {
  await page.click(selector);
  await page.waitForTimeout(300); // Wait for any animations or state updates
  await page.waitForLoadState('networkidle');
}
