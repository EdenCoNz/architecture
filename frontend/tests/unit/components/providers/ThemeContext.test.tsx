/**
 * Unit Tests for ThemeContext
 *
 * Tests the theme context provider and custom hook.
 * Following TDD best practices with comprehensive test coverage.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, renderHook } from '@testing-library/react';
import {
  ThemeContextProvider,
  useThemeContext,
} from '../../../../src/components/providers/ThemeContext';
import { apiService } from '../../../../src/services/api';
import type { ReactNode } from 'react';

// Mock the API service
vi.mock('../../../../src/services/api', () => ({
  apiService: {
    getThemePreference: vi.fn(),
    updateThemePreference: vi.fn(),
  },
}));

describe('ThemeContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('ThemeContextProvider', () => {
    it('should render children components', async () => {
      // Arrange
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'light' },
        status: 200,
      });

      // Act
      render(
        <ThemeContextProvider>
          <div data-testid="child">Test Child</div>
        </ThemeContextProvider>
      );

      // Assert
      const child = await screen.findByTestId('child');
      expect(child).toBeInTheDocument();
    });

    it('should provide theme context to children', async () => {
      // Arrange
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'dark' },
        status: 200,
      });

      function TestComponent() {
        const { themeMode } = useThemeContext();
        return <div data-testid="theme-mode">{themeMode}</div>;
      }

      // Act
      render(
        <ThemeContextProvider>
          <TestComponent />
        </ThemeContextProvider>
      );

      // Assert
      await waitFor(() => {
        const themeModeElement = screen.getByTestId('theme-mode');
        expect(themeModeElement).toHaveTextContent('dark');
      });
    });

    it('should provide all theme context values', async () => {
      // Arrange
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'light' },
        status: 200,
      });

      function TestComponent() {
        const context = useThemeContext();
        return (
          <div>
            <div data-testid="theme-mode">{context.themeMode}</div>
            <div data-testid="resolved-mode">{context.resolvedThemeMode}</div>
            <div data-testid="is-loading">{context.isLoading ? 'loading' : 'loaded'}</div>
            <div data-testid="has-setter">
              {typeof context.setThemeMode === 'function' ? 'yes' : 'no'}
            </div>
          </div>
        );
      }

      // Act
      render(
        <ThemeContextProvider>
          <TestComponent />
        </ThemeContextProvider>
      );

      // Assert
      await waitFor(() => {
        expect(screen.getByTestId('is-loading')).toHaveTextContent('loaded');
      });

      expect(screen.getByTestId('theme-mode')).toHaveTextContent('light');
      expect(screen.getByTestId('resolved-mode')).toHaveTextContent('light');
      expect(screen.getByTestId('has-setter')).toHaveTextContent('yes');
    });
  });

  describe('useThemeContext Hook', () => {
    it('should throw error when used outside provider', () => {
      // Arrange - suppress expected error in console
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      // Act & Assert
      expect(() => {
        renderHook(() => useThemeContext());
      }).toThrow('useThemeContext must be used within a ThemeContextProvider');

      // Cleanup
      consoleErrorSpy.mockRestore();
    });

    it('should return theme context when used inside provider', async () => {
      // Arrange
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'auto' },
        status: 200,
      });

      const wrapper = ({ children }: { children: ReactNode }) => (
        <ThemeContextProvider>{children}</ThemeContextProvider>
      );

      // Act
      const { result } = renderHook(() => useThemeContext(), { wrapper });

      // Assert
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.themeMode).toBe('auto');
      expect(result.current.resolvedThemeMode).toMatch(/^(light|dark)$/);
      expect(typeof result.current.setThemeMode).toBe('function');
    });

    it('should return consistent context value across multiple uses', async () => {
      // Arrange
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'dark' },
        status: 200,
      });

      function TestComponent() {
        const context1 = useThemeContext();
        const context2 = useThemeContext();

        return (
          <div>
            <div data-testid="context-1">{context1.themeMode}</div>
            <div data-testid="context-2">{context2.themeMode}</div>
            <div data-testid="same-instance">{context1 === context2 ? 'same' : 'different'}</div>
          </div>
        );
      }

      // Act
      render(
        <ThemeContextProvider>
          <TestComponent />
        </ThemeContextProvider>
      );

      // Assert
      await waitFor(() => {
        expect(screen.getByTestId('context-1')).toHaveTextContent('dark');
      });

      expect(screen.getByTestId('context-2')).toHaveTextContent('dark');
      expect(screen.getByTestId('same-instance')).toHaveTextContent('same');
    });
  });
});
