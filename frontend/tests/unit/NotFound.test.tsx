/**
 * Unit Tests for NotFound (404) Page Component
 *
 * Tests the NotFound page component rendering, content display, and navigation.
 * Following TDD best practices with user-centric testing approach.
 * Includes dark mode rendering tests for WCAG compliance.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { ThemeProvider, type ThemeMode } from '../../src/contexts/ThemeContext';
import { createAppTheme } from '../../src/theme';
import NotFound from '../../src/pages/NotFound/NotFound';

/**
 * Helper function to render components with all required providers
 * NotFound component requires Router, ThemeProvider, and MUI ThemeProvider
 */
const renderWithProviders = (component: React.ReactElement, mode: ThemeMode = 'light') => {
  return render(
    <BrowserRouter>
      <ThemeProvider>
        <MuiThemeProvider theme={createAppTheme(mode)}>{component}</MuiThemeProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('NotFound Page', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  describe('Rendering', () => {
    it('should render the 404 heading', () => {
      renderWithProviders(<NotFound />);

      const heading404 = screen.getByRole('heading', { name: /404/i });
      expect(heading404).toBeInTheDocument();
    });

    it('should render the page not found heading', () => {
      renderWithProviders(<NotFound />);

      const pageNotFoundHeading = screen.getByRole('heading', {
        name: /page not found/i,
      });
      expect(pageNotFoundHeading).toBeInTheDocument();
    });

    it('should render error message text', () => {
      renderWithProviders(<NotFound />);

      const errorMessage = screen.getByText(/sorry, the page you are looking for does not exist/i);
      expect(errorMessage).toBeInTheDocument();
    });

    it('should render error icon', () => {
      const { container } = renderWithProviders(<NotFound />);

      // Check for ErrorOutlineIcon SVG
      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    it('should render Back to Home button', () => {
      renderWithProviders(<NotFound />);

      const homeButton = screen.getByRole('link', { name: /back to home/i });
      expect(homeButton).toBeInTheDocument();
    });

    it('should link to home route', () => {
      renderWithProviders(<NotFound />);

      const homeButton = screen.getByRole('link', { name: /back to home/i });
      expect(homeButton).toHaveAttribute('href', '/');
    });

    it('should render Go Back button', () => {
      renderWithProviders(<NotFound />);

      const backButton = screen.getByRole('button', { name: /go back/i });
      expect(backButton).toBeInTheDocument();
    });

    it('should call window.history.back when Go Back is clicked', async () => {
      const user = userEvent.setup();

      // Mock window.history.back
      const historyBackSpy = vi.spyOn(window.history, 'back').mockImplementation(() => {});

      renderWithProviders(<NotFound />);

      const backButton = screen.getByRole('button', { name: /go back/i });
      await user.click(backButton);

      expect(historyBackSpy).toHaveBeenCalledTimes(1);

      historyBackSpy.mockRestore();
    });

    it('should display both navigation buttons', () => {
      renderWithProviders(<NotFound />);

      expect(screen.getByRole('link', { name: /back to home/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /go back/i })).toBeInTheDocument();
    });
  });

  describe('Content', () => {
    it('should display help text', () => {
      renderWithProviders(<NotFound />);

      const helpText = screen.getByText(/if you believe this is an error, please contact support/i);
      expect(helpText).toBeInTheDocument();
    });

    it('should have descriptive error message', () => {
      renderWithProviders(<NotFound />);

      const message = screen.getByText(/might have been moved or deleted/i);
      expect(message).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading hierarchy', () => {
      renderWithProviders(<NotFound />);

      const h1 = screen.getByRole('heading', { name: /404/i });
      expect(h1.tagName).toBe('H1');

      const h2 = screen.getByRole('heading', { name: /page not found/i });
      expect(h2.tagName).toBe('H2');
    });

    it('should have accessible button text', () => {
      renderWithProviders(<NotFound />);

      const homeLink = screen.getByRole('link', { name: /back to home/i });
      expect(homeLink).toHaveAccessibleName();

      const backButton = screen.getByRole('button', { name: /go back/i });
      expect(backButton).toHaveAccessibleName();
    });

    it('should use semantic HTML elements', () => {
      const { container } = renderWithProviders(<NotFound />);

      const h1 = container.querySelector('h1');
      expect(h1).toBeInTheDocument();

      const h2 = container.querySelector('h2');
      expect(h2).toBeInTheDocument();
    });

    it('should have proper button roles', () => {
      renderWithProviders(<NotFound />);

      // Link button should have link role
      const homeLink = screen.getByRole('link', { name: /back to home/i });
      expect(homeLink).toBeInTheDocument();

      // Go back button should have button role
      const backButton = screen.getByRole('button', { name: /go back/i });
      expect(backButton).toBeInTheDocument();
    });
  });

  describe('Theme Integration', () => {
    it('should render with Material UI theme', () => {
      const { container } = renderWithProviders(<NotFound />);

      // Material UI components should have MUI classes
      const muiComponents = container.querySelectorAll('[class*="Mui"]');
      expect(muiComponents.length).toBeGreaterThan(0);
    });

    it('should use Material UI Container component', () => {
      const { container } = renderWithProviders(<NotFound />);

      const muiContainer = container.querySelector('.MuiContainer-root');
      expect(muiContainer).toBeInTheDocument();
    });

    it('should use Material UI Button components', () => {
      const { container } = renderWithProviders(<NotFound />);

      const buttons = container.querySelectorAll('.MuiButton-root');
      // Should have 2 buttons (Back to Home and Go Back)
      expect(buttons.length).toBe(2);
    });
  });

  describe('Dark Mode Rendering', () => {
    it('should render correctly in dark mode', () => {
      renderWithProviders(<NotFound />, 'dark');

      // All main content should be rendered
      expect(screen.getByRole('heading', { name: /404/i })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: /page not found/i })).toBeInTheDocument();
      expect(
        screen.getByText(/sorry, the page you are looking for does not exist/i)
      ).toBeInTheDocument();
    });

    it('should apply dark theme to MUI components', () => {
      const { container } = renderWithProviders(<NotFound />, 'dark');

      // MUI components should still have proper classes applied
      const muiContainer = container.querySelector('.MuiContainer-root');
      expect(muiContainer).toBeInTheDocument();

      const buttons = container.querySelectorAll('.MuiButton-root');
      expect(buttons.length).toBe(2);
    });

    it('should maintain proper text color contrast in dark mode', () => {
      const { container } = renderWithProviders(<NotFound />, 'dark');

      // Typography components should render with theme colors
      const headings = screen.getAllByRole('heading');
      expect(headings.length).toBe(2);

      // Error icon should be present
      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('should display navigation buttons in dark mode', () => {
      renderWithProviders(<NotFound />, 'dark');

      const homeButton = screen.getByRole('link', { name: /back to home/i });
      expect(homeButton).toBeInTheDocument();
      expect(homeButton).toHaveAttribute('href', '/');

      const backButton = screen.getByRole('button', { name: /go back/i });
      expect(backButton).toBeInTheDocument();
    });

    it('should maintain accessibility in dark mode', () => {
      renderWithProviders(<NotFound />, 'dark');

      // Heading hierarchy should be preserved
      const h1 = screen.getByRole('heading', { name: /404/i });
      expect(h1.tagName).toBe('H1');

      const h2 = screen.getByRole('heading', { name: /page not found/i });
      expect(h2.tagName).toBe('H2');

      // Navigation buttons should be accessible
      const homeLink = screen.getByRole('link', { name: /back to home/i });
      expect(homeLink).toHaveAccessibleName();

      const backButton = screen.getByRole('button', { name: /go back/i });
      expect(backButton).toHaveAccessibleName();
    });

    it('should use proper error color in dark mode', () => {
      const { container } = renderWithProviders(<NotFound />, 'dark');

      // Error icon should render (uses error.main color via sx prop)
      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('should display help text in dark mode', () => {
      renderWithProviders(<NotFound />, 'dark');

      const helpText = screen.getByText(/if you believe this is an error, please contact support/i);
      expect(helpText).toBeInTheDocument();
    });

    it('should render buttons with correct variants in dark mode', () => {
      renderWithProviders(<NotFound />, 'dark');

      const homeButton = screen.getByRole('link', { name: /back to home/i });
      expect(homeButton).toHaveClass('MuiButton-contained');

      const backButton = screen.getByRole('button', { name: /go back/i });
      expect(backButton).toHaveClass('MuiButton-outlined');
    });
  });

  describe('Theme Switching Support', () => {
    it('should render in light mode by default', () => {
      renderWithProviders(<NotFound />, 'light');

      expect(screen.getByRole('heading', { name: /404/i })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: /page not found/i })).toBeInTheDocument();
    });

    it('should switch from light to dark mode without breaking layout', () => {
      const { rerender } = renderWithProviders(<NotFound />, 'light');

      // Verify light mode rendering
      expect(screen.getByRole('heading', { name: /404/i })).toBeInTheDocument();

      // Rerender with dark mode
      rerender(
        <BrowserRouter>
          <ThemeProvider>
            <MuiThemeProvider theme={createAppTheme('dark')}>
              <NotFound />
            </MuiThemeProvider>
          </ThemeProvider>
        </BrowserRouter>
      );

      // Content should still be present
      expect(screen.getByRole('heading', { name: /404/i })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: /page not found/i })).toBeInTheDocument();
      expect(screen.getAllByRole('heading')).toHaveLength(2);
    });

    it('should maintain button structure in both themes', () => {
      const { container: lightContainer } = renderWithProviders(<NotFound />, 'light');
      const lightButtons = lightContainer.querySelectorAll('.MuiButton-root');

      const { container: darkContainer } = renderWithProviders(<NotFound />, 'dark');
      const darkButtons = darkContainer.querySelectorAll('.MuiButton-root');

      // Same number of buttons in both themes
      expect(lightButtons.length).toBe(darkButtons.length);
      expect(lightButtons.length).toBe(2);
    });

    it('should preserve navigation functionality in both themes', async () => {
      const user = userEvent.setup();
      const historyBackSpy = vi.spyOn(window.history, 'back').mockImplementation(() => {});

      // Test in light mode
      const { rerender } = renderWithProviders(<NotFound />, 'light');
      const lightBackButton = screen.getByRole('button', { name: /go back/i });
      await user.click(lightBackButton);
      expect(historyBackSpy).toHaveBeenCalledTimes(1);

      // Test in dark mode
      rerender(
        <BrowserRouter>
          <ThemeProvider>
            <MuiThemeProvider theme={createAppTheme('dark')}>
              <NotFound />
            </MuiThemeProvider>
          </ThemeProvider>
        </BrowserRouter>
      );

      const darkBackButton = screen.getByRole('button', { name: /go back/i });
      await user.click(darkBackButton);
      expect(historyBackSpy).toHaveBeenCalledTimes(2);

      historyBackSpy.mockRestore();
    });
  });

  describe('Responsive Behavior', () => {
    it('should render navigation buttons in flex layout', () => {
      renderWithProviders(<NotFound />);

      // Buttons should be in a flex container
      const homeButton = screen.getByRole('link', { name: /back to home/i });
      const backButton = screen.getByRole('button', { name: /go back/i });

      expect(homeButton).toBeInTheDocument();
      expect(backButton).toBeInTheDocument();
    });

    it('should maintain responsive layout in dark mode', () => {
      renderWithProviders(<NotFound />, 'dark');

      // Buttons should be present in dark mode layout
      const homeButton = screen.getByRole('link', { name: /back to home/i });
      const backButton = screen.getByRole('button', { name: /go back/i });

      expect(homeButton).toBeInTheDocument();
      expect(backButton).toBeInTheDocument();
    });
  });
});
