/**
 * Theme Slice Tests
 *
 * Unit tests for theme state management including mode switching,
 * system preference detection, and state persistence.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import themeReducer, {
  setThemeMode,
  toggleTheme,
  initializeTheme,
  selectThemeMode,
  selectEffectiveTheme,
  type ThemeMode,
  type ThemeState,
} from './themeSlice';

describe('themeSlice', () => {
  describe('reducer', () => {
    let initialState: ThemeState;

    beforeEach(() => {
      initialState = {
        mode: 'light',
      };
    });

    it('should return initial state when called with undefined', () => {
      const state = themeReducer(undefined, { type: 'unknown' });
      expect(state).toEqual({ mode: 'light' });
    });

    describe('setThemeMode', () => {
      it('should set theme mode to light', () => {
        const state = themeReducer(initialState, setThemeMode('light'));
        expect(state.mode).toBe('light');
      });

      it('should set theme mode to dark', () => {
        const state = themeReducer(initialState, setThemeMode('dark'));
        expect(state.mode).toBe('dark');
      });

      it('should set theme mode to auto', () => {
        const state = themeReducer(initialState, setThemeMode('auto'));
        expect(state.mode).toBe('auto');
      });

      it('should transition from dark to light', () => {
        const darkState: ThemeState = { mode: 'dark' };
        const state = themeReducer(darkState, setThemeMode('light'));
        expect(state.mode).toBe('light');
      });

      it('should transition from auto to dark', () => {
        const autoState: ThemeState = { mode: 'auto' };
        const state = themeReducer(autoState, setThemeMode('dark'));
        expect(state.mode).toBe('dark');
      });
    });

    describe('toggleTheme', () => {
      it('should toggle from light to dark', () => {
        const state = themeReducer(initialState, toggleTheme());
        expect(state.mode).toBe('dark');
      });

      it('should toggle from dark to light', () => {
        const darkState: ThemeState = { mode: 'dark' };
        const state = themeReducer(darkState, toggleTheme());
        expect(state.mode).toBe('light');
      });

      it('should toggle from auto to dark', () => {
        const autoState: ThemeState = { mode: 'auto' };
        const state = themeReducer(autoState, toggleTheme());
        expect(state.mode).toBe('dark');
      });
    });

    describe('initializeTheme', () => {
      it('should set theme from payload', () => {
        const state = themeReducer(initialState, initializeTheme('dark'));
        expect(state.mode).toBe('dark');
      });

      it('should default to light if no payload provided', () => {
        const state = themeReducer(initialState, initializeTheme(undefined as any));
        expect(state.mode).toBe('light');
      });
    });
  });

  describe('selectors', () => {
    it('selectThemeMode should return current theme mode', () => {
      const state = { theme: { mode: 'dark' as ThemeMode } };
      expect(selectThemeMode(state as any)).toBe('dark');
    });

    it('selectEffectiveTheme should return light when mode is light', () => {
      const state = { theme: { mode: 'light' as ThemeMode } };
      expect(selectEffectiveTheme(state as any)).toBe('light');
    });

    it('selectEffectiveTheme should return dark when mode is dark', () => {
      const state = { theme: { mode: 'dark' as ThemeMode } };
      expect(selectEffectiveTheme(state as any)).toBe('dark');
    });

    it('selectEffectiveTheme should return system preference when mode is auto', () => {
      const state = { theme: { mode: 'auto' as ThemeMode } };

      // Mock prefers-color-scheme: dark
      const mockMatchMedia = vi.fn().mockImplementation((query: string) => ({
        matches: query === '(prefers-color-scheme: dark)',
        media: query,
        onchange: null,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      }));

      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: mockMatchMedia,
      });

      expect(selectEffectiveTheme(state as any)).toBe('dark');
    });

    it('selectEffectiveTheme should default to light when auto and no preference', () => {
      const state = { theme: { mode: 'auto' as ThemeMode } };

      // Mock no dark mode preference
      const mockMatchMedia = vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      }));

      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: mockMatchMedia,
      });

      expect(selectEffectiveTheme(state as any)).toBe('light');
    });
  });
});
