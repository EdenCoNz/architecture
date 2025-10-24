/**
 * Configuration Module Tests
 *
 * Tests for environment configuration loading, validation, and error handling
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  getEnv,
  getBooleanEnv,
  getNumberEnv,
  getEnvironment,
  validateApiUrl,
  ConfigValidationError,
} from './index';

// Mock import.meta.env
const mockEnv: Record<string, string | boolean | undefined> = {};
const deletedKeys = new Set<string>();

// Store the original import.meta.env
const originalEnv = { ...import.meta.env };

// Helper to update import.meta.env with mock values
function updateImportMetaEnv() {
  // Clear all current values
  Object.keys(import.meta.env).forEach((key) => {
    delete (import.meta.env as Record<string, unknown>)[key];
  });

  // Start with original env
  const mergedEnv = { ...originalEnv };

  // Remove explicitly deleted keys
  deletedKeys.forEach((key) => {
    delete mergedEnv[key];
  });

  // Apply mock values
  Object.assign(mergedEnv, mockEnv);

  // Apply to import.meta.env
  Object.assign(import.meta.env, mergedEnv);
}

describe('Configuration Module', () => {
  beforeEach(() => {
    // Clear mock environment before each test
    Object.keys(mockEnv).forEach((key) => delete mockEnv[key]);
    deletedKeys.clear();
    // Reset import.meta.env to original state
    Object.keys(import.meta.env).forEach((key) => {
      delete (import.meta.env as Record<string, unknown>)[key];
    });
    Object.assign(import.meta.env, originalEnv);
  });

  describe('getEnv', () => {
    it('should return environment variable value', () => {
      mockEnv.VITE_TEST_VAR = 'test-value';
      updateImportMetaEnv();
      expect(getEnv('TEST_VAR')).toBe('test-value');
    });

    it('should return default value when variable not set', () => {
      updateImportMetaEnv();
      expect(getEnv('MISSING_VAR', 'default')).toBe('default');
    });

    it('should throw error for required missing variable', () => {
      updateImportMetaEnv();
      expect(() => getEnv('REQUIRED_VAR', undefined, true)).toThrow(ConfigValidationError);
      expect(() => getEnv('REQUIRED_VAR', undefined, true)).toThrow(
        'Missing required environment variable: VITE_REQUIRED_VAR'
      );
    });

    it('should not throw for required variable that exists', () => {
      mockEnv.VITE_REQUIRED_VAR = 'exists';
      updateImportMetaEnv();
      expect(() => getEnv('REQUIRED_VAR', undefined, true)).not.toThrow();
      expect(getEnv('REQUIRED_VAR', undefined, true)).toBe('exists');
    });
  });

  describe('getBooleanEnv', () => {
    it('should return true for "true" string', () => {
      mockEnv.VITE_BOOL_VAR = 'true';
      updateImportMetaEnv();
      expect(getBooleanEnv('BOOL_VAR')).toBe(true);
    });

    it('should return true for "1" string', () => {
      mockEnv.VITE_BOOL_VAR = '1';
      updateImportMetaEnv();
      expect(getBooleanEnv('BOOL_VAR')).toBe(true);
    });

    it('should return false for "false" string', () => {
      mockEnv.VITE_BOOL_VAR = 'false';
      updateImportMetaEnv();
      expect(getBooleanEnv('BOOL_VAR')).toBe(false);
    });

    it('should return false for "0" string', () => {
      mockEnv.VITE_BOOL_VAR = '0';
      updateImportMetaEnv();
      expect(getBooleanEnv('BOOL_VAR')).toBe(false);
    });

    it('should return default value when not set', () => {
      updateImportMetaEnv();
      expect(getBooleanEnv('MISSING_BOOL')).toBe(false);
      expect(getBooleanEnv('MISSING_BOOL', true)).toBe(true);
    });
  });

  describe('getNumberEnv', () => {
    it('should return numeric value', () => {
      mockEnv.VITE_NUM_VAR = '42';
      updateImportMetaEnv();
      expect(getNumberEnv('NUM_VAR', 0)).toBe(42);
    });

    it('should return default value when not set', () => {
      updateImportMetaEnv();
      expect(getNumberEnv('MISSING_NUM', 100)).toBe(100);
    });

    it('should throw for non-numeric value', () => {
      mockEnv.VITE_NUM_VAR = 'not-a-number';
      updateImportMetaEnv();
      expect(() => getNumberEnv('NUM_VAR', 0)).toThrow(ConfigValidationError);
      expect(() => getNumberEnv('NUM_VAR', 0)).toThrow('must be a valid number');
    });

    it('should enforce minimum value', () => {
      mockEnv.VITE_NUM_VAR = '5';
      updateImportMetaEnv();
      expect(() => getNumberEnv('NUM_VAR', 0, 10)).toThrow(ConfigValidationError);
      expect(() => getNumberEnv('NUM_VAR', 0, 10)).toThrow('must be >= 10');
    });

    it('should enforce maximum value', () => {
      mockEnv.VITE_NUM_VAR = '150';
      updateImportMetaEnv();
      expect(() => getNumberEnv('NUM_VAR', 0, undefined, 100)).toThrow(ConfigValidationError);
      expect(() => getNumberEnv('NUM_VAR', 0, undefined, 100)).toThrow('must be <= 100');
    });

    it('should accept value within range', () => {
      mockEnv.VITE_NUM_VAR = '50';
      updateImportMetaEnv();
      expect(() => getNumberEnv('NUM_VAR', 0, 1, 100)).not.toThrow();
      expect(getNumberEnv('NUM_VAR', 0, 1, 100)).toBe(50);
    });
  });

  describe('getEnvironment', () => {
    it('should return test environment when MODE is test', () => {
      mockEnv.MODE = 'test';
      updateImportMetaEnv();
      expect(getEnvironment()).toBe('test');
    });

    it('should return test environment when VITE_NODE_ENV is test', () => {
      mockEnv.MODE = 'development';
      mockEnv.VITE_NODE_ENV = 'test';
      updateImportMetaEnv();
      expect(getEnvironment()).toBe('test');
    });

    it('should return production environment when MODE is production', () => {
      mockEnv.MODE = 'production';
      deletedKeys.add('VITE_NODE_ENV');
      updateImportMetaEnv();
      expect(getEnvironment()).toBe('production');
    });

    it('should allow staging override in production mode', () => {
      mockEnv.MODE = 'production';
      mockEnv.VITE_NODE_ENV = 'staging';
      updateImportMetaEnv();
      expect(getEnvironment()).toBe('staging');
    });

    it('should default to development for other modes', () => {
      mockEnv.MODE = 'development';
      deletedKeys.add('VITE_NODE_ENV');
      updateImportMetaEnv();
      expect(getEnvironment()).toBe('development');
    });
  });

  describe('validateApiUrl', () => {
    it('should accept valid HTTP URL', () => {
      expect(() => validateApiUrl('http://localhost:8000')).not.toThrow();
    });

    it('should accept valid HTTPS URL', () => {
      expect(() => validateApiUrl('https://api.example.com')).not.toThrow();
    });

    it('should throw for empty URL', () => {
      expect(() => validateApiUrl('')).toThrow(ConfigValidationError);
      expect(() => validateApiUrl('')).toThrow('API URL cannot be empty');
    });

    it('should throw for invalid URL format', () => {
      expect(() => validateApiUrl('not-a-url')).toThrow(ConfigValidationError);
      expect(() => validateApiUrl('not-a-url')).toThrow('Invalid API URL format');
    });

    it('should throw for non-HTTP protocol', () => {
      expect(() => validateApiUrl('ftp://example.com')).toThrow(ConfigValidationError);
      expect(() => validateApiUrl('ftp://example.com')).toThrow(
        'must use http:// or https:// protocol'
      );
    });

    it('should warn for HTTP in production', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      mockEnv.PROD = true;
      updateImportMetaEnv();

      validateApiUrl('http://api.example.com');

      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('non-HTTPS API URL in production')
      );

      consoleSpy.mockRestore();
    });
  });

  describe('ConfigValidationError', () => {
    it('should create error with correct message', () => {
      const error = new ConfigValidationError('Test error message');
      expect(error.message).toBe('Test error message');
      expect(error.name).toBe('ConfigValidationError');
      expect(error).toBeInstanceOf(Error);
    });
  });

  describe('Configuration Integration', () => {
    it('should load configuration with all required values', () => {
      // Set up minimal required environment
      mockEnv.MODE = 'development';
      mockEnv.VITE_API_URL = 'http://localhost:8000';
      updateImportMetaEnv();

      // Import config module (this will call loadConfig)
      // Note: In a real test, you'd need to mock the module or reload it
      expect(() => {
        validateApiUrl(mockEnv.VITE_API_URL as string);
        getEnv('API_URL', undefined, true);
      }).not.toThrow();
    });

    it('should fail when required configuration is missing', () => {
      mockEnv.MODE = 'production';
      deletedKeys.add('VITE_API_URL');
      updateImportMetaEnv();

      expect(() => getEnv('API_URL', undefined, true)).toThrow(ConfigValidationError);
    });
  });
});
