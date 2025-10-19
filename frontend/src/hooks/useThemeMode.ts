/**
 * useThemeMode Hook
 *
 * Custom React hook for managing theme mode state with backend synchronization.
 * Handles theme preference loading, system preference detection, and persistence.
 */

import { useState, useEffect, useCallback } from 'react';
import type { ThemeMode } from '@/types';
import { apiService } from '@/services/api';
import { getSystemThemePreference } from '@/theme';

/**
 * Hook return type
 */
export interface UseThemeModeReturn {
  /** Current theme mode */
  themeMode: ThemeMode;
  /** Resolved theme mode (converts 'auto' to 'light' or 'dark') */
  resolvedThemeMode: 'light' | 'dark';
  /** System preference for dark mode */
  systemPrefersDark: boolean;
  /** Loading state while fetching preference */
  isLoading: boolean;
  /** Error state */
  error: Error | null;
  /** Function to update theme mode */
  setThemeMode: (mode: ThemeMode) => Promise<void>;
}

/**
 * Custom hook for managing theme mode
 *
 * Features:
 * - Fetches user preference from backend on mount
 * - Detects system theme preference for 'auto' mode
 * - Persists theme changes to backend
 * - Listens for system theme changes
 * - Handles loading and error states
 *
 * @returns UseThemeModeReturn object with theme state and controls
 */
export function useThemeMode(): UseThemeModeReturn {
  const [themeMode, setThemeModeState] = useState<ThemeMode>('auto');
  const [systemPrefersDark, setSystemPrefersDark] = useState(getSystemThemePreference());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  /**
   * Load theme preference from backend on mount
   */
  useEffect(() => {
    let isMounted = true;

    const loadThemePreference = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const response = await apiService.getThemePreference();

        if (isMounted) {
          setThemeModeState(response.data.theme);
        }
      } catch (err) {
        if (isMounted) {
          // If API fails, keep default 'auto' mode
          console.warn('Failed to load theme preference, using auto mode:', err);
          setError(err instanceof Error ? err : new Error('Failed to load theme preference'));
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadThemePreference();

    return () => {
      isMounted = false;
    };
  }, []);

  /**
   * Listen for system theme preference changes
   */
  useEffect(() => {
    // Check if matchMedia is supported (older browsers may not have it)
    if (typeof window.matchMedia !== 'function') {
      return; // No cleanup needed
    }

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = (e: MediaQueryListEvent) => {
      setSystemPrefersDark(e.matches);
    };

    // Modern browsers use addEventListener
    mediaQuery.addEventListener('change', handleChange);

    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  /**
   * Update theme mode and persist to backend
   */
  const setThemeMode = useCallback(async (mode: ThemeMode) => {
    try {
      setError(null);

      // Optimistically update local state
      setThemeModeState(mode);

      // Persist to backend
      await apiService.updateThemePreference(mode);
    } catch (err) {
      console.error('Failed to update theme preference:', err);
      setError(err instanceof Error ? err : new Error('Failed to update theme preference'));

      // Optionally: revert optimistic update on error
      // For now, we keep the optimistic update since the user explicitly chose it
    }
  }, []);

  /**
   * Resolve 'auto' mode to actual theme based on system preference
   */
  const resolvedThemeMode =
    themeMode === 'auto' ? (systemPrefersDark ? 'dark' : 'light') : themeMode;

  return {
    themeMode,
    resolvedThemeMode,
    systemPrefersDark,
    isLoading,
    error,
    setThemeMode,
  };
}
