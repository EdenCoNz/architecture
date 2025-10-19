/**
 * Header Component
 *
 * Top application bar providing branding, navigation, and global actions.
 * Implements responsive design with mobile-first approach.
 * Includes theme toggle for light/dark mode switching.
 */

import { AppBar, Toolbar, Typography, IconButton, Box } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { ThemeToggle } from '../theme';

interface HeaderProps {
  onMenuClick?: () => void;
}

export const Header = ({ onMenuClick }: HeaderProps) => {
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

        {/* Global actions: Theme toggle, etc. */}
        <Box sx={{ display: 'flex', gap: 1 }}>
          <ThemeToggle edge="end" />
          {/* Future: User menu, notifications, etc. */}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
