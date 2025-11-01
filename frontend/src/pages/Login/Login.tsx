/**
 * Login Page Component
 *
 * Feature: 20 - Basic Login Functionality
 * Stories: 20.3 (Collect user name), 20.4 (Collect user email address), 20.5 (Submit login information), 20.9 (Handle login errors gracefully)
 *
 * Main login page that provides a simple authentication interface.
 * Users can log in with just their name and email (no password required).
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Container, Typography, Paper, Alert } from '@mui/material';
import { LoginForm } from '../../components/forms';
import { submitBasicLogin, ApiError } from '../../services/api';

/**
 * Login Page - Provides basic authentication interface
 *
 * This component:
 * - Displays the login form
 * - Handles form submission to the backend API
 * - Manages loading and error states
 * - Stores JWT tokens on successful login
 * - Redirects to home page after successful login
 */
export function Login() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Handle login form submission
   * Calls the backend API using the centralized API service and handles success/error responses
   *
   * Acceptance Criteria (Story 20.5):
   * - AC1: When both fields filled and submitted, information is sent to system
   * - AC2: During submission, loading indicator shown and button disabled
   * - AC3: On success, user redirected to main application
   * - AC4: On error, clear error message displayed
   *
   * Acceptance Criteria (Story 20.9):
   * - AC1: When system is unavailable, show message indicating service is temporarily unavailable
   * - AC2: When there's a network error, show message explaining the connection issue
   * - AC3: Error message displayed prominently and remains visible until user takes action
   * - AC4: User can easily retry login attempt after error
   */
  const handleLogin = async (name: string, email: string) => {
    setIsSubmitting(true);
    setError(null);

    try {
      // Call backend API using centralized service
      // This uses getRuntimeConfig() to get the correct API URL for the environment
      const data = await submitBasicLogin(name, email);

      // Store tokens in localStorage per API contract guidance
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);

      // Store user data (optional, for quick access)
      localStorage.setItem('user', JSON.stringify(data.user));

      // AC3: Redirect to home page on success
      navigate('/');
    } catch (err) {
      // AC4: Handle errors and display clear messages
      if (err instanceof ApiError) {
        // API errors already have user-friendly messages
        setError(err.message);
      } else if (err instanceof Error) {
        // Unexpected errors
        console.error('Login error:', err);
        setError('An unexpected error occurred. Please try again.');
      } else {
        // Unknown error type
        console.error('Unknown login error:', err);
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '80vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          py: 8,
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 3,
          }}
        >
          {/* Page title */}
          <Typography component="h1" variant="h4" align="center" sx={{ fontWeight: 500 }}>
            Welcome
          </Typography>

          <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 2 }}>
            Enter your name and email to get started
          </Typography>

          {/* Login form */}
          <LoginForm
            onSubmit={handleLogin}
            isSubmitting={isSubmitting}
            externalError={error || undefined}
          />

          {/* Informational message */}
          <Alert severity="info" sx={{ mt: 2, width: '100%' }}>
            No password required. We'll remember you on this device.
          </Alert>
        </Paper>

        {/* Footer text */}
        <Typography variant="caption" color="text.secondary" align="center" sx={{ mt: 4 }}>
          By logging in, you agree to our terms of service and privacy policy.
        </Typography>
      </Box>
    </Container>
  );
}

export default Login;
