# Features Directory

This directory contains feature-based modules following the **Feature-Sliced Design** pattern.

## Structure

Each feature should be self-contained with its own:

- Components
- Hooks
- Services
- Types
- Tests
- State management (if needed)

## Example Structure

```
features/
  authentication/
    components/
      LoginForm.tsx
      RegisterForm.tsx
    hooks/
      useAuth.ts
    services/
      auth.service.ts
    types/
      auth.types.ts
    index.ts
  dashboard/
    components/
      DashboardCard.tsx
      DashboardChart.tsx
    hooks/
      useDashboardData.ts
    index.ts
```

## Guidelines

1. **Self-Contained**: Each feature should contain everything it needs
2. **Single Responsibility**: Each feature focuses on one business domain
3. **Reusable Components**: Extract truly reusable components to `src/components/`
4. **Clear Exports**: Use index.ts for clean barrel exports
5. **Collocated Tests**: Keep tests close to implementation files

## When to Use Features vs Components

- **Features**: Business logic, domain-specific functionality
- **Components**: Generic, reusable UI components without business logic
