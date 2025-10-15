/**
 * NotFound (404) Page Component
 *
 * Displays when user navigates to a route that doesn't exist.
 * Provides helpful navigation options to get back to the application.
 */

import { Box, Typography, Container, Button } from '@mui/material';
import { Link } from 'react-router-dom';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import HomeIcon from '@mui/icons-material/Home';

function NotFound() {
  return (
    <Container maxWidth="md">
      <Box
        sx={{
          py: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 4,
          textAlign: 'center',
        }}
      >
        {/* Error Icon */}
        <ErrorOutlineIcon
          sx={{
            fontSize: 120,
            color: 'error.main',
          }}
        />

        {/* 404 Message */}
        <Box>
          <Typography
            variant="h1"
            component="h1"
            gutterBottom
            sx={{
              fontWeight: 700,
              color: 'text.primary',
              fontSize: {
                xs: '4rem',
                sm: '6rem',
                md: '8rem',
              },
            }}
          >
            404
          </Typography>
          <Typography
            variant="h4"
            component="h2"
            gutterBottom
            sx={{
              fontWeight: 400,
              color: 'text.primary',
            }}
          >
            Page Not Found
          </Typography>
          <Typography
            variant="body1"
            color="text.secondary"
            sx={{
              mb: 4,
              maxWidth: 600,
            }}
          >
            Sorry, the page you are looking for does not exist. It might have been moved or deleted,
            or you may have mistyped the URL.
          </Typography>
        </Box>

        {/* Navigation Options */}
        <Box
          sx={{
            display: 'flex',
            gap: 2,
            flexDirection: {
              xs: 'column',
              sm: 'row',
            },
          }}
        >
          <Button
            component={Link}
            to="/"
            variant="contained"
            color="primary"
            size="large"
            startIcon={<HomeIcon />}
          >
            Back to Home
          </Button>
          <Button
            variant="outlined"
            color="primary"
            size="large"
            onClick={() => window.history.back()}
          >
            Go Back
          </Button>
        </Box>

        {/* Additional Help */}
        <Box sx={{ mt: 4 }}>
          <Typography variant="body2" color="text.secondary">
            If you believe this is an error, please contact support.
          </Typography>
        </Box>
      </Box>
    </Container>
  );
}

export default NotFound;
