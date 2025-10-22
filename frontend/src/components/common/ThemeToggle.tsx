/**
 * ThemeToggle Component
 *
 * Provides an IconButton control for switching between light and dark themes.
 * Displays theme-appropriate icons (sun/moon) and includes tooltip for discoverability.
 *
 * Design specifications from docs/design-brief.md - Feature: Theme Toggle Control
 */

import { IconButton, Tooltip } from '@mui/material';
import { LightMode, DarkMode } from '@mui/icons-material';
import type { ThemeMode } from '../../contexts/useTheme';

export interface ThemeToggleProps {
  /**
   * Current theme mode - determines which icon to display
   */
  mode: ThemeMode;

  /**
   * Callback function triggered when toggle is clicked
   */
  onToggle: () => void;
}

/**
 * ThemeToggle component displays a button to switch between light and dark themes.
 *
 * Visual behavior:
 * - Light mode: Shows sun icon (LightMode), tooltip "Switch to dark mode"
 * - Dark mode: Shows moon icon (DarkMode), tooltip "Switch to light mode"
 *
 * Accessibility:
 * - 48x48px minimum touch target (MUI IconButton default)
 * - Dynamic aria-label indicating action
 * - Keyboard accessible (Tab to focus, Enter/Space to activate)
 * - High contrast in both themes (15.8:1 light, 14.9:1 dark)
 *
 * @param props - ThemeToggleProps
 * @returns IconButton with theme-appropriate icon and tooltip
 */
export const ThemeToggle = ({ mode, onToggle }: ThemeToggleProps) => {
  const tooltipTitle = mode === 'light' ? 'Switch to dark mode' : 'Switch to light mode';
  const ariaLabel = mode === 'light' ? 'Switch to dark mode' : 'Switch to light mode';

  return (
    <Tooltip title={tooltipTitle}>
      <IconButton
        onClick={onToggle}
        color="inherit"
        aria-label={ariaLabel}
        sx={{
          transition: 'transform 300ms ease-in-out',
          '&:hover': {
            transform: 'scale(1.05)',
          },
          '&:active': {
            transform: 'rotate(180deg)',
          },
        }}
      >
        {mode === 'light' ? <DarkMode /> : <LightMode />}
      </IconButton>
    </Tooltip>
  );
};

export default ThemeToggle;
