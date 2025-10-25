/**
 * Playwright Configuration for E2E Tests
 *
 * Configures test execution, browser settings, reporting,
 * and environment-specific options.
 *
 * Story 13.3: Test User Login Flow
 */

import { defineConfig, devices } from '@playwright/test';

/**
 * Read environment variables for test configuration
 */
const TEST_BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:5174';
const TEST_API_URL = process.env.TEST_API_URL || 'http://localhost:8001';
const CI = !!process.env.CI;

export default defineConfig({
  // Test directory
  testDir: './specs',

  // Test timeout (2 minutes per test)
  timeout: 120000,

  // Expect timeout (10 seconds for assertions)
  expect: {
    timeout: 10000,
  },

  // Test artifacts directory
  outputDir: '../reports/test-results',

  // Fail build on CI if tests fail
  fullyParallel: !CI,

  // Retry failed tests
  retries: CI ? 2 : 0,

  // Number of parallel workers
  workers: CI ? 2 : undefined,

  // Reporter configuration
  reporter: [
    // HTML report for local viewing
    ['html', { outputFolder: '../reports/html/e2e-report', open: 'never' }],

    // JSON report for CI/CD
    ['json', { outputFile: '../reports/json/e2e-report.json' }],

    // List reporter for console output
    ['list'],

    // JUnit reporter for CI/CD
    ['junit', { outputFile: '../reports/junit/e2e-results.xml' }],
  ],

  // Global setup/teardown
  // globalSetup: require.resolve('./global-setup.ts'),
  // globalTeardown: require.resolve('./global-teardown.ts'),

  // Shared settings for all projects
  use: {
    // Base URL for tests
    baseURL: TEST_BASE_URL,

    // Capture screenshot on failure
    screenshot: 'only-on-failure',

    // Capture video on first retry
    video: 'retain-on-failure',

    // Capture trace on failure
    trace: 'retain-on-failure',

    // Action timeout
    actionTimeout: 10000,

    // Navigation timeout
    navigationTimeout: 30000,

    // Ignore HTTPS errors in test environment
    ignoreHTTPSErrors: true,

    // Extra HTTP headers
    extraHTTPHeaders: {
      'Accept': 'application/json',
    },
  },

  // Configure projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
      },
    },

    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
        viewport: { width: 1280, height: 720 },
      },
    },

    {
      name: 'webkit',
      use: {
        ...devices['Desktop Safari'],
        viewport: { width: 1280, height: 720 },
      },
    },

    // Mobile browsers
    {
      name: 'mobile-chrome',
      use: {
        ...devices['Pixel 5'],
      },
    },

    {
      name: 'mobile-safari',
      use: {
        ...devices['iPhone 12'],
      },
    },

    // Tablet browsers
    {
      name: 'tablet-ipad',
      use: {
        ...devices['iPad Pro'],
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
        {
          command: 'cd ../backend && python manage.py runserver 8001',
          url: `${TEST_API_URL}/api/v1/health/`,
          timeout: 120000,
          reuseExistingServer: true,
        },
      ],
});
