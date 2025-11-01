# Application Design Brief

## Overview
- **Problem**: Modern web applications require a cohesive, scalable design system that ensures consistency, accessibility, and optimal user experience across all features and components.
- **Solution**: A comprehensive Material UI-based design system with carefully selected color palettes, typography scales, spacing systems, and component patterns that align with Material Design 3 principles while maintaining flexibility for brand expression.
- **Target users**: End users expecting modern, accessible, and intuitive web interfaces; developers requiring clear design specifications for implementation.

## Material UI Theme Configuration

### Primary Color
- **Main**: `#1976d2` (Medium Blue)
- **Light**: `#42a5f5` (Light Blue)
- **Dark**: `#1565c0` (Dark Blue)
- **Contrast Text**: `#ffffff`
- **Rationale**: Professional blue conveys trust, stability, and reliability. Sufficient contrast for accessibility while maintaining visual appeal.

### Secondary Color
- **Main**: `#dc004e` (Vibrant Pink)
- **Light**: `#f50057` (Light Pink)
- **Dark**: `#9a0036` (Dark Pink)
- **Contrast Text**: `#ffffff`
- **Rationale**: Creates visual interest and draws attention to key actions. Complements primary color without competing.

### Error Color
- **Main**: `#d32f2f` (Red 700)
- **Light**: `#ef5350` (Red 400)
- **Dark**: `#c62828` (Red 800)
- **Rationale**: Standard error red with WCAG AA compliance.

### Warning Color
- **Main**: `#ed6c02` (Orange 700)
- **Light**: `#ff9800` (Orange 500)
- **Dark**: `#e65100` (Orange 900)
- **Rationale**: Distinctive from error, clearly communicates caution.

### Info Color
- **Main**: `#0288d1` (Light Blue 700)
- **Light**: `#03a9f4` (Light Blue 500)
- **Dark**: `#01579b` (Light Blue 900)
- **Rationale**: Differentiates informational messages from primary actions.

### Success Color
- **Main**: `#2e7d32` (Green 700)
- **Light**: `#4caf50` (Green 500)
- **Dark**: `#1b5e20` (Green 900)
- **Rationale**: Universal success indicator with strong contrast.

### Typography
- **Font Family**: `'Roboto', 'Helvetica', 'Arial', sans-serif` (MUI default)
- **Base Font Size**: 16px
- **Font Weight Range**: 300 (Light), 400 (Regular), 500 (Medium), 700 (Bold)
- **Rationale**: Roboto is optimized for Material Design, highly legible across devices, and supports extensive character sets.

### Spacing Scale
- **Base Unit**: 8px (MUI default)
- **Scale**: Uses MUI spacing function - spacing(1) = 8px, spacing(2) = 16px, etc.
- **Rationale**: 8px grid system ensures consistent rhythm, aligns with touch target sizes (48px minimum = spacing(6)).

### Shape
- **Border Radius**: 4px (MUI default)
- **Rationale**: Subtle rounding softens interfaces without appearing overly rounded. Consistent with Material Design 3.

### Breakpoints
- **xs**: 0px (mobile portrait)
- **sm**: 600px (mobile landscape, small tablets)
- **md**: 900px (tablets, small laptops)
- **lg**: 1200px (desktops)
- **xl**: 1536px (large desktops)
- **Rationale**: MUI defaults cover standard device ranges. Mobile-first approach ensures core experience works on smallest screens.

### Component Overrides
- **Button**: `textTransform: 'none'` - Preserves readability, avoids aggressive all-caps styling
- **Card**: Elevation 1 by default, elevation 3 on hover for interactive cards
- **AppBar**: Elevation 0 with bottom border for cleaner modern look

## Visual System

### Extended Color Palette

| Purpose | Color | Hex Code | Usage |
|---------|-------|----------|-------|
| Background Default | Paper | `#ffffff` | Main content backgrounds |
| Background Paper | White | `#fafafa` | Card and elevated surface backgrounds |
| Text Primary | Dark Grey | `rgba(0, 0, 0, 0.87)` | Primary content text |
| Text Secondary | Medium Grey | `rgba(0, 0, 0, 0.6)` | Secondary content text |
| Text Disabled | Light Grey | `rgba(0, 0, 0, 0.38)` | Disabled text states |
| Divider | Grey | `rgba(0, 0, 0, 0.12)` | Separators and borders |
| Action Active | Primary | `rgba(25, 118, 210, 0.54)` | Active icons and indicators |
| Action Hover | Black | `rgba(0, 0, 0, 0.04)` | Hover state backgrounds |
| Action Selected | Primary | `rgba(25, 118, 210, 0.08)` | Selected state backgrounds |
| Action Disabled Background | Grey | `rgba(0, 0, 0, 0.12)` | Disabled button backgrounds |

### Typography Scale

| Variant | Size | Weight | Line Height | Letter Spacing | Usage |
|---------|------|--------|-------------|----------------|-------|
| h1 | 96px | 300 | 1.167 | -1.5px | Hero headings, marketing |
| h2 | 60px | 300 | 1.2 | -0.5px | Page titles |
| h3 | 48px | 400 | 1.167 | 0px | Section headings |
| h4 | 34px | 400 | 1.235 | 0.25px | Subsection headings |
| h5 | 24px | 400 | 1.334 | 0px | Card titles, dialog titles |
| h6 | 20px | 500 | 1.6 | 0.15px | Component titles |
| subtitle1 | 16px | 400 | 1.75 | 0.15px | Subtitle text, large secondary |
| subtitle2 | 14px | 500 | 1.57 | 0.1px | Dense subtitle text |
| body1 | 16px | 400 | 1.5 | 0.15px | Primary body text |
| body2 | 14px | 400 | 1.43 | 0.15px | Secondary body text, captions |
| button | 14px | 500 | 1.75 | 0.4px | Button labels (uppercase removed) |
| caption | 12px | 400 | 1.66 | 0.4px | Help text, timestamps |
| overline | 12px | 400 | 2.66 | 1px | Labels, eyebrows |

### Spacing System
- **4px** (spacing(0.5)): Tight inline spacing, icon padding
- **8px** (spacing(1)): Minimum touch padding, compact list items
- **16px** (spacing(2)): Default component padding, list item spacing
- **24px** (spacing(3)): Section spacing within cards
- **32px** (spacing(4)): Component spacing, card padding
- **48px** (spacing(6)): Section headings, large component spacing
- **64px** (spacing(8)): Page section spacing
- **96px** (spacing(12)): Major page divisions

### Layout Grid
- **Container Max Widths**: xs: auto, sm: 600px, md: 960px, lg: 1280px, xl: 1920px
- **Grid Columns**: 12-column system
- **Grid Spacing**: spacing(2) = 16px default gutter
- **Usage**: Responsive layouts using Grid v6 `size` and `offset` props

## Component Library

### MUI Components Used

#### Layout Components
- **Container**: Page-level content wrapper with responsive max-widths
- **Grid**: Responsive grid system for layouts (v6 API with size/offset)
- **Stack**: One-dimensional layouts with automatic spacing
- **Box**: Utility component for custom layouts and spacing

#### Navigation
- **AppBar**: Top application bar for branding and navigation
- **Drawer**: Side navigation drawer (temporary for mobile, permanent for desktop)
- **Tabs**: Horizontal content organization
- **Breadcrumbs**: Hierarchical navigation indicator
- **BottomNavigation**: Mobile primary navigation

#### Input Components
- **TextField**: Text input with outlined variant default
- **Button**: Text, contained, outlined variants
- **IconButton**: Icon-only actions
- **Checkbox**: Multi-select options
- **Radio**: Single-select options
- **Switch**: Toggle states
- **Select**: Dropdown selection
- **Autocomplete**: Searchable select with suggestions

#### Data Display
- **Card**: Content containers with optional actions
- **Table**: Tabular data display with sorting and pagination
- **List**: Vertical content lists
- **Chip**: Compact elements for tags, categories, selections
- **Avatar**: User or entity representation
- **Badge**: Notification indicators
- **Tooltip**: Contextual help on hover

#### Feedback
- **Alert**: Contextual feedback messages (success, info, warning, error)
- **Snackbar**: Brief notifications at screen bottom
- **Dialog**: Modal dialogs for confirmations and forms
- **CircularProgress**: Loading indicator for async operations
- **LinearProgress**: Progress bars for determinate operations
- **Skeleton**: Loading placeholders matching content shape

#### Surfaces
- **Paper**: Elevated surfaces with customizable elevation
- **Accordion**: Expandable content sections
- **Card**: Content containers (uses Paper internally)

### Custom Component Patterns

#### Page Layout Pattern
```
AppBar (sticky top)
  └─ Toolbar
      ├─ Menu Icon (mobile)
      ├─ Logo/Title
      └─ Actions
Container
  └─ Grid layout
      └─ Content
```

#### Card Action Pattern
```
Card
  ├─ CardMedia (optional)
  ├─ CardHeader (title, subtitle, avatar)
  ├─ CardContent
  └─ CardActions (align right)
```

#### Form Pattern
```
Stack (spacing: 3)
  ├─ TextField (fullWidth)
  ├─ TextField (fullWidth)
  └─ Stack (direction: row, justifyContent: flex-end, spacing: 2)
      ├─ Button (variant: outlined)
      └─ Button (variant: contained)
```

## Navigation & User Flow

### Navigation Pattern
- **Mobile (< md)**: Bottom navigation or temporary drawer triggered by menu icon
- **Desktop (>= md)**: Persistent drawer or top horizontal navigation via AppBar
- **Breadcrumbs**: For hierarchical content navigation (3+ levels deep)

### Primary User Flows
- **Authentication**: Login → Dashboard → Feature
- **Content Discovery**: Home → Browse/Search → Detail → Action
- **Task Completion**: Entry Point → Form/Wizard → Confirmation → Success

## Features

### Feature: Dark Mode and Light Mode Themes
**Purpose**: Provide dual theme system allowing users to select visual appearance that suits their preferences and viewing conditions, reducing eye strain and improving accessibility.

**Design Decisions**:
- **Material Design 3 dark theme principles**: Follows MD3 elevation overlays, surface tinting, and contrast guidelines for professional, accessible dark mode
- **Independent color palettes**: Each theme uses carefully selected colors optimized for its background, not simple inversions
- **WCAG AA compliance in both themes**: All text and UI elements meet 4.5:1 (text) and 3:1 (UI) contrast ratios in both light and dark modes
- **Semantic color system**: Colors defined by purpose (primary, error, success) adapt contextually to theme, maintaining meaning across modes

**Theme Philosophy**:
- **Light Theme**: Professional, clean, high-energy aesthetic suitable for bright environments. Optimized for readability on white/light backgrounds.
- **Dark Theme**: Reduced eye strain in low-light conditions, modern aesthetic, battery savings on OLED displays. Uses elevated surfaces with subtle tinting rather than pure black.

#### Light Theme Palette

| Color Token | Value | Contrast vs Background | Usage |
|-------------|-------|----------------------|-------|
| **Backgrounds** | | | |
| background.default | `#fafafa` | - | Page background, lowest elevation |
| background.paper | `#ffffff` | - | Card, dialog, drawer surfaces |
| **Text** | | | |
| text.primary | `rgba(0, 0, 0, 0.87)` | 15.8:1 | Primary content, headings |
| text.secondary | `rgba(0, 0, 0, 0.6)` | 7.7:1 | Secondary content, descriptions |
| text.disabled | `rgba(0, 0, 0, 0.38)` | 3.9:1 | Disabled states (non-interactive) |
| **Primary** | | | |
| primary.main | `#1976d2` | 4.65:1 (on white) | Primary buttons, links, focus states |
| primary.light | `#42a5f5` | 3.1:1 (on white) | Hover states, selected backgrounds |
| primary.dark | `#1565c0` | 5.9:1 (on white) | Active states, pressed buttons |
| primary.contrastText | `#ffffff` | 4.65:1 (on primary.main) | Text on primary backgrounds |
| **Secondary** | | | |
| secondary.main | `#dc004e` | 5.2:1 (on white) | Accent actions, FABs |
| secondary.light | `#f50057` | 3.9:1 (on white) | Secondary hover states |
| secondary.dark | `#9a0036` | 8.5:1 (on white) | Secondary active states |
| secondary.contrastText | `#ffffff` | 5.2:1 (on secondary.main) | Text on secondary backgrounds |
| **Semantic Colors** | | | |
| error.main | `#d32f2f` | 5.1:1 (on white) | Error messages, destructive actions |
| error.light | `#ef5350` | 3.8:1 (on white) | Error backgrounds |
| error.dark | `#c62828` | 6.5:1 (on white) | Error active states |
| warning.main | `#ed6c02` | 4.6:1 (on white) | Warning messages |
| warning.light | `#ff9800` | 3.2:1 (on white) | Warning backgrounds |
| warning.dark | `#e65100` | 6.8:1 (on white) | Warning active states |
| info.main | `#0288d1` | 4.9:1 (on white) | Informational messages |
| info.light | `#03a9f4` | 3.4:1 (on white) | Info backgrounds |
| info.dark | `#01579b` | 7.2:1 (on white) | Info active states |
| success.main | `#2e7d32` | 4.7:1 (on white) | Success messages, confirmations |
| success.light | `#4caf50` | 3.3:1 (on white) | Success backgrounds |
| success.dark | `#1b5e20` | 7.9:1 (on white) | Success active states |
| **UI Elements** | | | |
| divider | `rgba(0, 0, 0, 0.12)` | - | Borders, separators |
| action.hover | `rgba(0, 0, 0, 0.04)` | - | Hover state overlay |
| action.selected | `rgba(0, 0, 0, 0.08)` | - | Selected state background |
| action.disabled | `rgba(0, 0, 0, 0.26)` | - | Disabled text |
| action.disabledBackground | `rgba(0, 0, 0, 0.12)` | - | Disabled button backgrounds |

#### Dark Theme Palette

