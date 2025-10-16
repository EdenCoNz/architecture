# Feature 3: Dark Mode Toggle

## Execution Order

### Phase 1 (Sequential)
- Story 1 (agent: ui-ux-designer) - Design foundation must come first

### Phase 2 (Parallel)
- Story 2 (agent: frontend-developer) - depends on Story 1
- Story 3 (agent: frontend-developer) - depends on Story 1

### Phase 3 (Sequential)
- Story 4 (agent: frontend-developer) - depends on Stories 2, 3

### Phase 4 (Sequential)
- Story 5 (agent: frontend-developer) - depends on Story 4

### Phase 5 (Sequential)
- Story 6 (agent: frontend-developer) - depends on Story 5

---

## User Stories

### 1. Design Dark Mode Color System and Toggle Component
Design the dark mode color palette, component specifications, and toggle interaction patterns that align with the existing Material Design 3 design system. Establish visual standards for dark theme variants of all UI elements including backgrounds, text colors, component states, and the theme toggle switch itself.

**Design Context**:
- Update docs/design-brief.md to incorporate design decisions for this feature
- Add a feature-specific section under the "## Features" heading
- Include component specifications, interaction patterns, and all UI states
- Ensure consistency with existing design system (colors, typography, spacing)

Acceptance Criteria:
- Dark mode color palette defined with background colors, text colors, and semantic colors (primary, secondary, error, warning, info, success) that meet WCAG AA contrast requirements
- Toggle switch component design specified with both light and dark mode appearances, including all states (default, hover, focus, active, disabled)
- Design brief updated with dark mode specifications under a new "Feature: Dark Mode" section
- All interactive component states documented (buttons, cards, inputs in dark mode)

Agent: ui-ux-designer
Dependencies: none

---

### 2. Create Theme Toggle Context and Provider
Implement a React Context for managing theme mode state (light/dark) with persistence to localStorage. Create a ThemeProvider wrapper that reads the user's preference and provides toggle functionality to child components.

Acceptance Criteria:
- ThemeContext created with useTheme hook exposing mode (light/dark) and toggleTheme function
- Theme preference persisted to localStorage and restored on page reload
- System preference detected via prefers-color-scheme media query on first visit
- Unit tests verify context state management, localStorage persistence, and system preference detection

Agent: frontend-developer
Dependencies: 1

---

### 3. Extend MUI Theme with Dark Mode Palette
Create dark mode color palette in the MUI theme configuration that mirrors the existing light mode palette structure. Define dark mode variants for all theme colors including backgrounds, text, primary, secondary, and semantic colors.

Acceptance Criteria:
- Dark mode palette added to frontend/src/theme/index.ts with all color tokens defined per design brief
- Theme dynamically switches between light and dark palettes based on mode from ThemeContext
- Dark mode colors meet WCAG AA contrast requirements (minimum 4.5:1 for text, 3:1 for UI components)
- Unit tests verify theme palette switches correctly when mode changes

Agent: frontend-developer
Dependencies: 1

---

### 4. Implement Toggle Switch Component
Build the theme toggle switch UI component that allows users to switch between light and dark modes. The component should display current theme state and trigger theme changes when clicked.

Acceptance Criteria:
- ThemeToggle component created using MUI Switch component with light/dark mode icons
- Component integrates with ThemeContext to read current mode and call toggleTheme
- Visual appearance matches design specifications for both light and dark modes
- Unit tests verify component renders correctly, shows current theme state, and calls toggleTheme on click

Agent: frontend-developer
Dependencies: 2, 3

---

### 5. Add Theme Toggle to Application Header
Integrate the theme toggle switch into the existing Header component, positioned in the AppBar actions area. Ensure the toggle is accessible on both mobile and desktop viewports.

Acceptance Criteria:
- ThemeToggle component added to Header component in the actions/toolbar area
- Toggle appears on both mobile (drawer) and desktop (AppBar) layouts
- Positioning follows existing Header spacing and alignment patterns
- Unit tests verify Header renders ThemeToggle and toggle functionality works within Header context

Agent: frontend-developer
Dependencies: 4

---

### 6. Test Dark Mode Across All Application Components
Verify dark mode displays correctly across all existing application components (Header, Home page, NotFound page) with proper contrast, readability, and visual consistency. Update component tests to cover both light and dark mode rendering.

Acceptance Criteria:
- All existing components render correctly in dark mode with proper contrast and colors
- Component unit tests updated to test both light and dark theme rendering
- Visual regression testing performed on all pages (Home, NotFound) in both themes
- No accessibility violations in dark mode (contrast, focus indicators, ARIA labels)

Agent: frontend-developer
Dependencies: 5

---
