/**
 * Onboarding Form E2E Tests
 *
 * Tests validate the complete onboarding form workflow including:
 * - Filling all required fields with valid data
 * - Form validation with invalid data
 * - Form submission and progression
 * - Multi-step navigation and data preservation
 * - Accessibility compliance
 *
 * Story 13.6: Test Onboarding Form Completion
 *
 * Acceptance Criteria:
 * 1. Form with all required fields should pass validation
 * 2. Invalid data should display appropriate validation errors
 * 3. Valid form submission should progress to next step
 * 4. Navigation between steps should preserve previously entered data
 */

import { test, expect } from '@playwright/test';
import { OnboardingPage, type OnboardingFormData } from '../../page-objects/OnboardingPage';

test.describe('Onboarding Form Completion', () => {
  let onboardingPage: OnboardingPage;

  // Valid test data
  const validFormData: OnboardingFormData = {
    sport: 'football',
    age: 25,
    experienceLevel: 'intermediate',
    trainingDays: '4-5',
    injuries: 'no',
    equipment: ['basic'],
  };

  test.beforeEach(async ({ page }) => {
    onboardingPage = new OnboardingPage(page);
    await onboardingPage.goto();
  });

  /**
   * Acceptance Criteria 1: Valid Form Completion
   * Given the onboarding form loads, when the test fills in all required fields
   * (age, sport, level, training days), then form validation should pass
   */
  test.describe('Valid Form Completion', () => {
    test('should allow filling all required fields with valid data', async () => {
      // Step 1: Select sport
      await onboardingPage.selectSport(validFormData.sport);

      // Verify sport is selected
      const isSportSelected = await onboardingPage.isSportSelected(validFormData.sport);
      expect(isSportSelected).toBe(true);

      // Next button should be enabled
      expect(await onboardingPage.isNextButtonEnabled()).toBe(true);
      await onboardingPage.clickNext();

      // Step 2: Fill age
      await onboardingPage.fillAge(validFormData.age);

      // Verify age is filled correctly
      const ageValue = await onboardingPage.getAgeValue();
      expect(ageValue).toBe(validFormData.age);

      // No validation errors should appear
      expect(await onboardingPage.hasAgeError()).toBe(false);

      // Next button should be enabled
      expect(await onboardingPage.isNextButtonEnabled()).toBe(true);
      await onboardingPage.clickNext();

      // Step 3: Select experience level
      await onboardingPage.selectExperienceLevel(validFormData.experienceLevel);

      // Verify experience level is selected
      const selectedLevel = await onboardingPage.getSelectedExperienceLevel();
      expect(selectedLevel).toBe(validFormData.experienceLevel);

      // Next button should be enabled
      expect(await onboardingPage.isNextButtonEnabled()).toBe(true);
      await onboardingPage.clickNext();

      // Step 4: Select training days
      await onboardingPage.selectTrainingDays(validFormData.trainingDays);

      // Next button should be enabled
      expect(await onboardingPage.isNextButtonEnabled()).toBe(true);
      await onboardingPage.clickNext();

      // Step 5: Select injury history
      await onboardingPage.selectInjuryHistory(validFormData.injuries === 'yes');

      // Verify injury history is selected
      const selectedInjuries = await onboardingPage.getSelectedInjuryHistory();
      expect(selectedInjuries).toBe(validFormData.injuries === 'yes');

      // Next button should be enabled
      expect(await onboardingPage.isNextButtonEnabled()).toBe(true);
      await onboardingPage.clickNext();

      // Step 6: Select equipment
      await onboardingPage.selectEquipment(validFormData.equipment);

      // Submit button should be enabled when all fields are valid
      expect(await onboardingPage.isSubmitButtonEnabled()).toBe(true);
    });

    test('should enable next button only when current step is complete', async () => {
      // Step 1: Next should be disabled initially
      expect(await onboardingPage.isNextButtonDisabled()).toBe(true);

      // After selecting sport, next should be enabled
      await onboardingPage.selectSport('football');
      expect(await onboardingPage.isNextButtonEnabled()).toBe(true);

      // Move to step 2
      await onboardingPage.clickNext();

      // Next should be disabled initially on step 2
      expect(await onboardingPage.isNextButtonDisabled()).toBe(true);

      // After filling age, next should be enabled
      await onboardingPage.fillAge(25);
      expect(await onboardingPage.isNextButtonEnabled()).toBe(true);
    });

    test('should show progress through all 6 steps', async () => {
      // Verify total steps
      const totalSteps = await onboardingPage.getTotalSteps();
      expect(totalSteps).toBe(6);

      // Start on step 1
      expect(await onboardingPage.isOnStep(1)).toBe(true);

      // Complete each step and verify progression
      await onboardingPage.selectSport('football');
      await onboardingPage.clickNext();
      expect(await onboardingPage.isOnStep(2)).toBe(true);

      await onboardingPage.fillAge(25);
      await onboardingPage.clickNext();
      expect(await onboardingPage.isOnStep(3)).toBe(true);

      await onboardingPage.selectExperienceLevel('intermediate');
      await onboardingPage.clickNext();
      expect(await onboardingPage.isOnStep(4)).toBe(true);

      await onboardingPage.selectTrainingDays('4-5');
      await onboardingPage.clickNext();
      expect(await onboardingPage.isOnStep(5)).toBe(true);

      await onboardingPage.selectInjuryHistory(false);
      await onboardingPage.clickNext();
      expect(await onboardingPage.isOnStep(6)).toBe(true);

      // Final step should be indicated
      expect(await onboardingPage.isFinalStep()).toBe(true);
    });

    test('should allow keyboard navigation through form fields', async ({ page }) => {
      // Start at first field - should be able to navigate with keyboard
      await page.keyboard.press('Tab');

      // Should be able to interact with focused element
      await page.keyboard.press('Enter'); // Select first sport option

      // Form should respond to keyboard inputs
      const hasProgressIndicator = await onboardingPage.progressIndicator.isVisible();
      expect(hasProgressIndicator).toBe(true);
    });
  });

  /**
   * Acceptance Criteria 2: Invalid Data Validation
   * Given invalid data is entered, when the test attempts to submit,
   * then appropriate validation errors should be displayed
   */
  test.describe('Invalid Data Validation', () => {
    test('should show validation error for age below minimum (13)', async () => {
      // Navigate to age step
      await onboardingPage.selectSport('football');
      await onboardingPage.clickNext();

      // Enter invalid age (below 13)
      await onboardingPage.fillAge(10);

      // Should show validation error
      expect(await onboardingPage.hasAgeError()).toBe(true);

      const errorMessage = await onboardingPage.getAgeError();
      expect(errorMessage).toMatch(/must be at least 13/i);

      // Next button should be disabled
      expect(await onboardingPage.isNextButtonDisabled()).toBe(true);
    });

    test('should show validation error for age above maximum (100)', async () => {
      // Navigate to age step
      await onboardingPage.selectSport('football');
      await onboardingPage.clickNext();

      // Enter invalid age (above 100)
      await onboardingPage.fillAge(105);

      // Should show validation error
      expect(await onboardingPage.hasAgeError()).toBe(true);

      const errorMessage = await onboardingPage.getAgeError();
      expect(errorMessage).toMatch(/please enter a valid age/i);

      // Next button should be disabled
      expect(await onboardingPage.isNextButtonDisabled()).toBe(true);
    });

    test('should show validation error for empty age field', async () => {
      // Navigate to age step
      await onboardingPage.selectSport('football');
      await onboardingPage.clickNext();

      // Fill age then clear it
      await onboardingPage.fillAge(25);
      await onboardingPage.ageInput.clear();
      await onboardingPage.ageInput.blur();

      // Should show validation error
      expect(await onboardingPage.hasAgeError()).toBe(true);

      // Next button should be disabled
      expect(await onboardingPage.isNextButtonDisabled()).toBe(true);
    });

    test('should prevent proceeding to next step when current step is incomplete', async () => {
      // On step 1, don't select sport
      expect(await onboardingPage.isNextButtonDisabled()).toBe(true);

      // Select sport to enable next
      await onboardingPage.selectSport('cricket');
      expect(await onboardingPage.isNextButtonEnabled()).toBe(true);

      // Move to step 2
      await onboardingPage.clickNext();

      // Don't fill age - next should be disabled
      expect(await onboardingPage.isNextButtonDisabled()).toBe(true);
    });

    test('should clear validation error when user corrects invalid input', async () => {
      // Navigate to age step
      await onboardingPage.selectSport('football');
      await onboardingPage.clickNext();

      // Enter invalid age
      await onboardingPage.fillAge(10);
      expect(await onboardingPage.hasAgeError()).toBe(true);

      // Correct the age
      await onboardingPage.fillAge(25);

      // Error should clear
      expect(await onboardingPage.hasAgeError()).toBe(false);

      // Next button should be enabled
      expect(await onboardingPage.isNextButtonEnabled()).toBe(true);
    });

    test('should validate age field on blur event', async () => {
      // Navigate to age step
      await onboardingPage.selectSport('football');
      await onboardingPage.clickNext();

      // Enter invalid age and trigger blur
      await onboardingPage.ageInput.fill('10');
      await onboardingPage.ageInput.blur();

      // Should show validation error after blur
      expect(await onboardingPage.hasAgeError()).toBe(true);
    });
  });

  /**
   * Acceptance Criteria 3: Form Submission and Progression
   * Given all fields are valid, when the form is submitted,
   * then the test should verify progression to the next step
   */
  test.describe('Form Submission and Progression', () => {
    test('should successfully submit form with all valid data', async ({ page }) => {
      // Fill complete form
      await onboardingPage.fillCompleteForm(validFormData);

      // Submit the form
      await onboardingPage.clickSubmit();

      // Should show success message or redirect
      const hasSuccess = await onboardingPage.hasSuccessMessage().catch(() => false);
      const hasRedirected = page.url() !== `${page.url().split('/')[0]}//${page.url().split('/')[2]}/onboarding`;

      // Either success message appears or redirect happens
      expect(hasSuccess || hasRedirected).toBe(true);
    });

    test('should redirect to home page after successful submission', async ({ page }) => {
      // Fill and submit complete form
      await onboardingPage.submitCompleteForm(validFormData);

      // Wait for redirect
      await onboardingPage.waitForSuccessfulSubmission('/');

      // Verify redirected to home page
      expect(page.url()).toContain('/');
      expect(page.url()).not.toContain('/onboarding');
    });

    test('should disable submit button while form is submitting', async () => {
      // Fill complete form
      await onboardingPage.fillCompleteForm(validFormData);

      // Verify submit button is enabled before submission
      expect(await onboardingPage.isSubmitButtonEnabled()).toBe(true);

      // Click submit
      await onboardingPage.clickSubmit();

      // Button should be disabled during submission (if we can catch it)
      // or success message should appear
      const isDisabled = await onboardingPage.submitButton.isDisabled().catch(() => false);
      const hasSuccess = await onboardingPage.hasSuccessMessage().catch(() => false);

      // Either button is disabled or success is shown
      expect(isDisabled || hasSuccess).toBe(true);
    });

    test('should show loading state during form submission', async () => {
      // Fill complete form
      await onboardingPage.fillCompleteForm(validFormData);

      // Submit the form
      await onboardingPage.clickSubmit();

      // Should show loading indicator or success message quickly
      const submitButtonText = await onboardingPage.submitButton.textContent();
      const hasLoadingState = submitButtonText?.toLowerCase().includes('submitting');
      const hasSuccess = await onboardingPage.hasSuccessMessage().catch(() => false);

      // Should show some feedback (loading or success)
      expect(hasLoadingState || hasSuccess).toBe(true);
    });

    test('should not allow form resubmission after successful submission', async ({ page }) => {
      // Fill and submit form
      await onboardingPage.submitCompleteForm(validFormData);

      // Wait for redirect
      await onboardingPage.waitForSuccessfulSubmission('/');

      // Try to navigate back to onboarding
      await page.goto('/onboarding');

      // Should either redirect away or show completion message
      const isOnOnboarding = page.url().includes('/onboarding');

      // User should not be able to access onboarding after completion
      // (implementation may vary - redirect or show message)
      expect(isOnOnboarding).toBe(false);
    });
  });

  /**
   * Acceptance Criteria 4: Multi-Step Navigation and Data Preservation
   * Given the onboarding form is multi-step, when the test navigates between steps,
   * then previously entered data should be preserved
   */
  test.describe('Multi-Step Navigation and Data Preservation', () => {
    test('should preserve sport selection when navigating forward and back', async () => {
      // Step 1: Select sport
      await onboardingPage.selectSport('football');
      const initialSelection = await onboardingPage.isSportSelected('football');
      expect(initialSelection).toBe(true);

      // Navigate forward
      await onboardingPage.clickNext();
      await onboardingPage.fillAge(25);
      await onboardingPage.clickNext();

      // Navigate back to step 1
      await onboardingPage.clickBack();
      await onboardingPage.clickBack();

      // Sport should still be selected
      const preservedSelection = await onboardingPage.isSportSelected('football');
      expect(preservedSelection).toBe(true);
    });

    test('should preserve age when navigating forward and back', async () => {
      // Navigate to age step
      await onboardingPage.selectSport('football');
      await onboardingPage.clickNext();

      // Fill age
      await onboardingPage.fillAge(30);
      const initialAge = await onboardingPage.getAgeValue();
      expect(initialAge).toBe(30);

      // Navigate forward then back
      await onboardingPage.clickNext();
      await onboardingPage.selectExperienceLevel('advanced');
      await onboardingPage.clickNext();

      // Navigate back to age
      await onboardingPage.clickBack();
      await onboardingPage.clickBack();

      // Age should be preserved
      const preservedAge = await onboardingPage.getAgeValue();
      expect(preservedAge).toBe(30);
    });

    test('should preserve experience level when navigating forward and back', async () => {
      // Navigate to experience step
      await onboardingPage.selectSport('cricket');
      await onboardingPage.clickNext();
      await onboardingPage.fillAge(28);
      await onboardingPage.clickNext();

      // Select experience level
      await onboardingPage.selectExperienceLevel('beginner');
      const initialLevel = await onboardingPage.getSelectedExperienceLevel();
      expect(initialLevel).toBe('beginner');

      // Navigate forward then back
      await onboardingPage.clickNext();
      await onboardingPage.clickBack();

      // Experience level should be preserved
      const preservedLevel = await onboardingPage.getSelectedExperienceLevel();
      expect(preservedLevel).toBe('beginner');
    });

    test('should preserve all data when navigating through entire form', async () => {
      const testData: OnboardingFormData = {
        sport: 'cricket',
        age: 35,
        experienceLevel: 'advanced',
        trainingDays: '6-7',
        injuries: 'yes',
        equipment: ['full-gym'],
      };

      // Fill entire form
      await onboardingPage.fillCompleteForm(testData);

      // Navigate back to beginning
      await onboardingPage.clickBack(); // From step 6 to 5
      await onboardingPage.clickBack(); // From step 5 to 4
      await onboardingPage.clickBack(); // From step 4 to 3
      await onboardingPage.clickBack(); // From step 3 to 2
      await onboardingPage.clickBack(); // From step 2 to 1

      // Verify step 1 data is preserved
      expect(await onboardingPage.isSportSelected(testData.sport)).toBe(true);

      // Navigate forward and verify each step
      await onboardingPage.clickNext();
      expect(await onboardingPage.getAgeValue()).toBe(testData.age);

      await onboardingPage.clickNext();
      expect(await onboardingPage.getSelectedExperienceLevel()).toBe(testData.experienceLevel);

      // All data should be preserved throughout navigation
      expect(await onboardingPage.verifyDataPersistence(testData)).toBe(true);
    });

    test('should show back button on all steps except the first', async () => {
      // Step 1: No back button
      expect(await onboardingPage.backButton.isVisible()).toBe(false);

      // Navigate to step 2
      await onboardingPage.selectSport('football');
      await onboardingPage.clickNext();

      // Step 2: Back button should be visible
      expect(await onboardingPage.backButton.isVisible()).toBe(true);

      // Continue to verify back button remains on all subsequent steps
      await onboardingPage.fillAge(25);
      await onboardingPage.clickNext();
      expect(await onboardingPage.backButton.isVisible()).toBe(true);
    });

    test('should maintain form validity when navigating back and forth', async () => {
      // Fill form up to step 3
      await onboardingPage.selectSport('football');
      await onboardingPage.clickNext();
      await onboardingPage.fillAge(25);
      await onboardingPage.clickNext();
      await onboardingPage.selectExperienceLevel('intermediate');

      // Next should be enabled
      expect(await onboardingPage.isNextButtonEnabled()).toBe(true);

      // Go back to step 2
      await onboardingPage.clickBack();

      // Age should still be valid, next should be enabled
      expect(await onboardingPage.hasAgeError()).toBe(false);
      expect(await onboardingPage.isNextButtonEnabled()).toBe(true);

      // Go back to step 1
      await onboardingPage.clickBack();

      // Sport should still be selected, next should be enabled
      expect(await onboardingPage.isNextButtonEnabled()).toBe(true);
    });

    test('should allow editing previously completed steps', async () => {
      // Complete first two steps
      await onboardingPage.selectSport('football');
      await onboardingPage.clickNext();
      await onboardingPage.fillAge(25);
      await onboardingPage.clickNext();

      // Go back and change sport
      await onboardingPage.clickBack();
      await onboardingPage.clickBack();
      await onboardingPage.selectSport('cricket');

      // Navigate forward - should show updated sport
      await onboardingPage.clickNext();

      // Age should still be preserved
      expect(await onboardingPage.getAgeValue()).toBe(25);

      // Navigate back to verify sport changed
      await onboardingPage.clickBack();
      expect(await onboardingPage.isSportSelected('cricket')).toBe(true);
    });
  });

  /**
   * Additional Tests: Accessibility and Edge Cases
   */
  test.describe('Accessibility and User Experience', () => {
    test('should have accessible form with proper ARIA labels', async () => {
      const accessibility = await onboardingPage.checkAccessibility();

      expect(accessibility.formAccessible).toBe(true);
      expect(accessibility.navigationAccessible).toBe(true);
    });

    test('should show progress indicator at all times', async () => {
      // Progress indicator should be visible on every step
      expect(await onboardingPage.progressIndicator.isVisible()).toBe(true);

      await onboardingPage.selectSport('football');
      await onboardingPage.clickNext();
      expect(await onboardingPage.progressIndicator.isVisible()).toBe(true);

      await onboardingPage.fillAge(25);
      await onboardingPage.clickNext();
      expect(await onboardingPage.progressIndicator.isVisible()).toBe(true);
    });

    test('should show current step number in progress indicator', async () => {
      // Step 1
      expect(await onboardingPage.getCurrentStep()).toBe(1);

      // Navigate to step 2
      await onboardingPage.selectSport('football');
      await onboardingPage.clickNext();
      expect(await onboardingPage.getCurrentStep()).toBe(2);

      // Navigate to step 3
      await onboardingPage.fillAge(25);
      await onboardingPage.clickNext();
      expect(await onboardingPage.getCurrentStep()).toBe(3);
    });

    test('should provide clear field labels and helper text', async () => {
      // Navigate to age field
      await onboardingPage.selectSport('football');
      await onboardingPage.clickNext();

      // Age field should have label
      const ageLabel = await onboardingPage.ageInput.getAttribute('aria-label') ||
                        await onboardingPage.page.locator('label[for="age"]').textContent();
      expect(ageLabel).toBeTruthy();

      // Should show helper text
      const helperText = await onboardingPage.page.getByText(/enter your age|13-100 years/i).isVisible();
      expect(helperText).toBe(true);
    });

    test('should handle rapid navigation clicks gracefully', async () => {
      await onboardingPage.selectSport('football');

      // Rapidly click next multiple times
      await onboardingPage.nextButton.click({ clickCount: 3, delay: 50 });

      // Should only advance one step at a time
      const currentStep = await onboardingPage.getCurrentStep();
      expect(currentStep).toBe(2);
    });
  });

  /**
   * Edge Cases and Error Handling
   */
  test.describe('Edge Cases', () => {
    test('should handle minimum valid age (13)', async () => {
      await onboardingPage.selectSport('football');
      await onboardingPage.clickNext();

      // Minimum valid age
      await onboardingPage.fillAge(13);

      // Should not show error
      expect(await onboardingPage.hasAgeError()).toBe(false);

      // Next should be enabled
      expect(await onboardingPage.isNextButtonEnabled()).toBe(true);
    });

    test('should handle maximum valid age (100)', async () => {
      await onboardingPage.selectSport('football');
      await onboardingPage.clickNext();

      // Maximum valid age
      await onboardingPage.fillAge(100);

      // Should not show error
      expect(await onboardingPage.hasAgeError()).toBe(false);

      // Next should be enabled
      expect(await onboardingPage.isNextButtonEnabled()).toBe(true);
    });

    test('should handle multiple equipment selections', async () => {
      // Navigate to equipment step
      await onboardingPage.fillCompleteForm({
        sport: 'football',
        age: 25,
        experienceLevel: 'intermediate',
        trainingDays: '4-5',
        injuries: 'no',
        equipment: ['none'], // Will be replaced
      });

      // Select multiple equipment items
      await onboardingPage.selectEquipment(['basic', 'full-gym']);

      // Submit button should be enabled with multiple selections
      expect(await onboardingPage.isSubmitButtonEnabled()).toBe(true);
    });

    test('should complete form with different sport selection (cricket)', async () => {
      const cricketData: OnboardingFormData = {
        sport: 'cricket',
        age: 22,
        experienceLevel: 'beginner',
        trainingDays: '2-3',
        injuries: 'no',
        equipment: ['none'],
      };

      // Fill and submit with cricket
      await onboardingPage.fillCompleteForm(cricketData);

      // Submit button should be enabled
      expect(await onboardingPage.isSubmitButtonEnabled()).toBe(true);
    });
  });
});
