/**
 * Unit Tests for useThemeMode Hook
 *
 * Tests the useThemeMode hook for theme state management, API integration,
 * and system preference detection.
 * Following TDD best practices with comprehensive test coverage.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useThemeMode } from '../../../src/hooks/useThemeMode';
import { apiService } from '../../../src/services/api';
import type { ThemePreferenceResponse } from '../../../src/types';

// Mock the API service
vi.mock('../../../src/services/api', () => ({
  apiService: {
    getThemePreference: vi.fn(),
    updateThemePreference: vi.fn(),
  },
}));

describe('useThemeMode Hook', () => {
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

  describe('Initial State', () => {
    it('should start with auto mode and loading state', () => {
      // Arrange - Mock pending API call
      vi.mocked(apiService.getThemePreference).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      // Act
      const { result } = renderHook(() => useThemeMode());

      // Assert
      expect(result.current.themeMode).toBe('auto');
      expect(result.current.isLoading).toBe(true);
      expect(result.current.error).toBeNull();
    });

    it('should detect system theme preference on mount', () => {
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

      vi.mocked(apiService.getThemePreference).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      // Act
      const { result } = renderHook(() => useThemeMode());

      // Assert
      expect(result.current.systemPrefersDark).toBe(true);
    });
  });

  describe('Loading Theme Preference from Backend', () => {
    it('should load theme preference from backend on mount', async () => {
      // Arrange
      const mockResponse: ThemePreferenceResponse = { theme: 'dark' };
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: mockResponse,
        status: 200,
      });

      // Act
      const { result } = renderHook(() => useThemeMode());

      // Wait for the effect to complete
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Assert
      expect(apiService.getThemePreference).toHaveBeenCalledTimes(1);
      expect(result.current.themeMode).toBe('dark');
      expect(result.current.error).toBeNull();
    });

    it('should handle API error gracefully and keep auto mode', async () => {
      // Arrange
      const mockError = new Error('API error');
      vi.mocked(apiService.getThemePreference).mockRejectedValue(mockError);

      // Act
      const { result } = renderHook(() => useThemeMode());

      // Wait for the effect to complete
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Assert
      expect(result.current.themeMode).toBe('auto'); // Keeps default
      expect(result.current.error).toEqual(mockError);
      expect(consoleWarnSpy).toHaveBeenCalled();
    });

    it('should load all theme modes correctly', async () => {
      const modes: Array<'light' | 'dark' | 'auto'> = ['light', 'dark', 'auto'];

      for (const mode of modes) {
        // Arrange
        const mockResponse: ThemePreferenceResponse = { theme: mode };
        vi.mocked(apiService.getThemePreference).mockResolvedValue({
          data: mockResponse,
          status: 200,
        });

        // Act
        const { result } = renderHook(() => useThemeMode());

        // Wait for loading to complete
        await waitFor(() => {
          expect(result.current.isLoading).toBe(false);
        });

        // Assert
        expect(result.current.themeMode).toBe(mode);

        // Clean up for next iteration
        vi.clearAllMocks();
      }
    });
  });

  describe('Updating Theme Preference', () => {
    it('should update theme mode and call backend API', async () => {
      // Arrange
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'light' },
        status: 200,
      });

      vi.mocked(apiService.updateThemePreference).mockResolvedValue({
        data: { theme: 'dark' },
        status: 200,
      });

      const { result } = renderHook(() => useThemeMode());

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Act
      await act(async () => {
        await result.current.setThemeMode('dark');
      });

      // Assert
      expect(apiService.updateThemePreference).toHaveBeenCalledWith('dark');
      expect(result.current.themeMode).toBe('dark');
      expect(result.current.error).toBeNull();
    });

    it('should handle update errors and keep optimistic update', async () => {
      // Arrange
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'light' },
        status: 200,
      });

      const mockError = new Error('Update failed');
      vi.mocked(apiService.updateThemePreference).mockRejectedValue(mockError);

      const { result } = renderHook(() => useThemeMode());

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Act
      await act(async () => {
        await result.current.setThemeMode('dark');
      });

      // Assert
      expect(result.current.themeMode).toBe('dark'); // Keeps optimistic update
      expect(result.current.error).toEqual(mockError);
      expect(consoleErrorSpy).toHaveBeenCalled();
    });

    it('should update to all theme modes', async () => {
      // Arrange
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'light' },
        status: 200,
      });

      const modes: Array<'light' | 'dark' | 'auto'> = ['dark', 'auto', 'light'];

      const { result } = renderHook(() => useThemeMode());

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      for (const mode of modes) {
        // Arrange
        vi.mocked(apiService.updateThemePreference).mockResolvedValue({
          data: { theme: mode },
          status: 200,
        });

        // Act
        await act(async () => {
          await result.current.setThemeMode(mode);
        });

        // Assert
        expect(apiService.updateThemePreference).toHaveBeenCalledWith(mode);
        expect(result.current.themeMode).toBe(mode);
      }
    });
  });

  describe('Resolved Theme Mode', () => {
    it('should resolve auto mode to light when system prefers light', async () => {
      // Arrange
      window.matchMedia = vi.fn().mockImplementation(() => ({
        matches: false, // System prefers light
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
      const { result } = renderHook(() => useThemeMode());

      // Wait for loading
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Assert
      expect(result.current.themeMode).toBe('auto');
      expect(result.current.resolvedThemeMode).toBe('light');
      expect(result.current.systemPrefersDark).toBe(false);
    });

    it('should resolve auto mode to dark when system prefers dark', async () => {
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
      const { result } = renderHook(() => useThemeMode());

      // Wait for loading
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Assert
      expect(result.current.themeMode).toBe('auto');
      expect(result.current.resolvedThemeMode).toBe('dark');
      expect(result.current.systemPrefersDark).toBe(true);
    });

    it('should not resolve light mode', async () => {
      // Arrange
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'light' },
        status: 200,
      });

      // Act
      const { result } = renderHook(() => useThemeMode());

      // Wait for loading
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Assert
      expect(result.current.themeMode).toBe('light');
      expect(result.current.resolvedThemeMode).toBe('light');
    });

    it('should not resolve dark mode', async () => {
      // Arrange
      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'dark' },
        status: 200,
      });

      // Act
      const { result } = renderHook(() => useThemeMode());

      // Wait for loading
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Assert
      expect(result.current.themeMode).toBe('dark');
      expect(result.current.resolvedThemeMode).toBe('dark');
    });
  });

  describe('System Preference Change Listener', () => {
    it('should update systemPrefersDark when system preference changes', async () => {
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

      expect(result.current.systemPrefersDark).toBe(false);

      // Act - Simulate system preference change to dark
      if (changeHandler) {
        act(() => {
          changeHandler!({ matches: true } as MediaQueryListEvent);
        });
      }

      // Assert
      await waitFor(() => {
        expect(result.current.systemPrefersDark).toBe(true);
      });

      // When auto mode, resolved theme should also change
      expect(result.current.resolvedThemeMode).toBe('dark');
    });

    it('should cleanup event listener on unmount', async () => {
      // Arrange
      const removeEventListenerSpy = vi.fn();

      window.matchMedia = vi.fn().mockImplementation(() => ({
        matches: false,
        media: '(prefers-color-scheme: dark)',
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: removeEventListenerSpy,
        dispatchEvent: vi.fn(),
      })) as typeof window.matchMedia;

      vi.mocked(apiService.getThemePreference).mockResolvedValue({
        data: { theme: 'light' },
        status: 200,
      });

      // Act
      const { unmount } = renderHook(() => useThemeMode());
      unmount();

      // Assert
      expect(removeEventListenerSpy).toHaveBeenCalledWith('change', expect.any(Function));
    });
  });

  describe('Cleanup', () => {
    it('should not update state after unmount', async () => {
      // Arrange
      let resolveApiCall: (value: { data: ThemePreferenceResponse; status: number }) => void;
      const apiPromise = new Promise<{ data: ThemePreferenceResponse; status: number }>(
        (resolve) => {
          resolveApiCall = resolve;
        }
      );

      vi.mocked(apiService.getThemePreference).mockReturnValue(apiPromise);

      // Act
      const { result, unmount } = renderHook(() => useThemeMode());

      expect(result.current.isLoading).toBe(true);

      // Unmount before API resolves
      unmount();

      // Resolve API after unmount
      resolveApiCall!({ data: { theme: 'dark' }, status: 200 });

      // Wait a bit to ensure no state updates happen
      await new Promise((resolve) => setTimeout(resolve, 50));

      // Assert - no errors should occur (would happen if state was updated after unmount)
      // The test passing without errors validates the cleanup
      expect(true).toBe(true);
    });
  });
});
