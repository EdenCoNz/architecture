/**
 * ThemeToggle Component
 *
 * Icon button control for toggling between light and dark themes.
 * Provides visual feedback of current theme and accessible interaction.
 */

import { IconButton, Tooltip } from '@mui/material';
import { Brightness7, Brightness4 } from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '../../store';
import { toggleTheme, selectThemeMode } from '../../store/slices/themeSlice';

export interface ThemeToggleProps {
  /**
   * Optional edge positioning for IconButton
   * @default false
   */
  edge?: 'start' | 'end' | false;

  /**
   * Optional additional styling
   */
  sx?: object;
}

/**
 * ThemeToggle - Button to switch between light and dark themes
 *
 * Features:
 * - Shows current theme with appropriate icon
 * - Toggles theme on click
 * - Keyboard accessible
 * - Provides tooltip for discoverability
 * - ARIA-compliant with descriptive labels
 */
const ThemeToggle = ({ edge = false, sx }: ThemeToggleProps) => {
  const dispatch = useAppDispatch();
  const themeMode = useAppSelector(selectThemeMode);

  const handleToggle = () => {
    dispatch(toggleTheme());
  };

  // Determine which icon to show and label to use
  const isDarkMode = themeMode === 'dark';
  const icon = isDarkMode ? <Brightness7 /> : <Brightness4 />;
  const label = isDarkMode ? 'Switch to light mode' : 'Switch to dark mode';
  const tooltipText = isDarkMode ? 'Switch to light mode' : 'Switch to dark mode';

  return (
    <Tooltip title={tooltipText} arrow>
      <IconButton
        edge={edge}
        color="inherit"
        onClick={handleToggle}
        aria-label={label}
        role="button"
        sx={{
          ...sx,
        }}
      >
        {icon}
      </IconButton>
    </Tooltip>
  );
};

export default ThemeToggle;
