# Visual Regression Testing - Quick Reference

## Quick Commands

### Run Tests
```bash
# All visual tests
./testing/run-tests.sh --suite visual

# Specific page
npx playwright test --config=visual/playwright.config.ts visual/specs/home.visual.spec.ts

# Specific browser
npx playwright test --config=visual/playwright.config.ts --project=desktop-chrome

# Debug mode
npx playwright test --config=visual/playwright.config.ts --debug

# UI mode (interactive)
npx playwright test --config=visual/playwright.config.ts --ui
```

### Update Baselines
```bash
# Update all baselines
npm run test:visual:update

# Update specific test
npx playwright test --config=visual/playwright.config.ts \
  visual/specs/home.visual.spec.ts --update-snapshots
```

### View Reports
```bash
# HTML report
npx playwright show-report ../reports/html/visual-report

# JSON report
cat ../reports/json/visual-report.json
```

## Test Structure Template

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

  test('should match baseline - desktop', async ({ page }) => {
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('your-page-desktop.png', {
      maxDiffPixels: 100,
    });
  });

  test('should match baseline - mobile', async ({ page }) => {
    await page.setViewportSize(VIEWPORTS.mobile);
    await preparePageForVisualTest(page);
    await waitForMuiComponents(page);

    await expect(page).toHaveScreenshot('your-page-mobile.png');
  });
});
```

## Helper Functions

```typescript
// Prepare page for stable screenshot
await preparePageForVisualTest(page);

// Wait for Material UI components
await waitForMuiComponents(page);

// Set theme mode
await setThemeMode(page, 'dark');

// Fill form field with stabilization
await fillFieldForVisualTest(page, '[name="email"]', 'test@example.com');

// Click and wait for changes
await clickForVisualTest(page, 'button[type="submit"]');

// Hide dynamic content
await hideDynamicContent(page);
```

## Viewports

```typescript
VIEWPORTS.desktop        // 1280x720
VIEWPORTS.desktopHd      // 1920x1080
VIEWPORTS.tablet         // 768x1024
VIEWPORTS.tabletLandscape // 1024x768
VIEWPORTS.mobile         // 375x667
VIEWPORTS.mobileLandscape // 667x375
VIEWPORTS.mobileSmall    // 320x568
```

## Screenshot Options

```typescript
await expect(page).toHaveScreenshot('page.png', {
  maxDiffPixels: 100,        // Max pixels that can differ
  threshold: 0.2,            // Pixel color threshold (0-1)
  fullPage: true,            // Capture full scrolling page
  mask: [                    // Hide dynamic elements
    page.locator('.timestamp'),
    page.locator('.user-id'),
  ],
});
```

## Common Patterns

### Multiple Viewports
```typescript
const viewports = [
  { size: VIEWPORTS.desktop, name: 'desktop' },
  { size: VIEWPORTS.tablet, name: 'tablet' },
  { size: VIEWPORTS.mobile, name: 'mobile' },
];

viewports.forEach(({ size, name }) => {
  test(`should match on ${name}`, async ({ page }) => {
    await page.setViewportSize(size);
    await preparePageForVisualTest(page);
    await expect(page).toHaveScreenshot(`page-${name}.png`);
  });
});
```

### Dark Mode Testing
```typescript
test('should match baseline - dark mode', async ({ page }) => {
  await page.goto('/page');
  await setThemeMode(page, 'dark');
  await preparePageForVisualTest(page);
  await expect(page).toHaveScreenshot('page-dark.png');
});
```

### Component Screenshot
```typescript
test('should match button component', async ({ page }) => {
  await page.goto('/page');
  await preparePageForVisualTest(page);

  const button = page.locator('[data-testid="submit-button"]');
  await expect(button).toHaveScreenshot('submit-button.png');
});
```

### Form States
```typescript
test.describe('Form States', () => {
  test('empty state', async ({ page }) => {
    await page.goto('/form');
    await preparePageForVisualTest(page);
    await expect(page).toHaveScreenshot('form-empty.png');
  });

  test('filled state', async ({ page }) => {
    await page.goto('/form');
    await fillFieldForVisualTest(page, '[name="email"]', 'test@example.com');
    await expect(page).toHaveScreenshot('form-filled.png');
  });

  test('error state', async ({ page }) => {
    await page.goto('/form');
    await clickForVisualTest(page, 'button[type="submit"]');
    await page.waitForTimeout(300);
    await expect(page).toHaveScreenshot('form-error.png');
  });
});
```

## Troubleshooting

### Tests Failing Randomly
- Ensure `preparePageForVisualTest()` is called
- Check if animations are disabled
- Verify fonts are loaded

### Different Results on Different Machines
- Run tests in Docker: `./testing/run-tests.sh --suite visual`
- Ensure baselines were created in Docker

### After UI Changes
1. Review diffs in HTML report
2. If intentional: `npm run test:visual:update`
3. Commit updated baselines

### Test Taking Too Long
- Run specific tests instead of all
- Use `--project=desktop-chrome` for one browser
- Increase `--workers=4`

## File Locations

```
testing/visual/
├── playwright.config.ts       # Configuration
├── tsconfig.json             # TypeScript config
├── specs/                    # Test files
│   ├── home.visual.spec.ts
│   ├── onboarding.visual.spec.ts
│   ├── assessment.visual.spec.ts
│   └── dashboard.visual.spec.ts
├── helpers/                  # Utilities
│   └── visual-test-helpers.ts
├── baselines/                # Baseline images (auto-generated)
├── VISUAL_TESTING_GUIDE.md  # Full documentation
└── QUICK_REFERENCE.md       # This file
```

## CI/CD

Visual tests run automatically in CI/CD:
```bash
./testing/run-tests.sh --suite visual
```

On failure, view diff artifacts in CI/CD output.

## More Information

See [VISUAL_TESTING_GUIDE.md](./VISUAL_TESTING_GUIDE.md) for:
- Detailed explanations
- Best practices
- Advanced techniques
- Complete troubleshooting guide
