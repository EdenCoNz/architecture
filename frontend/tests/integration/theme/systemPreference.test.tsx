/**
 * Integration Tests for System Theme Preference Detection
 *
 * Tests the complete flow of system theme preference detection,
 * including initial detection, real-time OS changes, and user overrides.
 * This verifies Story #5: Detect System Theme Preference.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { ReactNode } from 'react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { useThemeMode } from '../../../src/hooks/useThemeMode';
import { AppThemeProvider } from '../../../src/components/providers/AppThemeProvider';
import { apiService } from '../../../src/services/api';
import themeReducer from '../../../src/store/slices/themeSlice';

// Mock the API service
vi.mock('../../../src/services/api', () => ({
  apiService: {
    getThemePreference: vi.fn(),
    updateThemePreference: vi.fn(),
  },
}));

describe('System Theme Preference Detection - Integration', () => {
  let matchMediaMock: typeof window.matchMedia;
  let consoleWarnSpy: ReturnType<typeof vi.spyOn>;
  let consoleErrorSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    // Store original matchMedia
    matchMediaMock = window.matchMedia;

    // Mock console to suppress expected warnings/errors in tests
    consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    // Reset all mocks before each test
    vi.clearAllMocks();
  });

  afterEach(() => {
    // Restore original matchMedia
    window.matchMedia = matchMediaMock;

    // Restore console methods
    consoleWarnSpy.mockRestore();
    consoleErrorSpy.mockRestore();
  });

  describe('Initial System Preference Detection', () => {
    it('should detect dark mode preference on first visit', async () => {
      // Arrange - Mock system prefers dark
      window.matchMedia = vi.fn().mockImplementation((query: string) => ({
        matches: query === '(prefers-color-scheme: dark)',
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })) as typeof window.matchMedia;

      // Mock API returns 'auto' (new user default)
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'auto' },
        status: 200,
      });

      // Act
      const { result } = renderHook(() => useThemeMode());

      // Wait for loading to complete
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Assert
      expect(result.current.themeMode).toBe('auto');
      expect(result.current.systemPrefersDark).toBe(true);
      expect(result.current.resolvedThemeMode).toBe('dark');
    });

    it('should detect light mode preference on first visit', async () => {
      // Arrange - Mock system prefers light
      window.matchMedia = vi.fn().mockImplementation(() => ({
        matches: false,
        media: '(prefers-color-scheme: dark)',
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })) as typeof window.matchMedia;

      // Mock API returns 'auto' (new user default)
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'auto' },
        status: 200,
      });

      // Act
      const { result } = renderHook(() => useThemeMode());

      // Wait for loading to complete
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Assert
      expect(result.current.themeMode).toBe('auto');
      expect(result.current.systemPrefersDark).toBe(false);
      expect(result.current.resolvedThemeMode).toBe('light');
    });

    it('should default to auto mode when API is unavailable', async () => {
      // Arrange - System prefers dark
      window.matchMedia = vi.fn().mockImplementation((query: string) => ({
        matches: query === '(prefers-color-scheme: dark)',
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })) as typeof window.matchMedia;

      // Mock API failure (backend unavailable)
      const mockError = new Error('Network error');
      vi.mocked(apiService.getThemePreference).mockRejectedValue(mockError);

      // Act
      const { result } = renderHook(() => useThemeMode());

      // Wait for loading to complete
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Assert - Should fall back to 'auto' mode
      expect(result.current.themeMode).toBe('auto');
      expect(result.current.systemPrefersDark).toBe(true);
      expect(result.current.resolvedThemeMode).toBe('dark');
      expect(result.current.error).toEqual(mockError);
    });
  });

  describe('Real-time OS Theme Changes', () => {
    it('should react to OS theme change from light to dark in auto mode', async () => {
      // Arrange
      let changeHandler: ((e: MediaQueryListEvent) => void) | null = null;

      window.matchMedia = vi.fn().mockImplementation(() => ({
        matches: false, // Initially light
        media: '(prefers-color-scheme: dark)',
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn((event: string, handler: (e: MediaQueryListEvent) => void) => {
          if (event === 'change') {
            changeHandler = handler;
          }
        }),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })) as typeof window.matchMedia;

      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'auto' },
        status: 200,
      });

      const { result } = renderHook(() => useThemeMode());

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Initial state - light
      expect(result.current.systemPrefersDark).toBe(false);
      expect(result.current.resolvedThemeMode).toBe('light');

      // Act - Simulate OS preference change to dark
      if (changeHandler) {
        act(() => {
          changeHandler!({ matches: true } as MediaQueryListEvent);
        });
      }

      // Assert - Theme should update to dark
      await waitFor(() => {
        expect(result.current.systemPrefersDark).toBe(true);
        expect(result.current.resolvedThemeMode).toBe('dark');
      });
    });

    it('should react to OS theme change from dark to light in auto mode', async () => {
      // Arrange
      let changeHandler: ((e: MediaQueryListEvent) => void) | null = null;

      window.matchMedia = vi.fn().mockImplementation(() => ({
        matches: true, // Initially dark
        media: '(prefers-color-scheme: dark)',
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn((event: string, handler: (e: MediaQueryListEvent) => void) => {
          if (event === 'change') {
            changeHandler = handler;
          }
        }),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })) as typeof window.matchMedia;

      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'auto' },
        status: 200,
      });

      const { result } = renderHook(() => useThemeMode());

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Initial state - dark
      expect(result.current.systemPrefersDark).toBe(true);
      expect(result.current.resolvedThemeMode).toBe('dark');

      // Act - Simulate OS preference change to light
      if (changeHandler) {
        act(() => {
          changeHandler!({ matches: false } as MediaQueryListEvent);
        });
      }

      // Assert - Theme should update to light
      await waitFor(() => {
        expect(result.current.systemPrefersDark).toBe(false);
        expect(result.current.resolvedThemeMode).toBe('light');
      });
    });

    it('should NOT affect theme when user has manual preference', async () => {
      // Arrange
      let changeHandler: ((e: MediaQueryListEvent) => void) | null = null;

      window.matchMedia = vi.fn().mockImplementation(() => ({
        matches: false, // System is light
        media: '(prefers-color-scheme: dark)',
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn((event: string, handler: (e: MediaQueryListEvent) => void) => {
          if (event === 'change') {
            changeHandler = handler;
          }
        }),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })) as typeof window.matchMedia;

      // User has manually selected dark mode
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'dark' },
        status: 200,
      });

      const { result } = renderHook(() => useThemeMode());

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Initial state - dark (manual preference)
      expect(result.current.themeMode).toBe('dark');
      expect(result.current.resolvedThemeMode).toBe('dark');

      // Act - Simulate OS preference change to dark
      if (changeHandler) {
        act(() => {
          changeHandler!({ matches: true } as MediaQueryListEvent);
        });
      }

      // Assert - Theme should STAY dark (no change because manual preference)
      await waitFor(() => {
        expect(result.current.themeMode).toBe('dark');
        expect(result.current.resolvedThemeMode).toBe('dark');
      });
    });
  });

  describe('Manual Override of System Preference', () => {
    it('should allow user to override system preference with manual selection', async () => {
      // Arrange - System prefers dark
      window.matchMedia = vi.fn().mockImplementation(() => ({
        matches: true,
        media: '(prefers-color-scheme: dark)',
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })) as typeof window.matchMedia;

      // User starts with auto mode
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'auto' },
        status: 200,
      });

      vi.mocked(apiService.updateThemePreference).mockResolvedValue({
        data: { theme: 'light' },
        status: 200,
      });

      const { result } = renderHook(() => useThemeMode());

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Initial state - auto mode following system (dark)
      expect(result.current.themeMode).toBe('auto');
      expect(result.current.resolvedThemeMode).toBe('dark');

      // Act - User manually selects light mode
      await act(async () => {
        await result.current.setThemeMode('light');
      });

      // Assert - Theme should be light regardless of system preference
      expect(result.current.themeMode).toBe('light');
      expect(result.current.resolvedThemeMode).toBe('light');
      expect(apiService.updateThemePreference).toHaveBeenCalledWith('light');
    });

    it('should allow user to return to auto mode after manual override', async () => {
      // Arrange - System prefers light
      window.matchMedia = vi.fn().mockImplementation(() => ({
        matches: false,
        media: '(prefers-color-scheme: dark)',
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })) as typeof window.matchMedia;

      // User has manual dark mode preference
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'dark' },
        status: 200,
      });

      vi.mocked(apiService.updateThemePreference).mockResolvedValue({
        data: { theme: 'auto' },
        status: 200,
      });

      const { result } = renderHook(() => useThemeMode());

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Initial state - manual dark mode
      expect(result.current.themeMode).toBe('dark');
      expect(result.current.resolvedThemeMode).toBe('dark');

      // Act - User switches back to auto mode
      await act(async () => {
        await result.current.setThemeMode('auto');
      });

      // Assert - Theme should follow system preference (light)
      expect(result.current.themeMode).toBe('auto');
      expect(result.current.resolvedThemeMode).toBe('light');
      expect(apiService.updateThemePreference).toHaveBeenCalledWith('auto');
    });
  });

  describe('Browser Compatibility', () => {
    it('should handle browsers without matchMedia support', async () => {
      // Arrange - Remove matchMedia support
      const originalMatchMedia = window.matchMedia;
      // @ts-expect-error - Testing browser without matchMedia
      delete window.matchMedia;

      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'auto' },
        status: 200,
      });

      // Act
      const { result } = renderHook(() => useThemeMode());

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Assert - Should default to light mode
      expect(result.current.themeMode).toBe('auto');
      expect(result.current.systemPrefersDark).toBe(false);
      expect(result.current.resolvedThemeMode).toBe('light');

      // Cleanup
      window.matchMedia = originalMatchMedia;
    });

    it('should handle browsers without prefers-color-scheme support', async () => {
      // Arrange - Mock matchMedia that doesn't match prefers-color-scheme
      window.matchMedia = vi.fn().mockImplementation(() => ({
        matches: false,
        media: 'not all', // Indicates query not supported
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
      const { result } = renderHook(() => useThemeMode());

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Assert - Should default to light mode
      expect(result.current.themeMode).toBe('auto');
      expect(result.current.resolvedThemeMode).toBe('light');
    });
  });

  describe('AppThemeProvider Integration', () => {
    it('should create correct MUI theme based on system preference', async () => {
      // Arrange - System prefers dark
      window.matchMedia = vi.fn().mockImplementation((query: string) => ({
        matches: query === '(prefers-color-scheme: dark)',
        media: query,
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

      // Create a store for the provider
      const store = configureStore({
        reducer: {
          theme: themeReducer,
        },
      });

      // Create wrapper with AppThemeProvider
      const wrapper = ({ children }: { children: ReactNode }) => (
        <Provider store={store}>
          <AppThemeProvider>{children}</AppThemeProvider>
        </Provider>
      );

      // Act
      const { result } = renderHook(() => useThemeMode(), { wrapper });

      // Wait for loading to complete
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Assert - Theme should be auto mode resolving to dark
      expect(result.current.themeMode).toBe('auto');
      expect(result.current.systemPrefersDark).toBe(true);
      expect(result.current.resolvedThemeMode).toBe('dark');
    });
  });

  describe('Edge Cases', () => {
    it('should handle multiple rapid OS theme changes', async () => {
      // Arrange
      let changeHandler: ((e: MediaQueryListEvent) => void) | null = null;

      window.matchMedia = vi.fn().mockImplementation(() => ({
        matches: false,
        media: '(prefers-color-scheme: dark)',
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn((event: string, handler: (e: MediaQueryListEvent) => void) => {
          if (event === 'change') {
            changeHandler = handler;
          }
        }),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })) as typeof window.matchMedia;

      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'auto' },
        status: 200,
      });

      const { result } = renderHook(() => useThemeMode());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Act - Multiple rapid changes
      if (changeHandler) {
        act(() => {
          changeHandler!({ matches: true } as MediaQueryListEvent); // dark
          changeHandler!({ matches: false } as MediaQueryListEvent); // light
          changeHandler!({ matches: true } as MediaQueryListEvent); // dark
        });
      }

      // Assert - Should settle on final state
      await waitFor(() => {
        expect(result.current.systemPrefersDark).toBe(true);
        expect(result.current.resolvedThemeMode).toBe('dark');
      });
    });

    it('should maintain system preference detection after API errors', async () => {
      // Arrange
      window.matchMedia = vi.fn().mockImplementation((query: string) => ({
        matches: query === '(prefers-color-scheme: dark)',
        media: query,
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

      // Mock update to fail
      const mockError = new Error('Server error');
      vi.mocked(apiService.updateThemePreference).mockRejectedValue(mockError);

      const { result } = renderHook(() => useThemeMode());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Act - Try to update (will fail)
      await act(async () => {
        await result.current.setThemeMode('dark');
      });

      // Assert - System preference detection should still work
      expect(result.current.systemPrefersDark).toBe(true);
      expect(result.current.themeMode).toBe('dark'); // Optimistic update kept
      expect(result.current.error).toEqual(mockError);
    });
  });
});
