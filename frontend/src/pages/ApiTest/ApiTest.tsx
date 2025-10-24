/**
 * API Connection Test Page Component
 *
 * Story-10.2: Test Page with User Interface
 * Story-10.3: API Call Functionality
 * Story-10.4: Display API Response
 * Provides a dedicated interface for testing backend connectivity.
 * Implements responsive design with clear visual hierarchy.
 * Handles API requests with loading states and error handling.
 * Displays backend response data in a user-friendly format.
 */

import { useState } from 'react';
import { Box, Typography, Container, Paper, Button, CircularProgress } from '@mui/material';
import WifiIcon from '@mui/icons-material/Wifi';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { testBackendConnection, ApiError } from '../../services';
import type { ApiTestResponse } from '../../services';

function ApiTest() {
  // State management
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<ApiTestResponse | null>(null);

  /**
   * Format ISO timestamp to user-friendly format
   * @param isoString - ISO 8601 timestamp from backend
   * @returns Formatted date and time string
   */
  const formatTimestamp = (isoString: string): string => {
    const date = new Date(isoString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
    });
  };

  /**
   * Handle test button click
   * Triggers API call to backend test endpoint
   */
  const handleTestConnection = async () => {
    // Clear previous error and response
    setError(null);
    setResponse(null);

    // Set loading state
    setIsLoading(true);

    try {
      // Call backend test endpoint
      const data = await testBackendConnection();

      // Store response data
      setResponse(data);
    } catch (err) {
      // Handle errors
      if (err instanceof ApiError) {
        setError(err.message);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      // Clear loading state
      setIsLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          py: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 4,
        }}
      >
        {/* Page Header */}
        <Box sx={{ textAlign: 'center' }}>
          <WifiIcon
            sx={{
              fontSize: 64,
              color: 'primary.main',
              mb: 2,
            }}
          />
          <Typography
            variant="h2"
            component="h1"
            gutterBottom
            sx={{
              fontWeight: 400,
              color: 'text.primary',
            }}
          >
            API Connection Test
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Test the connection between frontend and backend applications
          </Typography>
        </Box>

        {/* Test Button */}
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 2,
            width: '100%',
          }}
        >
          <Button
            variant="contained"
            color="primary"
            size="large"
            disabled={isLoading}
            onClick={handleTestConnection}
            startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : null}
            sx={{
              minWidth: { xs: 200, sm: 240 },
              py: 1.5,
            }}
          >
            {isLoading ? 'Testing Connection...' : 'Test Backend Connection'}
          </Button>
        </Box>

        {/* Results Display Area */}
        <Paper
          elevation={1}
          data-testid="test-results-area"
          aria-label="API test results display area"
          sx={{
            width: '100%',
            p: 4,
            minHeight: 200,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'background.paper',
          }}
        >
          {error ? (
            <Typography variant="body1" color="error" sx={{ textAlign: 'center' }}>
              Connection failed: {error}
            </Typography>
          ) : response ? (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 2,
                width: '100%',
              }}
            >
              {/* Success Icon and Message */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CheckCircleIcon sx={{ fontSize: 32, color: 'success.main' }} />
                <Typography variant="h6" color="success.main" sx={{ fontWeight: 500 }}>
                  Connection Successful
                </Typography>
              </Box>

              {/* Backend Message */}
              <Box
                sx={{
                  width: '100%',
                  p: 2,
                  backgroundColor: 'action.hover',
                  borderRadius: 1,
                }}
              >
                <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                  Backend Response:
                </Typography>
                <Typography variant="body1" color="text.primary">
                  {response.message}
                </Typography>
              </Box>

              {/* Timestamp */}
              <Box
                sx={{
                  width: '100%',
                  p: 2,
                  backgroundColor: 'action.hover',
                  borderRadius: 1,
                }}
              >
                <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                  Response Time:
                </Typography>
                <Typography variant="body1" color="text.primary">
                  {formatTimestamp(response.timestamp)}
                </Typography>
              </Box>
            </Box>
          ) : (
            <Typography variant="body1" color="text.secondary" sx={{ textAlign: 'center' }}>
              No test results yet. Click the button above to test the backend connection.
            </Typography>
          )}
        </Paper>

        {/* Information Section */}
        <Box
          sx={{
            width: '100%',
            mt: 2,
          }}
        >
          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
            This page allows you to manually verify that the frontend can communicate with the
            backend API.
          </Typography>
        </Box>
      </Box>
    </Container>
  );
}

export default ApiTest;
