# Visual Regression Tests

## Overview

Visual regression tests detect unintended UI changes across releases by comparing screenshots of the current UI against baseline images.

## Framework

- **Playwright** - Screenshot capture and comparison
- **pixelmatch** - Pixel-level image comparison
- **pngjs** - PNG image processing

## Test Organization

```
visual/
├── specs/
│   ├── login-page.spec.ts
│   ├── dashboard.spec.ts
│   ├── onboarding-form.spec.ts
│   └── assessment-form.spec.ts
├── baselines/
│   ├── login-page/
│   ├── dashboard/
│   ├── onboarding-form/
│   └── assessment-form/
├── diffs/
│   └── (generated on failures)
├── playwright.config.js
└── README.md
```

## Running Visual Tests

**All visual tests:**
```bash
./testing/run-tests.sh --suite visual
```

**Update baselines (after intentional UI changes):**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
    npm run test:visual:update
```

**Specific test:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
    npx playwright test --config=visual/playwright.config.js visual/specs/login-page.spec.ts
```

## Writing Visual Tests

### Basic Visual Test

```typescript
import { test, expect } from '@playwright/test';

test.describe('Login Page Visual Regression', () => {
  test('should match baseline screenshot', async ({ page }) => {
    // Navigate to page
    await page.goto('/login');

    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');

    // Take screenshot and compare
    await expect(page).toHaveScreenshot('login-page.png', {
      maxDiffPixels: 100, // Allow 100 pixels difference
    });
  });

  test('should match baseline for mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto('/login');
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveScreenshot('login-page-mobile.png');
  });
});
```

### Component-Level Screenshots

```typescript
test('should match button component', async ({ page }) => {
  await page.goto('/components');

  // Screenshot specific element
  const button = page.locator('[data-testid="primary-button"]');
  await expect(button).toHaveScreenshot('primary-button.png');
});
```

### Multiple States

```typescript
test.describe('Form States', () => {
  test('empty state', async ({ page }) => {
    await page.goto('/form');
    await expect(page).toHaveScreenshot('form-empty.png');
  });

  test('filled state', async ({ page }) => {
    await page.goto('/form');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await expect(page).toHaveScreenshot('form-filled.png');
  });

  test('error state', async ({ page }) => {
    await page.goto('/form');
    await page.click('button[type="submit"]');
    await expect(page).toHaveScreenshot('form-error.png');
  });
});
```

## Configuration

### Playwright Config (`playwright.config.js`)

```javascript
module.exports = {
  testDir: './visual/specs',
  snapshotDir: './visual/baselines',
  outputDir: './visual/diffs',

  expect: {
    toHaveScreenshot: {
      maxDiffPixels: 100,      // Max pixels that can differ
      threshold: 0.2,           // Pixel color difference threshold (0-1)
      animations: 'disabled',   // Disable animations
    },
  },

  use: {
    baseURL: 'http://proxy:80',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'Desktop Chrome',
      use: { browserName: 'chromium', viewport: { width: 1280, height: 720 } },
    },
    {
      name: 'Mobile Safari',
      use: { browserName: 'webkit', viewport: { width: 375, height: 667 } },
    },
  ],
};
```

## Best Practices

### Stable Screenshots

1. **Disable animations:**
   ```typescript
   await page.goto('/page', { waitUntil: 'networkidle' });
   await page.addStyleTag({ content: '* { animation: none !important; }' });
   ```

2. **Hide dynamic content:**
   ```typescript
   // Hide timestamp or dynamic data
   await page.addStyleTag({ content: '.timestamp { display: none; }' });
   ```

3. **Use consistent viewport sizes:**
   ```typescript
   await page.setViewportSize({ width: 1280, height: 720 });
   ```

4. **Wait for fonts to load:**
   ```typescript
   await page.waitForLoadState('networkidle');
   await page.waitForFunction(() => document.fonts.ready);
   ```

### Masking Dynamic Content

```typescript
test('masked dynamic content', async ({ page }) => {
  await page.goto('/dashboard');

  await expect(page).toHaveScreenshot('dashboard.png', {
    mask: [
      page.locator('.timestamp'),
      page.locator('.user-id'),
      page.locator('.session-info'),
    ],
  });
});
```

