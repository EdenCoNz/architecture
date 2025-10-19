/**
 * Theme Switching Integration Tests
 *
 * Comprehensive test suite for verifying theme switching works correctly
 * across all pages and components in the application.
 *
 * Test Coverage:
 * - All pages render in both light and dark modes
 * - Theme toggle functionality works across all pages
 * - Theme transitions are smooth without visual glitches
 * - All MUI components display correctly in both themes
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '../test-utils';
import App from '../../App';

describe('Theme Switching Integration Tests', () => {
  describe('Home Page Theme Switching', () => {
    beforeEach(() => {
      window.history.pushState({}, '', '/');
    });

    it('should render home page correctly in light mode', async () => {
      render(<App />, {
        preloadedState: {
          theme: { mode: 'light' },
        },
      });

      // Wait for page to load and theme to initialize
      await waitFor(() => {
        expect(screen.getByText('Welcome to the Application')).toBeInTheDocument();
      });

      // Verify page content
      expect(screen.getByText('React 19')).toBeInTheDocument();
      expect(screen.getByText('Material UI v7')).toBeInTheDocument();
      expect(screen.getByText('React Router v7')).toBeInTheDocument();

      // Verify navigation links (styled as buttons)
      expect(screen.getByRole('link', { name: 'API Test Page' })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: 'Test 404 Page' })).toBeInTheDocument();

      // Verify theme toggle shows dark mode icon (action to switch TO dark)
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /switch to dark mode/i })).toBeInTheDocument();
      });
    });

    it('should render home page correctly in dark mode', async () => {
      render(<App />, {
        preloadedState: {
          theme: { mode: 'dark' },
        },
      });

      // Wait for page to load
      await waitFor(() => {
        expect(screen.getByText('Welcome to the Application')).toBeInTheDocument();
      });

      // Verify page content exists in dark mode
      expect(screen.getByText('React 19')).toBeInTheDocument();

      // Verify theme toggle shows light mode icon (action to switch TO light)
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /switch to light mode/i })).toBeInTheDocument();
      });
    });

    it('should toggle theme on home page', async () => {
      const user = userEvent.setup();
      const { store } = render(<App />, {
        preloadedState: {
          theme: { mode: 'light' },
        },
      });

      // Verify initial state
      expect((store.getState() as { theme: { mode: string } }).theme.mode).toBe('light');

      // Click theme toggle
      const toggleButton = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(toggleButton);

      // Verify theme changed
      expect((store.getState() as { theme: { mode: string } }).theme.mode).toBe('dark');

      // Verify button label updated
      expect(screen.getByRole('button', { name: /switch to light mode/i })).toBeInTheDocument();
    });

    it('should maintain theme when navigating to other pages', async () => {
      const user = userEvent.setup();
      const { store } = render(<App />, {
        preloadedState: {
          theme: { mode: 'dark' },
        },
      });

      // Verify dark mode
      expect((store.getState() as { theme: { mode: string } }).theme.mode).toBe('dark');

      // Navigate to test page
      const testPageLink = screen.getByRole('link', { name: 'API Test Page' });
      await user.click(testPageLink);

      // Wait for navigation
      await waitFor(() => {
        expect(screen.getByText('API Test Page')).toBeInTheDocument();
      });

      // Verify theme persisted
      expect((store.getState() as { theme: { mode: string } }).theme.mode).toBe('dark');
      expect(screen.getByRole('button', { name: /switch to light mode/i })).toBeInTheDocument();
    });

    it('should render all MUI components correctly on home page in both modes', () => {
      // Test light mode
      const { unmount: unmount1 } = render(<App />, {
        preloadedState: { theme: { mode: 'light' } },
      });

      // Verify Typography components
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
      expect(screen.getByRole('heading', { level: 2, name: 'React 19' })).toBeInTheDocument();

      // Verify Button components
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);

      unmount1();

      // Test dark mode
      render(<App />, {
        preloadedState: { theme: { mode: 'dark' } },
      });

      // Verify same components exist in dark mode
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
      expect(screen.getByRole('heading', { level: 2, name: 'React 19' })).toBeInTheDocument();
      expect(screen.getAllByRole('button').length).toBeGreaterThan(0);
    });
  });

  describe('Test Page Theme Switching', () => {
    beforeEach(() => {
      window.history.pushState({}, '', '/test');
    });

    it('should render test page correctly in light mode', () => {
      render(<App />, {
        preloadedState: {
          theme: { mode: 'light' },
        },
      });

      // Verify page content
      expect(screen.getByText('API Test Page')).toBeInTheDocument();
      expect(screen.getByText('Test backend connectivity and API responses')).toBeInTheDocument();

      // Verify button
      expect(
        screen.getByRole('button', { name: /test backend api connection/i })
      ).toBeInTheDocument();

      // Verify theme toggle
      expect(screen.getByRole('button', { name: /switch to dark mode/i })).toBeInTheDocument();
    });

    it('should render test page correctly in dark mode', () => {
      render(<App />, {
        preloadedState: {
          theme: { mode: 'dark' },
        },
      });

      // Verify page content exists
      expect(screen.getByText('API Test Page')).toBeInTheDocument();

      // Verify theme toggle shows light mode option
      expect(screen.getByRole('button', { name: /switch to light mode/i })).toBeInTheDocument();
    });

    it('should toggle theme on test page', async () => {
      const user = userEvent.setup();
      const { store } = render(<App />, {
        preloadedState: {
          theme: { mode: 'light' },
        },
      });

      // Click theme toggle
      const toggleButton = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(toggleButton);

      // Verify theme changed
      expect((store.getState() as { theme: { mode: string } }).theme.mode).toBe('dark');
    });

    it('should render Card component correctly in both modes', () => {
      // Light mode
      const { unmount: unmount1 } = render(<App />, {
        preloadedState: { theme: { mode: 'light' } },
      });

      // Find the card by its header content
      const cardHeader = screen.getByText('API Test Page');
      expect(cardHeader).toBeInTheDocument();

      unmount1();

      // Dark mode
      render(<App />, {
        preloadedState: { theme: { mode: 'dark' } },
      });

      // Verify card still renders in dark mode
      expect(screen.getByText('API Test Page')).toBeInTheDocument();
    });

    it('should show loading state correctly in both modes', async () => {
      const user = userEvent.setup();

      // Test in light mode
      const { unmount: unmount1 } = render(<App />, {
        preloadedState: { theme: { mode: 'light' } },
      });

      const testButton = screen.getByRole('button', { name: /test backend api connection/i });
      await user.click(testButton);

      // Button should be disabled during loading
      expect(testButton).toBeDisabled();
      expect(testButton).toHaveAttribute('aria-busy', 'true');

      unmount1();

      // Test in dark mode
      render(<App />, {
        preloadedState: { theme: { mode: 'dark' } },
      });

      const testButtonDark = screen.getByRole('button', { name: /test backend api connection/i });
      await user.click(testButtonDark);

      expect(testButtonDark).toBeDisabled();
      expect(testButtonDark).toHaveAttribute('aria-busy', 'true');
    });
  });

  describe('NotFound Page Theme Switching', () => {
    beforeEach(() => {
      window.history.pushState({}, '', '/nonexistent-route');
    });

    it('should render 404 page correctly in light mode', () => {
      render(<App />, {
        preloadedState: {
          theme: { mode: 'light' },
        },
      });

      // Verify page content
      expect(screen.getByRole('heading', { level: 1, name: '404' })).toBeInTheDocument();
      expect(screen.getByRole('heading', { level: 2, name: 'Page Not Found' })).toBeInTheDocument();

      // Verify navigation links and buttons
      expect(screen.getByRole('link', { name: 'Back to Home' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Go Back' })).toBeInTheDocument();

      // Verify theme toggle
      expect(screen.getByRole('button', { name: /switch to dark mode/i })).toBeInTheDocument();
    });

    it('should render 404 page correctly in dark mode', () => {
      render(<App />, {
        preloadedState: {
          theme: { mode: 'dark' },
        },
      });

      // Verify page content exists
      expect(screen.getByRole('heading', { level: 1, name: '404' })).toBeInTheDocument();

      // Verify theme toggle
      expect(screen.getByRole('button', { name: /switch to light mode/i })).toBeInTheDocument();
    });

    it('should toggle theme on 404 page', async () => {
      const user = userEvent.setup();
      const { store } = render(<App />, {
        preloadedState: {
          theme: { mode: 'light' },
        },
      });

      // Click theme toggle
      const toggleButton = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(toggleButton);

      // Verify theme changed
      expect((store.getState() as { theme: { mode: string } }).theme.mode).toBe('dark');
    });

    it('should render large typography correctly in both modes', () => {
      // Light mode
      const { unmount: unmount1 } = render(<App />, {
        preloadedState: { theme: { mode: 'light' } },
      });

      const heading404 = screen.getByRole('heading', { level: 1, name: '404' });
      expect(heading404).toBeInTheDocument();

      unmount1();

      // Dark mode
      render(<App />, {
        preloadedState: { theme: { mode: 'dark' } },
      });

      const heading404Dark = screen.getByRole('heading', { level: 1, name: '404' });
      expect(heading404Dark).toBeInTheDocument();
    });

    it('should render navigation buttons correctly in both modes', () => {
      // Light mode
      const { unmount: unmount1 } = render(<App />, {
        preloadedState: { theme: { mode: 'light' } },
      });

      expect(screen.getByRole('link', { name: 'Back to Home' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Go Back' })).toBeInTheDocument();

      unmount1();

      // Dark mode
      render(<App />, {
        preloadedState: { theme: { mode: 'dark' } },
      });

      expect(screen.getByRole('link', { name: 'Back to Home' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Go Back' })).toBeInTheDocument();
    });
  });

  describe('Header Component Theme Switching', () => {
    it('should render header correctly in light mode', () => {
      render(<App />, {
        preloadedState: {
          theme: { mode: 'light' },
        },
      });

      // Verify app title
      expect(screen.getByRole('heading', { level: 1, name: 'Application' })).toBeInTheDocument();

      // Verify theme toggle
      expect(screen.getByRole('button', { name: /switch to dark mode/i })).toBeInTheDocument();

      // Verify menu button exists (for mobile)
      expect(screen.getByRole('button', { name: /open navigation menu/i })).toBeInTheDocument();
    });

    it('should render header correctly in dark mode', () => {
      render(<App />, {
        preloadedState: {
          theme: { mode: 'dark' },
        },
      });

      // Verify app title
      expect(screen.getByRole('heading', { level: 1, name: 'Application' })).toBeInTheDocument();

      // Verify theme toggle shows light mode option
      expect(screen.getByRole('button', { name: /switch to light mode/i })).toBeInTheDocument();
    });

    it('should persist header across all pages with correct theme', async () => {
      const user = userEvent.setup();
      render(<App />, {
        preloadedState: {
          theme: { mode: 'dark' },
        },
      });

      // Verify header on home page
      expect(screen.getByRole('heading', { level: 1, name: 'Application' })).toBeInTheDocument();

      // Navigate to test page
      await user.click(screen.getByRole('button', { name: 'API Test Page' }));

      await waitFor(() => {
        expect(screen.getByText('API Test Page')).toBeInTheDocument();
      });

      // Verify header still present with dark theme
      expect(screen.getByRole('heading', { level: 1, name: 'Application' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /switch to light mode/i })).toBeInTheDocument();

      // Navigate to 404 page
      await user.click(screen.getByRole('button', { name: 'Test 404 Page' }));

      await waitFor(() => {
        expect(screen.getByText('Page Not Found')).toBeInTheDocument();
      });

      // Verify header still present with dark theme
      expect(screen.getByRole('heading', { level: 1, name: 'Application' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /switch to light mode/i })).toBeInTheDocument();
    });
  });

  describe('Theme Transition Smoothness', () => {
    it('should not cause layout shifts when toggling theme', async () => {
      const user = userEvent.setup();
      render(<App />);

      // Get initial link position
      const testLink = screen.getByRole('link', { name: 'API Test Page' });
      const initialRect = testLink.getBoundingClientRect();

      // Toggle theme
      const toggleButton = screen.getByRole('button', { name: /switch to/i });
      await user.click(toggleButton);

      // Wait for any transitions
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /switch to/i })).toBeInTheDocument();
      });

      // Get new link position
      const newRect = testLink.getBoundingClientRect();

      // Link position should not change (allowing for minor browser rounding)
      expect(Math.abs(initialRect.top - newRect.top)).toBeLessThan(1);
      expect(Math.abs(initialRect.left - newRect.left)).toBeLessThan(1);
    });

    it('should maintain content visibility during theme switch', async () => {
      const user = userEvent.setup();
      render(<App />);

      // Verify content is visible before toggle
      const heading = screen.getByText('Welcome to the Application');
      expect(heading).toBeVisible();

      // Toggle theme
      const toggleButton = screen.getByRole('button', { name: /switch to/i });
      await user.click(toggleButton);

      // Content should still be visible after toggle
      expect(heading).toBeVisible();
    });
  });

  describe('Rapid Theme Toggling', () => {
    it('should handle rapid theme toggling without errors', async () => {
      const user = userEvent.setup();
      const { store } = render(<App />, {
        preloadedState: {
          theme: { mode: 'light' },
        },
      });

      const toggleButton = screen.getByRole('button', { name: /switch to/i });

      // Rapid toggle multiple times
      await user.click(toggleButton);
      await user.click(toggleButton);
      await user.click(toggleButton);
      await user.click(toggleButton);
      await user.click(toggleButton);

      // Should end in dark mode (odd number of clicks)
      await waitFor(() => {
        expect((store.getState() as { theme: { mode: string } }).theme.mode).toBe('dark');
      });

      // Page should still be functional
      expect(screen.getByText('Welcome to the Application')).toBeInTheDocument();
    });

    it('should handle theme toggling while navigating', async () => {
      const user = userEvent.setup();
      render(<App />);

      // Toggle theme
      await user.click(screen.getByRole('button', { name: /switch to/i }));

      // Immediately navigate
      await user.click(screen.getByRole('link', { name: 'API Test Page' }));

      // Should successfully navigate and maintain theme
      await waitFor(() => {
        expect(screen.getByText('API Test Page')).toBeInTheDocument();
      });

      expect(screen.getByRole('button', { name: /switch to/i })).toBeInTheDocument();
    });
  });

  describe('Skip Link Accessibility', () => {
    it('should render skip link in both themes', () => {
      // Light mode
      const { container: container1, unmount: unmount1 } = render(<App />, {
        preloadedState: { theme: { mode: 'light' } },
      });

      const skipLink1 = container1.querySelector('a.skip-link');
      expect(skipLink1).toBeInTheDocument();
      expect(skipLink1).toHaveAttribute('href', '#main-content');

      unmount1();

      // Dark mode
      const { container: container2 } = render(<App />, {
        preloadedState: { theme: { mode: 'dark' } },
      });

      const skipLink2 = container2.querySelector('a.skip-link');
      expect(skipLink2).toBeInTheDocument();
      expect(skipLink2).toHaveAttribute('href', '#main-content');
    });
  });

  describe('Main Content Area', () => {
    it('should have main landmark with correct id in both themes', () => {
      // Light mode
      const { unmount: unmount1 } = render(<App />, {
        preloadedState: { theme: { mode: 'light' } },
      });

      const main1 = screen.getByRole('main');
      expect(main1).toBeInTheDocument();
      expect(main1).toHaveAttribute('id', 'main-content');

      unmount1();

      // Dark mode
      render(<App />, {
        preloadedState: { theme: { mode: 'dark' } },
      });

      const main2 = screen.getByRole('main');
      expect(main2).toBeInTheDocument();
      expect(main2).toHaveAttribute('id', 'main-content');
    });
  });

  describe('Cross-Component Consistency', () => {
    it('should apply theme consistently across all components on home page', () => {
      render(<App />, {
        preloadedState: {
          theme: { mode: 'dark' },
        },
      });

      // All components should be rendered
      expect(screen.getByRole('heading', { level: 1, name: 'Application' })).toBeInTheDocument(); // Header
      expect(screen.getByText('Welcome to the Application')).toBeInTheDocument(); // Home content
      expect(screen.getAllByRole('button').length).toBeGreaterThan(0); // Buttons
    });

    it('should apply theme consistently across all pages', async () => {
      const user = userEvent.setup();
      render(<App />, {
        preloadedState: {
          theme: { mode: 'dark' },
        },
      });

      // Home page
      expect(screen.getByRole('button', { name: /switch to light mode/i })).toBeInTheDocument();

      // Navigate to test page
      await user.click(screen.getByRole('link', { name: 'API Test Page' }));
      await waitFor(() => {
        expect(screen.getByText('API Test Page')).toBeInTheDocument();
      });
      expect(screen.getByRole('button', { name: /switch to light mode/i })).toBeInTheDocument();

      // Navigate to 404
      window.history.pushState({}, '', '/nonexistent');
      window.dispatchEvent(new PopStateEvent('popstate'));

      await waitFor(() => {
        expect(screen.getByText('Page Not Found')).toBeInTheDocument();
      });
      expect(screen.getByRole('button', { name: /switch to light mode/i })).toBeInTheDocument();
    });
  });
});
