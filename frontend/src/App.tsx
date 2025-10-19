/**
 * Root App Component
 *
 * Main application shell providing theme, layout structure, routing, and global providers.
 * Implements Material UI best practices with proper accessibility support and dynamic theming.
 */

import { Box } from '@mui/material';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store';
import { ThemeContextProvider, AppThemeProvider } from './components';
import { Header } from './components/layout';
import { Home, NotFound, TestPage } from './pages';
import './styles/global.css';

/**
 * ThemedApp - Inner app component with theme providers and routing
 */
function ThemedApp() {
  return (
    <ThemeContextProvider>
      <AppThemeProvider>
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

                {/* Test page route - API connectivity test */}
                <Route path="/test" element={<TestPage />} />

                {/* 404 Not Found route - catches all unmatched routes */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </Box>
          </Box>
        </BrowserRouter>
      </AppThemeProvider>
    </ThemeContextProvider>
  );
}

/**
 * App - Root component with Redux provider
 */
function App() {
  return (
    <Provider store={store}>
      <ThemedApp />
    </Provider>
  );
}

export default App;
