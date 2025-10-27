/**
 * Tests for Version Information Utility
 *
 * These tests verify that version information is properly exposed at runtime
 * for support engineers, administrators, and monitoring tools.
 *
 * Feature #16 Story 16.6: Expose Frontend Version at Runtime
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { getVersion, logVersionInfo, exposeVersionToWindow } from './version';

describe('Version Utility', () => {
  describe('getVersion', () => {
    it('should return version from package.json', () => {
      const version = getVersion();

      // Version should be a non-empty string
      expect(version).toBeTruthy();
      expect(typeof version).toBe('string');
      expect(version.length).toBeGreaterThan(0);
    });

    it('should follow semantic versioning format (MAJOR.MINOR.PATCH)', () => {
      const version = getVersion();

      // Semantic versioning regex: X.Y.Z where X, Y, Z are numbers
      // Also supports prerelease and build metadata: X.Y.Z-prerelease+build
      const semverRegex = /^\d+\.\d+\.\d+(-[\w.]+)?(\+[\w.]+)?$/;

      expect(version).toMatch(semverRegex);
    });

    it('should return version "1.0.0" as initially configured in Story 16.1', () => {
      const version = getVersion();

      // This verifies Story 16.1 implementation is working
      // In test environment, version might have -test suffix
      expect(version).toMatch(/^1\.0\.0/);
      expect(version.startsWith('1.0.0')).toBe(true);
    });
  });

  describe('logVersionInfo', () => {
    beforeEach(() => {
      // Mock console methods
      vi.spyOn(console, 'log').mockImplementation(() => {});
      vi.spyOn(console, 'info').mockImplementation(() => {});
    });

    it('should log version information to console', () => {
      logVersionInfo();

      // Should log at least once
      expect(console.log).toHaveBeenCalled();
    });

    it('should include version number in log output', () => {
      logVersionInfo();

      const version = getVersion();

      // Check that version appears in one of the console.log calls
      const logCalls = (console.log as unknown as ReturnType<typeof vi.spyOn>).mock.calls;
      const allLogOutputs = logCalls.map((call) => call.join(' ')).join(' ');

      expect(allLogOutputs).toContain(version);
    });

    it('should include "Frontend" or "version" keyword in log output', () => {
      logVersionInfo();

      const logCalls = (console.log as unknown as ReturnType<typeof vi.spyOn>).mock.calls;
      const allLogOutputs = logCalls.map((call) => call.join(' ')).join(' ');

      // Should mention either "Frontend" or "version" to make it clear what's being logged
      const hasRelevantKeyword =
        allLogOutputs.toLowerCase().includes('frontend') ||
        allLogOutputs.toLowerCase().includes('version');

      expect(hasRelevantKeyword).toBe(true);
    });

    it('should support optional environment parameter', () => {
      // Should not throw when called with environment
      expect(() => logVersionInfo('production')).not.toThrow();
      expect(() => logVersionInfo('development')).not.toThrow();
      expect(() => logVersionInfo('staging')).not.toThrow();
    });
  });

  describe('exposeVersionToWindow', () => {
    beforeEach(() => {
      // Clean up window object before each test
      if ('APP_VERSION' in window) {
        delete (window as { APP_VERSION?: unknown }).APP_VERSION;
      }
      if ('__APP_INFO__' in window) {
        delete (window as { __APP_INFO__?: unknown }).__APP_INFO__;
      }
    });

    it('should expose version information to window object', () => {
      exposeVersionToWindow();

      // Check for version info on window object
      // Could be at window.APP_VERSION or window.__APP_INFO__.version
      const hasVersionOnWindow =
        'APP_VERSION' in window ||
        ('__APP_INFO__' in window &&
          typeof (window as { __APP_INFO__?: { version?: string } }).__APP_INFO__ === 'object' &&
          'version' in ((window as { __APP_INFO__?: { version?: string } }).__APP_INFO__ || {}));

      expect(hasVersionOnWindow).toBe(true);
    });

    it('should expose version that matches getVersion()', () => {
      exposeVersionToWindow();

      const expectedVersion = getVersion();

      // Get version from window object
      let windowVersion: string | undefined;

      if ('APP_VERSION' in window) {
        windowVersion = (window as { APP_VERSION?: string }).APP_VERSION;
      } else if ('__APP_INFO__' in window) {
        const appInfo = (window as { __APP_INFO__?: { version?: string } }).__APP_INFO__;
        windowVersion = appInfo?.version;
      }

      expect(windowVersion).toBe(expectedVersion);
    });

    it('should expose version information that is accessible in browser dev tools', () => {
      exposeVersionToWindow();

      // Verify we can access the version through window object
      // This is what support engineers would use in dev tools
      const version = getVersion();

      // Try common patterns for accessing version info
      const patterns = [
        (window as { APP_VERSION?: string }).APP_VERSION,
        (window as { __APP_INFO__?: { version?: string } }).__APP_INFO__?.version,
      ];

      const foundVersion = patterns.find((v) => v === version);
      expect(foundVersion).toBe(version);
    });

    it('should handle multiple calls without error', () => {
      // Should be idempotent
      expect(() => {
        exposeVersionToWindow();
        exposeVersionToWindow();
        exposeVersionToWindow();
      }).not.toThrow();
    });
  });

  describe('Integration - Version exposure at runtime', () => {
    beforeEach(() => {
      vi.spyOn(console, 'log').mockImplementation(() => {});

      if ('APP_VERSION' in window) {
        delete (window as { APP_VERSION?: unknown }).APP_VERSION;
      }
      if ('__APP_INFO__' in window) {
        delete (window as { __APP_INFO__?: unknown }).__APP_INFO__;
      }
    });

    it('should make version accessible through multiple channels', () => {
      // This tests the acceptance criteria:
      // - Version visible in console
      // - Version accessible in browser dev tools
      // - Version automatically sourced from package.json

      const version = getVersion();

      // Log version info
      logVersionInfo();

      // Expose to window
      exposeVersionToWindow();

      // Verify console logging happened
      expect(console.log).toHaveBeenCalled();
      const logCalls = (console.log as unknown as ReturnType<typeof vi.spyOn>).mock.calls;
      const allLogOutputs = logCalls.map((call) => call.join(' ')).join(' ');
      expect(allLogOutputs).toContain(version);

      // Verify window exposure
      const patterns = [
        (window as { APP_VERSION?: string }).APP_VERSION,
        (window as { __APP_INFO__?: { version?: string } }).__APP_INFO__?.version,
      ];

      const foundVersion = patterns.find((v) => v === version);
      expect(foundVersion).toBe(version);
    });

    it('should reflect package.json version automatically', () => {
      // This verifies that version comes from package.json (Story 16.1)
      // and updates automatically when package.json changes

      const version = getVersion();

      // Version should be sourced from Vite's build process which reads package.json
      // Vite automatically exposes package.json version at build time
      // In test environment, version might have -test suffix
      expect(version).toMatch(/^1\.0\.0/);
      expect(version.startsWith('1.0.0')).toBe(true);
    });
  });

  describe('Cross-environment consistency', () => {
    it('should return same version regardless of how it is accessed', () => {
      const directVersion = getVersion();

      logVersionInfo();
      exposeVersionToWindow();

      const patterns = [
        (window as { APP_VERSION?: string }).APP_VERSION,
        (window as { __APP_INFO__?: { version?: string } }).__APP_INFO__?.version,
      ];

      const windowVersion = patterns.find((v) => v === directVersion);

      // All methods should return the same version
      expect(windowVersion).toBe(directVersion);
    });

    it('should work consistently across development, staging, and production', () => {
      // Version should be available regardless of environment
      const version = getVersion();

      expect(version).toBeTruthy();
      expect(typeof version).toBe('string');

      // Test with different environment parameters
      expect(() => logVersionInfo('development')).not.toThrow();
      expect(() => logVersionInfo('staging')).not.toThrow();
      expect(() => logVersionInfo('production')).not.toThrow();
    });
  });
});
