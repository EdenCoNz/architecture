/**
 * Unit Tests for Home Page Component
 *
 * Tests the Home page component rendering, content display, and navigation.
 * Following TDD best practices with user-centric testing approach.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import theme from '../../src/theme';
import Home from '../../src/pages/Home/Home';

/**
 * Helper function to render components with all required providers
 * Home component requires both Router and Theme providers
 */
const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <ThemeProvider theme={theme}>{component}</ThemeProvider>
    </BrowserRouter>
  );
};

describe('Home Page', () => {
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

  describe('Component Import Validation', () => {
    /**
     * Regression test for GitHub Issue #30
     * Validates that the Home component renders without TypeScript compilation errors
     * and properly uses Material UI components with correct JSX tag matching.
     *
     * This test prevents:
     * - JSX tag mismatches (e.g., <Containeeeeer> vs </Container>)
     * - Incorrect component imports
     * - TypeScript compilation failures in CI/CD
     */
    it('should render successfully without TypeScript errors', () => {
      // This test will fail at compile time if there are TypeScript errors
      // such as JSX tag mismatches or incorrect imports
      expect(() => renderWithProviders(<Home />)).not.toThrow();

      // Verify component rendered
      const heading = screen.getByRole('heading', {
        name: /welcome to the application/i,
      });
      expect(heading).toBeInTheDocument();
    });

    it('should properly import and use Container component from Material UI', () => {
      const { container } = renderWithProviders(<Home />);

      // Verify Container component is correctly imported and rendered
      const muiContainer = container.querySelector('.MuiContainer-root');
      expect(muiContainer).toBeInTheDocument();

      // Verify Container has correct props applied (maxWidth="lg")
      expect(muiContainer).toHaveClass('MuiContainer-maxWidthLg');
    });

    it('should have all Material UI components correctly imported and rendered', () => {
      const { container } = renderWithProviders(<Home />);

      // Verify Container component (main layout container)
      const containerComponent = container.querySelector('.MuiContainer-root');
      expect(containerComponent).toBeInTheDocument();

      // Verify Box components (layout components)
      const boxComponents = container.querySelectorAll('.MuiBox-root');
      expect(boxComponents.length).toBeGreaterThan(0);

      // Verify Typography components (text elements)
      const typographyComponents = container.querySelectorAll('.MuiTypography-root');
      expect(typographyComponents.length).toBeGreaterThan(0);

      // Verify Paper components (feature cards)
      const paperComponents = container.querySelectorAll('.MuiPaper-root');
      expect(paperComponents.length).toBe(3); // Three feature cards

      // Verify Button component (CTA button)
      const buttonComponent = container.querySelector('.MuiButton-root');
      expect(buttonComponent).toBeInTheDocument();

      // Verify Icon component (HomeIcon)
      const iconComponent = container.querySelector('.MuiSvgIcon-root');
      expect(iconComponent).toBeInTheDocument();
    });

    it('should have matching JSX opening and closing tags', () => {
      // This test ensures TypeScript compilation succeeds
      // Any JSX tag mismatch would cause a compilation error before tests run
      const { container } = renderWithProviders(<Home />);

      // If we reach this point, TypeScript compilation was successful
      // meaning all JSX tags are properly matched
      expect(container).toBeTruthy();

      // Additional verification that the component structure is intact
      const muiContainer = container.querySelector('.MuiContainer-root');
      expect(muiContainer).toBeInTheDocument();

      // Verify the entire component tree rendered correctly
      const allMuiComponents = container.querySelectorAll('[class*="Mui"]');
      expect(allMuiComponents.length).toBeGreaterThan(0);
    });
  });
});
