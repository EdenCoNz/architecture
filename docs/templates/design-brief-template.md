# Application Design Brief

## Overview
- Problem: [1-2 sentences describing the core problem]
- Solution: [1-2 sentences describing the design solution]
- Target users: [Who, primary goals]

## Material UI Theme Configuration
- **Primary Color**: [Hex code and usage rationale]
- **Secondary Color**: [Hex code and usage rationale]
- **Typography**: [Font family, scale configuration]
- **Spacing Scale**: [8px grid or custom]
- **Shape**: [Border radius configuration]
- **Breakpoints**: [Any custom breakpoint modifications]
- **Component Overrides**: [Global MUI component customizations]

## Visual System
- Colors: [Extended palette with hex codes and usage - builds on MUI theme]
- Typography: [Semantic usage - h1-h6, body1-2, button, etc.]
- Spacing: [8px grid system with MUI spacing function]
- Layout: [MUI breakpoints - xs/sm/md/lg/xl usage strategy]

## Component Library
- **MUI Components Used**: [List of MUI components with customization notes]
- **Custom Components**: [Purpose, variants, states]
- **Component Patterns**: [Common compositions and usage patterns]

## Navigation & User Flow
- [Navigation pattern]: [Description]
- [User flow]: [Key paths through the application]

## Features

### Feature: [Feature Name]
**Purpose**: [1 sentence]

**Design Decisions**:
- [Decision 1]: [Why - 1 sentence]
- [Decision 2]: [Why - 1 sentence]

**Components Used**: [List components from library]

**Interaction Patterns**: [Describe key interactions]

**States**: [Loading, empty, error, success states]

---

## Accessibility
- WCAG AA compliance (4.5:1 text contrast, 3:1 UI contrast)
- Keyboard navigation support
- Screen reader considerations
- [Any specific considerations]

## Design Tokens

### MUI Theme Object
```javascript
{
  palette: {
    primary: { main: '#...', light: '#...', dark: '#...' },
    secondary: { main: '#...', light: '#...', dark: '#...' },
    error: { main: '#...' },
    // ... other palette colors
  },
  typography: {
    fontFamily: '...',
    h1: { fontSize: '...', fontWeight: '...' },
    // ... other typography variants
  },
  spacing: 8, // Base unit
  shape: { borderRadius: 4 },
  breakpoints: {
    values: { xs: 0, sm: 600, md: 900, lg: 1200, xl: 1536 }
  }
}
```

### CSS Variables (if using cssVariables: true)
```css
/* MUI generates these automatically from theme */
--mui-palette-primary-main: #...;
--mui-palette-secondary-main: #...;
--mui-spacing: 8px;
```

## Responsive Strategy
- Mobile-first approach (MUI default)
- MUI Breakpoints: xs (0px), sm (600px), md (900px), lg (1200px), xl (1536px)
- Grid System: MUI Grid v6 with size/offset props
- Responsive Typography: clamp() for fluid scaling
- [Key responsive behaviors and component adaptations]
