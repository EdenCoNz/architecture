/**
 * Material UI Theme Configuration
 *
 * Custom theme configuration implementing the design system from design-brief.md.
 * Includes color palette, typography, spacing, breakpoints, and component overrides.
 * Supports dynamic light/dark mode switching.
 */

export { createAppTheme, getSystemThemePreference, getResolvedThemeMode } from './createAppTheme';

// Default theme export for backward compatibility (light mode)
import { createAppTheme } from './createAppTheme';
const theme = createAppTheme('light', false);
export default theme;
