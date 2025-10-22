/**
 * Theme Hook
 *
 * Provides access to theme context and theme mode utilities.
 * Separated from component exports to support hot module replacement (HMR).
 */

import { useContext, createContext } from 'react';

export type ThemeMode = 'light' | 'dark';

export interface ThemeContextValue {
  mode: ThemeMode;
  toggleTheme: () => void;
  setThemeMode: (mode: ThemeMode) => void;
}

// Create and export the context so it can be imported by ThemeProvider
export const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

/**
 * Hook to access theme context
 * @throws Error if used outside of ThemeProvider
 * @returns Theme context value with mode and theme control functions
 */
export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
