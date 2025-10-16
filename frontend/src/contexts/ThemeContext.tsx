/**
 * ThemeContext - Theme Mode State Management
 *
 * Provides theme mode (light/dark) state management with:
 * - localStorage persistence
 * - System preference detection via prefers-color-scheme
 * - Theme toggle functionality
 *
 * Usage:
 * ```tsx
 * import { ThemeProvider, useTheme } from './contexts/ThemeContext';
 *
 * // Wrap app with provider
 * <ThemeProvider>
 *   <App />
 * </ThemeProvider>
 *
 * // Use in components
 * const { mode, toggleTheme } = useTheme();
 * ```
 */

import { createContext, useContext, useState, useMemo, type ReactNode } from 'react';

/**
 * Type definition for theme mode
 */
export type ThemeMode = 'light' | 'dark';

/**
 * Theme context value interface
 */
interface ThemeContextValue {
  /** Current theme mode (light or dark) */
  mode: ThemeMode;
  /** Function to toggle between light and dark modes */
  toggleTheme: () => void;
}

/**
 * localStorage key for persisting theme preference
 */
const THEME_STORAGE_KEY = 'themeMode';

/**
 * Create theme context with null default
 * Null indicates context is not yet initialized
 */
const ThemeContext = createContext<ThemeContextValue | null>(null);

/**
 * ThemeProvider Props
 */
interface ThemeProviderProps {
  /** Child components that will have access to theme context */
  children: ReactNode;
}

/**
 * Detects system color scheme preference
 * @returns 'dark' if system prefers dark mode, 'light' otherwise
 */
const getSystemPreference = (): ThemeMode => {
  // Check if matchMedia is available (SSR compatibility)
  if (typeof window === 'undefined' || !window.matchMedia) {
    return 'light';
  }

  // Query system preference
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  return prefersDark ? 'dark' : 'light';
};

/**
 * Gets initial theme mode from localStorage or system preference
 * Priority: localStorage > system preference > default to light
 * @returns Initial theme mode
 */
const getInitialThemeMode = (): ThemeMode => {
  // Try to get from localStorage first
  const storedMode = localStorage.getItem(THEME_STORAGE_KEY);

  if (storedMode === 'light' || storedMode === 'dark') {
    return storedMode;
  }

  // Fall back to system preference
  return getSystemPreference();
};

/**
 * ThemeProvider Component
 *
 * Manages theme mode state and provides it to child components.
 * Handles localStorage persistence and system preference detection.
 *
 * @example
 * ```tsx
 * <ThemeProvider>
 *   <App />
 * </ThemeProvider>
 * ```
 */
export function ThemeProvider({ children }: ThemeProviderProps) {
  // Initialize theme mode from localStorage or system preference
  const [mode, setMode] = useState<ThemeMode>(getInitialThemeMode);

  /**
   * Toggle theme between light and dark modes
   * Persists preference to localStorage
   */
  const toggleTheme = () => {
    setMode((prevMode) => {
      const newMode = prevMode === 'light' ? 'dark' : 'light';
      // Persist to localStorage
      localStorage.setItem(THEME_STORAGE_KEY, newMode);
      return newMode;
    });
  };

  // Memoize context value to prevent unnecessary re-renders
  const contextValue = useMemo(
    () => ({
      mode,
      toggleTheme,
    }),
    [mode]
  );

  return <ThemeContext.Provider value={contextValue}>{children}</ThemeContext.Provider>;
}

/**
 * useTheme Hook
 *
 * Custom hook to access theme context in components.
 * Provides theme mode and toggle function.
 *
 * @throws {Error} If used outside ThemeProvider
 * @returns Theme context value with mode and toggleTheme
 *
 * @example
 * ```tsx
 * const { mode, toggleTheme } = useTheme();
 *
 * return (
 *   <div>
 *     <p>Current mode: {mode}</p>
 *     <button onClick={toggleTheme}>Toggle Theme</button>
 *   </div>
 * );
 * ```
 */
export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);

  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }

  return context;
}
