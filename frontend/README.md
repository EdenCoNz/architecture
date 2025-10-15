# Frontend Web Application

A modern, scalable frontend web application built with React 19, TypeScript, Material UI, and Vite. This project follows Test-Driven Development (TDD) principles and industry best practices for maintainability, performance, and accessibility.

## Table of Contents

- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Development](#development)
- [Available Scripts](#available-scripts)
- [Project Structure](#project-structure)
- [Development Guidelines](#development-guidelines)
  - [Coding Conventions](#coding-conventions)
  - [Test-Driven Development](#test-driven-development)
  - [Material UI Best Practices](#material-ui-best-practices)
  - [State Management](#state-management)
  - [Accessibility](#accessibility)
- [Testing](#testing)
- [Building for Production](#building-for-production)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Resources](#resources)

## Overview

This application provides a robust foundation for building modern web applications with:

- **Component-based architecture**: Modular, reusable React components
- **Type safety**: Full TypeScript coverage for better developer experience
- **Modern UI**: Material UI v7 with Material Design 3 principles
- **State management**: Redux Toolkit for predictable state updates
- **Routing**: React Router v7 for client-side navigation
- **Testing**: Comprehensive test coverage with Vitest and React Testing Library
- **Code quality**: ESLint and Prettier for consistent code standards
- **Fast development**: Vite for lightning-fast HMR and builds

## Technology Stack

### Core Framework
- **React 19.1.1**: Latest React with improved performance and features
- **TypeScript 5.9**: Static typing for enhanced code quality
- **Vite 7.1**: Next-generation frontend build tool

### UI Framework
- **Material UI 7.3**: Comprehensive React component library
- **Emotion 11.14**: CSS-in-JS styling solution
- **Material Icons**: Official Material Design icon set

### State & Routing
- **Redux Toolkit 2.9**: Modern Redux state management
- **React Router 7.9**: Declarative routing for React

### Testing
- **Vitest 3.2**: Fast unit test framework powered by Vite
- **React Testing Library 16.3**: User-centric component testing
- **jsdom 27.0**: DOM implementation for Node.js

### Code Quality
- **ESLint 9.36**: Linting for code quality
- **Prettier 3.6**: Opinionated code formatting
- **TypeScript ESLint 8.45**: TypeScript-specific linting rules

## Getting Started

### Prerequisites

Ensure you have the following installed:

- **Node.js**: v20.x or higher (LTS recommended)
- **npm**: v10.x or higher (comes with Node.js)
- **Git**: For version control

Check your versions:

```bash
node --version  # Should be v20.x or higher
npm --version   # Should be v10.x or higher
```

### Installation

1. **Navigate to the frontend directory**:

```bash
cd frontend
```

2. **Install dependencies**:

```bash
npm install
```

This will install all dependencies listed in `package.json` and may take a few minutes on first run.

3. **Verify installation**:

```bash
npm run dev
```

If successful, you should see output indicating the dev server is running, typically at `http://localhost:5173`.

### Development

Start the development server with hot module replacement (HMR):

```bash
npm run dev
```

The application will be available at:
- **Local**: http://localhost:5173
- **Network**: Check terminal output for network URL

Changes to source files will automatically reload in the browser.

## Available Scripts

### Development Scripts

#### `npm run dev`
Starts the Vite development server with hot module replacement.

```bash
npm run dev
```

- Opens the app at http://localhost:5173
- Automatically reloads on file changes
- Shows build errors and warnings in browser and terminal

#### `npm run preview`
Preview the production build locally before deployment.

```bash
npm run preview
```

- Runs after `npm run build`
- Serves the built files from `dist/`
- Tests production build behavior

### Build Scripts

#### `npm run build`
Creates an optimized production build.

```bash
npm run build
```

- Compiles TypeScript (`tsc -b`)
- Bundles and minifies code with Vite
- Outputs to `dist/` directory
- Optimizes assets (images, CSS, JS)
- Generates source maps for debugging

**Output**: `dist/` directory ready for deployment

### Code Quality Scripts

#### `npm run lint`
Runs ESLint to check code quality and identify issues.

```bash
npm run lint
```

- Checks all `.ts` and `.tsx` files
- Reports errors and warnings
- Does not modify files

#### `npm run lint:fix`
Automatically fixes ESLint issues where possible.

```bash
npm run lint:fix
```

- Fixes auto-fixable issues (formatting, unused imports, etc.)
- Reports remaining issues that require manual fixes
- Modifies files in place

#### `npm run format`
Formats code using Prettier.

```bash
npm run format
```

- Applies Prettier formatting to all source files
- Formats TypeScript, JavaScript, JSON, CSS, and Markdown
- Modifies files in place

#### `npm run format:check`
Checks if code is formatted correctly without modifying files.

```bash
npm run format:check
```

- Useful in CI/CD pipelines
- Reports formatting issues
- Does not modify files
- Returns exit code 1 if formatting issues found

### Testing Scripts

#### `npm test` or `npm run test`
Runs tests in watch mode.

```bash
npm test
```

- Watches for file changes
- Re-runs affected tests automatically
- Interactive test runner
- Press 'a' to run all tests, 'q' to quit

#### `npm run test:ui`
Opens Vitest UI for interactive test exploration.

```bash
npm run test:ui
```

- Browser-based test interface
- Visual test results and coverage
- Filter and search tests
- View test execution time

#### `npm run test:run`
Runs all tests once (no watch mode).

```bash
npm run test:run
```

- Runs entire test suite
- Useful for CI/CD pipelines
- Exits after completion
- Returns exit code based on test results

#### `npm run test:coverage`
Generates test coverage report.

```bash
npm run test:coverage
```

- Runs all tests with coverage collection
- Generates HTML, JSON, and text reports
- Opens coverage/index.html in browser
- Shows line, branch, function, and statement coverage

**Coverage thresholds**:
- Target: 80% coverage minimum
- View detailed report: `coverage/index.html`

## Project Structure

```
frontend/
├── public/                    # Static assets (served directly)
│   └── vite.svg              # Favicon and static files
├── src/                       # Source code
│   ├── assets/               # Images, icons, fonts
│   ├── components/           # Reusable UI components
│   │   ├── common/          # Generic components (Button, Card, etc.)
│   │   ├── layout/          # Layout components (Header, Footer)
│   │   ├── forms/           # Form components (Input, Select)
│   │   └── feedback/        # Feedback components (Toast, Alert)
│   ├── pages/               # Route-level page components
│   │   ├── Home/            # Home page
│   │   └── NotFound/        # 404 page
│   ├── features/            # Feature-based modules (optional)
│   ├── hooks/               # Custom React hooks
│   ├── utils/               # Utility functions
│   ├── services/            # API clients and services
│   ├── store/               # Redux state management
│   │   ├── slices/         # Redux Toolkit slices
│   │   └── middleware/     # Custom middleware
│   ├── theme/               # Material UI theme configuration
│   ├── styles/              # Global CSS (minimal)
│   ├── types/               # TypeScript type definitions
│   ├── constants/           # Application constants
│   ├── App.tsx              # Root component
│   └── main.tsx             # Application entry point
├── tests/                    # Test files
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   ├── e2e/                 # End-to-end tests
│   ├── utils/               # Test utilities and helpers
│   └── fixtures/            # Mock data
├── dist/                     # Production build (generated)
├── node_modules/             # Dependencies (generated)
├── index.html               # Entry HTML file
├── package.json             # Dependencies and scripts
├── vite.config.ts           # Vite configuration
├── tsconfig.json            # TypeScript configuration
├── eslint.config.js         # ESLint configuration
├── .prettierrc              # Prettier configuration
└── README.md                # This file
```

For detailed structure documentation, see [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md).

## Development Guidelines

### Coding Conventions

#### File Naming

- **Components**: PascalCase - `Button.tsx`, `UserProfile.tsx`
- **Utilities/Hooks**: camelCase - `formatDate.ts`, `useAuth.ts`
- **Constants**: UPPER_SNAKE_CASE - `API_BASE_URL`, `MAX_FILE_SIZE`
- **Test files**: `ComponentName.test.tsx`
- **Type files**: `ComponentName.types.ts`

#### Component Structure

```typescript
// ComponentName.tsx
import React from 'react';
import { Box } from '@mui/material';
import type { ComponentNameProps } from './ComponentName.types';

/**
 * ComponentName description
 * @param props - Component props
 */
export const ComponentName: React.FC<ComponentNameProps> = ({ prop1, prop2 }) => {
  // Hooks first
  const [state, setState] = React.useState();

  // Event handlers
  const handleClick = () => {
    // Handle click
  };

  // Render
  return (
    <Box>
      {/* Component JSX */}
    </Box>
  );
};

// ComponentName.types.ts
export interface ComponentNameProps {
  prop1: string;
  prop2?: number;
}
```

#### Import Order

1. External dependencies (React, libraries)
2. Internal absolute imports (components, utils)
3. Relative imports
4. Type imports (at the end)
5. CSS/styles

```typescript
import React from 'react';
import { Box, Typography } from '@mui/material';

import { Button } from '@/components';
import { formatDate } from '@/utils';

import { LocalComponent } from './LocalComponent';

import type { MyType } from './types';
```

### Test-Driven Development

We follow TDD principles for all new features:

#### TDD Workflow

1. **Red**: Write a failing test first
2. **Green**: Write minimal code to pass the test
3. **Refactor**: Improve code while keeping tests passing

#### Example TDD Cycle

```typescript
// 1. RED: Write failing test
describe('Button', () => {
  it('should call onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByText('Click me'));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});

// 2. GREEN: Implement feature
export const Button: React.FC<ButtonProps> = ({ onClick, children }) => {
  return <button onClick={onClick}>{children}</button>;
};

// 3. REFACTOR: Improve implementation
export const Button: React.FC<ButtonProps> = ({ onClick, children, ...props }) => {
  return (
    <MuiButton onClick={onClick} {...props}>
      {children}
    </MuiButton>
  );
};
```

### Material UI Best Practices

#### Styling Approaches

1. **sx prop** for one-off customizations:

```typescript
<Box sx={{ p: 2, mb: 3, bgcolor: 'primary.main' }}>
  Content
</Box>
```

2. **styled() API** for reusable styled components:

```typescript
import { styled } from '@mui/material/styles';
import { Box } from '@mui/material';

const StyledCard = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.paper,
}));
```

3. **Theme overrides** for global customization (in `src/theme/`):

```typescript
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

#### Performance Tips

- Use named imports for tree-shaking: `import { Button } from '@mui/material'`
- Avoid `<Box>` in loops (use native HTML elements)
- Memoize expensive components with `React.memo`
- Use virtualization for lists with 500+ items

#### Responsive Design

```typescript
<Box
  sx={{
    width: { xs: '100%', sm: '50%', md: '33%' },
    p: { xs: 1, sm: 2, md: 3 },
  }}
>
  Responsive content
</Box>
```

### State Management

#### Local State
Use `useState` or `useReducer` for component-specific state:

```typescript
const [count, setCount] = useState(0);
```

#### Global State
Use Redux Toolkit for app-wide state:

```typescript
// store/slices/userSlice.ts
import { createSlice } from '@reduxjs/toolkit';

const userSlice = createSlice({
  name: 'user',
  initialState: { name: '', email: '' },
  reducers: {
    setUser: (state, action) => {
      state.name = action.payload.name;
      state.email = action.payload.email;
    },
  },
});

export const { setUser } = userSlice.actions;
export default userSlice.reducer;
```

#### When to Use What

- **Local state**: UI state, form inputs, toggles
- **Context**: Theme, auth, user preferences (shared across components)
- **Redux**: Complex app state, cross-feature state, state requiring persistence

### Accessibility

All components must meet WCAG 2.1 Level AA standards:

- **Semantic HTML**: Use appropriate elements (`<button>`, `<nav>`, `<main>`)
- **ARIA attributes**: Add when semantic HTML isn't sufficient
- **Keyboard navigation**: All interactive elements must be keyboard accessible
- **Color contrast**: 4.5:1 for text, 3:1 for UI components
- **Alternative text**: Provide for all images and icons

```typescript
// Good: Accessible button
<Button
  aria-label="Close dialog"
  onClick={handleClose}
>
  <CloseIcon />
</Button>

// Bad: Non-accessible button
<div onClick={handleClose}>
  <CloseIcon />
</div>
```

## Testing

### Running Tests

```bash
# Watch mode (development)
npm test

# Run all tests once
npm run test:run

# Interactive UI
npm run test:ui

# Coverage report
npm run test:coverage
```

### Test Structure

```typescript
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Button } from './Button';

describe('Button', () => {
  it('should render children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('should handle click events', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    screen.getByText('Click me').click();

    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### Test Coverage Goals

- **Unit tests**: 80%+ coverage
- **Integration tests**: Critical user flows
- **Accessibility tests**: All interactive components

## Building for Production

### Create Production Build

```bash
npm run build
```

This command:
1. Type-checks TypeScript code (`tsc -b`)
2. Bundles and minifies JavaScript
3. Optimizes CSS and assets
4. Generates source maps
5. Outputs to `dist/` directory

### Build Output

```
dist/
├── assets/           # Bundled JS, CSS, and assets (with hashed names)
├── index.html        # Entry HTML
└── vite.svg          # Static assets from public/
```

### Preview Production Build

```bash
npm run build
npm run preview
```

Access at http://localhost:4173

### Deployment

The `dist/` directory can be deployed to any static hosting service:

- **Vercel**: `vercel deploy`
- **Netlify**: Drag and drop `dist/` folder
- **GitHub Pages**: Deploy `dist/` to `gh-pages` branch
- **AWS S3**: Upload `dist/` contents to S3 bucket
- **Docker**: Serve with nginx or any static server

## Troubleshooting

### Development Server Issues

**Issue**: Port 5173 already in use

```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Or use a different port
npm run dev -- --port 3000
```

**Issue**: Module not found errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Build Issues

**Issue**: TypeScript compilation errors

```bash
# Check TypeScript errors
npx tsc --noEmit

# Fix common issues
npm run lint:fix
```

**Issue**: Out of memory during build

```bash
# Increase Node.js memory
NODE_OPTIONS=--max-old-space-size=4096 npm run build
```

### Test Issues

**Issue**: Tests timing out

```typescript
// Increase timeout in test file
it('should complete async operation', async () => {
  // ...
}, 10000); // 10 second timeout
```

**Issue**: jsdom errors

```bash
# Reinstall jsdom
npm install jsdom --save-dev
```

## Contributing

We welcome contributions! Please follow these guidelines:

### Development Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write tests first** (TDD):
   ```bash
   npm test
   ```

3. **Implement the feature**:
   - Follow coding conventions
   - Ensure tests pass
   - Add documentation

4. **Run quality checks**:
   ```bash
   npm run lint
   npm run format
   npm run test:coverage
   ```

5. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

6. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Build process or tool changes

### Code Review Checklist

- Tests pass and coverage maintained
- Code follows style guidelines
- TypeScript types are correct
- Accessibility standards met
- Documentation updated
- No console errors or warnings

## Resources

### Official Documentation

- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Material UI Documentation](https://mui.com/)
- [Vite Documentation](https://vitejs.dev/)
- [Redux Toolkit Documentation](https://redux-toolkit.js.org/)
- [React Router Documentation](https://reactrouter.com/)
- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)

### Learning Resources

- [React Tutorial](https://react.dev/learn)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [Material Design Guidelines](https://m3.material.io/)
- [Redux Essentials](https://redux.js.org/tutorials/essentials/part-1-overview-concepts)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

### Tools

- [React DevTools](https://react.dev/learn/react-developer-tools)
- [Redux DevTools](https://github.com/reduxjs/redux-devtools)
- [VS Code](https://code.visualstudio.com/)
- [Chrome DevTools](https://developer.chrome.com/docs/devtools/)

## License

[Add your license here]

---

**Version**: 1.0.0
**Last Updated**: 2025-10-15
**Maintained by**: Frontend Team

For questions or issues, please open an issue in the repository or contact the development team.
