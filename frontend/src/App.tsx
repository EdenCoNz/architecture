/**
 * Root App Component
 *
 * Main application shell providing theme, layout structure, routing, and global providers.
 * Implements Material UI best practices with proper accessibility support.
 * Integrates ThemeContext for light/dark mode management.
 */

import { useMemo } from 'react';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { createAppTheme } from './theme';
import { ThemeProvider, useTheme } from './contexts';
import { Header } from './components/layout';
import { Home, NotFound } from './pages';
import './styles/global.css';

/**
 * AppContent Component
 *
 * Inner component that has access to theme context
 * Separated to allow useTheme hook to work correctly
 */
function AppContent() {
  const { mode } = useTheme();

  // Create theme based on current mode
  // Memoized to prevent unnecessary theme recreations
  const theme = useMemo(() => createAppTheme(mode), [mode]);

  return (
    <MuiThemeProvider theme={theme}>
      {/* CssBaseline provides consistent CSS reset across browsers */}
      <CssBaseline />

      {/* React Router for client-side routing */}
      <BrowserRouter>
        {/* Skip link for accessibility - keyboard and screen reader users */}
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>

        {/* Application Shell */}
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            minHeight: '100vh',
          }}
        >
          {/* Header with sticky positioning */}
          <Header />

          {/* Main content area with routes */}
          <Box
            component="main"
            id="main-content"
            sx={{
              flexGrow: 1,
              py: 4,
            }}
          >
            <Routes>
              {/* Home route */}
              <Route path="/" element={<Home />} />

              {/* 404 Not Found route - catches all unmatched routes */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Box>
        </Box>
      </BrowserRouter>
    </MuiThemeProvider>
  );
}

/**
 * App Component
 *
 * Root component that wraps the application with ThemeProvider
 * for theme mode state management
 */
function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;
