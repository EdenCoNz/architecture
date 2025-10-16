/**
 * Unit Tests for Header Component
 *
 * Tests the Header component rendering, accessibility, and user interactions.
 * Following TDD best practices with comprehensive test coverage.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { ThemeProvider } from '../../src/contexts/ThemeContext';
import { createAppTheme } from '../../src/theme';
import { Header } from '../../src/components/layout/Header';

/**
 * Helper function to render components with both Material UI theme and ThemeContext
 * Required for proper Material UI component rendering and theme toggle functionality
 */
const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider>
      <MuiThemeProvider theme={createAppTheme('light')}>{component}</MuiThemeProvider>
    </ThemeProvider>
  );
};

describe('Header Component', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  describe('Rendering', () => {
    it('should render the application title', () => {
      renderWithTheme(<Header />);

      const title = screen.getByText('Application');
      expect(title).toBeInTheDocument();
    });

    it('should render as an AppBar component', () => {
      const { container } = renderWithTheme(<Header />);

      // AppBar renders as a header element with specific role
      const header = container.querySelector('header');
      expect(header).toBeInTheDocument();
    });

    it('should render the menu button', () => {
      renderWithTheme(<Header />);

      const menuButton = screen.getByRole('button', { name: /open navigation menu/i });
      expect(menuButton).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA label on menu button', () => {
      renderWithTheme(<Header />);

      const menuButton = screen.getByRole('button', { name: /open navigation menu/i });
      expect(menuButton).toHaveAttribute('aria-label', 'open navigation menu');
    });

    it('should be keyboard accessible', () => {
      renderWithTheme(<Header />);

      const menuButton = screen.getByRole('button', { name: /open navigation menu/i });
      expect(menuButton).toHaveAttribute('type', 'button');
    });

    it('should render semantic HTML with header element', () => {
      const { container } = renderWithTheme(<Header />);

      const header = container.querySelector('header');
      expect(header).toBeInTheDocument();
    });
  });

  describe('Responsive Behavior', () => {
    it('should render menu icon for mobile view', () => {
      renderWithTheme(<Header />);

      // Menu button should be present (visibility controlled by CSS)
      const menuButton = screen.getByRole('button', { name: /open navigation menu/i });
      expect(menuButton).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('should call onMenuClick when menu button is clicked', async () => {
      const mockOnMenuClick = vi.fn();
      const user = userEvent.setup();

      renderWithTheme(<Header onMenuClick={mockOnMenuClick} />);

      const menuButton = screen.getByRole('button', { name: /open navigation menu/i });
      await user.click(menuButton);

      expect(mockOnMenuClick).toHaveBeenCalledTimes(1);
    });

    it('should not throw error when onMenuClick is not provided', async () => {
      const user = userEvent.setup();

      renderWithTheme(<Header />);

      const menuButton = screen.getByRole('button', { name: /open navigation menu/i });

      // Should not throw error when clicking without onMenuClick prop
      await expect(user.click(menuButton)).resolves.not.toThrow();
    });
  });

  describe('Styling and Theme Integration', () => {
    it('should apply Material UI theme correctly', () => {
      const { container } = renderWithTheme(<Header />);

      const header = container.querySelector('header');
      expect(header).toBeInTheDocument();

      // AppBar component should render with MUI classes
      expect(header).toHaveClass('MuiAppBar-root');
    });

    it('should use sticky positioning', () => {
      const { container } = renderWithTheme(<Header />);

      const header = container.querySelector('header');
      expect(header).toHaveClass('MuiAppBar-positionSticky');
    });
  });
});
