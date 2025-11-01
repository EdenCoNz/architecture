/**
 * LoginForm Component
 *
 * Feature: 20 - Basic Login Functionality
 * Stories: 20.3 (Collect user name), 20.4 (Collect user email address)
 *
 * Basic login form component that collects user name and email address.
 * Implements validation per API contract and accessibility best practices.
 */

import { useState } from 'react';
import type { FormEvent, ChangeEvent } from 'react';
import { Box, TextField, Typography, Button, CircularProgress } from '@mui/material';
import type { FormErrors } from '../../types';
import { VALIDATION_CONSTRAINTS } from '../../types';

/**
 * Props for LoginForm component
 */
export interface LoginFormProps {
  /** Callback when form is submitted with valid data */
  onSubmit: (name: string, email: string) => Promise<void>;
  /** Whether the form is currently submitting */
  isSubmitting?: boolean;
  /** External error message to display (e.g., from API) */
  externalError?: string;
}

/**
 * Validates email format using HTML5 email validation pattern
 * Matches the backend validation (RFC 5322 email format)
 */
const isValidEmail = (email: string): boolean => {
  // HTML5 email validation pattern - matches backend EmailField validation
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailPattern.test(email);
};

/**
 * Validates the name field per API contract
 */
const validateName = (name: string): string | undefined => {
  const trimmedName = name.trim();

  if (trimmedName.length === 0) {
    return 'Name is required';
  }

  if (trimmedName.length > VALIDATION_CONSTRAINTS.NAME_MAX_LENGTH) {
    return `Name must be ${VALIDATION_CONSTRAINTS.NAME_MAX_LENGTH} characters or less`;
  }

  return undefined;
};

/**
 * Validates the email field per API contract
 */
const validateEmail = (email: string): string | undefined => {
  const trimmedEmail = email.trim();

  if (trimmedEmail.length === 0) {
    return 'Email is required';
  }

  if (trimmedEmail.length > VALIDATION_CONSTRAINTS.EMAIL_MAX_LENGTH) {
    return `Email must be ${VALIDATION_CONSTRAINTS.EMAIL_MAX_LENGTH} characters or less`;
  }

  if (!isValidEmail(trimmedEmail)) {
    return 'Enter a valid email address';
  }

  return undefined;
};

/**
 * LoginForm - Collects user name and email for basic authentication
 *
 * Acceptance Criteria (Story 20.3 - Name field):
 * - When user focuses on name field, shows clear active indication
 * - When user types name, text appears immediately without delay
 * - When name field is empty on submit, shows "Name is required" message
 * - Accepts any text input including special characters and numbers
 *
 * Acceptance Criteria (Story 20.4 - Email field):
 * - When user focuses on email field, shows clear active indication
 * - When user types email, text appears immediately without delay
 * - When email field is empty on submit, shows "Email is required" message
 * - When email format is invalid on submit, shows "Enter a valid email address" message
 */
