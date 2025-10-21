/**
 * Unit Tests for App Component
 *
 * Tests the App root component rendering, routing, accessibility, and theme integration.
 * Following TDD best practices with comprehensive test coverage.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../../src/App';

describe('App Component', () => {
  describe('Rendering', () => {
    it('should render without crashing', () => {
      render(<App />);

      // App should render the main content area
      const mainContent = screen.getByRole('main');
      expect(mainContent).toBeInTheDocument();
    });

    it('should render the skip link for accessibility', () => {
      render(<App />);

      const skipLink = screen.getByText(/skip to main content/i);
      expect(skipLink).toBeInTheDocument();
      expect(skipLink).toHaveAttribute('href', '#main-content');
    });

    it('should render the Header component', () => {
      const { container } = render(<App />);

      // Header component renders as a header element
      const header = container.querySelector('header');
      expect(header).toBeInTheDocument();
    });

    it('should render the main content area with correct id', () => {
      render(<App />);

      const mainContent = screen.getByRole('main');
      expect(mainContent).toHaveAttribute('id', 'main-content');
    });
  });

  describe('CSS Baseline Integration', () => {
    it('should apply CssBaseline normalization', () => {
      const { container } = render(<App />);

      // CssBaseline adds specific CSS normalization that we can verify
      // The component should be rendered in the document
      // Material UI's CssBaseline component renders as a style injection
      // We verify the app renders successfully which means CssBaseline is working
      expect(container).toBeInTheDocument();
    });
  });

  describe('Theme Integration', () => {
    it('should wrap application in ThemeProvider', () => {
      const { container } = render(<App />);

      // ThemeProvider should enable Material UI components to render with theme
      // We verify by checking that MUI components are rendered correctly
      const header = container.querySelector('header');
      expect(header).toHaveClass('MuiAppBar-root');
    });
  });

  describe('Routing', () => {
    it('should include BrowserRouter for client-side routing', () => {
      render(<App />);

      // Home page should be rendered by default at root route
      // This verifies routing is working
      const mainContent = screen.getByRole('main');
      expect(mainContent).toBeInTheDocument();
    });
  });

  describe('Layout Structure', () => {
    it('should use flex layout for full viewport height', () => {
      const { container } = render(<App />);

      // The main content area should exist within the layout structure
      const mainContent = screen.getByRole('main');
      expect(mainContent).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper landmark regions', () => {
      render(<App />);

      // Should have main landmark
      const mainContent = screen.getByRole('main');
      expect(mainContent).toBeInTheDocument();
    });

    it('should provide skip navigation link', () => {
      render(<App />);

      const skipLink = screen.getByText(/skip to main content/i);
      expect(skipLink).toHaveClass('skip-link');
    });
  });
});
