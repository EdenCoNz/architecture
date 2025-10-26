# Onboarding Form E2E Tests

**Story 13.6: Test Onboarding Form Completion**

## Overview

This directory contains end-to-end tests for the onboarding assessment form workflow. The tests validate that new users can successfully complete the onboarding process, including multi-step navigation, form validation, and data persistence.

**Note on Routing (Feature #14)**: As of Feature #14, the onboarding form is now the primary entry point of the application, displayed at the root URL (`/`). The legacy `/onboarding` route redirects to `/` for backward compatibility.

## Test Coverage

### Test File: `onboarding-form.spec.ts`

#### 1. Valid Form Completion
Tests that validate successful form completion with valid data:
- ✅ All required fields can be filled with valid data
- ✅ Next button enables only when current step is complete
- ✅ Progress indicator shows all 6 steps correctly
- ✅ Keyboard navigation works throughout the form

#### 2. Invalid Data Validation
Tests that validate form validation and error handling:
- ✅ Age below minimum (13) shows appropriate error
- ✅ Age above maximum (100) shows appropriate error
- ✅ Empty age field shows validation error
- ✅ Next button disabled when step is incomplete
- ✅ Validation errors clear when user corrects input
- ✅ Age validation triggers on blur event

#### 3. Form Submission and Progression
Tests that validate form submission behavior:
- ✅ Form submits successfully with all valid data
- ✅ Successful submission handling (form completion workflow)
- ✅ Submit button disables during submission
- ✅ Loading state displays during submission
- ✅ Form cannot be resubmitted after completion

#### 4. Multi-Step Navigation and Data Preservation
Tests that validate step navigation and data persistence:
- ✅ Sport selection preserved when navigating forward/back
- ✅ Age preserved when navigating forward/back
- ✅ Experience level preserved when navigating forward/back
- ✅ All data preserved throughout entire form navigation
- ✅ Back button shows on all steps except first
- ✅ Form validity maintained during navigation
- ✅ Previously completed steps can be edited

#### 5. Accessibility and User Experience
Tests that validate accessibility and UX:
- ✅ Form has proper ARIA labels
- ✅ Progress indicator visible at all times
- ✅ Current step number displayed in progress indicator
- ✅ Clear field labels and helper text
- ✅ Rapid navigation clicks handled gracefully

#### 6. Edge Cases
Tests that validate boundary conditions:
- ✅ Minimum valid age (13) accepted
- ✅ Maximum valid age (100) accepted
- ✅ Multiple equipment selections allowed
- ✅ Different sport selections (football, cricket) work

## Acceptance Criteria

All tests implement the acceptance criteria from Story 13.6:

1. **Valid Form Completion**: Given the onboarding form loads, when the test fills in all required fields (age, sport, level, training days), then form validation should pass ✅

2. **Invalid Data Validation**: Given invalid data is entered, when the test attempts to submit, then appropriate validation errors should be displayed ✅

3. **Form Submission**: Given all fields are valid, when the form is submitted, then the test should verify progression to the next step ✅

4. **Data Preservation**: Given the onboarding form is multi-step, when the test navigates between steps, then previously entered data should be preserved ✅

## Page Object Model

The tests use the `OnboardingPage` page object model (`testing/e2e/page-objects/OnboardingPage.ts`) which provides:

- **Navigation methods**: `goto()`, `clickNext()`, `clickBack()`, `clickSubmit()`
- **Field interaction methods**: `selectSport()`, `fillAge()`, `selectExperienceLevel()`, etc.
- **Validation methods**: `hasAgeError()`, `hasFormError()`, `hasSuccessMessage()`
- **Verification methods**: `isNextButtonEnabled()`, `getCurrentStep()`, `verifyDataPersistence()`
- **Utility methods**: `fillCompleteForm()`, `submitCompleteForm()`, `checkAccessibility()`

## Running the Tests

### Run all onboarding tests:
```bash
npm run test:e2e:onboarding
```

### Run with headed browser (see the test execute):
```bash
npm run test:e2e:headed -- e2e/specs/onboarding/onboarding-form.spec.ts
```

### Run in debug mode:
```bash
npm run test:e2e:debug -- e2e/specs/onboarding/onboarding-form.spec.ts
```

### Run specific test:
```bash
npx playwright test --config=e2e/playwright.config.ts -g "should allow filling all required fields"
```

### Run in UI mode (interactive):
```bash
npm run ui -- e2e/specs/onboarding/onboarding-form.spec.ts
```

## Test Data

Tests use predefined valid form data:
```typescript
{
  sport: 'football',
  age: 25,
  experienceLevel: 'intermediate',
  trainingDays: '4-5',
  injuries: 'no',
  equipment: ['basic']
}
```

Edge cases tested include:
- Minimum age: 13
- Maximum age: 100
- Multiple equipment selections
- Both sport options (football, cricket)

## Test Results

Test results are generated in multiple formats:
- **HTML Report**: `testing/reports/html/e2e-report/`
- **JSON Report**: `testing/reports/json/e2e-report.json`
- **JUnit XML**: `testing/reports/junit/e2e-results.xml`

View the HTML report:
```bash
npm run report
```

## Browser Coverage

Tests run on multiple browsers:
- ✅ Chromium (Desktop Chrome)
- ✅ Firefox
- ✅ WebKit (Safari)
- ✅ Mobile Chrome (Pixel 5)
- ✅ Mobile Safari (iPhone 12)
- ✅ Tablet (iPad Pro)

## Dependencies

The tests require:
- **Playwright**: ^1.41.0
- **@playwright/test**: ^1.41.0
- **TypeScript**: ^5.3.3
- **Node.js**: >=20.0.0

## Test Structure

Each test follows the Arrange-Act-Assert pattern:

```typescript
test('should do something', async ({ page }) => {
  // Arrange: Set up test data and navigate to page
  const onboardingPage = new OnboardingPage(page);
  await onboardingPage.goto();

  // Act: Perform the action being tested
  await onboardingPage.selectSport('football');
  await onboardingPage.clickNext();

  // Assert: Verify the expected outcome
  expect(await onboardingPage.isOnStep(2)).toBe(true);
});
```

## Troubleshooting

### Tests fail with timeout errors
- Increase timeout in `playwright.config.ts`
- Check if frontend/backend services are running
- Use headed mode to see what's happening

### Form elements not found
- Check if selectors in OnboardingPage match actual implementation
- Use debug mode to inspect the page
- Verify form is fully loaded before interactions

### Data preservation tests fail
- Check if form state management is working correctly
- Verify localStorage or state management implementation
- Use browser DevTools to inspect state

## Future Enhancements

Potential additions to the test suite:
- Visual regression tests for form appearance
- Performance tests for form submission
- Network error handling tests
- Cross-browser compatibility screenshots
- Accessibility audit with axe-core

## Related Stories

- **Story 11.7**: Complete Assessment Form (frontend implementation)
- **Story 11.8**: Progress Through Assessment Steps (multi-step implementation)
- **Story 13.1**: Set Up Test Execution Environment
- **Story 13.2**: Configure Test Data Isolation
- **Story 13.7**: Test Assessment Data Submission (backend tests)
- **Story 13.8**: Test Profile Creation from Assessment (backend tests)
