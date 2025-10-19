/**
 * Theme Slice
 *
 * Redux state management for application theme (light/dark/auto mode).
 * Supports manual selection and automatic system preference detection.
 */

import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

export type ThemeMode = 'light' | 'dark' | 'auto';
export type EffectiveTheme = 'light' | 'dark';

export interface ThemeState {
  mode: ThemeMode;
}

const initialState: ThemeState = {
  mode: 'light',
};

/**
 * Detects system color scheme preference
 */
const getSystemTheme = (): EffectiveTheme => {
  if (typeof window === 'undefined') {
    return 'light';
  }

  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  return prefersDark ? 'dark' : 'light';
};

const themeSlice = createSlice({
  name: 'theme',
  initialState,
  reducers: {
    /**
     * Sets the theme mode to a specific value
     */
    setThemeMode: (state, action: PayloadAction<ThemeMode>) => {
      state.mode = action.payload;
    },

    /**
     * Toggles between light and dark mode
     * If in auto mode, switches to light first
     */
    toggleTheme: (state) => {
      if (state.mode === 'dark') {
        state.mode = 'light';
      } else {
        // From 'light' or 'auto', go to dark
        state.mode = 'dark';
      }
    },

    /**
     * Initializes theme from persisted storage or defaults
     */
    initializeTheme: (state, action: PayloadAction<ThemeMode | undefined>) => {
      state.mode = action.payload || 'light';
    },
  },
});

// Actions
export const { setThemeMode, toggleTheme, initializeTheme } = themeSlice.actions;

// Selectors
export const selectThemeMode = (state: { theme: ThemeState }): ThemeMode => state.theme.mode;

export const selectEffectiveTheme = (state: { theme: ThemeState }): EffectiveTheme => {
  const mode = state.theme.mode;

  if (mode === 'auto') {
    return getSystemTheme();
  }

  return mode;
};

// Reducer
export default themeSlice.reducer;
