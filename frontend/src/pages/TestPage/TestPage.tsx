/**
 * API Test Page Component
 *
 * Test page for verifying backend connectivity and API responses.
 * Implements the design specifications from design-brief.md with full accessibility support.
 */

import { useState } from 'react';
import {
  Container,
  Card,
  CardHeader,
  CardContent,
  Stack,
  Button,
  Alert,
  Paper,
  Typography,
  Box,
  CircularProgress,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { apiService, ApiError } from '@/services/api';
import type { HealthCheckResponse } from '@/types';

/**
 * State type for the API test page
 */
type TestState = 'initial' | 'loading' | 'success' | 'error';

function TestPage() {
  const [state, setState] = useState<TestState>('initial');
  const [responseData, setResponseData] = useState<HealthCheckResponse | null>(null);
  const [timestamp, setTimestamp] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');

  /**
   * Handles the test button click
   * Calls the backend health check endpoint via the API service
   */
  const handleTestConnection = async () => {
    // Clear previous results
    setResponseData(null);
    setErrorMessage('');

    // Set loading state
    setState('loading');

    try {
      // Call backend health check API
      const response = await apiService.getHealth();

      // Set success state with actual backend response
      setState('success');
      setResponseData(response.data);
      setTimestamp(new Date().toLocaleString());
    } catch (error) {
      // Set error state
      setState('error');

      // Extract error message
      if (error instanceof ApiError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage('Failed to connect to backend. Please check if the server is running.');
      }
    }
  };

  return (
    <Container
      maxWidth="md"
      sx={{
        py: { xs: 2, sm: 4 },
      }}
    >
      <Card elevation={2}>
        <CardHeader
          title="API Test Page"
          subheader="Test backend connectivity and API responses"
          titleTypographyProps={{
            variant: 'h5',
            component: 'h1',
          }}
          subheaderTypographyProps={{
            variant: 'body2',
          }}
        />
        <CardContent>
          <Stack spacing={3}>
            {/* Button and Alert Section */}
            <Stack spacing={2} alignItems="flex-start">
              {/* Test Button */}
              <Button
                variant="contained"
                color="primary"
                size="large"
                startIcon={
                  state === 'loading' ? (
                    <CircularProgress size={24} color="inherit" />
                  ) : (
                    <SendIcon />
                  )
                }
                onClick={handleTestConnection}
                disabled={state === 'loading'}
                aria-label="Test backend API connection"
                aria-busy={state === 'loading'}
                sx={{
                  width: { xs: '100%', sm: 'auto' },
                }}
              >
                Test Backend Connection
              </Button>

              {/* Success Alert */}
              {state === 'success' && (
                <Alert severity="success" variant="filled" role="alert" sx={{ width: '100%' }}>
                  Connection successful! Response received from backend.
                </Alert>
              )}

              {/* Error Alert */}
              {state === 'error' && (
                <Alert severity="error" variant="filled" role="alert" sx={{ width: '100%' }}>
                  {errorMessage}
                </Alert>
              )}
            </Stack>

            {/* Response Display Section */}
            {state === 'success' && responseData && (
              <Paper
                component="section"
                aria-live="polite"
                elevation={1}
                sx={{
                  p: 3,
                  border: 1,
                  borderColor: 'divider',
                }}
              >
                <Typography variant="h6" component="h2" sx={{ mb: 2 }}>
                  Response Data
                </Typography>

                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ display: 'block', mb: 1 }}
                >
                  Received at: {timestamp}
                </Typography>

                <Box
                  component="pre"
                  sx={{
                    fontFamily: '"Courier New", monospace',
                    fontSize: '14px',
                    backgroundColor: 'background.default',
                    p: 2,
                    borderRadius: 1,
                    maxHeight: '400px',
                    overflowY: 'auto',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    margin: 0,
                  }}
                >
                  <Typography component="code" variant="body2">
                    {JSON.stringify(responseData, null, 2)}
                  </Typography>
                </Box>
              </Paper>
            )}
          </Stack>
        </CardContent>
      </Card>
    </Container>
  );
}

export default TestPage;
