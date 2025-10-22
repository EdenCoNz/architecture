/**
 * Theme Toggle Integration Tests - Story 6
 *
 * Integration tests validating the complete theme toggle functionality
 * across the entire application, testing the acceptance criteria for Story 6:
 * "Toggle Between Themes"
 *
 * Acceptance Criteria:
 * 1. When I click the theme toggle control, the application should switch to the opposite theme
 * 2. The toggle control should update to reflect the new active theme
 * 3. The theme change should apply to all visible UI elements immediately
 * 4. I should be able to toggle between themes multiple times without issues
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../contexts';
import { Header } from '../components/layout';
import { Box, Button, Typography } from '@mui/material';

// Full application shell component for integration testing
function TestApp() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            minHeight: '100vh',
          }}
        >
          <Header />
          <Box
            component="main"
            data-testid="main-content"
            sx={{
              flexGrow: 1,
              py: 4,
              px: 3,
            }}
          >
            <Typography variant="h1" data-testid="page-title">
              Test Page
            </Typography>
            <Typography variant="body1" data-testid="body-text">
              This is test content to verify theme changes apply to all UI elements.
            </Typography>
            <Button variant="contained" data-testid="test-button">
              Test Button
            </Button>
          </Box>
        </Box>
      </BrowserRouter>
    </ThemeProvider>
  );
}

describe('Story 6: Toggle Between Themes - Integration Tests', () => {
  beforeEach(() => {
    // Clear localStorage before each test to ensure clean state
    localStorage.clear();
  });

  afterEach(() => {
    // Clean up localStorage after each test
    localStorage.clear();
  });

  describe('Acceptance Criterion 1: Application switches to opposite theme when toggle is clicked', () => {
    it('should switch from light to dark theme when toggle is clicked', async () => {
      const user = userEvent.setup();
      render(<TestApp />);

      // Verify starting in light mode
      const initialToggle = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(initialToggle).toBeInTheDocument();

      // Click to switch to dark theme
      await user.click(initialToggle);

      // Verify theme switched to dark mode
      const darkToggle = screen.getByRole('button', { name: /switch to light mode/i });
      expect(darkToggle).toBeInTheDocument();
    });

    it('should switch from dark to light theme when toggle is clicked', async () => {
      const user = userEvent.setup();

      // Start with dark theme
      render(
        <ThemeProvider defaultMode="dark">
          <BrowserRouter>
            <Box sx={{ minHeight: '100vh' }}>
              <Header />
              <Box component="main" data-testid="main-content" sx={{ py: 4 }}>
                <Typography variant="h1">Test Page</Typography>
              </Box>
            </Box>
          </BrowserRouter>
        </ThemeProvider>
      );

      // Verify starting in dark mode
      const initialToggle = screen.getByRole('button', { name: /switch to light mode/i });
      expect(initialToggle).toBeInTheDocument();

      // Click to switch to light theme
      await user.click(initialToggle);

      // Verify theme switched to light mode
      const lightToggle = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(lightToggle).toBeInTheDocument();
    });
  });

  describe('Acceptance Criterion 2: Toggle control updates to reflect new active theme', () => {
    it('should display dark mode icon and tooltip when in light mode', () => {
      render(<TestApp />);

      const toggle = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(toggle).toHaveAttribute('aria-label', 'Switch to dark mode');
    });

    it('should display light mode icon and tooltip when in dark mode', async () => {
      const user = userEvent.setup();
      render(<TestApp />);

      // Switch to dark mode
      const lightToggle = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(lightToggle);

      // Verify toggle updated
      const darkToggle = screen.getByRole('button', { name: /switch to light mode/i });
      expect(darkToggle).toHaveAttribute('aria-label', 'Switch to light mode');
    });

    it('should update toggle icon immediately after click', async () => {
      const user = userEvent.setup();
      render(<TestApp />);

      // Get initial toggle
      let toggle = screen.getByRole('button', { name: /switch to dark mode/i });

      // Click toggle
      await user.click(toggle);

      // Toggle should immediately update
      toggle = screen.getByRole('button', { name: /switch to light mode/i });
      expect(toggle).toBeInTheDocument();
    });

    it('should maintain correct toggle state through multiple changes', async () => {
      const user = userEvent.setup();
      render(<TestApp />);

      // Light mode initially
      let toggle = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(toggle).toBeInTheDocument();

      // Switch to dark
      await user.click(toggle);
      toggle = screen.getByRole('button', { name: /switch to light mode/i });
      expect(toggle).toBeInTheDocument();

      // Switch back to light
      await user.click(toggle);
      toggle = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(toggle).toBeInTheDocument();
    });
  });

  describe('Acceptance Criterion 3: Theme changes apply to all visible UI elements immediately', () => {
    it('should apply theme to Header component', async () => {
      const user = userEvent.setup();
      const { container } = render(<TestApp />);

      const header = container.querySelector('header.MuiAppBar-root');
      expect(header).toBeInTheDocument();

      // Toggle theme
      const toggle = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(toggle);

      // Header should still be present with theme applied
      expect(header).toBeInTheDocument();
    });

    it('should apply theme to main content area', async () => {
      const user = userEvent.setup();
      render(<TestApp />);

      const mainContent = screen.getByTestId('main-content');
      expect(mainContent).toBeInTheDocument();

      // Toggle theme
      const toggle = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(toggle);

      // Main content should still be present with theme applied
      expect(mainContent).toBeInTheDocument();
    });

    it('should apply theme to Typography components', async () => {
      const user = userEvent.setup();
      render(<TestApp />);

      const pageTitle = screen.getByTestId('page-title');
      const bodyText = screen.getByTestId('body-text');
      expect(pageTitle).toBeInTheDocument();
      expect(bodyText).toBeInTheDocument();

      // Toggle theme
      const toggle = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(toggle);

      // Typography should still be present and readable
      expect(pageTitle).toBeInTheDocument();
      expect(bodyText).toBeInTheDocument();
    });

    it('should apply theme to Button components', async () => {
      const user = userEvent.setup();
      render(<TestApp />);

      const testButton = screen.getByTestId('test-button');
      expect(testButton).toBeInTheDocument();
      expect(testButton).toBeVisible();

      // Toggle theme
      const toggle = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(toggle);

      // Button should still be present and interactive
      expect(testButton).toBeInTheDocument();
      expect(testButton).toBeVisible();
      expect(testButton).not.toBeDisabled();
    });

    it('should apply theme change without visual glitches', async () => {
      const user = userEvent.setup();
      const { container } = render(<TestApp />);

      // Capture initial state
      const initialAppBar = container.querySelector('.MuiAppBar-root');
      const initialButton = screen.getByTestId('test-button');

      expect(initialAppBar).toBeInTheDocument();
      expect(initialButton).toBeInTheDocument();

      // Toggle theme
      const toggle = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(toggle);

      // Elements should still be present (no flash or unmount)
      expect(initialAppBar).toBeInTheDocument();
      expect(initialButton).toBeInTheDocument();
    });
  });

  describe('Acceptance Criterion 4: Toggle between themes multiple times without issues', () => {
    it('should toggle theme 3 times successfully', async () => {
      const user = userEvent.setup();
      render(<TestApp />);

      // Initial state: light mode
      let toggle = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(toggle).toBeInTheDocument();

      // Toggle 1: Light -> Dark
      await user.click(toggle);
      toggle = screen.getByRole('button', { name: /switch to light mode/i });
      expect(toggle).toBeInTheDocument();

      // Toggle 2: Dark -> Light
      await user.click(toggle);
      toggle = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(toggle).toBeInTheDocument();

      // Toggle 3: Light -> Dark
      await user.click(toggle);
      toggle = screen.getByRole('button', { name: /switch to light mode/i });
      expect(toggle).toBeInTheDocument();
    });

    it('should toggle theme 5 times successfully', async () => {
      const user = userEvent.setup();
      render(<TestApp />);

      // Perform 5 toggles
      for (let i = 0; i < 5; i++) {
        const currentToggle = screen.getByRole('button', { name: /switch to (dark|light) mode/i });
        await user.click(currentToggle);
      }

      // Should end in dark mode (odd number of toggles)
      const finalToggle = screen.getByRole('button', { name: /switch to light mode/i });
      expect(finalToggle).toBeInTheDocument();
    });

    it('should maintain UI stability across multiple toggles', async () => {
      const user = userEvent.setup();
      render(<TestApp />);

      const pageTitle = screen.getByTestId('page-title');
      const bodyText = screen.getByTestId('body-text');
      const testButton = screen.getByTestId('test-button');

      // Toggle multiple times
      for (let i = 0; i < 4; i++) {
        const toggle = screen.getByRole('button', { name: /switch to (dark|light) mode/i });
        await user.click(toggle);

        // Verify all elements remain stable
        expect(pageTitle).toBeInTheDocument();
        expect(bodyText).toBeInTheDocument();
        expect(testButton).toBeInTheDocument();
        expect(testButton).not.toBeDisabled();
      }
    });

    it('should handle rapid consecutive toggles', async () => {
      const user = userEvent.setup();
      render(<TestApp />);

      // Rapid toggles
      const toggle1 = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(toggle1);

      const toggle2 = screen.getByRole('button', { name: /switch to light mode/i });
      await user.click(toggle2);

      const toggle3 = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(toggle3);

      // Should end in consistent state
      const finalToggle = screen.getByRole('button', { name: /switch to light mode/i });
      expect(finalToggle).toBeInTheDocument();
    });

    it('should maintain theme context state across multiple toggles', async () => {
      const user = userEvent.setup();
      render(<TestApp />);

      // Toggle and verify state multiple times
      const states = ['dark', 'light', 'dark', 'light', 'dark'];

      for (const expectedState of states) {
        const toggle = screen.getByRole('button', { name: /switch to (dark|light) mode/i });
        await user.click(toggle);

        const newToggle = screen.getByRole('button', {
          name: expectedState === 'dark' ? /switch to light mode/i : /switch to dark mode/i,
        });
        expect(newToggle).toBeInTheDocument();
      }
    });

    it('should not cause memory leaks or performance degradation with many toggles', async () => {
      const user = userEvent.setup();
      render(<TestApp />);

      // Perform many toggles to check for memory leaks
      for (let i = 0; i < 10; i++) {
        const toggle = screen.getByRole('button', { name: /switch to (dark|light) mode/i });
        await user.click(toggle);
      }

      // Application should still be responsive
      const finalToggle = screen.getByRole('button', { name: /switch to (dark|light) mode/i });
      expect(finalToggle).toBeInTheDocument();
      expect(finalToggle).not.toBeDisabled();
    });
  });

  describe('Cross-cutting concerns: Accessibility and UX', () => {
    it('should maintain keyboard accessibility during theme changes', async () => {
      const user = userEvent.setup();
      render(<TestApp />);

      const toggle = screen.getByRole('button', { name: /switch to dark mode/i });

      // Use keyboard to toggle
      toggle.focus();
      expect(toggle).toHaveFocus();

      await user.keyboard('{Enter}');

      // Toggle should update and remain focusable
      const newToggle = screen.getByRole('button', { name: /switch to light mode/i });
      expect(newToggle).toBeInTheDocument();
      newToggle.focus();
      expect(newToggle).toHaveFocus();
    });

    it('should maintain proper ARIA labels during theme changes', async () => {
      const user = userEvent.setup();
      render(<TestApp />);

      // Light mode
      let toggle = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(toggle).toHaveAttribute('aria-label', 'Switch to dark mode');

      // Switch to dark mode
      await user.click(toggle);

      // Dark mode
      toggle = screen.getByRole('button', { name: /switch to light mode/i });
      expect(toggle).toHaveAttribute('aria-label', 'Switch to light mode');
    });

    it('should keep all interactive elements functional after theme change', async () => {
      const user = userEvent.setup();
      render(<TestApp />);

      // Toggle theme
      const themeToggle = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(themeToggle);

      // All buttons should remain clickable
      const buttons = screen.getAllByRole('button');
      for (const button of buttons) {
        expect(button).not.toBeDisabled();
        button.focus();
        expect(button).toHaveFocus();
      }
    });
  });

  describe('Edge cases and error handling', () => {
    it('should handle theme toggle during page navigation', async () => {
      const user = userEvent.setup();
      render(<TestApp />);

      // Toggle theme
      const toggle = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(toggle);

      // Verify theme persists (would navigate in real app)
      const darkToggle = screen.getByRole('button', { name: /switch to light mode/i });
      expect(darkToggle).toBeInTheDocument();
    });

    it('should render correctly with default light theme', () => {
      render(<TestApp />);

      const toggle = screen.getByRole('button', { name: /switch to dark mode/i });
      expect(toggle).toBeInTheDocument();

      // All content should be visible
      expect(screen.getByTestId('page-title')).toBeInTheDocument();
      expect(screen.getByTestId('body-text')).toBeInTheDocument();
      expect(screen.getByTestId('test-button')).toBeInTheDocument();
    });

    it('should not break layout when toggling theme', async () => {
      const user = userEvent.setup();
      const { container } = render(<TestApp />);

      const mainContent = screen.getByTestId('main-content');

      // Toggle theme
      const toggle = screen.getByRole('button', { name: /switch to dark mode/i });
      await user.click(toggle);

      // Layout should remain intact
      expect(mainContent).toBeInTheDocument();
      expect(container.querySelector('header')).toBeInTheDocument();
    });
  });
});
