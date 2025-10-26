/**
 * OnboardingPage Page Object Model
 *
 * Encapsulates interactions with the onboarding assessment form.
 * Supports both single-step and multi-step form interactions.
 *
 * Story 13.6: Test Onboarding Form Completion
 *
 * This page object provides methods for:
 * - Navigating to onboarding page
 * - Filling in form fields (sport, age, experience, training days, injuries, equipment)
 * - Validating form state and errors
 * - Submitting the form
 * - Navigating between steps (for multi-step form)
 */

import { Page, Locator, expect } from '@playwright/test';

export interface OnboardingFormData {
  sport: 'football' | 'cricket';
  age: number;
  experienceLevel: 'beginner' | 'intermediate' | 'advanced';
  trainingDays: '2-3' | '4-5' | '6-7';
  injuries: 'no' | 'yes';
  equipment: ('none' | 'basic' | 'full-gym')[];
}

export class OnboardingPage {
  readonly page: Page;

  // Navigation
  readonly url = '/onboarding';

  // Sport Selection (Step 1)
  readonly footballCard: Locator;
  readonly cricketCard: Locator;
  readonly sportErrorMessage: Locator;

  // Age Input (Step 2)
  readonly ageInput: Locator;
  readonly ageErrorMessage: Locator;

  // Experience Level (Step 3)
  readonly beginnerRadio: Locator;
  readonly intermediateRadio: Locator;
  readonly advancedRadio: Locator;
  readonly experienceLevelErrorMessage: Locator;

  // Training Days (Step 4)
  readonly trainingDays23Card: Locator;
  readonly trainingDays45Card: Locator;
  readonly trainingDays67Card: Locator;

  // Injury History (Step 5)
  readonly noInjuriesRadio: Locator;
  readonly yesInjuriesRadio: Locator;

  // Equipment (Step 6)
  readonly noEquipmentCard: Locator;
  readonly basicEquipmentCard: Locator;
  readonly fullGymCard: Locator;

  // Navigation buttons
  readonly nextButton: Locator;
  readonly backButton: Locator;
  readonly submitButton: Locator;

  // Progress indicator
  readonly progressIndicator: Locator;
  readonly stepIndicator: Locator;

  // Form-level elements
  readonly form: Locator;
  readonly successMessage: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;

    // Sport Selection
    this.footballCard = page.getByRole('button', { name: /select football/i });
    this.cricketCard = page.getByRole('button', { name: /select cricket/i });
    this.sportErrorMessage = page.getByRole('alert').filter({ hasText: /sport/i });

    // Age Input
    this.ageInput = page.getByLabel(/age/i);
    this.ageErrorMessage = page.getByText(/age is required|must be at least|please enter a valid age/i);

    // Experience Level
    this.beginnerRadio = page.getByRole('radio', { name: /beginner/i });
    this.intermediateRadio = page.getByRole('radio', { name: /intermediate/i });
    this.advancedRadio = page.getByRole('radio', { name: /advanced/i });
    this.experienceLevelErrorMessage = page.getByRole('alert').filter({ hasText: /experience/i });

    // Training Days
    this.trainingDays23Card = page.getByRole('button', { name: /2-3 days per week/i });
    this.trainingDays45Card = page.getByRole('button', { name: /4-5 days per week/i });
    this.trainingDays67Card = page.getByRole('button', { name: /6-7 days per week/i });

    // Injury History
    this.noInjuriesRadio = page.getByRole('radio', { name: /no injuries/i });
    this.yesInjuriesRadio = page.getByRole('radio', { name: /i have injury history/i });

    // Equipment
    this.noEquipmentCard = page.getByRole('button', { name: /no equipment/i });
    this.basicEquipmentCard = page.getByRole('button', { name: /basic equipment/i });
    this.fullGymCard = page.getByRole('button', { name: /full gym/i });

    // Navigation buttons
    this.nextButton = page.getByRole('button', { name: /^next$/i });
    this.backButton = page.getByRole('button', { name: /back/i });
    this.submitButton = page.getByRole('button', { name: /submit assessment/i });

    // Progress indicator
    this.progressIndicator = page.getByRole('progressbar', { name: /assessment progress/i });
    this.stepIndicator = page.getByText(/step \d+ of \d+/i);

