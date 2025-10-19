# Theme Switching Test Plan

## Story: Test Theme Switching Across All Pages

**Story ID**: Feature #6, Story #6
**Test Date**: 2025-10-19
**Tester**: Frontend Developer Agent

## Test Environment

- **Framework**: React 19
- **UI Library**: Material UI v7
- **Theme System**: Light/Dark mode with system preference detection
- **Testing Tools**: Vitest, React Testing Library
- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)

---

## Application Structure

### Routes and Pages

1. **Home Page** (`/`)
   - Route: `/`
   - Component: `Home.tsx`
   - Description: Landing page with welcome message, feature cards, and navigation buttons

2. **Test Page** (`/test`)
   - Route: `/test`
   - Component: `TestPage.tsx`
   - Description: API connectivity test page with form, buttons, alerts, and code display

3. **404 Not Found** (`*`)
   - Route: `*` (catch-all)
   - Component: `NotFound.tsx`
   - Description: Error page with large typography, icons, and navigation options

### Layout Components

1. **Header**
   - Component: `Header.tsx`
   - Contains: AppBar, Toolbar, Typography, IconButton, ThemeToggle
   - Position: Sticky top navigation across all pages

### Theme Components

1. **ThemeToggle**
   - Component: `ThemeToggle.tsx`
   - Function: Icon button to toggle between light/dark modes
   - Location: Header (top right)

---

## Material UI Components Used

### Typography

- h1, h2, h3, h4, h5, h6
- body1, body2
- caption
- Subtitle typography

### Layout

- Container
- Box
- Paper
- Stack

### Inputs & Controls

- Button (contained, outlined)
- IconButton
- Tooltip

### Feedback

- Alert (success, error variants with filled style)
- CircularProgress

### Surfaces

- Card
- CardHeader
- CardContent
- AppBar
- Toolbar

### Navigation

- React Router Links (styled as buttons)

### Icons

- Material Icons (Home, ErrorOutline, Send, Menu, Brightness7, Brightness4)

---

## Test Categories

### 1. Visual Rendering Tests

#### 1.1 Home Page

- [ ] **Light Mode**: All components render with correct light theme colors
- [ ] **Dark Mode**: All components render with correct dark theme colors
- [ ] **Typography**: Text is readable with proper contrast in both modes
- [ ] **Icons**: HomeIcon displays correctly in both modes
- [ ] **Cards**: Paper components have proper elevation and background
- [ ] **Buttons**: Primary contained and outlined buttons look correct
- [ ] **Spacing**: Layout maintains proper spacing and alignment

#### 1.2 Test Page

- [ ] **Light Mode**: All components render correctly
- [ ] **Dark Mode**: All components render correctly
- [ ] **Card Component**: Card elevation and styling correct
- [ ] **Buttons**: Test button with icon displays properly
- [ ] **Alerts**: Success and error alerts have proper contrast
- [ ] **Code Display**: Pre-formatted code block is readable in both modes
- [ ] **Loading State**: CircularProgress visible in both modes

#### 1.3 NotFound Page

- [ ] **Light Mode**: Error page displays correctly
- [ ] **Dark Mode**: Error page displays correctly
- [ ] **Large Typography**: 404 heading is readable and styled properly
- [ ] **Error Icon**: ErrorOutlineIcon displays with error color
- [ ] **Buttons**: Navigation buttons styled correctly

#### 1.4 Header Component

- [ ] **Light Mode**: AppBar has correct primary color
- [ ] **Dark Mode**: AppBar background and borders correct
- [ ] **Typography**: App title is readable
- [ ] **Theme Toggle**: Icon button displays correct icon for current mode
- [ ] **Menu Icon**: Visible on mobile, hidden on desktop

---

### 2. Component Functionality Tests

#### 2.1 Theme Toggle

- [ ] **Click Toggle**: Theme switches correctly when clicked
- [ ] **Icon Update**: Icon changes from sun to moon (and vice versa)
- [ ] **Tooltip**: Tooltip text updates based on current mode
- [ ] **ARIA Labels**: Accessibility labels update correctly
- [ ] **Keyboard Navigation**: Works with Enter and Space keys

#### 2.2 Theme Persistence

- [ ] **Redux Store**: Theme mode stored correctly in Redux
- [ ] **Initial Load**: Theme preference loaded on app mount
- [ ] **State Consistency**: All components reflect same theme

---

### 3. Transition and Animation Tests

#### 3.1 Theme Switch Transitions

- [ ] **No Flash**: No white flash or jarring transition when switching
- [ ] **Smooth Transition**: Colors transition smoothly (225ms as per design)
- [ ] **All Elements**: All components transition simultaneously
- [ ] **Text Readability**: Text remains readable during transition

#### 3.2 Visual Glitches

- [ ] **No Layout Shift**: Layout doesn't shift during theme change
- [ ] **No Flicker**: No flickering or jumping of components
- [ ] **Icons Stable**: Icons don't resize or jump during transition

---

### 4. Accessibility Tests

#### 4.1 Contrast Ratios (WCAG 2.1 Level AA)

