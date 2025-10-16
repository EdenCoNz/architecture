/**
 * ThemeToggle Component
 *
 * A toggle switch that allows users to switch between light and dark themes.
 * Integrates with ThemeContext to read current mode and trigger theme changes.
 *
 * Features:
 * - MUI Switch component with light/dark mode icons
 * - Integrates with ThemeContext for state management
 * - Accessible with ARIA attributes and keyboard support
 * - Visual indicators for current theme state
 *
 * Usage:
 * ```tsx
 * import ThemeToggle from './components/ThemeToggle';
 *
 * function Header() {
 *   return (
 *     <AppBar>
 *       <Toolbar>
 *         <ThemeToggle />
 *       </Toolbar>
 *     </AppBar>
 *   );
 * }
 * ```
 */

import { Switch, Box } from '@mui/material';
import { Brightness7, Brightness4 } from '@mui/icons-material';
import { useTheme } from '../../contexts/ThemeContext';

/**
 * ThemeToggle Component
 *
 * Renders a switch that toggles between light and dark themes.
 * Shows sun icon for light mode, moon icon for dark mode.
 *
 * @returns Theme toggle switch component
 */
function ThemeToggle() {
  const { mode, toggleTheme } = useTheme();

  // Switch is checked when in dark mode
  const isDarkMode = mode === 'dark';

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
      }}
    >
      {/* Light mode icon (Sun) */}
      <Brightness7
        sx={{
          color: isDarkMode ? 'action.disabled' : 'warning.main',
          fontSize: '1.25rem',
        }}
        data-testid="Brightness7Icon"
      />

      {/* Theme toggle switch */}
      <Switch
        checked={isDarkMode}
        onChange={toggleTheme}
        inputProps={{
          'aria-label': 'Toggle dark mode',
        }}
        color="default"
      />

      {/* Dark mode icon (Moon) */}
      <Brightness4
        sx={{
          color: isDarkMode ? 'warning.main' : 'action.disabled',
          fontSize: '1.25rem',
        }}
        data-testid="Brightness4Icon"
      />
    </Box>
  );
}

export default ThemeToggle;
