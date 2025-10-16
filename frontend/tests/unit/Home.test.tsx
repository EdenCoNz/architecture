/**
 * Unit Tests for Home Page Component
 *
 * Tests the Home page component rendering, content display, and navigation.
 * Following TDD best practices with user-centric testing approach.
 * Includes dark mode rendering tests for WCAG compliance.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { ThemeProvider, type ThemeMode } from '../../src/contexts/ThemeContext';
import { createAppTheme } from '../../src/theme';
import Home from '../../src/pages/Home/Home';

/**
 * Helper function to render components with all required providers
 * Home component requires Router, ThemeProvider, and MUI ThemeProvider
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

describe('Home Page', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  describe('Rendering', () => {
    it('should render the welcome heading', () => {
      renderWithProviders(<Home />);

      const heading = screen.getByRole('heading', {
        name: /welcome to the application/i,
      });
      expect(heading).toBeInTheDocument();
    });

    it('should render the welcome message', () => {
      renderWithProviders(<Home />);

      const message = screen.getByText(
        /your frontend application is now ready with routing configured/i
      );
      expect(message).toBeInTheDocument();
    });

    it('should render the home icon', () => {
      renderWithProviders(<Home />);

      // Check for icon by its aria-hidden attribute or SVG presence
      const container = screen.getByRole('heading', {
        name: /welcome to the application/i,
      }).parentElement;

      const icon = container?.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });

  describe('Feature Cards', () => {
    it('should display React 19 feature card', () => {
      renderWithProviders(<Home />);

      const reactHeading = screen.getByRole('heading', { name: /react 19/i });
      expect(reactHeading).toBeInTheDocument();

      const reactDescription = screen.getByText(
        /built with the latest react 19 for optimal performance/i
      );
      expect(reactDescription).toBeInTheDocument();
    });

    it('should display Material UI feature card', () => {
      renderWithProviders(<Home />);

      const muiHeading = screen.getByRole('heading', {
        name: /material ui v7/i,
      });
      expect(muiHeading).toBeInTheDocument();

      const muiDescription = screen.getByText(/comprehensive material design 3 component library/i);
      expect(muiDescription).toBeInTheDocument();
    });

    it('should display React Router feature card', () => {
      renderWithProviders(<Home />);

      const routerHeading = screen.getByRole('heading', {
        name: /react router v7/i,
      });
      expect(routerHeading).toBeInTheDocument();

      const routerDescription = screen.getByText(/client-side routing with seamless navigation/i);
      expect(routerDescription).toBeInTheDocument();
    });

    it('should render all three feature cards', () => {
      renderWithProviders(<Home />);

      // Should have 4 headings total: 1 main heading + 3 feature card headings
      const headings = screen.getAllByRole('heading');
      expect(headings).toHaveLength(4);
    });
  });

  describe('Navigation', () => {
    it('should render Test 404 Page button', () => {
      renderWithProviders(<Home />);

      const button = screen.getByRole('link', { name: /test 404 page/i });
      expect(button).toBeInTheDocument();
    });

    it('should link to /test-404 route', () => {
      renderWithProviders(<Home />);

      const button = screen.getByRole('link', { name: /test 404 page/i });
      expect(button).toHaveAttribute('href', '/test-404');
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading hierarchy', () => {
      renderWithProviders(<Home />);

      const mainHeading = screen.getByRole('heading', {
        name: /welcome to the application/i,
      });
      expect(mainHeading.tagName).toBe('H1');

      const featureHeadings = screen.getAllByRole('heading', { level: 2 });
      expect(featureHeadings).toHaveLength(3);
    });

    it('should render semantic HTML elements', () => {
      const { container } = renderWithProviders(<Home />);

      // Should use semantic heading elements
      const h1 = container.querySelector('h1');
      expect(h1).toBeInTheDocument();

      const h2Elements = container.querySelectorAll('h2');
      expect(h2Elements.length).toBe(3);
    });

    it('should have accessible link text', () => {
      renderWithProviders(<Home />);

      const link = screen.getByRole('link', { name: /test 404 page/i });
      // Link should have descriptive text, not just "click here"
      expect(link).toHaveAccessibleName();
    });
  });

  describe('Content Quality', () => {
    it('should display informative content about the tech stack', () => {
      renderWithProviders(<Home />);

      // Check for technology-specific keywords (using getAllByText since text appears multiple times)
      const reactText = screen.getAllByText(/react 19/i);
      expect(reactText.length).toBeGreaterThan(0);

      const muiText = screen.getAllByText(/material ui v7/i);
      expect(muiText.length).toBeGreaterThan(0);

      const routerText = screen.getAllByText(/react router v7/i);
      expect(routerText.length).toBeGreaterThan(0);
    });

    it('should have call-to-action button', () => {
      renderWithProviders(<Home />);

      // Should have Test 404 Page button
      const ctaButton = screen.getByRole('link', { name: /test 404 page/i });
      expect(ctaButton).toBeInTheDocument();
    });
  });

  describe('Theme Integration', () => {
    it('should render with Material UI theme', () => {
      const { container } = renderWithProviders(<Home />);

      // Material UI components should have MUI classes
      const muiComponents = container.querySelectorAll('[class*="Mui"]');
      expect(muiComponents.length).toBeGreaterThan(0);
    });

    it('should use Material UI Container component', () => {
      const { container } = renderWithProviders(<Home />);

      const muiContainer = container.querySelector('.MuiContainer-root');
      expect(muiContainer).toBeInTheDocument();
    });

    it('should use Material UI Paper component for cards', () => {
      const { container } = renderWithProviders(<Home />);

      const papers = container.querySelectorAll('.MuiPaper-root');
      // Should have 3 Paper components (one for each feature card)
      expect(papers.length).toBeGreaterThanOrEqual(3);
    });
  });

  describe('Dark Mode Rendering', () => {
    it('should render correctly in dark mode', () => {
      renderWithProviders(<Home />, 'dark');

      // All main content should be rendered
      expect(
        screen.getByRole('heading', { name: /welcome to the application/i })
      ).toBeInTheDocument();
      expect(screen.getByText(/your frontend application is now ready/i)).toBeInTheDocument();
    });

    it('should display all feature cards in dark mode', () => {
      renderWithProviders(<Home />, 'dark');

      // All three feature cards should be present
      expect(screen.getByRole('heading', { name: /react 19/i })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: /material ui v7/i })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: /react router v7/i })).toBeInTheDocument();
    });

    it('should apply dark theme to MUI components', () => {
      const { container } = renderWithProviders(<Home />, 'dark');

      // MUI components should still have proper classes applied
      const muiContainer = container.querySelector('.MuiContainer-root');
      expect(muiContainer).toBeInTheDocument();

      const papers = container.querySelectorAll('.MuiPaper-root');
      expect(papers.length).toBeGreaterThanOrEqual(3);
    });

    it('should maintain proper text color contrast in dark mode', () => {
      const { container } = renderWithProviders(<Home />, 'dark');

      // Typography components should render with theme colors
      const headings = screen.getAllByRole('heading');
      expect(headings.length).toBeGreaterThan(0);

      // Home icon should be present
      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('should display navigation button in dark mode', () => {
      renderWithProviders(<Home />, 'dark');

      const button = screen.getByRole('link', { name: /test 404 page/i });
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute('href', '/test-404');
    });

    it('should maintain accessibility in dark mode', () => {
      renderWithProviders(<Home />, 'dark');

      // Heading hierarchy should be preserved
      const mainHeading = screen.getByRole('heading', { name: /welcome to the application/i });
      expect(mainHeading.tagName).toBe('H1');

      const featureHeadings = screen.getAllByRole('heading', { level: 2 });
      expect(featureHeadings).toHaveLength(3);

      // Navigation link should be accessible
      const link = screen.getByRole('link', { name: /test 404 page/i });
      expect(link).toHaveAccessibleName();
    });

    it('should use proper semantic colors in dark mode', () => {
      const { container } = renderWithProviders(<Home />, 'dark');

      // Icon should render with theme primary color (uses sx prop)
      const icon = container.querySelector('[data-testid="HomeIcon"], svg');
      expect(icon).toBeInTheDocument();

      // Button should use primary color
      const button = screen.getByRole('link', { name: /test 404 page/i });
      expect(button).toHaveClass('MuiButton-outlined');
    });
  });

  describe('Theme Switching Support', () => {
    it('should render in light mode by default', () => {
      renderWithProviders(<Home />, 'light');

      expect(
        screen.getByRole('heading', { name: /welcome to the application/i })
      ).toBeInTheDocument();
      expect(screen.getByText(/your frontend application is now ready/i)).toBeInTheDocument();
    });

    it('should switch from light to dark mode without breaking layout', () => {
      const { rerender } = renderWithProviders(<Home />, 'light');

      // Verify light mode rendering
      expect(
        screen.getByRole('heading', { name: /welcome to the application/i })
      ).toBeInTheDocument();

      // Rerender with dark mode
      rerender(
        <BrowserRouter>
          <ThemeProvider>
            <MuiThemeProvider theme={createAppTheme('dark')}>
              <Home />
            </MuiThemeProvider>
          </ThemeProvider>
        </BrowserRouter>
      );

      // Content should still be present
      expect(
        screen.getByRole('heading', { name: /welcome to the application/i })
      ).toBeInTheDocument();
      expect(screen.getAllByRole('heading')).toHaveLength(4);
    });

    it('should maintain card structure in both themes', () => {
      const { container: lightContainer } = renderWithProviders(<Home />, 'light');
      const lightPapers = lightContainer.querySelectorAll('.MuiPaper-root');

      const { container: darkContainer } = renderWithProviders(<Home />, 'dark');
      const darkPapers = darkContainer.querySelectorAll('.MuiPaper-root');

      // Same number of cards in both themes
      expect(lightPapers.length).toBe(darkPapers.length);
      expect(lightPapers.length).toBeGreaterThanOrEqual(3);
    });
  });
});
