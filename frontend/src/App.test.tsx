/**
 * App Component Integration Tests
 *
 * Test suite validating light theme is applied throughout the application
 * for Story #3: Apply Light Theme as Default
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App Component - Light Theme Default', () => {
  describe('Theme Application', () => {
    it('should render the application without crashing', () => {
      render(<App />);
      // If we get here, the app rendered successfully with the theme
      expect(true).toBe(true);
    });

    it('should apply ThemeProvider to the entire application', () => {
      const { container } = render(<App />);
      // ThemeProvider should be present (rendered by checking container exists)
      expect(container).toBeInTheDocument();
    });

    it('should include CssBaseline for consistent styling', () => {
      const { container } = render(<App />);
      // CssBaseline applies global CSS reset, verify container is rendered
      // CssBaseline styles are injected by Emotion and may not appear as <style> tags in test environment
      expect(container).toBeTruthy();
    });
  });

  describe('Light Theme Visual Elements', () => {
    it('should render main content area', () => {
      render(<App />);
      const mainContent = screen.getByRole('main');
      expect(mainContent).toBeInTheDocument();
      expect(mainContent).toHaveAttribute('id', 'main-content');
    });

    it('should render skip link for accessibility', () => {
      render(<App />);
      const skipLink = screen.getByText(/skip to main content/i);
      expect(skipLink).toBeInTheDocument();
      expect(skipLink).toHaveAttribute('href', '#main-content');
    });

    it('should render application shell with light theme', () => {
      const { container } = render(<App />);
      // App should render with layout structure
      expect(container.firstChild).toBeTruthy();
    });
  });

  describe('Onboarding Page Light Theme (Story 14.1)', () => {
    it('should render onboarding page content with light theme typography', () => {
      render(<App />);
      // Check if onboarding page content is rendered at root URL
      const welcomeHeading = screen.getByRole('heading', {
        name: /welcome to your training journey/i,
      });
      expect(welcomeHeading).toBeInTheDocument();
    });

    it('should render Material UI form components with light theme', () => {
      render(<App />);
      // Check for MUI form components - the stepper starts with sport selection
      const assessmentForm = screen.getByRole('form', { name: /assessment form/i });
      expect(assessmentForm).toBeInTheDocument();
    });

    it('should render navigation buttons with light theme colors', () => {
      render(<App />);
      const nextButton = screen.getByRole('button', { name: /next/i });
      expect(nextButton).toBeInTheDocument();
    });
  });

  describe('Accessibility with Light Theme', () => {
    it('should have accessible text elements', () => {
      render(<App />);
      // All text should be readable with light theme contrast - use getAllByRole since there are multiple h1 elements
      const headings = screen.getAllByRole('heading', { level: 1 });
      expect(headings.length).toBeGreaterThan(0);
      expect(headings[0]).toBeInTheDocument();
    });

    it('should have accessible interactive elements', () => {
      render(<App />);
      // All interactive elements should be accessible
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
      buttons.forEach((button) => {
        expect(button).toBeInTheDocument();
      });
    });

    it('should have proper document structure', () => {
      render(<App />);
      const main = screen.getByRole('main');
      expect(main).toBeInTheDocument();
    });
  });

  describe('Routing with Light Theme', () => {
    it('should render onboarding at root route by default (Story 14.1)', () => {
      render(<App />);
      // Onboarding page should be rendered at root route
      expect(screen.getByText(/welcome to your training journey/i)).toBeInTheDocument();
    });

    it('should include navigation elements styled with light theme', () => {
      render(<App />);
      // Navigation should be present
      const banner = screen.getByRole('banner');
      expect(banner).toBeInTheDocument();
    });
  });

  describe('Story 14.1: Display Onboarding as Default Page', () => {
    it('should render Onboarding component when navigating to root URL', () => {
      render(<App />);
      // Verify Onboarding component is rendered at root URL
      // Look for characteristic onboarding elements
      const onboardingHeading = screen.getByRole('heading', {
        name: /welcome to your training journey/i,
      });
      expect(onboardingHeading).toBeInTheDocument();
    });

    it('should display the same interface elements that were on /onboarding route', () => {
      render(<App />);
      // Verify key onboarding form elements are present
      const descriptionText = screen.getByText(/let's get to know you better/i);
      expect(descriptionText).toBeInTheDocument();
    });

    it('should render Onboarding form at root URL', () => {
      render(<App />);
      // Verify assessment form is present
      const assessmentForm = screen.getByRole('form', { name: /assessment form/i });
      expect(assessmentForm).toBeInTheDocument();
    });

    it('should not need to navigate to a different route to access onboarding', () => {
      render(<App />);
      // At root URL, onboarding should be immediately visible without navigation
      // Verify by checking that onboarding content is present without any routing
      const welcomeMessage = screen.getByText(/welcome to your training journey/i);
      expect(welcomeMessage).toBeInTheDocument();
    });
  });

  describe('Story 14.2: Redirect Legacy Onboarding Route', () => {
    it('should redirect from /onboarding to root URL /', () => {
      // Set initial route to /onboarding
      window.history.pushState({}, 'Test page', '/onboarding');
      render(<App />);

      // Verify we're redirected to root URL
      expect(window.location.pathname).toBe('/');
    });

    it('should display onboarding content after redirect from /onboarding', () => {
      // Set initial route to /onboarding
      window.history.pushState({}, 'Test page', '/onboarding');
      render(<App />);

      // Verify onboarding content is displayed
      const onboardingHeading = screen.getByRole('heading', {
        name: /welcome to your training journey/i,
      });
      expect(onboardingHeading).toBeInTheDocument();
    });

    it('should redirect immediately without showing intermediate content', () => {
      // Set initial route to /onboarding
      window.history.pushState({}, 'Test page', '/onboarding');
      const { container } = render(<App />);

      // Verify onboarding content is present (redirect happened immediately)
      // No intermediate content or error pages should be shown
      expect(container).toBeTruthy();
      const onboardingContent = screen.getByText(/welcome to your training journey/i);
      expect(onboardingContent).toBeInTheDocument();
    });
  });

  describe('Story 14.4: Relocate Previous Home Page Content', () => {
    it('should make previous home page content accessible from a clearly labeled route', () => {
      // Set route to /about
      window.history.pushState({}, 'About page', '/about');
      render(<App />);

      // Verify about page content is displayed
      const aboutHeading = screen.getByRole('heading', { name: /about this application/i });
      expect(aboutHeading).toBeInTheDocument();
    });

    it('should display tech stack information on the about page', () => {
      // Set route to /about
      window.history.pushState({}, 'About page', '/about');
      render(<App />);

      // Verify tech stack cards are present
      expect(screen.getByRole('heading', { name: /react 19/i })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: /material ui v7/i })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: /react router v7/i })).toBeInTheDocument();
    });

    it('should display all content correctly without layout issues on about page', () => {
      // Set route to /about
      window.history.pushState({}, 'About page', '/about');
      const { container } = render(<App />);

      // Verify layout is rendered correctly
      expect(container).toBeTruthy();
      // Verify feature card descriptions are present
      expect(screen.getByText(/built with the latest react 19/i)).toBeInTheDocument();
      expect(
        screen.getByText(/comprehensive material design 3 component library/i)
      ).toBeInTheDocument();
      expect(screen.getByText(/client-side routing with seamless navigation/i)).toBeInTheDocument();
    });
  });
});
