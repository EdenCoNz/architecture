/**
 * Vitest Test Setup File
 *
 * Global configuration and setup for all test files.
 * This file is loaded before each test file runs.
 */

import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

/**
 * Cleanup after each test to prevent memory leaks and test interference
 * Automatically unmounts React components and clears the DOM
 */
afterEach(() => {
  cleanup();
});

/**
 * Mock window.matchMedia for responsive design testing
 * Material UI and responsive components require this for breakpoint testing
 */
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {}, // Deprecated but required for some libraries
    removeListener: () => {}, // Deprecated but required for some libraries
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

/**
 * Mock IntersectionObserver for components that use it
 * Useful for lazy loading and visibility detection components
 */
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
} as any;

/**
 * Suppress console errors in tests (optional - remove if you want to see all errors)
 * Uncomment the lines below to suppress expected console errors during testing
 */
// const originalError = console.error;
// beforeAll(() => {
//   console.error = (...args: any[]) => {
//     if (
//       typeof args[0] === 'string' &&
//       args[0].includes('Warning: ReactDOM.render')
//     ) {
//       return;
//     }
//     originalError.call(console, ...args);
//   };
// });
//
// afterAll(() => {
//   console.error = originalError;
// });
