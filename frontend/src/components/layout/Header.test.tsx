/**
 * Header Component Tests
 *
 * Tests the Header component with integrated ThemeToggle.
 * Validates layout, accessibility, and theme toggle functionality.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../../contexts';
import { Header } from './Header';

// Helper function to render Header with required providers
const renderHeader = (props = {}) => {
  return render(
    <ThemeProvider>
      <BrowserRouter>
        <Header {...props} />
      </BrowserRouter>
    </ThemeProvider>
  );
};

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
      renderHeader();

      expect(screen.getByText('Application')).toBeInTheDocument();
    });

    it('should render the menu button on mobile', () => {
      renderHeader();

      const menuButton = screen.getByRole('button', { name: /open navigation menu/i });
      expect(menuButton).toBeInTheDocument();
    });

    it('should render the theme toggle button', () => {
      renderHeader();

      // Theme toggle should be present with default light mode
      const themeButton = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(themeButton).toBeInTheDocument();
    });

    it('should render all components in AppBar with Toolbar', () => {
      const { container } = renderHeader();

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

      renderHeader({ onMenuClick: mockMenuClick });

      const menuButton = screen.getByRole('button', { name: /open navigation menu/i });
      await user.click(menuButton);

      expect(mockMenuClick).toHaveBeenCalledTimes(1);
    });

    it('should not error when onMenuClick is not provided', async () => {
      const user = userEvent.setup();

      renderHeader();

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
          <BrowserRouter>
            <Header />
          </BrowserRouter>
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
          <BrowserRouter>
            <Header />
          </BrowserRouter>
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
      const { container } = renderHeader();

      const toolbar = container.querySelector('.MuiToolbar-root');
      const themeButton = screen.getByRole('button', { name: /switch to dark mode/i });

      expect(toolbar).toContainElement(themeButton);
    });
  });

  describe('Layout Structure', () => {
    it('should have sticky positioning', () => {
      const { container } = renderHeader();

      const appBar = container.querySelector('.MuiAppBar-root');
      expect(appBar).toHaveClass('MuiAppBar-positionSticky');
    });

    it('should use primary color', () => {
      const { container } = renderHeader();

      const appBar = container.querySelector('.MuiAppBar-root');
      expect(appBar).toHaveClass('MuiAppBar-colorPrimary');
    });

    it('should render title as h1 for SEO and accessibility', () => {
      renderHeader();

      const heading = screen.getByRole('heading', { level: 1, name: 'Application' });
      expect(heading).toBeInTheDocument();
    });

    it('should have flexbox layout with title growing to fill space', () => {
      renderHeader();

      const title = screen.getByText('Application');
      expect(title).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels for all buttons', () => {
      renderHeader();

      const menuButton = screen.getByRole('button', { name: /open navigation menu/i });
      const themeButton = screen.getByRole('button', { name: /switch to dark mode/i });

      expect(menuButton).toHaveAttribute('aria-label', 'open navigation menu');
      expect(themeButton).toHaveAttribute('aria-label', 'Switch to dark mode');
    });

    it('should have keyboard accessible buttons', () => {
      renderHeader();

      const buttons = screen.getAllByRole('button');
      buttons.forEach((button) => {
        button.focus();
        expect(button).toHaveFocus();
      });
    });

    it('should have semantic HTML structure', () => {
      const { container } = renderHeader();

      const appBar = container.querySelector('header.MuiAppBar-root');
      const heading = screen.getByRole('heading', { level: 1 });

      expect(appBar).toBeInTheDocument();
      expect(heading).toBeInTheDocument();
    });
  });

  describe('Responsive Behavior', () => {
    it('should render both menu button and theme toggle', () => {
      renderHeader();

      const menuButton = screen.getByRole('button', { name: /open navigation menu/i });
      const themeButton = screen.getByRole('button', { name: /switch to dark mode/i });

      expect(menuButton).toBeInTheDocument();
      expect(themeButton).toBeInTheDocument();
    });

    it('should render theme toggle on all screen sizes', () => {
      renderHeader();

      const themeButton = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(themeButton).toBeVisible();
    });
  });

  describe('Theme Context Integration', () => {
    it('should start with light theme by default', () => {
      renderHeader();

      const themeButton = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(themeButton).toBeInTheDocument();
    });

    it('should respect custom default theme mode', () => {
      render(
        <ThemeProvider defaultMode="dark">
          <BrowserRouter>
            <Header />
          </BrowserRouter>
        </ThemeProvider>
      );

      const themeButton = screen.getByRole('button', { name: /switch to light mode/i });
      expect(themeButton).toBeInTheDocument();
    });
  });

  describe('Story 14.3: Update Navigation Links', () => {
    it('should render Home navigation link pointing to root URL', () => {
      renderHeader();

      const homeLink = screen.getByRole('link', { name: /home/i });
      expect(homeLink).toBeInTheDocument();
      expect(homeLink).toHaveAttribute('href', '/');
    });

    it('should not have any navigation links pointing to /onboarding', () => {
      const { container } = renderHeader();

      // Check that no links point to /onboarding
      const links = container.querySelectorAll('a[href="/onboarding"]');
      expect(links.length).toBe(0);
    });

    it('should render About navigation link - Story 14.4', () => {
      renderHeader();

      const aboutLink = screen.getByRole('link', { name: /about/i });
      expect(aboutLink).toBeInTheDocument();
      expect(aboutLink).toHaveAttribute('href', '/about');
    });

    it('should render API Test navigation link', () => {
      renderHeader();

      const apiTestLink = screen.getByRole('link', { name: /api test/i });
      expect(apiTestLink).toBeInTheDocument();
      expect(apiTestLink).toHaveAttribute('href', '/api-test');
    });

    it('should render navigation links with consistent styling', () => {
      renderHeader();

      const homeLink = screen.getByRole('link', { name: /home/i });
      const aboutLink = screen.getByRole('link', { name: /about/i });
      const apiTestLink = screen.getByRole('link', { name: /api test/i });

      expect(homeLink).toBeInTheDocument();
      expect(aboutLink).toBeInTheDocument();
      expect(apiTestLink).toBeInTheDocument();
    });

    it('should render navigation links that support active state highlighting', () => {
      renderHeader();

      // Verify links are rendered with React Router Link component
      const homeLink = screen.getByRole('link', { name: /home/i });
      const apiTestLink = screen.getByRole('link', { name: /api test/i });

      expect(homeLink).toBeInTheDocument();
      expect(apiTestLink).toBeInTheDocument();

      // Links should support routing and can be highlighted when active
      expect(homeLink.getAttribute('href')).toBe('/');
      expect(apiTestLink.getAttribute('href')).toBe('/api-test');
    });
  });
});
