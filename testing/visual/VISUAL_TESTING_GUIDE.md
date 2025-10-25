# Visual Regression Testing Guide

**Story 13.9: Visual Regression Testing**

## Overview

Visual regression testing automatically detects unintended UI changes across releases by comparing screenshots of the current UI against baseline images. This guide provides comprehensive information on running, writing, and maintaining visual regression tests.

## Table of Contents

- [Quick Start](#quick-start)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Writing Visual Tests](#writing-visual-tests)
- [Baseline Management](#baseline-management)
- [Handling Test Failures](#handling-test-failures)
- [Best Practices](#best-practices)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Running All Visual Tests

```bash
# From project root
./testing/run-tests.sh --suite visual

# Or from testing directory
npm run test:visual
```

### Running Specific Test Files

```bash
# Run only home page tests
npx playwright test --config=visual/playwright.config.ts visual/specs/home.visual.spec.ts

# Run only onboarding tests
npx playwright test --config=visual/playwright.config.ts visual/specs/onboarding.visual.spec.ts

# Run only assessment tests
npx playwright test --config=visual/playwright.config.ts visual/specs/assessment.visual.spec.ts

# Run only dashboard tests
npx playwright test --config=visual/playwright.config.ts visual/specs/dashboard.visual.spec.ts
```

### Updating Baselines After Intentional UI Changes

```bash
# Update all baselines
npm run test:visual:update

# Update specific test baselines
npx playwright test --config=visual/playwright.config.ts visual/specs/home.visual.spec.ts --update-snapshots
```

## Test Structure

```
visual/
├── playwright.config.ts       # Playwright configuration
├── tsconfig.json             # TypeScript configuration
├── specs/                    # Test specifications
│   ├── home.visual.spec.ts
│   ├── onboarding.visual.spec.ts
│   ├── assessment.visual.spec.ts
│   └── dashboard.visual.spec.ts
├── helpers/                  # Reusable test utilities
│   └── visual-test-helpers.ts
├── baselines/                # Baseline screenshots (generated)
│   ├── home-desktop-light.png
│   ├── onboarding-initial-mobile.png
│   └── ...
└── VISUAL_TESTING_GUIDE.md  # This file
```

## Running Tests

### Basic Test Execution

```bash
# All visual tests
npm run test:visual

# With debug mode
npx playwright test --config=visual/playwright.config.ts --debug

# With UI mode (interactive)
npx playwright test --config=visual/playwright.config.ts --ui

# Specific browser only
npx playwright test --config=visual/playwright.config.ts --project=desktop-chrome
```

### Test Options

```bash
# Show browser while running (headed mode)
npx playwright test --config=visual/playwright.config.ts --headed

# Run tests matching a pattern
npx playwright test --config=visual/playwright.config.ts -g "dark mode"

# Run with maximum workers
npx playwright test --config=visual/playwright.config.ts --workers=4

# Generate HTML report
npx playwright test --config=visual/playwright.config.ts --reporter=html
```

### Viewing Test Results

```bash
# Open HTML report
npx playwright show-report ../reports/html/visual-report

# View JSON report
cat ../reports/json/visual-report.json

# View JUnit XML
cat ../reports/junit/visual-results.xml
```

## Writing Visual Tests

### Basic Visual Test Structure

```typescript
import { test, expect } from '@playwright/test';
import {
  preparePageForVisualTest,
  waitForMuiComponents,
  VIEWPORTS,
} from '../helpers/visual-test-helpers';

test.describe('Page Name - Visual Regression', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/your-page');
  });

  test('should match baseline - desktop view', async ({ page }) => {
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('your-page-desktop.png', {
      maxDiffPixels: 100,
    });
  });
});
```

### Testing Different States

```typescript
test.describe('Form States', () => {
  test('should match baseline - empty form', async ({ page }) => {
    await page.goto('/form');
    await preparePageForVisualTest(page);

    await expect(page).toHaveScreenshot('form-empty.png');
  });

  test('should match baseline - filled form', async ({ page }) => {
    await page.goto('/form');
    await preparePageForVisualTest(page);

    // Fill form fields
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');

    await expect(page).toHaveScreenshot('form-filled.png');
  });

  test('should match baseline - validation errors', async ({ page }) => {
    await page.goto('/form');
    await preparePageForVisualTest(page);

    // Trigger validation
    await page.click('button[type="submit"]');
    await page.waitForTimeout(300);

    await expect(page).toHaveScreenshot('form-errors.png');
  });
});
```

### Testing Responsive Design

```typescript
import { VIEWPORTS } from '../helpers/visual-test-helpers';

test.describe('Responsive Layout', () => {
  test('should match baseline - mobile', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.mobile);
    await page.goto('/page');
    await preparePageForVisualTest(page);

    await expect(page).toHaveScreenshot('page-mobile.png');
  });

  test('should match baseline - tablet', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.tablet);
    await page.goto('/page');
    await preparePageForVisualTest(page);

    await expect(page).toHaveScreenshot('page-tablet.png');
  });

  test('should match baseline - desktop', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.desktop);
    await page.goto('/page');
    await preparePageForVisualTest(page);

    await expect(page).toHaveScreenshot('page-desktop.png');
  });
});
```

### Testing Dark Mode

```typescript
import { setThemeMode } from '../helpers/visual-test-helpers';

test.describe('Theme Variations', () => {
  test('should match baseline - light mode', async ({ page }) => {
    await page.goto('/page');
    await setThemeMode(page, 'light');
    await preparePageForVisualTest(page);

    await expect(page).toHaveScreenshot('page-light.png');
  });

  test('should match baseline - dark mode', async ({ page }) => {
    await page.goto('/page');
    await setThemeMode(page, 'dark');
    await preparePageForVisualTest(page);

    await expect(page).toHaveScreenshot('page-dark.png');
  });
});
```

### Component-Level Screenshots

```typescript
test('should match baseline - specific component', async ({ page }) => {
  await page.goto('/page');
  await preparePageForVisualTest(page);

  // Screenshot specific element
  const button = page.locator('[data-testid="primary-button"]');
  await expect(button).toHaveScreenshot('primary-button.png');
});
```

### Masking Dynamic Content

```typescript
test('should match baseline - masked dynamic content', async ({ page }) => {
  await page.goto('/dashboard');
  await preparePageForVisualTest(page);

  // Mask elements that change between runs
  await expect(page).toHaveScreenshot('dashboard.png', {
    mask: [
      page.locator('.timestamp'),
      page.locator('.session-id'),
      page.locator('[data-testid="user-avatar"]'),
    ],
  });
});
```

## Baseline Management

### Creating Initial Baselines

When you run visual tests for the first time, Playwright automatically creates baseline screenshots:

```bash
# First run creates baselines
npm run test:visual
```

Baselines are stored in `testing/visual/baselines/` directory.

### Updating Baselines After UI Changes

After intentional UI changes, update baselines:

```bash
# Update all baselines
npm run test:visual:update

# Update specific test
npx playwright test --config=visual/playwright.config.ts \
  visual/specs/home.visual.spec.ts \
  --update-snapshots

# Update baselines for specific project (browser)
npx playwright test --config=visual/playwright.config.ts \
  --project=desktop-chrome \
  --update-snapshots
```

### Committing Baselines to Git

Baseline images should be committed to version control:

```bash
git add testing/visual/baselines/
git commit -m "Update visual regression baselines"
```

### Baseline Naming Convention

Baselines are automatically named by Playwright based on:
- Test file name
- Test name
- Project name (browser)

Example: `home-desktop-light-desktop-chrome.png`

## Handling Test Failures

### Understanding Test Failures

When a visual test fails, Playwright generates three images:

1. **Expected** (`baselines/test-name.png`) - The baseline image
2. **Actual** (`test-results/test-name-actual.png`) - The current screenshot
3. **Diff** (`test-results/test-name-diff.png`) - Visual difference highlighted

### Reviewing Failures

```bash
# Open HTML report to view diffs
npx playwright show-report ../reports/html/visual-report

# View diff images directly
open ../reports/visual-results/test-name/test-name-diff.png
```

### Determining If Changes Are Intentional

#### Intentional Changes (Update Baseline)

If the visual change is expected:

```bash
# Accept the new visual appearance
npm run test:visual:update

# Or update specific test
npx playwright test --config=visual/playwright.config.ts \
  visual/specs/home.visual.spec.ts \
  --update-snapshots
```

#### Unintentional Changes (Fix the Bug)

If the visual change is a regression:

1. Review the diff to understand what changed
2. Fix the UI bug in your code
3. Re-run the tests to verify the fix

```bash
# Re-run tests after fix
npm run test:visual
```

### Common Failure Causes

1. **Font loading issues** - Fonts not loaded before screenshot
2. **Animation timing** - Animations not disabled
3. **Dynamic content** - Timestamps, IDs, or random data
4. **Async operations** - Data not loaded before screenshot
5. **Browser differences** - Different rendering across browsers

## Best Practices

### 1. Stable Screenshots

Always use the helper utilities to ensure stable screenshots:

```typescript
import { preparePageForVisualTest, waitForMuiComponents } from '../helpers/visual-test-helpers';

test('my visual test', async ({ page }) => {
  await page.goto('/page');

  // Prepare page for stable screenshot
  await preparePageForVisualTest(page);
  await waitForMuiComponents(page);

  await expect(page).toHaveScreenshot('page.png');
});
```

### 2. Mask Dynamic Content

Hide or mask content that changes between runs:

```typescript
// Option 1: Mask elements
await expect(page).toHaveScreenshot('page.png', {
  mask: [
    page.locator('.timestamp'),
    page.locator('.session-id'),
  ],
});

// Option 2: Hide with CSS
await page.addStyleTag({
  content: '.timestamp { visibility: hidden !important; }',
});
```

### 3. Use Consistent Viewports

Use predefined viewport constants:

```typescript
import { VIEWPORTS } from '../helpers/visual-test-helpers';

await page.setViewportSize(VIEWPORTS.mobile);
```

Available viewports:
- `desktop`: 1280x720
- `desktopHd`: 1920x1080
- `tablet`: 768x1024
- `tabletLandscape`: 1024x768
- `mobile`: 375x667
- `mobileLandscape`: 667x375
- `mobileSmall`: 320x568

### 4. Test Critical UI States

Focus on testing:
- Empty states
- Filled/populated states
- Error states
- Loading states
- Success states
- Different user roles/permissions

### 5. Test Multiple Browsers

Visual tests run on multiple browsers by default:
- Desktop Chrome
- Desktop Firefox
- Desktop Safari
- Mobile Chrome (Pixel 5)
- Mobile Safari (iPhone 12)
- Tablet (iPad Pro)
- Dark mode variant

### 6. Set Appropriate Thresholds

Adjust `maxDiffPixels` based on test needs:

```typescript
// Strict comparison (for small components)
await expect(button).toHaveScreenshot('button.png', {
  maxDiffPixels: 10,
});

// Lenient comparison (for full pages)
await expect(page).toHaveScreenshot('page.png', {
  maxDiffPixels: 150,
});
```

### 7. Group Related Tests

Organize tests by page or feature:

```typescript
test.describe('Login Page', () => {
  test.describe('Form States', () => {
    // Tests for different form states
  });

  test.describe('Responsive Layout', () => {
    // Tests for different viewports
  });

  test.describe('Theme Variations', () => {
    // Tests for light/dark themes
  });
});
```

### 8. Avoid Flaky Tests

Common causes of flaky visual tests:
- Not waiting for network idle
- Not waiting for fonts to load
- Not disabling animations
- Not waiting for async operations
- Testing time-dependent content

Use helper utilities to avoid these issues.

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Visual Regression Tests

on:
  pull_request:
    branches: [main, develop]

jobs:
  visual-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Visual Tests
        run: ./testing/run-tests.sh --suite visual

      - name: Upload Visual Diffs
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: visual-test-diffs
          path: testing/reports/visual-results/
          retention-days: 7

      - name: Upload HTML Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: visual-test-report
          path: testing/reports/html/visual-report/
          retention-days: 7
```

### Running Tests in Docker

Visual tests are designed to run in Docker for consistency:

```bash
# Using docker-compose
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
  npm run test:visual

# Update baselines in Docker
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
  npm run test:visual:update
```

### Baseline Storage

Baselines should be:
- ✅ Committed to version control (git)
- ✅ Consistent across environments (Docker ensures this)
- ✅ Updated when UI intentionally changes
- ❌ Not ignored in `.gitignore`
- ❌ Not generated on CI/CD (use committed baselines)

## Troubleshooting

### Tests Failing Locally But Passing in CI

**Cause**: Different rendering environments

**Solution**:
1. Run tests in Docker locally: `./testing/run-tests.sh --suite visual`
2. Ensure fonts are consistent (Docker includes them)
3. Update baselines in Docker if needed

### Fonts Not Rendering Correctly

**Cause**: Fonts not loaded before screenshot

**Solution**:
```typescript
await preparePageForVisualTest(page);
await page.waitForFunction(() => document.fonts.ready);
```

### Animations Causing Flakiness

**Cause**: Animations not disabled

**Solution**:
```typescript
await preparePageForVisualTest(page); // Disables animations automatically
```

### Tests Failing After Dependency Updates

**Cause**: Material UI or other dependency visual changes

**Solution**:
1. Review diffs to understand changes
2. If intentional, update baselines: `npm run test:visual:update`
3. Commit updated baselines

### Different Results on Different Machines

**Cause**: Inconsistent environments

**Solution**: Always run visual tests in Docker:
```bash
./testing/run-tests.sh --suite visual
```

### Baseline Image Mismatch on First Run

**Cause**: No baseline exists yet

**Solution**: First run creates baselines automatically. Review and commit them:
```bash
npm run test:visual
git add testing/visual/baselines/
git commit -m "Add visual regression baselines"
```

### Tests Taking Too Long

**Solutions**:
1. Run specific tests: `npx playwright test --config=visual/playwright.config.ts visual/specs/home.visual.spec.ts`
2. Run single project: `--project=desktop-chrome`
3. Increase workers: `--workers=4`
4. Skip slow tests locally: `test.skip('slow test', ...)`

## Helper Functions Reference

### `preparePageForVisualTest(page)`
Prepares page for stable visual testing:
- Waits for network idle
- Waits for fonts to load
- Disables animations and transitions
- Removes focus rings

### `waitForMuiComponents(page)`
Waits for Material UI components to render:
- Waits for Emotion styles
- Waits for ripple effects

### `setThemeMode(page, mode)`
Sets theme to light or dark mode:
- Emulates color scheme
- Toggles theme if app has theme switcher

### `hideDynamicContent(page)`
Hides common dynamic content:
- Timestamps
- Date/time displays
- Dynamic IDs

### `fillFieldForVisualTest(page, selector, value)`
Fills form field and waits for stabilization:
- Fills field
- Waits for validation

### `clickForVisualTest(page, selector)`
Clicks element and waits for visual changes:
- Clicks element
- Waits for animations
- Waits for network idle

## Test Coverage

Current visual regression test coverage:

### Home Page (`home.visual.spec.ts`)
- ✅ Desktop light mode
- ✅ Desktop dark mode
- ✅ Tablet viewport
- ✅ Mobile viewport
- ✅ Header component
- ✅ Theme toggle
- ✅ Full page scroll
- ✅ Mobile landscape
- ✅ Small mobile device
- ✅ Navigation hover states

### Onboarding Page (`onboarding.visual.spec.ts`)
- ✅ Initial load (desktop, mobile, tablet, dark mode)
- ✅ Empty form validation errors
- ✅ Partially filled form
- ✅ Completely filled valid form
- ✅ Invalid age validation
- ✅ Dropdown interactions (sport, level, training days)
- ✅ Responsive layout (various viewports)
- ✅ Form component states (focused, hover)

### Assessment Form (`assessment.visual.spec.ts`)
- ✅ Stepper navigation (all steps)
- ✅ Stepper on mobile and dark mode
- ✅ All field states (empty, filled)
- ✅ Validation states
- ✅ Responsive design (all viewports)
- ✅ Dark mode variations

### Dashboard (`dashboard.visual.spec.ts`)
- ✅ Main view (desktop, mobile, tablet, dark mode)
- ✅ Full page
- ✅ Navigation states
- ✅ Responsive breakpoints
- ✅ Theme variations (light/dark on desktop/mobile)
- ✅ Interactive elements (theme toggle, buttons)
- ✅ Layout components

## Additional Resources

- [Playwright Documentation](https://playwright.dev/docs/test-snapshots)
- [Material UI Testing](https://mui.com/material-ui/guides/testing/)
- [Visual Regression Testing Best Practices](https://playwright.dev/docs/test-snapshots#best-practices)

## Support

For issues or questions:
1. Check this documentation
2. Review test failures in HTML report
3. Check Playwright documentation
4. Consult the team

---

**Last Updated**: Story 13.9 Implementation
**Maintained By**: Frontend Development Team
