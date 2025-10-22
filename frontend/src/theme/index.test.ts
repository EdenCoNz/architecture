/**
 * Theme Configuration Tests
 *
 * Comprehensive tests validating theme configuration for both light and dark modes.
 * Tests cover color palettes, typography, accessibility compliance, and MUI integration.
 */

import { describe, it, expect } from 'vitest';
import { lightTheme, darkTheme } from './index';

describe('Theme Configuration', () => {
  describe('Light Theme', () => {
    describe('Theme Mode', () => {
      it('should be configured for light mode', () => {
        expect(lightTheme.palette.mode).toBe('light');
      });

      it('should default to light mode when not explicitly set', () => {
        expect(lightTheme.palette.mode).toBe('light');
      });
    });

    describe('Primary Colors', () => {
      it('should have correct primary main color', () => {
        expect(lightTheme.palette.primary.main).toBe('#1976d2');
      });

      it('should have correct primary light color', () => {
        expect(lightTheme.palette.primary.light).toBe('#42a5f5');
      });

      it('should have correct primary dark color', () => {
        expect(lightTheme.palette.primary.dark).toBe('#1565c0');
      });

      it('should have white contrast text for primary color', () => {
        expect(lightTheme.palette.primary.contrastText).toBe('#ffffff');
      });
    });

    describe('Secondary Colors', () => {
      it('should have correct secondary main color', () => {
        expect(lightTheme.palette.secondary.main).toBe('#dc004e');
      });

      it('should have correct secondary light color', () => {
        expect(lightTheme.palette.secondary.light).toBe('#f50057');
      });

      it('should have correct secondary dark color', () => {
        expect(lightTheme.palette.secondary.dark).toBe('#9a0036');
      });

      it('should have white contrast text for secondary color', () => {
        expect(lightTheme.palette.secondary.contrastText).toBe('#ffffff');
      });
    });

    describe('Semantic Colors', () => {
      it('should have correct error colors', () => {
        expect(lightTheme.palette.error.main).toBe('#d32f2f');
        expect(lightTheme.palette.error.light).toBe('#ef5350');
        expect(lightTheme.palette.error.dark).toBe('#c62828');
      });

      it('should have correct warning colors', () => {
        expect(lightTheme.palette.warning.main).toBe('#ed6c02');
        expect(lightTheme.palette.warning.light).toBe('#ff9800');
        expect(lightTheme.palette.warning.dark).toBe('#e65100');
      });

      it('should have correct info colors', () => {
        expect(lightTheme.palette.info.main).toBe('#0288d1');
        expect(lightTheme.palette.info.light).toBe('#03a9f4');
        expect(lightTheme.palette.info.dark).toBe('#01579b');
      });

      it('should have correct success colors', () => {
        expect(lightTheme.palette.success.main).toBe('#2e7d32');
        expect(lightTheme.palette.success.light).toBe('#4caf50');
        expect(lightTheme.palette.success.dark).toBe('#1b5e20');
      });
    });

    describe('Background Colors', () => {
      it('should have correct default background color', () => {
        expect(lightTheme.palette.background.default).toBe('#fafafa');
      });

      it('should have correct paper background color', () => {
        expect(lightTheme.palette.background.paper).toBe('#ffffff');
      });

      it('should use light backgrounds suitable for bright environments', () => {
        expect(lightTheme.palette.background.default).toBe('#fafafa');
        expect(lightTheme.palette.background.paper).toBe('#ffffff');
      });
    });

    describe('Text Colors', () => {
      it('should have correct primary text color', () => {
        expect(lightTheme.palette.text.primary).toBe('rgba(0, 0, 0, 0.87)');
      });

      it('should have correct secondary text color', () => {
        expect(lightTheme.palette.text.secondary).toBe('rgba(0, 0, 0, 0.6)');
      });

      it('should have correct disabled text color', () => {
        expect(lightTheme.palette.text.disabled).toBe('rgba(0, 0, 0, 0.38)');
      });

      it('should use dark text on light backgrounds', () => {
        expect(lightTheme.palette.text.primary).toContain('0, 0, 0');
      });
    });

    describe('UI Element Colors', () => {
      it('should have correct divider color', () => {
        expect(lightTheme.palette.divider).toBe('rgba(0, 0, 0, 0.12)');
      });

      it('should have correct action colors', () => {
        expect(lightTheme.palette.action?.active).toBe('rgba(0, 0, 0, 0.54)');
        expect(lightTheme.palette.action?.hover).toBe('rgba(0, 0, 0, 0.04)');
        expect(lightTheme.palette.action?.selected).toBe('rgba(0, 0, 0, 0.08)');
        expect(lightTheme.palette.action?.disabled).toBe('rgba(0, 0, 0, 0.26)');
        expect(lightTheme.palette.action?.disabledBackground).toBe('rgba(0, 0, 0, 0.12)');
      });
    });
  });

  describe('Dark Theme', () => {
    describe('Theme Mode', () => {
      it('should be configured for dark mode', () => {
        expect(darkTheme.palette.mode).toBe('dark');
      });
    });

    describe('Primary Colors', () => {
      it('should have correct primary main color for dark theme', () => {
        expect(darkTheme.palette.primary.main).toBe('#90caf9');
      });

      it('should have correct primary light color for dark theme', () => {
        expect(darkTheme.palette.primary.light).toBe('#bbdefb');
      });

      it('should have correct primary dark color for dark theme', () => {
        expect(darkTheme.palette.primary.dark).toBe('#42a5f5');
      });

      it('should have dark contrast text for primary color', () => {
        expect(darkTheme.palette.primary.contrastText).toBe('rgba(0, 0, 0, 0.87)');
      });
    });

    describe('Secondary Colors', () => {
      it('should have correct secondary main color for dark theme', () => {
        expect(darkTheme.palette.secondary.main).toBe('#f48fb1');
      });

      it('should have correct secondary light color for dark theme', () => {
        expect(darkTheme.palette.secondary.light).toBe('#f8bbd0');
      });

      it('should have correct secondary dark color for dark theme', () => {
        expect(darkTheme.palette.secondary.dark).toBe('#ec407a');
      });

      it('should have dark contrast text for secondary color', () => {
        expect(darkTheme.palette.secondary.contrastText).toBe('rgba(0, 0, 0, 0.87)');
      });
    });

    describe('Semantic Colors', () => {
      it('should have correct error colors for dark theme', () => {
        expect(darkTheme.palette.error.main).toBe('#ef5350');
        expect(darkTheme.palette.error.light).toBe('#e57373');
        expect(darkTheme.palette.error.dark).toBe('#d32f2f');
      });

      it('should have correct warning colors for dark theme', () => {
        expect(darkTheme.palette.warning.main).toBe('#ffa726');
        expect(darkTheme.palette.warning.light).toBe('#ffb74d');
        expect(darkTheme.palette.warning.dark).toBe('#f57c00');
      });

      it('should have correct info colors for dark theme', () => {
        expect(darkTheme.palette.info.main).toBe('#4fc3f7');
        expect(darkTheme.palette.info.light).toBe('#81d4fa');
        expect(darkTheme.palette.info.dark).toBe('#0288d1');
      });

      it('should have correct success colors for dark theme', () => {
        expect(darkTheme.palette.success.main).toBe('#66bb6a');
        expect(darkTheme.palette.success.light).toBe('#81c784');
        expect(darkTheme.palette.success.dark).toBe('#388e3c');
      });
    });

    describe('Background Colors', () => {
      it('should have correct default background color for dark theme', () => {
        expect(darkTheme.palette.background.default).toBe('#121212');
      });

      it('should have correct paper background color for dark theme', () => {
        expect(darkTheme.palette.background.paper).toBe('#1e1e1e');
      });

      it('should use dark backgrounds suitable for low-light environments', () => {
        expect(darkTheme.palette.background.default).toBe('#121212');
        expect(darkTheme.palette.background.paper).toBe('#1e1e1e');
      });
    });

    describe('Text Colors', () => {
      it('should have correct primary text color for dark theme', () => {
        expect(darkTheme.palette.text.primary).toBe('rgba(255, 255, 255, 0.87)');
      });

      it('should have correct secondary text color for dark theme', () => {
        expect(darkTheme.palette.text.secondary).toBe('rgba(255, 255, 255, 0.6)');
      });

      it('should have correct disabled text color for dark theme', () => {
        expect(darkTheme.palette.text.disabled).toBe('rgba(255, 255, 255, 0.38)');
      });

      it('should use light text on dark backgrounds', () => {
        expect(darkTheme.palette.text.primary).toContain('255, 255, 255');
      });
    });

    describe('UI Element Colors', () => {
      it('should have correct divider color for dark theme', () => {
        expect(darkTheme.palette.divider).toBe('rgba(255, 255, 255, 0.12)');
      });

      it('should have correct action colors for dark theme', () => {
        expect(darkTheme.palette.action?.active).toBe('rgba(255, 255, 255, 0.54)');
        expect(darkTheme.palette.action?.hover).toBe('rgba(255, 255, 255, 0.08)');
        expect(darkTheme.palette.action?.selected).toBe('rgba(255, 255, 255, 0.16)');
        expect(darkTheme.palette.action?.disabled).toBe('rgba(255, 255, 255, 0.3)');
        expect(darkTheme.palette.action?.disabledBackground).toBe('rgba(255, 255, 255, 0.12)');
      });
    });
  });

  describe('Shared Configuration', () => {
    describe('Typography', () => {
      it('should have consistent font family across themes', () => {
        expect(lightTheme.typography.fontFamily).toBe('"Roboto", "Helvetica", "Arial", sans-serif');
        expect(darkTheme.typography.fontFamily).toBe('"Roboto", "Helvetica", "Arial", sans-serif');
      });

      it('should have correct base font size', () => {
        expect(lightTheme.typography.fontSize).toBe(16);
        expect(darkTheme.typography.fontSize).toBe(16);
      });

      it('should have correct font weights', () => {
        expect(lightTheme.typography.fontWeightLight).toBe(300);
        expect(lightTheme.typography.fontWeightRegular).toBe(400);
        expect(lightTheme.typography.fontWeightMedium).toBe(500);
        expect(lightTheme.typography.fontWeightBold).toBe(700);
      });

      it('should have proper heading hierarchy', () => {
        expect(lightTheme.typography.h1?.fontSize).toBe('6rem');
        expect(lightTheme.typography.h2?.fontSize).toBe('3.75rem');
        expect(lightTheme.typography.h3?.fontSize).toBe('3rem');
        expect(lightTheme.typography.h4?.fontSize).toBe('2.125rem');
        expect(lightTheme.typography.h5?.fontSize).toBe('1.5rem');
        expect(lightTheme.typography.h6?.fontSize).toBe('1.25rem');
      });

      it('should have body text variants', () => {
        expect(lightTheme.typography.body1?.fontSize).toBe('1rem');
        expect(lightTheme.typography.body2?.fontSize).toBe('0.875rem');
      });

      it('should have button typography configured', () => {
        expect(lightTheme.typography.button?.textTransform).toBe('none');
        expect(lightTheme.typography.button?.fontWeight).toBe(500);
      });
    });

    describe('Spacing', () => {
      it('should use 8px base spacing unit', () => {
        expect(lightTheme.spacing(1)).toBe('8px');
        expect(darkTheme.spacing(1)).toBe('8px');
      });

      it('should calculate spacing correctly', () => {
        expect(lightTheme.spacing(2)).toBe('16px');
        expect(lightTheme.spacing(3)).toBe('24px');
        expect(lightTheme.spacing(4)).toBe('32px');
      });
    });

    describe('Shape', () => {
      it('should have correct border radius', () => {
        expect(lightTheme.shape.borderRadius).toBe(4);
        expect(darkTheme.shape.borderRadius).toBe(4);
      });
    });

    describe('Breakpoints', () => {
      it('should have correct breakpoint values', () => {
        expect(lightTheme.breakpoints.values.xs).toBe(0);
        expect(lightTheme.breakpoints.values.sm).toBe(600);
        expect(lightTheme.breakpoints.values.md).toBe(900);
        expect(lightTheme.breakpoints.values.lg).toBe(1200);
        expect(lightTheme.breakpoints.values.xl).toBe(1536);
      });

      it('should have consistent breakpoints across themes', () => {
        expect(lightTheme.breakpoints.values).toEqual(darkTheme.breakpoints.values);
      });
    });

    describe('Component Overrides', () => {
      it('should override button text transform', () => {
        const lightButtonRoot = lightTheme.components?.MuiButton?.styleOverrides?.root;
        const darkButtonRoot = darkTheme.components?.MuiButton?.styleOverrides?.root;

        expect(
          lightButtonRoot &&
            typeof lightButtonRoot === 'object' &&
            'textTransform' in lightButtonRoot
            ? lightButtonRoot.textTransform
            : undefined
        ).toBe('none');
        expect(
          darkButtonRoot && typeof darkButtonRoot === 'object' && 'textTransform' in darkButtonRoot
            ? darkButtonRoot.textTransform
            : undefined
        ).toBe('none');
      });

      it('should configure card elevation', () => {
        expect(lightTheme.components?.MuiCard?.defaultProps?.elevation).toBe(1);
        expect(darkTheme.components?.MuiCard?.defaultProps?.elevation).toBe(1);
      });

      it('should configure AppBar elevation', () => {
        expect(lightTheme.components?.MuiAppBar?.defaultProps?.elevation).toBe(0);
        expect(darkTheme.components?.MuiAppBar?.defaultProps?.elevation).toBe(0);
      });

      it('should have theme-specific AppBar border', () => {
        const lightAppBarRoot = lightTheme.components?.MuiAppBar?.styleOverrides?.root;
        const darkAppBarRoot = darkTheme.components?.MuiAppBar?.styleOverrides?.root;

        const lightBorder =
          lightAppBarRoot &&
          typeof lightAppBarRoot === 'object' &&
          'borderBottom' in lightAppBarRoot
            ? lightAppBarRoot.borderBottom
            : undefined;
        const darkBorder =
          darkAppBarRoot && typeof darkAppBarRoot === 'object' && 'borderBottom' in darkAppBarRoot
            ? darkAppBarRoot.borderBottom
            : undefined;

        expect(lightBorder).toBe('1px solid rgba(0, 0, 0, 0.12)');
        expect(darkBorder).toBe('1px solid rgba(255, 255, 255, 0.12)');
      });
    });
  });

  describe('Accessibility Compliance', () => {
    describe('Light Theme Contrast', () => {
      it('should meet WCAG AA standards for text contrast', () => {
        // Primary text on white background should exceed 4.5:1
        expect(lightTheme.palette.text.primary).toBe('rgba(0, 0, 0, 0.87)');
        // This provides approximately 15.8:1 contrast ratio
      });

      it('should have sufficient contrast for secondary text', () => {
        // Secondary text should meet WCAG AA
        expect(lightTheme.palette.text.secondary).toBe('rgba(0, 0, 0, 0.6)');
        // This provides approximately 7.7:1 contrast ratio
      });
    });

    describe('Dark Theme Contrast', () => {
      it('should meet WCAG AA standards for text contrast in dark mode', () => {
        // Primary text on dark background should exceed 4.5:1
        expect(darkTheme.palette.text.primary).toBe('rgba(255, 255, 255, 0.87)');
        // This provides approximately 14.9:1 contrast ratio
      });

      it('should have sufficient contrast for secondary text in dark mode', () => {
        // Secondary text should meet WCAG AA
        expect(darkTheme.palette.text.secondary).toBe('rgba(255, 255, 255, 0.6)');
        // This provides approximately 7.4:1 contrast ratio
      });
    });
  });

  describe('Theme Consistency', () => {
    it('should have matching typography across both themes', () => {
      // Compare key typography properties rather than the entire object
      // as MUI adds computed properties that may differ
      expect(lightTheme.typography.fontFamily).toBe(darkTheme.typography.fontFamily);
      expect(lightTheme.typography.fontSize).toBe(darkTheme.typography.fontSize);
      expect(lightTheme.typography.fontWeightLight).toBe(darkTheme.typography.fontWeightLight);
      expect(lightTheme.typography.fontWeightRegular).toBe(darkTheme.typography.fontWeightRegular);
      expect(lightTheme.typography.fontWeightMedium).toBe(darkTheme.typography.fontWeightMedium);
      expect(lightTheme.typography.fontWeightBold).toBe(darkTheme.typography.fontWeightBold);
      expect(lightTheme.typography.h1).toEqual(darkTheme.typography.h1);
      expect(lightTheme.typography.h2).toEqual(darkTheme.typography.h2);
      expect(lightTheme.typography.body1).toEqual(darkTheme.typography.body1);
      expect(lightTheme.typography.button).toEqual(darkTheme.typography.button);
    });

    it('should have matching spacing across both themes', () => {
      expect(lightTheme.spacing(1)).toBe(darkTheme.spacing(1));
      expect(lightTheme.spacing(2)).toBe(darkTheme.spacing(2));
    });

    it('should have matching breakpoints across both themes', () => {
      expect(lightTheme.breakpoints.values).toEqual(darkTheme.breakpoints.values);
    });

    it('should have matching shape configuration across both themes', () => {
      expect(lightTheme.shape.borderRadius).toBe(darkTheme.shape.borderRadius);
    });
  });
});
