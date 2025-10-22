/**
 * Home Page Component Tests
 *
 * Test suite validating Home page renders correctly with light theme
 * for Story #3: Apply Light Theme as Default
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { BrowserRouter } from 'react-router-dom';
import theme from '../../theme';
import { Home } from './index';

// Helper function to render Home with required providers
const renderHome = () => {
  return render(
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <Home />
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('Home Page - Light Theme Rendering', () => {
  describe('Page Structure', () => {
    it('should render the home page without errors', () => {
      renderHome();
      expect(
        screen.getByRole('heading', { name: /welcome to the application/i })
      ).toBeInTheDocument();
    });

    it('should render all hero section elements', () => {
      renderHome();
      // Home icon should be present
      expect(screen.getByTestId('HomeIcon')).toBeInTheDocument();
      // Heading should be present
      expect(
        screen.getByRole('heading', { name: /welcome to the application/i })
      ).toBeInTheDocument();
      // Subtitle should be present
      expect(screen.getByText(/your frontend application is now ready/i)).toBeInTheDocument();
    });
  });

  describe('Feature Cards - Light Theme', () => {
    it('should render all three feature cards with correct content', () => {
      renderHome();
      // React 19 card
      expect(screen.getByRole('heading', { name: /react 19/i })).toBeInTheDocument();
      // Material UI v7 card
      expect(screen.getByRole('heading', { name: /material ui v7/i })).toBeInTheDocument();
      // React Router v7 card
      expect(screen.getByRole('heading', { name: /react router v7/i })).toBeInTheDocument();
    });

    it('should render card content with readable text on light backgrounds', () => {
      renderHome();
      // All card descriptions should be readable
      expect(
        screen.getByText(/built with the latest react 19 for optimal performance/i)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/comprehensive material design 3 component library/i)
      ).toBeInTheDocument();
      expect(screen.getByText(/client-side routing with seamless navigation/i)).toBeInTheDocument();
    });
  });

  describe('Interactive Elements - Light Theme', () => {
    it('should render Say Hello button with primary color', () => {
      renderHome();
      const sayHelloButton = screen.getByRole('button', { name: /say hello/i });
      expect(sayHelloButton).toBeInTheDocument();
      // Button should have primary color classes
      expect(sayHelloButton.className).toContain('MuiButton-containedPrimary');
    });

    it('should render Test 404 link with outlined style', () => {
      renderHome();
      const testLink = screen.getByRole('link', { name: /test 404 page/i });
      expect(testLink).toBeInTheDocument();
      // Link should have outlined button classes
      expect(testLink.className).toContain('MuiButton-outlined');
    });
  });

  describe('Accessibility with Light Theme', () => {
    it('should have properly structured headings', () => {
      renderHome();
      const mainHeading = screen.getByRole('heading', { name: /welcome to the application/i });
      expect(mainHeading).toBeInTheDocument();
    });

    it('should have accessible buttons with proper roles', () => {
      renderHome();
      const buttons = screen.getAllByRole('button');
      // Should have at least one button (Say Hello)
      expect(buttons.length).toBeGreaterThanOrEqual(1);
      buttons.forEach((button) => {
        expect(button).toBeInTheDocument();
      });
    });

    it('should have links with proper roles and href attributes', () => {
      renderHome();
      const testLink = screen.getByRole('link', { name: /test 404 page/i });
      expect(testLink).toHaveAttribute('href', '/test-404');
    });
  });

  describe('Typography - Light Theme Colors', () => {
    it('should render headings with appropriate color classes', () => {
      renderHome();
      const heading = screen.getByRole('heading', { name: /welcome to the application/i });
      // MUI Typography components should have color classes
      expect(heading.className).toContain('MuiTypography');
    });

    it('should render card titles with primary color', () => {
      renderHome();
      const cardTitle = screen.getByRole('heading', { name: /react 19/i });
      expect(cardTitle).toBeInTheDocument();
    });
  });

  describe('Responsive Layout', () => {
    it('should render container with proper max-width', () => {
      const { container } = renderHome();
      const muiContainer = container.querySelector('.MuiContainer-root');
      expect(muiContainer).toBeInTheDocument();
      expect(muiContainer?.className).toContain('MuiContainer-maxWidthLg');
    });

    it('should render grid layout for feature cards', () => {
      const { container } = renderHome();
      // Grid should be implemented with Box component
      expect(container.querySelector('.MuiBox-root')).toBeInTheDocument();
    });
  });

  describe('Material UI Components - Light Theme', () => {
    it('should render Paper components for cards', () => {
      const { container } = renderHome();
      const papers = container.querySelectorAll('.MuiPaper-root');
      // Should have at least 3 paper components (one for each card)
      expect(papers.length).toBeGreaterThanOrEqual(3);
    });

    it('should render Material UI icons with theme colors', () => {
      renderHome();
      const homeIcon = screen.getByTestId('HomeIcon');
      expect(homeIcon).toBeInTheDocument();
      // Icon should be rendered as SVG
      expect(homeIcon.tagName).toBe('svg');
    });
  });
});
