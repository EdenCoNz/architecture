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
      expect(screen.getByRole('heading', { name: /equipment/i })).toBeInTheDocument();
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

      // Equipment (at least one)
      const noEquipment = screen.getByRole('button', { name: /no equipment/i });
      await user.click(noEquipment);

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
      const mockSubmit = vi.fn(
        () =>
          new Promise<{ success: boolean }>((resolve) =>
            setTimeout(() => resolve({ success: true }), 100)
          )
      );
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

      // Button should show loading state
      expect(submitButton).toBeDisabled();
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
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
          equipment: ['none'],
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
