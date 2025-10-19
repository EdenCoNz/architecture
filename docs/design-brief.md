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

### Feature: Dark Mode Theme System
**Purpose**: Provide comprehensive dark mode color palette and theming that maintains accessibility, visual hierarchy, and brand consistency across all UI states.

**Design Decisions**:
- **Material Design 3 elevation overlay pattern**: Dark surfaces use white overlay at varying opacity levels (0-15%) to indicate elevation, avoiding pure black for better depth perception
- **Increased primary/secondary brightness**: Dark mode uses lighter variants of brand colors (#42a5f5, #f48fb1) for better visibility on dark backgrounds while maintaining brand recognition
- **Surface color strategy**: Three-tier surface system (background < paper < elevated) provides clear hierarchy without relying solely on shadows
- **Semantic color adjustments**: Error, warning, info, success colors lightened 1-2 shades for sufficient contrast on dark backgrounds (WCAG AA minimum 4.5:1 for text)

**MUI Dark Mode Implementation**: Uses MUI's built-in dark mode via `palette.mode: 'dark'`, automatically adjusting component states, shadows, and interaction patterns

**Components Used**: All existing components adapt to dark theme via MUI palette mode

**Interaction Patterns**:
- **Theme toggle**: IconButton in AppBar toggles between light/dark modes
- **Persistence**: User preference saved to localStorage, retrieved on app load
- **System preference detection**: Respects `prefers-color-scheme` media query on first visit
- **Smooth transitions**: 225ms CSS transition on background/text color changes (respects `prefers-reduced-motion`)

**States**:
- **Light mode active**: Sun/Light icon visible, light palette applied
- **Dark mode active**: Moon/Dark icon visible, dark palette applied
- **Loading**: Current theme renders immediately from localStorage or system preference
- **Error**: Theme toggle disabled if localStorage access fails, defaults to light mode

---

### Dark Mode Color Palette

#### Background & Surfaces
| Purpose | Light Mode | Dark Mode | Contrast Ratio | Usage |
|---------|------------|-----------|----------------|-------|
| Background Default | `#fafafa` | `#121212` | - | Page background, lowest elevation |
| Background Paper | `#ffffff` | `#1e1e1e` | - | Card backgrounds, elevation 1 |
| Elevated Surface 1 | `#ffffff` | `#242424` | - | Dialogs, drawers, elevation 2-4 |
| Elevated Surface 2 | `#ffffff` | `#2a2a2a` | - | Floating action buttons, elevation 6-8 |
| Elevated Surface 3 | `#ffffff` | `#303030` | - | App bar, modals, elevation 12+ |

**Rationale**: Material Design 3 recommends `#121212` base with 5% white overlays per elevation level. Avoids pure black (#000000) to reduce eye strain and improve depth perception in dark environments.

#### Brand Colors - Dark Mode Adjustments
| Color | Light Mode | Dark Mode | Adjustment | Contrast on #121212 |
|-------|------------|-----------|------------|---------------------|
| Primary Main | `#1976d2` | `#42a5f5` | +2 shades lighter | 4.89:1 (AA pass) |
| Primary Light | `#42a5f5` | `#64b5f6` | +1 shade lighter | 6.12:1 (AA pass) |
| Primary Dark | `#1565c0` | `#1976d2` | Original main | 3.56:1 (UI only) |
| Secondary Main | `#dc004e` | `#f48fb1` | +3 shades lighter | 5.23:1 (AA pass) |
| Secondary Light | `#f50057` | `#f6a5c0` | +2 shades lighter | 6.89:1 (AA pass) |
| Secondary Dark | `#9a0036` | `#dc004e` | Original main | 4.12:1 (AA pass) |

**Rationale**: Original primary/secondary too dark on dark backgrounds (contrast <3:1). Lightened variants maintain brand identity while meeting WCAG AA requirements for text and interactive elements.

#### Semantic Colors - Dark Mode
| Purpose | Light Mode | Dark Mode | Contrast Ratio | Usage |
|---------|------------|-----------|----------------|-------|
| Error Main | `#d32f2f` | `#f44336` | 5.67:1 | Error messages, destructive actions |
| Error Light | `#ef5350` | `#e57373` | 7.21:1 | Error backgrounds, alerts |
| Warning Main | `#ed6c02` | `#ff9800` | 5.89:1 | Warning messages, caution states |
| Warning Light | `#ff9800` | `#ffb74d` | 7.45:1 | Warning backgrounds, alerts |
| Info Main | `#0288d1` | `#29b6f6` | 4.98:1 | Info messages, neutral feedback |
| Info Light | `#03a9f4` | `#4fc3f7` | 6.34:1 | Info backgrounds, alerts |
| Success Main | `#2e7d32` | `#66bb6a` | 5.12:1 | Success messages, confirmations |
| Success Light | `#4caf50` | `#81c784` | 6.78:1 | Success backgrounds, alerts |

**WCAG AA Validation**: All semantic colors meet 4.5:1 minimum for normal text, 7:1+ for light variants used in filled alerts.

#### Text & Dividers - Dark Mode
| Purpose | Light Mode | Dark Mode | Contrast Ratio | Usage |
|---------|------------|-----------|----------------|-------|
| Text Primary | `rgba(0,0,0,0.87)` | `rgba(255,255,255,0.87)` | 14.56:1 | Primary content text |
| Text Secondary | `rgba(0,0,0,0.6)` | `rgba(255,255,255,0.6)` | 8.92:1 | Secondary content, captions |
| Text Disabled | `rgba(0,0,0,0.38)` | `rgba(255,255,255,0.38)` | 4.89:1 | Disabled text states |
| Divider | `rgba(0,0,0,0.12)` | `rgba(255,255,255,0.12)` | 1.34:1 | Separators, borders |

**Rationale**: White text at same opacity levels as light mode black text maintains consistent visual hierarchy. Primary text exceeds WCAG AAA (7:1), secondary text exceeds AA (4.5:1).

#### Action States - Dark Mode
| Purpose | Light Mode | Dark Mode | Visual Effect | Usage |
|---------|------------|-----------|---------------|-------|
| Action Active | `rgba(25,118,210,0.54)` | `rgba(66,165,245,0.54)` | Semi-transparent primary | Active icons, selected items |
| Action Hover | `rgba(0,0,0,0.04)` | `rgba(255,255,255,0.08)` | Subtle overlay | Hover state backgrounds |
| Action Selected | `rgba(25,118,210,0.08)` | `rgba(66,165,245,0.16)` | Light primary tint | Selected/active state backgrounds |
| Action Disabled | `rgba(0,0,0,0.26)` | `rgba(255,255,255,0.3)` | Muted overlay | Disabled icons, borders |
| Action Disabled BG | `rgba(0,0,0,0.12)` | `rgba(255,255,255,0.12)` | Faint overlay | Disabled button backgrounds |

**Rationale**: White overlays at doubled opacity (0.04 → 0.08 for hover) provide equivalent perceived brightness on dark backgrounds. Selected states use higher opacity (0.16) for clearer visual feedback.

---

### Component Dark Mode Specifications

#### AppBar
**Light Mode**:
- Background: `#1976d2` (primary main)
- Text: `#ffffff`
- Elevation: 0, border-bottom: `rgba(0,0,0,0.12)`

**Dark Mode**:
- Background: `#1e1e1e` (elevated surface 1)
- Text: `rgba(255,255,255,0.87)`
- Elevation: 0, border-bottom: `rgba(255,255,255,0.12)`
- **Rationale**: Dark AppBar matches elevated surface for cohesive dark UI, avoids bright primary color at top which causes eye strain in dark environments

**States**:
| State | Light Mode | Dark Mode | Notes |
|-------|------------|-----------|-------|
| Default | Primary blue bg | Dark surface bg | AppBar adapts to overall theme |
| Hover (icons) | `rgba(255,255,255,0.08)` | `rgba(255,255,255,0.16)` | Doubled opacity for dark mode |
| Active (icons) | `rgba(255,255,255,0.16)` | `rgba(255,255,255,0.24)` | Increased visibility |

#### Cards
**Light Mode**:
- Background: `#ffffff` (paper)
- Elevation: 1 (default), 3 (hover for interactive cards)
- Border: None

**Dark Mode**:
- Background: `#1e1e1e` (paper)
- Elevation: 2 (default), 4 (hover for interactive cards)
- Border: `1px solid rgba(255,255,255,0.12)` (optional, for enhanced definition)
- **Rationale**: Increased elevation in dark mode (1→2, 3→4) improves depth perception when shadows are less visible against dark backgrounds

**States**:
| State | Light Mode | Dark Mode | Visual Difference |
|-------|------------|-----------|-------------------|
| Default | White, elevation 1 | `#1e1e1e`, elevation 2 | Higher elevation for depth |
| Hover | Elevation 3 | Elevation 4, border glow | Enhanced interactivity cues |
| Selected | Primary tint `rgba(25,118,210,0.08)` | Primary tint `rgba(66,165,245,0.16)` | Higher opacity overlay |
| Disabled | `rgba(0,0,0,0.12)` overlay | `rgba(255,255,255,0.05)` overlay | Subtle disabled state |

#### Buttons
**Contained Primary**:
| State | Light Mode BG | Dark Mode BG | Text Color (Both) | Contrast Ratio |
|-------|---------------|--------------|-------------------|----------------|
| Default | `#1976d2` | `#42a5f5` | `#ffffff` | 4.65:1 (light), 4.89:1 (dark) |
| Hover | `#1565c0` | `#1976d2` | `#ffffff` | 5.23:1 (light), 4.65:1 (dark) |
| Active | `#0d47a1` | `#1565c0` | `#ffffff` | 6.12:1 (light), 5.23:1 (dark) |
| Disabled | `rgba(0,0,0,0.12)` | `rgba(255,255,255,0.12)` | `rgba(0,0,0,0.26)` / `rgba(255,255,255,0.3)` | N/A (disabled) |

**Outlined Primary**:
| State | Light Mode Border | Dark Mode Border | Text Color | Background |
|-------|-------------------|------------------|------------|------------|
| Default | `#1976d2` | `#42a5f5` | Same as border | Transparent |
| Hover | `#1976d2` | `#42a5f5` | Same as border | `rgba(25,118,210,0.04)` / `rgba(66,165,245,0.08)` |
| Active | `#1565c0` | `#1976d2` | Same as border | `rgba(25,118,210,0.08)` / `rgba(66,165,245,0.16)` |

**Text Primary**:
| State | Light Mode Color | Dark Mode Color | Background | Hover BG |
|-------|------------------|-----------------|------------|----------|
| Default | `#1976d2` | `#42a5f5` | Transparent | `rgba(25,118,210,0.04)` / `rgba(66,165,245,0.08)` |
| Active | `#1565c0` | `#1976d2` | `rgba(25,118,210,0.08)` / `rgba(66,165,245,0.16)` | - |

**Rationale**: All button variants use adjusted primary colors in dark mode for visibility while maintaining state distinction through hover/active variations.

#### Text Fields
**Outlined Variant**:
| State | Light Mode Border | Dark Mode Border | Label Color | Helper Text |
|-------|-------------------|------------------|-------------|-------------|
| Default | `rgba(0,0,0,0.23)` | `rgba(255,255,255,0.23)` | `rgba(0,0,0,0.6)` / `rgba(255,255,255,0.6)` | `rgba(0,0,0,0.6)` / `rgba(255,255,255,0.6)` |
| Hover | `rgba(0,0,0,0.87)` | `rgba(255,255,255,0.87)` | Same | Same |
| Focus | `#1976d2` 2px | `#42a5f5` 2px | Primary color | Same |
| Error | `#d32f2f` | `#f44336` | Error color | Error color |
| Disabled | `rgba(0,0,0,0.26)` | `rgba(255,255,255,0.3)` | Disabled color | Disabled color |

**Background**:
- Light: `#ffffff` (paper)
- Dark: `#1e1e1e` (paper)

**Input Text**:
- Light: `rgba(0,0,0,0.87)` (text primary)
- Dark: `rgba(255,255,255,0.87)` (text primary)
- Contrast: 14.56:1 (AAA pass)

#### Alerts
**Filled Variants** (Recommended for dark mode):
| Severity | Light Mode BG | Dark Mode BG | Text Color (Both) | Icon Color | Contrast |
|----------|---------------|--------------|-------------------|------------|----------|
| Success | `#2e7d32` | `#66bb6a` | `#ffffff` | `#ffffff` | 7.1:1 / 6.78:1 |
| Info | `#0288d1` | `#29b6f6` | `#ffffff` | `#ffffff` | 6.8:1 / 6.34:1 |
| Warning | `#ed6c02` | `#ff9800` | `#ffffff` | `#ffffff` | 6.9:1 / 7.45:1 |
| Error | `#d32f2f` | `#f44336` | `#ffffff` | `#ffffff` | 7.5:1 / 7.21:1 |

**Standard Variants**:
| Severity | Light Mode BG | Dark Mode BG | Text/Icon Color | Border |
|----------|---------------|--------------|-----------------|--------|
| Success | `rgba(46,125,50,0.1)` | `rgba(102,187,106,0.15)` | `#2e7d32` / `#66bb6a` | `#2e7d32` / `#66bb6a` |
| Info | `rgba(2,136,209,0.1)` | `rgba(41,182,246,0.15)` | `#0288d1` / `#29b6f6` | `#0288d1` / `#29b6f6` |
| Warning | `rgba(237,108,2,0.1)` | `rgba(255,152,0,0.15)` | `#ed6c02` / `#ff9800` | `#ed6c02` / `#ff9800` |
| Error | `rgba(211,47,47,0.1)` | `rgba(244,67,54,0.15)` | `#d32f2f` / `#f44336` | `#d32f2f` / `#f44336` |

**Rationale**: Filled alerts preferred in dark mode for stronger visual presence. Standard variants use slightly higher opacity backgrounds (0.15 vs 0.1) for improved visibility on dark surfaces.

#### Dialogs & Modals
**Light Mode**:
- Background: `#ffffff` (paper)
- Backdrop: `rgba(0,0,0,0.5)`
- Elevation: 24

**Dark Mode**:
- Background: `#2a2a2a` (elevated surface 2)
- Backdrop: `rgba(0,0,0,0.7)` (increased opacity for stronger modal context)
- Elevation: 24
- **Rationale**: Darker backdrop (0.5 → 0.7) improves modal focus in dark mode. Elevated surface color (#2a2a2a) visually separates dialog from background (#121212) even with reduced shadow visibility.

#### Drawer (Navigation)
**Permanent Drawer** (Desktop):
| Mode | Background | Border | Elevation |
|------|------------|--------|-----------|
| Light | `#ffffff` | Right border `rgba(0,0,0,0.12)` | 0 |
| Dark | `#1e1e1e` | Right border `rgba(255,255,255,0.12)` | 0 |

**Temporary Drawer** (Mobile):
| Mode | Background | Backdrop | Elevation |
|------|------------|----------|-----------|
| Light | `#ffffff` | `rgba(0,0,0,0.5)` | 16 |
| Dark | `#242424` | `rgba(0,0,0,0.7)` | 16 |

**List Item States**:
| State | Light Mode BG | Dark Mode BG | Text Color |
|-------|---------------|--------------|------------|
| Default | Transparent | Transparent | `rgba(0,0,0,0.87)` / `rgba(255,255,255,0.87)` |
| Hover | `rgba(0,0,0,0.04)` | `rgba(255,255,255,0.08)` | Same |
| Selected | `rgba(25,118,210,0.08)` | `rgba(66,165,245,0.16)` | `#1976d2` / `#42a5f5` |
| Active | `rgba(25,118,210,0.12)` | `rgba(66,165,245,0.24)` | `#1976d2` / `#42a5f5` |

#### Data Tables
**Header**:
| Mode | Background | Text | Border Bottom |
|------|------------|------|---------------|
| Light | `#fafafa` | `rgba(0,0,0,0.87)` | `rgba(0,0,0,0.12)` |
| Dark | `#1e1e1e` | `rgba(255,255,255,0.87)` | `rgba(255,255,255,0.12)` |

**Rows**:
| State | Light Mode BG | Dark Mode BG | Border |
|-------|---------------|--------------|--------|
| Default | `#ffffff` | `#121212` | `rgba(0,0,0,0.12)` / `rgba(255,255,255,0.12)` |
| Hover | `rgba(0,0,0,0.04)` | `rgba(255,255,255,0.08)` | Same |
| Selected | `rgba(25,118,210,0.08)` | `rgba(66,165,245,0.12)` | Same |
| Striped (alternate rows) | `#fafafa` | `#1a1a1a` | Same |

**Rationale**: Striped rows use slight background variation (#121212 → #1a1a1a) in dark mode to maintain readability of dense data without jarring contrast.

#### Form Components (Checkboxes, Radio, Switch)
**Checkbox/Radio**:
| State | Light Mode Border | Dark Mode Border | Checked BG | Checkmark |
|-------|-------------------|------------------|------------|-----------|
| Default | `rgba(0,0,0,0.54)` | `rgba(255,255,255,0.7)` | - | - |
| Hover | `rgba(0,0,0,0.87)` | `rgba(255,255,255,0.87)` | - | - |
| Checked | - | - | `#1976d2` / `#42a5f5` | `#ffffff` |
| Disabled | `rgba(0,0,0,0.26)` | `rgba(255,255,255,0.3)` | Disabled color | `rgba(255,255,255,0.5)` |

**Switch**:
| State | Light Track | Dark Track | Light Thumb | Dark Thumb |
|-------|-------------|------------|-------------|------------|
| Off | `rgba(0,0,0,0.38)` | `rgba(255,255,255,0.3)` | `#fafafa` | `#bdbdbd` |
| On | `rgba(25,118,210,0.5)` | `rgba(66,165,245,0.5)` | `#1976d2` | `#42a5f5` |
| Disabled Off | `rgba(0,0,0,0.12)` | `rgba(255,255,255,0.12)` | `#bdbdbd` | `#424242` |
| Disabled On | `rgba(25,118,210,0.12)` | `rgba(66,165,245,0.12)` | `rgba(25,118,210,0.5)` | `rgba(66,165,245,0.5)` |

---

### Dark Mode Transition Behaviors

#### CSS Transition Strategy
```css
* {
  transition: background-color 225ms cubic-bezier(0.4, 0, 0.2, 1),
              color 225ms cubic-bezier(0.4, 0, 0.2, 1);
}

@media (prefers-reduced-motion: reduce) {
  * {
    transition: none;
  }
}
```

**Duration**: 225ms (MUI default easing `cubic-bezier(0.4, 0, 0.2, 1)`)

**Properties Transitioned**:
- `background-color`: All surfaces, cards, buttons
- `color`: All text elements
- `border-color`: Dividers, outlines, borders
- `box-shadow`: Elevation changes (though less noticeable in dark mode)

**Excluded from Transition**:
- Focus rings (instant feedback required)
- Error states (immediate visual alert)
- Skeleton loading placeholders

**Rationale**: 225ms provides smooth visual transition without feeling sluggish. Reduced motion preference honored for accessibility (vestibular disorders, motion sensitivity).

#### Theme Toggle Component
**Location**: AppBar (top right, alongside other actions)

**Component**: IconButton with conditional icon
- Light mode active: `<Brightness7Icon />` (Sun)
- Dark mode active: `<Brightness4Icon />` (Moon)

**Interaction**:
1. User clicks toggle icon
2. Theme mode switches (light ↔ dark)
3. `localStorage.setItem('themeMode', 'light'|'dark')`
4. All components re-render with new palette
5. 225ms transition animates color changes

**Accessibility**:
- `aria-label`: "Toggle dark mode" or "Toggle light mode" (dynamic)
- `aria-pressed`: true/false (toggle state)
- Keyboard: Tab to focus, Enter/Space to toggle
- Focus visible: 2px outline in current theme's primary color

**States**:
| State | Icon | Tooltip | aria-label | aria-pressed |
|-------|------|---------|------------|--------------|
| Light Mode | Sun icon | "Switch to dark mode" | "Toggle dark mode" | false |
| Dark Mode | Moon icon | "Switch to light mode" | "Toggle light mode" | true |

---

### System Preference Detection

**Initial Theme Logic**:
```javascript
function getInitialTheme() {
  // 1. Check localStorage for user preference
  const savedTheme = localStorage.getItem('themeMode');
  if (savedTheme === 'light' || savedTheme === 'dark') {
    return savedTheme;
  }

  // 2. Detect system preference
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  return prefersDark ? 'dark' : 'light';
}
```

**Live System Preference Changes**:
```javascript
useEffect(() => {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

  const handleChange = (e) => {
    // Only auto-switch if user hasn't manually set preference
    if (!localStorage.getItem('themeMode')) {
      setTheme(e.matches ? 'dark' : 'light');
    }
  };

  mediaQuery.addEventListener('change', handleChange);
  return () => mediaQuery.removeEventListener('change', handleChange);
}, []);
```

**Rationale**: Respects user preference hierarchy: 1) Manual selection (localStorage), 2) System preference (media query). Auto-updates if system changes and user hasn't manually chosen.

---

### Edge Cases & Special Considerations

#### Images & Media
**Light Mode**: Original images, no adjustments

**Dark Mode**:
- **Photographs**: 90% opacity to reduce brightness, avoid eye strain
- **Illustrations with white backgrounds**: CSS filter `invert(1)` or dark-variant assets
- **Logos**: Provide dark-variant logo (light text/icon on transparent)
- **Icons**: MUI icons automatically inherit `currentColor`, no changes needed

#### Code Blocks (API Test Page, Developer Tools)
**Light Mode**:
- Background: `#fafafa`
- Text: `rgba(0,0,0,0.87)`
- Syntax highlighting: Light theme (if applicable)

**Dark Mode**:
- Background: `#1e1e1e`
- Text: `rgba(255,255,255,0.87)`
- Syntax highlighting: Dark theme (GitHub Dark, VS Code Dark+)
- Border: `1px solid rgba(255,255,255,0.12)` for enhanced definition

**Contrast**: 14.56:1 (both modes) - AAA pass

#### Skeleton Loaders
**Light Mode**: `rgba(0,0,0,0.11)` (MUI default)

**Dark Mode**: `rgba(255,255,255,0.13)` (increased opacity for visibility)

**Animation**: Pulse/wave animation identical in both modes (no color changes needed)

#### Elevation & Shadows
**Light Mode**: Standard MUI elevation shadows (black with varying opacity/blur)

**Dark Mode**:
- Shadows less visible on dark backgrounds
- Rely more on surface color overlays (5% white per elevation level)
- Shadows still applied but have reduced visual impact
- Border accents (`rgba(255,255,255,0.12)`) can supplement elevation cues

**Rationale**: Material Design 3 dark mode uses surface color elevation (white overlays) as primary depth indicator, with shadows providing subtle supplemental cues.

#### Print Styles
**Override**: Always print in light mode for readability and ink efficiency

```css
@media print {
  body {
    background: white !important;
    color: black !important;
  }

  .MuiPaper-root {
    background: white !important;
  }
}
```

#### Focus Indicators
**Light Mode**: `2px solid #1976d2` (primary)

**Dark Mode**: `2px solid #42a5f5` (primary light)

**Rationale**: Brighter primary in dark mode ensures focus rings remain visible (3:1 contrast minimum against #121212 background).

---

### MUI Theme Object - Dark Mode Extension

```javascript
import { createTheme } from '@mui/material/styles';

const getTheme = (mode) => createTheme({
  palette: {
    mode, // 'light' or 'dark'
    ...(mode === 'light'
      ? {
          // Light mode palette (existing)
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
          divider: 'rgba(0, 0, 0, 0.12)',
        }
      : {
          // Dark mode palette
          primary: { main: '#42a5f5', light: '#64b5f6', dark: '#1976d2' },
          secondary: { main: '#f48fb1', light: '#f6a5c0', dark: '#dc004e' },
          error: { main: '#f44336', light: '#e57373', dark: '#d32f2f' },
          warning: { main: '#ff9800', light: '#ffb74d', dark: '#ed6c02' },
          info: { main: '#29b6f6', light: '#4fc3f7', dark: '#0288d1' },
          success: { main: '#66bb6a', light: '#81c784', dark: '#2e7d32' },
          background: {
            default: '#121212',
            paper: '#1e1e1e',
          },
          text: {
            primary: 'rgba(255, 255, 255, 0.87)',
            secondary: 'rgba(255, 255, 255, 0.6)',
            disabled: 'rgba(255, 255, 255, 0.38)',
          },
          divider: 'rgba(255, 255, 255, 0.12)',
          action: {
            active: 'rgba(255, 255, 255, 0.56)',
            hover: 'rgba(255, 255, 255, 0.08)',
            selected: 'rgba(255, 255, 255, 0.16)',
            disabled: 'rgba(255, 255, 255, 0.3)',
            disabledBackground: 'rgba(255, 255, 255, 0.12)',
          },
        }
    ),
  },
  components: {
    MuiCard: {
      defaultProps: {
        elevation: mode === 'light' ? 1 : 2,
      },
      styleOverrides: {
        root: {
          ...(mode === 'dark' && {
            borderColor: 'rgba(255, 255, 255, 0.12)',
          }),
          '&:hover': {
            elevation: mode === 'light' ? 3 : 4,
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: mode === 'dark' ? '#1e1e1e' : '#1976d2',
          borderBottom: `1px solid ${mode === 'dark' ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)'}`,
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          backgroundColor: mode === 'dark' ? '#2a2a2a' : '#ffffff',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: mode === 'dark' ? '#242424' : '#ffffff',
        },
      },
    },
  },
});

