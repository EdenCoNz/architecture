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

## Implementation Guidelines

### Styling Approach Priority
1. **MUI Theme**: Global design tokens, component defaults
2. **sx prop**: Component-specific one-off styles, responsive overrides
3. **styled()**: Reusable custom components, complex hover states
4. **Global CSS**: CSS reset, utility classes, print styles

### File Organization
```
src/
├─ theme/
│  ├─ index.ts          # Theme configuration export
│  ├─ palette.ts        # Color definitions
│  ├─ typography.ts     # Typography scale
│  └─ components.ts     # Component overrides
├─ components/
│  └─ [ComponentName]/
│     ├─ index.tsx      # Component implementation
│     ├─ styles.ts      # styled() components (if needed)
│     └─ types.ts       # TypeScript interfaces
```

### Theme Usage Example
```jsx
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {/* App content */}
    </ThemeProvider>
  );
}
```

### Responsive Styling Patterns
```jsx
// Using sx prop with breakpoints
<Box
  sx={{
    padding: { xs: 2, md: 4 },
    display: { xs: 'block', md: 'flex' },
    gap: 2,
  }}
>

// Using theme breakpoints in styled()
const ResponsiveCard = styled(Card)(({ theme }) => ({
  [theme.breakpoints.down('sm')]: {
    padding: theme.spacing(2),
  },
  [theme.breakpoints.up('md')]: {
    padding: theme.spacing(4),
  },
}));
```

### Accessibility Implementation
```jsx
// Semantic HTML with ARIA
<Button
  aria-label="Add item to cart"
  aria-describedby="cart-help-text"
>
  <AddIcon />
</Button>
<Typography id="cart-help-text" variant="caption">
  Click to add item to your shopping cart
</Typography>

// Focus management
const dialogRef = useRef();
useEffect(() => {
  if (open) {
    dialogRef.current?.focus();
  }
}, [open]);
```
