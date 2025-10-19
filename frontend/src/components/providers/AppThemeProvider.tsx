/**
 * App Theme Provider Component
 *
 * Wrapper component that provides dynamic theme switching capability to the application.
 * Manages theme state, system preference detection, and backend synchronization.
 */

import { useMemo, type ReactNode } from 'react';
import { ThemeProvider as MuiThemeProvider, CssBaseline } from '@mui/material';
import { createAppTheme } from '@/theme';
import { useThemeMode } from '@/hooks';

/**
 * Props for AppThemeProvider component
 */
export interface AppThemeProviderProps {
  /** Child components to render within the theme provider */
  children: ReactNode;
}

/**
 * App Theme Provider
 *
 * Provides the MUI theme to the application with dynamic light/dark mode switching.
 *
 * Features:
 * - Fetches user theme preference from backend on mount
 * - Detects and responds to system theme preference changes
 * - Provides theme mode state and setter to child components via useThemeMode hook
 * - Applies smooth transitions when theme changes (225ms as per design brief)
 *
 * Usage:
 * ```tsx
 * <AppThemeProvider>
 *   <App />
 * </AppThemeProvider>
 * ```
 *
 * @param props - Component props
 * @returns Theme provider component
 */
export function AppThemeProvider({ children }: AppThemeProviderProps) {
  const { resolvedThemeMode, systemPrefersDark } = useThemeMode();

  /**
   * Create theme based on resolved theme mode
   * Memoized to prevent unnecessary theme recreations
   */
  const theme = useMemo(() => {
    return createAppTheme(resolvedThemeMode, systemPrefersDark);
  }, [resolvedThemeMode, systemPrefersDark]);

  return (
    <MuiThemeProvider theme={theme}>
      {/* CssBaseline provides consistent CSS reset across browsers */}
      <CssBaseline />
      {children}
    </MuiThemeProvider>
  );
}

export default AppThemeProvider;
