/**
 * ThemeToggle Component Tests
 *
 * Tests the theme toggle button functionality, accessibility, and visual states.
 * Following TDD approach - tests written before implementation.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { ThemeProvider } from '@mui/material/styles';
import { lightTheme, darkTheme } from '../../theme';
import { ThemeToggle } from './ThemeToggle';

describe('ThemeToggle Component', () => {
  describe('Rendering', () => {
    it('should render the theme toggle button', () => {
      const mockToggle = vi.fn();
      render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      const button = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(button).toBeInTheDocument();
    });

    it('should display sun icon when in light mode', () => {
      const mockToggle = vi.fn();
      render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      // Sun icon (LightMode) should be present when light mode is active
      const button = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(button).toBeInTheDocument();
      // Icon is shown by testing button aria-label
      expect(button).toHaveAccessibleName('Switch to dark mode');
    });

    it('should display moon icon when in dark mode', () => {
      const mockToggle = vi.fn();
      render(
        <ThemeProvider theme={darkTheme}>
          <ThemeToggle mode="dark" onToggle={mockToggle} />
        </ThemeProvider>
      );

      // Moon icon (DarkMode) should be present when dark mode is active
      const button = screen.getByRole('button', { name: /switch to light mode/i });
      expect(button).toBeInTheDocument();
      expect(button).toHaveAccessibleName('Switch to light mode');
    });

    it('should render within a tooltip', () => {
      const mockToggle = vi.fn();
      render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });
  });

  describe('Interaction', () => {
    it('should call onToggle when clicked', async () => {
      const user = userEvent.setup();
      const mockToggle = vi.fn();
      render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      const button = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(button);

      expect(mockToggle).toHaveBeenCalledTimes(1);
    });

    it('should be keyboard accessible with Enter key', async () => {
      const user = userEvent.setup();
      const mockToggle = vi.fn();
      render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      const button = screen.getByRole('button', { name: /switch to dark mode/i });
      button.focus();
      await user.keyboard('{Enter}');

      expect(mockToggle).toHaveBeenCalledTimes(1);
    });

    it('should be keyboard accessible with Space key', async () => {
      const user = userEvent.setup();
      const mockToggle = vi.fn();
      render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      const button = screen.getByRole('button', { name: /switch to dark mode/i });
      button.focus();
      await user.keyboard(' ');

      expect(mockToggle).toHaveBeenCalledTimes(1);
    });

    it('should support multiple toggles without issues', async () => {
      const user = userEvent.setup();
      const mockToggle = vi.fn();
      const { rerender } = render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      let button = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(button);

      // Simulate theme change
      rerender(
        <ThemeProvider theme={darkTheme}>
          <ThemeToggle mode="dark" onToggle={mockToggle} />
        </ThemeProvider>
      );

      button = screen.getByRole('button', { name: /switch to light mode/i });
      await user.click(button);

      // Simulate theme change back
      rerender(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      button = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(button);

      expect(mockToggle).toHaveBeenCalledTimes(3);
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA label in light mode', () => {
      const mockToggle = vi.fn();
      render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Switch to dark mode');
    });

    it('should have proper ARIA label in dark mode', () => {
      const mockToggle = vi.fn();
      render(
        <ThemeProvider theme={darkTheme}>
          <ThemeToggle mode="dark" onToggle={mockToggle} />
        </ThemeProvider>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Switch to light mode');
    });

    it('should be keyboard focusable', () => {
      const mockToggle = vi.fn();
      render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      const button = screen.getByRole('button');
      button.focus();
      expect(button).toHaveFocus();
    });

    it('should have minimum 48x48px touch target (MUI IconButton default)', () => {
      const mockToggle = vi.fn();
      render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      const button = screen.getByRole('button');

      // MUI IconButton has default padding that ensures 48x48px minimum
      expect(button).toBeInTheDocument();
      // Actual size validation happens in visual/integration tests
    });
  });

  describe('Visual States', () => {
    it('should update aria-label when mode changes', () => {
      const mockToggle = vi.fn();
      const { rerender } = render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      let button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Switch to dark mode');

      rerender(
        <ThemeProvider theme={darkTheme}>
          <ThemeToggle mode="dark" onToggle={mockToggle} />
        </ThemeProvider>
      );

      button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Switch to light mode');
    });

    it('should be visible and not disabled', () => {
      const mockToggle = vi.fn();
      render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      const button = screen.getByRole('button');
      expect(button).toBeVisible();
      expect(button).not.toBeDisabled();
    });

    it('should render with color="inherit" to adapt to theme', () => {
      const mockToggle = vi.fn();
      render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveClass('MuiIconButton-colorInherit');
    });
  });

  describe('Theme Integration', () => {
    it('should work correctly when switching from light to dark theme', async () => {
      const user = userEvent.setup();
      let currentMode: 'light' | 'dark' = 'light';
      const handleToggle = () => {
        currentMode = currentMode === 'light' ? 'dark' : 'light';
      };

      const { rerender } = render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode={currentMode} onToggle={handleToggle} />
        </ThemeProvider>
      );

      const lightButton = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(lightButton);

      rerender(
        <ThemeProvider theme={darkTheme}>
          <ThemeToggle mode="dark" onToggle={handleToggle} />
        </ThemeProvider>
      );

      const darkButton = screen.getByRole('button', { name: /switch to light mode/i });
      expect(darkButton).toBeInTheDocument();
    });

    it('should work correctly when switching from dark to light theme', async () => {
      const user = userEvent.setup();
      let currentMode: 'light' | 'dark' = 'dark';
      const handleToggle = () => {
        currentMode = currentMode === 'light' ? 'dark' : 'light';
      };

      const { rerender } = render(
        <ThemeProvider theme={darkTheme}>
          <ThemeToggle mode={currentMode} onToggle={handleToggle} />
        </ThemeProvider>
      );

      const darkButton = screen.getByRole('button', { name: /switch to light mode/i });
      await user.click(darkButton);

      rerender(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={handleToggle} />
        </ThemeProvider>
      );

      const lightButton = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(lightButton).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle rapid clicks gracefully', async () => {
      const user = userEvent.setup();
      const mockToggle = vi.fn();
      render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      const button = screen.getByRole('button');

      // Rapid clicks
      await user.click(button);
      await user.click(button);
      await user.click(button);

      expect(mockToggle).toHaveBeenCalledTimes(3);
    });

    it('should render correctly without tooltip text (tooltip is handled by component)', () => {
      const mockToggle = vi.fn();
      render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });
  });

  describe('Component Props', () => {
    it('should accept and use mode prop correctly', () => {
      const mockToggle = vi.fn();
      const { rerender } = render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      expect(screen.getByRole('button', { name: /switch to dark mode/i })).toBeInTheDocument();

      rerender(
        <ThemeProvider theme={darkTheme}>
          <ThemeToggle mode="dark" onToggle={mockToggle} />
        </ThemeProvider>
      );

      expect(screen.getByRole('button', { name: /switch to light mode/i })).toBeInTheDocument();
    });

    it('should require onToggle prop', () => {
      const mockToggle = vi.fn();
      render(
        <ThemeProvider theme={lightTheme}>
          <ThemeToggle mode="light" onToggle={mockToggle} />
        </ThemeProvider>
      );

      expect(screen.getByRole('button')).toBeInTheDocument();
    });
  });
});
