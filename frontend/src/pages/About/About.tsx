/**
 * About Page Component
 *
 * Informational page about the application and its tech stack.
 * Contains the content that was previously on the Home page.
 * Follows Material UI design patterns with responsive layout.
 */

import { Box, Typography, Container, Paper } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';

function About() {
  return (
    <Container maxWidth="lg">
      <Box
        sx={{
          py: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 4,
        }}
      >
        {/* Hero Section */}
        <Box sx={{ textAlign: 'center' }}>
          <InfoIcon
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
            About This Application
          </Typography>
          <Typography variant="h5" component="p" color="text.secondary" sx={{ mb: 4 }}>
            Built with modern web technologies for optimal performance and user experience
          </Typography>
        </Box>

        {/* Feature Cards */}
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: {
              xs: '1fr',
              sm: 'repeat(2, 1fr)',
              md: 'repeat(3, 1fr)',
            },
            gap: 3,
            width: '100%',
          }}
        >
          <Paper
            elevation={1}
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
            }}
          >
            <Typography variant="h6" component="h2" color="primary">
              React 19
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Built with the latest React 19 for optimal performance and modern features.
            </Typography>
          </Paper>

          <Paper
            elevation={1}
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
            }}
          >
            <Typography variant="h6" component="h2" color="primary">
              Material UI v7
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Comprehensive Material Design 3 component library with excellent accessibility.
            </Typography>
          </Paper>

          <Paper
            elevation={1}
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
            }}
          >
            <Typography variant="h6" component="h2" color="primary">
              React Router v7
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Client-side routing with seamless navigation and no page reloads.
            </Typography>
          </Paper>
        </Box>
      </Box>
    </Container>
  );
}

export default About;