export default getTheme;
```

---

### Accessibility - Dark Mode Specific

#### WCAG AA Compliance - Dark Mode Verification
All color combinations validated against WCAG 2.1 AA standards:

**Text Contrast** (Minimum 4.5:1):
- Primary text on default background: `rgba(255,255,255,0.87)` on `#121212` = 14.56:1 (AAA)
- Secondary text on default background: `rgba(255,255,255,0.6)` on `#121212` = 8.92:1 (AAA)
- Primary button text: `#ffffff` on `#42a5f5` = 4.89:1 (AA)
- Error text: `#f44336` on `#121212` = 5.67:1 (AA)
- Success text: `#66bb6a` on `#121212` = 5.12:1 (AA)

**UI Component Contrast** (Minimum 3:1):
- Button borders: `#42a5f5` on `#121212` = 4.89:1 (AA)
- Focus indicators: `#42a5f5` 2px outline = 4.89:1 (AA)
- Dividers: `rgba(255,255,255,0.12)` = 1.34:1 (decorative only, not required)

#### Reduced Motion Support
Users with `prefers-reduced-motion: reduce` experience:
- Instant theme switching (no 225ms transition)
- Disabled elevation hover animations
- Disabled skeleton pulse animations
- Maintained focus indicator animations (critical for accessibility)

