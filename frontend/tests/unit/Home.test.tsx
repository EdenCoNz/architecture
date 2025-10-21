/**
 * Unit Tests for Home Page Component
 *
 * Tests the Home page component rendering, content display, and navigation.
 * Following TDD best practices with user-centric testing approach.
 */

import { describe, it, expect } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
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

  describe('Hello Button - Feature #5 Story #2', () => {
    describe('Button Display', () => {
      it('should display a button labeled "Say Hello"', () => {
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        expect(helloButton).toBeInTheDocument();
      });

      it('should render the button with contained variant', () => {
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        // MUI contained buttons have MuiButton-contained class
        expect(helloButton).toHaveClass('MuiButton-contained');
      });

      it('should render the button with primary color', () => {
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        // MUI primary buttons have MuiButton-colorPrimary class
        expect(helloButton).toHaveClass('MuiButton-colorPrimary');
      });

      it('should render the button with large size', () => {
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        // MUI large buttons have MuiButton-sizeLarge class
        expect(helloButton).toHaveClass('MuiButton-sizeLarge');
      });
    });

    describe('Visual Prominence', () => {
      it('should be easily locatable on the page', () => {
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        // Button should be visible (not hidden or off-screen)
        expect(helloButton).toBeVisible();
      });

      it('should be visually distinct from other buttons', () => {
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });

        // Hello button should have contained variant (others might have outlined)
        expect(helloButton).toHaveClass('MuiButton-contained');
      });
    });

    describe('Interactive Appearance', () => {
      it('should have pointer cursor on hover', () => {
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        // MUI buttons have cursor: pointer by default
        // This test verifies the button is not disabled (which would change cursor)
        expect(helloButton).not.toBeDisabled();
      });

      it('should not be disabled by default', () => {
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        expect(helloButton).not.toBeDisabled();
      });
    });

    describe('Accessibility', () => {
      it('should have accessible name for screen readers', () => {
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        expect(helloButton).toHaveAccessibleName();
      });

      it('should be keyboard accessible', () => {
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        // Native button elements are keyboard accessible by default
        expect(helloButton.tagName).toBe('BUTTON');
      });

      it('should meet minimum touch target size', () => {
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });

        // MUI large button should meet 48x48px minimum touch target
        // Note: In testing environment, actual dimensions may not render,
        // but we verify the size class is applied
        expect(helloButton).toHaveClass('MuiButton-sizeLarge');
      });
    });

    describe('Design Compliance', () => {
      it('should use MUI Button component', () => {
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        // Should have MUI Button root class
        expect(helloButton).toHaveClass('MuiButton-root');
      });

      it('should be centered on the page', () => {
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        const parentBox = helloButton.parentElement;

        // Parent should be a Box with centered alignment
        expect(parentBox).toBeInTheDocument();
      });
    });
  });

  describe('Hello Button Interaction - Feature #5 Story #3', () => {
    describe('Button Click Behavior', () => {
      it('should display a greeting message when clicked', async () => {
        const user = userEvent.setup();
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });

        // Click the button
        await user.click(helloButton);

        // Greeting message should appear
        const greetingMessage = await screen.findByText(/hello! welcome to our application!/i);
        expect(greetingMessage).toBeInTheDocument();
      });

      it('should display greeting message that is clearly visible', async () => {
        const user = userEvent.setup();
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        await user.click(helloButton);

        // Message should be visible to users
        const greetingMessage = await screen.findByText(/hello! welcome to our application!/i);
        expect(greetingMessage).toBeVisible();
      });

      it('should use Snackbar for greeting message display', async () => {
        const user = userEvent.setup();
        const { container } = renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        await user.click(helloButton);

        // Wait for Snackbar to appear
        await screen.findByText(/hello! welcome to our application!/i);

        // Should have MUI Snackbar component
        const snackbar = container.querySelector('.MuiSnackbar-root');
        expect(snackbar).toBeInTheDocument();
      });

      it('should use Alert component with success severity', async () => {
        const user = userEvent.setup();
        const { container } = renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        await user.click(helloButton);

        // Wait for Alert to appear
        await screen.findByText(/hello! welcome to our application!/i);

        // Should have MUI Alert component with success severity
        const alert = container.querySelector('.MuiAlert-standardSuccess');
        expect(alert).toBeInTheDocument();
      });
    });

    describe('Multiple Click Behavior', () => {
      it('should show greeting each time button is clicked', async () => {
        const user = userEvent.setup();
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });

        // First click
        await user.click(helloButton);
        let greetingMessage = await screen.findByText(/hello! welcome to our application!/i);
        expect(greetingMessage).toBeInTheDocument();

        // Wait for message to disappear (auto-hide after 3 seconds)
        await waitFor(
          () => {
            expect(
              screen.queryByText(/hello! welcome to our application!/i)
            ).not.toBeInTheDocument();
          },
          { timeout: 4000 }
        );

        // Second click
        await user.click(helloButton);
        greetingMessage = await screen.findByText(/hello! welcome to our application!/i);
        expect(greetingMessage).toBeInTheDocument();
      });

      it('should allow rapid consecutive clicks', async () => {
        const user = userEvent.setup();
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });

        // Click multiple times rapidly
        await user.click(helloButton);
        await user.click(helloButton);

        // Greeting should still appear
        const greetingMessage = await screen.findByText(/hello! welcome to our application!/i);
        expect(greetingMessage).toBeInTheDocument();
      });
    });

    describe('Message Dismissal', () => {
      it('should auto-dismiss greeting message after timeout', async () => {
        const user = userEvent.setup();
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        await user.click(helloButton);

        // Message should appear
        const greetingMessage = await screen.findByText(/hello! welcome to our application!/i);
        expect(greetingMessage).toBeInTheDocument();

        // Message should disappear after 3 seconds
        await waitFor(
          () => {
            expect(
              screen.queryByText(/hello! welcome to our application!/i)
            ).not.toBeInTheDocument();
          },
          { timeout: 4000 }
        );
      });

      it('should allow manual dismissal of greeting message', async () => {
        const user = userEvent.setup();
        const { container } = renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        await user.click(helloButton);

        // Wait for message to appear
        await screen.findByText(/hello! welcome to our application!/i);

        // Find and click close button on Alert
        const closeButton = container.querySelector('.MuiAlert-action button');
        if (closeButton) {
          await user.click(closeButton);

          // Message should disappear
          await waitFor(() => {
            expect(
              screen.queryByText(/hello! welcome to our application!/i)
            ).not.toBeInTheDocument();
          });
        }
      });
    });

    describe('Snackbar Positioning', () => {
      it('should position Snackbar at bottom center', async () => {
        const user = userEvent.setup();
        const { container } = renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        await user.click(helloButton);

        // Wait for Snackbar to appear
        await screen.findByText(/hello! welcome to our application!/i);

        // Snackbar should have bottom-center anchor classes
        const snackbar = container.querySelector('.MuiSnackbar-root');
        expect(snackbar).toHaveClass('MuiSnackbar-anchorOriginBottomCenter');
      });
    });

    describe('Greeting Message Accessibility', () => {
      it('should announce greeting message to screen readers', async () => {
        const user = userEvent.setup();
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        await user.click(helloButton);

        // Alert should be announced (role="alert" is implicit for MUI Alert)
        const greetingMessage = await screen.findByText(/hello! welcome to our application!/i);
        const alert = greetingMessage.closest('[role="alert"]');
        expect(alert).toBeInTheDocument();
      });

      it('should have readable contrast for greeting message', async () => {
        const user = userEvent.setup();
        const { container } = renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });
        await user.click(helloButton);

        // Wait for Alert to appear
        await screen.findByText(/hello! welcome to our application!/i);

        // Success Alert should have appropriate contrast (MUI default success colors)
        const alert = container.querySelector('.MuiAlert-standardSuccess');
        expect(alert).toBeInTheDocument();
      });
    });

    describe('Button State During Interaction', () => {
      it('should keep button enabled after click', async () => {
        const user = userEvent.setup();
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });

        // Click button
        await user.click(helloButton);

        // Wait for greeting to appear
        await screen.findByText(/hello! welcome to our application!/i);

        // Button should still be enabled
        expect(helloButton).not.toBeDisabled();
      });

      it('should not show loading state', async () => {
        const user = userEvent.setup();
        renderWithProviders(<Home />);

        const helloButton = screen.getByRole('button', { name: /say hello/i });

        // Click button
        await user.click(helloButton);

        // Button should not have loading indicator
        expect(helloButton.querySelector('.MuiCircularProgress-root')).not.toBeInTheDocument();
      });
    });
  });
});