    // Form-level elements
    this.form = page.getByRole('form', { name: /assessment form/i });
    this.successMessage = page.getByRole('alert').filter({ hasText: /success|processing/i });
    this.errorMessage = page.getByRole('alert').filter({ hasText: /error|unable|failed/i });
  }

  // Navigation methods
  async goto() {
    await this.page.goto(this.url);
    await this.waitForLoad();
  }

  async waitForLoad() {
    await this.form.waitFor({ state: 'visible' });
  }

  // Sport selection methods
  async selectSport(sport: 'football' | 'cricket') {
    const card = sport === 'football' ? this.footballCard : this.cricketCard;
    await card.click();
    // Wait for selection to be registered
    await this.page.waitForTimeout(100);
  }

  async isSportSelected(sport: 'football' | 'cricket'): Promise<boolean> {
    const card = sport === 'football' ? this.footballCard : this.cricketCard;
    // Check if card has primary color border (selected state)
    const cardElement = await card.locator('..').locator('..');
    const borderColor = await cardElement.evaluate((el) => {
      return window.getComputedStyle(el).borderColor;
    });
    // Selected cards have a colored border (not transparent)
    return !borderColor.includes('rgba(0, 0, 0, 0)') && borderColor !== 'transparent';
  }

  // Age input methods
  async fillAge(age: number) {
    await this.ageInput.clear();
    await this.ageInput.fill(age.toString());
    // Trigger blur event to show validation
    await this.ageInput.blur();
  }

  async getAgeValue(): Promise<number | null> {
    const value = await this.ageInput.inputValue();
    return value ? parseInt(value, 10) : null;
  }

  // Experience level methods
  async selectExperienceLevel(level: 'beginner' | 'intermediate' | 'advanced') {
    const radio = level === 'beginner'
      ? this.beginnerRadio
      : level === 'intermediate'
      ? this.intermediateRadio
      : this.advancedRadio;
    await radio.click();
  }

  async getSelectedExperienceLevel(): Promise<string | null> {
    if (await this.beginnerRadio.isChecked()) return 'beginner';
    if (await this.intermediateRadio.isChecked()) return 'intermediate';
    if (await this.advancedRadio.isChecked()) return 'advanced';
    return null;
  }

  // Training days methods
  async selectTrainingDays(days: '2-3' | '4-5' | '6-7') {
    const card = days === '2-3'
      ? this.trainingDays23Card
      : days === '4-5'
      ? this.trainingDays45Card
      : this.trainingDays67Card;
    await card.click();
    await this.page.waitForTimeout(100);
  }

  // Injury history methods
  async selectInjuryHistory(hasInjuries: boolean) {
    const radio = hasInjuries ? this.yesInjuriesRadio : this.noInjuriesRadio;
    await radio.click();
  }

  async getSelectedInjuryHistory(): Promise<boolean | null> {
    if (await this.noInjuriesRadio.isChecked()) return false;
    if (await this.yesInjuriesRadio.isChecked()) return true;
    return null;
  }

  // Equipment methods
  async selectEquipment(equipment: ('none' | 'basic' | 'full-gym')[]) {
    // First, clear any existing selections by clicking them again
    const allCards = [this.noEquipmentCard, this.basicEquipmentCard, this.fullGymCard];
    for (const card of allCards) {
      const isSelected = await this.isEquipmentSelected(card);
      if (isSelected) {
        await card.click();
        await this.page.waitForTimeout(100);
      }
    }

    // Then select the desired equipment
    for (const item of equipment) {
      const card = item === 'none'
        ? this.noEquipmentCard
        : item === 'basic'
        ? this.basicEquipmentCard
        : this.fullGymCard;
      await card.click();
      await this.page.waitForTimeout(100);
    }
  }

  async isEquipmentSelected(card: Locator): Promise<boolean> {
    const cardElement = await card.locator('..').locator('..');
    const borderColor = await cardElement.evaluate((el) => {
      return window.getComputedStyle(el).borderColor;
    });
    return !borderColor.includes('rgba(0, 0, 0, 0)') && borderColor !== 'transparent';
  }

  // Navigation methods
  async clickNext() {
    await this.nextButton.click();
    // Wait for step transition
    await this.page.waitForTimeout(300);
  }

  async clickBack() {
    await this.backButton.click();
    // Wait for step transition
    await this.page.waitForTimeout(300);
  }

  async clickSubmit() {
    await this.submitButton.click();
  }

  async isNextButtonEnabled(): Promise<boolean> {
    return await this.nextButton.isEnabled();
  }

  async isNextButtonDisabled(): Promise<boolean> {
    return await this.nextButton.isDisabled();
  }

  async isSubmitButtonEnabled(): Promise<boolean> {
    return await this.submitButton.isEnabled();
  }

  // Progress indicator methods
  async getCurrentStep(): Promise<number> {
    const text = await this.stepIndicator.textContent();
    const match = text?.match(/step (\d+) of \d+/i);
    return match ? parseInt(match[1], 10) : 0;
  }

  async getTotalSteps(): Promise<number> {
    const text = await this.stepIndicator.textContent();
    const match = text?.match(/step \d+ of (\d+)/i);
    return match ? parseInt(match[1], 10) : 0;
  }

  async isOnStep(stepNumber: number): Promise<boolean> {
    const currentStep = await this.getCurrentStep();
    return currentStep === stepNumber;
  }

  async isFinalStep(): Promise<boolean> {
    const text = await this.stepIndicator.textContent();
    return text?.toLowerCase().includes('final step') ?? false;
  }

  // Validation methods
  async hasAgeError(): Promise<boolean> {
    return await this.ageErrorMessage.isVisible().catch(() => false);
  }

  async getAgeError(): Promise<string | null> {
    if (await this.hasAgeError()) {
      return await this.ageErrorMessage.textContent();
    }
    return null;
  }

  async hasFormError(): Promise<boolean> {
    return await this.errorMessage.isVisible().catch(() => false);
  }

  async hasSuccessMessage(): Promise<boolean> {
    return await this.successMessage.isVisible().catch(() => false);
  }

  // Complete form methods
  async fillCompleteForm(data: OnboardingFormData) {
    // Step 1: Sport Selection
    await this.selectSport(data.sport);
    await this.clickNext();

    // Step 2: Age
    await this.fillAge(data.age);
    await this.clickNext();

    // Step 3: Experience Level
    await this.selectExperienceLevel(data.experienceLevel);
    await this.clickNext();

    // Step 4: Training Days
    await this.selectTrainingDays(data.trainingDays);
    await this.clickNext();

    // Step 5: Injury History
    await this.selectInjuryHistory(data.injuries === 'yes');
    await this.clickNext();

    // Step 6: Equipment
    await this.selectEquipment(data.equipment);
  }

  async submitCompleteForm(data: OnboardingFormData) {
    await this.fillCompleteForm(data);
    await this.clickSubmit();
  }

  // Wait for successful submission
  async waitForSuccessfulSubmission(redirectUrl: string = '/') {
    await this.page.waitForURL(`**${redirectUrl}`, {
      timeout: 10000,
      waitUntil: 'networkidle'
    });
  }

  // Verify data persistence when navigating between steps
  async verifyDataPersistence(data: Partial<OnboardingFormData>): Promise<boolean> {
    try {
      if (data.sport) {
        const isSportSelected = await this.isSportSelected(data.sport);
        if (!isSportSelected) return false;
      }

      if (data.age) {
        const ageValue = await this.getAgeValue();
        if (ageValue !== data.age) return false;
      }

      if (data.experienceLevel) {
        const level = await this.getSelectedExperienceLevel();
        if (level !== data.experienceLevel) return false;
      }

      if (data.injuries !== undefined) {
        const injuries = await this.getSelectedInjuryHistory();
        const expected = data.injuries === 'yes';
        if (injuries !== expected) return false;
      }

      return true;
    } catch (error) {
      return false;
    }
  }

  // Accessibility checks
  async checkAccessibility(): Promise<{
    formAccessible: boolean;
    allFieldsAccessible: boolean;
    navigationAccessible: boolean;
  }> {
    const formHasLabel = await this.form.getAttribute('aria-label') !== null;

    const ageHasLabel = await this.ageInput.getAttribute('aria-label') !== null ||
                        await this.ageInput.getAttribute('id') !== null;

    const nextHasLabel = await this.nextButton.getAttribute('aria-label') !== null ||
                         await this.nextButton.textContent() !== null;

    return {
      formAccessible: formHasLabel,
      allFieldsAccessible: ageHasLabel,
      navigationAccessible: nextHasLabel,
    };
  }
}