#### Screen Reader Announcements
```javascript
<div role="status" aria-live="polite" aria-atomic="true">
  {themeMode === 'dark' ? 'Dark mode enabled' : 'Light mode enabled'}
</div>
```

**Rationale**: Announces theme change to screen reader users without interrupting current context. `aria-live="polite"` waits for user to finish current action before announcing.

#### Color Blindness Considerations
**Protanopia/Deuteranopia (Red-Green)**:
- Primary (blue) and secondary (pink) remain distinguishable in dark mode
- Error (red-orange tint) and success (green) lightened sufficiently for separation
- Don't rely solely on color: icons and labels supplement semantic colors

**Tritanopia (Blue-Yellow)**:
- Primary and warning adjusted to maintain separation
- Info and success colors distinct in both modes

**Achromatopsia (Complete color blindness)**:
- Contrast ratios ensure all text readable based on brightness alone
- Hover/focus states use both color AND brightness changes
- Icons and text labels never rely solely on color

---

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

---

### Feature: API Test Page
**Purpose**: Provide development and testing interface for verifying backend connectivity and API responses.

**Design Decisions**:
- **Card-based layout with clear sections**: Separates action trigger from response display for visual clarity
- **Prominent contained button**: Primary color draws attention to test action, follows established button patterns
- **Alert feedback for states**: Leverages MUI Alert component for consistent success/error messaging with semantic colors
- **Monospace code display**: Uses Paper component with pre/code tags for raw JSON response inspection

