/**
 * Login Page Tests
 *
 * Feature 20 - Story 20.5: Submit login information
 * Feature 20 - Story 20.9: Handle login errors gracefully
 *
 * Test coverage for Login page integration:
 * - Page renders correctly with LoginForm
 * - Handles successful login submission
 * - Handles API errors (network, service unavailable, rate limiting, etc.)
 * - Navigates on successful login
 * - Error messages remain visible and allow retry
 *
 * Note: Detailed form field tests are in LoginForm.test.tsx
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import Login from './Login';
import * as apiService from '../../services/api';

// Mock the API service
vi.mock('../../services/api', () => ({
  submitBasicLogin: vi.fn(),
  ApiError: class ApiError extends Error {
    status?: number;
    statusText?: string;
    constructor(message: string, status?: number, statusText?: string) {
      super(message);
      this.name = 'ApiError';
      this.status = status;
      this.statusText = statusText;
    }
  },
}));

// Mock the navigate function
// This mock is set up AFTER importing react-router-dom to allow MemoryRouter to work properly
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Helper to render with Router context
// Uses MemoryRouter which is designed for testing and provides complete Router context
// MemoryRouter is preferred over BrowserRouter for tests because:
// - It doesn't depend on browser history API
// - Provides isolated routing state for each test
// - Works reliably in both local and CI environments
const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <MemoryRouter initialEntries={['/login']}>
      {component}
    </MemoryRouter>
  );
};

describe('Login Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('Page Rendering', () => {
    it('renders the login page with title and form', () => {
      renderWithRouter(<Login />);

      expect(screen.getByText(/welcome/i)).toBeInTheDocument();
      expect(screen.getByText(/enter your name and email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /log in/i })).toBeInTheDocument();
    });

    it('displays informational message about no password required', () => {
      renderWithRouter(<Login />);

      expect(
        screen.getByText(/no password required.*remember you on this device/i)
      ).toBeInTheDocument();
    });
  });

  describe('Story 20.5 & 20.9: Submit login information and error handling', () => {
    it('AC1: submits user information when both fields are filled', async () => {
      const user = userEvent.setup();
      const mockResponse = {
        message: 'Login successful.',
        user: {
          id: 1,
          email: 'test@example.com',
          first_name: 'Test',
          last_name: 'User',
          is_active: true,
          date_joined: '2025-11-02T10:00:00Z',
        },
        access: 'mock-access-token',
        refresh: 'mock-refresh-token',
        is_new_user: false,
      };

      vi.mocked(apiService.submitBasicLogin).mockResolvedValueOnce(mockResponse);

      renderWithRouter(<Login />);

      // Fill in the form
      const nameInput = screen.getByLabelText(/name/i);
      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      await user.type(nameInput, 'Test User');
      await user.type(emailInput, 'test@example.com');
      await user.click(submitButton);

      // Verify API was called with correct data
      await waitFor(() => {
        expect(apiService.submitBasicLogin).toHaveBeenCalledWith('Test User', 'test@example.com');
      });
    });

    it('AC2: shows loading indicator during submission', async () => {
      const user = userEvent.setup();
      let resolveLogin: (value: unknown) => void;
      const loginPromise = new Promise((resolve) => {
        resolveLogin = resolve;
      });

      vi.mocked(apiService.submitBasicLogin).mockReturnValueOnce(loginPromise as never);

      renderWithRouter(<Login />);

      // Fill in and submit form
      await user.type(screen.getByLabelText(/name/i), 'Test User');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.click(screen.getByRole('button', { name: /log in/i }));

      // Should show loading state
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /logging in/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /logging in/i })).toBeDisabled();
      });

      // Resolve the promise to clean up
      resolveLogin!({
        message: 'Login successful.',
        user: {
          id: 1,
          email: 'test@example.com',
          first_name: 'Test',
          last_name: 'User',
          is_active: true,
          date_joined: '2025-11-02T10:00:00Z',
        },
        access: 'mock-access-token',
        refresh: 'mock-refresh-token',
        is_new_user: false,
      });
    });

    it('AC3: redirects to main application on successful login', async () => {
      const user = userEvent.setup();
      const mockResponse = {
        message: 'Login successful.',
        user: {
          id: 1,
          email: 'test@example.com',
          first_name: 'Test',
          last_name: 'User',
          is_active: true,
          date_joined: '2025-11-02T10:00:00Z',
        },
        access: 'mock-access-token',
        refresh: 'mock-refresh-token',
        is_new_user: false,
      };

      vi.mocked(apiService.submitBasicLogin).mockResolvedValueOnce(mockResponse);

      renderWithRouter(<Login />);

      // Fill in and submit form
      await user.type(screen.getByLabelText(/name/i), 'Test User');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.click(screen.getByRole('button', { name: /log in/i }));

      // Should navigate to home page
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/');
      });

      // Should store tokens in localStorage
      expect(localStorage.getItem('access_token')).toBe('mock-access-token');
      expect(localStorage.getItem('refresh_token')).toBe('mock-refresh-token');
      expect(localStorage.getItem('user')).toBeTruthy();
    });

    it('AC4: shows clear error message when login fails', async () => {
      const user = userEvent.setup();
      const mockError = new apiService.ApiError(
        'Invalid credentials. Please check your email and try again.',
        400
      );

      vi.mocked(apiService.submitBasicLogin).mockRejectedValueOnce(mockError);

      renderWithRouter(<Login />);

      // Fill in and submit form
      await user.type(screen.getByLabelText(/name/i), 'Test User');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.click(screen.getByRole('button', { name: /log in/i }));

      // Should display error message
      await waitFor(() => {
        expect(
          screen.getByText(/invalid credentials.*check your email/i)
        ).toBeInTheDocument();
      });

      // Should not navigate
      expect(mockNavigate).not.toHaveBeenCalled();

      // Should not store tokens
      expect(localStorage.getItem('access_token')).toBeNull();
      expect(localStorage.getItem('refresh_token')).toBeNull();
    });

    it('handles network errors gracefully', async () => {
      const user = userEvent.setup();
      const mockError = new Error('Network error');

      vi.mocked(apiService.submitBasicLogin).mockRejectedValueOnce(mockError);

      renderWithRouter(<Login />);

      // Fill in and submit form
      await user.type(screen.getByLabelText(/name/i), 'Test User');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.click(screen.getByRole('button', { name: /log in/i }));

      // Should display generic error message
      await waitFor(() => {
        expect(screen.getByText(/unexpected error occurred/i)).toBeInTheDocument();
      });
    });

    it('stores user data correctly on successful login', async () => {
      const user = userEvent.setup();
      const mockResponse = {
        message: 'Account created successfully.',
        user: {
          id: 2,
          email: 'newuser@example.com',
          first_name: 'New',
          last_name: 'User',
          is_active: true,
          date_joined: '2025-11-02T10:30:00Z',
        },
        access: 'new-access-token',
        refresh: 'new-refresh-token',
        is_new_user: true,
      };

      vi.mocked(apiService.submitBasicLogin).mockResolvedValueOnce(mockResponse);

      renderWithRouter(<Login />);

      // Fill in and submit form
      await user.type(screen.getByLabelText(/name/i), 'New User');
      await user.type(screen.getByLabelText(/email/i), 'newuser@example.com');
      await user.click(screen.getByRole('button', { name: /log in/i }));

      // Verify user data is stored
      await waitFor(() => {
        const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
        expect(storedUser.id).toBe(2);
        expect(storedUser.email).toBe('newuser@example.com');
        expect(storedUser.first_name).toBe('New');
        expect(storedUser.last_name).toBe('User');
      });
    });
  });

  describe('Story 20.9: Handle login errors gracefully', () => {
    it('AC1: shows service unavailable message when system is down (503)', async () => {
      const user = userEvent.setup();
      const mockError = new apiService.ApiError(
        'The service is temporarily unavailable. Please try again in a few moments.',
        503,
        'Service Unavailable'
      );

      vi.mocked(apiService.submitBasicLogin).mockRejectedValueOnce(mockError);

      renderWithRouter(<Login />);

      // Fill in and submit form
      await user.type(screen.getByLabelText(/name/i), 'Test User');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.click(screen.getByRole('button', { name: /log in/i }));

      // Should display service unavailable message
      await waitFor(() => {
        expect(
          screen.getByText(/service is temporarily unavailable/i)
        ).toBeInTheDocument();
      });

      // Should display prominently with error styling (use getAllByRole to handle multiple alerts)
      const errorAlerts = screen.getAllByRole('alert');
      const errorAlert = errorAlerts.find(alert =>
        alert.textContent?.includes('service is temporarily unavailable')
      );
      expect(errorAlert).toBeInTheDocument();
    });

    it('AC2: shows network error message when connection fails', async () => {
      const user = userEvent.setup();
      const mockError = new apiService.ApiError(
        'Unable to connect to the server. Please check your internet connection and try again.'
      );

      vi.mocked(apiService.submitBasicLogin).mockRejectedValueOnce(mockError);

      renderWithRouter(<Login />);

      // Fill in and submit form
      await user.type(screen.getByLabelText(/name/i), 'Test User');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.click(screen.getByRole('button', { name: /log in/i }));

      // Should display network error message
      await waitFor(() => {
        expect(
          screen.getByText(/unable to connect to the server.*check your internet connection/i)
        ).toBeInTheDocument();
      });
    });

    it('AC2: shows timeout message when request takes too long', async () => {
      const user = userEvent.setup();
      const mockError = new apiService.ApiError(
        'The connection is taking too long. Please check your internet connection and try again.'
      );

      vi.mocked(apiService.submitBasicLogin).mockRejectedValueOnce(mockError);

      renderWithRouter(<Login />);

      // Fill in and submit form
      await user.type(screen.getByLabelText(/name/i), 'Test User');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.click(screen.getByRole('button', { name: /log in/i }));

      // Should display timeout message
      await waitFor(() => {
        expect(
          screen.getByText(/connection is taking too long.*check your internet connection/i)
        ).toBeInTheDocument();
      });
    });

    it('AC3: error message is displayed prominently with proper ARIA attributes', async () => {
      const user = userEvent.setup();
      const mockError = new apiService.ApiError('Test error message', 400);

      vi.mocked(apiService.submitBasicLogin).mockRejectedValueOnce(mockError);

      renderWithRouter(<Login />);

      // Fill in and submit form
      await user.type(screen.getByLabelText(/name/i), 'Test User');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.click(screen.getByRole('button', { name: /log in/i }));

      // Should display error with proper accessibility attributes
      await waitFor(() => {
        const errorAlerts = screen.getAllByRole('alert');
        const errorAlert = errorAlerts.find(alert =>
          alert.textContent?.includes('Test error message')
        );
        expect(errorAlert).toBeInTheDocument();
        expect(errorAlert).toHaveTextContent('Test error message');
        expect(errorAlert).toHaveAttribute('aria-live', 'polite');
      });
    });

    it('AC3: error message remains visible until user takes action', async () => {
      const user = userEvent.setup();
      const mockError = new apiService.ApiError('Persistent error message', 500);

      vi.mocked(apiService.submitBasicLogin).mockRejectedValueOnce(mockError);

      renderWithRouter(<Login />);

      // Fill in and submit form
      await user.type(screen.getByLabelText(/name/i), 'Test User');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.click(screen.getByRole('button', { name: /log in/i }));

      // Wait for error to appear
      await waitFor(() => {
        expect(screen.getByText(/persistent error message/i)).toBeInTheDocument();
      });

      // Error should still be visible after a short delay (not auto-dismissed)
      await new Promise(resolve => setTimeout(resolve, 1000));
      expect(screen.getByText(/persistent error message/i)).toBeInTheDocument();

      // Error should remain until user modifies form
      const nameInput = screen.getByLabelText(/name/i) as HTMLInputElement;
      await user.clear(nameInput);

      // Error should still be visible (only clears on new submission)
      expect(screen.getByText(/persistent error message/i)).toBeInTheDocument();
    });

    it('AC4: user can easily retry login attempt after error', async () => {
      const user = userEvent.setup();
      const mockError = new apiService.ApiError('First attempt failed', 500);
      const mockSuccess = {
        message: 'Login successful.',
        user: {
          id: 1,
          email: 'test@example.com',
          first_name: 'Test',
          last_name: 'User',
          is_active: true,
          date_joined: '2025-11-02T10:00:00Z',
        },
        access: 'mock-access-token',
        refresh: 'mock-refresh-token',
        is_new_user: false,
      };

      // First attempt fails, second succeeds
      vi.mocked(apiService.submitBasicLogin)
        .mockRejectedValueOnce(mockError)
        .mockResolvedValueOnce(mockSuccess);

      renderWithRouter(<Login />);

      // First attempt - fails
      await user.type(screen.getByLabelText(/name/i), 'Test User');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.click(screen.getByRole('button', { name: /log in/i }));

      // Error should appear
      await waitFor(() => {
        expect(screen.getByText(/first attempt failed/i)).toBeInTheDocument();
      });

      // Retry - click login button again
      await user.click(screen.getByRole('button', { name: /log in/i }));

      // Error should be cleared and login should succeed
      await waitFor(() => {
        expect(screen.queryByText(/first attempt failed/i)).not.toBeInTheDocument();
        expect(mockNavigate).toHaveBeenCalledWith('/');
      });

      // Verify second API call was made
      expect(apiService.submitBasicLogin).toHaveBeenCalledTimes(2);
    });

    it('shows rate limiting message (429)', async () => {
      const user = userEvent.setup();
      const mockError = new apiService.ApiError(
        'Too many login attempts. Please wait a moment and try again.',
        429,
        'Too Many Requests'
      );

      vi.mocked(apiService.submitBasicLogin).mockRejectedValueOnce(mockError);

      renderWithRouter(<Login />);

      // Fill in and submit form
      await user.type(screen.getByLabelText(/name/i), 'Test User');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.click(screen.getByRole('button', { name: /log in/i }));

      // Should display rate limiting message
      await waitFor(() => {
        expect(
          screen.getByText(/too many login attempts.*wait a moment/i)
        ).toBeInTheDocument();
      });
    });

    it('shows server error message (500)', async () => {
      const user = userEvent.setup();
      const mockError = new apiService.ApiError(
        'Something went wrong on our end. Please try again in a few moments.',
        500,
        'Internal Server Error'
      );

      vi.mocked(apiService.submitBasicLogin).mockRejectedValueOnce(mockError);

      renderWithRouter(<Login />);

      // Fill in and submit form
      await user.type(screen.getByLabelText(/name/i), 'Test User');
      await user.type(screen.getByLabelText(/email/i), 'test@example.com');
      await user.click(screen.getByRole('button', { name: /log in/i }));

      // Should display server error message
      await waitFor(() => {
        expect(
          screen.getByText(/something went wrong on our end/i)
        ).toBeInTheDocument();
      });
    });

    it('shows validation error message (400)', async () => {
      const user = userEvent.setup();
      const mockError = new apiService.ApiError(
        'email: Enter a valid email address.',
        400,
        'Bad Request'
      );

      vi.mocked(apiService.submitBasicLogin).mockRejectedValueOnce(mockError);

      renderWithRouter(<Login />);

      // Fill in and submit form
      await user.type(screen.getByLabelText(/name/i), 'Test User');
      await user.type(screen.getByLabelText(/email/i), 'invalid-email');
      await user.click(screen.getByRole('button', { name: /log in/i }));

      // Should display validation error message
      await waitFor(() => {
        expect(
          screen.getByText(/enter a valid email address/i)
        ).toBeInTheDocument();
      });
    });
  });
});
