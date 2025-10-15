# Styles Directory

Global styles and CSS utilities for the application.

## Philosophy

This project uses **Material UI with Emotion** as the primary styling solution. This directory contains:

- Global CSS resets and base styles
- CSS utility classes (use sparingly)
- Global animations and transitions
- Print styles

## Material UI Styling Approaches

We follow Material UI v6 best practices:

### 1. sx Prop (One-off Customizations)

```tsx
<Box sx={{ mt: 2, color: 'primary.main' }}>Content</Box>
```

### 2. styled() API (Reusable Components)

```tsx
const StyledButton = styled(Button)(({ theme }) => ({
  padding: theme.spacing(2),
  '&:hover': {
    backgroundColor: theme.palette.primary.dark,
  },
}));
```

### 3. Theme Overrides (Global Customization)

```tsx
const theme = createTheme({
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
        },
      },
    },
  },
});
```

## Global Styles

Global styles should be minimal. Most styling should be:

1. Component-scoped using sx prop or styled()
2. Theme-based for consistency
3. Responsive by default

## File Naming Convention

- `global.css` - Global resets and base styles
- `animations.css` - Reusable CSS animations
- `print.css` - Print-specific styles
- `utilities.css` - CSS utility classes (use sparingly)

## Guidelines

1. **Avoid Global CSS**: Prefer component-scoped styles
2. **Use Theme Variables**: Access theme values via sx prop or styled()
3. **Mobile-First**: Write styles for mobile, then scale up
4. **Accessibility**: Ensure sufficient color contrast (4.5:1 for text)
5. **Performance**: Avoid deep nesting and complex selectors
