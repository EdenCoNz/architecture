/**
 * Theme Middleware
 *
 * Redux middleware for persisting theme preference to localStorage
 * and syncing theme changes across tabs.
 */

import type { Middleware } from '@reduxjs/toolkit';
import { setThemeMode, toggleTheme, type ThemeMode } from '../slices/themeSlice';

const THEME_STORAGE_KEY = 'app-theme-mode';

/**
 * Saves theme preference to localStorage
 */
export const saveThemeToStorage = (mode: ThemeMode): void => {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, mode);
  } catch (error) {
    console.warn('Failed to save theme preference:', error);
  }
};

/**
 * Loads theme preference from localStorage
 */
export const loadThemeFromStorage = (): ThemeMode | null => {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored && ['light', 'dark', 'auto'].includes(stored)) {
      return stored as ThemeMode;
    }
  } catch (error) {
    console.warn('Failed to load theme preference:', error);
  }
  return null;
};

/**
 * Middleware that persists theme changes to localStorage
 */
export const themeMiddleware: Middleware = (storeApi) => (next) => (action) => {
  const result = next(action);

  // Save to localStorage when theme changes
  if (setThemeMode.match(action) || toggleTheme.match(action)) {
    const state = storeApi.getState() as { theme: { mode: ThemeMode } };
    if (state?.theme?.mode) {
      saveThemeToStorage(state.theme.mode);
    }
  }

  return result;
};

export default themeMiddleware;
