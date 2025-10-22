/**
 * Static Analysis Tests for ThemeContext
 *
 * These tests verify code quality standards are met including
 * no duplicate imports and proper code organization.
 */

import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';

describe('ThemeContext Code Quality', () => {
  const themeContextPath = resolve(__dirname, 'ThemeContext.tsx');
  const useThemePath = resolve(__dirname, 'useTheme.ts');
  const themeContextContent = readFileSync(themeContextPath, 'utf-8');
  const useThemeContent = readFileSync(useThemePath, 'utf-8');

  describe('Import Organization', () => {
    it('should not have duplicate imports from the same module', () => {
      // Parse imports from the file
      const importLines = themeContextContent
        .split('\n')
        .filter((line) => line.trim().startsWith('import '));

      // Extract module names from imports
      const importSources = importLines
        .map((line) => {
          const match = line.match(/from ['"](.+)['"]/);
          return match ? match[1] : null;
        })
        .filter((source): source is string => source !== null);

      // Check for duplicates
      const uniqueSources = new Set(importSources);
      const hasDuplicates = uniqueSources.size !== importSources.length;

      if (hasDuplicates) {
        // Find which modules are duplicated
        const sourceCount = importSources.reduce(
          (acc, source) => {
            acc[source] = (acc[source] || 0) + 1;
            return acc;
          },
          {} as Record<string, number>
        );

        const duplicates = Object.entries(sourceCount)
          .filter(([_, count]) => count > 1)
          .map(([source]) => source);

        expect.fail(
          `Found duplicate imports from: ${duplicates.join(', ')}\n` +
            `Each module should be imported only once.`
        );
      }

      expect(hasDuplicates).toBe(false);
    });

    it('should consolidate all imports from react into single import statement', () => {
      const reactImportLines = themeContextContent
        .split('\n')
        .filter((line) => line.trim().startsWith('import ') && line.includes("from 'react'"));

      expect(reactImportLines.length).toBeLessThanOrEqual(1);
    });

    it('should have well-organized imports section', () => {
      const lines = themeContextContent.split('\n');
      const importEndIndex = lines.findIndex(
        (line, idx) =>
          idx > 0 &&
          !line.trim().startsWith('import ') &&
          !line.trim().startsWith('*') &&
          line.trim() !== '' &&
          !line.trim().startsWith('//')
      );

      expect(importEndIndex).toBeGreaterThan(0);
    });
  });

  describe('Code Structure', () => {
    it('should export ThemeProvider component from ThemeContext', () => {
      expect(themeContextContent).toContain('export function ThemeProvider');
    });

    it('should export useTheme hook from useTheme module', () => {
      expect(useThemeContent).toContain('export function useTheme');
    });

    it('should export ThemeMode type from useTheme module', () => {
      expect(useThemeContent).toContain('export type ThemeMode');
    });
  });
});
