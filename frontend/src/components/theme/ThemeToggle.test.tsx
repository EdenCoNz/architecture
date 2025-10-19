/**
 * ThemeToggle Component Tests
 *
 * Tests for theme toggle control including interaction, accessibility,
 * and visual feedback.
 */

import { describe, it, expect } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '../../test/test-utils';
import ThemeToggle from './ThemeToggle';

describe('ThemeToggle', () => {
  describe('Rendering', () => {
    it('should render the theme toggle button', () => {
      render(<ThemeToggle />);
      const button = screen.getByRole('button', { name: /switch to/i });
      expect(button).toBeInTheDocument();
    });

    it('should display light mode icon when in light mode', () => {
      render(<ThemeToggle />, {
        preloadedState: {
          theme: { mode: 'light' },
        },
      });

      const button = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(button).toBeInTheDocument();
    });

    it('should display dark mode icon when in dark mode', () => {
      render(<ThemeToggle />, {
        preloadedState: {
          theme: { mode: 'dark' },
        },
      });

      const button = screen.getByRole('button', { name: /switch to light mode/i });
      expect(button).toBeInTheDocument();
    });

    it('should have proper tooltip text', async () => {
      const user = userEvent.setup();
      render(<ThemeToggle />);

      const button = screen.getByRole('button', { name: /switch to/i });
      await user.hover(button);

      await waitFor(() => {
        expect(screen.getByRole('tooltip')).toBeInTheDocument();
      });
    });
  });

  describe('Interaction', () => {
    it('should toggle theme when clicked', async () => {
      const user = userEvent.setup();
      const { store } = render(<ThemeToggle />);

      const button = screen.getByRole('button', { name: /switch to/i });

      // Initial state is light
      expect((store.getState() as { theme: { mode: string } }).theme.mode).toBe('light');

      // Click to toggle to dark
      await user.click(button);
      expect((store.getState() as { theme: { mode: string } }).theme.mode).toBe('dark');

      // Click to toggle back to light
      await user.click(button);
      expect((store.getState() as { theme: { mode: string } }).theme.mode).toBe('light');
    });

    it('should toggle with keyboard (Enter)', async () => {
      const user = userEvent.setup();
      const { store } = render(<ThemeToggle />);

      const button = screen.getByRole('button', { name: /switch to/i });
      button.focus();

      await user.keyboard('{Enter}');
      expect((store.getState() as { theme: { mode: string } }).theme.mode).toBe('dark');
    });

    it('should toggle with keyboard (Space)', async () => {
      const user = userEvent.setup();
      const { store } = render(<ThemeToggle />);

      const button = screen.getByRole('button', { name: /switch to/i });
      button.focus();

      await user.keyboard(' ');
      expect((store.getState() as { theme: { mode: string } }).theme.mode).toBe('dark');
    });
  });

  describe('Accessibility', () => {
    it('should have accessible name', () => {
      render(<ThemeToggle />);
      const button = screen.getByRole('button', { name: /switch to/i });
      expect(button).toHaveAccessibleName();
    });

    it('should be keyboard focusable', () => {
      render(<ThemeToggle />);
      const button = screen.getByRole('button', { name: /switch to/i });
      button.focus();
      expect(button).toHaveFocus();
    });

    it('should update aria-label when theme changes', async () => {
      const user = userEvent.setup();
      render(<ThemeToggle />);

      const button = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(button).toBeInTheDocument();

      await user.click(button);

      const updatedButton = screen.getByRole('button', { name: /switch to light mode/i });
      expect(updatedButton).toBeInTheDocument();
    });

    it('should have role="button"', () => {
      render(<ThemeToggle />);
      const button = screen.getByRole('button', { name: /switch to/i });
      expect(button).toHaveAttribute('role', 'button');
    });
  });

  describe('Visual Feedback', () => {
    it('should show different icons for different modes', () => {
      // Test light mode
      const { unmount: unmount1 } = render(<ThemeToggle />, {
        preloadedState: {
          theme: { mode: 'light' },
        },
      });

      // Light mode should show dark mode icon (toggle action)
      expect(screen.getByRole('button', { name: /dark mode/i })).toBeInTheDocument();
      unmount1();

      // Test dark mode
      render(<ThemeToggle />, {
        preloadedState: {
          theme: { mode: 'dark' },
        },
      });

      // Dark mode should show light mode icon (toggle action)
      expect(screen.getByRole('button', { name: /light mode/i })).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle rapid clicks', async () => {
      const user = userEvent.setup();
      const { store } = render(<ThemeToggle />);

      const button = screen.getByRole('button', { name: /switch to/i });

      // Rapid clicks
      await user.click(button);
      await user.click(button);
      await user.click(button);

      // Should be in dark mode after odd number of clicks
      expect((store.getState() as { theme: { mode: string } }).theme.mode).toBe('dark');
    });

    it('should work when starting in auto mode', async () => {
      const user = userEvent.setup();
      const { store } = render(<ThemeToggle />, {
        preloadedState: {
          theme: { mode: 'auto' },
        },
      });

      const button = screen.getByRole('button', { name: /switch to/i });
      await user.click(button);

      // Should switch from auto to dark
      expect((store.getState() as { theme: { mode: string } }).theme.mode).toBe('dark');
    });
  });
});