- [ ] **Light Mode Text**: Primary text meets 4.5:1 ratio
- [ ] **Dark Mode Text**: Primary text meets 4.5:1 ratio
- [ ] **UI Components**: Buttons and controls meet 3:1 ratio
- [ ] **Error States**: Error messages have sufficient contrast

#### 4.2 Keyboard Navigation

- [ ] **Theme Toggle**: Focusable and operable via keyboard
- [ ] **All Buttons**: Can be reached and activated via Tab and Enter
- [ ] **Skip Link**: Skip to main content link works in both modes

#### 4.3 Screen Reader Support

- [ ] **ARIA Labels**: Proper labels on interactive elements
- [ ] **Live Regions**: Alerts announced correctly
- [ ] **Semantic HTML**: Proper heading hierarchy maintained

---

### 5. Edge Case Tests

#### 5.1 App States

- [ ] **Initial Load**: Theme applied correctly on first load
- [ ] **Loading State**: CircularProgress visible in both themes
- [ ] **Error State**: Error alerts readable in both themes
- [ ] **Success State**: Success alerts readable in both themes
- [ ] **Empty State**: Components with no content render correctly

#### 5.2 Rapid Interactions

- [ ] **Rapid Toggling**: Multiple rapid clicks handled gracefully
- [ ] **Navigation During Transition**: Navigating while theme changes works
- [ ] **Concurrent Actions**: Other interactions work during theme switch

#### 5.3 System Preference Changes

- [ ] **Auto Mode**: Responds to system preference changes (if implemented)
- [ ] **Manual Override**: Manual selection persists over system preference

---

### 6. Cross-Component Consistency

#### 6.1 Color Palette

- [ ] **Primary Colors**: Consistent across all components
- [ ] **Secondary Colors**: Consistent usage
- [ ] **Error/Warning/Success**: Semantic colors consistent
- [ ] **Backgrounds**: Paper vs default backgrounds correct

#### 6.2 Typography

- [ ] **Font Families**: Consistent across all text
- [ ] **Font Weights**: Proper weights applied
- [ ] **Line Heights**: Readable line spacing maintained

#### 6.3 Spacing

- [ ] **Padding/Margin**: Consistent spacing scale used
- [ ] **Component Gaps**: Stack and Grid gaps consistent

---

### 7. Performance Tests

#### 7.1 Theme Switch Performance

- [ ] **Switch Speed**: Theme switches within 225ms target
- [ ] **No Blocking**: UI remains responsive during switch
- [ ] **Memory**: No memory leaks from repeated switching

#### 7.2 Render Performance

- [ ] **Initial Render**: Fast initial page load in both modes
- [ ] **Re-renders**: Minimal re-renders when theme changes
- [ ] **Theme Memoization**: Theme object properly memoized

---

## Testing Methodology

### Manual Testing

1. Visual inspection of each page in both modes
2. Interactive testing of theme toggle
3. Navigation between pages while in each mode
4. Contrast ratio verification using browser tools

### Automated Testing

1. Component tests for ThemeToggle functionality
2. Integration tests for theme switching across pages
3. Visual regression tests (optional, for CI/CD)
4. Accessibility tests with axe-core

### Browser Testing

1. Chrome (latest)
2. Firefox (latest)
3. Safari (latest)
4. Edge (latest)

---

## Test Execution Log

### Test Run 1: Automated Component Tests

- **Date**: 2025-10-19
- **Status**: To be executed
- **Results**: Pending

### Test Run 2: Manual Visual Testing

- **Date**: 2025-10-19
- **Status**: To be executed
- **Results**: Pending

### Test Run 3: Accessibility Audit

- **Date**: 2025-10-19
- **Status**: To be executed
- **Results**: Pending

---

## Known Issues / Findings

_(To be populated during testing)_

---

## Sign-off

### Test Coverage

- [ ] All pages tested in both modes
- [ ] All components tested in both modes
- [ ] Theme transitions verified
- [ ] Accessibility verified
- [ ] Edge cases covered

### Acceptance Criteria Met

- [ ] All existing pages render correctly in both themes
- [ ] All existing components display properly in both themes
- [ ] Theme transitions are smooth without visual glitches

### Recommendation

- [ ] Ready for production
- [ ] Requires fixes (see issues)
- [ ] Additional testing needed

---

## Appendix

### Color Palette Reference

#### Light Mode

- Primary: #1976d2
- Background Default: #fafafa
- Background Paper: #ffffff
- Text Primary: rgba(0, 0, 0, 0.87)
- Text Secondary: rgba(0, 0, 0, 0.6)

#### Dark Mode

- Primary: #42a5f5
- Background Default: #121212
- Background Paper: #1e1e1e
- Text Primary: rgba(255, 255, 255, 0.87)
- Text Secondary: rgba(255, 255, 255, 0.6)

### WCAG 2.1 AA Requirements

- **Normal text**: 4.5:1 contrast ratio
- **Large text**: 3:1 contrast ratio
- **UI components**: 3:1 contrast ratio
- **Graphical objects**: 3:1 contrast ratio