| Color Token | Value | Contrast vs Background | Usage |
|-------------|-------|----------------------|-------|
| **Backgrounds** | | | |
| background.default | `#121212` | - | Page background, lowest elevation |
| background.paper | `#1e1e1e` | - | Card, dialog, drawer surfaces (elevation 1) |
| **Elevated Surfaces** (MD3 overlay system) | | | |
| elevation-0 | `#121212` | - | Default background |
| elevation-1 | `#1e1e1e` | - | App bar, cards |
| elevation-2 | `#232323` | - | Floating action buttons, hover states |
| elevation-3 | `#252525` | - | Drawers, modals |
| elevation-4 | `#272727` | - | Dialogs |
| elevation-6 | `#2c2c2c` | - | Snackbars |
| elevation-8 | `#2e2e2e` | - | Menus, tooltips |
| **Text** | | | |
| text.primary | `rgba(255, 255, 255, 0.87)` | 14.9:1 | Primary content, headings |
| text.secondary | `rgba(255, 255, 255, 0.6)` | 7.4:1 | Secondary content, descriptions |
| text.disabled | `rgba(255, 255, 255, 0.38)` | 3.7:1 | Disabled states (non-interactive) |
| **Primary** | | | |
| primary.main | `#90caf9` | 6.2:1 (on #121212) | Primary buttons, links, focus states |
| primary.light | `#bbdefb` | 9.8:1 (on #121212) | Hover states, selected backgrounds |
| primary.dark | `#42a5f5` | 4.1:1 (on #121212) | Active states, pressed buttons |
| primary.contrastText | `rgba(0, 0, 0, 0.87)` | 11.2:1 (on primary.main) | Text on primary backgrounds |
| **Secondary** | | | |
| secondary.main | `#f48fb1` | 5.8:1 (on #121212) | Accent actions, FABs |
| secondary.light | `#f8bbd0` | 8.1:1 (on #121212) | Secondary hover states |
| secondary.dark | `#ec407a` | 4.2:1 (on #121212) | Secondary active states |
| secondary.contrastText | `rgba(0, 0, 0, 0.87)` | 10.5:1 (on secondary.main) | Text on secondary backgrounds |
| **Semantic Colors** | | | |
| error.main | `#ef5350` | 5.6:1 (on #121212) | Error messages, destructive actions |
| error.light | `#e57373` | 6.9:1 (on #121212) | Error backgrounds |
| error.dark | `#d32f2f` | 4.8:1 (on #121212) | Error active states |
| warning.main | `#ffa726` | 7.1:1 (on #121212) | Warning messages |
| warning.light | `#ffb74d` | 8.9:1 (on #121212) | Warning backgrounds |
| warning.dark | `#f57c00` | 5.8:1 (on #121212) | Warning active states |
| info.main | `#4fc3f7` | 7.8:1 (on #121212) | Informational messages |
| info.light | `#81d4fa` | 10.2:1 (on #121212) | Info backgrounds |
| info.dark | `#0288d1` | 5.1:1 (on #121212) | Info active states |
| success.main | `#66bb6a` | 6.4:1 (on #121212) | Success messages, confirmations |
| success.light | `#81c784` | 7.9:1 (on #121212) | Success backgrounds |
| success.dark | `#388e3c` | 4.9:1 (on #121212) | Success active states |
| **UI Elements** | | | |
| divider | `rgba(255, 255, 255, 0.12)` | - | Borders, separators |
| action.hover | `rgba(255, 255, 255, 0.08)` | - | Hover state overlay |
| action.selected | `rgba(255, 255, 255, 0.16)` | - | Selected state background |
| action.disabled | `rgba(255, 255, 255, 0.3)` | - | Disabled text |
| action.disabledBackground | `rgba(255, 255, 255, 0.12)` | - | Disabled button backgrounds |

#### UI States - Light Theme

| Component | State | Background | Text/Icon | Border | Elevation | Transition |
|-----------|-------|-----------|-----------|--------|-----------|------------|
| **Button (Contained)** | Default | primary.main (#1976d2) | #ffffff | none | 2 | - |
| | Hover | primary.dark (#1565c0) | #ffffff | none | 4 | 225ms |
| | Focus | primary.main | #ffffff | 2px outline primary.light | 2 | 0ms |
| | Active | primary.dark | #ffffff | none | 8 | 150ms |
| | Disabled | rgba(0,0,0,0.12) | rgba(0,0,0,0.26) | none | 0 | - |
| **Button (Outlined)** | Default | transparent | primary.main | 1px primary.main | 0 | - |
| | Hover | rgba(25,118,210,0.04) | primary.dark | 1px primary.main | 0 | 225ms |
| | Focus | transparent | primary.main | 2px primary.main | 0 | 0ms |
| | Active | rgba(25,118,210,0.12) | primary.dark | 1px primary.dark | 0 | 150ms |
| | Disabled | transparent | rgba(0,0,0,0.26) | 1px rgba(0,0,0,0.12) | 0 | - |
| **Button (Text)** | Default | transparent | primary.main | none | 0 | - |
| | Hover | rgba(25,118,210,0.04) | primary.dark | none | 0 | 225ms |
| | Focus | transparent | primary.main | 2px outline primary.light | 0 | 0ms |
| | Active | rgba(25,118,210,0.12) | primary.dark | none | 0 | 150ms |
| | Disabled | transparent | rgba(0,0,0,0.26) | none | 0 | - |
| **TextField** | Default | transparent | text.primary | 1px rgba(0,0,0,0.23) | 0 | - |
| | Hover | transparent | text.primary | 1px rgba(0,0,0,0.87) | 0 | 225ms |
| | Focus | transparent | text.primary | 2px primary.main | 0 | 0ms |
| | Error | transparent | error.main | 2px error.main | 0 | 0ms |
| | Disabled | rgba(0,0,0,0.04) | rgba(0,0,0,0.38) | 1px rgba(0,0,0,0.12) | 0 | - |
| **Card** | Default | #ffffff | text.primary | none | 1 | - |
| | Hover (interactive) | #ffffff | text.primary | none | 3 | 225ms |
| | Focus | #ffffff | text.primary | 2px outline primary.main | 1 | 0ms |
| | Selected | #ffffff | text.primary | 2px solid primary.main | 1 | - |
| **List Item** | Default | transparent | text.primary | none | 0 | - |
| | Hover | rgba(0,0,0,0.04) | text.primary | none | 0 | 150ms |
| | Focus | transparent | text.primary | 2px outline primary.main | 0 | 0ms |
| | Selected | rgba(25,118,210,0.08) | primary.main | none | 0 | - |
| **Switch** | Off | rgba(0,0,0,0.38) | #fafafa | none | 1 | - |
| | On | primary.main | #ffffff | none | 1 | 225ms |
| | Disabled Off | rgba(0,0,0,0.12) | rgba(0,0,0,0.12) | none | 0 | - |
| | Disabled On | rgba(25,118,210,0.3) | rgba(255,255,255,0.3) | none | 0 | - |
| **Checkbox** | Unchecked | transparent | rgba(0,0,0,0.54) | 2px rgba(0,0,0,0.54) | 0 | - |
| | Checked | primary.main | #ffffff | 2px primary.main | 0 | 150ms |
| | Indeterminate | primary.main | #ffffff | 2px primary.main | 0 | 150ms |
| | Disabled Unchecked | transparent | rgba(0,0,0,0.26) | 2px rgba(0,0,0,0.26) | 0 | - |
| | Disabled Checked | rgba(0,0,0,0.26) | rgba(0,0,0,0.26) | 2px rgba(0,0,0,0.26) | 0 | - |

#### UI States - Dark Theme

| Component | State | Background | Text/Icon | Border | Elevation | Transition |
|-----------|-------|-----------|-----------|--------|-----------|------------|
| **Button (Contained)** | Default | primary.main (#90caf9) | rgba(0,0,0,0.87) | none | 2 | - |
| | Hover | primary.light (#bbdefb) | rgba(0,0,0,0.87) | none | 4 | 225ms |
| | Focus | primary.main | rgba(0,0,0,0.87) | 2px outline primary.dark | 2 | 0ms |
| | Active | primary.dark (#42a5f5) | rgba(0,0,0,0.87) | none | 8 | 150ms |
| | Disabled | rgba(255,255,255,0.12) | rgba(255,255,255,0.3) | none | 0 | - |
| **Button (Outlined)** | Default | transparent | primary.main | 1px primary.main | 0 | - |
| | Hover | rgba(144,202,249,0.08) | primary.light | 1px primary.main | 0 | 225ms |
| | Focus | transparent | primary.main | 2px primary.main | 0 | 0ms |
| | Active | rgba(144,202,249,0.16) | primary.light | 1px primary.light | 0 | 150ms |
| | Disabled | transparent | rgba(255,255,255,0.3) | 1px rgba(255,255,255,0.12) | 0 | - |
| **Button (Text)** | Default | transparent | primary.main | none | 0 | - |
| | Hover | rgba(144,202,249,0.08) | primary.light | none | 0 | 225ms |
| | Focus | transparent | primary.main | 2px outline primary.dark | 0 | 0ms |
| | Active | rgba(144,202,249,0.16) | primary.light | none | 0 | 150ms |
| | Disabled | transparent | rgba(255,255,255,0.3) | none | 0 | - |
| **TextField** | Default | transparent | text.primary | 1px rgba(255,255,255,0.23) | 0 | - |
| | Hover | transparent | text.primary | 1px rgba(255,255,255,0.87) | 0 | 225ms |
| | Focus | transparent | text.primary | 2px primary.main | 0 | 0ms |
| | Error | transparent | error.main | 2px error.main | 0 | 0ms |
| | Disabled | rgba(255,255,255,0.04) | rgba(255,255,255,0.38) | 1px rgba(255,255,255,0.12) | 0 | - |
| **Card** | Default | #1e1e1e | text.primary | none | 1 | - |
| | Hover (interactive) | #232323 | text.primary | none | 3 | 225ms |
| | Focus | #1e1e1e | text.primary | 2px outline primary.main | 1 | 0ms |
| | Selected | #1e1e1e | text.primary | 2px solid primary.main | 1 | - |
| **List Item** | Default | transparent | text.primary | none | 0 | - |
| | Hover | rgba(255,255,255,0.08) | text.primary | none | 0 | 150ms |
| | Focus | transparent | text.primary | 2px outline primary.main | 0 | 0ms |
| | Selected | rgba(144,202,249,0.16) | primary.main | none | 0 | - |
| **Switch** | Off | rgba(255,255,255,0.38) | #2c2c2c | none | 1 | - |
| | On | primary.main | rgba(0,0,0,0.87) | none | 1 | 225ms |
| | Disabled Off | rgba(255,255,255,0.12) | rgba(255,255,255,0.12) | none | 0 | - |
| | Disabled On | rgba(144,202,249,0.3) | rgba(0,0,0,0.3) | none | 0 | - |
| **Checkbox** | Unchecked | transparent | rgba(255,255,255,0.7) | 2px rgba(255,255,255,0.7) | 0 | - |
| | Checked | primary.main | rgba(0,0,0,0.87) | 2px primary.main | 0 | 150ms |
| | Indeterminate | primary.main | rgba(0,0,0,0.87) | 2px primary.main | 0 | 150ms |
| | Disabled Unchecked | transparent | rgba(255,255,255,0.3) | 2px rgba(255,255,255,0.3) | 0 | - |
| | Disabled Checked | rgba(255,255,255,0.3) | rgba(255,255,255,0.3) | 2px rgba(255,255,255,0.3) | 0 | - |

#### Accessibility Compliance Summary

**Light Theme Compliance**:
- Text Primary (15.8:1): Exceeds WCAG AAA (7:1)
- Text Secondary (7.7:1): Exceeds WCAG AAA (7:1)
- Primary Button (4.65:1): Passes WCAG AA (4.5:1)
- All semantic colors: Pass WCAG AA minimum
- UI components: All pass 3:1 contrast requirement

**Dark Theme Compliance**:
- Text Primary (14.9:1): Exceeds WCAG AAA (7:1)
- Text Secondary (7.4:1): Exceeds WCAG AAA (7:1)
- Primary Button (6.2:1): Exceeds WCAG AA (4.5:1)
- All semantic colors: Pass WCAG AA minimum with enhanced ratios
- UI components: All pass 3:1 contrast requirement

**Special Considerations**:
- Focus indicators: 2px outline minimum, 3:1 contrast ratio
- Disabled states: Intentionally lower contrast (non-interactive)
- Large text (18px+): Can use 3:1 contrast ratio per WCAG
- Interactive elements: All meet 48x48px minimum touch target
- Color blind safe: Semantic colors distinguished by luminance, not hue alone

#### MUI Theme Implementation Structure

Both themes use MUI's `createTheme` with mode-specific palette configurations:

**Light Theme**:
```javascript
{
  palette: {
    mode: 'light',
    primary: { main: '#1976d2', light: '#42a5f5', dark: '#1565c0' },
    secondary: { main: '#dc004e', light: '#f50057', dark: '#9a0036' },
    error: { main: '#d32f2f', light: '#ef5350', dark: '#c62828' },
    warning: { main: '#ed6c02', light: '#ff9800', dark: '#e65100' },
    info: { main: '#0288d1', light: '#03a9f4', dark: '#01579b' },
    success: { main: '#2e7d32', light: '#4caf50', dark: '#1b5e20' },
    background: { default: '#fafafa', paper: '#ffffff' },
    text: {
      primary: 'rgba(0, 0, 0, 0.87)',
      secondary: 'rgba(0, 0, 0, 0.6)',
      disabled: 'rgba(0, 0, 0, 0.38)',
    },
  }
}
```

**Dark Theme**:
```javascript
{
  palette: {
    mode: 'dark',
    primary: { main: '#90caf9', light: '#bbdefb', dark: '#42a5f5' },
    secondary: { main: '#f48fb1', light: '#f8bbd0', dark: '#ec407a' },
    error: { main: '#ef5350', light: '#e57373', dark: '#d32f2f' },
    warning: { main: '#ffa726', light: '#ffb74d', dark: '#f57c00' },
    info: { main: '#4fc3f7', light: '#81d4fa', dark: '#0288d1' },
    success: { main: '#66bb6a', light: '#81c784', dark: '#388e3c' },
    background: { default: '#121212', paper: '#1e1e1e' },
    text: {
      primary: 'rgba(255, 255, 255, 0.87)',
      secondary: 'rgba(255, 255, 255, 0.6)',
      disabled: 'rgba(255, 255, 255, 0.38)',
    },
  }
}
```

#### Design Rationale

**Color Selection**:
- Light theme: Standard Material Design colors, proven for readability
- Dark theme: Lighter shades of primary/secondary for sufficient contrast on dark backgrounds
- Semantic colors: Adjusted luminance to maintain WCAG compliance in both themes

**Background Strategy**:
- Light: Off-white (#fafafa) reduces eye strain vs pure white
- Dark: Elevated surfaces (#1e1e1e, #232323, etc.) create depth, avoid pure black for better contrast and reduced OLED burn-in

**Text Opacity**:
- Consistent alpha values across themes (0.87, 0.6, 0.38) maintain hierarchy
- Higher opacity for primary text ensures readability
- Lower opacity for secondary content creates visual hierarchy without additional colors

**State Feedback**:
- Hover states: Subtle background overlays (0.04-0.08 alpha)
- Focus states: 2px outline for keyboard navigation visibility
- Active states: Increased elevation + color shift for tactile feedback
- Disabled states: Reduced contrast signals non-interactive elements

### Feature: Application Shell
**Purpose**: Establish consistent layout structure and navigation framework for entire application.

**Design Decisions**:
- **AppBar with responsive drawer**: Provides familiar navigation pattern that adapts from mobile to desktop
- **Content Container with consistent padding**: Ensures content never touches viewport edges, maintains readability max-width
- **Sticky AppBar**: Keeps navigation accessible during scroll, reinforces application context

**Components Used**: AppBar, Toolbar, Drawer, Container, Stack, Box, IconButton

**Interaction Patterns**:
- Mobile: Hamburger menu opens temporary drawer overlay
- Desktop: Drawer persistent by default, collapsible via toggle
- Active route highlighted in navigation list
- Smooth transitions (225ms) for drawer open/close

**States**:
- **Loading**: AppBar renders immediately, Skeleton placeholders in content area
- **Empty**: Navigation available, empty state illustration in content with CTA
- **Error**: Error Alert banner below AppBar, navigation remains functional
- **Success**: Full layout with content populated

## Accessibility

### WCAG AA Compliance
- **Text Contrast**: Minimum 4.5:1 for normal text, 3:1 for large text (18px+)
  - Primary text on white: 15.8:1 (rgba(0,0,0,0.87) on #ffffff)
  - Secondary text on white: 7.7:1 (rgba(0,0,0,0.6) on #ffffff)
  - Primary button: 4.65:1 (#ffffff on #1976d2)
- **UI Component Contrast**: Minimum 3:1 for interactive elements
  - Button borders: 3.1:1
  - Focus indicators: 3.1:1 minimum

### Keyboard Navigation
- **Tab Order**: Logical flow matching visual hierarchy
- **Focus Indicators**: MUI default focus rings visible (2px outline with offset)
- **Skip Links**: "Skip to main content" link for screen reader and keyboard users
- **Shortcuts**: Common patterns (Esc to close dialogs, Arrow keys in lists)

### Screen Reader Support
- **Semantic HTML**: Proper heading hierarchy (h1 → h2 → h3)
- **ARIA Labels**: All IconButtons have aria-label attributes
- **ARIA Live Regions**: Snackbar notifications announced
- **Alt Text**: All meaningful images include descriptive alt text

### Additional Considerations
- **Focus Management**: Focus moves to dialogs on open, returns to trigger on close
- **Error Identification**: Form errors announced to screen readers with aria-describedby
- **Motion Reduction**: Respects prefers-reduced-motion media query
- **Touch Targets**: Minimum 48x48px (MUI default for buttons and interactive elements)

## Design Tokens

### MUI Theme Object
```javascript
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#dc004e',
      light: '#f50057',
      dark: '#9a0036',
      contrastText: '#ffffff',
    },
    error: {
      main: '#d32f2f',
      light: '#ef5350',
      dark: '#c62828',
    },
    warning: {
      main: '#ed6c02',
      light: '#ff9800',
      dark: '#e65100',
    },
    info: {
      main: '#0288d1',
      light: '#03a9f4',
      dark: '#01579b',
    },
    success: {
      main: '#2e7d32',
      light: '#4caf50',
      dark: '#1b5e20',
    },
    background: {
      default: '#fafafa',
      paper: '#ffffff',
    },
    text: {
      primary: 'rgba(0, 0, 0, 0.87)',
      secondary: 'rgba(0, 0, 0, 0.6)',
      disabled: 'rgba(0, 0, 0, 0.38)',
    },
    divider: 'rgba(0, 0, 0, 0.12)',
    action: {
      active: 'rgba(0, 0, 0, 0.54)',
      hover: 'rgba(0, 0, 0, 0.04)',
      selected: 'rgba(0, 0, 0, 0.08)',
      disabled: 'rgba(0, 0, 0, 0.26)',
      disabledBackground: 'rgba(0, 0, 0, 0.12)',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    fontSize: 16,
    fontWeightLight: 300,
    fontWeightRegular: 400,
    fontWeightMedium: 500,
    fontWeightBold: 700,
    h1: {
      fontSize: '6rem',
      fontWeight: 300,
      lineHeight: 1.167,
      letterSpacing: '-0.09375rem',
    },
    h2: {
      fontSize: '3.75rem',
      fontWeight: 300,
      lineHeight: 1.2,
      letterSpacing: '-0.03125rem',
    },
    h3: {
      fontSize: '3rem',
      fontWeight: 400,
      lineHeight: 1.167,
      letterSpacing: '0rem',
    },
    h4: {
      fontSize: '2.125rem',
      fontWeight: 400,
      lineHeight: 1.235,
      letterSpacing: '0.015625rem',
    },
    h5: {
      fontSize: '1.5rem',
      fontWeight: 400,
      lineHeight: 1.334,
      letterSpacing: '0rem',
    },
    h6: {
      fontSize: '1.25rem',
      fontWeight: 500,
      lineHeight: 1.6,
      letterSpacing: '0.009375rem',
    },
    subtitle1: {
      fontSize: '1rem',
      fontWeight: 400,
      lineHeight: 1.75,
      letterSpacing: '0.009375rem',
    },
    subtitle2: {
      fontSize: '0.875rem',
      fontWeight: 500,
      lineHeight: 1.57,
      letterSpacing: '0.00625rem',
    },
    body1: {
      fontSize: '1rem',
      fontWeight: 400,
      lineHeight: 1.5,
      letterSpacing: '0.009375rem',
    },
    body2: {
      fontSize: '0.875rem',
      fontWeight: 400,
      lineHeight: 1.43,
      letterSpacing: '0.009375rem',
    },
    button: {
      fontSize: '0.875rem',
      fontWeight: 500,
      lineHeight: 1.75,
      letterSpacing: '0.025rem',
      textTransform: 'none',
    },
    caption: {
      fontSize: '0.75rem',
      fontWeight: 400,
      lineHeight: 1.66,
      letterSpacing: '0.025rem',
    },
    overline: {
      fontSize: '0.75rem',
      fontWeight: 400,
      lineHeight: 2.66,
      letterSpacing: '0.0625rem',
      textTransform: 'uppercase',
    },
  },
  spacing: 8, // Base unit in pixels
  shape: {
    borderRadius: 4,
  },
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 900,
      lg: 1200,
      xl: 1536,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
        },
      },
      defaultProps: {
        disableElevation: false,
      },
    },
    MuiCard: {
      defaultProps: {
        elevation: 1,
      },
      styleOverrides: {
        root: {
          '&:hover': {
            elevation: 3,
          },
        },
      },
    },
    MuiAppBar: {
      defaultProps: {
        elevation: 0,
      },
      styleOverrides: {
        root: {
          borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
        },
      },
    },
  },
});

export default theme;
```

### CSS Variables (if using cssVariables: true)
```css
/* MUI generates these automatically from theme when cssVariables enabled */
:root {
  /* Palette */
  --mui-palette-primary-main: #1976d2;
  --mui-palette-primary-light: #42a5f5;
  --mui-palette-primary-dark: #1565c0;
  --mui-palette-secondary-main: #dc004e;
  --mui-palette-error-main: #d32f2f;
  --mui-palette-warning-main: #ed6c02;
  --mui-palette-info-main: #0288d1;
  --mui-palette-success-main: #2e7d32;
  --mui-palette-background-default: #fafafa;
  --mui-palette-background-paper: #ffffff;
  --mui-palette-text-primary: rgba(0, 0, 0, 0.87);
  --mui-palette-text-secondary: rgba(0, 0, 0, 0.6);

  /* Spacing */
  --mui-spacing: 8px;

  /* Shape */
  --mui-shape-borderRadius: 4px;
}
```

### Custom CSS Variables (for non-MUI styling)
```css
:root {
  /* Semantic Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-2xl: 48px;
  --spacing-3xl: 64px;

  /* Z-index Scale */
  --z-index-dropdown: 1000;
  --z-index-sticky: 1020;
  --z-index-fixed: 1030;
  --z-index-modal-backdrop: 1040;
  --z-index-modal: 1050;
  --z-index-popover: 1060;
  --z-index-tooltip: 1070;

  /* Transitions */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 225ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);

  /* Shadows (matching MUI elevation) */
  --shadow-1: 0px 2px 1px -1px rgba(0,0,0,0.2), 0px 1px 1px 0px rgba(0,0,0,0.14), 0px 1px 3px 0px rgba(0,0,0,0.12);
  --shadow-2: 0px 3px 1px -2px rgba(0,0,0,0.2), 0px 2px 2px 0px rgba(0,0,0,0.14), 0px 1px 5px 0px rgba(0,0,0,0.12);
  --shadow-3: 0px 3px 3px -2px rgba(0,0,0,0.2), 0px 3px 4px 0px rgba(0,0,0,0.14), 0px 1px 8px 0px rgba(0,0,0,0.12);
}
```

## Responsive Strategy

### Mobile-First Approach
All layouts designed for mobile (320px+) first, progressively enhanced for larger screens using MUI breakpoints.

### MUI Breakpoints Usage
- **xs (0px)**: Mobile portrait - Single column, full-width components, bottom navigation
- **sm (600px)**: Mobile landscape, small tablets - Two-column cards, persistent search
- **md (900px)**: Tablets, small laptops - Permanent drawer option, three-column grids, side-by-side forms
- **lg (1200px)**: Desktops - Four-column grids, expanded data tables, dashboard layouts
- **xl (1536px)**: Large desktops - Maximum content width constraints, additional sidebars

### Grid System Implementation
Using MUI Grid v6 with `size` and `offset` props:
```jsx
<Grid container spacing={2}>
  <Grid size={{ xs: 12, sm: 6, md: 4 }}>
    {/* Full width mobile, half tablet, third desktop */}
  </Grid>
</Grid>
```

### Responsive Typography
Fluid typography using clamp() for headings:
```javascript
h1: {
  fontSize: 'clamp(2.5rem, 5vw, 6rem)',
},
h2: {
  fontSize: 'clamp(2rem, 4vw, 3.75rem)',
},
```

### Component Responsive Behaviors

#### AppBar
- **xs-sm**: Fixed top, hamburger menu, minimal actions
- **md+**: Optional permanent drawer toggle, expanded actions, search bar

#### Navigation
- **xs-sm**: Bottom navigation (4-5 items) or temporary drawer
- **md+**: Permanent drawer (240px) or top horizontal tabs

#### Data Tables
- **xs-sm**: Card-based list view with key fields only
- **md+**: Full table with all columns, horizontal scroll if needed

#### Forms
- **xs**: Single column, full-width inputs, stacked buttons
- **sm+**: Two-column layout for related fields, inline button groups
- **md+**: Three-column for complex forms, side-by-side validation

#### Cards
- **xs**: Single column, full-width
- **sm**: 2 columns
- **md**: 3 columns
- **lg**: 4 columns
- **xl**: 4-6 columns with max-width constraint

### Performance Considerations
- **Lazy Load**: Below-fold content, drawer contents, dialog contents
- **Image Optimization**: Responsive images with srcset, lazy loading
- **Code Splitting**: Route-based splitting, component-based for large features
- **Critical CSS**: Inline critical styles, defer non-critical

### Touch Optimization
- **Minimum Touch Targets**: 48x48px (MUI default)
- **Spacing**: Minimum 8px between interactive elements
- **Gesture Support**: Swipe for drawer on mobile, pull-to-refresh where applicable
- **Hover States**: Show on touch (tap and hold) or disable on touch devices

### Feature: Hello Button Component
**Purpose**: Provide a welcoming, interactive entry point on the main page that greets users when clicked.

**Design Decisions**:
- **MUI Button Component (variant: contained, color: primary)**: Uses established primary color for clear call-to-action, contained variant provides strong visual weight appropriate for primary action
- **Large size with spacing(6) minimum touch target**: Ensures 48x48px accessibility requirement, makes button prominent and easy to tap on mobile
- **Center-aligned on page with generous whitespace**: Creates focal point, reduces cognitive load, guides user attention to primary interaction

**Component Specifications**:

| Aspect | Specification |
|--------|--------------|
| **Component** | MUI Button (contained variant) |
| **Text** | "Say Hello" |
| **Color** | primary (theme.palette.primary.main: #1976d2) |
| **Size** | large (height: 42.25px, padding: 8px 22px) |
| **Typography** | button variant (14px, 500 weight, 0.4px letter-spacing) |
| **Min Dimensions** | 48x48px (MUI touch target) |
| **Border Radius** | 4px (theme.shape.borderRadius) |
| **Elevation** | 2 (default MUI button elevation) |
| **Position** | Horizontally centered in Container, vertically centered in viewport |
| **Top Margin** | spacing(8) = 64px from page top |

**Interactive States**:

| State | Background | Text Color | Elevation | Cursor | Transition |
|-------|-----------|------------|-----------|--------|------------|
| **Default** | #1976d2 (primary.main) | #ffffff | 2 | pointer | - |
| **Hover** | #1565c0 (primary.dark) | #ffffff | 4 | pointer | 225ms |
| **Focus** | #1976d2 | #ffffff | 2 | pointer | 2px outline offset |
| **Active** | #1565c0 | #ffffff | 8 | pointer | 150ms |
| **Disabled** | rgba(0,0,0,0.12) | rgba(0,0,0,0.26) | 0 | not-allowed | - |

**Feedback Mechanism**:
- **Component**: MUI Snackbar with Alert (severity: success)
- **Message**: "Hello! Welcome to our application!"
- **Position**: Bottom center (anchorOrigin: { vertical: 'bottom', horizontal: 'center' })
- **Duration**: 3000ms auto-hide
- **Icon**: CheckCircle icon (MUI default for success Alert)
- **Background**: theme.palette.success.main (#2e7d32) with light variant for Alert
- **Transition**: Slide up entrance, fade out exit (225ms)

**All UI States**:
- **Default**: Button visible, ready for interaction
- **Loading**: Not applicable for this simple interaction (no async operation)
- **Success**: Snackbar appears with success message after click
- **Error**: Not applicable (no failure mode for greeting)
- **Empty**: Not applicable (button always present)

**Accessibility**:
- **Contrast Ratio**: 4.65:1 (white text #ffffff on primary blue #1976d2) - passes WCAG AA
- **Keyboard Navigation**: Tab to focus, Enter/Space to activate
- **Focus Indicator**: MUI default 2px outline with offset, primary color
- **Screen Reader**: Button text "Say Hello" descriptive of action
- **ARIA**: No additional ARIA needed (native button semantics sufficient)
- **Touch Target**: 48x48px minimum enforced by large size variant

**Responsive Behavior**:

| Breakpoint | Button Width | Container Padding | Vertical Position |
|-----------|--------------|-------------------|-------------------|
| **xs (0-599px)** | min-width: 120px | spacing(2) = 16px | margin-top: spacing(6) |
| **sm (600-899px)** | min-width: 140px | spacing(3) = 24px | margin-top: spacing(8) |
| **md (900px+)** | min-width: 160px | spacing(4) = 32px | margin-top: spacing(8) |

**Layout Structure**:
```jsx
<Container maxWidth="md">
  <Box
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '50vh',
      mt: { xs: 6, sm: 8 },
    }}
  >
    <Button
      variant="contained"
      color="primary"
      size="large"
      onClick={handleClick}
      sx={{ minWidth: { xs: 120, sm: 140, md: 160 } }}
    >
      Say Hello
    </Button>
  </Box>
  <Snackbar
    open={open}
    autoHideDuration={3000}
    onClose={handleClose}
    anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
  >
    <Alert severity="success" onClose={handleClose}>
      Hello! Welcome to our application!
    </Alert>
  </Snackbar>
</Container>
```

**Styling Approach**: sx prop for responsive overrides, MUI theme for colors and spacing

**Components Used**: Button, Container, Box, Snackbar, Alert

**Interaction Pattern**:
1. User views centered button on main page
2. User hovers - button darkens, elevation increases
3. User clicks/taps - button momentarily increases elevation (active state)
4. Snackbar slides up from bottom center with success message
5. After 3 seconds, Snackbar auto-dismisses with fade transition
6. User can click button again for repeated greeting

### Feature: Theme Toggle Control
**Purpose**: Provide intuitive, accessible control for users to switch between dark and light themes, with clear visual indication of current theme state.

**Design Decisions**:
- **MUI IconButton with theme-specific icons**: Uses universally recognized sun/moon iconography, minimal visual weight appropriate for utility control
- **Positioned in AppBar top-right**: Prime location for application-level settings, consistent with modern web application patterns
- **Animated icon transition**: 300ms rotation + scale provides satisfying micro-interaction feedback
- **Tooltip for discoverability**: "Switch to dark mode" / "Switch to light mode" clarifies action for new users
- **Instant theme application**: No loading state needed - theme switches immediately via MUI ThemeProvider

**Component Specifications**:

| Aspect | Specification |
|--------|--------------|
| **Component** | MUI IconButton with conditional icon rendering |
| **Icons** | Light Mode: LightMode (sun icon), Dark Mode: DarkMode (moon icon) |
| **Icon Size** | medium (24x24px default MUI) |
| **Min Touch Target** | 48x48px (enforced by MUI IconButton padding) |
| **Color** | inherit (adapts to current theme text.primary) |
| **Position** | AppBar, right side of Toolbar, after primary navigation |
| **Spacing** | marginLeft: spacing(2) = 16px from preceding element |
| **Elevation** | 0 (flat, part of AppBar surface) |
| **Border Radius** | 50% (circular, MUI IconButton default) |

**Icon Specifications**:

| Theme Mode | Icon Component | Semantic Meaning | Aria Label |
|------------|---------------|------------------|------------|
| **Light Mode Active** | LightMode (sun) | "Currently light, click for dark" | "Switch to dark mode" |
| **Dark Mode Active** | DarkMode (moon) | "Currently dark, click for light" | "Switch to light mode" |

**Interactive States - Light Theme**:

| State | Background | Icon Color | Opacity | Transform | Transition | Cursor |
|-------|-----------|-----------|---------|-----------|------------|--------|
| **Default** | transparent | rgba(0,0,0,0.87) | 1 | scale(1) rotate(0deg) | - | pointer |
| **Hover** | rgba(0,0,0,0.04) | rgba(0,0,0,0.87) | 1 | scale(1.05) | 150ms | pointer |
| **Focus** | rgba(0,0,0,0.04) | rgba(0,0,0,0.87) | 1 | scale(1) | 0ms | pointer |
| **Active** | rgba(0,0,0,0.12) | rgba(0,0,0,0.87) | 1 | scale(0.95) | 100ms | pointer |
| **On Click** | rgba(0,0,0,0.04) | rgba(0,0,0,0.87) | 1 | rotate(180deg) | 300ms ease-in-out | pointer |

**Interactive States - Dark Theme**:

| State | Background | Icon Color | Opacity | Transform | Transition | Cursor |
|-------|-----------|-----------|---------|-----------|------------|--------|
| **Default** | transparent | rgba(255,255,255,0.87) | 1 | scale(1) rotate(0deg) | - | pointer |
| **Hover** | rgba(255,255,255,0.08) | rgba(255,255,255,0.87) | 1 | scale(1.05) | 150ms | pointer |
| **Focus** | rgba(255,255,255,0.08) | rgba(255,255,255,0.87) | 1 | scale(1) | 0ms | pointer |
| **Active** | rgba(255,255,255,0.16) | rgba(255,255,255,0.87) | 1 | scale(0.95) | 100ms | pointer |
| **On Click** | rgba(255,255,255,0.08) | rgba(255,255,255,0.87) | 1 | rotate(180deg) | 300ms ease-in-out | pointer |

**Visual Feedback Mechanism**:
- **Icon Rotation**: 180-degree rotation on click signals state change
- **Scale Pulse**: Subtle 1.05x scale on hover indicates interactivity
- **Immediate Theme Switch**: Entire UI updates simultaneously with click (no loading spinner)
- **Tooltip Indicator**: Shows current action (not current state) - "Switch to [opposite mode]"

**All UI States**:
- **Default**: IconButton visible with current theme icon, ready for interaction
- **Hover**: Background overlay appears, icon scales up slightly
- **Focus (Keyboard)**: Focus ring visible (2px outline, 3:1 contrast), background overlay
- **Active (Click)**: Background darkens, icon scales down momentarily
- **Transitioning**: Icon rotates 180 degrees, theme updates across all components (300ms)
- **Disabled**: Not applicable - theme toggle always interactive

**Accessibility**:

| Aspect | Specification | Compliance |
|--------|--------------|------------|
| **Touch Target** | 48x48px minimum | WCAG 2.1 AA (2.5.5) |
| **Icon Contrast - Light** | rgba(0,0,0,0.87) on #ffffff = 15.8:1 | WCAG AAA (7:1) |
| **Icon Contrast - Dark** | rgba(255,255,255,0.87) on #121212 = 14.9:1 | WCAG AAA (7:1) |
| **Focus Indicator** | 2px outline, 3:1 minimum contrast | WCAG AA (2.4.7) |
| **ARIA Label** | Dynamic: "Switch to dark mode" / "Switch to light mode" | WCAG AA (4.1.2) |
| **Keyboard Navigation** | Tab to focus, Enter/Space to activate | WCAG AA (2.1.1) |
| **Screen Reader** | Icon + aria-label announce action and state | WCAG AA (4.1.3) |
| **Role** | button (native IconButton semantics) | - |

**Responsive Behavior**:

| Breakpoint | Display | Position | Icon Size | Touch Target | Tooltip |
|-----------|---------|----------|-----------|--------------|---------|
| **xs (0-599px)** | visible | AppBar right | 24x24px | 48x48px | Hidden on touch |
| **sm (600-899px)** | visible | AppBar right | 24x24px | 48x48px | Shows on hover |
| **md (900px+)** | visible | AppBar right | 24x24px | 48x48px | Shows on hover |

**Layout Structure**:
```jsx
<AppBar position="sticky" elevation={0}>
  <Toolbar>
    {/* Left: Menu icon, Logo/Title */}
    <Box sx={{ flexGrow: 1 }} />
    {/* Right: Theme toggle */}
    <Tooltip title={themeMode === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}>
      <IconButton
        onClick={handleThemeToggle}
        color="inherit"
        aria-label={themeMode === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
        sx={{
          transition: 'transform 300ms ease-in-out',
          '&:active': {
            transform: 'rotate(180deg)',
          },
        }}
      >
        {themeMode === 'light' ? <DarkMode /> : <LightMode />}
      </IconButton>
    </Tooltip>
  </Toolbar>
</AppBar>
```

**Styling Approach**:
- sx prop for rotation animation and responsive behavior
- MUI theme colors for icon (inherit adapts automatically)
- MUI IconButton default states for hover/focus

**Components Used**:
- IconButton (MUI)
- Tooltip (MUI)
- LightMode icon (MUI @mui/icons-material)
- DarkMode icon (MUI @mui/icons-material)
- Box (for AppBar layout)

**Interaction Pattern**:
1. User views AppBar with sun icon (light mode) or moon icon (dark mode)
2. User hovers - IconButton background appears, icon scales 1.05x, tooltip shows action
3. User clicks/taps:
   - IconButton scales down to 0.95x (active state)
   - Icon rotates 180 degrees over 300ms
   - Theme context updates immediately
   - All UI components re-render with new theme
   - Icon switches to opposite (sun → moon or moon → sun)
   - Tooltip updates to opposite action
4. User can toggle repeatedly without delay or issues

**Theme Switch Technical Flow**:
- Click triggers theme context/state update
- MUI ThemeProvider receives new theme object
- All components consuming theme re-render with new palette
- Icon rotation animation provides visual continuity during re-render
- localStorage updated with new preference (handled by persistence feature)

**Icon Semantic Rationale**:
- **Sun (LightMode)**: Shown when light theme active - represents current state
- **Moon (DarkMode)**: Shown when dark theme active - represents current state
- Alternative pattern (showing destination rather than state) considered but rejected for clarity
- Tooltip resolves any ambiguity by stating action explicitly

**Discoverability Enhancements**:
- Prominent AppBar placement ensures visibility on every page
- Icon-only design saves space while Tooltip provides clarity
- Universal sun/moon iconography requires no cultural translation
- High contrast in both themes ensures icon never "disappears"

### Feature: Onboarding & Assessment Form
**Purpose**: Collect essential user information (age, sport, level, training days, injury history, equipment) through multi-step form to enable personalized training program generation.

**Design Decisions**:
- **Multi-step form with progress indicator**: Reduces cognitive load by showing one section at a time, clear progress indication maintains orientation
- **Inline validation with immediate feedback**: Validates input as user types/blurs, prevents submission errors, improves completion rates
- **Mobile-first vertical form layout**: Single-column form optimized for mobile, expands to two-column on larger screens where appropriate
- **Clear error states with actionable messages**: Specific error messages guide user to correct input, not generic "invalid" messages

**Form Structure**:
- Step 1: Sport Selection (Story 11.1)
- Step 2: Age Information (Story 11.2)
- Step 3: Training Experience Level
- Step 4: Weekly Training Availability
- Step 5: Injury History
- Step 6: Available Equipment
- Step 7: Review & Submit

#### Story 11.1: Sport Selection

**Component Specifications**:

| Aspect | Specification |
|--------|--------------|
| **Component** | MUI Card with CardActionArea for interactive surface |
| **Available Sports** | Football, Cricket (initial implementation) |
| **Layout** | Grid with responsive columns: xs: 1, sm: 2 |
| **Card Dimensions** | Min height: 160px, Full width within grid |
| **Card Spacing** | Grid gap: spacing(3) = 24px |
| **Selection Indicator** | CheckCircle icon (24px) in top-right corner when selected |
| **Touch Target** | Full card surface (minimum 48px height enforced, actual min 160px) |
| **Sport Icons** | SportsFootballIcon (Football), SportsCricketIcon (Cricket) - 48px size |

**Sport Card Structure**:
```jsx
<Card
  elevation={selected ? 3 : 1}
  sx={{
    border: selected ? '2px solid' : '2px solid transparent',
    borderColor: selected ? 'primary.main' : 'transparent',
    transition: 'all 225ms cubic-bezier(0.4, 0, 0.2, 1)',
  }}
>
  <CardActionArea
    onClick={handleSelect}
    aria-label={`Select ${sportName}`}
    sx={{
      minHeight: 160,
      p: 3,
      position: 'relative',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
    }}
  >
    {/* Sport Icon - 48x48px */}
    <Box sx={{ mb: 2 }}>
      <SportIcon
        sx={{
          fontSize: 48,
          color: selected ? 'primary.main' : 'text.secondary',
          transition: 'color 225ms',
        }}
      />
    </Box>

    {/* Sport Name */}
    <Typography
      variant="h6"
      align="center"
      sx={{ color: selected ? 'primary.main' : 'text.primary', transition: 'color 225ms' }}
    >
      {sportName}
    </Typography>

    {/* Selected Indicator */}
    {selected && (
      <CheckCircleIcon
        sx={{
          position: 'absolute',
          top: 16,
          right: 16,
          color: 'primary.main',
          fontSize: 24,
        }}
      />
    )}
  </CardActionArea>
</Card>
```

**Interactive States - Sport Selection Cards (Light Theme)**:

| State | Border | Background | Elevation | Icon Color | Card Text Color | Check Icon | Transition |
|-------|--------|-----------|-----------|------------|-----------------|------------|------------|
| **Default (Unselected)** | 2px transparent | #ffffff | 1 | rgba(0,0,0,0.6) | rgba(0,0,0,0.87) | Hidden | - |
| **Hover (Unselected)** | 2px transparent | #ffffff | 2 | rgba(0,0,0,0.87) | rgba(0,0,0,0.87) | Hidden | 225ms |
| **Focus (Keyboard)** | 2px primary.main outline | #ffffff | 1 | rgba(0,0,0,0.87) | rgba(0,0,0,0.87) | Hidden | 0ms |
| **Selected** | 2px solid #1976d2 | #ffffff | 3 | #1976d2 | #1976d2 | Visible #1976d2 | 225ms |
| **Selected + Hover** | 2px solid #1565c0 | #ffffff | 4 | #1565c0 | #1565c0 | Visible #1565c0 | 225ms |

**Interactive States - Sport Selection Cards (Dark Theme)**:

| State | Border | Background | Elevation | Icon Color | Card Text Color | Check Icon | Transition |
|-------|--------|-----------|-----------|------------|-----------------|------------|------------|
| **Default (Unselected)** | 2px transparent | #1e1e1e | 1 | rgba(255,255,255,0.6) | rgba(255,255,255,0.87) | Hidden | - |
| **Hover (Unselected)** | 2px transparent | #232323 | 2 | rgba(255,255,255,0.87) | rgba(255,255,255,0.87) | Hidden | 225ms |
| **Focus (Keyboard)** | 2px primary.main outline | #1e1e1e | 1 | rgba(255,255,255,0.87) | rgba(255,255,255,0.87) | Hidden | 0ms |
| **Selected** | 2px solid #90caf9 | #1e1e1e | 3 | #90caf9 | #90caf9 | Visible #90caf9 | 225ms |
| **Selected + Hover** | 2px solid #bbdefb | #232323 | 4 | #bbdefb | #bbdefb | Visible #bbdefb | 225ms |

**Validation & Error States**:

| State | Display Condition | Component | Message | Color | Position |
|-------|------------------|-----------|---------|-------|----------|
| **No Error** | Sport selected or form not yet submitted | None | - | - | - |
| **Error - No Selection** | User clicks "Continue" without selecting sport | Alert (severity: error) | "Please select your sport to continue" | error.main | Below cards, margin-top: spacing(3) |
| **Success - Selected** | Sport selected | CheckCircle icon in card | - | primary.main | Top-right corner of selected card |

**All UI States**:
- **Default**: Two sport cards displayed, neither selected, no error message
- **Single Selected**: One card with border, elevated, check icon; other card normal state
- **Hover Unselected**: Card elevation increases to 2, icon darkens
- **Hover Selected**: Selected card elevation increases to 4, border/icon color intensifies
- **Keyboard Focus**: 2px outline on focused card, clear focus ring
- **Error**: Alert banner appears below cards with error message, cards remain interactive
- **Loading**: Not applicable for selection (no async operation)

**Accessibility**:

| Aspect | Specification | Compliance |
|--------|--------------|------------|
| **Card Contrast** | Border 2px solid primary.main (3:1 minimum) | WCAG AA (1.4.11) |
| **Text Contrast - Light** | rgba(0,0,0,0.87) on #ffffff = 15.8:1 | WCAG AAA |
| **Text Contrast - Dark** | rgba(255,255,255,0.87) on #1e1e1e = 14.9:1 | WCAG AAA |
| **Icon Contrast - Selected** | primary.main on paper background > 3:1 | WCAG AA |
| **Touch Target** | Full card min 160px height, full width | WCAG 2.1 AA (2.5.5) |
| **Keyboard Navigation** | Tab to focus cards, Enter/Space to select | WCAG AA (2.1.1) |
| **Screen Reader** | CardActionArea with aria-label: "Select {sport}" | WCAG AA (4.1.2) |
| **Selection Announcement** | aria-live region announces selection change | WCAG AA (4.1.3) |
| **Error Announcement** | Alert component auto-announces error message | WCAG AA (4.1.3) |
| **Focus Management** | Focus moves to error Alert when validation fails (optional) | WCAG AA (2.4.3) |

**Responsive Behavior**:

| Breakpoint | Grid Columns | Card Width | Card Height | Icon Size | Spacing |
|-----------|--------------|------------|-------------|-----------|---------|
| **xs (0-599px)** | 1 column | 100% | min 160px | 48px | gap: 24px |
| **sm (600-899px)** | 2 columns | 50% (minus gap) | min 160px | 48px | gap: 24px |
| **md (900px+)** | 2 columns | 50% (minus gap) | min 160px | 48px | gap: 24px |

**Layout Structure**:
```jsx
<Container maxWidth="md">
  <Box sx={{ py: 4 }}>
    {/* Section Header */}
    <Typography variant="h4" component="h1" gutterBottom align="center">
      Select Your Sport
    </Typography>
    <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 4 }}>
      Choose your primary sport to receive personalized training programs
    </Typography>

    {/* Sport Selection Grid */}
    <Grid container spacing={3} sx={{ mb: 3 }}>
      <Grid size={{ xs: 12, sm: 6 }}>
        <SportCard sport="Football" icon={SportsFootballIcon} selected={selectedSport === 'Football'} onSelect={() => setSelectedSport('Football')} />
      </Grid>
      <Grid size={{ xs: 12, sm: 6 }}>
        <SportCard sport="Cricket" icon={SportsCricketIcon} selected={selectedSport === 'Cricket'} onSelect={() => setSelectedSport('Cricket')} />
      </Grid>
    </Grid>

    {/* Error Alert (conditional) */}
    {error && (
      <Alert severity="error" sx={{ mb: 3 }}>
        Please select your sport to continue
      </Alert>
    )}

    {/* Selection Announcement for Screen Readers */}
    <Box
      role="status"
      aria-live="polite"
      aria-atomic="true"
      sx={{ position: 'absolute', left: -10000, width: 1, height: 1, overflow: 'hidden' }}
    >
      {selectedSport ? `${selectedSport} selected` : ''}
    </Box>
  </Box>
</Container>
```

**Styling Approach**:
- sx prop for responsive card states and selection styling
- MUI theme for colors (primary.main, text colors, elevation)
- Grid v6 size prop for responsive layout
- Transitions for smooth state changes (225ms cubic-bezier)

**Components Used**:
- Card (container for sport options)
- CardActionArea (interactive surface)
- Grid (responsive layout) - v6 with size prop
- Typography (headings, descriptions)
- Alert (error messages)
- Box (layout structure, screen reader announcements)
- CheckCircleIcon (selection indicator)
- SportsFootballIcon, SportsCricketIcon (sport icons from @mui/icons-material)
- Container (page layout wrapper)

**Interaction Pattern**:
1. User views two sport cards (Football, Cricket) in grid layout
2. User hovers over card - elevation increases, icon darkens
3. User clicks/taps card:
   - Selected card: border appears (2px primary), elevation 3, check icon in corner, text/icon turn primary color
   - Previously selected card (if any): returns to default state
   - Screen reader announces: "{Sport} selected"
4. User attempts to proceed without selection:
   - Error Alert appears below cards: "Please select your sport to continue"
   - Alert auto-announces for screen readers
5. User selects sport after error:
   - Error Alert disappears
   - Selection indicated normally
6. User can change selection any time by clicking different card

**Icon Mapping**:
- Football: SportsFootballIcon (@mui/icons-material/SportsFootball)
- Cricket: SportsCricketIcon (@mui/icons-material/SportsCricket)
- Future sports should use appropriate @mui/icons-material sport icons

**Selection State Management**:
- Single state variable tracking selected sport (string | null)
- Click handler: `setSelectedSport(sport)` (no deselect - always one required)
- Alternative pattern allowing deselect: `setSelectedSport(sport === selectedSport ? null : sport)`
- Validation check before proceeding: `if (!selectedSport) { setError(true); return; }`

**Design Rationale**:
- **Card-based selection over radio buttons**: More engaging visual presentation, provides larger touch targets, better suits small number of options (2 choices)
- **Visual selection state (border + elevation + icon)**: Ensures clarity across color blindness and low vision, multiple redundant cues
- **Full-card interactive area**: Maximizes clickable/tappable surface for accessibility and mobile usability
- **Generous spacing (24px)**: Prevents accidental selections on touch devices, provides breathing room
- **Error appears in context**: Below cards rather than distant location improves scannability
- **Screen reader announcements**: Selection changes communicated to non-sighted users via aria-live region
- **Single-select enforced**: Prevents confusion about multiple sport selection, matches acceptance criteria (deselect previous)

#### Story 11.2: Age Input Field

**Component Specifications**:

| Aspect | Specification |
|--------|--------------|
| **Component** | MUI TextField (outlined variant, type="number") |
| **Label** | "Age" |
| **Helper Text (Default)** | "Enter your age (13-100 years)" |
| **Placeholder** | "" (no placeholder, label provides context) |
| **Input Type** | number |
| **Min Value** | 13 |
| **Max Value** | 100 |
| **Required** | Yes |
| **Full Width** | true (mobile), controlled by Grid on desktop |
| **Auto Focus** | true (when step becomes active) |
| **Input Mode** | numeric (mobile keyboard optimization) |

**Validation Rules**:

| Rule | Validation | Error Message | Trigger |
|------|-----------|---------------|---------|
| **Required** | Value must exist | "Age is required" | onBlur, onSubmit |
| **Minimum Age** | Value >= 13 | "You must be at least 13 years old to use this service" | onChange, onBlur |
| **Maximum Age** | Value <= 100 | "Please enter a valid age" | onChange, onBlur |
| **Numeric** | Is valid number | "Please enter a valid age" | onChange |
| **Integer** | No decimals | "Please enter a valid age" | onChange |

**Interactive States - Light Theme**:

| State | Border Color | Border Width | Background | Text Color | Label Color | Helper/Error Text |
|-------|-------------|--------------|-----------|-----------|-------------|------------------|
| **Default** | rgba(0,0,0,0.23) | 1px | transparent | text.primary | text.secondary | text.secondary |
| **Hover** | rgba(0,0,0,0.87) | 1px | transparent | text.primary | text.primary | text.secondary |
| **Focus** | primary.main (#1976d2) | 2px | transparent | text.primary | primary.main | text.secondary |
| **Error** | error.main (#d32f2f) | 2px | transparent | text.primary | error.main | error.main |
| **Error + Focus** | error.main | 2px | transparent | text.primary | error.main | error.main |
| **Disabled** | rgba(0,0,0,0.12) | 1px | rgba(0,0,0,0.04) | text.disabled | text.disabled | text.disabled |
| **Success (Valid)** | success.main (#2e7d32) | 2px | transparent | text.primary | success.main | success.main |

**Interactive States - Dark Theme**:

| State | Border Color | Border Width | Background | Text Color | Label Color | Helper/Error Text |
|-------|-------------|--------------|-----------|-----------|-------------|------------------|
| **Default** | rgba(255,255,255,0.23) | 1px | transparent | text.primary | text.secondary | text.secondary |
| **Hover** | rgba(255,255,255,0.87) | 1px | transparent | text.primary | text.primary | text.secondary |
| **Focus** | primary.main (#90caf9) | 2px | transparent | text.primary | primary.main | text.secondary |
| **Error** | error.main (#ef5350) | 2px | transparent | text.primary | error.main | error.main |
| **Error + Focus** | error.main | 2px | transparent | text.primary | error.main | error.main |
| **Disabled** | rgba(255,255,255,0.12) | 1px | rgba(255,255,255,0.04) | text.disabled | text.disabled | text.disabled |
| **Success (Valid)** | success.main (#66bb6a) | 2px | transparent | text.primary | success.main | success.main |

**Validation Feedback States**:

| Validation State | Visual Indicator | Helper Text | Icon | Timing |
|-----------------|-----------------|-------------|------|--------|
| **Untouched** | Default border | "Enter your age (13-100 years)" | None | Initial |
| **Valid** | Success border (optional) | "Enter your age (13-100 years)" | CheckCircle (optional) | After onBlur with valid input |
| **Age < 13** | Error border | "You must be at least 13 years old to use this service" | Error icon | Immediate on onChange/onBlur |
| **Age > 100** | Error border | "Please enter a valid age" | Error icon | Immediate on onChange/onBlur |
| **Non-numeric** | Error border | "Please enter a valid age" | Error icon | Immediate on onChange |
| **Empty (after touch)** | Error border | "Age is required" | Error icon | onBlur |

**Accessibility**:

| Aspect | Specification | Compliance |
|--------|--------------|------------|
| **Label Association** | htmlFor attribute linking label to input | WCAG AA (1.3.1) |
| **Error Announcement** | aria-describedby links to error message, aria-invalid="true" | WCAG AA (3.3.1, 3.3.3) |
| **Required Indicator** | required attribute, aria-required="true" | WCAG AA (3.3.2) |
| **Helper Text** | aria-describedby for guidance text | WCAG AA (3.3.2) |
| **Keyboard Navigation** | Tab to focus, number keys to input, up/down arrows increment/decrement | WCAG AA (2.1.1) |
| **Touch Target** | 48px minimum height | WCAG AA (2.5.5) |
| **Contrast - Light** | 4.65:1 (label), 15.8:1 (input text) | WCAG AA (1.4.3) |
| **Contrast - Dark** | 6.2:1 (label), 14.9:1 (input text) | WCAG AA (1.4.3) |
| **Error Identification** | Visual (border color) + textual (error message) | WCAG AA (3.3.1) |

**Responsive Behavior**:

| Breakpoint | Layout | Width | Label Placement | Helper Text |
|-----------|--------|-------|----------------|-------------|
| **xs (0-599px)** | Single column | 100% (fullWidth) | Above input (floating) | Below input |
| **sm (600-899px)** | Single column | 100% (fullWidth) | Above input (floating) | Below input |
| **md (900px+)** | Two-column option | 50% (Grid size={6}) | Above input (floating) | Below input |

**Layout Structure**:
```jsx
<Box sx={{ mb: 3 }}>
  <TextField
    id="age"
    name="age"
    label="Age"
    type="number"
    fullWidth
    required
    autoFocus
    inputProps={{
      min: 13,
      max: 100,
      inputMode: 'numeric',
      'aria-describedby': 'age-helper-text',
    }}
    value={formData.age}
    onChange={handleAgeChange}
    onBlur={handleAgeBlur}
    error={!!errors.age}
    helperText={errors.age || "Enter your age (13-100 years)"}
    FormHelperTextProps={{
      id: 'age-helper-text',
    }}
  />
</Box>
```

**Validation Logic Flow**:
1. User focuses field - border changes to focus state
2. User types number:
   - If < 13: Immediate error "You must be at least 13 years old to use this service"
   - If > 100: Immediate error "Please enter a valid age"
   - If non-numeric/decimal: Immediate error "Please enter a valid age"
   - If 13-100: Clear any previous errors, optional success state
3. User blurs field:
   - If empty: Error "Age is required"
   - Re-validate against all rules
4. Form submission:
   - Validate all fields
   - Focus first field with error
   - Display error summary if multiple errors

**Styling Approach**:
- MUI TextField default styling with theme integration
- sx prop for spacing and responsive overrides
- Error states handled by MUI error prop
- Helper text switches between guidance and error messages

**Components Used**:
- TextField (MUI outlined variant)
- Box (for spacing wrapper)
- FormHelperText (built into TextField)

**Integration with Multi-Step Form**:
- Field appears in Step 2 of onboarding flow
- Validation occurs before allowing progression to next step
- Value persists when navigating back/forward through steps
- Form submission blocked if age validation fails
- Progress indicator shows step completion status

**Edge Cases Handled**:
- Copy-paste of invalid values (e.g., text, decimals)
- Leading zeros (e.g., "013" normalized to "13")
- Negative numbers (rejected by type="number" and min validation)
- Extremely large numbers (rejected by max validation)
- Empty submission after touching field
- Browser autofill (validated after autofill)

**Design Rationale**:
- **Number input type**: Provides appropriate mobile keyboard, built-in increment/decrement controls
- **Inline validation**: Immediate feedback improves UX, prevents form submission errors
- **Age range 13-100**: Complies with COPPA (Children's Online Privacy Protection Act), reasonable upper bound
- **Specific error messages**: "at least 13 years old" is more actionable than generic "invalid age"
- **Optional success state**: Can be added for positive reinforcement, not required by acceptance criteria


#### Story 11.3: Experience Level Selection

**Component Specifications**:

| Aspect | Specification |
|--------|--------------|
| **Container** | Box wrapper with mb: 3 for spacing |
| **Layout** | Stack with spacing(3) = 24px between elements |
| **Section Title** | Typography variant h5 (24px, 400 weight) |
| **Section Subtitle** | Typography variant body2 (14px), color text.secondary |
| **Selection Component** | MUI RadioGroup with FormControlLabel per option |
| **Radio Button Size** | medium (24x24px icon, 48x48px touch target) |
| **Radio Button Color** | primary (theme.palette.primary.main) |
| **Option Spacing** | spacing(2) = 16px vertical between options |
| **Validation Message** | FormHelperText, color error.main, with ErrorOutline icon |

**Experience Level Options**:

| Level | Label | Description | Value |
|-------|-------|-------------|-------|
| **Beginner** | "Beginner" | "New to structured training, or returning after extended break (6+ months). Focus on building foundation and learning proper form." | "beginner" |
| **Intermediate** | "Intermediate" | "Consistent training for 6+ months. Comfortable with basic exercises and ready to increase intensity and complexity." | "intermediate" |
| **Advanced** | "Advanced" | "Training consistently for 1+ year with structured programs. Comfortable with high-intensity workouts and complex movements." | "advanced" |

**Interactive States - Light Theme**:

| State | Radio Border | Radio Fill | Label Text | Background | Border | Description |
|-------|--------------|------------|------------|------------|--------|-------------|
| **Unselected Default** | 2px rgba(0,0,0,0.54) | transparent | text.primary | transparent | none | text.secondary |
| **Unselected Hover** | 2px rgba(0,0,0,0.87) | rgba(0,0,0,0.04) | text.primary | rgba(0,0,0,0.02) | none | text.secondary |
| **Selected** | 2px primary.main (#1976d2) | primary.main | text.primary | rgba(25,118,210,0.04) | 1px primary.main | text.primary |
| **Selected Hover** | 2px primary.dark | primary.dark | text.primary | rgba(25,118,210,0.08) | 1px primary.dark | text.primary |
| **Focus (Keyboard)** | 2px primary.main | current fill | text.primary | current bg | 2px outline primary | current |
| **Error State** | 2px error.main | transparent | text.primary | transparent | 1px error.main | error.main |

**Interactive States - Dark Theme**:

| State | Radio Border | Radio Fill | Label Text | Background | Border | Description |
|-------|--------------|------------|------------|------------|--------|-------------|
| **Unselected Default** | 2px rgba(255,255,255,0.7) | transparent | text.primary | transparent | none | text.secondary |
| **Unselected Hover** | 2px rgba(255,255,255,0.87) | rgba(255,255,255,0.08) | text.primary | rgba(255,255,255,0.04) | none | text.secondary |
| **Selected** | 2px primary.main (#90caf9) | primary.main | text.primary | rgba(144,202,249,0.12) | 1px primary.main | text.primary |
| **Selected Hover** | 2px primary.light | primary.light | text.primary | rgba(144,202,249,0.16) | 1px primary.light | text.primary |
| **Focus (Keyboard)** | 2px primary.main | current fill | text.primary | current bg | 2px outline primary | current |
| **Error State** | 2px error.main | transparent | text.primary | transparent | 1px error.main | error.main |

**All UI States**:

| State | Condition | Visual Treatment | User Action |
|-------|-----------|------------------|-------------|
| **Default** | No selection made | All options unselected, neutral state | User can select any option |
| **Selected** | One option chosen | Selected radio filled with primary color, FormControlLabel has subtle background and border | User can change selection |
| **Validation Error** | Next clicked without selection | Error border on FormControl, error message "Please select your experience level" with icon below options | User must select to proceed |
| **Validation Success** | Valid selection made | No error indicators, ready to proceed | User can proceed to next step |
| **Disabled** | Form locked during submission | All options opacity 0.38, cursor not-allowed | User cannot interact |

**Layout Structure**:
```jsx
<Box sx={{ mb: 3 }}>
  <Stack spacing={3}>
    {/* Section Header */}
    <Box>
      <Typography variant="h5" gutterBottom>
        What's your training experience level?
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Select the level that best matches your current fitness and training background
      </Typography>
    </Box>

    {/* Radio Group */}
    <FormControl error={!!errors.experienceLevel} component="fieldset" fullWidth>
      <RadioGroup
        value={formData.experienceLevel}
        onChange={handleExperienceLevelChange}
        name="experience-level"
      >
        {/* Beginner Option */}
        <FormControlLabel
          value="beginner"
          control={<Radio />}
          label={
            <Box sx={{ ml: 1 }}>
              <Typography variant="body1" fontWeight={500}>
                Beginner
              </Typography>
              <Typography variant="body2" color="text.secondary">
                New to structured training, or returning after extended break (6+ months).
                Focus on building foundation and learning proper form.
              </Typography>
            </Box>
          }
          sx={{
            border: formData.experienceLevel === 'beginner' ? '1px solid' : 'none',
            borderColor: 'primary.main',
            backgroundColor: formData.experienceLevel === 'beginner' ? 'action.selected' : 'transparent',
            borderRadius: 1,
            p: 2,
            mb: 2,
            m: 0,
            alignItems: 'flex-start',
            '&:hover': {
              backgroundColor: 'action.hover',
            },
          }}
        />

        {/* Intermediate Option */}
        <FormControlLabel
          value="intermediate"
          control={<Radio />}
          label={
            <Box sx={{ ml: 1 }}>
              <Typography variant="body1" fontWeight={500}>
                Intermediate
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Consistent training for 6+ months. Comfortable with basic exercises
                and ready to increase intensity and complexity.
              </Typography>
            </Box>
          }
          sx={{
            border: formData.experienceLevel === 'intermediate' ? '1px solid' : 'none',
            borderColor: 'primary.main',
            backgroundColor: formData.experienceLevel === 'intermediate' ? 'action.selected' : 'transparent',
            borderRadius: 1,
            p: 2,
            mb: 2,
            m: 0,
            alignItems: 'flex-start',
            '&:hover': {
              backgroundColor: 'action.hover',
            },
          }}
        />

        {/* Advanced Option */}
        <FormControlLabel
          value="advanced"
          control={<Radio />}
          label={
            <Box sx={{ ml: 1 }}>
              <Typography variant="body1" fontWeight={500}>
                Advanced
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Training consistently for 1+ year with structured programs.
                Comfortable with high-intensity workouts and complex movements.
              </Typography>
            </Box>
          }
          sx={{
            border: formData.experienceLevel === 'advanced' ? '1px solid' : 'none',
            borderColor: 'primary.main',
            backgroundColor: formData.experienceLevel === 'advanced' ? 'action.selected' : 'transparent',
            borderRadius: 1,
            p: 2,
            mb: 2,
            m: 0,
            alignItems: 'flex-start',
            '&:hover': {
              backgroundColor: 'action.hover',
            },
          }}
        />
      </RadioGroup>

      {/* Error Message */}
      {errors.experienceLevel && (
        <FormHelperText>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <ErrorOutline fontSize="small" />
            {errors.experienceLevel}
          </Box>
        </FormHelperText>
      )}
    </FormControl>
  </Stack>
</Box>
```

**Responsive Behavior**:

| Breakpoint | Container Padding | Option Layout | Description Text | Radio Size |
|-----------|------------------|---------------|------------------|------------|
| **xs (0-599px)** | spacing(2) = 16px | Single column, full width | Full text visible, line wrap | 24x24px, 48x48px touch |
| **sm (600-899px)** | spacing(3) = 24px | Single column, max 600px | Full text visible | 24x24px, 48x48px touch |
| **md (900px+)** | spacing(4) = 32px | Single column, max 800px | Full text visible | 24x24px, 48x48px touch |

**Accessibility**:

| Aspect | Specification | Compliance |
|--------|--------------|------------|
| **Radio Contrast - Light** | rgba(0,0,0,0.54) border on white = 7.2:1 | WCAG AAA |
| **Radio Contrast - Dark** | rgba(255,255,255,0.7) border on #1e1e1e = 9.8:1 | WCAG AAA |
| **Label Text Contrast** | text.primary meets 15.8:1 (light), 14.9:1 (dark) | WCAG AAA |
| **Focus Indicator** | 2px outline, primary color, 3:1+ contrast | WCAG AA (2.4.7) |
| **Touch Target** | 48x48px minimum for radio buttons | WCAG 2.1 AA (2.5.5) |
| **Keyboard Navigation** | Tab to focus options, Arrow keys to select, Space to toggle | WCAG AA (2.1.1) |
| **Screen Reader** | FormControlLabel provides radio + label association, error announced via aria-describedby | WCAG AA (4.1.3) |
| **Radio Group Role** | radiogroup role (native RadioGroup), aria-required, aria-invalid when error | WCAG AA (4.1.2) |
| **Error Association** | FormHelperText linked via aria-describedby to RadioGroup | WCAG AA (3.3.1) |

**Validation Rules**:
- **Required**: User must select exactly one option before proceeding to next step
- **Trigger**: Validation occurs on Next button click (form-level validation)
- **Error Display**: Error message "Please select your experience level" appears below options with ErrorOutline icon
- **Error Clear**: Selecting any option immediately clears error state
- **Persistence**: Selection persists when user navigates back/forward in stepper

**Components Used**:
- Typography (MUI) - h5 for title, body2 for descriptions
- FormControl, FormControlLabel, FormHelperText (MUI)
- RadioGroup, Radio (MUI)
- Stack, Box (MUI)
- ErrorOutline icon (MUI @mui/icons-material)

**Styling Approach**:
- sx prop for conditional styling based on selection state (border, background)
- MUI theme for colors, spacing, typography
- Dynamic border and background based on selected value
- Hover states via sx pseudo-selectors (&:hover)
- alignItems: 'flex-start' on FormControlLabel to align radio button with first line of text

**Integration with Multi-Step Form**:
- Appears in Step 3 of onboarding flow
- Follows Age Information (Story 11.2), precedes Weekly Training Availability
- Validation integrated with form-level validation (blocks Next button if invalid)
- Value stored in parent form state (formData.experienceLevel)
- Progress indicator shows step completion status
- User can navigate back to revise selection without losing data

**Edge Cases Handled**:
- No initial selection (default state shows all options unselected)
- User clicks Next without selecting (validation error displays)
- User changes selection (previous selection automatically deselected by radio group behavior)
- User navigates back and changes selection (updated value persists forward)
- Form submission while error present (blocked at form level)

**Design Rationale**:
- **Descriptive options over minimal labels**: Experience level is subjective, detailed descriptions reduce ambiguity and help users self-assess accurately
- **Card-like option treatment with borders**: Larger touch targets (entire FormControlLabel clickable), clearer visual grouping, easier to scan and compare options
- **Inline descriptions within labels**: User doesn't need external help/tooltips to understand options, reduces cognitive load
- **Single-column vertical layout**: Reduces horizontal comparison fatigue, easier to read multi-line descriptions top-to-bottom, works better on mobile
- **Subtle selected state**: Primary color border + light background tint signals selection without overwhelming, maintains visual hierarchy with unselected options
- **Radio buttons over buttons/chips**: Standard pattern for mutually exclusive choices, users familiar with interaction model, accessibility built-in


#### Story 11.5: Injury History Reporting

**Component Specifications**:

| Aspect | Specification |
|--------|--------------|
| **Primary Component** | MUI RadioGroup for binary choice |
| **Injury Type Selection** | MUI Chip array with clickable variant, multi-select behavior |
| **Description Input** | MUI TextField (multiline, 3 rows, fullWidth, outlined) |
| **Container Layout** | Stack (spacing: 3, direction: column) |
| **Section Title** | Typography variant: h6 (20px, 500 weight) |
| **Helper Text** | Typography variant: body2 (14px, secondary color) |
| **Chip Dimensions** | height: 32px, padding: 8px 12px, min-touch: 48x48px (with spacing) |
| **Chip Colors** | Default: outlined gray, Selected: filled primary |

**Common Injury Types**:
- Knee injury
- Ankle injury
- Shoulder injury
- Back/spine injury
- Hamstring injury
- Other injury

**Layout Structure**:
```jsx
<Stack spacing={3}>
  <Typography variant="h6">Injury History</Typography>
  <Typography variant="body2" color="text.secondary">
    Do you have any current or recent injuries we should consider?
  </Typography>

  <RadioGroup value={hasInjuries} onChange={handleInjuryChoice}>
    <FormControlLabel
      value="no"
      control={<Radio />}
      label="No injuries"
    />
    <FormControlLabel
      value="yes"
      control={<Radio />}
      label="I have injury history"
    />
  </RadioGroup>

  {hasInjuries === 'yes' && (
    <Stack spacing={2}>
      <Typography variant="subtitle2">
        Select injury types (optional)
      </Typography>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {injuryTypes.map(type => (
          <Chip
            key={type}
            label={type}
            onClick={() => toggleInjuryType(type)}
            color={selectedTypes.includes(type) ? 'primary' : 'default'}
            variant={selectedTypes.includes(type) ? 'filled' : 'outlined'}
          />
        ))}
      </Box>

      <TextField
        label="Injury details (optional)"
        placeholder="Describe your injury, when it occurred, and any limitations..."
        multiline
        rows={3}
        fullWidth
        value={injuryDescription}
        onChange={handleDescriptionChange}
        helperText="This helps us customize your program around your recovery needs"
      />
    </Stack>
  )}
</Stack>
```

**Interactive States - Radio Buttons**:

| State | Background | Border | Icon Color | Cursor | Transition |
|-------|-----------|--------|------------|--------|------------|
| **Unchecked Default** | transparent | 2px rgba(0,0,0,0.54) | rgba(0,0,0,0.54) | pointer | - |
| **Unchecked Hover** | rgba(0,0,0,0.04) | 2px rgba(0,0,0,0.87) | rgba(0,0,0,0.87) | pointer | 150ms |
| **Checked Default** | primary.main | 2px primary.main | #ffffff | pointer | 150ms |
| **Checked Hover** | primary.dark | 2px primary.dark | #ffffff | pointer | 150ms |
| **Focus** | transparent | 2px outline primary.main | current | pointer | 0ms |

**Interactive States - Chips**:

| State | Background | Border | Text Color | Elevation | Cursor | Transition |
|-------|-----------|--------|------------|-----------|--------|------------|
| **Unselected Default** | transparent | 1px rgba(0,0,0,0.23) | text.primary | 0 | pointer | - |
| **Unselected Hover** | rgba(0,0,0,0.04) | 1px rgba(0,0,0,0.87) | text.primary | 0 | pointer | 150ms |
| **Selected Default** | primary.main | none | primary.contrastText | 0 | pointer | 150ms |
| **Selected Hover** | primary.dark | none | primary.contrastText | 1 | pointer | 150ms |
| **Focus** | current | 2px outline primary.light | current | current | pointer | 0ms |

**Interactive States - TextField**:

| State | Background | Border | Label Color | Text Color | Helper Text | Transition |
|-------|-----------|--------|-------------|------------|-------------|------------|
| **Default** | transparent | 1px rgba(0,0,0,0.23) | text.secondary | text.primary | text.secondary | - |
| **Hover** | transparent | 1px rgba(0,0,0,0.87) | text.primary | text.primary | text.secondary | 225ms |
| **Focus** | transparent | 2px primary.main | primary.main | text.primary | text.secondary | 0ms |
| **Filled** | transparent | 1px rgba(0,0,0,0.23) | primary.main | text.primary | text.secondary | - |

**All UI States**:
- **Default (no selection)**: Both radio options visible, no expansion, proceed enabled but no injury data captured
- **No injuries selected**: "No injuries" radio checked, no expansion shown, empty injury data stored
- **Injuries indicated**: "I have injury history" radio checked, expanded section shows chips and text field
- **Injury types selected**: Chips show filled primary variant for selected types, outlined default for unselected
- **Description provided**: TextField shows user input, character count if limits applied
- **Empty expansion**: User selects "I have injury history" but provides no details - valid state, allows proceed

**Accessibility**:

| Aspect | Specification | Compliance |
|--------|--------------|------------|
| **Radio Contrast** | Checked: 4.65:1, Unchecked: 7.7:1 | WCAG AA |
| **Chip Text Contrast** | Selected: 4.65:1, Unselected: 15.8:1 | WCAG AA |
| **Chip Touch Target** | 48x48px (32px height + 8px gap = 40px, 48x48px with padding) | WCAG AA 2.5.5 |
| **Focus Indicators** | 2px outline, 3:1 minimum contrast | WCAG AA 2.4.7 |
| **Keyboard Navigation** | Tab through radio → chips → text field, Enter/Space to toggle | WCAG AA 2.1.1 |
| **Screen Reader** | Radio group labeled "Injury History", chips announce selected/unselected state | WCAG AA 4.1.2 |
| **ARIA Labels** | RadioGroup aria-label, Chips aria-pressed state | WCAG AA 4.1.3 |
| **Error Feedback** | Not applicable - all choices valid | - |

**Responsive Behavior**:

| Breakpoint | Radio Layout | Chip Layout | Chip Min-Width | TextField Rows | Spacing |
|-----------|-------------|-------------|----------------|----------------|---------|
| **xs (0-599px)** | Vertical stack | Flex wrap, 2-3 per row | 100px | 3 | spacing(2) |
| **sm (600-899px)** | Vertical stack | Flex wrap, 3-4 per row | 120px | 3 | spacing(2) |
| **md (900px+)** | Vertical stack | Flex wrap, 4-5 per row | 120px | 4 | spacing(3) |

**Validation Rules**:
- **Radio selection**: Optional (can proceed without selection, treated as "no injuries")
- **Injury types**: Optional even when "I have injury history" selected
- **Description**: Optional, no character limits enforced in UI (backend may apply reasonable limits like 500 chars)
- **Multi-select chips**: No maximum selection limit
- **State consistency**: Switching from "yes" to "no" clears selected types and description

**Data Capture Format**:
```typescript
{
  hasInjuries: boolean,
  injuryTypes: string[], // Array of selected injury type strings
  injuryDescription: string | null // Free-text description or null
}
```

**Styling Approach**:
- sx prop for responsive chip layout (flexWrap, gap)
- MUI theme for all colors, spacing, and typography
- RadioGroup and FormControlLabel for accessible radio behavior
- Chip color and variant props for selection states
- TextField with helperText for user guidance

**Components Used**:
- Stack (layout)
- Typography (labels, helper text)
- RadioGroup, Radio, FormControlLabel (binary choice)
- Chip (injury type selection)
- TextField (multiline description)
- Box (chip container with flex layout)

**Interaction Pattern**:
1. User views section with two radio options
2. User selects "No injuries" → radio checked, no expansion, data saved as empty
3. OR User selects "I have injury history" → radio checked, expansion appears with animation (225ms slide down)
4. User clicks chips to toggle injury types → chips transition to filled primary variant
5. User types in description field → standard text input behavior
6. User switches back to "No injuries" → expansion collapses (225ms slide up), selections cleared
7. Form can be submitted at any state - all choices are valid

**Conditional Display Logic**:
- Expansion section (chips + text field) only renders when `hasInjuries === 'yes'`
- Uses MUI Collapse or conditional rendering with slide transition
- Maintains expansion state until user explicitly changes radio selection
- Cleared data is not recoverable if user switches back and forth (fresh state each expansion)

**User Guidance**:
- Helper text clarifies purpose: "Do you have any current or recent injuries we should consider?"
- Chip section labeled: "Select injury types (optional)"
- TextField placeholder: "Describe your injury, when it occurred, and any limitations..."
- TextField helper text: "This helps us customize your program around your recovery needs"
- "Optional" labels prevent user anxiety about skipping details

**Integration with Onboarding Flow**:
- Appears as step in multi-step onboarding form (Step 5 of 7)
- Follows training availability selection, precedes equipment selection
- Progress indicator shows user position in flow
- Next button enabled regardless of injury detail provided (non-blocking)
- Data persisted when user navigates to next step

**Design Rationale**:
- **Two-step pattern**: Binary choice first reduces cognitive load, expansion only when needed prevents overwhelming users with no injuries
- **Chip selection**: Faster than dropdowns, visual feedback immediate, common injuries covered
- **Optional details**: Respects user privacy, allows quick completion, but provides option for specificity
- **Multi-select chips**: Users often have multiple injuries or injury-prone areas
- **Collapsible expansion**: Keeps form compact when not applicable, progressive disclosure pattern


#### Story 11.6: Equipment Selection

**Component Specifications**:

| Aspect | Specification |
|--------|--------------|
| **Primary Component** | MUI Chip (clickable variant with icon) |
| **Container** | Stack with flexbox wrapping |
| **Section Title** | Typography variant h6 (20px, 500 weight) |
| **Help Text** | Typography variant body2 (14px, secondary color) |
| **Chip Size** | medium (32px height, 8px 12px padding) |
| **Chip Spacing** | 8px gap between chips (spacing(1)) |
| **Min Touch Target** | 48x48px (achieved via padding around chips) |
| **Icons** | CheckCircle (selected), Add (unselected) |
| **Validation Message** | Alert severity="error" |

**Equipment Categories & Items**:

| Category | Individual Items |
|----------|-----------------|
| **No Equipment** | Bodyweight exercises only |
| **Basic Equipment** | Dumbbells, Resistance Bands, Yoga Mat, Jump Rope |
| **Full Gym** | Barbells, Squat Rack, Bench Press, Cable Machine, Leg Press, Rowing Machine, Treadmill |

**Equipment Data**:
```typescript
const equipmentItems = [
  // Basic Equipment
  { id: 'dumbbells', label: 'Dumbbells', category: 'basic' },
  { id: 'resistance-bands', label: 'Resistance Bands', category: 'basic' },
  { id: 'yoga-mat', label: 'Yoga Mat', category: 'basic' },
  { id: 'jump-rope', label: 'Jump Rope', category: 'basic' },

  // Full Gym Equipment
  { id: 'barbells', label: 'Barbells', category: 'gym' },
  { id: 'squat-rack', label: 'Squat Rack', category: 'gym' },
  { id: 'bench-press', label: 'Bench Press', category: 'gym' },
  { id: 'cable-machine', label: 'Cable Machine', category: 'gym' },
  { id: 'leg-press', label: 'Leg Press', category: 'gym' },
  { id: 'rowing-machine', label: 'Rowing Machine', category: 'gym' },
  { id: 'treadmill', label: 'Treadmill', category: 'gym' },
];
```

**Selection Behavior**:
- Category click selects all items in that category
- Category click again deselects all items in category
- Individual items toggle independently
- All items selected automatically selects category
- Any item deselected automatically deselects category
- "No Equipment" mutually exclusive with all others
- Selecting equipment after "No Equipment" clears "No Equipment"

**Interactive States - Light Theme**:

| Component | State | Background | Border | Icon Color | Text Color | Transition |
|-----------|-------|-----------|--------|-----------|-----------|------------|
| **Chip (Unselected)** | Default | rgba(0,0,0,0.08) | none | rgba(0,0,0,0.54) | rgba(0,0,0,0.87) | - |
| | Hover | rgba(0,0,0,0.12) | none | rgba(0,0,0,0.54) | rgba(0,0,0,0.87) | 150ms |
| | Focus | rgba(0,0,0,0.08) | 2px primary.main | rgba(0,0,0,0.54) | rgba(0,0,0,0.87) | 0ms |
| **Chip (Selected)** | Default | primary.main (#1976d2) | none | #ffffff | #ffffff | - |
| | Hover | primary.dark (#1565c0) | none | #ffffff | #ffffff | 150ms |
| | Focus | primary.main | 2px primary.light | #ffffff | #ffffff | 0ms |

**Interactive States - Dark Theme**:

| Component | State | Background | Border | Icon Color | Text Color | Transition |
|-----------|-------|-----------|--------|-----------|-----------|------------|
| **Chip (Unselected)** | Default | rgba(255,255,255,0.08) | none | rgba(255,255,255,0.7) | rgba(255,255,255,0.87) | - |
| | Hover | rgba(255,255,255,0.12) | none | rgba(255,255,255,0.7) | rgba(255,255,255,0.87) | 150ms |
| | Focus | rgba(255,255,255,0.08) | 2px primary.main | rgba(255,255,255,0.7) | rgba(255,255,255,0.87) | 0ms |
| **Chip (Selected)** | Default | primary.main (#90caf9) | none | rgba(0,0,0,0.87) | rgba(0,0,0,0.87) | - |
| | Hover | primary.light (#bbdefb) | none | rgba(0,0,0,0.87) | rgba(0,0,0,0.87) | 150ms |
| | Focus | primary.main | 2px primary.dark | rgba(0,0,0,0.87) | rgba(0,0,0,0.87) | 0ms |

**All UI States**:
- **Default**: Chips visible, none selected, no error
- **Partial Selection**: Some chips selected (primary), others unselected (default)
- **Category Selected**: Category chip + all items in category selected
- **No Equipment Selected**: Only "No Equipment" selected, all others unselected
- **Validation Error**: Alert appears with "Please indicate your available equipment"
- **Valid**: At least one option selected, no error

**Accessibility**:

| Aspect | Specification | Compliance |
|--------|--------------|------------|
| **Touch Target** | 48x48px minimum | WCAG 2.1 AA (2.5.5) |
| **Chip Contrast - Unselected Light** | 14.2:1 | WCAG AAA (7:1) |
| **Chip Contrast - Selected Light** | 4.65:1 | WCAG AA (4.5:1) |
| **Chip Contrast - Unselected Dark** | 13.8:1 | WCAG AAA (7:1) |
| **Chip Contrast - Selected Dark** | 11.2:1 | WCAG AAA (7:1) |
| **Focus Indicator** | 2px outline, 3:1 contrast | WCAG AA (2.4.7) |
| **ARIA Label** | Includes selection state | WCAG AA (4.1.2) |
| **ARIA Live** | Error Alert announced | WCAG AA (4.1.3) |
| **Keyboard** | Tab + Enter/Space | WCAG AA (2.1.1) |
| **Screen Reader** | "Dumbbells, selected" | WCAG AA (1.3.1) |

**Responsive Behavior**:

| Breakpoint | Chips Per Row | Chip Size | Spacing |
|-----------|---------------|-----------|---------|
| **xs (0-599px)** | 2-3 | medium (32px) | 8px |
| **sm (600-899px)** | 4-5 | medium (32px) | 8px |
| **md (900px+)** | 6-8 | medium (32px) | 8px |

**Layout Structure**:
```jsx
<Box sx={{ mb: 4 }}>
  <Typography variant="h6" sx={{ mb: 1 }}>
    Available Equipment
  </Typography>
  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
    Select all equipment you have access to. You can choose multiple items.
  </Typography>

  <Box sx={{ mb: 2 }}>
    <Typography variant="subtitle2" sx={{ mb: 1 }}>Quick Categories</Typography>
    <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 1 }}>
      <Chip
        icon={noEquipmentSelected ? <CheckCircle /> : <Add />}
        label="No Equipment"
        onClick={handleNoEquipmentClick}
        color={noEquipmentSelected ? "primary" : "default"}
        clickable
        aria-label={`No Equipment, ${noEquipmentSelected ? 'selected' : 'not selected'}`}
      />
      <Chip
        icon={basicSelected ? <CheckCircle /> : <Add />}
        label="Basic Equipment"
        onClick={handleBasicClick}
        color={basicSelected ? "primary" : "default"}
        clickable
        aria-label={`Basic Equipment, ${basicSelected ? 'selected' : 'not selected'}`}
      />
      <Chip
        icon={gymSelected ? <CheckCircle /> : <Add />}
        label="Full Gym"
        onClick={handleFullGymClick}
        color={gymSelected ? "primary" : "default"}
        clickable
        aria-label={`Full Gym, ${gymSelected ? 'selected' : 'not selected'}`}
      />
    </Stack>
  </Box>

  <Box>
    <Typography variant="subtitle2" sx={{ mb: 1 }}>Specific Equipment</Typography>
    <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 1 }}>
      {equipmentItems.map((item) => (
        <Chip
          key={item.id}
          icon={selectedEquipment.includes(item.id) ? <CheckCircle /> : <Add />}
          label={item.label}
          onClick={() => handleEquipmentToggle(item.id)}
          color={selectedEquipment.includes(item.id) ? "primary" : "default"}
          clickable
          aria-label={`${item.label}, ${selectedEquipment.includes(item.id) ? 'selected' : 'not selected'}`}
        />
      ))}
    </Stack>
  </Box>

  {error && (
    <Alert severity="error" sx={{ mt: 2 }} role="alert">
      Please indicate your available equipment
    </Alert>
  )}
</Box>
```

**Components Used**: Chip, Stack, Box, Typography, Alert, CheckCircle icon, Add icon

**Interaction Pattern**:
1. User views category and individual equipment chips
2. User clicks "Basic Equipment" - all basic items select
3. User clicks individual "Barbells" - chip selects, "Full Gym" stays unselected
4. User clicks "No Equipment" - all previous selections clear
5. Attempting to proceed without selection shows error
6. Selecting any equipment dismisses error

**Design Rationale**:
- **Multi-select chips**: Flexible equipment specification, clear visual state
- **Category shortcuts**: Reduces clicks for common scenarios
- **CheckCircle vs Add icons**: Clear distinction beyond color (color blind safe)
- **Intelligent category state**: Auto-selects/deselects based on items
- **"No Equipment" exclusivity**: Prevents contradictory selections
- **Wrapping layout**: Adapts to screen sizes

### Feature: Equipment Assessment Single Selection (Feature #19)

**Purpose**: Enable users to specify their available training equipment through a single-selection interface that clearly indicates only one option can be selected, providing accurate equipment information for personalized training program generation.

**Design Decisions**:
- **Radio button pattern with descriptive cards**: Uses universally understood single-select pattern, card-based layout provides larger touch targets and clearer visual grouping than traditional radio buttons
- **Explicit level descriptions**: Each equipment level includes clear, specific descriptions (e.g., "No equipment - bodyweight only") to help users self-identify accurately
- **Visual deselection feedback**: When user selects a different option, previously selected option automatically deselects visually with smooth transitions
- **Required field indication**: Interface clearly indicates equipment selection is required for form progression
- **Consistent with onboarding patterns**: Follows existing single-select pattern from Feature #11 Sport Selection (Story 11.1)

#### Story 19.1: Design Single Selection Equipment Assessment

**Component Specifications**:

| Aspect | Specification |
|--------|--------------|
| **Primary Component** | MUI RadioGroup with FormControlLabel per option |
| **Container** | Box wrapper with mb: 3 for spacing |
| **Layout** | Stack with spacing(3) = 24px between elements |
| **Section Title** | Typography variant h5 (24px, 400 weight) |
| **Section Subtitle** | Typography variant body2 (14px), color text.secondary |
| **Radio Button Size** | medium (24x24px icon, 48x48px touch target) |
| **Radio Button Color** | primary (theme.palette.primary.main) |
| **Card Styling** | FormControlLabel with conditional border and background |
| **Option Spacing** | spacing(2) = 16px vertical between options |
| **Required Indicator** | Typography with asterisk and color error.main |
| **Validation Message** | FormHelperText, color error.main, with ErrorOutline icon |

**Equipment Level Options**:

| Level | Label | Description | Value | Primary Use |
|-------|-------|-------------|-------|------------|
| **No Equipment** | "No Equipment" | "Bodyweight only - no equipment, weights, or machines available. Focus on exercises using body weight, gravity, and gravity resistance." | "no-equipment" | Minimal/home setup |
| **Basic Equipment** | "Basic Equipment" | "Minimal gear - some weights or simple equipment (dumbbells, resistance bands, basic furniture). Transitional setup with limited options." | "basic-equipment" | Home or basic gym |
| **Full Gym** | "Full Gym" | "Complete equipment access - all common gym equipment including barbells, machines, cables, accessories. Unlimited exercise options." | "full-gym" | Full commercial gym |

**Interactive States - Light Theme**:

| State | Radio Border | Radio Fill | Label Text | Option Background | Option Border | Description Color | Elevation |
|-------|--------------|------------|------------|------------------|---------------|------------------|-----------|
| **Unselected Default** | 2px rgba(0,0,0,0.54) | transparent | text.primary | transparent | none | text.secondary | 0 |
| **Unselected Hover** | 2px rgba(0,0,0,0.87) | rgba(0,0,0,0.04) | text.primary | rgba(0,0,0,0.02) | none | text.secondary | 0 |
| **Selected** | 2px primary.main (#1976d2) | primary.main | text.primary | rgba(25,118,210,0.04) | 1px primary.main | text.primary | 0 |
| **Selected Hover** | 2px primary.dark | primary.dark | text.primary | rgba(25,118,210,0.08) | 1px primary.dark | text.primary | 1 |
| **Focus (Keyboard)** | 2px primary.main | current fill | text.primary | current bg | 2px outline primary | current | 0 |
| **Error State** | 2px error.main | transparent | text.primary | transparent | 1px error.main | error.main | 0 |
| **Disabled** | 2px rgba(0,0,0,0.26) | rgba(0,0,0,0.26) | rgba(0,0,0,0.38) | rgba(0,0,0,0.02) | none | rgba(0,0,0,0.38) | 0 |

**Interactive States - Dark Theme**:

| State | Radio Border | Radio Fill | Label Text | Option Background | Option Border | Description Color | Elevation |
|-------|--------------|------------|------------|------------------|---------------|------------------|-----------|
| **Unselected Default** | 2px rgba(255,255,255,0.7) | transparent | text.primary | transparent | none | text.secondary | 0 |
| **Unselected Hover** | 2px rgba(255,255,255,0.87) | rgba(255,255,255,0.08) | text.primary | rgba(255,255,255,0.04) | none | text.secondary | 0 |
| **Selected** | 2px primary.main (#90caf9) | primary.main | text.primary | rgba(144,202,249,0.12) | 1px primary.main | text.primary | 0 |
| **Selected Hover** | 2px primary.light | primary.light | text.primary | rgba(144,202,249,0.16) | 1px primary.light | text.primary | 1 |
| **Focus (Keyboard)** | 2px primary.main | current fill | text.primary | current bg | 2px outline primary | current | 0 |
| **Error State** | 2px error.main | transparent | text.primary | transparent | 1px error.main | error.main | 0 |
| **Disabled** | 2px rgba(255,255,255,0.3) | rgba(255,255,255,0.3) | rgba(255,255,255,0.38) | rgba(255,255,255,0.02) | none | rgba(255,255,255,0.38) | 0 |

**All UI States**:

| State | Condition | Visual Treatment | User Action | Next Step |
|-------|-----------|------------------|-------------|-----------|
| **Default (No Selection)** | Page load, or after deselecting all | All three options visible with unselected radio buttons, equal visual weight, no borders | User can select any option | Selection changes option appearance |
| **Single Selected** | User clicks one option | Selected option has primary border, subtle background, radio filled with primary color; other options return to default appearance | User can change selection by clicking different option | Previous selection deselected, new one selected |
| **Required Field Unmet** | User attempts to proceed without selection | Error message appears below options: "Equipment level is required" with ErrorOutline icon, form submission blocked | User must select option to proceed | Selecting any option clears error |
| **Error Dismissed** | User selects equipment after seeing error | Error message disappears, selected option styled normally with border and background | User can proceed to next step | Form submission allowed |
| **Disabled/Locked** | Form submission in progress or page disabled | All radio buttons opacity 0.38, cursor not-allowed, no hover states responsive | User cannot interact | State resolves, options re-enable |

**Layout Structure**:
```jsx
<Box sx={{ mb: 3 }}>
  <Stack spacing={3}>
    {/* Section Header with Required Indicator */}
    <Box>
      <Typography variant="h5" gutterBottom>
        What equipment do you have available?
        <Typography component="span" sx={{ color: 'error.main', ml: 0.5 }}>*</Typography>
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Select the equipment level that best matches your training setup
      </Typography>
    </Box>

    {/* Radio Group */}
    <FormControl error={!!errors.equipmentLevel} component="fieldset" fullWidth>
      <RadioGroup
        value={formData.equipmentLevel}
        onChange={handleEquipmentChange}
        name="equipment-level"
      >
        {/* No Equipment Option */}
        <FormControlLabel
          value="no-equipment"
          control={<Radio />}
          label={
            <Box sx={{ ml: 1 }}>
              <Typography variant="body1" fontWeight={500}>
                No Equipment
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Bodyweight only - no equipment, weights, or machines available.
                Focus on exercises using body weight, gravity, and gravity resistance.
              </Typography>
            </Box>
          }
          sx={{
            border: formData.equipmentLevel === 'no-equipment' ? '1px solid' : 'none',
            borderColor: 'primary.main',
            backgroundColor: formData.equipmentLevel === 'no-equipment' ? 'action.selected' : 'transparent',
            borderRadius: 1,
            p: 2,
            mb: 2,
            m: 0,
            alignItems: 'flex-start',
            transition: 'all 225ms cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              backgroundColor: formData.equipmentLevel === 'no-equipment' ? 'action.selected' : 'action.hover',
            },
          }}
        />

        {/* Basic Equipment Option */}
        <FormControlLabel
          value="basic-equipment"
          control={<Radio />}
          label={
            <Box sx={{ ml: 1 }}>
              <Typography variant="body1" fontWeight={500}>
                Basic Equipment
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Minimal gear - some weights or simple equipment (dumbbells, resistance bands, basic furniture).
                Transitional setup with limited options.
              </Typography>
            </Box>
          }
          sx={{
            border: formData.equipmentLevel === 'basic-equipment' ? '1px solid' : 'none',
            borderColor: 'primary.main',
            backgroundColor: formData.equipmentLevel === 'basic-equipment' ? 'action.selected' : 'transparent',
            borderRadius: 1,
            p: 2,
            mb: 2,
            m: 0,
            alignItems: 'flex-start',
            transition: 'all 225ms cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              backgroundColor: formData.equipmentLevel === 'basic-equipment' ? 'action.selected' : 'action.hover',
            },
          }}
        />

        {/* Full Gym Option */}
        <FormControlLabel
          value="full-gym"
          control={<Radio />}
          label={
            <Box sx={{ ml: 1 }}>
              <Typography variant="body1" fontWeight={500}>
                Full Gym
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Complete equipment access - all common gym equipment including barbells, machines,
                cables, accessories. Unlimited exercise options.
              </Typography>
            </Box>
          }
          sx={{
            border: formData.equipmentLevel === 'full-gym' ? '1px solid' : 'none',
            borderColor: 'primary.main',
            backgroundColor: formData.equipmentLevel === 'full-gym' ? 'action.selected' : 'transparent',
            borderRadius: 1,
            p: 2,
            mb: 2,
            m: 0,
            alignItems: 'flex-start',
            transition: 'all 225ms cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              backgroundColor: formData.equipmentLevel === 'full-gym' ? 'action.selected' : 'action.hover',
            },
          }}
        />
      </RadioGroup>

      {/* Error Message */}
      {errors.equipmentLevel && (
        <FormHelperText sx={{ mt: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <ErrorOutline fontSize="small" />
            {errors.equipmentLevel}
          </Box>
        </FormHelperText>
      )}

      {/* Required Field Indicator */}
      <FormHelperText sx={{ mt: 2 }}>
        * Required field
      </FormHelperText>
    </FormControl>
  </Stack>
</Box>
```

**Responsive Behavior**:

| Breakpoint | Container Padding | Option Layout | Description Text | Label Size | Radio Size |
|-----------|------------------|---------------|------------------|------------|------------|
| **xs (0-599px)** | spacing(2) = 16px | Single column, full width | Full text visible, line wrap | body1 | 24x24px, 48x48px touch |
| **sm (600-899px)** | spacing(3) = 24px | Single column, max 600px | Full text visible | body1 | 24x24px, 48x48px touch |
| **md (900px+)** | spacing(4) = 32px | Single column, max 800px | Full text visible | body1 | 24x24px, 48x48px touch |

**Accessibility**:

| Aspect | Specification | Compliance |
|--------|--------------|------------|
| **Radio Contrast - Light** | rgba(0,0,0,0.54) border on white = 7.2:1 | WCAG AAA |
| **Radio Contrast - Dark** | rgba(255,255,255,0.7) border on #1e1e1e = 9.8:1 | WCAG AAA |
| **Label Text Contrast** | text.primary meets 15.8:1 (light), 14.9:1 (dark) | WCAG AAA |
| **Description Text Contrast** | text.secondary meets 7.7:1 (light), 7.4:1 (dark) | WCAG AAA |
| **Focus Indicator** | 2px outline, primary color, 3:1+ contrast | WCAG AA (2.4.7) |
| **Touch Target** | 48x48px minimum for radio buttons | WCAG 2.1 AA (2.5.5) |
| **Keyboard Navigation** | Tab to focus options, Arrow keys to select, Space to confirm | WCAG AA (2.1.1) |
| **Screen Reader** | FormControlLabel provides radio + label association, descriptions read sequentially | WCAG AA (4.1.3) |
| **Radio Group Role** | radiogroup role (native RadioGroup), aria-required="true", aria-invalid when error | WCAG AA (4.1.2) |
| **Error Association** | FormHelperText linked via aria-describedby to RadioGroup | WCAG AA (3.3.1) |
| **Required Indicator** | Asterisk with aria-label or explicit "Required field" text | WCAG AA (3.3.2) |
| **Selection Announcement** | aria-live region announces selection change (handled by RadioGroup) | WCAG AA (4.1.3) |

**Validation Rules**:
- **Required**: User must select exactly one equipment level before proceeding
- **Trigger**: Validation occurs on form submission or Next button click
- **Error Display**: Error message "Equipment level is required" appears below options with ErrorOutline icon
- **Error Clear**: Selecting any option immediately clears error state
- **Persistence**: Selection persists when user navigates back/forward in stepper
- **Auto-deselect**: When user selects different option, previous selection automatically deselects (radio group behavior)

**Validation Error States**:

| Error Scenario | Error Message | Display Location | Visual Treatment | Clear Condition |
|----------------|---------------|------------------|------------------|-----------------|
| **No Selection** | "Equipment level is required" | Below RadioGroup with FormHelperText | Red border on FormControl, ErrorOutline icon | Selecting any option |
| **Form Submission Blocked** | (message displays above form) | Alert or focused error area | Error state visible at field level | Fixing validation error |

**Components Used**:
- Typography (MUI) - h5 for title, body2 for descriptions, body1 for option labels
- FormControl, FormControlLabel, FormHelperText (MUI)
- RadioGroup, Radio (MUI)
- Stack, Box (MUI)
- ErrorOutline icon (MUI @mui/icons-material)

**Styling Approach**:
- sx prop for conditional styling based on selection state (border, background)
- MUI theme for colors, spacing, typography
- Dynamic border and background based on selected value
- Hover states via sx pseudo-selectors (&:hover)
- transition property for smooth state changes (225ms cubic-bezier)
- alignItems: 'flex-start' on FormControlLabel to align radio button with first line of text

**Integration with Multi-Step Form**:
- Appears in Step 6 of onboarding flow (after Injury History, before Review & Submit)
- Follows existing onboarding pattern from Feature #11 (Sport Selection, Experience Level)
- Validation integrated with form-level validation (blocks Next button if invalid)
- Value stored in parent form state (formData.equipmentLevel)
- Progress indicator shows step completion status
- User can navigate back to revise selection without losing data
- Story 19.2 and 19.3 (conditional follow-up for basic equipment) will appear below this section

**Edge Cases Handled**:
- No initial selection (default state shows all options unselected)
- User clicks Next without selecting (validation error displays)
- User changes selection (previous selection automatically deselected by radio group behavior)
- User navigates back and changes selection (updated value persists forward)
- Form submission while error present (blocked at form level)
- Error state persists until user selects option
- User selects same option twice (no re-render, selection remains stable)

**Design Rationale**:
- **Radio buttons with card-like treatment**: Implements standard single-select pattern users are familiar with, card-based presentation with borders and backgrounds makes selections more visually prominent than traditional radio buttons
- **Explicit equipment descriptions over icons**: Equipment levels are concrete but may be ambiguous without context (what exactly is "basic"?), detailed descriptions reduce confusion and help users self-assess accurately
- **Three-level taxonomy**: Covers common scenarios (no gym access, limited home setup, full commercial gym), matches industry-standard equipment classification
- **Clear required field indication**: Asterisk + helper text ensures users understand this is mandatory
- **Consistent with onboarding patterns**: Uses same single-select pattern, card styling, and error handling as Sport Selection (Story 11.1), reduces cognitive load through design consistency
- **Inline descriptions within labels**: User doesn't need external help/tooltips to understand options, reduces cognitive load
- **Single-column vertical layout**: Reduces horizontal comparison fatigue, easier to read multi-line descriptions top-to-bottom, works better on mobile
- **Smooth transitions**: 225ms transitions make state changes smooth and less jarring
- **Accessible error handling**: Error message clear and associated with field via aria-describedby, keyboard navigable

**Future Feature Integration**:
- Story 19.2 will add conditional follow-up section that appears when "basic-equipment" selected
- Story 19.3 will add detailed equipment item selection within that follow-up section
- Backend validation (Story 19.7) will enforce single selection at API level
- Conditional logic ensures follow-up only displays for "basic-equipment" level

#### Story 19.2: Design Basic Equipment Follow-up Prompt

**Purpose**: Create a conditional prompt section that appears immediately after "basic equipment" is selected, guiding users to specify their individual equipment items, establishing visual connection to the equipment selection above.

**Component Specifications**:

| Aspect | Specification |
|--------|--------------|
| **Container** | Box with conditional rendering (only visible when equipmentLevel === 'basic-equipment') |
| **Wrapper Styling** | mt: 3, mb: 3, border: '1px solid', borderColor: 'divider', borderRadius: 2, p: 3, backgroundColor: 'action.selected' (light), rgba(144,202,249,0.08) (dark) |
| **Transition** | Fade in: 300ms ease-in, Fade out: 200ms ease-out |
| **Section Title** | Typography variant h6 (20px, 500 weight), gutterBottom: true |
| **Section Subtitle** | Typography variant body2 (14px), color text.secondary, mb: 2 |
| **Prompt Message** | Typography variant body1 (16px), color text.primary, mb: 3 |
| **Connected Line** | Optional visual connector: 2px left border, primary.main color, full height of follow-up section |
| **Icon** | InfoOutlined icon from @mui/icons-material, 24x24px, color primary.main |
| **Spacing** | spacing(1) = 8px between elements within prompt, spacing(2) = 16px before content area |

**Follow-up Prompt Content**:

| Element | Content | Typography | Color |
|---------|---------|-----------|-------|
| **Section Title** | "Equipment Details" | h6 (20px, 500 weight) | text.primary |
| **Prompt Text** | "Please specify which equipment items you have" | body2 (14px) | text.secondary |
| **Main Instruction** | "Select all items that apply to your training setup:" | body1 (16px) | text.primary |
| **Helper Text** | "This helps us customize your workout program to match your actual equipment" | body2 (14px, italic) | text.secondary |
| **Custom Item Note** | "Don't see your equipment? Use the 'Other' option to add custom items" | caption (12px) | text.secondary |

**Visibility & Conditional Logic**:

| Condition | Visibility | Animation | Behavior |
|-----------|-----------|-----------|----------|
| **Initial Load (no selection)** | Hidden (display: none) | N/A | Not rendered in DOM |
| **User selects basic-equipment** | Visible | Fade in 300ms | Smooth entrance, focus management to title |
| **User changes to no-equipment** | Hidden | Fade out 200ms | Smooth exit, clear related form state |
| **User changes to full-gym** | Hidden | Fade out 200ms | Smooth exit, clear related form state |
| **User navigates back/forward** | Visible if basic-equipment selected | Instant | Persists state, restores previous selections |

**Layout Structure**:

```jsx
{formData.equipmentLevel === 'basic-equipment' && (
  <Box
    sx={{
      mt: 3,
      mb: 3,
      p: 3,
      borderRadius: 2,
      border: '1px solid',
      borderColor: 'divider',
      backgroundColor: theme.palette.mode === 'light'
        ? 'rgba(25,118,210,0.04)'
        : 'rgba(144,202,249,0.08)',
      borderLeft: '4px solid',
      borderLeftColor: 'primary.main',
      transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
      opacity: formData.equipmentLevel === 'basic-equipment' ? 1 : 0,
      pointerEvents: formData.equipmentLevel === 'basic-equipment' ? 'auto' : 'none',
    }}
  >
    <Stack spacing={2}>
      {/* Header with Icon */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <InfoOutlined sx={{ color: 'primary.main', fontSize: 24 }} />
        <Typography variant="h6" sx={{ mb: 0 }}>
          Equipment Details
        </Typography>
      </Box>

      {/* Prompt Text */}
      <Typography variant="body1" sx={{ color: 'text.primary', fontWeight: 500 }}>
        Please specify which equipment items you have
      </Typography>

      <Typography variant="body2" color="text.secondary">
        Select all items that apply to your training setup:
      </Typography>

      {/* Helper Text */}
      <Typography
        variant="body2"
        color="text.secondary"
        sx={{ fontStyle: 'italic', mt: 1 }}
      >
        This helps us customize your workout program to match your actual equipment.
        Don't see your equipment? Use the 'Other' option to add custom items.
      </Typography>

      {/* Equipment Items Section (Story 19.3 will add content here) */}
      {/* Placeholder for Story 19.3 implementation */}
    </Stack>
  </Box>
)}
```

**Visual Connection to Equipment Selection**:

| Visual Element | Purpose | Implementation |
|---------------|---------|-----------------|
| **Left Border Accent** | Connects follow-up to equipment selection above | 4px left border in primary.main color |
| **Subtle Background** | Distinguishes follow-up section as related content | Light primary background (4-8% opacity) |
| **Icon Association** | Visual cue that this is supplementary information | InfoOutlined icon in primary.main color |
| **Proximity** | Follows immediately after equipment selection | mt: 3 margin, no content between |
| **Color Consistency** | Uses primary color from selected option | All accent elements use primary.main |
| **Border Style** | Matches equipment option card borders | 1px divider + 4px accent border |

**Interactive States - Light Theme**:

| State | Background | Border | Text | Icon | Transition |
|-------|-----------|--------|------|------|-----------|
| **Visible (basic selected)** | rgba(25,118,210,0.04) | 1px divider + 4px primary.main left | text.primary | primary.main | 300ms fade-in |
| **Hidden (other selected)** | transparent | none | text.secondary | text.secondary | 200ms fade-out |
| **On Hover** | rgba(25,118,210,0.08) | 1px divider + 4px primary.main left | text.primary | primary.main | Instant |
| **Focus Within** | rgba(25,118,210,0.08) | 2px divider + 4px primary.main left | text.primary | primary.main | Instant |

**Interactive States - Dark Theme**:

| State | Background | Border | Text | Icon | Transition |
|-------|-----------|--------|------|------|-----------|
| **Visible (basic selected)** | rgba(144,202,249,0.08) | 1px divider + 4px primary.main left | text.primary | primary.main | 300ms fade-in |
| **Hidden (other selected)** | transparent | none | text.secondary | text.secondary | 200ms fade-out |
| **On Hover** | rgba(144,202,249,0.12) | 1px divider + 4px primary.main left | text.primary | primary.main | Instant |
| **Focus Within** | rgba(144,202,249,0.12) | 2px divider + 4px primary.main left | text.primary | primary.main | Instant |

**All UI States**:

| State | Condition | Visual Treatment | User Action | Next Step |
|-------|-----------|------------------|-------------|-----------|
| **Hidden** | equipmentLevel !== 'basic-equipment' | Not rendered in DOM, opacity 0, pointerEvents none | User can select other equipment levels | N/A |
| **Appearing** | equipmentLevel changed to 'basic-equipment' | Fade in 300ms, focus moves to follow-up title, background highlights | User reviews prompt and can interact | User reads instructions and selects equipment items |
| **Visible** | equipmentLevel === 'basic-equipment' | Full opacity, interactive state, ready for input | User can read prompt and see equipment selection area below | User selects equipment items in Story 19.3 section |
| **Disappearing** | equipmentLevel changed away from 'basic-equipment' | Fade out 200ms, related state cleared | User cannot interact | Content removed from DOM |
| **Focus State** | Keyboard user tabs into section | Subtle background increase, 2px border enhancement | User can read and navigate content | User can access equipment items section via Tab |

**Responsive Behavior**:

| Breakpoint | Container Padding | Title Size | Text Size | Icon Size | Spacing |
|-----------|------------------|-----------|----------|----------|---------|
| **xs (0-599px)** | spacing(2) = 16px | h6 (20px) | body1 (16px), body2 (14px) | 24x24px | spacing(1) = 8px |
| **sm (600-899px)** | spacing(3) = 24px | h6 (20px) | body1 (16px), body2 (14px) | 24x24px | spacing(2) = 16px |
| **md (900px+)** | spacing(3) = 24px | h6 (20px) | body1 (16px), body2 (14px) | 24x24px | spacing(2) = 16px |

**Accessibility**:

| Aspect | Specification | Compliance |
|--------|--------------|------------|
| **Color Contrast (Light)** | Primary.main (#1976d2) on white = 7.2:1 | WCAG AAA |
| **Color Contrast (Dark)** | Primary.main (#90caf9) on #1e1e1e = 8.4:1 | WCAG AAA |
| **Text Contrast - Title** | text.primary = 15.8:1 (light), 14.9:1 (dark) | WCAG AAA |
| **Text Contrast - Body** | text.primary = 15.8:1 (light), 14.9:1 (dark) | WCAG AAA |
| **Text Contrast - Secondary** | text.secondary = 7.7:1 (light), 7.4:1 (dark) | WCAG AA |
| **Focus Indicator** | Left border increases to 2px on focus-within | WCAG AA (2.4.7) |
| **Icon Semantics** | InfoOutlined icon paired with "Equipment Details" text, not just icon alone | WCAG AA (1.1.1) |
| **Dynamic Content** | aria-live="polite" on parent Box to announce appearance/disappearance | WCAG AA (4.1.3) |
| **Keyboard Navigation** | Tab to section, Enter/Space to interact with nested controls | WCAG AA (2.1.1) |
| **Screen Reader** | Title announced first, helper text read sequentially | WCAG AA (2.4.3) |
| **Semantic Structure** | Stack provides logical content grouping, Typography provides semantic hierarchy | WCAG AA (1.3.1) |
| **Motion** | Uses smooth transition (300ms), respects prefers-reduced-motion | WCAG AA (2.3.3) |

**Validation & Error Handling**:

| Scenario | Behavior | Display |
|----------|----------|---------|
| **Basic equipment selected, no items chosen** | Form submission blocked, validation error for equipment items required | Error message appears in Story 19.3 section |
| **Basic equipment selected, items chosen** | Follow-up section remains visible with selections highlighted | No error state |
| **User switches away from basic** | Follow-up disappears, all equipment item selections cleared | Smooth fade-out transition |
| **User switches back to basic** | Follow-up reappears, previous selections restored (if available) | Smooth fade-in, focus to title |

**Components Used**:
- Box (MUI) - Container wrapper
- Stack (MUI) - Layout of internal elements
- Typography (MUI) - Title, prompt text, helper text
- InfoOutlined icon (MUI @mui/icons-material) - Visual indicator
- Transition - CSS transition for fade in/out
- Conditional rendering - React conditional logic for visibility

**Styling Approach**:
- sx prop for conditional opacity and pointer-events
- CSS transitions for 300ms fade-in, 200ms fade-out
- Left border accent (4px primary.main) for visual connection
- Subtle background color (4-8% opacity of primary) for distinction
- Theme-aware colors for light/dark mode support
- prefers-reduced-motion media query for accessibility

**Integration with Multi-Step Form**:
- Appears immediately after equipment level selection (Story 19.1)
- Visual connection through proximity, left border accent, and color consistency
- Conditional visibility: only rendered when equipmentLevel === 'basic-equipment'
- No validation at this level (validation happens at Story 19.3 level for equipment items)
- Story 19.3 will add checkbox/chip selection controls inside this section
- Maintains consistent styling with rest of onboarding form
- User can navigate back/forward and see section with previous state restored

**Design Rationale**:
- **Conditional visibility with fade transitions**: Immediately guides user attention to next step without disorientation, smooth motion prevents jarring content shifts
- **Visual connection elements**: Left border accent and subtle background create clear association with equipment selection above, helps user understand this is supplementary detail
- **Icon + text combination**: InfoOutlined icon signals "this is informational/helpful" without relying solely on icon alone, text ensures screen reader announces purpose
- **Explicit prompt text**: "Please specify which equipment items you have" removes ambiguity about what user should do, reduces cognitive load
- **Helper text with context**: Explains WHY this matters ("customize workout program") and addresses common question (how to add custom items), reduces user friction
- **Subtle styling**: Uses soft background and accent border instead of prominent card, keeps visual hierarchy focused on equipment selection above while still making follow-up discoverable
- **Immediate appearance**: Appears instantly when user selects basic equipment (no delay), signals responsive system and confirms selection
- **Responsive spacing**: Maintains consistent visual hierarchy across all screen sizes with appropriate spacing adjustments

**Future Feature Integration**:
- Story 19.3 will add equipment item selection controls (checkboxes/chips) inside this section
- Story 19.5 will implement conditional show/hide logic for this section in frontend
- Story 19.6 will add functionality to manage multiple equipment item selections
- Backend validation (Story 19.8) will ensure basic equipment includes at least one item
- This section serves as container for all basic equipment detail interactions

#### Story 19.3: Design Individual Equipment Item Selection

**Purpose**: Create UI for users to select individual equipment items from predefined options and add custom equipment, enabling precise specification of available training equipment.

**Component Specifications**:

| Aspect | Specification |
|--------|--------------|
| **Primary Component** | MUI FormGroup with multiple FormControlLabel + Checkbox components |
| **Predefined Items Container** | Box wrapper with Grid layout (xs: 1 col, sm: 2 cols, md: 3 cols) |
| **Custom Input Section** | Stack with TextField (single-line input) + Button (add custom item) |
| **Checkbox Size** | small (18x18px icon, 40x40px touch target) |
| **Checkbox Color** | primary (theme.palette.primary.main) |
| **Item Layout** | Checkbox + Label in horizontal arrangement with 8px gap |
| **Predefined Item Spacing** | spacing(1.5) = 12px between checkbox items in grid |
| **Custom Item Input** | spacing(2) = 16px below predefined items |
| **Custom Item Button** | MUI Button variant="outlined" size="small", primary color |
| **Selected Items Display** | Chips component to show selected items with delete icons |

**Predefined Equipment Items**:

| Item | Label | Value | Category | Examples |
|------|-------|-------|----------|----------|
| **Dumbbell** | "Dumbbell" | "dumbbell" | Free Weights | Individual hand weights |
| **Barbell** | "Barbell" | "barbell" | Free Weights | Long bars with plates |
| **Kettlebell** | "Kettlebell" | "kettlebell" | Free Weights | Single-handle weights |
| **Resistance Bands** | "Resistance Bands" | "resistance-bands" | Resistance | Loop or tube bands |
| **Pull-up Bar** | "Pull-up Bar" | "pull-up-bar" | Bodyweight Assist | Door frame or wall-mounted |
| **Bench** | "Bench" | "bench" | Equipment | Weight bench, seat, or sturdy chair |
| **Yoga Mat** | "Yoga Mat" | "yoga-mat" | Accessories | Exercise or yoga mat |

**Interactive States - Light Theme**:

| State | Checkbox Border | Checkbox Fill | Label Text | Background | Border | Hover Background |
|-------|-----------------|---------------|------------|-----------|--------|-----------------|
| **Unchecked Default** | 2px rgba(0,0,0,0.54) | transparent | text.primary | transparent | none | rgba(0,0,0,0.04) |
| **Unchecked Hover** | 2px rgba(0,0,0,0.87) | transparent | text.primary | rgba(0,0,0,0.04) | none | rgba(0,0,0,0.04) |
| **Checked** | 2px primary.main | primary.main | text.primary | rgba(25,118,210,0.04) | none | rgba(25,118,210,0.08) |
| **Checked Hover** | 2px primary.dark | primary.dark | text.primary | rgba(25,118,210,0.08) | none | rgba(25,118,210,0.08) |
| **Focus (Keyboard)** | 2px primary.main | current fill | text.primary | current bg | 2px outline primary | current |
| **Disabled** | 2px rgba(0,0,0,0.26) | rgba(0,0,0,0.26) | rgba(0,0,0,0.38) | rgba(0,0,0,0.02) | none | transparent |

**Interactive States - Dark Theme**:

| State | Checkbox Border | Checkbox Fill | Label Text | Background | Border | Hover Background |
|-------|-----------------|---------------|------------|-----------|--------|-----------------|
| **Unchecked Default** | 2px rgba(255,255,255,0.7) | transparent | text.primary | transparent | none | rgba(255,255,255,0.08) |
| **Unchecked Hover** | 2px rgba(255,255,255,0.87) | transparent | text.primary | rgba(255,255,255,0.08) | none | rgba(255,255,255,0.08) |
| **Checked** | 2px primary.main | primary.main | text.primary | rgba(144,202,249,0.12) | none | rgba(144,202,249,0.12) |
| **Checked Hover** | 2px primary.light | primary.light | text.primary | rgba(144,202,249,0.16) | none | rgba(144,202,249,0.16) |
| **Focus (Keyboard)** | 2px primary.main | current fill | text.primary | current bg | 2px outline primary | current |
| **Disabled** | 2px rgba(255,255,255,0.3) | rgba(255,255,255,0.3) | rgba(255,255,255,0.38) | rgba(255,255,255,0.02) | none | transparent |

**All UI States**:

| State | Condition | Visual Treatment | User Action | Next Step |
|-------|-----------|------------------|-------------|-----------|
| **Empty (No Items Selected)** | Initial load within follow-up section | All predefined checkboxes unchecked, custom input empty, no chips displayed | User can select any items or enter custom | Selection checked visually, chips appear |
| **Item Selected** | User clicks predefined item checkbox | Checkbox filled with primary color, background highlight, chip appears in selected items area | User can select more, uncheck, or add custom | Item persists, form can be submitted |
| **Multiple Items** | User selects 2+ items | All selected checkboxes marked with primary color, all chips displayed in compact layout | User can deselect or add more | Form submission proceeds if form valid |
| **Custom Item Entry** | User types in "Other" text field | Text displays in input, Add button enabled (if text non-empty) | User can submit via button or Continue form | Chip appears, custom item added to selections |
| **Custom Item Added** | User clicks Add button or presses Enter | Input clears, new chip appears with delete icon, input refocused | User can add more custom or select predefined | All custom items persist through form navigation |
| **Item Unselected** | User unchecks a previously selected item | Checkbox returns to unchecked state, associated chip removed | User can proceed with remaining items | State persists if user navigates back |
| **Custom Item Deleted** | User clicks X on custom item chip | Chip removed from display, custom item cleared from selections | User can re-add or continue with remaining | Other items unaffected |
| **No Items Selected (Error)** | User attempts form submission without items | Error message displays: "Please select at least one equipment item or enter a custom item", input border highlights | User must select/add item to proceed | Selecting any item clears error |
| **Validation Error** | Form submission fails item count validation | Error state persists until user makes selection | User adds item to fix | Error clears |

**Layout Structure**:

```jsx
{/* Story 19.3: Equipment Items Selection - Inside Story 19.2 follow-up section */}
<Stack spacing={3}>
  {/* Predefined Equipment Items */}
  <Box>
    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
      Select all items that apply to your training setup:
    </Typography>
    <FormGroup>
      <Grid container spacing={1.5}>
        {['dumbbell', 'barbell', 'kettlebell', 'resistance-bands', 'pull-up-bar', 'bench', 'yoga-mat'].map((item) => (
          <Grid item xs={12} sm={6} md={4} key={item}>
            <FormControlLabel
              control={<Checkbox
                checked={selectedItems.includes(item)}
                onChange={(e) => handleItemToggle(item, e.target.checked)}
                size="small"
              />}
              label={toTitleCase(item)}
              sx={{
                width: '100%',
                m: 0,
                p: 1.5,
                borderRadius: 1,
                transition: 'all 225ms cubic-bezier(0.4, 0, 0.2, 1)',
                backgroundColor: selectedItems.includes(item) ? 'action.selected' : 'transparent',
                '&:hover': {
                  backgroundColor: selectedItems.includes(item) ? 'action.selected' : 'action.hover',
                },
              }}
            />
          </Grid>
        ))}
      </Grid>
    </FormGroup>
  </Box>

  {/* Divider */}
  <Divider />

  {/* Custom Equipment Item Input */}
  <Box>
    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
      Don't see your equipment? Add a custom item:
    </Typography>
    <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
      <TextField
        placeholder="e.g., Cable machine, Smith machine"
        variant="outlined"
        size="small"
        fullWidth
        value={customItemInput}
        onChange={(e) => setCustomItemInput(e.target.value)}
        onKeyPress={(e) => {
          if (e.key === 'Enter' && customItemInput.trim()) {
            handleAddCustomItem();
          }
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            '&:hover fieldset': {
              borderColor: 'primary.main',
            },
            '&.Mui-focused fieldset': {
              borderColor: 'primary.main',
            },
          },
        }}
      />
      <Button
        variant="outlined"
        onClick={handleAddCustomItem}
        disabled={!customItemInput.trim()}
        sx={{
          minWidth: '80px',
          textTransform: 'none',
        }}
      >
        Add
      </Button>
    </Stack>
  </Box>

  {/* Selected Items Display (Chips) */}
  {selectedItems.length > 0 && (
    <Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Selected equipment:
      </Typography>
      <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 1 }}>
        {selectedItems.map((item) => (
          <Chip
            key={item}
            label={toTitleCase(item)}
            onDelete={() => handleItemRemove(item)}
            color="primary"
            variant="outlined"
            size="small"
            sx={{
              mt: 0.5,
              textTransform: 'capitalize',
            }}
          />
        ))}
      </Stack>
    </Box>
  )}

  {/* Validation Error */}
  {errors.equipmentItems && (
    <FormHelperText error sx={{ mt: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        <ErrorOutline fontSize="small" />
        {errors.equipmentItems}
      </Box>
    </FormHelperText>
  )}
</Stack>
```

**Predefined Items Grid Layout**:

| Breakpoint | Columns | Item Width | Spacing |
|-----------|---------|-----------|---------|
| **xs (0-599px)** | 1 | Full width minus padding | 12px |
| **sm (600-899px)** | 2 | ~45% width each | 12px |
| **md (900px+)** | 3 | ~30% width each | 12px |

**Custom Item Input Layout**:

| Breakpoint | Direction | TextField Width | Button Width | Spacing |
|-----------|-----------|-----------------|-------------|---------|
| **xs (0-599px)** | row (stacked) | 100% | auto | 8px |
| **sm (600px+)** | row | flex | auto | 8px |

**Selected Items Chip Display**:

| Aspect | Specification |
|--------|--------------|
| **Container** | Stack with direction="row", gap: 1 (8px), flex wrap enabled |
| **Chip Variant** | outlined, size="small", color="primary" |
| **Chip Label** | Title-cased equipment name |
| **Chip Delete** | X icon on right side, removes item on click |
| **Chip Color** | primary.main for filled, outlined variant |
| **Spacing Between Chips** | 8px gap with flex wrap for responsive layout |

**Typography Specifications**:

| Element | Variant | Size | Weight | Color | Usage |
|---------|---------|------|--------|-------|-------|
| **Predefined Label** | body2 (14px) | 14px | 400 | text.primary | Item checkbox labels |
| **Section Instruction** | body2 (14px) | 14px | 400 | text.secondary | "Select all items..." |
| **Custom Item Instruction** | body2 (14px) | 14px | 400 | text.secondary | "Don't see your equipment?" |
| **Selected Items Label** | body2 (14px) | 14px | 400 | text.secondary | "Selected equipment:" |
| **Chip Label** | body2 (12px) | 12px | 400 | primary.main | Item names in chips |
| **Error Message** | body2 (14px) | 14px | 400 | error.main | Validation error text |

**Accessibility**:

| Aspect | Specification | Compliance |
|--------|--------------|------------|
| **Checkbox Contrast - Light** | rgba(0,0,0,0.54) on white = 7.2:1 | WCAG AAA |
| **Checkbox Contrast - Dark** | rgba(255,255,255,0.7) on #1e1e1e = 9.8:1 | WCAG AAA |
| **Label Text Contrast** | text.primary = 15.8:1 (light), 14.9:1 (dark) | WCAG AAA |
| **Secondary Text Contrast** | text.secondary = 7.7:1 (light), 7.4:1 (dark) | WCAG AA |
| **Focus Indicator** | 2px outline primary, 3:1+ contrast | WCAG AA (2.4.7) |
| **Touch Target** | 40x40px minimum for checkboxes | WCAG 2.1 AA (2.5.5) |
| **Keyboard Navigation** | Tab to focus items, Space to toggle, Enter in text field | WCAG AA (2.1.1) |
| **Screen Reader** | FormControlLabel provides checkbox + label association, instructions read sequentially | WCAG AA (4.1.3) |
| **Form Group Role** | FormGroup role (native Checkbox group), aria-label for group | WCAG AA (4.1.2) |
| **Error Association** | FormHelperText linked via aria-describedby to FormGroup | WCAG AA (3.3.1) |
| **Custom Input Label** | Placeholder + visible label "Don't see your equipment?" provides context | WCAG AA (3.3.2) |
| **Chip Semantics** | Chips use button role with accessible delete action, aria-label for close | WCAG AA (4.1.3) |

**Responsive Behavior**:

| Breakpoint | Predefined Grid | Custom Input | Chips | Spacing |
|-----------|-----------------|-------------|-------|---------|
| **xs (0-599px)** | 1 column, full width | Stack direction row, inputs stack vertically | Single row with wrap | spacing(1.5) = 12px |
| **sm (600-899px)** | 2 columns | Row layout, side-by-side | Single row with wrap | spacing(1.5) = 12px |
| **md (900px+)** | 3 columns | Row layout, side-by-side | Single row with wrap | spacing(1.5) = 12px |

**Validation Rules**:

- **At least one item required**: Form submission fails if no predefined items selected AND no custom items added
- **Error Display**: "Please select at least one equipment item or enter a custom item"
- **Error Clear**: Selecting any predefined item OR adding custom item clears validation error
- **Custom Item Rules**:
  - Trim whitespace before checking
  - Prevent empty custom items
  - Allow duplicate prevention (warn if item already exists)
  - Max length 50 characters for custom items
  - Alphanumeric + basic punctuation allowed
- **Persistence**: Selected items persist when user navigates back/forward in stepper
- **Auto-clear**: When user changes equipment level away from "basic-equipment", all items cleared

**Validation Error States**:

| Error Scenario | Error Message | Display Location | Visual Treatment | Clear Condition |
|----------------|---------------|------------------|------------------|-----------------|
| **No Items Selected** | "Please select at least one equipment item or enter a custom item" | Below chips/input area with FormHelperText | Red text, ErrorOutline icon | Selecting any item |
| **Invalid Custom Input** | "Equipment name must be 1-50 characters" | Below text field | Red input border | Correcting input |
| **Duplicate Item** | "You've already added '[item name]'" | Below text field, warning style | Orange/warning color | Removing duplicate or changing input |

**Components Used**:

- FormGroup, FormControlLabel, Checkbox (MUI)
- TextField, Button (MUI)
- Chip (MUI)
- Grid, Box, Stack, Divider (MUI)
- Typography (MUI)
- FormHelperText (MUI)
- ErrorOutline icon (MUI @mui/icons-material)

**Styling Approach**:

- sx prop for conditional styling (background color based on checked state)
- MUI theme for colors, spacing, typography
- Checkbox size="small" for space efficiency
- Grid responsive layout using xs/sm/md breakpoints
- Chip component for selected items display with delete action
- TextField with outlined variant for custom input
- Button variant="outlined" for secondary action
- Smooth transitions (225ms) for checkbox state changes
- Flex wrap and gap spacing for responsive chip layout

**Integration with Multi-Step Form**:

- Renders inside Story 19.2 follow-up section (only when equipmentLevel === 'basic-equipment')
- Form-level validation blocks Next button if no items selected
- Selected items stored in parent form state (formData.equipmentItems)
- Value is array of strings: ['dumbbell', 'barbell', 'custom-item-name']
- Validation integrated with form-level validation
- User can navigate back to revise selections without losing data
- Story 19.6 (frontend) will handle multiple selection logic
- Story 19.8 (backend) will validate at least one item for basic equipment

**Edge Cases Handled**:

- No initial selection: Empty state shows all checkboxes unchecked
- User selects then unselects all items: Can proceed if validation not triggered
- User tries to add empty custom item: Add button disabled when input empty
- User adds duplicate custom item: Prevented with error message
- User navigates away and back: Items persist if available
- User changes equipment level: All items cleared when switching away from basic-equipment
- User selects same item twice: Not possible (checkboxes, not chips)
- Long custom item names: Truncated in chip display with full text in tooltip
- Very many custom items: Chips wrap to multiple lines, remain scrollable/readable

**Design Rationale**:

- **Checkboxes for multi-select pattern**: Standard UI pattern users expect, clearly indicates multiple selections allowed (vs radio buttons for single selection in Story 19.1)
- **Predefined items with custom fallback**: Covers 90%+ of users' equipment while allowing flexibility for edge cases, reduces cognitive load by providing suggestions
- **Grid layout for predefined items**: More compact and scannable than vertical list, responsive columns adapt to screen size
- **Chip display of selections**: Shows at-a-glance which items selected, delete action readily available, compact visual treatment
- **Custom item input with Add button**: Clear affordance for adding items, Enter key support reduces friction, preview in chips immediately shows addition
- **Divider between predefined and custom**: Visual separation clarifies that custom is optional, helps users understand section structure
- **Inline validation errors**: Appears near the control causing issue, paired with icon for accessibility
- **Touch target sizing**: 40x40px minimum for checkboxes meets WCAG touch target guidelines
- **Responsive grid columns**: Maximizes use of horizontal space on larger screens while maintaining legibility on mobile
- **Placeholder + label for custom input**: Provides context for text field purpose while maintaining compact layout
- **Color consistency**: Uses primary color for all selection indicators (checkboxes, chips) to maintain visual cohesion with Story 19.1 and 19.2

**Future Feature Integration**:

- Story 19.5: Show Basic Equipment Follow-up (implements conditional rendering of entire follow-up section including this component)
- Story 19.6: Select Multiple Equipment Items (implements checkbox toggle logic and form state management)
- Story 19.8: Validate Basic Equipment Items (backend validation ensures at least one item)

---

### Feature: Basic Login Form (Feature #20)

**Purpose**: Enable users to access the application by providing their name and email address through a simple, visually clear login form that requires minimal cognitive effort and provides confidence in data entry without password authentication or verification.

**Design Decisions**:
- **Minimal form pattern**: Two-field form (name + email) reduces friction, follows established form patterns from existing features
- **MUI TextField outlined variant**: Consistent with existing form inputs (Assessment Form), provides clear field boundaries and visual hierarchy
- **Single primary action**: One contained button eliminates decision paralysis, clear call-to-action for proceeding
- **Inline validation with helper text**: Real-time feedback on email format, error states with clear messaging
- **Full-width layout on mobile**: Maximizes touch target size, reduces horizontal scrolling on small screens
- **Centered card layout**: Focuses attention on login task, reduces visual noise during authentication flow

**User Flow**:
- User lands on login page → Sees centered login form → Enters name → Enters email → Clicks "Continue" → Redirected to main application (or error feedback if validation fails)

#### Story 20.2: Login Form Interface Design

**Purpose**: Create a visually clear and intuitive login form interface that allows users to easily identify input requirements, understand expected formats, and confidently submit their credentials.

**Component Specifications**:

| Aspect | Specification |
|--------|--------------|
| **Container Component** | MUI Card with elevation={3} for prominence |
| **Card Width** | xs: 100% (mobile), sm: 480px (tablet+), max-width: 90vw |
| **Card Padding** | CardContent with spacing(4) = 32px all sides |
| **Layout Component** | Stack with spacing={3} (24px) vertical rhythm |
| **Input Components** | MUI TextField variant="outlined" size="medium" fullWidth |
| **Input Spacing** | spacing(3) = 24px between form fields |
| **Action Button** | MUI Button variant="contained" color="primary" size="large" fullWidth |
| **Button Height** | 48px (large size ensures minimum touch target) |
| **Typography Hierarchy** | h5 (24px) for title, body1 (16px) for inputs, body2 (14px) for helper text |
| **Alignment** | Centered horizontally on page, vertically centered or top-aligned based on viewport height |

**Field Specifications**:

| Field | Label | Placeholder | Type | Validation | Helper Text (Default) | Error Text |
|-------|-------|-------------|------|------------|----------------------|-----------|
| **Name** | "Name" | "Enter your full name" | text | Required, min 1 char | "" | "Name is required" |
| **Email** | "Email Address" | "you@example.com" | email | Required, valid email format | "" | "Please enter a valid email address" |

**Interactive States - Light Theme**:

| State | Border Color | Background | Label Color | Helper Text Color | Icon/Indicator |
|-------|-------------|-----------|------------|------------------|---------------|
| **Default (Empty)** | rgba(0,0,0,0.23) | transparent | text.secondary | text.secondary | None |
| **Focus** | primary.main (#1976d2) | transparent | primary.main | text.secondary | Blue left border accent (2px) |
| **Filled (Valid)** | rgba(0,0,0,0.23) | transparent | text.primary | text.secondary | None |
| **Hover (Empty)** | rgba(0,0,0,0.87) | transparent | text.secondary | text.secondary | None |
| **Error** | error.main (#d32f2f) | transparent | error.main | error.main | ErrorOutline icon (20px) |
| **Disabled** | rgba(0,0,0,0.12) | rgba(0,0,0,0.02) | rgba(0,0,0,0.38) | rgba(0,0,0,0.38) | None |

**Interactive States - Dark Theme**:

| State | Border Color | Background | Label Color | Helper Text Color | Icon/Indicator |
|-------|-------------|-----------|------------|------------------|---------------|
| **Default (Empty)** | rgba(255,255,255,0.23) | transparent | text.secondary | text.secondary | None |
| **Focus** | primary.main (#90caf9) | transparent | primary.main | text.secondary | Blue left border accent (2px) |
| **Filled (Valid)** | rgba(255,255,255,0.23) | transparent | text.primary | text.secondary | None |
| **Hover (Empty)** | rgba(255,255,255,0.7) | transparent | text.secondary | text.secondary | None |
| **Error** | error.main (#f44336) | transparent | error.main | error.main | ErrorOutline icon (20px) |
| **Disabled** | rgba(255,255,255,0.12) | rgba(255,255,255,0.02) | rgba(255,255,255,0.38) | rgba(255,255,255,0.38) | None |

**Button States - Light Theme**:

| State | Background | Text Color | Elevation | Border | Cursor | Transition |
|-------|-----------|-----------|----------|--------|--------|-----------|
| **Default** | primary.main (#1976d2) | #ffffff | 2 | none | pointer | 225ms cubic-bezier(0.4, 0, 0.2, 1) |
| **Hover** | primary.dark (#1565c0) | #ffffff | 4 | none | pointer | 225ms cubic-bezier(0.4, 0, 0.2, 1) |
| **Active/Pressed** | primary.dark (#1565c0) | #ffffff | 8 | none | pointer | 225ms cubic-bezier(0.4, 0, 0.2, 1) |
| **Focus (Keyboard)** | primary.main (#1976d2) | #ffffff | 2 | 2px outline primary | pointer | 225ms cubic-bezier(0.4, 0, 0.2, 1) |
| **Loading** | primary.main (#1976d2) | transparent | 2 | none | default | 225ms cubic-bezier(0.4, 0, 0.2, 1) |
| **Disabled** | rgba(0,0,0,0.12) | rgba(0,0,0,0.26) | 0 | none | not-allowed | 225ms cubic-bezier(0.4, 0, 0.2, 1) |

**Button States - Dark Theme**:

| State | Background | Text Color | Elevation | Border | Cursor | Transition |
|-------|-----------|-----------|----------|--------|--------|-----------|
| **Default** | primary.main (#90caf9) | rgba(0,0,0,0.87) | 2 | none | pointer | 225ms cubic-bezier(0.4, 0, 0.2, 1) |
| **Hover** | primary.light (#bbdefb) | rgba(0,0,0,0.87) | 4 | none | pointer | 225ms cubic-bezier(0.4, 0, 0.2, 1) |
| **Active/Pressed** | primary.light (#bbdefb) | rgba(0,0,0,0.87) | 8 | none | pointer | 225ms cubic-bezier(0.4, 0, 0.2, 1) |
| **Focus (Keyboard)** | primary.main (#90caf9) | rgba(0,0,0,0.87) | 2 | 2px outline primary | pointer | 225ms cubic-bezier(0.4, 0, 0.2, 1) |
| **Loading** | primary.main (#90caf9) | transparent | 2 | none | default | 225ms cubic-bezier(0.4, 0, 0.2, 1) |
| **Disabled** | rgba(255,255,255,0.12) | rgba(255,255,255,0.3) | 0 | none | not-allowed | 225ms cubic-bezier(0.4, 0, 0.2, 1) |

**All UI States**:

| State | Condition | Visual Treatment | User Action | Next Step |
|-------|-----------|------------------|-------------|-----------|
| **Initial Load** | User lands on login page | Empty form, both fields unfocused, button enabled | User can focus name field | Name field gains focus state |
| **Name Field Focus** | User clicks/tabs to name field | Blue focus border, label moves to top, placeholder visible | User types name | Text appears in field |
| **Name Field Filled** | User has entered text | Text displays, label at top, border returns to default | User can proceed to email | Tab or click to email field |
| **Name Field Empty Error** | User leaves name empty and tries to submit | Red error border, error text below field: "Name is required" | User must enter name | Error clears when user types |
| **Email Field Focus** | User clicks/tabs to email field | Blue focus border, label moves to top, placeholder visible | User types email | Text appears in field |
| **Email Field Filled (Valid)** | User has entered valid email format | Text displays, label at top, border returns to default | User can submit form | Click Continue button |
| **Email Field Filled (Invalid)** | User enters invalid email and leaves field | Red error border, error text: "Please enter a valid email address" | User corrects email format | Error clears when valid |
| **Email Field Empty Error** | User leaves email empty and tries to submit | Red error border, error text: "Email is required" | User must enter email | Error clears when user types |
| **Form Submitting** | User clicks Continue with valid inputs | Button shows loading spinner, button disabled, fields disabled | User waits for response | Success redirect or error message |
| **Submission Success** | Backend accepts login | Brief success feedback (optional), redirect to main app | User automatically redirected | User sees main application |
| **Submission Error (Network)** | Network failure during submit | Alert/Snackbar: "Connection error. Please try again." | User can retry submission | Click Continue again |
| **Submission Error (Server)** | Server returns error (e.g., invalid email) | Alert/Snackbar with specific error message from server | User corrects issue | Resubmit form |

**Layout Structure**:

```jsx
{/* Story 20.2: Login Form Interface */}
<Box
  sx={{
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'background.default',
    p: 2,
  }}
>
  <Card
    elevation={3}
    sx={{
      width: '100%',
      maxWidth: { xs: '100%', sm: '480px' },
      maxHeight: '90vh',
    }}
  >
    <CardContent sx={{ p: 4 }}>
      <Stack spacing={3}>
        {/* Title */}
        <Box>
          <Typography variant="h5" component="h1" fontWeight={500} gutterBottom>
            Welcome
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Enter your details to continue
          </Typography>
        </Box>

        {/* Form Fields */}
        <Stack component="form" spacing={3} onSubmit={handleSubmit} noValidate>
          {/* Name Field */}
          <TextField
            id="name"
            name="name"
            label="Name"
            placeholder="Enter your full name"
            variant="outlined"
            fullWidth
            required
            autoComplete="name"
            autoFocus
            value={formData.name}
            onChange={handleNameChange}
            error={!!errors.name}
            helperText={errors.name}
            disabled={isSubmitting}
            inputProps={{
              'aria-label': 'Name',
              'aria-required': 'true',
              'aria-invalid': !!errors.name,
              'aria-describedby': errors.name ? 'name-error' : undefined,
            }}
          />

          {/* Email Field */}
          <TextField
            id="email"
            name="email"
            label="Email Address"
            placeholder="you@example.com"
            type="email"
            variant="outlined"
            fullWidth
            required
            autoComplete="email"
            value={formData.email}
            onChange={handleEmailChange}
            error={!!errors.email}
            helperText={errors.email}
            disabled={isSubmitting}
            inputProps={{
              'aria-label': 'Email Address',
              'aria-required': 'true',
              'aria-invalid': !!errors.email,
              'aria-describedby': errors.email ? 'email-error' : undefined,
            }}
          />

          {/* Submit Button */}
          <Button
            type="submit"
            variant="contained"
            color="primary"
            size="large"
            fullWidth
            disabled={isSubmitting}
            sx={{
              mt: 2,
              height: 48,
              textTransform: 'none',
              fontSize: '1rem',
              fontWeight: 500,
            }}
          >
            {isSubmitting ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              'Continue'
            )}
          </Button>
        </Stack>
      </Stack>
    </CardContent>
  </Card>
</Box>
```

**Responsive Behavior**:

| Breakpoint | Card Width | Card Padding | Vertical Alignment | Layout Changes |
|-----------|-----------|-------------|-------------------|----------------|
| **xs (0-599px)** | 100% width (minus 16px margin) | 32px | Centered vertically | Full-width fields, stacked layout |
| **sm (600-899px)** | 480px fixed width | 32px | Centered vertically | Fixed-width card, stacked layout |
| **md (900px+)** | 480px fixed width | 32px | Centered vertically | Fixed-width card, stacked layout |

**Validation Rules**:

| Field | Rule | Trigger | Error Message | Validation Type |
|-------|------|---------|--------------|----------------|
| **Name** | Required (min 1 char after trim) | onBlur, onSubmit | "Name is required" | Client-side |
| **Name** | Max 100 characters | onChange | "Name must be less than 100 characters" | Client-side |
| **Email** | Required | onBlur, onSubmit | "Email is required" | Client-side |
| **Email** | Valid email format (regex) | onBlur, onSubmit | "Please enter a valid email address" | Client-side |
| **Email** | Max 254 characters | onChange | "Email must be less than 254 characters" | Client-side |

**Email Validation Regex**:
```javascript
/^[^\s@]+@[^\s@]+\.[^\s@]+$/
```

**Accessibility Features**:

| Feature | Implementation | WCAG Guideline | Purpose |
|---------|---------------|----------------|---------|
| **Focus Management** | Auto-focus on name field on page load | 2.4.3 Focus Order | Keyboard users start input immediately |
| **Keyboard Navigation** | Tab order: Name → Email → Continue button | 2.4.3 Focus Order | Predictable tab sequence |
| **Error Identification** | aria-invalid, aria-describedby on error fields | 3.3.1 Error Identification | Screen readers announce errors |
| **Labels** | Explicit labels with htmlFor matching input IDs | 3.3.2 Labels or Instructions | Clear field identification |
| **Required Fields** | aria-required="true" on required inputs | 3.3.2 Labels or Instructions | Indicates mandatory fields |
| **Error Messages** | Role="alert" on error text, associated with field | 3.3.3 Error Suggestion | Screen readers announce validation errors |
| **Color Contrast** | Error red: 5.1:1 contrast (WCAG AA) | 1.4.3 Contrast (Minimum) | Readable error states |
| **Touch Targets** | Button 48px height minimum | 2.5.5 Target Size | Meets minimum touch target |
| **Loading State** | aria-busy="true" during submission | 4.1.3 Status Messages | Announces loading state |

**Error Handling Patterns**:

1. **Inline Field Errors**: Display immediately below field with error border and icon
2. **Form-level Errors**: Display in Snackbar at top of viewport for server/network errors
3. **Real-time Validation**: Email format validated onBlur (not onChange to avoid premature errors)
4. **Required Field Validation**: Triggered onBlur and onSubmit
5. **Error Recovery**: Errors clear when user corrects input (onChange clears error if valid)

**Loading States**:

| Phase | Visual Indicator | Button State | Fields State | Duration |
|-------|-----------------|--------------|-------------|----------|
| **Idle** | None | Enabled, "Continue" text | Enabled | N/A |
| **Validating** | None | Enabled (validation fast) | Enabled | <100ms |
| **Submitting** | Spinner in button center | Disabled, spinner visible | Disabled | Variable |
| **Success** | Optional success icon/message | Disabled | Disabled | <500ms before redirect |
| **Error** | Snackbar with error message | Enabled, "Continue" text | Enabled | Until dismissed |

**Design Rationale**:

- **Centered card layout**: Focuses user attention on single task, reduces visual clutter during authentication flow, follows established pattern from Feature 11 (Onboarding)
- **Two-field minimum**: Balances user identification needs with minimal friction, no password reduces barrier to entry
- **Email validation client-side**: Immediate feedback prevents submission errors, reduces server load from invalid submissions
- **Auto-focus on name field**: Reduces time-to-first-input, keyboard users can start typing immediately
- **Full-width button**: Clear primary action, large touch target (48px), visually prominent
- **Loading spinner in button**: Keeps user informed during async operations, prevents double-submission
- **Outlined TextField variant**: Consistent with existing form patterns (Assessment Form), clear field boundaries
- **Placeholder text with examples**: Guides users on expected format without cluttering interface
- **Helper text for errors only**: Reduces visual noise when form valid, shows guidance when needed
- **Material elevation on card**: Creates depth hierarchy, separates form from background
- **Responsive card width**: Full-width on mobile maximizes space, fixed width on desktop prevents excessive line length

**Integration with Existing Patterns**:

- **Form Pattern Consistency**: Matches Stack spacing and TextField usage from Assessment Form (Feature 11)
- **Button Treatment**: Follows primary button pattern (contained variant, full-width on mobile)
- **Typography Scale**: Uses h5 for page title, body1 for inputs (consistent with existing features)
- **Color System**: Uses theme.palette.primary for actions, error for validation, text.secondary for helper text
- **Spacing System**: 8px grid system (spacing(3) = 24px, spacing(4) = 32px)

**Future Enhancement Considerations**:

- Social login buttons (Google, GitHub) could be added below primary action with divider
- "Remember me" checkbox could extend session persistence (Feature 20.8 dependency)
- Password field could be added for enhanced security (future authentication upgrade)
- Multi-step form could split name/email into separate screens (for mobile optimization)
- Progressive disclosure could hide email field until name is valid (reduces cognitive load)

**Contrast Validation**:

All color combinations meet WCAG AA standards:
- Primary button text on primary.main: 4.65:1 (WCAG AA Pass)
- Error text on white background: 5.1:1 (WCAG AA Pass)
- Helper text (text.secondary) on white: 7.7:1 (WCAG AAA Pass)
- Focus border (primary.main) on white: 4.65:1 (WCAG AA Pass for UI components)
- Story 19.11: Predefined Equipment Options Management (backend configuration of predefined items list)
