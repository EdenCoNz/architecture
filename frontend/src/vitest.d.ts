/**
 * Type definitions for Vitest and Testing Library matchers
 *
 * Provides TypeScript support for jest-dom matchers in Vitest tests
 */

import '@testing-library/jest-dom';
import { TestingLibraryMatchers } from '@testing-library/jest-dom/matchers';
import { Assertion, AsymmetricMatchersContaining } from 'vitest';

type CustomMatchers<R = unknown> = TestingLibraryMatchers<typeof expect.stringContaining, R>;

declare module 'vitest' {
  interface Assertion<T = any> extends CustomMatchers<T> {}
  interface AsymmetricMatchersContaining extends CustomMatchers {}
}
