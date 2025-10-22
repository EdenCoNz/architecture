/**
 * Theme Context
 *
 * Provides theme mode state management for the application.
 * Enables switching between light and dark themes.
 * Persists theme preference to localStorage for cross-session continuity.
 */

import { createContext, useContext, useState, useMemo, useEffect } from 'react';
import type { ReactNode } from 'react';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { lightTheme, darkTheme } from '../theme';

export type ThemeMode = 'light' | 'dark';

interface ThemeContextValue {
  mode: ThemeMode;
  toggleTheme: () => void;
  setThemeMode: (mode: ThemeMode) => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

const STORAGE_KEY = 'theme-mode';

/**
 * Load theme preference from localStorage
 * @param defaultMode - Default mode to use if localStorage is empty or has invalid value
 * @returns The theme mode from localStorage or the default mode
 */
function loadThemeFromStorage(defaultMode: ThemeMode): ThemeMode {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'light' || stored === 'dark') {
      return stored;
    }
  } catch (error) {
    // localStorage not available or error reading
    console.warn('Failed to load theme from localStorage:', error);
  }
  return defaultMode;
}

/**
 * Save theme preference to localStorage
 * @param mode - Theme mode to save
 */
function saveThemeToStorage(mode: ThemeMode): void {
  try {
    localStorage.setItem(STORAGE_KEY, mode);
  } catch (error) {
    // localStorage not available or quota exceeded
    console.warn('Failed to save theme to localStorage:', error);
  }
}

interface ThemeProviderProps {
  children: ReactNode;
  defaultMode?: ThemeMode;
}

export function ThemeProvider({ children, defaultMode = 'light' }: ThemeProviderProps) {
  // Initialize state with theme from localStorage or defaultMode
  const [mode, setMode] = useState<ThemeMode>(() => {
    // Load from localStorage, using defaultMode as fallback
    return loadThemeFromStorage(defaultMode);
  });

  // Save theme to localStorage whenever it changes
  useEffect(() => {
    saveThemeToStorage(mode);
  }, [mode]);

  const toggleTheme = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  const setThemeMode = (newMode: ThemeMode) => {
    setMode(newMode);
  };

  const theme = useMemo(() => (mode === 'light' ? lightTheme : darkTheme), [mode]);

  const contextValue = useMemo(
    () => ({
      mode,
      toggleTheme,
      setThemeMode,
    }),
    [mode]
  );

  return (
    <ThemeContext.Provider value={contextValue}>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
