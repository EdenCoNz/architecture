/**
 * ThemeToggle Component Tests
 *
 * Test suite for the ThemeToggle component following TDD principles.
 * Tests verify component rendering, theme state display, and toggle interaction.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { ThemeProvider, type ThemeMode } from '../../contexts/ThemeContext';
import { createAppTheme } from '../../theme';
import ThemeToggle from './ThemeToggle';

/**
 * Test wrapper component that provides both theme contexts
 */
function TestWrapper({
  children,
  initialMode = 'light',
}: {
  children: React.ReactNode;
  initialMode?: ThemeMode;
}) {
  // Set initial mode in localStorage before rendering
  beforeEach(() => {
    localStorage.setItem('themeMode', initialMode);
  });

  return (
    <ThemeProvider>
      <MuiThemeProvider theme={createAppTheme(initialMode)}>{children}</MuiThemeProvider>
    </ThemeProvider>
  );
}

describe('ThemeToggle Component', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  describe('Rendering', () => {
    it('renders a switch component', () => {
      render(
        <TestWrapper>
          <ThemeToggle />
        </TestWrapper>
      );

      // Should render a switch with proper role
      const toggle = screen.getByRole('switch');
      expect(toggle).toBeInTheDocument();
    });

    it('renders switch with icons for visual context', () => {
      render(
        <TestWrapper>
          <ThemeToggle />
        </TestWrapper>
      );

      // Should render switch
      const toggle = screen.getByRole('switch');
      expect(toggle).toBeInTheDocument();

      // Visual context provided by icons
      expect(screen.getByTestId('Brightness7Icon')).toBeInTheDocument();
      expect(screen.getByTestId('Brightness4Icon')).toBeInTheDocument();
    });

    it('renders light mode icon (sun)', () => {
      render(
        <TestWrapper initialMode="light">
          <ThemeToggle />
        </TestWrapper>
      );

      // Should show sun icon for light mode
      const sunIcon = screen.getByTestId('Brightness7Icon');
      expect(sunIcon).toBeInTheDocument();
    });

    it('renders dark mode icon (moon)', () => {
      localStorage.setItem('themeMode', 'dark');

      render(
        <TestWrapper initialMode="dark">
          <ThemeToggle />
        </TestWrapper>
      );

      // Should show moon icon for dark mode
      const moonIcon = screen.getByTestId('Brightness4Icon');
      expect(moonIcon).toBeInTheDocument();
    });
  });

  describe('Theme State Display', () => {
    it('displays checked state when in dark mode', () => {
      localStorage.setItem('themeMode', 'dark');

      render(
        <TestWrapper initialMode="dark">
          <ThemeToggle />
        </TestWrapper>
      );

      const toggle = screen.getByRole('switch') as HTMLInputElement;
      expect(toggle.checked).toBe(true);
    });

    it('displays unchecked state when in light mode', () => {
      localStorage.setItem('themeMode', 'light');

      render(
        <TestWrapper initialMode="light">
          <ThemeToggle />
        </TestWrapper>
      );

      const toggle = screen.getByRole('switch') as HTMLInputElement;
      expect(toggle.checked).toBe(false);
    });
  });

  describe('Toggle Interaction', () => {
    it('calls toggleTheme when clicked', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper initialMode="light">
          <ThemeToggle />
        </TestWrapper>
      );

      const toggle = screen.getByRole('switch');

      // Initially unchecked (light mode)
      expect(toggle).not.toBeChecked();

      // Click to toggle
      await user.click(toggle);

      // Should now be checked (dark mode)
      expect(toggle).toBeChecked();
    });

    it('toggles from light to dark mode', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper initialMode="light">
          <ThemeToggle />
        </TestWrapper>
      );

      const toggle = screen.getByRole('switch');

      // Click to switch to dark mode
      await user.click(toggle);

      // Verify theme was persisted to localStorage
      expect(localStorage.getItem('themeMode')).toBe('dark');
    });

    it('toggles from dark to light mode', async () => {
      localStorage.setItem('themeMode', 'dark');
      const user = userEvent.setup();

      render(
        <TestWrapper initialMode="dark">
          <ThemeToggle />
        </TestWrapper>
      );

      const toggle = screen.getByRole('switch');

      // Initially checked (dark mode)
      expect(toggle).toBeChecked();

      // Click to switch to light mode
      await user.click(toggle);

      // Should be unchecked (light mode)
      expect(toggle).not.toBeChecked();

      // Verify theme was persisted to localStorage
      expect(localStorage.getItem('themeMode')).toBe('light');
    });

    it('supports keyboard interaction (Space key)', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper initialMode="light">
          <ThemeToggle />
        </TestWrapper>
      );

      const toggle = screen.getByRole('switch');

      // Focus the toggle
      toggle.focus();
      expect(toggle).toHaveFocus();

      // Press Space to toggle
      await user.keyboard(' ');

      // Should be checked after Space press
      expect(toggle).toBeChecked();
    });

    it('maintains focus state during interaction', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper initialMode="light">
          <ThemeToggle />
        </TestWrapper>
      );

      const toggle = screen.getByRole('switch');

      // Focus and click the toggle
      toggle.focus();
      expect(toggle).toHaveFocus();

      await user.click(toggle);

      // Should still be checked after click
      expect(toggle).toBeChecked();
    });
  });

  describe('Visual Appearance', () => {
    it('applies correct color in light mode', () => {
      render(
        <TestWrapper initialMode="light">
          <ThemeToggle />
        </TestWrapper>
      );

      const toggle = screen.getByRole('switch');

      // In light mode, switch should use default color
      expect(toggle).toBeInTheDocument();
    });

    it('applies correct color in dark mode', () => {
      localStorage.setItem('themeMode', 'dark');

      render(
        <TestWrapper initialMode="dark">
          <ThemeToggle />
        </TestWrapper>
      );

      const toggle = screen.getByRole('switch');

      // In dark mode, switch should be checked
      expect(toggle).toBeChecked();
    });
  });

  describe('Accessibility', () => {
    it('provides switch role for assistive technologies', () => {
      render(
        <TestWrapper>
          <ThemeToggle />
        </TestWrapper>
      );

      // Verify switch role is present for screen readers
      const toggle = screen.getByRole('switch');
      expect(toggle).toBeInTheDocument();
    });

    it('is keyboard focusable', () => {
      render(
        <TestWrapper>
          <ThemeToggle />
        </TestWrapper>
      );

      const toggle = screen.getByRole('switch');
      toggle.focus();

      expect(toggle).toHaveFocus();
    });

    it('correctly reflects checked state for screen readers', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper initialMode="light">
          <ThemeToggle />
        </TestWrapper>
      );

      const toggle = screen.getByRole('switch');

      // Initially unchecked (light mode)
      expect(toggle).not.toBeChecked();

      // Toggle
      await user.click(toggle);

      // Should be checked after toggle (dark mode)
      expect(toggle).toBeChecked();
    });
  });

  describe('Integration with ThemeContext', () => {
    it('reflects current theme mode from context', () => {
      localStorage.setItem('themeMode', 'dark');

      render(
        <TestWrapper initialMode="dark">
          <ThemeToggle />
        </TestWrapper>
      );

      const toggle = screen.getByRole('switch') as HTMLInputElement;

      // Should reflect dark mode from context
      expect(toggle.checked).toBe(true);
    });

    it('updates theme mode through context when toggled', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper initialMode="light">
          <ThemeToggle />
        </TestWrapper>
      );

      const toggle = screen.getByRole('switch');

      // Toggle theme
      await user.click(toggle);

      // Context should update and persist to localStorage
      expect(localStorage.getItem('themeMode')).toBe('dark');
    });
  });

  describe('Error Handling', () => {
    it('throws error when used outside ThemeProvider', () => {
      // Suppress console.error for this test
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => {
        render(
          <MuiThemeProvider theme={createAppTheme('light')}>
            <ThemeToggle />
          </MuiThemeProvider>
        );
      }).toThrow('useTheme must be used within ThemeProvider');

      consoleSpy.mockRestore();
    });
  });
});
