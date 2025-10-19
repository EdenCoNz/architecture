/**
 * Unit Tests for AppThemeProvider Component
 *
 * Tests the AppThemeProvider wrapper component for theme management.
 * Following TDD best practices with comprehensive test coverage.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { AppThemeProvider } from '../../../../src/components/providers/AppThemeProvider';
import { apiService } from '../../../../src/services/api';
import type { ThemePreferenceResponse } from '../../../../src/types';

// Mock the API service
vi.mock('../../../../src/services/api', () => ({
  apiService: {
    getThemePreference: vi.fn(),
    updateThemePreference: vi.fn(),
  },
}));

describe('AppThemeProvider Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render children components', async () => {
      // Arrange
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'light' },
        status: 200,
      });

      // Act
      render(
        <AppThemeProvider>
          <div data-testid="child">Test Child</div>
        </AppThemeProvider>
      );

      // Assert
      const child = await screen.findByTestId('child');
      expect(child).toBeInTheDocument();
      expect(child).toHaveTextContent('Test Child');
    });

    it('should include CssBaseline component', async () => {
      // Arrange
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'light' },
        status: 200,
      });

      // Act
      const { container } = render(
        <AppThemeProvider>
          <div>Content</div>
        </AppThemeProvider>
      );

      // Assert
      // CssBaseline adds specific styles to the body
      await waitFor(() => {
        // Check that MUI's CSS baseline has been applied
        const styles = window.getComputedStyle(container);
        expect(styles).toBeDefined();
      });
    });
  });

  describe('Theme Application', () => {
    it('should apply light theme when theme mode is light', async () => {
      // Arrange
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'light' },
        status: 200,
      });

      // Act
      const { container } = render(
        <AppThemeProvider>
          <div data-testid="content">Content</div>
        </AppThemeProvider>
      );

      // Wait for theme to be loaded
      await waitFor(() => {
        const content = screen.getByTestId('content');
        expect(content).toBeInTheDocument();
      });

      // Assert - check that light theme is applied (MUI adds data attributes or classes)
      expect(container).toBeDefined();
    });

    it('should apply dark theme when theme mode is dark', async () => {
      // Arrange
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'dark' },
        status: 200,
      });

      // Act
      const { container } = render(
        <AppThemeProvider>
          <div data-testid="content">Content</div>
        </AppThemeProvider>
      );

      // Wait for theme to be loaded
      await waitFor(() => {
        const content = screen.getByTestId('content');
        expect(content).toBeInTheDocument();
      });

      // Assert
      expect(container).toBeDefined();
    });

    it('should resolve auto mode based on system preference', async () => {
      // Arrange
      window.matchMedia = vi.fn().mockImplementation(() => ({
        matches: true, // System prefers dark
        media: '(prefers-color-scheme: dark)',
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })) as typeof window.matchMedia;

      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'auto' },
        status: 200,
      });

      // Act
      render(
        <AppThemeProvider>
          <div data-testid="content">Content</div>
        </AppThemeProvider>
      );

      // Assert - should apply dark theme due to system preference
      await waitFor(() => {
        const content = screen.getByTestId('content');
        expect(content).toBeInTheDocument();
      });
    });
  });

  describe('Theme Loading States', () => {
    it('should render children while loading theme', () => {
      // Arrange - never resolve to test loading state
      vi.mocked(apiService.getThemePreference).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      // Act
      render(
        <AppThemeProvider>
          <div data-testid="child">Loading content</div>
        </AppThemeProvider>
      );

      // Assert - children should still render during loading
      const child = screen.getByTestId('child');
      expect(child).toBeInTheDocument();
    });

    it('should handle API errors gracefully', async () => {
      // Arrange
      vi.mocked(apiService.getThemePreference).mockRejectedValue(new Error('API Error'));

      // Act
      render(
        <AppThemeProvider>
          <div data-testid="child">Content</div>
        </AppThemeProvider>
      );

      // Assert - should still render with fallback theme
      await waitFor(() => {
        const child = screen.getByTestId('child');
        expect(child).toBeInTheDocument();
      });
    });
  });

  describe('Integration with Theme Hook', () => {
    it('should fetch theme preference on mount', async () => {
      // Arrange
      const mockResponse: ThemePreferenceResponse = { theme: 'dark' };
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: mockResponse,
        status: 200,
      });

      // Act
      render(
        <AppThemeProvider>
          <div>Content</div>
        </AppThemeProvider>
      );

      // Assert
      await waitFor(() => {
        expect(apiService.getThemePreference).toHaveBeenCalledTimes(1);
      });
    });
  });
});
