/**
 * Unit Tests for Theme Factory Functions
 *
 * Tests the createAppTheme factory and utility functions for theme creation.
 * Following TDD best practices with comprehensive test coverage.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  createAppTheme,
  getSystemThemePreference,
  getResolvedThemeMode,
} from '../../../src/theme/createAppTheme';

describe('Theme Factory Functions', () => {
  describe('createAppTheme', () => {
    describe('Light Mode', () => {
      it('should create a light theme when mode is "light"', () => {
        const theme = createAppTheme('light');

        expect(theme.palette.mode).toBe('light');
      });

      it('should use correct light mode primary colors', () => {
        const theme = createAppTheme('light');

        expect(theme.palette.primary.main).toBe('#1976d2');
        expect(theme.palette.primary.light).toBe('#42a5f5');
        expect(theme.palette.primary.dark).toBe('#1565c0');
      });

      it('should use correct light mode secondary colors', () => {
        const theme = createAppTheme('light');

        expect(theme.palette.secondary.main).toBe('#dc004e');
        expect(theme.palette.secondary.light).toBe('#f50057');
        expect(theme.palette.secondary.dark).toBe('#9a0036');
      });

      it('should use correct light mode background colors', () => {
        const theme = createAppTheme('light');

        expect(theme.palette.background.default).toBe('#fafafa');
        expect(theme.palette.background.paper).toBe('#ffffff');
      });

      it('should use correct light mode text colors', () => {
        const theme = createAppTheme('light');

        expect(theme.palette.text.primary).toBe('rgba(0, 0, 0, 0.87)');
        expect(theme.palette.text.secondary).toBe('rgba(0, 0, 0, 0.6)');
        expect(theme.palette.text.disabled).toBe('rgba(0, 0, 0, 0.38)');
      });
    });

    describe('Dark Mode', () => {
      it('should create a dark theme when mode is "dark"', () => {
        const theme = createAppTheme('dark');

        expect(theme.palette.mode).toBe('dark');
      });

      it('should use lightened primary colors for dark mode', () => {
        const theme = createAppTheme('dark');

        // Dark mode uses lighter primary for better contrast on dark backgrounds
        expect(theme.palette.primary.main).toBe('#42a5f5');
        expect(theme.palette.primary.light).toBe('#64b5f6');
        expect(theme.palette.primary.dark).toBe('#1976d2');
      });

      it('should use lightened secondary colors for dark mode', () => {
        const theme = createAppTheme('dark');

        // Dark mode uses lighter secondary for better contrast
        expect(theme.palette.secondary.main).toBe('#f48fb1');
        expect(theme.palette.secondary.light).toBe('#f6a5c0');
        expect(theme.palette.secondary.dark).toBe('#dc004e');
      });

      it('should use Material Design 3 dark background colors', () => {
        const theme = createAppTheme('dark');

        expect(theme.palette.background.default).toBe('#121212');
        expect(theme.palette.background.paper).toBe('#1e1e1e');
      });

      it('should use correct dark mode text colors', () => {
        const theme = createAppTheme('dark');

        expect(theme.palette.text.primary).toBe('rgba(255, 255, 255, 0.87)');
        expect(theme.palette.text.secondary).toBe('rgba(255, 255, 255, 0.6)');
        expect(theme.palette.text.disabled).toBe('rgba(255, 255, 255, 0.38)');
      });

      it('should use increased card elevation for dark mode', () => {
        const theme = createAppTheme('dark');

        // Dark mode cards use elevation 2 instead of 1
        expect(theme.components?.MuiCard?.defaultProps?.elevation).toBe(2);
      });

      it('should configure AppBar for dark mode', () => {
        const theme = createAppTheme('dark');

        const appBarStyles = theme.components?.MuiAppBar?.styleOverrides?.root as Record<
          string,
          unknown
        >;
        expect(appBarStyles.backgroundColor).toBe('#1e1e1e');
        expect(appBarStyles.borderBottom).toBe('1px solid rgba(255, 255, 255, 0.12)');
      });
    });

    describe('Auto Mode', () => {
      it('should create light theme for auto mode when system prefers light', () => {
        const theme = createAppTheme('auto', false);

        expect(theme.palette.mode).toBe('light');
        expect(theme.palette.background.default).toBe('#fafafa');
      });

      it('should create dark theme for auto mode when system prefers dark', () => {
        const theme = createAppTheme('auto', true);

        expect(theme.palette.mode).toBe('dark');
        expect(theme.palette.background.default).toBe('#121212');
      });
    });

    describe('Shared Theme Properties', () => {
      it('should apply typography configuration to both themes', () => {
        const lightTheme = createAppTheme('light');
        const darkTheme = createAppTheme('dark');

        expect(lightTheme.typography.fontFamily).toBe('"Roboto", "Helvetica", "Arial", sans-serif');
        expect(darkTheme.typography.fontFamily).toBe('"Roboto", "Helvetica", "Arial", sans-serif');

        expect(lightTheme.typography.fontSize).toBe(16);
        expect(darkTheme.typography.fontSize).toBe(16);
      });

      it('should apply spacing configuration to both themes', () => {
        const lightTheme = createAppTheme('light');
        const darkTheme = createAppTheme('dark');

        // MUI v7 spacing returns strings with 'px' suffix
        expect(lightTheme.spacing(1)).toBe('8px');
        expect(darkTheme.spacing(1)).toBe('8px');

        expect(lightTheme.spacing(2)).toBe('16px');
        expect(darkTheme.spacing(2)).toBe('16px');
      });

      it('should apply shape configuration to both themes', () => {
        const lightTheme = createAppTheme('light');
        const darkTheme = createAppTheme('dark');

        expect(lightTheme.shape.borderRadius).toBe(4);
        expect(darkTheme.shape.borderRadius).toBe(4);
      });

      it('should apply breakpoints to both themes', () => {
        const lightTheme = createAppTheme('light');
        const darkTheme = createAppTheme('dark');

        expect(lightTheme.breakpoints.values).toEqual({
          xs: 0,
          sm: 600,
          md: 900,
          lg: 1200,
          xl: 1536,
        });

        expect(darkTheme.breakpoints.values).toEqual({
          xs: 0,
          sm: 600,
          md: 900,
          lg: 1200,
          xl: 1536,
        });
      });

      it('should disable text transform on buttons for both themes', () => {
        const lightTheme = createAppTheme('light');
        const darkTheme = createAppTheme('dark');

        const lightButtonStyles = lightTheme.components?.MuiButton?.styleOverrides?.root as Record<
          string,
          unknown
        >;
        const darkButtonStyles = darkTheme.components?.MuiButton?.styleOverrides?.root as Record<
          string,
          unknown
        >;

        expect(lightButtonStyles.textTransform).toBe('none');
        expect(darkButtonStyles.textTransform).toBe('none');
      });
    });

    describe('Semantic Colors', () => {
      it('should adjust error colors for dark mode', () => {
        const lightTheme = createAppTheme('light');
        const darkTheme = createAppTheme('dark');

        expect(lightTheme.palette.error.main).toBe('#d32f2f');
        expect(darkTheme.palette.error.main).toBe('#f44336');
      });

      it('should adjust warning colors for dark mode', () => {
        const lightTheme = createAppTheme('light');
        const darkTheme = createAppTheme('dark');

        expect(lightTheme.palette.warning.main).toBe('#ed6c02');
        expect(darkTheme.palette.warning.main).toBe('#ff9800');
      });

      it('should adjust info colors for dark mode', () => {
        const lightTheme = createAppTheme('light');
        const darkTheme = createAppTheme('dark');

        expect(lightTheme.palette.info.main).toBe('#0288d1');
        expect(darkTheme.palette.info.main).toBe('#29b6f6');
      });

      it('should adjust success colors for dark mode', () => {
        const lightTheme = createAppTheme('light');
        const darkTheme = createAppTheme('dark');

        expect(lightTheme.palette.success.main).toBe('#2e7d32');
        expect(darkTheme.palette.success.main).toBe('#66bb6a');
      });
    });
  });

  describe('getSystemThemePreference', () => {
    let matchMediaMock: typeof window.matchMedia;

    beforeEach(() => {
      // Store original matchMedia
      matchMediaMock = window.matchMedia;
    });

    afterEach(() => {
      // Restore original matchMedia
      window.matchMedia = matchMediaMock;
    });

    it('should return true when system prefers dark mode', () => {
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

      const prefersDark = getSystemThemePreference();

      expect(prefersDark).toBe(true);
      expect(window.matchMedia).toHaveBeenCalledWith('(prefers-color-scheme: dark)');
    });

    it('should return false when system prefers light mode', () => {
      window.matchMedia = vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })) as typeof window.matchMedia;

      const prefersDark = getSystemThemePreference();

      expect(prefersDark).toBe(false);
    });
  });

  describe('getResolvedThemeMode', () => {
    it('should return "light" when mode is "light"', () => {
      const resolved = getResolvedThemeMode('light');

      expect(resolved).toBe('light');
    });

    it('should return "dark" when mode is "dark"', () => {
      const resolved = getResolvedThemeMode('dark');

      expect(resolved).toBe('dark');
    });

    it('should return "light" for auto mode when system prefers light', () => {
      const resolved = getResolvedThemeMode('auto', false);

      expect(resolved).toBe('light');
    });

    it('should return "dark" for auto mode when system prefers dark', () => {
      const resolved = getResolvedThemeMode('auto', true);

      expect(resolved).toBe('dark');
    });
  });
});
