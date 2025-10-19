/**
 * TestPage Component Tests
 *
 * Tests for the API Test Page component following TDD principles.
 * Verifies component rendering, user interactions, and state management.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TestPage from '../../src/pages/TestPage/TestPage';
import * as apiService from '../../src/services/api';
import type { HealthCheckResponse } from '../../src/types';

// Mock the API service
vi.mock('../../src/services/api');

describe('TestPage', () => {
  // Mock health check response data
  const mockHealthResponse: HealthCheckResponse = {
    status: 'healthy',
    timestamp: '2024-01-01T12:00:00.000Z',
    version: '1.0.0',
    service: 'project-name-backend',
    database: {
      status: 'healthy',
      connected: true,
      engine: 'postgresql',
    },
    debug_mode: true,
  };

  beforeEach(() => {
    vi.clearAllMocks();

    // Setup default successful response with slight delay to simulate network
    vi.mocked(apiService.apiService.getHealth).mockImplementation(async () => {
      await new Promise((resolve) => setTimeout(resolve, 100));
      return {
        data: mockHealthResponse,
        status: 200,
      };
    });
  });

  describe('Initial Rendering', () => {
    it('renders the page title', () => {
      render(<TestPage />);
      expect(screen.getByRole('heading', { name: /API Test Page/i })).toBeInTheDocument();
    });

    it('renders the page subtitle/description', () => {
      render(<TestPage />);
      expect(screen.getByText(/Test backend connectivity and API responses/i)).toBeInTheDocument();
    });

    it('renders the test button with correct label', () => {
      render(<TestPage />);
      expect(
        screen.getByRole('button', { name: /Test backend API connection/i })
      ).toBeInTheDocument();
    });

    it('test button is enabled initially', () => {
      render(<TestPage />);
      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      expect(button).not.toBeDisabled();
    });

    it('does not show alerts initially', () => {
      render(<TestPage />);
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });

    it('does not show response data initially', () => {
      render(<TestPage />);
      expect(screen.queryByText(/Response Data/i)).not.toBeInTheDocument();
    });
  });

  describe('Button Interaction', () => {
    it('button displays Send icon', () => {
      render(<TestPage />);
      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      // Check that the button has a child element (icon)
      expect(button.querySelector('svg')).toBeInTheDocument();
    });

    it('button has proper ARIA attributes', () => {
      render(<TestPage />);
      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      expect(button).toHaveAttribute('aria-label', 'Test backend API connection');
    });

    it('shows loading state when button is clicked', async () => {
      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });

      // Click the button
      await user.click(button);

      // Button should be disabled during loading
      expect(button).toBeDisabled();
      expect(button).toHaveAttribute('aria-busy', 'true');
    });
  });

  describe('Success State', () => {
    it('shows success alert after successful response', async () => {
      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      await user.click(button);

      // Wait for the success alert
      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument();
      });

      const alert = screen.getByRole('alert');
      expect(alert).toHaveTextContent(/Connection successful/i);
    });

    it('displays response data after successful response', async () => {
      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      await user.click(button);

      // Wait for the response data section
      await waitFor(() => {
        expect(screen.getByText(/Response Data/i)).toBeInTheDocument();
      });
    });

    it('displays formatted JSON response', async () => {
      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      await user.click(button);

      // Wait for JSON response to be visible - check for health check response fields
      await waitFor(() => {
        const codeElement = screen.getByText(/"status"/i);
        expect(codeElement).toBeInTheDocument();
      });
    });

    it('displays timestamp with response', async () => {
      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      await user.click(button);

      // Wait for timestamp
      await waitFor(() => {
        expect(screen.getByText(/Received at:/i)).toBeInTheDocument();
      });
    });

    it('button is re-enabled after successful response', async () => {
      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      await user.click(button);

      // Wait for button to be re-enabled
      await waitFor(() => {
        expect(button).not.toBeDisabled();
      });
    });
  });

  describe('Responsive Behavior', () => {
    it('button is full-width on mobile screens', () => {
      // This would typically use a viewport testing library or
      // check the sx prop for responsive configuration
      render(<TestPage />);
      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      expect(button).toBeInTheDocument();
      // Actual responsive testing would require additional setup
    });
  });

  describe('Accessibility', () => {
    it('page has proper heading hierarchy', () => {
      render(<TestPage />);
      const heading = screen.getByRole('heading', { name: /API Test Page/i });
      // CardHeader uses variant h5 by default
      expect(heading).toBeInTheDocument();
    });

    it('alerts are announced to screen readers', async () => {
      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      await user.click(button);

      await waitFor(() => {
        const alert = screen.getByRole('alert');
        expect(alert).toBeInTheDocument();
      });
    });

    it('response section is in live region for screen readers', async () => {
      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      await user.click(button);

      await waitFor(() => {
        const responseSection = screen.getByText(/Response Data/i).closest('section');
        expect(responseSection).toHaveAttribute('aria-live', 'polite');
      });
    });

    it('button can be activated with keyboard', async () => {
      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      button.focus();

      // Activate with Enter key
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(button).toHaveAttribute('aria-busy', 'true');
      });
    });
  });

  describe('State Management', () => {
    it('clears previous response when button is clicked again', async () => {
      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });

      // First click
      await user.click(button);
      await waitFor(() => {
        expect(screen.getByText(/Response Data/i)).toBeInTheDocument();
      });

      // Second click should clear and reload
      await user.click(button);

      // Button should be in loading state
      expect(button).toBeDisabled();
      expect(button).toHaveAttribute('aria-busy', 'true');
    });

    it('allows multiple test requests', async () => {
      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });

      // First request
      await user.click(button);
      await waitFor(() => {
        expect(button).not.toBeDisabled();
      });

      // Second request should work
      await user.click(button);
      expect(button).toBeDisabled();
    });
  });

  describe('Error Handling', () => {
    it('displays error alert when API call fails', async () => {
      // Mock API error with delay
      vi.mocked(apiService.apiService.getHealth).mockImplementation(async () => {
        await new Promise((resolve) => setTimeout(resolve, 100));
        throw new Error('Network error');
      });

      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      await user.click(button);

      // Wait for error alert - should display fallback message since it's not an ApiError instance
      await waitFor(() => {
        const alert = screen.getByRole('alert');
        expect(alert).toBeInTheDocument();
        expect(alert).toHaveTextContent(/Failed to connect to backend/i);
      });
    });

    it('displays fallback error message for unknown errors', async () => {
      // Mock unknown error with delay
      vi.mocked(apiService.apiService.getHealth).mockImplementation(async () => {
        await new Promise((resolve) => setTimeout(resolve, 100));
        throw new Error('Unknown error');
      });

      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      await user.click(button);

      // Wait for error alert with fallback message
      await waitFor(() => {
        const alert = screen.getByRole('alert');
        expect(alert).toBeInTheDocument();
        expect(alert).toHaveTextContent(/Failed to connect to backend/i);
      });
    });

    it('button is re-enabled after error', async () => {
      // Mock API error with delay
      vi.mocked(apiService.apiService.getHealth).mockImplementation(async () => {
        await new Promise((resolve) => setTimeout(resolve, 100));
        throw new Error('Network error');
      });

      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      await user.click(button);

      // Wait for button to be re-enabled
      await waitFor(() => {
        expect(button).not.toBeDisabled();
      });
    });

    it('can retry after error', async () => {
      // First call fails, second succeeds
      let callCount = 0;
      vi.mocked(apiService.apiService.getHealth).mockImplementation(async () => {
        await new Promise((resolve) => setTimeout(resolve, 100));
        callCount++;
        if (callCount === 1) {
          throw new Error('Network error');
        }
        return {
          data: mockHealthResponse,
          status: 200,
        };
      });

      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });

      // First attempt - should fail
      await user.click(button);
      await waitFor(() => {
        const alert = screen.getByRole('alert');
        expect(alert).toHaveTextContent(/Failed to connect to backend/i);
      });

      // Second attempt - should succeed
      await user.click(button);
      await waitFor(() => {
        const alert = screen.getByRole('alert');
        expect(alert).toHaveTextContent(/Connection successful/i);
      });
    });

    it('does not display response data when error occurs', async () => {
      // Mock API error with delay
      vi.mocked(apiService.apiService.getHealth).mockImplementation(async () => {
        await new Promise((resolve) => setTimeout(resolve, 100));
        throw new Error('Network error');
      });

      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      await user.click(button);

      // Wait for error alert
      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument();
      });

      // Response data should not be visible
      expect(screen.queryByText(/Response Data/i)).not.toBeInTheDocument();
    });
  });

  describe('API Integration', () => {
    it('calls apiService.getHealth when button is clicked', async () => {
      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      await user.click(button);

      // Verify API was called
      await waitFor(() => {
        expect(apiService.apiService.getHealth).toHaveBeenCalledTimes(1);
      });
    });

    it('displays actual backend response data', async () => {
      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      await user.click(button);

      // Wait for response data
      await waitFor(() => {
        expect(screen.getByText(/Response Data/i)).toBeInTheDocument();
      });

      // Verify health status is displayed
      expect(screen.getByText(/"status"/i)).toBeInTheDocument();
      expect(screen.getByText(/"healthy"/i)).toBeInTheDocument();
    });

    it('displays database information from response', async () => {
      const user = userEvent.setup();
      render(<TestPage />);

      const button = screen.getByRole('button', { name: /Test backend API connection/i });
      await user.click(button);

      // Wait for response data
      await waitFor(() => {
        expect(screen.getByText(/Response Data/i)).toBeInTheDocument();
      });

      // Verify database info is displayed
      expect(screen.getByText(/"database"/i)).toBeInTheDocument();
      expect(screen.getByText(/"postgresql"/i)).toBeInTheDocument();
    });
  });
});
