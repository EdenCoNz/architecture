/**
 * Export Separation Tests for ThemeContext
 *
 * These tests verify that component exports and utility exports are properly
 * separated to support hot module replacement (HMR) and react-refresh.
 */

import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';

describe('ThemeContext Export Separation', () => {
  const themeContextPath = resolve(__dirname, 'ThemeContext.tsx');
  const themeHooksPath = resolve(__dirname, 'useTheme.ts');

  describe('Component File (ThemeContext.tsx)', () => {
    it('should exist and be readable', () => {
      const fileContent = readFileSync(themeContextPath, 'utf-8');
      expect(fileContent).toBeDefined();
      expect(fileContent.length).toBeGreaterThan(0);
    });

    it('should only export the ThemeProvider component', () => {
      const fileContent = readFileSync(themeContextPath, 'utf-8');

      // Should export ThemeProvider
      expect(fileContent).toContain('export function ThemeProvider');

      // Should NOT export useTheme hook (moved to separate file)
      const useThemeExportPattern = /export\s+function\s+useTheme/;
      expect(useThemeExportPattern.test(fileContent)).toBe(false);
    });

    it('should not export utility functions directly', () => {
      const fileContent = readFileSync(themeContextPath, 'utf-8');

      // Check that utility functions are not exported
      const exportedUtilityPattern =
        /export\s+(function|const)\s+(loadThemeFromStorage|saveThemeToStorage)/;
      expect(exportedUtilityPattern.test(fileContent)).toBe(false);
    });

    it('should not export types other than props types needed by the component', () => {
      const fileContent = readFileSync(themeContextPath, 'utf-8');

      // ThemeProvider props interface can be exported or not (implementation detail)
      // But ThemeMode and ThemeContextValue should be in the hooks file
      const themeModeExportPattern = /export\s+type\s+ThemeMode/;
      expect(themeModeExportPattern.test(fileContent)).toBe(false);
    });
  });

  describe('Utility File (useTheme.ts)', () => {
    it('should exist and be readable', () => {
      const fileContent = readFileSync(themeHooksPath, 'utf-8');
      expect(fileContent).toBeDefined();
      expect(fileContent.length).toBeGreaterThan(0);
    });

    it('should export the useTheme hook', () => {
      const fileContent = readFileSync(themeHooksPath, 'utf-8');
      expect(fileContent).toContain('export function useTheme');
    });

    it('should export ThemeMode type', () => {
      const fileContent = readFileSync(themeHooksPath, 'utf-8');
      expect(fileContent).toContain('export type ThemeMode');
    });

    it('should not export any React components', () => {
      const fileContent = readFileSync(themeHooksPath, 'utf-8');

      // Should not have component exports
      const componentExportPattern = /export\s+function\s+\w+Provider/;
      expect(componentExportPattern.test(fileContent)).toBe(false);
    });
  });

  describe('React Refresh Compatibility', () => {
    it('ThemeContext.tsx should be compatible with react-refresh', () => {
      const fileContent = readFileSync(themeContextPath, 'utf-8');

      // File should only export components (ThemeProvider)
      // No utility function exports should be present
      const exportStatements = fileContent
        .split('\n')
        .filter((line) => line.trim().startsWith('export '));

      // Check that all exports are either:
      // 1. Component functions (ThemeProvider)
      // 2. Type exports (which don't affect react-refresh)
      const nonComponentExports = exportStatements.filter((line) => {
        // Allow type exports
        if (line.includes('export type') || line.includes('export interface')) {
          return false;
        }
        // Allow ThemeProvider export
        if (line.includes('ThemeProvider')) {
          return false;
        }
        // Any other export is a violation
        return true;
      });

      expect(nonComponentExports).toHaveLength(0);
    });
  });
});
