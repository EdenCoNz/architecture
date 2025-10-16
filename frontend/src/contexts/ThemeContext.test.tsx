/**
 * ThemeContext Unit Tests
 *
 * Tests for theme mode state management, localStorage persistence,
 * and system preference detection.
 *
 * Following TDD approach - tests written before implementation.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, renderHook, act } from '@testing-library/react';
import { ThemeProvider, useTheme } from './ThemeContext';

describe('ThemeContext', () => {
  // Clear localStorage and reset mocks before each test
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  // Clean up after each test
  afterEach(() => {
    localStorage.clear();
  });

  describe('ThemeProvider', () => {
    it('should render children without crashing', () => {
      render(
        <ThemeProvider>
          <div>Test Child</div>
        </ThemeProvider>
      );

      expect(screen.getByText('Test Child')).toBeInTheDocument();
    });

    it('should provide theme context to children', () => {
      const TestComponent = () => {
        const { mode } = useTheme();
        return <div>Current mode: {mode}</div>;
      };

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      expect(screen.getByText(/Current mode:/)).toBeInTheDocument();
    });
  });

  describe('Initial theme mode', () => {
    it('should default to light mode when no preference exists', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: ThemeProvider,
      });

      expect(result.current.mode).toBe('light');
    });

    it('should detect system preference for dark mode', () => {
      // Mock matchMedia to return dark mode preference
      window.matchMedia = vi.fn().mockImplementation((query) => ({
        matches: query === '(prefers-color-scheme: dark)',
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      }));

      const { result } = renderHook(() => useTheme(), {
        wrapper: ThemeProvider,
      });

      expect(result.current.mode).toBe('dark');
    });

    it('should detect system preference for light mode', () => {
      // Mock matchMedia to return light mode preference
      window.matchMedia = vi.fn().mockImplementation((query) => ({
        matches: query === '(prefers-color-scheme: light)',
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      }));

      const { result } = renderHook(() => useTheme(), {
        wrapper: ThemeProvider,
      });

      expect(result.current.mode).toBe('light');
    });

    it('should restore theme preference from localStorage', () => {
      // Set dark mode in localStorage
      localStorage.setItem('themeMode', 'dark');

      const { result } = renderHook(() => useTheme(), {
        wrapper: ThemeProvider,
      });

      expect(result.current.mode).toBe('dark');
    });

    it('should prioritize localStorage over system preference', () => {
      // Set dark mode in localStorage
      localStorage.setItem('themeMode', 'dark');

      // Mock matchMedia to return light mode preference
      window.matchMedia = vi.fn().mockImplementation((query) => ({
        matches: query === '(prefers-color-scheme: light)',
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      }));

      const { result } = renderHook(() => useTheme(), {
        wrapper: ThemeProvider,
      });

      // localStorage should take precedence
      expect(result.current.mode).toBe('dark');
    });
  });

  describe('toggleTheme function', () => {
    it('should toggle from light to dark mode', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: ThemeProvider,
      });

      expect(result.current.mode).toBe('light');

      act(() => {
        result.current.toggleTheme();
      });

      expect(result.current.mode).toBe('dark');
    });

    it('should toggle from dark to light mode', () => {
      // Start with dark mode
      localStorage.setItem('themeMode', 'dark');

      const { result } = renderHook(() => useTheme(), {
        wrapper: ThemeProvider,
      });

      expect(result.current.mode).toBe('dark');

      act(() => {
        result.current.toggleTheme();
      });

      expect(result.current.mode).toBe('light');
    });

    it('should toggle multiple times correctly', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: ThemeProvider,
      });

      expect(result.current.mode).toBe('light');

      act(() => {
        result.current.toggleTheme();
      });
      expect(result.current.mode).toBe('dark');

      act(() => {
        result.current.toggleTheme();
      });
      expect(result.current.mode).toBe('light');

      act(() => {
        result.current.toggleTheme();
      });
      expect(result.current.mode).toBe('dark');
    });
  });

  describe('localStorage persistence', () => {
    it('should persist theme mode to localStorage when toggled', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: ThemeProvider,
      });

      act(() => {
        result.current.toggleTheme();
      });

      expect(localStorage.getItem('themeMode')).toBe('dark');
    });

    it('should update localStorage when toggling back', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: ThemeProvider,
      });

      act(() => {
        result.current.toggleTheme(); // light -> dark
      });
      expect(localStorage.getItem('themeMode')).toBe('dark');

      act(() => {
        result.current.toggleTheme(); // dark -> light
      });
      expect(localStorage.getItem('themeMode')).toBe('light');
    });

    it('should persist initial system preference to localStorage after first toggle', () => {
      // Mock dark system preference
      window.matchMedia = vi.fn().mockImplementation((query) => ({
        matches: query === '(prefers-color-scheme: dark)',
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      }));

      const { result } = renderHook(() => useTheme(), {
        wrapper: ThemeProvider,
      });

      // Should start with dark mode from system preference
      expect(result.current.mode).toBe('dark');

      // Toggle to light
      act(() => {
        result.current.toggleTheme();
      });

      // Should persist light mode preference
      expect(localStorage.getItem('themeMode')).toBe('light');
    });
  });

  describe('useTheme hook error handling', () => {
    it('should throw error when used outside ThemeProvider', () => {
      // Suppress console.error for this test
      const originalError = console.error;
      console.error = vi.fn();

      expect(() => {
        renderHook(() => useTheme());
      }).toThrow('useTheme must be used within ThemeProvider');

      // Restore console.error
      console.error = originalError;
    });
  });

  describe('Integration test', () => {
    it('should maintain theme state across component re-renders', () => {
      const TestComponent = () => {
        const { mode, toggleTheme } = useTheme();
        return (
          <div>
            <div>Mode: {mode}</div>
            <button onClick={toggleTheme}>Toggle Theme</button>
          </div>
        );
      };

      const { rerender, unmount } = render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Get initial mode (could be light or dark depending on previous tests/localStorage)
      const initialModeText = screen.getByText(/Mode:/);
      const initialMode = initialModeText.textContent?.includes('dark') ? 'dark' : 'light';
      const expectedMode = initialMode === 'light' ? 'dark' : 'light';

      const button = screen.getByRole('button', { name: /toggle theme/i });

      act(() => {
        button.click();
      });

      expect(screen.getByText(`Mode: ${expectedMode}`)).toBeInTheDocument();

      // Re-render component
      rerender(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      );

      // Theme state should persist across re-renders
      expect(screen.getByText(`Mode: ${expectedMode}`)).toBeInTheDocument();

      // Cleanup
      unmount();
    });
  });

  describe('Page reload persistence', () => {
    it('should restore theme state after simulated page reload', () => {
      // First render - toggle to a known state
      const { result: firstResult, unmount: unmountFirst } = renderHook(() => useTheme(), {
        wrapper: ThemeProvider,
      });

      // Get the initial mode
      const initialMode = firstResult.current.mode;
      const targetMode = initialMode === 'light' ? 'dark' : 'light';

      // Toggle to target mode
      act(() => {
        firstResult.current.toggleTheme();
      });

      expect(firstResult.current.mode).toBe(targetMode);
      expect(localStorage.getItem('themeMode')).toBe(targetMode);

      // Unmount the first hook to simulate page unload
      unmountFirst();

      // Simulate page reload by creating new hook instance
      const { result: secondResult } = renderHook(() => useTheme(), {
        wrapper: ThemeProvider,
      });

      // Should restore the target mode from localStorage
      expect(secondResult.current.mode).toBe(targetMode);
    });
  });

  describe('Type safety', () => {
    it('should expose correct types for mode', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: ThemeProvider,
      });

      // TypeScript should enforce that mode is 'light' | 'dark'
      const mode: 'light' | 'dark' = result.current.mode;
      expect(['light', 'dark']).toContain(mode);
    });

    it('should expose toggleTheme as a function', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: ThemeProvider,
      });

      expect(typeof result.current.toggleTheme).toBe('function');
    });
  });
});
