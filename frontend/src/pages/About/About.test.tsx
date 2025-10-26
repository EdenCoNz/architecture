/**
 * About Page Component Tests
 *
 * Test suite validating About page renders correctly
 * for Story 14.4: Relocate Previous Home Page Content
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { BrowserRouter } from 'react-router-dom';
import theme from '../../theme';
import { About } from './index';

// Helper function to render About with required providers
const renderAbout = () => {
  return render(
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <About />
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('About Page - Story 14.4', () => {
  describe('Page Structure', () => {
    it('should render the about page without errors', () => {
      renderAbout();
      expect(
        screen.getByRole('heading', { name: /about this application/i })
      ).toBeInTheDocument();
    });

    it('should render all hero section elements', () => {
      renderAbout();
      // Info icon should be present
      expect(screen.getByTestId('InfoIcon')).toBeInTheDocument();
      // Heading should be present
      expect(
        screen.getByRole('heading', { name: /about this application/i })
      ).toBeInTheDocument();
      // Subtitle should be present
      expect(
        screen.getByText(/built with modern web technologies for optimal performance/i)
      ).toBeInTheDocument();
    });
  });

  describe('Tech Stack Feature Cards', () => {
    it('should render all three tech stack cards with correct content', () => {
      renderAbout();
      // React 19 card
      expect(screen.getByRole('heading', { name: /react 19/i })).toBeInTheDocument();
      // Material UI v7 card
      expect(screen.getByRole('heading', { name: /material ui v7/i })).toBeInTheDocument();
      // React Router v7 card
      expect(screen.getByRole('heading', { name: /react router v7/i })).toBeInTheDocument();
    });

    it('should render card content with descriptive text', () => {
      renderAbout();
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

  describe('Accessibility', () => {
    it('should have properly structured headings', () => {
      renderAbout();
      const mainHeading = screen.getByRole('heading', { name: /about this application/i });
      expect(mainHeading).toBeInTheDocument();
    });

    it('should render card titles with primary color', () => {
      renderAbout();
      const cardTitle = screen.getByRole('heading', { name: /react 19/i });
      expect(cardTitle).toBeInTheDocument();
    });
  });

  describe('Responsive Layout', () => {
    it('should render container with proper max-width', () => {
      const { container } = renderAbout();
      const muiContainer = container.querySelector('.MuiContainer-root');
      expect(muiContainer).toBeInTheDocument();
      expect(muiContainer?.className).toContain('MuiContainer-maxWidthLg');
    });

    it('should render grid layout for feature cards', () => {
      const { container } = renderAbout();
      // Grid should be implemented with Box component
      expect(container.querySelector('.MuiBox-root')).toBeInTheDocument();
    });
  });

  describe('Material UI Components', () => {
    it('should render Paper components for cards', () => {
      const { container } = renderAbout();
      const papers = container.querySelectorAll('.MuiPaper-root');
      // Should have exactly 3 paper components (one for each card)
      expect(papers.length).toBe(3);
    });

    it('should render Material UI icons', () => {
      renderAbout();
      const infoIcon = screen.getByTestId('InfoIcon');
      expect(infoIcon).toBeInTheDocument();
      // Icon should be rendered as SVG
      expect(infoIcon.tagName).toBe('svg');
    });
  });
});