### Multiple Viewports

```typescript
const viewports = [
  { width: 1920, height: 1080, name: 'desktop-hd' },
  { width: 1280, height: 720, name: 'desktop' },
  { width: 768, height: 1024, name: 'tablet' },
  { width: 375, height: 667, name: 'mobile' },
];

viewports.forEach(({ width, height, name }) => {
  test(`should match on ${name}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.goto('/page');
    await expect(page).toHaveScreenshot(`page-${name}.png`);
  });
});
```

## Baseline Management

### Creating Baselines

**First run generates baselines:**
```bash
npx playwright test --config=visual/playwright.config.js
```

Baselines are stored in `visual/baselines/`.

### Updating Baselines

**After intentional UI changes:**
```bash
npx playwright test --config=visual/playwright.config.js --update-snapshots
```

**Update specific test:**
```bash
npx playwright test --config=visual/playwright.config.js visual/specs/login-page.spec.ts --update-snapshots
```

### Reviewing Changes

**View diff images:**
```bash
open visual/diffs/login-page-diff.png
```

**Use Playwright trace viewer:**
```bash
npx playwright show-report testing/reports/playwright-report
```

## Handling Failures

### Review Diff

When a visual test fails:

1. **Check the diff image:**
   ```bash
   open visual/diffs/failed-test-diff.png
   ```

2. **Review actual vs expected:**
   - Expected: `visual/baselines/test-name.png`
   - Actual: `visual/diffs/test-name-actual.png`
   - Diff: `visual/diffs/test-name-diff.png`

3. **Determine if change is intentional:**
   - Yes → Update baseline with `--update-snapshots`
   - No → Fix the UI regression

### Common Issues

**Fonts not loading:**
```typescript
await page.waitForFunction(() => document.fonts.ready);
```

**Animations causing flakiness:**
```typescript
await page.addStyleTag({ content: '* { animation: none !important; transition: none !important; }' });
```

**Dynamic content:**
```typescript
// Mask dynamic areas
await expect(page).toHaveScreenshot({
  mask: [page.locator('.dynamic-content')],
});
```

## CI/CD Integration

Visual tests in CI/CD:

1. **Use consistent environment** - Docker ensures same fonts, rendering
2. **Store baselines in git** - Track UI changes in version control
3. **Fail on differences** - Block PRs with visual regressions
4. **Upload diffs as artifacts** - Review changes in CI/CD UI

### GitHub Actions Example

```yaml
- name: Run Visual Tests
  run: ./testing/run-tests.sh --suite visual

- name: Upload Visual Diffs
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: visual-diffs
    path: testing/visual/diffs/
```

## Threshold Configuration

**Per-test threshold:**
```typescript
await expect(page).toHaveScreenshot('page.png', {
  maxDiffPixels: 100,      // Max 100 pixels can differ
  threshold: 0.2,           // Each pixel can differ by 20%
});
```

**Global threshold** in `playwright.config.js`:
```javascript
expect: {
  toHaveScreenshot: {
    maxDiffPixels: 100,
    threshold: 0.2,
  },
},
```

## Implementation Status

✅ **Story 13.9 - COMPLETED**: Full visual regression test suite implemented including:
- ✅ Home/Dashboard page visual tests
- ✅ Onboarding form visual tests (all states and viewports)
- ✅ Assessment form visual tests (stepper, validation, responsiveness)
- ✅ Multi-viewport testing (desktop, tablet, mobile)
- ✅ Dark mode testing
- ✅ Component-level visual tests
- ✅ Helper utilities for stable visual testing

## Comprehensive Guide

For detailed information on writing, running, and maintaining visual regression tests, see:

**[VISUAL_TESTING_GUIDE.md](./VISUAL_TESTING_GUIDE.md)**

This guide includes:
- Quick start instructions
- Writing visual tests
- Baseline management
- Handling test failures
- Best practices
- CI/CD integration
- Troubleshooting
- Helper functions reference
