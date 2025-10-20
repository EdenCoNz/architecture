/**
 * Temporary test to trigger workflow failure for testing
 * This test is intentionally designed to fail to test the workflow failure detection system
 */
import { describe, it, expect } from 'vitest';

describe('Workflow Test', () => {
  it('should fail to trigger workflow failure detection', () => {
    // This test will fail to trigger the workflow chain
    expect(true).toBe(false);
  });
});