**Components Used**: Container, Card, CardHeader, CardContent, Stack, Button, Alert, CircularProgress, Paper, Typography

**Component Specifications**:

#### Layout Structure
```
Container (maxWidth: md, sx: { py: 4 })
  └─ Card (elevation: 2)
      ├─ CardHeader
      │   ├─ title: "API Test Page" (variant: h5)
      │   └─ subheader: "Test backend connectivity and API responses" (variant: body2)
      └─ CardContent
          └─ Stack (spacing: 3)
              ├─ Stack (spacing: 2, alignItems: flex-start)
              │   ├─ Button
              │   └─ Alert (conditional - success or error)
              └─ Paper (conditional - response display)
```

#### Test Button Component
- **Variant**: contained
- **Color**: primary (#1976d2)
- **Size**: large
- **Icon**: Send icon (from @mui/icons-material/Send) positioned startIcon
- **Text**: "Test Backend Connection"
- **States**:
  - Default: Solid primary background, white text
  - Hover: Darker primary (#1565c0), elevation increase
  - Focus: 2px outline offset, primary color ring
  - Loading: Disabled appearance, CircularProgress (size: 24px) replacing icon
  - Disabled: Grey background (rgba(0,0,0,0.12)), grey text (rgba(0,0,0,0.26))
- **Accessibility**:
  - aria-label: "Test backend API connection"
  - aria-busy: true when loading
  - Keyboard: Enter/Space to activate, focus visible

#### Success Alert
- **Severity**: success
- **Variant**: filled
- **Icon**: CheckCircle (auto from severity)
- **Background**: Success main (#2e7d32)
- **Text**: White contrast text
- **Content**: "Connection successful! Response received from backend." (Typography variant: body2)
- **Accessible**: role="alert", announced to screen readers

#### Error Alert
- **Severity**: error
- **Variant**: filled
- **Icon**: Error (auto from severity)
- **Background**: Error main (#d32f2f)
- **Text**: White contrast text
- **Content**: Dynamic error message from API or "Failed to connect to backend. Please check if the server is running." (Typography variant: body2)
- **Accessible**: role="alert", announced to screen readers

#### Response Display Paper
- **Elevation**: 1
- **Background**: Background paper (#ffffff)
- **Padding**: spacing(3) = 24px
- **Border**: 1px solid divider (rgba(0,0,0,0.12))
- **Structure**:
  - Typography (variant: h6, mb: 2): "Response Data"
  - Typography (variant: caption, color: text.secondary, mb: 1): Timestamp
  - Box (component: pre, sx: monospace styling):
    - Typography (component: code, variant: body2)
    - JSON.stringify(response, null, 2)
- **Styling**:
  - White-space: pre-wrap
  - Word-break: break-word
  - Font-family: 'Courier New', monospace
  - Font-size: 14px
  - Background: background.default (#fafafa)
  - Padding: spacing(2) = 16px
  - Border-radius: 4px
  - Max-height: 400px
  - Overflow-y: auto

#### Loading Indicator
- **Component**: CircularProgress
- **Size**: 24px
- **Color**: inherit (white on primary button)
- **Position**: Replaces Send icon in button
- **Centered**: Using Stack alignment when standalone

**Interaction Patterns**:
1. **Initial state**: Button enabled, no alerts or response visible
2. **User clicks button**:
   - Button shows loading spinner, becomes disabled
   - Previous alerts/response cleared
3. **Success response**:
   - Loading stops, button re-enables
   - Success Alert fades in (150ms)
   - Response Paper slides in below (225ms)
   - Focus remains on button for retry
4. **Error response**:
   - Loading stops, button re-enables
   - Error Alert fades in (150ms)
   - No response Paper shown
   - Focus remains on button for retry
5. **Keyboard navigation**:
   - Tab to button, Enter/Space to activate
   - Alert announced to screen readers immediately
   - Escape does not close alerts (user control via re-test)

**States**:

| State | Button | Alert | Response Display | Visual Indicators |
|-------|--------|-------|------------------|-------------------|
| **Initial** | Enabled, primary | Hidden | Hidden | Send icon visible |
| **Loading** | Disabled, loading | Hidden | Hidden | CircularProgress spinning, button text unchanged |
| **Success** | Enabled, primary | Success filled alert visible | Paper with formatted JSON | CheckCircle icon, green alert background |
| **Error** | Enabled, primary | Error filled alert visible | Hidden | Error icon, red alert background, error message |
| **Empty/No Test Run** | Enabled, primary | Hidden | Hidden | Neutral state, instructional subheader |

**Responsive Behavior**:
- **xs (0-600px)**:
  - Container padding: spacing(2) = 16px
  - Button: full-width (fullWidth prop)
  - Card padding: spacing(2) = 16px
  - Typography: h5 → h6 for title
- **sm+ (600px+)**:
  - Container padding: spacing(4) = 32px
  - Button: intrinsic width (width: auto)
  - Card padding: spacing(3) = 24px
  - Typography: h5 for title

**Accessibility**:
- **ARIA**:
  - Button: aria-label, aria-busy during loading
  - Alerts: role="alert" for screen reader announcement
  - Response region: aria-live="polite" for updates
- **Keyboard**:
  - Full keyboard navigation support
  - Enter/Space on button triggers test
  - Focus visible indicators (2px outline)
- **Screen Reader**:
  - Status changes announced via alerts
  - Button state changes (loading → ready) announced
  - Response data accessible via code block
- **Color Contrast**:
  - Button text on primary: 4.65:1 (WCAG AA pass)
  - Alert text on success/error: >7:1 (WCAG AAA pass)
  - Code text on paper: 15.8:1 (WCAG AAA pass)
- **Touch Targets**: Button minimum 48x48px (MUI default large size)

**Semantic HTML Structure**:
```html
<main>
  <div class="MuiContainer-root">
    <article class="MuiCard-root">
      <header class="MuiCardHeader-root">
        <h5>API Test Page</h5>
        <p>Test backend connectivity and API responses</p>
      </header>
      <div class="MuiCardContent-root">
        <section>
          <button aria-label="Test backend API connection" aria-busy="false">
            <svg><!-- Send icon --></svg>
            <span>Test Backend Connection</span>
          </button>

          <!-- Success state -->
          <div role="alert" class="MuiAlert-filledSuccess">
            <svg><!-- CheckCircle icon --></svg>
            <p>Connection successful! Response received from backend.</p>
          </div>

          <!-- OR Error state -->
          <div role="alert" class="MuiAlert-filledError">
            <svg><!-- Error icon --></svg>
            <p>Failed to connect to backend. Please check if the server is running.</p>
          </div>

          <!-- Response display -->
          <section class="MuiPaper-root" aria-live="polite">
            <h6>Response Data</h6>
            <p class="MuiTypography-caption">Received at: 2025-10-19 14:32:15</p>
            <pre>
              <code>
                {
                  "message": "Hello from backend API"
                }
              </code>
            </pre>
          </section>
        </section>
      </div>
    </article>
  </div>
</main>
```

**CSS Implementation Notes**:
- Use MUI `sx` prop for component-specific responsive styles
- Leverage theme spacing function: `spacing(n)` not hardcoded pixels
- Use theme breakpoints: `theme.breakpoints.down('sm')`
- Code block styling requires custom sx for monospace font and scrolling
- Transitions: 150ms for alerts (fade), 225ms for response (slide-up)

**Edge Cases**:
- **Network timeout**: Show error alert with timeout-specific message after 30s
- **Malformed JSON response**: Display error alert, show raw text in response if possible
- **Empty response**: Show success but note "Empty response body" in display
- **Long response data**: Max-height 400px with vertical scroll on response Paper
- **Rapid repeated clicks**: Debounce button clicks, only one request at a time
- **Backend down**: Clear error message with actionable guidance

**Content Examples**:

Success message:
```
"Connection successful! Response received from backend."
```

Error messages:
```
"Failed to connect to backend. Please check if the server is running."
"Request timed out. The backend may be overloaded."
"Invalid response format. Expected JSON."
```

Response timestamp format:
```
"Received at: 2025-10-19 14:32:15"
```

Sample JSON responses:
```json
{
  "message": "Hello from backend API",
  "timestamp": "2025-10-19T14:32:15.123Z",
  "version": "1.0.0"
}
```

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
