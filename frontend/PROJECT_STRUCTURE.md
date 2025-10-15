# Frontend Project Structure

This document provides a comprehensive overview of the project's directory structure and organization principles.

## Overview

This React + TypeScript + Material UI application follows industry best practices for scalability, maintainability, and testability. The structure supports both small prototypes and large enterprise applications.

## Root Directory Structure

```
frontend/
├── public/                    # Static assets served directly
├── src/                       # Source code
├── tests/                     # Test files organized by type
├── dist/                      # Production build output (generated)
├── node_modules/              # Dependencies (generated)
├── index.html                 # Entry HTML file
├── package.json               # Dependencies and scripts
├── vite.config.ts             # Vite configuration
├── tsconfig.json              # TypeScript configuration
├── eslint.config.js           # ESLint configuration
└── README.md                  # Project documentation
```

## Source Directory (`src/`)

### Component Organization

```
src/components/
├── common/                    # Generic, reusable components
│   ├── Button/
│   ├── Card/
│   └── index.ts              # Barrel export
├── layout/                    # Layout and structural components
│   ├── Header/
│   ├── Footer/
│   ├── Sidebar/
│   └── index.ts
├── forms/                     # Form-specific components
│   ├── Input/
│   ├── Select/
│   └── index.ts
├── feedback/                  # User feedback components
│   ├── Toast/
│   ├── Alert/
│   └── index.ts
└── index.ts                   # Main component barrel export
```

**Guidelines:**
- Each component gets its own directory
- Colocate tests: `Button/Button.test.tsx`
- Include types: `Button/Button.types.ts`
- Export via index: `Button/index.ts`

### Pages

```
src/pages/
├── Home/
│   ├── Home.tsx
│   ├── Home.test.tsx
│   └── index.ts
├── NotFound/
│   └── NotFound.tsx
└── index.ts
```

**Guidelines:**
- One page per route
- Pages compose components and features
- Handle route-level concerns (data fetching, layout)

### Features

```
src/features/
├── authentication/
│   ├── components/
│   ├── hooks/
│   ├── services/
│   ├── types/
│   └── index.ts
└── dashboard/
    ├── components/
    ├── hooks/
    └── index.ts
```

**Guidelines:**
- Feature-based organization for complex domains
- Self-contained modules
- Clear boundaries between features

### Utilities and Hooks

```
src/
├── utils/                     # Pure utility functions
│   ├── formatters.ts
│   ├── validators.ts
│   └── index.ts
├── hooks/                     # Custom React hooks
│   ├── useLocalStorage.ts
│   ├── useDebounce.ts
│   └── index.ts
├── services/                  # API clients and external services
│   ├── api.ts
│   ├── auth.service.ts
│   └── index.ts
└── constants/                 # Application constants
    └── index.ts
```

### State Management

```
src/store/
├── slices/                    # Redux Toolkit slices
│   ├── authSlice.ts
│   ├── userSlice.ts
│   └── index.ts
├── middleware/                # Custom middleware
│   └── index.ts
└── index.ts                   # Store configuration
```

**Guidelines:**
- Use Redux Toolkit for global state
- Keep local state in components when possible
- One slice per domain/feature

### Theme and Styles

```
src/
├── theme/                     # Material UI theme configuration
│   ├── index.ts
│   ├── palette.ts
│   ├── typography.ts
│   └── components.ts
└── styles/                    # Global CSS (minimal)
    ├── global.css
    └── README.md
```

**Primary Styling:** Material UI with Emotion (sx prop, styled() API)

### Types and Assets

```
src/
├── types/                     # TypeScript type definitions
│   ├── index.ts
│   ├── api.types.ts
│   └── common.types.ts
└── assets/                    # Static assets
    ├── images/
    ├── icons/
    ├── fonts/
    └── README.md
```

## Tests Directory

```
tests/
├── unit/                      # Unit tests
│   ├── components/
│   └── utils/
├── integration/               # Integration tests
│   └── features/
├── e2e/                       # End-to-end tests
│   └── user-flows/
├── utils/                     # Test utilities
│   ├── test-utils.tsx
│   └── mock-data.ts
├── fixtures/                  # Mock data and fixtures
└── README.md
```

## File Naming Conventions

### Components
- PascalCase: `Button.tsx`, `UserProfile.tsx`
- Test files: `Button.test.tsx`
- Type files: `Button.types.ts`
- Style files: `Button.styles.ts` (if not using sx/styled)

### Utilities and Hooks
- camelCase: `formatDate.ts`, `useAuth.ts`
- Hooks prefix: `use[HookName].ts`

### Constants
- UPPER_SNAKE_CASE: `API_BASE_URL`, `MAX_FILE_SIZE`

### Types
- PascalCase: `User`, `ApiResponse`
- Interface prefix (optional): `IUser` or `User`

## Import Aliases

Configure path aliases in `tsconfig.json` for clean imports:

```typescript
// Instead of: import { Button } from '../../../../components/common/Button';
// Use: import { Button } from '@/components';

// Common aliases:
@/components
@/pages
@/features
@/utils
@/hooks
@/services
@/store
@/theme
@/types
@/assets
```

## Code Organization Principles

### 1. Separation of Concerns
- UI components separate from business logic
- API calls in services, not components
- State management separate from UI

### 2. Colocation
- Keep related files together
- Tests next to implementation
- Types next to usage

### 3. Scalability
- Feature-based organization for large apps
- Type-based organization (components, utils) for small apps
- Easy to split into micro-frontends if needed

### 4. Testability
- Pure functions for utilities
- Dependency injection for services
- Test-friendly component design

### 5. Reusability
- Generic components in `components/`
- Domain-specific components in `features/`
- Shared utilities in `utils/`

## Architecture Patterns

### Component Architecture
```
Component
├── Presentation Layer (UI)
├── Logic Layer (Hooks, State)
└── Data Layer (Services, API)
```

### State Management Strategy
- **Local State**: Component-level with useState/useReducer
- **Shared State**: Context API for non-global state
- **Global State**: Redux Toolkit for app-wide state
- **Server State**: React Query/RTK Query for API data

### Testing Strategy (TDD)
1. **Red**: Write failing test
2. **Green**: Implement minimal code
3. **Refactor**: Improve while tests pass

## Best Practices

### DO
✅ Use TypeScript for type safety
✅ Write tests first (TDD)
✅ Use barrel exports (index.ts) for clean imports
✅ Follow Material UI styling best practices
✅ Keep components small and focused
✅ Use semantic HTML and ARIA attributes
✅ Optimize for Web Vitals (LCP, FID, CLS)

### DON'T
❌ Deep nest components beyond 3 levels
❌ Create god components with too much logic
❌ Mix business logic with presentation
❌ Ignore accessibility (a11y)
❌ Skip tests for critical paths
❌ Use inline styles (prefer sx prop or styled())
❌ Commit large unoptimized assets

## Resources

- [React Documentation](https://react.dev/)
- [Material UI Documentation](https://mui.com/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Redux Toolkit Documentation](https://redux-toolkit.js.org/)
- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)

---

**Last Updated**: 2025-10-15
**Version**: 1.0.0
**Maintainer**: Frontend Team
