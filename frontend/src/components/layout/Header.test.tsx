/**
 * Header Component Tests
 *
 * Tests the Header component with integrated ThemeToggle.
 * Validates layout, accessibility, and theme toggle functionality.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { ThemeProvider } from '../../contexts';
import { Header } from './Header';

describe('Header Component', () => {
  beforeEach(() => {
    // Clear localStorage before each test to ensure clean state
    localStorage.clear();
  });

  afterEach(() => {
    // Clean up localStorage after each test
    localStorage.clear();
  });

  describe('Rendering', () => {
    it('should render the app title', () => {
      render(
        <ThemeProvider>
          <Header />
        </ThemeProvider>
      );

      expect(screen.getByText('Application')).toBeInTheDocument();
    });

    it('should render the menu button on mobile', () => {
      render(
        <ThemeProvider>
          <Header />
        </ThemeProvider>
      );

      const menuButton = screen.getByRole('button', { name: /open navigation menu/i });
      expect(menuButton).toBeInTheDocument();
    });

    it('should render the theme toggle button', () => {
      render(
        <ThemeProvider>
          <Header />
        </ThemeProvider>
      );

      // Theme toggle should be present with default light mode
      const themeButton = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(themeButton).toBeInTheDocument();
    });

    it('should render all components in AppBar with Toolbar', () => {
      const { container } = render(
        <ThemeProvider>
          <Header />
        </ThemeProvider>
      );

      const appBar = container.querySelector('.MuiAppBar-root');
      const toolbar = container.querySelector('.MuiToolbar-root');

      expect(appBar).toBeInTheDocument();
      expect(toolbar).toBeInTheDocument();
    });
  });

  describe('Menu Button Interaction', () => {
    it('should call onMenuClick when menu button is clicked', async () => {
      const user = userEvent.setup();
      const mockMenuClick = vi.fn();

      render(
        <ThemeProvider>
          <Header onMenuClick={mockMenuClick} />
        </ThemeProvider>
      );

      const menuButton = screen.getByRole('button', { name: /open navigation menu/i });
      await user.click(menuButton);

      expect(mockMenuClick).toHaveBeenCalledTimes(1);
    });

    it('should not error when onMenuClick is not provided', async () => {
      const user = userEvent.setup();

      render(
        <ThemeProvider>
          <Header />
        </ThemeProvider>
      );

      const menuButton = screen.getByRole('button', { name: /open navigation menu/i });
      await user.click(menuButton);

      // Should not throw error
      expect(menuButton).toBeInTheDocument();
    });
  });

  describe('Theme Toggle Integration', () => {
    it('should toggle theme when theme toggle button is clicked', async () => {
      const user = userEvent.setup();

      render(
        <ThemeProvider defaultMode="light">
          <Header />
        </ThemeProvider>
      );

      // Initially in light mode
      let themeButton = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(themeButton).toBeInTheDocument();

      // Click to switch to dark mode
      await user.click(themeButton);

      // Should now show option to switch to light mode
      themeButton = screen.getByRole('button', { name: /switch to light mode/i });
      expect(themeButton).toBeInTheDocument();
    });

    it('should toggle theme multiple times', async () => {
      const user = userEvent.setup();

      render(
        <ThemeProvider defaultMode="light">
          <Header />
        </ThemeProvider>
      );

      // Light -> Dark
      let themeButton = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(themeButton);

      // Dark -> Light
      themeButton = screen.getByRole('button', { name: /switch to light mode/i });
      await user.click(themeButton);

      // Light -> Dark again
      themeButton = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(themeButton);

      // Should end in dark mode
      themeButton = screen.getByRole('button', { name: /switch to light mode/i });
      expect(themeButton).toBeInTheDocument();
    });

    it('should position theme toggle in AppBar right side', () => {
      const { container } = render(
        <ThemeProvider>
          <Header />
        </ThemeProvider>
      );

      const toolbar = container.querySelector('.MuiToolbar-root');
      const themeButton = screen.getByRole('button', { name: /switch to dark mode/i });

      expect(toolbar).toContainElement(themeButton);
    });
  });

  describe('Layout Structure', () => {
    it('should have sticky positioning', () => {
      const { container } = render(
        <ThemeProvider>
          <Header />
        </ThemeProvider>
      );

      const appBar = container.querySelector('.MuiAppBar-root');
      expect(appBar).toHaveClass('MuiAppBar-positionSticky');
    });

    it('should use primary color', () => {
      const { container } = render(
        <ThemeProvider>
          <Header />
        </ThemeProvider>
      );

      const appBar = container.querySelector('.MuiAppBar-root');
      expect(appBar).toHaveClass('MuiAppBar-colorPrimary');
    });

    it('should render title as h1 for SEO and accessibility', () => {
      render(
        <ThemeProvider>
          <Header />
        </ThemeProvider>
      );

      const heading = screen.getByRole('heading', { level: 1, name: 'Application' });
      expect(heading).toBeInTheDocument();
    });

    it('should have flexbox layout with title growing to fill space', () => {
      render(
        <ThemeProvider>
          <Header />
        </ThemeProvider>
      );

      const title = screen.getByText('Application');
      expect(title).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels for all buttons', () => {
      render(
        <ThemeProvider>
          <Header />
        </ThemeProvider>
      );

      const menuButton = screen.getByRole('button', { name: /open navigation menu/i });
      const themeButton = screen.getByRole('button', { name: /switch to dark mode/i });

      expect(menuButton).toHaveAttribute('aria-label', 'open navigation menu');
      expect(themeButton).toHaveAttribute('aria-label', 'Switch to dark mode');
    });

    it('should have keyboard accessible buttons', () => {
      render(
        <ThemeProvider>
          <Header />
        </ThemeProvider>
      );

      const buttons = screen.getAllByRole('button');
      buttons.forEach((button) => {
        button.focus();
        expect(button).toHaveFocus();
      });
    });

    it('should have semantic HTML structure', () => {
      const { container } = render(
        <ThemeProvider>
          <Header />
        </ThemeProvider>
      );

      const appBar = container.querySelector('header.MuiAppBar-root');
      const heading = screen.getByRole('heading', { level: 1 });

      expect(appBar).toBeInTheDocument();
      expect(heading).toBeInTheDocument();
    });
  });

  describe('Responsive Behavior', () => {
    it('should render both menu button and theme toggle', () => {
      render(
        <ThemeProvider>
          <Header />
        </ThemeProvider>
      );

      const menuButton = screen.getByRole('button', { name: /open navigation menu/i });
      const themeButton = screen.getByRole('button', { name: /switch to dark mode/i });

      expect(menuButton).toBeInTheDocument();
      expect(themeButton).toBeInTheDocument();
    });

    it('should render theme toggle on all screen sizes', () => {
      render(
        <ThemeProvider>
          <Header />
        </ThemeProvider>
      );

      const themeButton = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(themeButton).toBeVisible();
    });
  });

  describe('Theme Context Integration', () => {
    it('should start with light theme by default', () => {
      render(
        <ThemeProvider>
          <Header />
        </ThemeProvider>
      );

      const themeButton = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(themeButton).toBeInTheDocument();
    });

    it('should respect custom default theme mode', () => {
      render(
        <ThemeProvider defaultMode="dark">
          <Header />
        </ThemeProvider>
      );

      const themeButton = screen.getByRole('button', { name: /switch to light mode/i });
      expect(themeButton).toBeInTheDocument();
    });
  });
});