export function LoginForm({
  onSubmit,
  isSubmitting = false,
  externalError,
}: LoginFormProps) {
  // Form field values
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  // Field touched state - tracks if user has interacted with field
  const [touched, setTouched] = useState({
    name: false,
    email: false,
  });

  // Form validation errors
  const [errors, setErrors] = useState<FormErrors>({});

  /**
   * Handle name field change
   * Acceptance Criteria: Text should appear immediately without delay
   */
  const handleNameChange = (e: ChangeEvent<HTMLInputElement>) => {
    setName(e.target.value);
    // Clear error when user starts typing
    if (errors.name) {
      setErrors((prev) => ({ ...prev, name: undefined }));
    }
  };

  /**
   * Handle email field change
   * Acceptance Criteria: Text should appear immediately without delay
   */
  const handleEmailChange = (e: ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    // Clear error when user starts typing
    if (errors.email) {
      setErrors((prev) => ({ ...prev, email: undefined }));
    }
  };

  /**
   * Handle name field blur - validate on blur for better UX
   */
  const handleNameBlur = () => {
    setTouched((prev) => ({ ...prev, name: true }));
    const error = validateName(name);
    if (error) {
      setErrors((prev) => ({ ...prev, name: error }));
    }
  };

  /**
   * Handle email field blur - validate on blur for better UX
   */
  const handleEmailBlur = () => {
    setTouched((prev) => ({ ...prev, email: true }));
    const error = validateEmail(email);
    if (error) {
      setErrors((prev) => ({ ...prev, email: error }));
    }
  };

  /**
   * Handle form submission
   * Validates all fields and calls onSubmit callback if valid
   */
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Mark all fields as touched
    setTouched({ name: true, email: true });

    // Validate all fields
    const nameError = validateName(name);
    const emailError = validateEmail(email);

    // Update errors state
    const newErrors: FormErrors = {
      name: nameError,
      email: emailError,
    };
    setErrors(newErrors);

    // If any errors, don't submit
    if (nameError || emailError) {
      return;
    }

    // Submit form with trimmed values
    try {
      await onSubmit(name.trim(), email.trim());
    } catch (error) {
      // Error handling is done by parent component
      console.error('Login form submission error:', error);
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      noValidate
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: 3,
        width: '100%',
        maxWidth: 400,
      }}
    >
      {/* External error message (e.g., from API) */}
      {externalError && (
        <Typography
          color="error"
          variant="body2"
          sx={{
            p: 2,
            bgcolor: 'error.lighter',
            borderRadius: 1,
            border: 1,
            borderColor: 'error.main',
          }}
          role="alert"
          aria-live="polite"
        >
          {externalError}
        </Typography>
      )}

      {/* Name field - Story 20.3 */}
      <TextField
        id="login-name"
        name="name"
        label="Name"
        type="text"
        value={name}
        onChange={handleNameChange}
        onBlur={handleNameBlur}
        error={touched.name && Boolean(errors.name)}
        helperText={touched.name && errors.name}
        disabled={isSubmitting}
        required
        fullWidth
        autoComplete="name"
        inputProps={{
          maxLength: VALIDATION_CONSTRAINTS.NAME_MAX_LENGTH,
          'aria-label': 'Your name',
          'aria-required': 'true',
          'aria-invalid': touched.name && Boolean(errors.name),
          'aria-describedby': touched.name && errors.name ? 'name-error' : undefined,
        }}
        FormHelperTextProps={{
          id: 'name-error',
          role: 'alert',
        }}
        sx={{
          '& .MuiInputBase-root': {
            // Acceptance Criteria: Clear indication when field is active
            '&.Mui-focused': {
              '& .MuiOutlinedInput-notchedOutline': {
                borderWidth: 2,
              },
            },
          },
        }}
      />

      {/* Email field - Story 20.4 */}
      <TextField
        id="login-email"
        name="email"
        label="Email"
        type="email"
        value={email}
        onChange={handleEmailChange}
        onBlur={handleEmailBlur}
        error={touched.email && Boolean(errors.email)}
        helperText={touched.email && errors.email}
        disabled={isSubmitting}
        required
        fullWidth
        autoComplete="email"
        inputProps={{
          maxLength: VALIDATION_CONSTRAINTS.EMAIL_MAX_LENGTH,
          'aria-label': 'Your email address',
          'aria-required': 'true',
          'aria-invalid': touched.email && Boolean(errors.email),
          'aria-describedby': touched.email && errors.email ? 'email-error' : undefined,
        }}
        FormHelperTextProps={{
          id: 'email-error',
          role: 'alert',
        }}
        sx={{
          '& .MuiInputBase-root': {
            // Acceptance Criteria: Clear indication when field is active
            '&.Mui-focused': {
              '& .MuiOutlinedInput-notchedOutline': {
                borderWidth: 2,
              },
            },
          },
        }}
      />

      {/* Submit button */}
      <Button
        type="submit"
        variant="contained"
        size="large"
        disabled={isSubmitting}
        fullWidth
        startIcon={isSubmitting ? <CircularProgress size={20} color="inherit" /> : null}
        sx={{ mt: 1 }}
      >
        {isSubmitting ? 'Logging in...' : 'Log In'}
      </Button>
    </Box>
  );
}

export default LoginForm;
