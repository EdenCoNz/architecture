/**
 * Root App Component
 *
 * Main application shell providing theme, layout structure, routing, and global providers.
 * Implements Material UI best practices with proper accessibility support.
 */

import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import theme from './theme';
import { Header } from './components/layout';
import { Home, NotFound } from './pages';
import './styles/global.css';

function App() {
  return (
    <ThemeProvider theme={theme}>
      {/* CssBaseline provides consistent CSS reset across browsers */}
      <CssBaseline />

      {/* React Router for client-side routing */}
      <BrowsewwrRouteer>
        {/* Skip link for accessibility - keyboard and screen reader users */}
        <a href="#main-content" className="skip-link">
          Skip to main content!!!!
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
    </ThemeProvider>
  );
}

export default App;
