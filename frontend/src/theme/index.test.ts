/**
 * Tests for MUI Theme Configuration with Dark Mode Support
 *
 * Tests verify:
 * - Theme palette switches correctly between light and dark modes
 * - Dark mode colors meet WCAG AA contrast requirements
 * - All color tokens are properly defined
 */

import { describe, it, expect } from 'vitest';
import { createAppTheme } from './index';

describe('Theme Configuration', () => {
  describe('Light Mode', () => {
    it('should create theme with light mode palette when mode is light', () => {
      const theme = createAppTheme('light');

      expect(theme.palette.mode).toBe('light');
      expect(theme.palette.background.default).toBe('#fafafa');
      expect(theme.palette.background.paper).toBe('#ffffff');
      expect(theme.palette.text.primary).toBe('rgba(0, 0, 0, 0.87)');
      expect(theme.palette.text.secondary).toBe('rgba(0, 0, 0, 0.6)');
    });

    it('should have correct primary colors for light mode', () => {
      const theme = createAppTheme('light');

      expect(theme.palette.primary.main).toBe('#1976d2');
      expect(theme.palette.primary.light).toBe('#42a5f5');
      expect(theme.palette.primary.dark).toBe('#1565c0');
      expect(theme.palette.primary.contrastText).toBe('#ffffff');
    });

    it('should have correct secondary colors for light mode', () => {
      const theme = createAppTheme('light');

      expect(theme.palette.secondary.main).toBe('#dc004e');
      expect(theme.palette.secondary.light).toBe('#f50057');
      expect(theme.palette.secondary.dark).toBe('#9a0036');
      expect(theme.palette.secondary.contrastText).toBe('#ffffff');
    });

    it('should have correct semantic colors for light mode', () => {
      const theme = createAppTheme('light');

      expect(theme.palette.error.main).toBe('#d32f2f');
      expect(theme.palette.warning.main).toBe('#ed6c02');
      expect(theme.palette.info.main).toBe('#0288d1');
      expect(theme.palette.success.main).toBe('#2e7d32');
    });
  });

  describe('Dark Mode', () => {
    it('should create theme with dark mode palette when mode is dark', () => {
      const theme = createAppTheme('dark');

      expect(theme.palette.mode).toBe('dark');
      expect(theme.palette.background.default).toBe('#121212');
      expect(theme.palette.background.paper).toBe('#1e1e1e');
      expect(theme.palette.text.primary).toBe('rgba(255, 255, 255, 0.87)');
      expect(theme.palette.text.secondary).toBe('rgba(255, 255, 255, 0.6)');
    });

    it('should have correct primary colors for dark mode', () => {
      const theme = createAppTheme('dark');

      expect(theme.palette.primary.main).toBe('#90caf9');
      expect(theme.palette.primary.light).toBe('#bbdefb');
      expect(theme.palette.primary.dark).toBe('#42a5f5');
    });

    it('should have correct secondary colors for dark mode', () => {
      const theme = createAppTheme('dark');

      expect(theme.palette.secondary.main).toBe('#f48fb1');
      expect(theme.palette.secondary.light).toBe('#ffc1e3');
      expect(theme.palette.secondary.dark).toBe('#bf5f82');
    });

    it('should have correct semantic colors for dark mode', () => {
      const theme = createAppTheme('dark');

      expect(theme.palette.error.main).toBe('#f44336');
      expect(theme.palette.warning.main).toBe('#ffa726');
      expect(theme.palette.info.main).toBe('#29b6f6');
      expect(theme.palette.success.main).toBe('#66bb6a');
    });

    it('should have correct divider color for dark mode', () => {
      const theme = createAppTheme('dark');

      expect(theme.palette.divider).toBe('rgba(255, 255, 255, 0.12)');
    });

    it('should have correct action colors for dark mode', () => {
      const theme = createAppTheme('dark');

      expect(theme.palette.action.hover).toBe('rgba(255, 255, 255, 0.08)');
      expect(theme.palette.action.selected).toBe('rgba(255, 255, 255, 0.16)');
      expect(theme.palette.action.disabledBackground).toBe('rgba(255, 255, 255, 0.12)');
    });
  });

  describe('Theme Switching', () => {
    it('should switch from light to dark mode correctly', () => {
      const lightTheme = createAppTheme('light');
      const darkTheme = createAppTheme('dark');

      // Verify mode changed
      expect(lightTheme.palette.mode).toBe('light');
      expect(darkTheme.palette.mode).toBe('dark');

      // Verify backgrounds switched
      expect(lightTheme.palette.background.default).not.toBe(darkTheme.palette.background.default);
      expect(lightTheme.palette.background.paper).not.toBe(darkTheme.palette.background.paper);

      // Verify text colors inverted
      expect(lightTheme.palette.text.primary).toContain('0, 0, 0');
      expect(darkTheme.palette.text.primary).toContain('255, 255, 255');
    });

    it('should maintain theme structure across modes', () => {
      const lightTheme = createAppTheme('light');
      const darkTheme = createAppTheme('dark');

      // Both themes should have same typography settings
      expect(lightTheme.typography.fontFamily).toBe(darkTheme.typography.fontFamily);
      expect(lightTheme.typography.fontSize).toBe(darkTheme.typography.fontSize);
      expect(lightTheme.typography.h1.fontSize).toBe(darkTheme.typography.h1.fontSize);
      expect(lightTheme.typography.body1.fontSize).toBe(darkTheme.typography.body1.fontSize);

      // Both themes should have same spacing
      expect(lightTheme.spacing(1)).toBe(darkTheme.spacing(1));
      expect(lightTheme.spacing(2)).toBe(darkTheme.spacing(2));

      // Both themes should have same shape
      expect(lightTheme.shape.borderRadius).toBe(darkTheme.shape.borderRadius);

      // Both themes should have same breakpoints
      expect(lightTheme.breakpoints.values).toEqual(darkTheme.breakpoints.values);
    });
  });

  describe('WCAG AA Contrast Requirements', () => {
    /**
     * Helper function to calculate relative luminance
     * Based on WCAG 2.1 specification
     */
    function getLuminance(hexColor: string): number {
      const rgb = hexColor.match(/^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i);
      if (!rgb) {
        throw new Error('Invalid hex color');
      }

      const [, r, g, b] = rgb;
      const [rVal, gVal, bVal] = [r, g, b].map((val) => {
        const channel = parseInt(val, 16) / 255;
        return channel <= 0.03928 ? channel / 12.92 : Math.pow((channel + 0.055) / 1.055, 2.4);
      });

      return 0.2126 * rVal + 0.7152 * gVal + 0.0722 * bVal;
    }

    /**
     * Helper function to calculate contrast ratio between two colors
     * Based on WCAG 2.1 specification
     */
    function getContrastRatio(color1: string, color2: string): number {
      const lum1 = getLuminance(color1);
      const lum2 = getLuminance(color2);
      const lighter = Math.max(lum1, lum2);
      const darker = Math.min(lum1, lum2);
      return (lighter + 0.05) / (darker + 0.05);
    }

    it('should meet WCAG AA contrast for dark mode text on background (minimum 4.5:1)', () => {
      const theme = createAppTheme('dark');
      const backgroundColor = theme.palette.background.default; // #121212

      // Calculate contrast for primary text (rgba format needs conversion)
      // For testing purposes, we use the actual hex approximation
      // rgba(255, 255, 255, 0.87) on #121212 ≈ #dedede
      const primaryTextApprox = '#dedede';
      const primaryTextContrast = getContrastRatio(primaryTextApprox, backgroundColor);

      expect(primaryTextContrast).toBeGreaterThanOrEqual(4.5);
    });

    it('should meet WCAG AA contrast for dark mode primary color on background (minimum 3:1)', () => {
      const theme = createAppTheme('dark');
      const backgroundColor = theme.palette.background.default; // #121212
      const primaryColor = theme.palette.primary.main; // #90caf9

      const contrast = getContrastRatio(primaryColor, backgroundColor);

      expect(contrast).toBeGreaterThanOrEqual(3.0);
    });

    it('should meet WCAG AA contrast for dark mode secondary color on background (minimum 3:1)', () => {
      const theme = createAppTheme('dark');
      const backgroundColor = theme.palette.background.default; // #121212
      const secondaryColor = theme.palette.secondary.main; // #f48fb1

      const contrast = getContrastRatio(secondaryColor, backgroundColor);

      expect(contrast).toBeGreaterThanOrEqual(3.0);
    });

    it('should meet WCAG AA contrast for dark mode error color on background (minimum 3:1)', () => {
      const theme = createAppTheme('dark');
      const backgroundColor = theme.palette.background.default; // #121212
      const errorColor = theme.palette.error.main; // #f44336

      const contrast = getContrastRatio(errorColor, backgroundColor);

      expect(contrast).toBeGreaterThanOrEqual(3.0);
    });

    it('should meet WCAG AA contrast for dark mode warning color on background (minimum 3:1)', () => {
      const theme = createAppTheme('dark');
      const backgroundColor = theme.palette.background.default; // #121212
      const warningColor = theme.palette.warning.main; // #ffa726

      const contrast = getContrastRatio(warningColor, backgroundColor);

      expect(contrast).toBeGreaterThanOrEqual(3.0);
    });

    it('should meet WCAG AA contrast for dark mode info color on background (minimum 3:1)', () => {
      const theme = createAppTheme('dark');
      const backgroundColor = theme.palette.background.default; // #121212
      const infoColor = theme.palette.info.main; // #29b6f6

      const contrast = getContrastRatio(infoColor, backgroundColor);

      expect(contrast).toBeGreaterThanOrEqual(3.0);
    });

    it('should meet WCAG AA contrast for dark mode success color on background (minimum 3:1)', () => {
      const theme = createAppTheme('dark');
      const backgroundColor = theme.palette.background.default; // #121212
      const successColor = theme.palette.success.main; // #66bb6a

      const contrast = getContrastRatio(successColor, backgroundColor);

      expect(contrast).toBeGreaterThanOrEqual(3.0);
    });
  });

  describe('Component Overrides', () => {
    it('should maintain component overrides across both modes', () => {
      const lightTheme = createAppTheme('light');
      const darkTheme = createAppTheme('dark');

      // Button overrides
      expect(lightTheme.components?.MuiButton?.styleOverrides?.root).toEqual(
        darkTheme.components?.MuiButton?.styleOverrides?.root
      );

      // Card overrides
      expect(lightTheme.components?.MuiCard?.defaultProps).toEqual(
        darkTheme.components?.MuiCard?.defaultProps
      );

      // AppBar overrides
      expect(lightTheme.components?.MuiAppBar?.defaultProps?.elevation).toBe(0);
      expect(darkTheme.components?.MuiAppBar?.defaultProps?.elevation).toBe(0);
    });

    it('should adapt AppBar border color for dark mode', () => {
      const darkTheme = createAppTheme('dark');

      const appBarBorder = darkTheme.components?.MuiAppBar?.styleOverrides?.root as {
        borderBottom?: string;
      };
      expect(appBarBorder?.borderBottom).toBe('1px solid rgba(255, 255, 255, 0.12)');
    });
  });

  describe('Default Mode', () => {
    it('should default to light mode when no mode specified', () => {
      const theme = createAppTheme();

      expect(theme.palette.mode).toBe('light');
    });
  });
});
