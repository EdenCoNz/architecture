/**
 * Root App Component
 *
 * Main application shell providing theme, layout structure, routing, and global providers.
 * Implements Material UI best practices with proper accessibility support.
 */

import { Box } from '@mui/material';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts';
import { Header } from './components/layout';
import { NotFound, ApiTest, Onboarding, About } from './pages';
import './styles/global.css';

function App() {
  return (
    <ThemeProvider>
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
              {/* Onboarding route as default - Feature #14 Story 14.1 */}
              <Route path="/" element={<Onboarding />} />

              {/* About route - Feature #14 Story 14.4 */}
              <Route path="/about" element={<About />} />

              {/* API Test route - Feature #10 */}
              <Route path="/api-test" element={<ApiTest />} />

              {/* Legacy onboarding route redirect - Feature #14 Story 14.2 */}
              <Route path="/onboarding" element={<Navigate to="/" replace />} />

              {/* 404 Not Found route - catches all unmatched routes */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Box>
        </Box>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
