/**
 * Vitest Test Setup
 *
 * Global test configuration and setup for all test files.
 * Configures jsdom, testing library, and any global test utilities.
 */

import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// Cleanup after each test to prevent test pollution
afterEach(() => {
  cleanup();
});

// Mock window.matchMedia for theme detection tests
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {}, // deprecated
    removeListener: () => {}, // deprecated
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => true,
  }),
});

// Mock API service to prevent actual API calls during tests
vi.mock('@/services/api', () => {
  class MockApiError extends Error {
    status: number;
    details?: Record<string, unknown>;

    constructor(message: string, status: number, details?: Record<string, unknown>) {
      super(message);
      this.name = 'ApiError';
      this.status = status;
      this.details = details;
    }
  }

  return {
    apiService: {
      getThemePreference: vi.fn().mockResolvedValue({
        success: true,
        data: { theme: 'auto' },
      }),
      updateThemePreference: vi.fn().mockResolvedValue({
        success: true,
        data: { theme: 'auto' },
      }),
      healthCheck: vi.fn().mockResolvedValue({
        success: true,
        data: { status: 'healthy', timestamp: new Date().toISOString() },
      }),
    },
    ApiError: MockApiError,
  };
});
