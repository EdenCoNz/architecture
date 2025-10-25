/**
 * Playwright Configuration for Visual Regression Tests
 *
 * Story 13.9: Visual Regression Testing
 *
 * Configures visual regression testing with screenshot comparison,
 * baseline management, and multi-viewport testing capabilities.
 */

import { defineConfig, devices } from '@playwright/test';

/**
 * Read environment variables for test configuration
 */
const TEST_BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:5174';
const CI = !!process.env.CI;

export default defineConfig({
  // Test directory
  testDir: './specs',

  // Test timeout (2 minutes per test)
  timeout: 120000,

  // Expect timeout (10 seconds for assertions)
  expect: {
    timeout: 10000,

    // Screenshot comparison settings
    toHaveScreenshot: {
      // Maximum number of pixels that can differ
      maxDiffPixels: 100,

      // Pixel color difference threshold (0-1)
      // 0 means colors must match exactly, 1 means any difference is acceptable
      threshold: 0.2,

      // Disable animations for consistent screenshots
      animations: 'disabled',

      // CSS to disable animations and transitions
      stylePath: undefined,

      // Scale down screenshots for faster comparison
      scale: 'css',
    },
  },

  // Snapshot directory for baseline images
  snapshotDir: './baselines',

  // Output directory for test artifacts
  outputDir: '../reports/visual-results',

  // Run tests in parallel (but not in CI for consistency)
  fullyParallel: !CI,

  // Retry failed tests
  retries: CI ? 2 : 0,

  // Number of parallel workers
  workers: CI ? 1 : undefined, // Single worker in CI for consistency

  // Reporter configuration
  reporter: [
    // HTML report for local viewing
    ['html', { outputFolder: '../reports/html/visual-report', open: 'never' }],

    // JSON report for CI/CD
    ['json', { outputFile: '../reports/json/visual-report.json' }],

    // List reporter for console output
    ['list'],

    // JUnit reporter for CI/CD
    ['junit', { outputFile: '../reports/junit/visual-results.xml' }],
  ],

  // Shared settings for all projects
  use: {
    // Base URL for tests
    baseURL: TEST_BASE_URL,

    // Capture screenshot on failure
    screenshot: 'only-on-failure',

    // Capture video on failure
    video: 'retain-on-failure',

    // Capture trace on failure
    trace: 'retain-on-failure',

    // Action timeout
    actionTimeout: 10000,

    // Navigation timeout
    navigationTimeout: 30000,

    // Ignore HTTPS errors in test environment
    ignoreHTTPSErrors: true,

    // Disable animations for consistent screenshots
    // This can be overridden per test if needed
    hasTouch: false,

    // Color scheme
    colorScheme: 'light',
  },

  // Configure projects for different browsers and viewports
  projects: [
    // Desktop - Chrome
    {
      name: 'desktop-chrome',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
      },
    },

    // Desktop - Firefox
    {
      name: 'desktop-firefox',
      use: {
        ...devices['Desktop Firefox'],
        viewport: { width: 1280, height: 720 },
      },
    },

    // Desktop - Safari
    {
      name: 'desktop-safari',
      use: {
        ...devices['Desktop Safari'],
        viewport: { width: 1280, height: 720 },
      },
    },

    // Tablet - iPad
    {
      name: 'tablet-ipad',
      use: {
        ...devices['iPad Pro'],
      },
    },

    // Mobile - iPhone
    {
      name: 'mobile-iphone',
      use: {
        ...devices['iPhone 12'],
      },
    },

    // Mobile - Android
    {
      name: 'mobile-android',
      use: {
        ...devices['Pixel 5'],
      },
    },

    // Dark mode testing (Desktop Chrome)
    {
      name: 'desktop-chrome-dark',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
        colorScheme: 'dark',
      },
    },
  ],

  // Web server configuration (for local development)
  // Starts dev servers before running tests
  webServer: CI
    ? undefined
    : [
        {
          command: 'cd ../frontend && npm run dev',
          url: TEST_BASE_URL,
          timeout: 120000,
          reuseExistingServer: true,
        },
      ],
});
