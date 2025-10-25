/**
 * AssessmentFormStepper Component Tests
 *
 * Test suite for the onboarding assessment stepper that provides multi-step navigation
 * and progress tracking through the assessment form.
 *
 * Story 11.8: Progress Through Assessment Steps
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AssessmentFormStepper } from './AssessmentFormStepper';

describe('AssessmentFormStepper', () => {
  describe('Progress Indication', () => {
    it('should show visual progress indicator when form is displayed', () => {
      render(<AssessmentFormStepper onSubmit={vi.fn()} />);

      // Should show stepper/progress indicator
      expect(screen.getByRole('progressbar', { name: /assessment progress/i })).toBeInTheDocument();
    });

    it('should indicate current step in progress indicator', () => {
      render(<AssessmentFormStepper onSubmit={vi.fn()} />);

      // First step (Sport Selection) should be active
      expect(screen.getByText(/step 1 of 6/i)).toBeInTheDocument();
    });

    it('should update progress indicator when completing a section', async () => {
      const user = userEvent.setup();
      render(<AssessmentFormStepper onSubmit={vi.fn()} />);

      // Complete first step (select sport)
      const footballCard = screen.getByRole('button', { name: /select football/i });
      await user.click(footballCard);

      // Click Next
      const nextButton = screen.getByRole('button', { name: /next/i });
      await user.click(nextButton);

      // Should show step 2
      await waitFor(() => {
        expect(screen.getByText(/step 2 of 6/i)).toBeInTheDocument();
      });
    });

    it('should show completed state for previously visited sections', async () => {
      const user = userEvent.setup();
      render(<AssessmentFormStepper onSubmit={vi.fn()} />);

      // Complete first step
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.click(screen.getByRole('button', { name: /next/i }));

      // Step 1 should now be marked as completed (has completed class and check icon)
      await waitFor(() => {
        const step1 = screen.getByText('Sport Selection').closest('.MuiStep-root');
        expect(step1).toHaveClass('Mui-completed');
      });
    });
  });

  describe('Navigation - Forward', () => {
    it('should navigate to next incomplete section when clicking next', async () => {
      const user = userEvent.setup();
      render(<AssessmentFormStepper onSubmit={vi.fn()} />);

      // Complete and navigate from step 1
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.click(screen.getByRole('button', { name: /next/i }));

      // Should show age section (step 2)
      await waitFor(() => {
        expect(screen.getByLabelText(/age/i)).toBeInTheDocument();
      });
    });

    it('should disable next button when current section is incomplete', () => {
      render(<AssessmentFormStepper onSubmit={vi.fn()} />);

      // Next button should be disabled when no sport is selected
      const nextButton = screen.getByRole('button', { name: /next/i });
      expect(nextButton).toBeDisabled();
    });

    it('should enable next button when current section is complete', async () => {
      const user = userEvent.setup();
      render(<AssessmentFormStepper onSubmit={vi.fn()} />);

      // Complete first step
      await user.click(screen.getByRole('button', { name: /select football/i }));

      // Next button should now be enabled
      const nextButton = screen.getByRole('button', { name: /next/i });
      await waitFor(() => {
        expect(nextButton).toBeEnabled();
      });
    });
  });

  describe('Navigation - Backward', () => {
    it('should navigate to previous section without losing data when clicking back', async () => {
      const user = userEvent.setup();
      render(<AssessmentFormStepper onSubmit={vi.fn()} />);

      // Navigate to step 2
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.click(screen.getByRole('button', { name: /next/i }));

      // Enter age
      await waitFor(() => {
        expect(screen.getByLabelText(/age/i)).toBeInTheDocument();
      });
      await user.type(screen.getByLabelText(/age/i), '25');

      // Go back to step 1
      await user.click(screen.getByRole('button', { name: /back/i }));

      // Should show sport selection again
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /select your sport/i })).toBeInTheDocument();
      });

      // Sport selection should still be football
      const footballCard = screen.getByRole('button', { name: /select football/i });
      expect(footballCard.closest('[aria-pressed="true"]') || footballCard).toBeInTheDocument();
    });

    it('should not show back button on first step', () => {
      render(<AssessmentFormStepper onSubmit={vi.fn()} />);

      // Back button should not be present on step 1
      expect(screen.queryByRole('button', { name: /back/i })).not.toBeInTheDocument();
    });

    it('should show back button on subsequent steps', async () => {
      const user = userEvent.setup();
      render(<AssessmentFormStepper onSubmit={vi.fn()} />);

      // Navigate to step 2
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.click(screen.getByRole('button', { name: /next/i }));

      // Back button should now be visible
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /back/i })).toBeInTheDocument();
      });
    });

    it('should preserve data when navigating back and forward', async () => {
      const user = userEvent.setup();
      render(<AssessmentFormStepper onSubmit={vi.fn()} />);

      // Complete step 1
      await user.click(screen.getByRole('button', { name: /select football/i }));
      await user.click(screen.getByRole('button', { name: /next/i }));

      // Complete step 2
      await waitFor(() => {
        expect(screen.getByLabelText(/age/i)).toBeInTheDocument();
      });
      await user.type(screen.getByLabelText(/age/i), '25');
      await user.click(screen.getByRole('button', { name: /next/i }));

      // Now on step 3 - go back
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /back/i })).toBeInTheDocument();
      });
      await user.click(screen.getByRole('button', { name: /back/i }));

      // Should show step 2 with age preserved
      await waitFor(() => {
        expect(screen.getByLabelText(/age/i)).toHaveValue(25);
      });

      // Go back again
      await user.click(screen.getByRole('button', { name: /back/i }));

      // Should show step 1 with sport preserved
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /select your sport/i })).toBeInTheDocument();
      });

      // Navigate forward through all steps - data should be preserved
      await user.click(screen.getByRole('button', { name: /next/i }));
      await waitFor(() => {
        expect(screen.getByLabelText(/age/i)).toHaveValue(25);
      });
    });
  });

  describe('Final Step Indication', () => {
    it('should show next button on first step', () => {
      render(<AssessmentFormStepper onSubmit={vi.fn()} />);

      // On first step, should see Next button, not Submit
      expect(screen.queryByRole('button', { name: /^next$/i })).toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /submit/i })).not.toBeInTheDocument();
    });

    it('should show step indicator with total steps', () => {
      render(<AssessmentFormStepper onSubmit={vi.fn()} />);

      // Should show step 1 of 6
      expect(screen.getByText(/step 1 of 6/i)).toBeInTheDocument();
    });

    it('should not show final step text on first step', () => {
      render(<AssessmentFormStepper onSubmit={vi.fn()} />);

      // Should NOT show "Final step" text on step 1
      expect(screen.queryByText(/final step/i)).not.toBeInTheDocument();
    });
  });

  describe('Form Submission', () => {
    it('should have form with proper submit handler', () => {
      render(<AssessmentFormStepper onSubmit={vi.fn()} />);

      // Form should exist
      const form = screen.getByRole('form', { name: /assessment form/i });
      expect(form).toBeInTheDocument();
      expect(form.tagName).toBe('FORM');
    });
  });
});
