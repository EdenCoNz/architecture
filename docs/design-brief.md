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
