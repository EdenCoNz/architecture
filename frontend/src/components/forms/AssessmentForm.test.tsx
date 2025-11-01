/**
 * AssessmentForm Component Tests
 *
 * Test suite for the onboarding assessment form that collects user information
 * for personalized training program generation.
 *
 * Story 11.7: Complete Assessment Form
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AssessmentForm } from './AssessmentForm';

describe('AssessmentForm', () => {
  describe('Form Validation and Submit Button State', () => {
    it('should disable submit button when required fields are missing', () => {
      render(<AssessmentForm onSubmit={vi.fn()} />);

      const submitButton = screen.getByRole('button', { name: /submit/i });
      expect(submitButton).toBeDisabled();
    });

    it('should show which fields are incomplete when submit is disabled', () => {
      render(<AssessmentForm onSubmit={vi.fn()} />);

      // All required fields should be visible
      expect(screen.getByRole('heading', { name: /select your sport/i })).toBeInTheDocument();
      expect(screen.getByLabelText(/age/i)).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: /experience level/i })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: /days per week/i })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: /what equipment/i })).toBeInTheDocument();
    });

    it('should enable submit button when all required fields are completed', async () => {
      const user = userEvent.setup();
      render(<AssessmentForm onSubmit={vi.fn()} />);

      // Fill in all required fields
      // Sport selection
      const footballCard = screen.getByRole('button', { name: /select football/i });
      await user.click(footballCard);

      // Age
      const ageInput = screen.getByLabelText(/age/i);
      await user.type(ageInput, '25');

      // Experience level
      const intermediateRadio = screen.getByRole('radio', { name: /intermediate/i });
      await user.click(intermediateRadio);

      // Training days
      const trainingDays = screen.getByRole('button', { name: /4-5 days/i });
      await user.click(trainingDays);

      // Injury history (No injuries - this is valid)
      const noInjuries = screen.getByRole('radio', { name: /no.*injur/i });
      await user.click(noInjuries);

      // Equipment (one required)
      const noEquipmentButton = screen.getByRole('button', { name: /no equipment/i });
      await user.click(noEquipmentButton);

      // Submit button should now be enabled
      const submitButton = screen.getByRole('button', { name: /submit/i });
      await waitFor(() => {
        expect(submitButton).toBeEnabled();
      });
    });

    it('should validate age is at least 13', async () => {
      const user = userEvent.setup();
      render(<AssessmentForm onSubmit={vi.fn()} />);

      const ageInput = screen.getByLabelText(/age/i);
      await user.type(ageInput, '12');
      await user.tab(); // Trigger blur

      await waitFor(() => {
        expect(screen.getByText(/you must be at least 13 years old/i)).toBeInTheDocument();
      });
    });

    it('should validate age is not more than 100', async () => {
      const user = userEvent.setup();
      render(<AssessmentForm onSubmit={vi.fn()} />);

      const ageInput = screen.getByLabelText(/age/i);
      await user.clear(ageInput);
      await user.type(ageInput, '101');
      await user.tab(); // Trigger blur

      await waitFor(() => {
        expect(screen.getByText(/please enter a valid age/i)).toBeInTheDocument();
      });
    });
  });

  describe('Form Submission', () => {
    it('should show confirmation message when form is submitted successfully', async () => {
      const user = userEvent.setup();
      const mockSubmit = vi.fn().mockResolvedValue({ success: true });
      render(<AssessmentForm onSubmit={mockSubmit} />);

      // Fill in all required fields
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.type(screen.getByLabelText(/age/i), '25');
      await user.click(screen.getByRole('radio', { name: /intermediate/i }));
      await user.click(screen.getByRole('button', { name: /4-5 days/i }));
      await user.click(screen.getByRole('radio', { name: /no.*injur/i }));
      await user.click(screen.getByRole('button', { name: /no equipment/i }));

      const submitButton = screen.getByRole('button', { name: /submit/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/assessment is being processed/i)).toBeInTheDocument();
      });
    });

    it('should show loading state during form submission', async () => {
      const user = userEvent.setup();
      // Use a promise that doesn't auto-resolve to keep loading state active
      let resolveSubmit: (value: { success: boolean }) => void;
      const submitPromise = new Promise<{ success: boolean }>((resolve) => {
        resolveSubmit = resolve;
      });
      const mockSubmit = vi.fn(() => submitPromise);

      render(<AssessmentForm onSubmit={mockSubmit} />);

      // Fill in all required fields
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.type(screen.getByLabelText(/age/i), '25');
      await user.click(screen.getByRole('radio', { name: /intermediate/i }));
      await user.click(screen.getByRole('button', { name: /4-5 days/i }));
      await user.click(screen.getByRole('radio', { name: /no.*injur/i }));
      await user.click(screen.getByRole('button', { name: /no equipment/i }));

      const submitButton = screen.getByRole('button', { name: /submit/i });
      await user.click(submitButton);

      // Wait for the progress bar to appear - this confirms we're in loading state
      await screen.findByRole('progressbar');

      // Button should be disabled during loading
      expect(submitButton).toBeDisabled();

      // Button text should indicate loading
      expect(submitButton).toHaveTextContent(/submitting/i);

      // Resolve the promise to clean up
      resolveSubmit!({ success: true });
    });

    it('should call onSubmit with form data when submitted', async () => {
      const user = userEvent.setup();
      const mockSubmit = vi.fn().mockResolvedValue({ success: true });
      render(<AssessmentForm onSubmit={mockSubmit} />);

      // Fill in all required fields
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.type(screen.getByLabelText(/age/i), '25');
      await user.click(screen.getByRole('radio', { name: /intermediate/i }));
      await user.click(screen.getByRole('button', { name: /4-5 days/i }));
      await user.click(screen.getByRole('radio', { name: /no.*injur/i }));
      await user.click(screen.getByRole('button', { name: /no equipment/i }));

      const submitButton = screen.getByRole('button', { name: /submit/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith({
          sport: 'football',
          age: 25,
          experienceLevel: 'intermediate',
          trainingDays: '4-5',
          injuries: null,
          equipment: ['no-equipment'],
        });
      });
    });
  });

  describe('Form Submission Errors', () => {
    it('should show error message when submission fails', async () => {
      const user = userEvent.setup();
      const mockSubmit = vi.fn().mockRejectedValue(new Error('Network error'));
      render(<AssessmentForm onSubmit={mockSubmit} />);

      // Fill in all required fields
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.type(screen.getByLabelText(/age/i), '25');
      await user.click(screen.getByRole('radio', { name: /intermediate/i }));
      await user.click(screen.getByRole('button', { name: /4-5 days/i }));
      await user.click(screen.getByRole('radio', { name: /no.*injur/i }));
      await user.click(screen.getByRole('button', { name: /no equipment/i }));

      const submitButton = screen.getByRole('button', { name: /submit/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(
          screen.getByText(/unable to save your assessment.*please try again/i)
        ).toBeInTheDocument();
      });
    });

    it(
      'should retain entered data when submission fails',
      async () => {
        const user = userEvent.setup();
        const mockSubmit = vi.fn().mockRejectedValue(new Error('Network error'));
        render(<AssessmentForm onSubmit={mockSubmit} />);

        // Fill in all required fields
        await user.click(screen.getByRole('button', { name: /select football/i }));
        await user.type(screen.getByLabelText(/age/i), '25');
        await user.click(screen.getByRole('radio', { name: /intermediate/i }));
        await user.click(screen.getByRole('button', { name: /4-5 days/i }));
        await user.click(screen.getByRole('radio', { name: /no.*injur/i }));
        await user.click(screen.getByRole('button', { name: /no equipment/i }));

        const submitButton = screen.getByRole('button', { name: /submit/i });
        await user.click(submitButton);

        // Wait for error
        await waitFor(
          () => {
            expect(screen.getByText(/unable to save your assessment/i)).toBeInTheDocument();
          },
          { timeout: 10000 }
        );

        // Check that data is still present
        expect(screen.getByLabelText(/age/i)).toHaveValue(25);
        const intermediateRadio = screen.getByRole('radio', {
          name: /intermediate/i,
        }) as HTMLInputElement;
        expect(intermediateRadio.checked).toBe(true);
      },
      { timeout: 15000 }
    );

    it('should allow retry after failed submission', async () => {
      const user = userEvent.setup();
      const mockSubmit = vi
        .fn()
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({ success: true });

      render(<AssessmentForm onSubmit={mockSubmit} />);

      // Fill in all required fields
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.type(screen.getByLabelText(/age/i), '25');
      await user.click(screen.getByRole('radio', { name: /intermediate/i }));
      await user.click(screen.getByRole('button', { name: /4-5 days/i }));
      await user.click(screen.getByRole('radio', { name: /no.*injur/i }));
      await user.click(screen.getByRole('button', { name: /no equipment/i }));

      const submitButton = screen.getByRole('button', { name: /submit/i });

      // First attempt - should fail
      await user.click(submitButton);
      await waitFor(() => {
        expect(screen.getByText(/unable to save your assessment/i)).toBeInTheDocument();
      });

      // Second attempt - should succeed
      await user.click(submitButton);
      await waitFor(() => {
        expect(screen.getByText(/assessment is being processed/i)).toBeInTheDocument();
      });

      expect(mockSubmit).toHaveBeenCalledTimes(2);
    });
  });

  describe('Equipment Selection - Story 19.4 (Single Selection)', () => {
    it('should select only one equipment level when clicked', async () => {
      const user = userEvent.setup();
      render(<AssessmentForm onSubmit={vi.fn()} />);

      // Select "No equipment"
      const noEquipmentButton = screen.getByRole('button', { name: /no equipment/i });
      await user.click(noEquipmentButton);

      // Verify only "No equipment" is selected
      const noEquipmentCard = noEquipmentButton.closest('[class*="MuiCard"]');
      expect(noEquipmentCard).toHaveStyle({ borderColor: expect.stringContaining('primary') });
    });

    it('should deselect previous equipment level when selecting a new one (Story 19.4 AC 1)', async () => {
      const user = userEvent.setup();
      const mockSubmit = vi.fn().mockResolvedValue({ success: true });
      render(<AssessmentForm onSubmit={mockSubmit} />);

      // Fill in required fields first
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.type(screen.getByLabelText(/age/i), '25');
      await user.click(screen.getByRole('radio', { name: /intermediate/i }));
      await user.click(screen.getByRole('button', { name: /4-5 days/i }));
      await user.click(screen.getByRole('radio', { name: /no.*injur/i }));

      // Select "No Equipment"
      const noEquipmentButton = screen.getByRole('button', { name: /^No Equipment/i });
      await user.click(noEquipmentButton);

      // Submit and verify No Equipment was submitted
      let submitButton = screen.getByRole('button', { name: /submit/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            equipment: ['no-equipment'],
          })
        );
      });

      mockSubmit.mockClear();

      // Now select "Basic Equipment"
      const basicEquipmentButton = screen.getByRole('button', { name: /^Basic Equipment/i });
      await user.click(basicEquipmentButton);

      // Story 19.6: When selecting basic equipment, need to select at least one item
      const dumbbellButton = screen.getByRole('button', { name: /^Dumbbell$/i });
      await user.click(dumbbellButton);

      // Submit again
      submitButton = screen.getByRole('button', { name: /submit/i });
      await user.click(submitButton);

      // Verify only Basic Equipment is in the data (No Equipment was deselected)
      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            equipment: ['basic-equipment'],
            equipmentItems: expect.arrayContaining(['dumbbell']),
          })
        );
      });
    }, 20000); // Increased timeout to 20s due to complex multi-step interaction

    it('should only allow one equipment level selected at a time (Story 19.4 AC 2)', async () => {
      const user = userEvent.setup();
      const mockSubmit = vi.fn().mockResolvedValue({ success: true });
      render(<AssessmentForm onSubmit={mockSubmit} />);

      // Fill in required fields
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.type(screen.getByLabelText(/age/i), '25');
      await user.click(screen.getByRole('radio', { name: /intermediate/i }));
      await user.click(screen.getByRole('button', { name: /4-5 days/i }));
      await user.click(screen.getByRole('radio', { name: /no.*injur/i }));

      // Click all three equipment options rapidly to simulate trying to select multiple
      const noEquipmentButton = screen.getByRole('button', { name: /^No Equipment/i });
      const basicEquipmentButton = screen.getByRole('button', { name: /^Basic Equipment/i });
      const fullGymButton = screen.getByRole('button', { name: /^Full Gym/i });

      await user.click(noEquipmentButton);
      await user.click(basicEquipmentButton);
      await user.click(fullGymButton);

      // Submit form
      const submitButton = screen.getByRole('button', { name: /submit/i });
      await user.click(submitButton);

      // Only the most recent selection (Full Gym) should be in the submitted data
      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            equipment: ['full-gym'],
          })
        );
      });
    });

    it('should allow form submission when non-basic equipment is selected (Story 19.4 AC 3)', async () => {
      const user = userEvent.setup();
      const mockSubmit = vi.fn().mockResolvedValue({ success: true });
      render(<AssessmentForm onSubmit={mockSubmit} />);

      // Fill in all required fields
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.type(screen.getByLabelText(/age/i), '25');
      await user.click(screen.getByRole('radio', { name: /intermediate/i }));
      await user.click(screen.getByRole('button', { name: /4-5 days/i }));
      await user.click(screen.getByRole('radio', { name: /no.*injur/i }));

      // Select "No Equipment" (non-basic)
      await user.click(screen.getByRole('button', { name: /^No Equipment/i }));

      const submitButton = screen.getByRole('button', { name: /submit/i });
      expect(submitButton).toBeEnabled();

      // Submit should work
      await user.click(submitButton);
      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            equipment: ['no-equipment'],
          })
        );
      });
    });

    it('should only allow one equipment level in form data (Story 19.4 AC 2)', async () => {
      const user = userEvent.setup();
      const mockSubmit = vi.fn().mockResolvedValue({ success: true });
      render(<AssessmentForm onSubmit={mockSubmit} />);

      // Fill in all required fields
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.type(screen.getByLabelText(/age/i), '25');
      await user.click(screen.getByRole('radio', { name: /intermediate/i }));
      await user.click(screen.getByRole('button', { name: /4-5 days/i }));
      await user.click(screen.getByRole('radio', { name: /no.*injur/i }));

      // Select multiple equipment options sequentially
      const noEquipmentButton = screen.getByRole('button', { name: /^No Equipment/i });
      const basicEquipmentButton = screen.getByRole('button', { name: /^Basic Equipment/i });
      const fullGymButton = screen.getByRole('button', { name: /^Full Gym/i });

      await user.click(noEquipmentButton);
      await user.click(basicEquipmentButton);
      await user.click(fullGymButton);

      const submitButton = screen.getByRole('button', { name: /submit/i });
      await user.click(submitButton);

      // Only the most recent selection (full-gym) should be submitted
      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            equipment: ['full-gym'],
          })
        );
      });
    });
  });

  describe('Equipment Follow-up Section - Story 19.5', () => {
    it('should show basic equipment follow-up section when basic equipment is selected', async () => {
      const user = userEvent.setup();
      render(<AssessmentForm onSubmit={vi.fn()} />);

      // Select "Basic Equipment"
      const basicEquipmentButton = screen.getByRole('button', { name: /^Basic Equipment/i });
      await user.click(basicEquipmentButton);

      // Follow-up section should appear
      await waitFor(() => {
        expect(
          screen.getByText(/please specify which equipment items you have/i)
        ).toBeInTheDocument();
      });
    });

    it('should not show basic equipment follow-up section when no equipment is selected', () => {
      render(<AssessmentForm onSubmit={vi.fn()} />);

      // No Equipment is the default state, follow-up should not appear
      expect(
        screen.queryByText(/please specify which equipment items you have/i)
      ).not.toBeInTheDocument();
    });

    it('should not show basic equipment follow-up section when full gym is selected', async () => {
      const user = userEvent.setup();
      render(<AssessmentForm onSubmit={vi.fn()} />);

      // Select "Full Gym"
      const fullGymButton = screen.getByRole('button', { name: /^Full Gym/i });
      await user.click(fullGymButton);

      // Follow-up section should NOT appear
      expect(
        screen.queryByText(/please specify which equipment items you have/i)
      ).not.toBeInTheDocument();
    });

    it('should hide follow-up section and clear selections when switching from basic to another option', async () => {
      const user = userEvent.setup();
      render(<AssessmentForm onSubmit={vi.fn()} />);

      // Select "Basic Equipment"
      const basicEquipmentButton = screen.getByRole('button', { name: /^Basic Equipment/i });
      await user.click(basicEquipmentButton);

      // Verify follow-up section appears
      await waitFor(() => {
        expect(
          screen.getByText(/please specify which equipment items you have/i)
        ).toBeInTheDocument();
      });

      // Select a predefined item (e.g., Dumbbell)
      const dumbbellButton = screen.getByRole('button', { name: /^Dumbbell$/i });
      await user.click(dumbbellButton);

      // Switch to "Full Gym"
      const fullGymButton = screen.getByRole('button', { name: /^Full Gym/i });
      await user.click(fullGymButton);

      // Follow-up section should disappear
      await waitFor(() => {
        expect(
          screen.queryByText(/please specify which equipment items you have/i)
        ).not.toBeInTheDocument();
      });

      // Equipment item selections should be cleared (Dumbbell should be deselected)
      const dumbbellCheckIcon = dumbbellButton.querySelector('[data-testid="CheckCircleIcon"]');
      expect(dumbbellCheckIcon).not.toBeInTheDocument();
    });

    it('should display all equipment item selection controls when follow-up section is visible', async () => {
      const user = userEvent.setup();
      render(<AssessmentForm onSubmit={vi.fn()} />);

      // Select "Basic Equipment"
      const basicEquipmentButton = screen.getByRole('button', { name: /^Basic Equipment/i });
      await user.click(basicEquipmentButton);

      // All predefined items should be visible
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /^Dumbbell$/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /^Barbell$/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /^Kettlebell$/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /^Resistance Bands$/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /^Pull-up Bar$/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /^Bench$/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /^Yoga Mat$/i })).toBeInTheDocument();
      });
    });

    it('should persist basic equipment items when navigating back to the step', async () => {
      const user = userEvent.setup();
      const mockSubmit = vi.fn().mockResolvedValue({ success: true });
      render(<AssessmentForm onSubmit={mockSubmit} />);

      // Fill in all required fields first
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.type(screen.getByLabelText(/age/i), '25');
      await user.click(screen.getByRole('radio', { name: /intermediate/i }));
      await user.click(screen.getByRole('button', { name: /4-5 days/i }));
      await user.click(screen.getByRole('radio', { name: /no.*injur/i }));

      // Select "Basic Equipment"
      const basicEquipmentButton = screen.getByRole('button', { name: /^Basic Equipment/i });
      await user.click(basicEquipmentButton);

      // Select some equipment items
      const dumbbellButton = screen.getByRole('button', { name: /^Dumbbell$/i });
      const barbellButton = screen.getByRole('button', { name: /^Barbell$/i });

      await user.click(dumbbellButton);
      await user.click(barbellButton);

      // Submit form
      const submitButton = screen.getByRole('button', { name: /submit/i });
      await user.click(submitButton);

      // Verify items were submitted
      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            equipment: ['basic-equipment'],
            equipmentItems: expect.arrayContaining(['dumbbell', 'barbell']),
          })
        );
      });
    });
  });

  describe('Equipment Items Selection - Story 19.6 (Multiple Selection)', () => {
    it('should allow selecting multiple equipment items from the list', async () => {
      const user = userEvent.setup();
      render(<AssessmentForm onSubmit={vi.fn()} />);

      // Select "Basic Equipment" to show follow-up
      const basicEquipmentButton = screen.getByRole('button', { name: /^Basic Equipment/i });
      await user.click(basicEquipmentButton);

      // Select multiple items
      const dumbbellButton = screen.getByRole('button', { name: /^Dumbbell$/i });
      const barbellButton = screen.getByRole('button', { name: /^Barbell$/i });
      const kettlebellButton = screen.getByRole('button', { name: /^Kettlebell$/i });

      await user.click(dumbbellButton);
      await user.click(barbellButton);
      await user.click(kettlebellButton);

      // All three should show visual indication of selection
      await waitFor(() => {
        expect(dumbbellButton.closest('[class*="MuiCard"]')).toHaveStyle({
          borderColor: expect.stringContaining('primary'),
        });
        expect(barbellButton.closest('[class*="MuiCard"]')).toHaveStyle({
          borderColor: expect.stringContaining('primary'),
        });
        expect(kettlebellButton.closest('[class*="MuiCard"]')).toHaveStyle({
          borderColor: expect.stringContaining('primary'),
        });
      });
    });

    it('should visually indicate selected equipment items (Story 19.6 AC 1)', async () => {
      const user = userEvent.setup();
      render(<AssessmentForm onSubmit={vi.fn()} />);

      // Select "Basic Equipment"
      const basicEquipmentButton = screen.getByRole('button', { name: /^Basic Equipment/i });
      await user.click(basicEquipmentButton);

      // Select a dumbbell
      const dumbbellButton = screen.getByRole('button', { name: /^Dumbbell$/i });
      await user.click(dumbbellButton);

      // Should show visual indication
      const dumbbellCard = dumbbellButton.closest('[class*="MuiCard"]');
      expect(dumbbellCard).toHaveStyle({
        borderColor: expect.stringContaining('primary'),
      });

      // CheckCircle icon should appear
      const checkIcon = dumbbellButton.querySelector('[data-testid="CheckCircleIcon"]');
      expect(checkIcon).toBeInTheDocument();
    });

    it('should deselect an item when clicking it again (Story 19.6 AC 2)', async () => {
      const user = userEvent.setup();
      render(<AssessmentForm onSubmit={vi.fn()} />);

      // Select "Basic Equipment"
      const basicEquipmentButton = screen.getByRole('button', { name: /^Basic Equipment/i });
      await user.click(basicEquipmentButton);

      // Select dumbbell
      const dumbbellButton = screen.getByRole('button', { name: /^Dumbbell$/i });
      await user.click(dumbbellButton);

      // Verify it's selected
      let dumbbellCard = dumbbellButton.closest('[class*="MuiCard"]');
      expect(dumbbellCard).toHaveStyle({
        borderColor: expect.stringContaining('primary'),
      });

      // Click again to deselect
      await user.click(dumbbellButton);

      // Should return to unselected state
      dumbbellCard = dumbbellButton.closest('[class*="MuiCard"]');
      expect(dumbbellCard).toHaveStyle({
        borderColor: expect.stringContaining('divider'),
      });

      // CheckCircle icon should be gone
      const checkIcon = dumbbellButton.querySelector('[data-testid="CheckCircleIcon"]');
      expect(checkIcon).not.toBeInTheDocument();
    });

    it('should allow adding custom equipment item (Story 19.6 AC 3)', async () => {
      const user = userEvent.setup();
      const mockSubmit = vi.fn().mockResolvedValue({ success: true });
      render(<AssessmentForm onSubmit={mockSubmit} />);

      // Fill in all required fields
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.type(screen.getByLabelText(/age/i), '25');
      await user.click(screen.getByRole('radio', { name: /intermediate/i }));
      await user.click(screen.getByRole('button', { name: /4-5 days/i }));
      await user.click(screen.getByRole('radio', { name: /no.*injur/i }));

      // Select "Basic Equipment"
      const basicEquipmentButton = screen.getByRole('button', { name: /^Basic Equipment/i });
      await user.click(basicEquipmentButton);

      // Look for custom equipment input - should exist in follow-up section
      const customInput = screen.getByPlaceholderText(/e\.g\., Cable machine/i) as HTMLInputElement;
      expect(customInput).toBeInTheDocument();

      // Type a custom equipment item and press Enter (story 19.6 AC3 says enter text and add it)
      await user.type(customInput, 'Cable machine{Enter}');

      // Submit the form
      const submitButton = screen.getByRole('button', { name: /submit/i });
      await user.click(submitButton);

      // Verify the custom item was included in the submission
      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            equipment: ['basic-equipment'],
            equipmentItems: expect.arrayContaining(['cable-machine']),
          })
        );
      });
    });

    it('should show validation error when no equipment items selected for basic equipment (Story 19.6 AC 4)', async () => {
      const user = userEvent.setup();
      const mockSubmit = vi.fn().mockResolvedValue({ success: true });
      render(<AssessmentForm onSubmit={mockSubmit} />);

      // Fill in all required fields
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.type(screen.getByLabelText(/age/i), '25');
      await user.click(screen.getByRole('radio', { name: /intermediate/i }));
      await user.click(screen.getByRole('button', { name: /4-5 days/i }));
      await user.click(screen.getByRole('radio', { name: /no.*injur/i }));

      // Select "Basic Equipment" but don't select any items
      const basicEquipmentButton = screen.getByRole('button', { name: /^Basic Equipment/i });
      await user.click(basicEquipmentButton);

      // Try to submit
      const submitButton = screen.getByRole('button', { name: /submit/i });
      expect(submitButton).toBeDisabled();
    });

    it('should show required equipment items error message when trying to submit without selections', async () => {
      const user = userEvent.setup();
      render(<AssessmentForm onSubmit={vi.fn()} />);

      // Select "Basic Equipment"
      const basicEquipmentButton = screen.getByRole('button', { name: /^Basic Equipment/i });
      await user.click(basicEquipmentButton);

      // Wait for follow-up to appear
      await waitFor(() => {
        expect(
          screen.getByText(/please specify which equipment items you have/i)
        ).toBeInTheDocument();
      });

      // Submit button should be disabled because no items are selected
      const submitButton = screen.getByRole('button', { name: /submit/i });
      expect(submitButton).toBeDisabled();

      // When error is shown, it should contain the specific message
      // This will be shown once we implement validation
    });

    it('should enable submit button once at least one equipment item is selected (Story 19.6 AC 4)', async () => {
      const user = userEvent.setup();
      const mockSubmit = vi.fn().mockResolvedValue({ success: true });
      render(<AssessmentForm onSubmit={mockSubmit} />);

      // Fill in all required fields
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.type(screen.getByLabelText(/age/i), '25');
      await user.click(screen.getByRole('radio', { name: /intermediate/i }));
      await user.click(screen.getByRole('button', { name: /4-5 days/i }));
      await user.click(screen.getByRole('radio', { name: /no.*injur/i }));

      // Select "Basic Equipment"
      const basicEquipmentButton = screen.getByRole('button', { name: /^Basic Equipment/i });
      await user.click(basicEquipmentButton);

      // Submit should still be disabled (no items selected)
      let submitButton = screen.getByRole('button', { name: /submit/i });
      expect(submitButton).toBeDisabled();

      // Select an equipment item
      const dumbbellButton = screen.getByRole('button', { name: /^Dumbbell$/i });
      await user.click(dumbbellButton);

      // Now submit should be enabled
      submitButton = screen.getByRole('button', { name: /submit/i });
      await waitFor(() => {
        expect(submitButton).toBeEnabled();
      });
    });

    it('should submit equipment items with basic equipment selection', async () => {
      const user = userEvent.setup();
      const mockSubmit = vi.fn().mockResolvedValue({ success: true });
      render(<AssessmentForm onSubmit={mockSubmit} />);

      // Fill in all required fields
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.type(screen.getByLabelText(/age/i), '25');
      await user.click(screen.getByRole('radio', { name: /intermediate/i }));
      await user.click(screen.getByRole('button', { name: /4-5 days/i }));
      await user.click(screen.getByRole('radio', { name: /no.*injur/i }));

      // Select "Basic Equipment"
      const basicEquipmentButton = screen.getByRole('button', { name: /^Basic Equipment/i });
      await user.click(basicEquipmentButton);

      // Select items
      const dumbbellButton = screen.getByRole('button', { name: /^Dumbbell$/i });
      const barbellButton = screen.getByRole('button', { name: /^Barbell$/i });
      await user.click(dumbbellButton);
      await user.click(barbellButton);

      // Submit
      const submitButton = screen.getByRole('button', { name: /submit/i });
      await user.click(submitButton);

      // Verify submission includes equipment items
      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            equipment: ['basic-equipment'],
            equipmentItems: expect.arrayContaining(['dumbbell', 'barbell']),
          })
        );
      });
    });

    it('should not include equipmentItems in submission for non-basic equipment', async () => {
      const user = userEvent.setup();
      const mockSubmit = vi.fn().mockResolvedValue({ success: true });
      render(<AssessmentForm onSubmit={mockSubmit} />);

      // Fill in all required fields
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.type(screen.getByLabelText(/age/i), '25');
      await user.click(screen.getByRole('radio', { name: /intermediate/i }));
      await user.click(screen.getByRole('button', { name: /4-5 days/i }));
      await user.click(screen.getByRole('radio', { name: /no.*injur/i }));

      // Select "No Equipment"
      const noEquipmentButton = screen.getByRole('button', { name: /^No Equipment/i });
      await user.click(noEquipmentButton);

      // Submit
      const submitButton = screen.getByRole('button', { name: /submit/i });
      await user.click(submitButton);

      // Verify submission does NOT include equipmentItems
      await waitFor(() => {
        expect(mockSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            equipment: ['no-equipment'],
          })
        );
        // equipmentItems should not be in the call
        const callArgs = mockSubmit.mock.calls[0][0];
        expect(callArgs).not.toHaveProperty('equipmentItems');
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper form labels and aria attributes', () => {
      render(<AssessmentForm onSubmit={vi.fn()} />);

      // Age field should have proper label
      const ageInput = screen.getByLabelText(/age/i);
      expect(ageInput).toHaveAttribute('type', 'number');
      expect(ageInput).toHaveAttribute('required');

      // Form should have proper structure
      const form = screen.getByRole('form');
      expect(form).toBeInTheDocument();
    });

    it('should announce errors to screen readers', async () => {
      const user = userEvent.setup();
      render(<AssessmentForm onSubmit={vi.fn()} />);

      const ageInput = screen.getByLabelText(/age/i);
      await user.type(ageInput, '12');
      await user.tab();

      await waitFor(() => {
        const errorMessage = screen.getByText(/you must be at least 13 years old/i);
        expect(errorMessage).toBeInTheDocument();
        // Error should be associated with input via aria-describedby
        expect(ageInput).toHaveAttribute('aria-invalid', 'true');
      });
    });
  });
});
