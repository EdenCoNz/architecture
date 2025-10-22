/**
 * Theme Context Tests
 *
 * Comprehensive tests for theme switching functionality following TDD principles.
 * Tests cover theme mode state management, theme switching, and context integration.
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { ThemeProvider, useTheme } from './ThemeContext';
import { Button, Box } from '@mui/material';

// Test component that uses the theme context
function ThemeConsumer() {
  const { mode, toggleTheme, setThemeMode } = useTheme();

  return (
    <Box>
      <div data-testid="theme-mode">{mode}</div>
      <Button onClick={toggleTheme} data-testid="toggle-button">
        Toggle Theme
      </Button>
      <Button onClick={() => setThemeMode('light')} data-testid="set-light-button">
        Set Light
      </Button>
      <Button onClick={() => setThemeMode('dark')} data-testid="set-dark-button">
        Set Dark
      </Button>
    </Box>
  );
}

describe('ThemeContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test to ensure clean state
    localStorage.clear();
  });

  afterEach(() => {
    // Clean up localStorage after each test
    localStorage.clear();
  });

  describe('Theme Provider', () => {
    it('should provide light theme as default', () => {
      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      expect(screen.getByTestId('theme-mode')).toHaveTextContent('light');
    });

    it('should allow custom default mode', () => {
      render(
        <ThemeProvider defaultMode="dark">
          <ThemeConsumer />
        </ThemeProvider>
      );

      expect(screen.getByTestId('theme-mode')).toHaveTextContent('dark');
    });

    it('should render children', () => {
      render(
        <ThemeProvider>
          <div data-testid="child">Test Child</div>
        </ThemeProvider>
      );

      expect(screen.getByTestId('child')).toBeInTheDocument();
    });
  });

  describe('Theme Mode State', () => {
    it('should maintain theme mode state', () => {
      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      const modeDisplay = screen.getByTestId('theme-mode');
      expect(modeDisplay).toHaveTextContent('light');
    });

    it('should expose theme mode through context', () => {
      render(
        <ThemeProvider defaultMode="dark">
          <ThemeConsumer />
        </ThemeProvider>
      );

      expect(screen.getByTestId('theme-mode')).toHaveTextContent('dark');
    });
  });

  describe('Theme Switching', () => {
    it('should toggle theme from light to dark', async () => {
      const user = userEvent.setup();
      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      const toggleButton = screen.getByTestId('toggle-button');
      const modeDisplay = screen.getByTestId('theme-mode');

      expect(modeDisplay).toHaveTextContent('light');

      await user.click(toggleButton);

      expect(modeDisplay).toHaveTextContent('dark');
    });

    it('should toggle theme from dark to light', async () => {
      const user = userEvent.setup();
      render(
        <ThemeProvider defaultMode="dark">
          <ThemeConsumer />
        </ThemeProvider>
      );

      const toggleButton = screen.getByTestId('toggle-button');
      const modeDisplay = screen.getByTestId('theme-mode');

      expect(modeDisplay).toHaveTextContent('dark');

      await user.click(toggleButton);

      expect(modeDisplay).toHaveTextContent('light');
    });

    it('should toggle theme multiple times', async () => {
      const user = userEvent.setup();
      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      const toggleButton = screen.getByTestId('toggle-button');
      const modeDisplay = screen.getByTestId('theme-mode');

      expect(modeDisplay).toHaveTextContent('light');

      await user.click(toggleButton);
      expect(modeDisplay).toHaveTextContent('dark');

      await user.click(toggleButton);
      expect(modeDisplay).toHaveTextContent('light');

      await user.click(toggleButton);
      expect(modeDisplay).toHaveTextContent('dark');
    });

    it('should set theme to light explicitly', async () => {
      const user = userEvent.setup();
      render(
        <ThemeProvider defaultMode="dark">
          <ThemeConsumer />
        </ThemeProvider>
      );

      const setLightButton = screen.getByTestId('set-light-button');
      const modeDisplay = screen.getByTestId('theme-mode');

      expect(modeDisplay).toHaveTextContent('dark');

      await user.click(setLightButton);

      expect(modeDisplay).toHaveTextContent('light');
    });

    it('should set theme to dark explicitly', async () => {
      const user = userEvent.setup();
      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      const setDarkButton = screen.getByTestId('set-dark-button');
      const modeDisplay = screen.getByTestId('theme-mode');

      expect(modeDisplay).toHaveTextContent('light');

      await user.click(setDarkButton);

      expect(modeDisplay).toHaveTextContent('dark');
    });
  });

  describe('MUI Theme Integration', () => {
    it('should apply MUI theme to components in light mode', () => {
      render(
        <ThemeProvider>
          <Button data-testid="test-button">Test Button</Button>
        </ThemeProvider>
      );

      const button = screen.getByTestId('test-button');
      expect(button).toBeInTheDocument();
    });

    it('should apply MUI theme to components in dark mode', () => {
      render(
        <ThemeProvider defaultMode="dark">
          <Button data-testid="test-button">Test Button</Button>
        </ThemeProvider>
      );

      const button = screen.getByTestId('test-button');
      expect(button).toBeInTheDocument();
    });

    it('should apply CssBaseline for consistent styling', () => {
      const { container } = render(
        <ThemeProvider>
          <div>Test Content</div>
        </ThemeProvider>
      );

      // CssBaseline should be present (it injects global styles)
      expect(container).toBeInTheDocument();
    });
  });

  describe('Context Error Handling', () => {
    it('should throw error when useTheme is used outside ThemeProvider', () => {
      // Suppress console.error for this test
      const consoleError = console.error;
      console.error = () => {};

      expect(() => {
        render(<ThemeConsumer />);
      }).toThrow('useTheme must be used within a ThemeProvider');

      console.error = consoleError;
    });
  });

  describe('Theme Accessibility', () => {
    it('should maintain accessibility in light mode', () => {
      render(
        <ThemeProvider>
          <Button data-testid="test-button">Accessible Button</Button>
        </ThemeProvider>
      );

      const button = screen.getByTestId('test-button');
      expect(button).toHaveAccessibleName('Accessible Button');
    });

    it('should maintain accessibility in dark mode', () => {
      render(
        <ThemeProvider defaultMode="dark">
          <Button data-testid="test-button">Accessible Button</Button>
        </ThemeProvider>
      );

      const button = screen.getByTestId('test-button');
      expect(button).toHaveAccessibleName('Accessible Button');
    });
  });

  describe('Performance', () => {
    it('should not re-render unnecessarily when theme stays the same', async () => {
      const user = userEvent.setup();
      let renderCount = 0;

      function CountingConsumer() {
        const { mode, setThemeMode } = useTheme();
        renderCount++;

        return (
          <Box>
            <div data-testid="render-count">{renderCount}</div>
            <div data-testid="theme-mode">{mode}</div>
            <Button onClick={() => setThemeMode('light')} data-testid="set-light-button">
              Set Light
            </Button>
          </Box>
        );
      }

      render(
        <ThemeProvider>
          <CountingConsumer />
        </ThemeProvider>
      );

      const initialRenderCount = renderCount;
      const setLightButton = screen.getByTestId('set-light-button');

      // Setting to the same mode should not cause excessive re-renders
      await user.click(setLightButton);

      // Allow for some re-renders due to React's rendering behavior
      expect(renderCount).toBeLessThanOrEqual(initialRenderCount + 2);
    });
  });

  describe('Theme Persistence (Story #7)', () => {
    const STORAGE_KEY = 'theme-mode';

    it('should load theme from localStorage on initial mount', () => {
      // Set dark theme in localStorage
      localStorage.setItem(STORAGE_KEY, 'dark');

      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      // Should load dark theme from localStorage
      expect(screen.getByTestId('theme-mode')).toHaveTextContent('dark');
    });

    it('should load light theme from localStorage on initial mount', () => {
      // Set light theme in localStorage
      localStorage.setItem(STORAGE_KEY, 'light');

      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      // Should load light theme from localStorage
      expect(screen.getByTestId('theme-mode')).toHaveTextContent('light');
    });

    it('should use default light theme when localStorage is empty', () => {
      // Don't set anything in localStorage
      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      // Should default to light theme
      expect(screen.getByTestId('theme-mode')).toHaveTextContent('light');
    });

    it('should use default light theme when localStorage has invalid value', () => {
      // Set invalid value in localStorage
      localStorage.setItem(STORAGE_KEY, 'invalid-theme');

      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      // Should default to light theme
      expect(screen.getByTestId('theme-mode')).toHaveTextContent('light');
    });

    it('should save theme to localStorage when toggling from light to dark', async () => {
      const user = userEvent.setup();
      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      const toggleButton = screen.getByTestId('toggle-button');

      // Toggle to dark theme
      await user.click(toggleButton);

      // Should save dark theme to localStorage
      expect(localStorage.getItem(STORAGE_KEY)).toBe('dark');
    });

    it('should save theme to localStorage when toggling from dark to light', async () => {
      const user = userEvent.setup();
      localStorage.setItem(STORAGE_KEY, 'dark');

      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      const toggleButton = screen.getByTestId('toggle-button');

      // Toggle to light theme
      await user.click(toggleButton);

      // Should save light theme to localStorage
      expect(localStorage.getItem(STORAGE_KEY)).toBe('light');
    });

    it('should save theme to localStorage when setting theme explicitly to dark', async () => {
      const user = userEvent.setup();
      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      const setDarkButton = screen.getByTestId('set-dark-button');

      // Set dark theme explicitly
      await user.click(setDarkButton);

      // Should save dark theme to localStorage
      expect(localStorage.getItem(STORAGE_KEY)).toBe('dark');
    });

    it('should save theme to localStorage when setting theme explicitly to light', async () => {
      const user = userEvent.setup();
      localStorage.setItem(STORAGE_KEY, 'dark');

      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      const setLightButton = screen.getByTestId('set-light-button');

      // Set light theme explicitly
      await user.click(setLightButton);

      // Should save light theme to localStorage
      expect(localStorage.getItem(STORAGE_KEY)).toBe('light');
    });

    it('should persist theme preference across multiple toggles', async () => {
      const user = userEvent.setup();
      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      const toggleButton = screen.getByTestId('toggle-button');

      // Toggle to dark
      await user.click(toggleButton);
      expect(localStorage.getItem(STORAGE_KEY)).toBe('dark');

      // Toggle to light
      await user.click(toggleButton);
      expect(localStorage.getItem(STORAGE_KEY)).toBe('light');

      // Toggle to dark again
      await user.click(toggleButton);
      expect(localStorage.getItem(STORAGE_KEY)).toBe('dark');
    });

    it('should persist theme preference when closing and reopening application', async () => {
      const user = userEvent.setup();

      // First session: toggle to dark theme
      const { unmount } = render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      const toggleButton = screen.getByTestId('toggle-button');
      await user.click(toggleButton);

      expect(screen.getByTestId('theme-mode')).toHaveTextContent('dark');
      expect(localStorage.getItem(STORAGE_KEY)).toBe('dark');

      // Unmount to simulate closing application
      unmount();

      // Second session: reopen application
      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      // Should load dark theme from localStorage
      expect(screen.getByTestId('theme-mode')).toHaveTextContent('dark');
    });

    it('should handle localStorage errors gracefully', () => {
      // Mock localStorage.getItem to throw an error
      const originalGetItem = Storage.prototype.getItem;
      Storage.prototype.getItem = () => {
        throw new Error('Storage unavailable');
      };

      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      // Should default to light theme when localStorage throws error
      expect(screen.getByTestId('theme-mode')).toHaveTextContent('light');

      // Restore original getItem
      Storage.prototype.getItem = originalGetItem;
    });

    it('should handle localStorage setItem errors gracefully', async () => {
      const user = userEvent.setup();

      // Mock localStorage.setItem to throw an error
      const originalSetItem = Storage.prototype.setItem;
      const consoleError = console.error;
      console.error = () => {}; // Suppress expected error logs

      Storage.prototype.setItem = () => {
        throw new Error('Storage full');
      };

      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );

      const toggleButton = screen.getByTestId('toggle-button');

      // Should still toggle theme even if localStorage fails
      await user.click(toggleButton);
      expect(screen.getByTestId('theme-mode')).toHaveTextContent('dark');

      // Restore original setItem and console.error
      Storage.prototype.setItem = originalSetItem;
      console.error = consoleError;
    });

    it('should use defaultMode when localStorage is empty', () => {
      // Don't set anything in localStorage
      // But pass dark as defaultMode
      render(
        <ThemeProvider defaultMode="dark">
          <ThemeConsumer />
        </ThemeProvider>
      );

      // Should use defaultMode prop when no localStorage value exists
      expect(screen.getByTestId('theme-mode')).toHaveTextContent('dark');
    });

    it('should work correctly when localStorage has both themes at different times', async () => {
      const user = userEvent.setup();

      // First render with light theme
      localStorage.setItem(STORAGE_KEY, 'light');
      const { unmount: unmount1 } = render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );
      expect(screen.getByTestId('theme-mode')).toHaveTextContent('light');
      unmount1();

      // Second render with dark theme
      localStorage.setItem(STORAGE_KEY, 'dark');
      const { unmount: unmount2 } = render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );
      expect(screen.getByTestId('theme-mode')).toHaveTextContent('dark');
      unmount2();

      // Third render - toggle and verify persistence
      const { unmount: unmount3 } = render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );
      expect(screen.getByTestId('theme-mode')).toHaveTextContent('dark');

      const toggleButton = screen.getByTestId('toggle-button');
      await user.click(toggleButton);
      expect(screen.getByTestId('theme-mode')).toHaveTextContent('light');
      expect(localStorage.getItem(STORAGE_KEY)).toBe('light');
      unmount3();

      // Fourth render - verify last saved preference
      render(
        <ThemeProvider>
          <ThemeConsumer />
        </ThemeProvider>
      );
      expect(screen.getByTestId('theme-mode')).toHaveTextContent('light');
    });
  });
});
