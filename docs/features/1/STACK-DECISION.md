# Technology Stack Decision - Quick Reference

**Date**: 2025-10-15
**Status**: ✅ Approved
**Full Analysis**: See [technology-stack-analysis.md](./technology-stack-analysis.md)

---

## Selected Technology Stack

### Core Technologies
- **Framework**: React 19
- **Type System**: TypeScript 5.7+
- **Build Tool**: Vite 6
- **Package Manager**: npm 10+

### UI & Styling
- **UI Framework**: Material UI (MUI) v6
- **CSS-in-JS**: Emotion 11

### State & Routing
- **State Management**: Redux Toolkit 2.x
- **Routing**: React Router 7

### Testing
- **Test Runner**: Vitest 2.x
- **Component Testing**: React Testing Library 16.x
- **API Mocking**: MSW 2.x

### Code Quality
- **Linting**: ESLint 9.x
- **Formatting**: Prettier 3.x
- **Git Hooks**: husky 9.x + lint-staged 15.x

---

## Why These Choices?

### React 19
- Largest ecosystem and community
- Best Material UI integration (MUI v6)
- Largest talent pool for hiring
- Enterprise-proven at scale
- Modern features: Actions, Server Components, React Compiler

### Vite 6
- 10-20x faster HMR than Webpack
- Near-instant server start (~500ms vs 5-10s)
- Modern ES modules approach
- Excellent React 19 support

### Material UI v6
- Best Material Design 3 implementation for React
- 50+ production-ready components
- WCAG 2.1 Level AA accessible
- Highly customizable theming
- Excellent TypeScript support

### Redux Toolkit
- Industry standard state management
- Excellent DevTools for debugging
- Simplified Redux with modern API
- Built-in RTK Query for data fetching
- First-class TypeScript support

### Vitest + React Testing Library
- Vite-native test runner (faster than Jest)
- User-centric testing approach
- Excellent TDD support
- Jest-compatible API

---

## Framework Comparison Summary

| Framework | Score | Best For |
|-----------|-------|----------|
| **React 19** ⭐ | ★★★★★ | Large-scale apps, best ecosystem, Material UI |
| Vue 3 | ★★★★☆ | Great DX, smaller projects |
| Angular 18 | ★★★☆☆ | Enterprise apps, opinionated structure |
| Svelte 5 | ★★★☆☆ | Small apps, performance-critical |

**React wins on**: Ecosystem, Material UI support, hiring, enterprise adoption, testing maturity

---

## Next Steps

1. Story #2: Initialize React project with Vite and npm
2. Story #3: Create project directory structure
3. Story #4: Design system with MUI theming
4. Story #5: Configure ESLint, Prettier, TypeScript

---

## Key Performance Targets

- **Cold Start**: ~500ms
- **HMR**: <100ms
- **First Contentful Paint**: <1.5s
- **Time to Interactive**: <3.5s
- **Base Bundle Size**: ~150-200KB gzipped

---

For detailed analysis, rationale, and trade-offs, see the complete [Technology Stack Analysis](./technology-stack-analysis.md).
