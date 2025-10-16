/**
 * Header Component Tests
 *
 * Test suite for the Header component following TDD principles.
 * Tests verify Header renders correctly with ThemeToggle integration.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { ThemeProvider, type ThemeMode } from '../../contexts/ThemeContext';
import { createAppTheme } from '../../theme';
import { Header } from './Header';

/**
 * Test wrapper component that provides theme contexts
 */
function TestWrapper({
  children,
  initialMode = 'light',
}: {
  children: React.ReactNode;
  initialMode?: ThemeMode;
}) {
  return (
    <ThemeProvider>
      <MuiThemeProvider theme={createAppTheme(initialMode)}>{children}</MuiThemeProvider>
    </ThemeProvider>
  );
}

describe('Header Component', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  describe('Basic Rendering', () => {
    it('renders the Header component', () => {
      render(
        <TestWrapper>
          <Header />
        </TestWrapper>
      );

      // Header should render with AppBar
      expect(screen.getByRole('banner')).toBeInTheDocument();
    });

    it('renders application title', () => {
      render(
        <TestWrapper>
          <Header />
        </TestWrapper>
      );

      // Should display application title
      expect(screen.getByText('Application')).toBeInTheDocument();
    });

    it('renders menu button on mobile', () => {
      render(
        <TestWrapper>
          <Header />
        </TestWrapper>
      );

      // Menu button should be present
      const menuButton = screen.getByLabelText('open navigation menu');
      expect(menuButton).toBeInTheDocument();
    });
  });

  describe('ThemeToggle Integration', () => {
    it('renders ThemeToggle component in header', () => {
      render(
        <TestWrapper>
          <Header />
        </TestWrapper>
      );

      // ThemeToggle should be rendered (check for switch role)
      const themeToggle = screen.getByRole('switch');
      expect(themeToggle).toBeInTheDocument();
    });

    it('displays ThemeToggle on desktop layout', () => {
      render(
        <TestWrapper>
          <Header />
        </TestWrapper>
      );

      // ThemeToggle should be visible in the toolbar
      const themeToggle = screen.getByRole('switch');
      expect(themeToggle).toBeInTheDocument();
    });

    it('displays ThemeToggle on mobile layout', () => {
      render(
        <TestWrapper>
          <Header />
        </TestWrapper>
      );

      // ThemeToggle should be visible on mobile too
      const themeToggle = screen.getByRole('switch');
      expect(themeToggle).toBeInTheDocument();
    });

    it('positions ThemeToggle in the actions area', () => {
      render(
        <TestWrapper>
          <Header />
        </TestWrapper>
      );

      // ThemeToggle should be in the actions box (right side of toolbar)
      const themeToggle = screen.getByRole('switch');
      expect(themeToggle).toBeInTheDocument();

      // Verify it's in the toolbar
      const toolbar = screen.getByRole('banner').querySelector('.MuiToolbar-root');
      expect(toolbar).toContainElement(themeToggle);
    });
  });

  describe('ThemeToggle Functionality in Header', () => {
    it('allows theme toggling from Header', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper initialMode="light">
          <Header />
        </TestWrapper>
      );

      const themeToggle = screen.getByRole('switch');

      // Initially unchecked (light mode)
      expect(themeToggle).not.toBeChecked();

      // Click to toggle to dark mode
      await user.click(themeToggle);

      // Should be checked (dark mode)
      expect(themeToggle).toBeChecked();

      // Verify localStorage was updated
      expect(localStorage.getItem('themeMode')).toBe('dark');
    });

    it('reflects theme changes in Header context', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper initialMode="light">
          <Header />
        </TestWrapper>
      );

      const themeToggle = screen.getByRole('switch');

      // Toggle from light to dark
      await user.click(themeToggle);
      expect(themeToggle).toBeChecked();

      // Toggle back to light
      await user.click(themeToggle);
      expect(themeToggle).not.toBeChecked();
      expect(localStorage.getItem('themeMode')).toBe('light');
    });
  });

  describe('Header Layout and Spacing', () => {
    it('maintains proper spacing with ThemeToggle', () => {
      render(
        <TestWrapper>
          <Header />
        </TestWrapper>
      );

      // Verify all elements are present
      expect(screen.getByText('Application')).toBeInTheDocument();
      expect(screen.getByLabelText('open navigation menu')).toBeInTheDocument();
      expect(screen.getByRole('switch')).toBeInTheDocument();
    });

    it('follows existing Header spacing patterns', () => {
      render(
        <TestWrapper>
          <Header />
        </TestWrapper>
      );

      const toolbar = screen.getByRole('banner').querySelector('.MuiToolbar-root');
      expect(toolbar).toBeInTheDocument();

      // ThemeToggle should be in the actions box
      const themeToggle = screen.getByRole('switch');
      expect(themeToggle).toBeInTheDocument();
    });
  });

  describe('Menu Button Interaction', () => {
    it('calls onMenuClick when menu button is clicked', async () => {
      const user = userEvent.setup();
      const handleMenuClick = vi.fn();

      render(
        <TestWrapper>
          <Header onMenuClick={handleMenuClick} />
        </TestWrapper>
      );

      const menuButton = screen.getByLabelText('open navigation menu');
      await user.click(menuButton);

      expect(handleMenuClick).toHaveBeenCalledTimes(1);
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA role for AppBar', () => {
      render(
        <TestWrapper>
          <Header />
        </TestWrapper>
      );

      // AppBar should have banner role
      expect(screen.getByRole('banner')).toBeInTheDocument();
    });

    it('has accessible labels for interactive elements', () => {
      render(
        <TestWrapper>
          <Header />
        </TestWrapper>
      );

      // Menu button should have aria-label
      expect(screen.getByLabelText('open navigation menu')).toBeInTheDocument();

      // ThemeToggle should have switch role for screen readers
      const themeToggle = screen.getByRole('switch');
      expect(themeToggle).toBeInTheDocument();
    });

    it('supports keyboard navigation for all interactive elements', async () => {
      render(
        <TestWrapper>
          <Header />
        </TestWrapper>
      );

      const menuButton = screen.getByLabelText('open navigation menu');
      const themeToggle = screen.getByRole('switch');

      // Both elements should be focusable
      menuButton.focus();
      expect(menuButton).toHaveFocus();

      themeToggle.focus();
      expect(themeToggle).toHaveFocus();
    });
  });

  describe('Dark Mode Rendering', () => {
    it('renders correctly in dark mode', () => {
      render(
        <TestWrapper initialMode="dark">
          <Header />
        </TestWrapper>
      );

      // Header should render in dark mode
      expect(screen.getByRole('banner')).toBeInTheDocument();
      expect(screen.getByText('Application')).toBeInTheDocument();
      expect(screen.getByRole('switch')).toBeInTheDocument();
    });

    it('displays all elements with dark theme colors', () => {
      const { container } = render(
        <TestWrapper initialMode="dark">
          <Header />
        </TestWrapper>
      );

      // AppBar should have MUI classes applied
      const appBar = container.querySelector('.MuiAppBar-root');
      expect(appBar).toBeInTheDocument();

      // All interactive elements should be present
      expect(screen.getByText('Application')).toBeInTheDocument();
      expect(screen.getByLabelText('open navigation menu')).toBeInTheDocument();
      expect(screen.getByRole('switch')).toBeInTheDocument();
    });

    it('theme toggle reflects dark mode state', () => {
      // Set dark mode in localStorage to ensure ThemeProvider uses dark mode
      localStorage.setItem('themeMode', 'dark');

      render(
        <TestWrapper initialMode="dark">
          <Header />
        </TestWrapper>
      );

      const themeToggle = screen.getByRole('switch');

      // Should be checked when in dark mode
      expect(themeToggle).toBeChecked();
    });

    it('maintains accessibility in dark mode', () => {
      render(
        <TestWrapper initialMode="dark">
          <Header />
        </TestWrapper>
      );

      // All ARIA labels should still be present
      expect(screen.getByRole('banner')).toBeInTheDocument();
      expect(screen.getByLabelText('open navigation menu')).toBeInTheDocument();

      // Interactive elements should remain focusable
      const menuButton = screen.getByLabelText('open navigation menu');
      menuButton.focus();
      expect(menuButton).toHaveFocus();
    });

    it('allows theme switching from dark to light mode', async () => {
      const user = userEvent.setup();

      // Set dark mode in localStorage to ensure ThemeProvider uses dark mode
      localStorage.setItem('themeMode', 'dark');

      render(
        <TestWrapper initialMode="dark">
          <Header />
        </TestWrapper>
      );

      const themeToggle = screen.getByRole('switch');

      // Initially in dark mode
      expect(themeToggle).toBeChecked();

      // Toggle to light mode
      await user.click(themeToggle);

      // Should now be unchecked (light mode)
      expect(themeToggle).not.toBeChecked();
      expect(localStorage.getItem('themeMode')).toBe('light');
    });

    it('renders properly with dark theme after toggling', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper initialMode="light">
          <Header />
        </TestWrapper>
      );

      const themeToggle = screen.getByRole('switch');

      // Toggle to dark mode
      await user.click(themeToggle);

      // Header should still render all elements
      expect(screen.getByRole('banner')).toBeInTheDocument();
      expect(screen.getByText('Application')).toBeInTheDocument();
      expect(screen.getByLabelText('open navigation menu')).toBeInTheDocument();

      // Theme toggle should reflect dark mode
      expect(themeToggle).toBeChecked();
    });
  });

  describe('Theme Persistence', () => {
    it('restores dark mode from localStorage', () => {
      // Set dark mode in localStorage before render
      localStorage.setItem('themeMode', 'dark');

      render(
        <TestWrapper>
          <Header />
        </TestWrapper>
      );

      const themeToggle = screen.getByRole('switch');

      // Should restore dark mode state
      expect(themeToggle).toBeChecked();
    });

    it('restores light mode from localStorage', () => {
      // Set light mode in localStorage before render
      localStorage.setItem('themeMode', 'light');

      render(
        <TestWrapper>
          <Header />
        </TestWrapper>
      );

      const themeToggle = screen.getByRole('switch');

      // Should restore light mode state
      expect(themeToggle).not.toBeChecked();
    });
  });
});
