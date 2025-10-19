/**
 * Theme Context
 *
 * React context for accessing and controlling theme mode throughout the application.
 * Provides theme mode state and setter function to all child components.
 */

import { createContext, useContext, type ReactNode } from 'react';
import { useThemeMode, type UseThemeModeReturn } from '@/hooks';

/**
 * Theme context type
 */
export type ThemeContextType = UseThemeModeReturn;

/**
 * Theme context - provides theme mode state and controls
 */
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

/**
 * Props for ThemeContextProvider component
 */
export interface ThemeContextProviderProps {
  /** Child components */
  children: ReactNode;
}

/**
 * Theme Context Provider
 *
 * Provides theme mode state and controls to all child components.
 *
 * @param props - Component props
 * @returns Context provider component
 */
export function ThemeContextProvider({ children }: ThemeContextProviderProps) {
  const themeModeState = useThemeMode();

  return <ThemeContext.Provider value={themeModeState}>{children}</ThemeContext.Provider>;
}

/**
 * Custom hook to access theme context
 *
 * @throws Error if used outside of ThemeContextProvider
 * @returns Theme context value
 */
// eslint-disable-next-line react-refresh/only-export-components
export function useThemeContext(): ThemeContextType {
  const context = useContext(ThemeContext);

  if (context === undefined) {
    throw new Error('useThemeContext must be used within a ThemeContextProvider');
  }

  return context;
}
