/**
 * LoginForm Component Tests
 *
 * Feature: 20 - Basic Login Functionality
 * Stories: 20.3 (Collect user name), 20.4 (Collect user email address)
 *
 * Tests for email and name field validation, accessibility, and user interactions.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';
import { VALIDATION_CONSTRAINTS } from '../../types';

describe('LoginForm', () => {
  let mockOnSubmit: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnSubmit = vi.fn().mockResolvedValue(undefined);
  });

  // ========================================================================
  // Story 20.3: Collect user name - Acceptance Criteria Tests
  // ========================================================================

  describe('Story 20.3: Name field', () => {
    it('should show clear indication when name field is focused', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const nameField = screen.getByLabelText(/your name/i);

      // Field should not be focused initially
      expect(nameField).not.toHaveFocus();

      // Focus the field
      await user.click(nameField);

      // Field should now be focused
      expect(nameField).toHaveFocus();
    });

    it('should display text immediately as user types in name field', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const nameField = screen.getByLabelText(/your name/i) as HTMLInputElement;

      // Type into name field
      await user.type(nameField, 'John Doe');

      // Text should appear immediately
      expect(nameField.value).toBe('John Doe');
    });

    it('should show "Name is required" message when name field is empty on submit', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const submitButton = screen.getByRole('button', { name: /log in/i });

      // Submit form without entering name
      await user.click(submitButton);

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/name is required/i)).toBeInTheDocument();
      });

      // Should not call onSubmit
      expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    it('should accept any text input including special characters and numbers', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const nameField = screen.getByLabelText(/your name/i) as HTMLInputElement;
      const emailField = screen.getByLabelText(/your email address/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      // Enter name with special characters and numbers
      const specialName = "O'Brien-Smith 123 Ⅲ";
      await user.type(nameField, specialName);
      await user.type(emailField, 'test@example.com');

      // Submit form
      await user.click(submitButton);

      // Should accept the special characters
      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(specialName, 'test@example.com');
      });
    });

    it('should reject name that exceeds max length', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const nameField = screen.getByLabelText(/your name/i) as HTMLInputElement;

      // Try to enter name exceeding max length
      // Note: The HTML maxLength attribute will prevent typing beyond limit
      const longName = 'a'.repeat(VALIDATION_CONSTRAINTS.NAME_MAX_LENGTH + 1);
      await user.type(nameField, longName);

      // Field should be limited to max length by HTML attribute
      expect(nameField.value.length).toBe(VALIDATION_CONSTRAINTS.NAME_MAX_LENGTH);
    });
  });

  // ========================================================================
  // Story 20.4: Collect user email address - Acceptance Criteria Tests
  // ========================================================================

  describe('Story 20.4: Email field', () => {
    it('should show clear indication when email field is focused', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const emailField = screen.getByLabelText(/your email address/i);

      // Field should not be focused initially
      expect(emailField).not.toHaveFocus();

      // Focus the field
      await user.click(emailField);

      // Field should now be focused
      expect(emailField).toHaveFocus();
    });

    it('should display text immediately as user types in email field', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const emailField = screen.getByLabelText(/your email address/i) as HTMLInputElement;

      // Type into email field
      await user.type(emailField, 'john@example.com');

      // Text should appear immediately
      expect(emailField.value).toBe('john@example.com');
    });

    it('should show "Email is required" message when email field is empty on submit', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const nameField = screen.getByLabelText(/your name/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      // Enter name but leave email empty
      await user.type(nameField, 'John Doe');
      await user.click(submitButton);

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      });

      // Should not call onSubmit
      expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    it('should show "Enter a valid email address" message when email format is invalid', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const nameField = screen.getByLabelText(/your name/i);
      const emailField = screen.getByLabelText(/your email address/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      // Enter invalid email formats
      const invalidEmails = [
        'notanemail',
        'missing@domain',
        '@nodomain.com',
        'no@domain',
        'spaces in@email.com',
      ];

      for (const invalidEmail of invalidEmails) {
        await user.clear(nameField);
        await user.clear(emailField);
        await user.type(nameField, 'John Doe');
        await user.type(emailField, invalidEmail);
        await user.click(submitButton);

        // Should show error message
        await waitFor(() => {
          expect(screen.getByText(/enter a valid email address/i)).toBeInTheDocument();
        });

        // Should not call onSubmit
        expect(mockOnSubmit).not.toHaveBeenCalled();

        mockOnSubmit.mockClear();
      }
    });

    it('should accept valid email formats', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const nameField = screen.getByLabelText(/your name/i);
      const emailField = screen.getByLabelText(/your email address/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      const validEmails = [
        'simple@example.com',
        'user.name@example.com',
        'user+tag@example.co.uk',
        'user_name@example.com',
        'user123@test-domain.com',
      ];

      for (const validEmail of validEmails) {
        await user.clear(nameField);
        await user.clear(emailField);
        await user.type(nameField, 'John Doe');
        await user.type(emailField, validEmail);
        await user.click(submitButton);

        // Should call onSubmit
        await waitFor(() => {
          expect(mockOnSubmit).toHaveBeenCalledWith('John Doe', validEmail);
        });

        mockOnSubmit.mockClear();
      }
    });

    it('should reject email that exceeds max length', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const emailField = screen.getByLabelText(/your email address/i) as HTMLInputElement;

      // Try to enter email exceeding max length (254 chars)
      // Note: The HTML maxLength attribute will prevent typing beyond limit
      const longEmail = 'a'.repeat(VALIDATION_CONSTRAINTS.EMAIL_MAX_LENGTH + 1);
      await user.type(emailField, longEmail);

      // Field should be limited to max length by HTML attribute
      expect(emailField.value.length).toBe(VALIDATION_CONSTRAINTS.EMAIL_MAX_LENGTH);
    });
  });

  // ========================================================================
  // Form Submission Tests
  // ========================================================================

  describe('Form submission', () => {
    it('should submit form with valid name and email', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const nameField = screen.getByLabelText(/your name/i);
      const emailField = screen.getByLabelText(/your email address/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      // Fill in valid data
      await user.type(nameField, 'Jane Smith');
      await user.type(emailField, 'jane.smith@example.com');
      await user.click(submitButton);

      // Should call onSubmit with trimmed values
      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith('Jane Smith', 'jane.smith@example.com');
      });
    });

    it('should trim whitespace from name and email before submitting', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const nameField = screen.getByLabelText(/your name/i);
      const emailField = screen.getByLabelText(/your email address/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      // Fill in data with extra whitespace
      await user.type(nameField, '  Jane Smith  ');
      await user.type(emailField, '  jane@example.com  ');
      await user.click(submitButton);

      // Should call onSubmit with trimmed values
      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith('Jane Smith', 'jane@example.com');
      });
    });

    it('should show loading state during submission', async () => {
      render(<LoginForm onSubmit={mockOnSubmit} isSubmitting={true} />);

      const submitButton = screen.getByRole('button', { name: /logging in/i });

      // Should show loading text when isSubmitting is true
      expect(submitButton).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
    });

    it('should disable fields during submission', async () => {
      render(<LoginForm onSubmit={mockOnSubmit} isSubmitting={true} />);

      const nameField = screen.getByLabelText(/your name/i);
      const emailField = screen.getByLabelText(/your email address/i);

      // Fields should be disabled
      expect(nameField).toBeDisabled();
      expect(emailField).toBeDisabled();
    });

    it('should display external error message', () => {
      const errorMessage = 'Invalid credentials';
      render(<LoginForm onSubmit={mockOnSubmit} externalError={errorMessage} />);

      // Should display error message
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
      expect(screen.getByRole('alert')).toHaveTextContent(errorMessage);
    });
  });

  // ========================================================================
  // Validation Behavior Tests
  // ========================================================================

  describe('Validation behavior', () => {
    it('should validate on blur after field is touched', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const emailField = screen.getByLabelText(/your email address/i);

      // Focus and blur without entering value
      await user.click(emailField);
      await user.tab(); // blur

      // Should show error after blur
      await waitFor(() => {
        expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      });
    });

    it('should clear errors when user starts typing', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const emailField = screen.getByLabelText(/your email address/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      // Submit to trigger error
      await user.click(submitButton);

      // Should show error
      await waitFor(() => {
        expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      });

      // Start typing
      await user.type(emailField, 'test@example.com');

      // Error should be cleared
      await waitFor(() => {
        expect(screen.queryByText(/email is required/i)).not.toBeInTheDocument();
      });
    });

    it('should show both field errors when both are invalid', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const submitButton = screen.getByRole('button', { name: /log in/i });

      // Submit without filling any fields
      await user.click(submitButton);

      // Should show both errors
      await waitFor(() => {
        expect(screen.getByText(/name is required/i)).toBeInTheDocument();
        expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      });
    });
  });

  // ========================================================================
  // Accessibility Tests
  // ========================================================================

  describe('Accessibility', () => {
    it('should have proper ARIA labels for form fields', () => {
      render(<LoginForm onSubmit={mockOnSubmit} />);

      // Name field
      const nameField = screen.getByLabelText(/your name/i);
      expect(nameField).toHaveAttribute('aria-label', 'Your name');
      expect(nameField).toHaveAttribute('aria-required', 'true');

      // Email field
      const emailField = screen.getByLabelText(/your email address/i);
      expect(emailField).toHaveAttribute('aria-label', 'Your email address');
      expect(emailField).toHaveAttribute('aria-required', 'true');
    });

    it('should have proper ARIA attributes when field has error', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const emailField = screen.getByLabelText(/your email address/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      // Submit to trigger error
      await user.click(submitButton);

      // Should have aria-invalid and aria-describedby
      await waitFor(() => {
        expect(emailField).toHaveAttribute('aria-invalid', 'true');
        expect(emailField).toHaveAttribute('aria-describedby', 'email-error');
      });
    });

    it('should have role="alert" on error messages', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const submitButton = screen.getByRole('button', { name: /log in/i });

      // Submit to trigger errors
      await user.click(submitButton);

      // Error messages should have role="alert"
      await waitFor(() => {
        const alerts = screen.getAllByRole('alert');
        expect(alerts.length).toBeGreaterThan(0);
      });
    });

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup();
      render(<LoginForm onSubmit={mockOnSubmit} />);

      const nameField = screen.getByLabelText(/your name/i);
      const emailField = screen.getByLabelText(/your email address/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      // Focus name field
      await user.tab();
      expect(nameField).toHaveFocus();

      // Tab to email field
      await user.tab();
      expect(emailField).toHaveFocus();

      // Tab to submit button
      await user.tab();
      expect(submitButton).toHaveFocus();
    });
  });
});
