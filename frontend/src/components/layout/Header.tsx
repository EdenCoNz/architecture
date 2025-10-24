/**
 * Header Component
 *
 * Top application bar providing branding, navigation, and global actions.
 * Implements responsive design with mobile-first approach.
 * Includes theme toggle control for switching between light and dark modes.
 */

import { AppBar, Toolbar, Typography, IconButton, Box, Button } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import WifiIcon from '@mui/icons-material/Wifi';
import { Link } from 'react-router-dom';
import { ThemeToggle } from '../common';
import { useTheme } from '../../contexts';

interface HeaderProps {
  onMenuClick?: () => void;
}

export const Header = ({ onMenuClick }: HeaderProps) => {
  const { mode, toggleTheme } = useTheme();

  return (
    <AppBar position="sticky" color="primary">
      <Toolbar>
        {/* Menu button - visible on mobile */}
        <IconButton
          edge="start"
          color="inherit"
          aria-label="open navigation menu"
          onClick={onMenuClick}
          sx={{
            mr: 2,
            display: { xs: 'block', md: 'none' },
          }}
        >
          <MenuIcon />
        </IconButton>

        {/* Application title/logo */}
        <Typography
          variant="h6"
          component="h1"
          sx={{
            flexGrow: 1,
            fontWeight: 500,
          }}
        >
          Application
        </Typography>

        {/* Global actions */}
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          {/* API Test navigation link */}
          <Button
            component={Link}
            to="/api-test"
            color="inherit"
            startIcon={<WifiIcon />}
            sx={{
              display: { xs: 'none', sm: 'flex' },
            }}
          >
            API Test
          </Button>
          <ThemeToggle mode={mode} onToggle={toggleTheme} />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
