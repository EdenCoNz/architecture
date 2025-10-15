# Tests Directory

Comprehensive testing infrastructure following Test-Driven Development (TDD) principles.

## Directory Structure

- **unit/**: Unit tests for individual functions, components, and modules
- **integration/**: Integration tests for feature workflows and component interactions
- **e2e/**: End-to-end tests for complete user journeys (Playwright, Cypress)
- **utils/**: Testing utilities, custom matchers, and helper functions
- **fixtures/**: Mock data and test fixtures

## Testing Philosophy

This project follows **Test-Driven Development (TDD)**:

1. **Red**: Write a failing test first
2. **Green**: Write minimal code to make the test pass
3. **Refactor**: Improve code while keeping tests green

## Testing Tools

- **Vitest**: Fast unit and integration test runner (Vite-native)
- **React Testing Library**: Component testing with user-centric approach
- **Testing Library User Event**: Realistic user interaction simulation
- **MSW (Mock Service Worker)**: API mocking for integration tests

## Best Practices

### Unit Tests
- Test individual functions and components in isolation
- Focus on public API and behavior, not implementation details
- Use descriptive test names: `should [expected behavior] when [condition]`
- Aim for 80%+ code coverage

### Integration Tests
- Test feature workflows and component interactions
- Mock external dependencies (API calls, third-party services)
- Test user journeys through multiple components
- Verify state management and data flow

### Component Tests
- Use React Testing Library queries by priority:
  1. getByRole (accessibility-first)
  2. getByLabelText
  3. getByPlaceholderText
  4. getByText
  5. getByTestId (last resort)
- Test user interactions, not implementation
- Verify accessibility (ARIA attributes, keyboard navigation)

### E2E Tests
- Test critical user paths
- Run in real browser environments
- Focus on happy paths and critical flows
- Keep E2E tests minimal due to execution time

## Example Test Structure

```typescript
// unit/utils/formatters.test.ts
describe('formatCurrency', () => {
  it('should format number as USD currency', () => {
    expect(formatCurrency(1234.56)).toBe('$1,234.56');
  });
});

// integration/features/auth/Login.test.tsx
describe('Login Flow', () => {
  it('should login user and redirect to dashboard', async () => {
    const user = userEvent.setup();
    render(<LoginPage />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(await screen.findByText(/dashboard/i)).toBeInTheDocument();
  });
});
```

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

## Writing Your First Test

1. Start with acceptance criteria from user stories
2. Write test cases that verify the criteria
3. Implement the feature to pass the tests
4. Refactor while keeping tests green
5. Add edge cases and error handling tests

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Library Queries Cheatsheet](https://testing-library.com/docs/queries/about)
- [Common Testing Mistakes](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
