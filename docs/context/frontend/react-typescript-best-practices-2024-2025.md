# React + TypeScript Best Practices and Toolchain (2024-2025)
**Date**: 2025-10-13
**Purpose**: Comprehensive guide for modern React development with TypeScript

## Summary

React 19 (released December 2024) represents the current state of the ecosystem, introducing Actions, Server Components, and improved TypeScript integration. The recommended toolchain centers on Vite for SPAs and Next.js 15 for full-stack applications, with pnpm as the preferred package manager. TypeScript 5.7+ provides enhanced type safety with better inference for hooks and Server Components. The industry has shifted to function components with hooks as the standard, making class components effectively deprecated for new development.

## 1. Latest React + TypeScript Setup

### Build Tools (2024-2025)

#### **Vite - Recommended for SPAs and Client-Side Applications**

**Key Facts:**
- Vite 6.x is the latest major version (as of 2024-2025)
- 15.3+ million weekly NPM downloads (2024)
- Requires Node.js 20.19+ or 22.12+
- Reduces build time by ~43% compared to Create React App (28.4s to 16.1s)
- Development server startup: 390ms (vs 4.5s for CRA)
- Uses esbuild (Rust-powered) for dependency pre-bundling
- Native ES modules support with instant Hot Module Replacement (HMR)

**Why Vite:**
- Zero-config TypeScript support out of the box
- Automatic code splitting via dynamic imports
- Fast iteration cycles ideal for component-driven development
- Built-in optimization for production using Rollup
- Framework-agnostic design allows architectural freedom

**Setup Command:**
```bash
npm create vite@latest my-react-app -- --template react-ts
# or with pnpm (recommended)
pnpm create vite my-react-app --template react-ts
```

**Best For:**
- Single-page applications (SPAs)
- Client-side rendered applications
- Small to medium-sized projects
- Microservice architectures
- Projects requiring fast iteration

#### **Next.js 15 - Recommended for Full-Stack and SEO-Critical Applications**

**Key Facts:**
- Next.js 15 released 2024 with stable React Server Components
- 7.3+ million weekly NPM downloads
- Built-in TypeScript support with zero configuration
- Integrated Turbopack (Rust-based bundler) for development
- File-based routing system with App Router

**Why Next.js:**
- Native Server-Side Rendering (SSR) and Static Site Generation (SSG)
- SEO-optimized by default with automatic HTML generation
- Integrated API routes for backend functionality
- Built-in image optimization and font loading
- Incremental Static Regeneration (ISR) for hybrid rendering
- Production-grade performance optimizations

**Setup Command:**
```bash
npx create-next-app@latest my-next-app --typescript
# or with pnpm
pnpm create next-app my-next-app --typescript
```

**Best For:**
- Content-heavy websites (blogs, documentation, marketing sites)
- E-commerce platforms
- Applications requiring SEO
- Full-stack applications with backend needs
- Enterprise applications with predictable scaling requirements

### TypeScript Configuration Best Practices

#### **Recommended tsconfig.json for React Projects (2024-2025)**

```json
{
  "compilerOptions": {
    // Language and Environment
    "target": "ES2022",                    // Modern JavaScript features
    "lib": ["ES2023", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",                    // New JSX transform (required for React 19)
    "module": "ESNext",
    "moduleResolution": "Bundler",         // Modern bundler resolution (Vite/Next.js)

    // Type Checking - Strict Mode (Recommended)
    "strict": true,
    "noUncheckedIndexedAccess": true,      // Safer array/object access
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitReturns": true,

    // Module Resolution
    "resolveJsonModule": true,
    "allowImportingTsExtensions": false,
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,
    "isolatedModules": true,               // Required for Vite
    "skipLibCheck": true,                  // Performance optimization

    // Emit
    "noEmit": true,                        // Let build tools handle compilation
    "declaration": false,
    "sourceMap": true,

    // Other
    "forceConsistentCasingInFileNames": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]                   // Path aliases
    }
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist", "build"]
}
```

#### **Key Configuration Decisions:**

1. **jsx: "react-jsx"** - Uses the new JSX transform introduced in React 17, required for React 19 features (ref as prop)
2. **moduleResolution: "Bundler"** - Modern resolution strategy for Vite/Next.js (replaces "Node")
3. **strict: true** - Enables all strict type-checking options (critical for production apps)
4. **noUncheckedIndexedAccess: true** - Prevents common array/object access bugs
5. **isolatedModules: true** - Required for Vite's fast compilation strategy
6. **skipLibCheck: true** - Improves compilation performance by skipping type checking of declaration files

#### **TypeScript Version Recommendations:**

- **Minimum**: TypeScript 5.0+
- **Recommended**: TypeScript 5.7+ (latest features as of 2024)
- **React 19 Type Definitions**: `@types/react@^19.0.0` and `@types/react-dom@^19.0.0`

**Installation:**
```bash
npm install --save-exact @types/react@^19.0.0 @types/react-dom@^19.0.0
```

**TypeScript 5.7 Key Features:**
- ES2024 support (use `--target es2024` and `--lib es2024`)
- Improved tsconfig.json discovery in editors
- Better type inference for React hooks
- Enhanced compatibility with React Server Components

## 2. Modern Development Practices

### Latest React Patterns (React 19)

#### **React 19 Key Features (Released December 2024)**

**1. Actions - New Pattern for Async State Management**

Actions automate handling of:
- Pending states during async operations
- Optimistic updates for instant UI feedback
- Error handling and rollback
- Form submissions and mutations

**Example:**
```tsx
import { useActionState } from 'react';

function UpdateNameForm() {
  const [error, submitAction, isPending] = useActionState(
    async (previousState: any, formData: FormData) => {
      const error = await updateName(formData.get('name') as string);
      if (error) {
        return error;
      }
      return null;
    },
    null,
  );

  return (
    <form action={submitAction}>
      <input type="text" name="name" />
      <button type="submit" disabled={isPending}>Update</button>
      {error && <p>{error}</p>}
    </form>
  );
}
```

**2. New Hooks in React 19**

| Hook | Purpose | Use Case |
|------|---------|----------|
| `useActionState` | Manages async action state | Form submissions, data mutations |
| `useOptimistic` | Instant UI updates during async operations | Shopping carts, like buttons |
| `useFormStatus` | Access form state without prop drilling | Submit buttons, loading indicators |
| `use` | Read promises and context in render | Async data fetching, conditional context |

**3. React Server Components (RSC)**

- Components that execute once on the server
- Send only rendered output (not JavaScript) to client
- Supported in Next.js 15, React Router 7 (upcoming), TanStack Start
- Reduce bundle size and improve initial page load

**Server Component Example:**
```tsx
// app/page.tsx - Server Component (Next.js 15)
async function ProductList() {
  // Fetch directly on server - no useEffect needed
  const products = await fetch('https://api.example.com/products').then(r => r.json());

  return (
    <div>
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
```

**4. Improved ref Handling**

- `ref` can now be accessed as a prop (no more `forwardRef` needed)
- `forwardRef` is deprecated and will be removed in future versions

**Before (React 18):**
```tsx
const MyInput = forwardRef<HTMLInputElement, Props>((props, ref) => {
  return <input {...props} ref={ref} />;
});
```

**After (React 19):**
```tsx
function MyInput({ ref, ...props }: Props & { ref?: React.Ref<HTMLInputElement> }) {
  return <input {...props} ref={ref} />;
}
```

### TypeScript Typing Strategies

#### **Component Props Typing**

**Best Practice: Interface for Props**
```tsx
// Use interface for extensibility
interface ButtonProps {
  /** The text to display inside the button */
  title: string;
  /** Click handler */
  onClick: () => void;
  /** Visual variant */
  variant?: 'primary' | 'secondary';
  /** Disable interaction */
  disabled?: boolean;
  /** Child elements */
  children?: React.ReactNode;
}

// Standard function component (recommended over React.FC)
function Button({ title, onClick, variant = 'primary', disabled, children }: ButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`btn btn-${variant}`}
    >
      {title}
      {children}
    </button>
  );
}
```

**Why not React.FC?**
- Cannot use generics with arrow functions in TSX files
- Function declaration provides better support for generic components
- More explicit and consistent with TypeScript conventions

#### **Hooks Typing Patterns**

**1. useState - Type Inference and Explicit Typing**

```tsx
// Type inferred from initial value
const [count, setCount] = useState(0); // number
const [name, setName] = useState(''); // string

// Explicit typing for union types
type Status = 'idle' | 'loading' | 'success' | 'error';
const [status, setStatus] = useState<Status>('idle');

// Complex state with interface
interface User {
  id: string;
  name: string;
  email: string;
}

const [user, setUser] = useState<User | null>(null);

// Lazy initialization with proper typing
const [data, setData] = useState<ExpensiveData>(() => computeExpensiveValue());
```

**2. useReducer - Discriminated Unions for Actions**

```tsx
// Define state type
interface State {
  count: number;
  error: string | null;
}

// Define action types using discriminated unions
type Action =
  | { type: 'increment' }
  | { type: 'decrement' }
  | { type: 'reset'; payload: number }
  | { type: 'error'; payload: string };

// Type-safe reducer
function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment':
      return { ...state, count: state.count + 1 };
    case 'decrement':
      return { ...state, count: state.count - 1 };
    case 'reset':
      return { ...state, count: action.payload };
    case 'error':
      return { ...state, error: action.payload };
    default:
      return state;
  }
}

// Usage
const [state, dispatch] = useReducer(reducer, { count: 0, error: null });
dispatch({ type: 'increment' }); // Type-safe
```

**3. useContext - Handling Nullable Context**

```tsx
interface AuthContextType {
  user: User | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
}

// Create context with null default
const AuthContext = createContext<AuthContextType | null>(null);

// Custom hook with runtime check
function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

// Provider component
function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const value: AuthContextType = {
    user,
    login: async (credentials) => { /* ... */ },
    logout: () => setUser(null),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
```

**4. useCallback and useMemo - Type Inference**

```tsx
// Types inferred from return value and parameters
const handleClick = useCallback((event: React.MouseEvent<HTMLButtonElement>) => {
  console.log('Button clicked', event.currentTarget);
}, []);

// Explicit return type for complex computations
const expensiveValue = useMemo<ComputedResult>(() => {
  return computeExpensiveValue(input);
}, [input]);

// Generic memoization
function useMemoizedValue<T>(factory: () => T, deps: React.DependencyList): T {
  return useMemo(factory, deps);
}
```

**5. useRef - DOM and Mutable References**

```tsx
// DOM element ref
const inputRef = useRef<HTMLInputElement>(null);

useEffect(() => {
  inputRef.current?.focus();
}, []);

// Mutable value ref (stores previous value)
const previousValueRef = useRef<number>(0);

useEffect(() => {
  previousValueRef.current = count;
}, [count]);
```

#### **Generic Components Pattern**

Generic components provide reusability while maintaining type safety.

```tsx
// Generic List component
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
  keyExtractor: (item: T) => string | number;
  emptyMessage?: string;
}

// Must use function declaration for generics in TSX
function List<T>({ items, renderItem, keyExtractor, emptyMessage }: ListProps<T>) {
  if (items.length === 0) {
    return <div>{emptyMessage || 'No items'}</div>;
  }

  return (
    <ul>
      {items.map((item) => (
        <li key={keyExtractor(item)}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}

// Usage - types are inferred
interface Product {
  id: number;
  name: string;
  price: number;
}

function ProductList({ products }: { products: Product[] }) {
  return (
    <List
      items={products}
      keyExtractor={(product) => product.id}
      renderItem={(product) => (
        <div>
          {product.name} - ${product.price}
        </div>
      )}
    />
  );
}
```

#### **Advanced Typing Patterns**

**1. Component Props with HTML Attributes**

```tsx
// Extend native HTML element props
interface CustomButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant: 'primary' | 'secondary';
  isLoading?: boolean;
}

function CustomButton({ variant, isLoading, children, ...htmlProps }: CustomButtonProps) {
  return (
    <button {...htmlProps} className={`btn-${variant}`} disabled={isLoading || htmlProps.disabled}>
      {isLoading ? 'Loading...' : children}
    </button>
  );
}
```

**2. Polymorphic Component Pattern**

```tsx
// Component that can render as different HTML elements
type PolymorphicProps<E extends React.ElementType> = {
  as?: E;
} & Omit<React.ComponentPropsWithoutRef<E>, 'as'>;

function Text<E extends React.ElementType = 'span'>({
  as,
  children,
  ...props
}: PolymorphicProps<E>) {
  const Component = as || 'span';
  return <Component {...props}>{children}</Component>;
}

// Usage
<Text>Default span</Text>
<Text as="p">Paragraph</Text>
<Text as="h1">Heading</Text>
```

**3. Event Handlers**

```tsx
// Specific event types
const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
  console.log(event.target.value);
};

const handleFormSubmit = (event: React.FormEvent<HTMLFormElement>) => {
  event.preventDefault();
  // ...
};

const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
  if (event.key === 'Enter') {
    // ...
  }
};
```

**4. CSS and Style Typing**

```tsx
// Inline styles
const styles: React.CSSProperties = {
  backgroundColor: 'blue',
  fontSize: '16px',
  padding: '10px',
};

function StyledComponent() {
  return <div style={styles}>Styled content</div>;
}
```

### State Management Recommendations (2024-2025)

#### **Decision Matrix**

| Scenario | Recommended Solution | Why |
|----------|---------------------|-----|
| Simple local state | `useState` | Built-in, no dependencies |
| Complex local state | `useReducer` | Predictable state transitions |
| Component tree prop drilling (theme, auth) | Context API | Built-in, dependency injection |
| Medium to large app state | Zustand | Lightweight (~1KB), no providers, fast |
| Server state (API data) | TanStack Query (React Query) | Caching, refetching, optimistic updates |
| Form state | React Hook Form | Performance, validation, DevTools |
| Large enterprise apps | Zustand + TanStack Query | Separation of concerns |

#### **Context API - Best Practices**

**Use For:** Dependency injection, not state management

```tsx
// GOOD: Dependency injection
const ThemeContext = createContext<Theme | null>(null);
const AuthContext = createContext<AuthContextType | null>(null);

// AVOID: Frequent updates (causes re-renders)
// Use Zustand instead for frequently changing state
```

**Key Limitation:** Every context value change triggers re-render of all consumers.

#### **Zustand - Recommended for Most Applications**

**Why Zustand (2024-2025):**
- Bundle size: <1KB (smallest state management library)
- No providers needed (cleaner code)
- TypeScript-first design
- Overcomes React context loss, concurrency issues, and zombie child problems
- Performance: 85ms average update time vs 220ms with traditional React state (in complex forms)
- Supports middleware (persist, devtools, immer)

**Setup:**
```bash
pnpm add zustand
```

**Basic Store:**
```tsx
import { create } from 'zustand';

interface BearStore {
  bears: number;
  increase: (by: number) => void;
  reset: () => void;
}

const useBearStore = create<BearStore>((set) => ({
  bears: 0,
  increase: (by) => set((state) => ({ bears: state.bears + by })),
  reset: () => set({ bears: 0 }),
}));

// Usage
function BearCounter() {
  const bears = useBearStore((state) => state.bears); // Selective subscription
  return <h1>{bears} bears</h1>;
}

function Controls() {
  const increase = useBearStore((state) => state.increase);
  return <button onClick={() => increase(1)}>Add bear</button>;
}
```

**Advanced Pattern: Zustand with Context (Multiple Store Instances)**

```tsx
import { createContext, useContext, useRef } from 'react';
import { createStore, useStore } from 'zustand';

interface TodoStore {
  todos: Todo[];
  addTodo: (text: string) => void;
}

const TodoContext = createContext<ReturnType<typeof createStore<TodoStore>> | null>(null);

function TodoProvider({ children }: { children: React.ReactNode }) {
  const storeRef = useRef(createStore<TodoStore>((set) => ({
    todos: [],
    addTodo: (text) => set((state) => ({ todos: [...state.todos, { id: Date.now(), text }] })),
  })));

  return <TodoContext.Provider value={storeRef.current}>{children}</TodoContext.Provider>;
}

function useTodos() {
  const store = useContext(TodoContext);
  if (!store) throw new Error('Missing TodoProvider');
  return useStore(store);
}
```

**Zustand with Persistence:**
```tsx
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      login: (user) => set({ user }),
      logout: () => set({ user: null }),
    }),
    {
      name: 'auth-storage', // localStorage key
    }
  )
);
```

#### **TanStack Query (React Query) - Server State Management**

**Best For:** API data fetching, caching, synchronization

```bash
pnpm add @tanstack/react-query
```

**Setup:**
```tsx
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Products />
    </QueryClientProvider>
  );
}

// Type-safe query
function Products() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['products'],
    queryFn: async (): Promise<Product[]> => {
      const response = await fetch('/api/products');
      if (!response.ok) throw new Error('Failed to fetch');
      return response.json();
    },
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {data?.map((product) => (
        <div key={product.id}>{product.name}</div>
      ))}
    </div>
  );
}
```

**Modern Practice (2025):** Many teams use **Zustand + TanStack Query** together:
- **Zustand**: Client-side UI state (modals, filters, temporary data)
- **TanStack Query**: Server state (API data, caching, refetching)

## 3. Tooling and Developer Experience

### Linting and Formatting

#### **ESLint 9 vs Biome - 2024-2025 Landscape**

**Current Recommendations:**

| Tool | Best For | Pros | Cons |
|------|----------|------|------|
| **ESLint + Prettier** | Established projects, TypeScript type checking | Mature ecosystem, 200+ typescript-eslint rules, extensive plugin support | Slower, two separate tools, more configuration |
| **Biome** | New projects, performance-critical CI/CD | 100x faster, single tool, Rust-based, 1:15 CI time vs 5:40 | Limited typescript-eslint rules (64 vs 200+), smaller ecosystem, less mature |

#### **ESLint 9 + Prettier Setup (Recommended for Production)**

**Install:**
```bash
pnpm add -D eslint @eslint/js @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint-plugin-react eslint-plugin-react-hooks prettier eslint-config-prettier
```

**eslint.config.js (ESLint 9 Flat Config):**
```js
import js from '@eslint/js';
import tseslint from '@typescript-eslint/eslint-plugin';
import tsparser from '@typescript-eslint/parser';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import prettier from 'eslint-config-prettier';

export default [
  js.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: tsparser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        ecmaFeatures: { jsx: true },
        project: './tsconfig.json',
      },
    },
    plugins: {
      '@typescript-eslint': tseslint,
      'react': react,
      'react-hooks': reactHooks,
    },
    rules: {
      ...tseslint.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      'react/react-in-jsx-scope': 'off', // Not needed in React 19
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',
    },
  },
  prettier,
];
```

**.prettierrc:**
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "arrowParens": "always"
}
```

**package.json scripts:**
```json
{
  "scripts": {
    "lint": "eslint . --ext .ts,.tsx",
    "lint:fix": "eslint . --ext .ts,.tsx --fix",
    "format": "prettier --write \"src/**/*.{ts,tsx,css,md}\""
  }
}
```

#### **Biome Setup (Alternative - Emerging Standard)**

**Install:**
```bash
pnpm add -D @biomejs/biome
```

**biome.json:**
```json
{
  "$schema": "https://biomejs.dev/schemas/1.9.4/schema.json",
  "organizeImports": { "enabled": true },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "suspicious": {
        "noExplicitAny": "warn"
      }
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "lineWidth": 100
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "semicolons": "always"
    }
  }
}
```

**package.json scripts:**
```json
{
  "scripts": {
    "lint": "biome check .",
    "lint:fix": "biome check --write .",
    "format": "biome format --write ."
  }
}
```

**Migration Strategy:**
- Run Biome alongside ESLint during transition
- Use for performance-critical scenarios (large codebases, CI/CD optimization)
- Frontend teams report CI pipeline time reduction from 5:40 to 1:15

**2025 Trend:** Biome adoption is growing rapidly, but ESLint + Prettier remains the production standard due to typescript-eslint completeness.

### Testing Frameworks and Approaches

#### **Recommended Stack: Vitest + React Testing Library**

**Why This Combination (2024-2025):**
- Official React team recommendation (Vite preferred over Create React App)
- Vitest leverages Vite's fast HMR and native ESM support
- Significantly faster than Jest (leverages Vite's build pipeline)
- Jest-compatible API (easy migration)
- Built-in TypeScript and ESM support
- Modern UI dashboard (vitest/ui)
- React Testing Library enforces accessibility-first testing

#### **Setup:**

**Install:**
```bash
pnpm add -D vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event @vitest/ui @vitest/coverage-v8
```

**vite.config.ts:**
```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
  },
});
```

**src/test/setup.ts:**
```ts
import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

// Extend Vitest's expect with jest-dom matchers
expect.extend(matchers);

// Cleanup after each test
afterEach(() => {
  cleanup();
});
```

**tsconfig.json (add):**
```json
{
  "compilerOptions": {
    "types": ["vitest/globals", "@testing-library/jest-dom"]
  }
}
```

**package.json scripts:**
```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

#### **Testing Best Practices (2024-2025)**

**1. Component Testing Example:**

```tsx
// Button.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button title="Click me" onClick={() => {}} />);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('calls onClick when clicked', async () => {
    const handleClick = vi.fn();
    const user = userEvent.setup();

    render(<Button title="Click me" onClick={handleClick} />);

    await user.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('disables button when disabled prop is true', () => {
    render(<Button title="Click me" onClick={() => {}} disabled />);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

**2. Testing Hooks:**

```tsx
// useCounter.test.ts
import { renderHook, act } from '@testing-library/react';
import { expect, it } from 'vitest';
import { useCounter } from './useCounter';

it('increments counter', () => {
  const { result } = renderHook(() => useCounter());

  expect(result.current.count).toBe(0);

  act(() => {
    result.current.increment();
  });

  expect(result.current.count).toBe(1);
});
```

**3. Testing Async Components:**

```tsx
// ProductList.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { ProductList } from './ProductList';

// Mock fetch
global.fetch = vi.fn();

describe('ProductList', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('displays loading state then products', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => [
        { id: 1, name: 'Product 1' },
        { id: 2, name: 'Product 2' },
      ],
    });

    render(<ProductList />);

    // Loading state
    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    // Wait for products
    await waitFor(() => {
      expect(screen.getByText('Product 1')).toBeInTheDocument();
      expect(screen.getByText('Product 2')).toBeInTheDocument();
    });
  });

  it('displays error on fetch failure', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('API Error'));

    render(<ProductList />);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
```

**4. Testing Context:**

```tsx
// useAuth.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from './AuthContext';

function TestComponent() {
  const { user, login, logout } = useAuth();

  return (
    <div>
      {user ? (
        <>
          <p>Logged in as {user.name}</p>
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <button onClick={() => login({ name: 'John' })}>Login</button>
      )}
    </div>
  );
}

it('logs in and out user', async () => {
  const user = userEvent.setup();

  render(
    <AuthProvider>
      <TestComponent />
    </AuthProvider>
  );

  // Not logged in initially
  expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();

  // Log in
  await user.click(screen.getByRole('button', { name: /login/i }));
  expect(screen.getByText(/logged in as john/i)).toBeInTheDocument();

  // Log out
  await user.click(screen.getByRole('button', { name: /logout/i }));
  expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
});
```

**Key Testing Principles:**
- Focus on user interactions (click, type, submit)
- Test behavior, not implementation details
- Use accessible queries (getByRole, getByLabelText)
- Handle async operations with waitFor
- Mock external dependencies (APIs, localStorage)
- Test edge cases and error states

### Package Managers (2024-2025)

#### **Recommendations:**

| Package Manager | Recommendation | Key Stats |
|----------------|----------------|-----------|
| **pnpm** | Strongly recommended for modern projects | 15.3M weekly downloads, 70% less disk space, fastest performance, excellent monorepo support |
| **npm** | Solid default choice | Bundled with Node.js, 7.3M weekly downloads, slower but reliable |
| **Yarn** | Use if existing project requires it | 7.3M weekly downloads, mature but declining adoption for new projects |

#### **pnpm - Recommended Choice**

**Why pnpm (2024-2025):**
- **Performance**: Fastest package manager in benchmarks
- **Disk Space**: Uses 70% less disk space via shared dependency model
- **Monorepo Support**: Built-in workspaces, filtering, and scoped commands
- **Security**: Strict dependency resolution prevents phantom dependencies
- **Modern**: Designed for modern JavaScript (ESM, TypeScript)

**Architecture:**
- Shared dependency store: All projects share a single copy of each package version
- Symlinks to node_modules: Fast installations without duplication
- Content-addressable storage: Only differences between versions are downloaded

**Installation:**
```bash
npm install -g pnpm
```

**Usage:**
```bash
pnpm create vite my-app --template react-ts
cd my-app
pnpm install
pnpm dev
```

**Workspace (Monorepo) Example - pnpm-workspace.yaml:**
```yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

**Key Commands:**
```bash
pnpm install          # Install dependencies
pnpm add zustand      # Add dependency
pnpm add -D vitest    # Add dev dependency
pnpm remove lodash    # Remove dependency
pnpm update           # Update dependencies
pnpm --filter app1 dev # Run script in specific workspace
```

#### **npm - Default Choice**

**When to Use:**
- Comes bundled with Node.js
- Simpler projects without complex requirements
- Teams already familiar with npm workflows

**Modern npm Features (npm 9+):**
- Faster performance improvements
- Better workspace support
- Improved security auditing

#### **Yarn - Legacy Projects**

**When to Use:**
- Existing projects using Yarn
- Teams with established Yarn workflows
- Projects requiring Yarn-specific plugins

**Note:** Yarn adoption is declining for new projects in favor of pnpm.

## 4. Performance and Production Best Practices

### Code Splitting and Optimization

#### **1. Route-Based Code Splitting (Highest Impact)**

Route-based splitting is the most effective place to start code splitting and achieves maximum bundle size reduction.

**React.lazy + Suspense:**

```tsx
import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// Lazy load route components
const Home = lazy(() => import('./pages/Home'));
const About = lazy(() => import('./pages/About'));
const Dashboard = lazy(() => import('./pages/Dashboard'));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

**TypeScript Typing:**
```tsx
// Type-safe lazy loading
const Dashboard = lazy(() =>
  import('./pages/Dashboard').then(module => ({
    default: module.Dashboard
  }))
);
```

#### **2. Component-Based Code Splitting**

Split large, non-essential, or conditional components.

**When to Split:**
- Large components with significant code or resources
- Conditional components (modals, tooltips, dropdowns)
- Secondary features (admin panels, settings)
- Heavy third-party libraries (charts, editors)

**Example:**
```tsx
import { lazy, Suspense, useState } from 'react';

// Split heavy components
const HeavyChart = lazy(() => import('./components/HeavyChart'));
const VideoPlayer = lazy(() => import('./components/VideoPlayer'));

function Dashboard() {
  const [showChart, setShowChart] = useState(false);

  return (
    <div>
      <h1>Dashboard</h1>
      <button onClick={() => setShowChart(!showChart)}>
        {showChart ? 'Hide' : 'Show'} Chart
      </button>

      {showChart && (
        <Suspense fallback={<div>Loading chart...</div>}>
          <HeavyChart />
        </Suspense>
      )}
    </div>
  );
}
```

#### **3. Dynamic Imports with Data Preloading**

**Prefetch Strategy:**
```tsx
import { lazy } from 'react';

const DashboardPage = lazy(() => import('./pages/Dashboard'));

function Navigation() {
  // Prefetch on hover
  const handleMouseEnter = () => {
    import('./pages/Dashboard'); // Start loading before navigation
  };

  return (
    <nav>
      <Link to="/dashboard" onMouseEnter={handleMouseEnter}>
        Dashboard
      </Link>
    </nav>
  );
}
```

#### **4. Vite Automatic Code Splitting**

Vite automatically splits code based on dynamic imports - no additional configuration needed.

**vite.config.ts (Advanced Optimization):**
```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate vendor chunks
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['zustand', '@tanstack/react-query'],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
});
```

#### **5. Bundle Analysis**

**Install:**
```bash
pnpm add -D rollup-plugin-visualizer
```

**vite.config.ts:**
```ts
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    visualizer({
      open: true,
      gzipSize: true,
      brotliSize: true,
    }),
  ],
});
```

**Run:**
```bash
pnpm build
# Opens bundle visualization in browser
```

#### **Best Practices:**
- Start with route-based splitting (highest ROI)
- Split components >50KB or with heavy dependencies
- Don't over-split - balance between requests and bundle size
- Use Suspense fallbacks for good UX
- Analyze bundles regularly with visualization tools
- Prefetch critical routes on hover/idle

### Type Safety Patterns

#### **1. Discriminated Unions for State**

```tsx
// Type-safe state management
type RequestState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: string };

function useApiRequest<T>(url: string) {
  const [state, setState] = useState<RequestState<T>>({ status: 'idle' });

  const fetchData = async () => {
    setState({ status: 'loading' });
    try {
      const response = await fetch(url);
      const data = await response.json();
      setState({ status: 'success', data });
    } catch (error) {
      setState({ status: 'error', error: (error as Error).message });
    }
  };

  return { state, fetchData };
}

// Usage - TypeScript enforces exhaustive checking
function DataDisplay() {
  const { state, fetchData } = useApiRequest<Product[]>('/api/products');

  // TypeScript ensures all states are handled
  switch (state.status) {
    case 'idle':
      return <button onClick={fetchData}>Load Data</button>;
    case 'loading':
      return <div>Loading...</div>;
    case 'success':
      return <div>{state.data.length} products</div>; // data is typed
    case 'error':
      return <div>Error: {state.error}</div>; // error is typed
  }
}
```

#### **2. Branded Types for IDs**

Prevent mixing different ID types.

```tsx
// Branded types
type UserId = string & { readonly __brand: 'UserId' };
type ProductId = string & { readonly __brand: 'ProductId' };

function createUserId(id: string): UserId {
  return id as UserId;
}

function createProductId(id: string): ProductId {
  return id as ProductId;
}

// Type-safe functions
function getUser(id: UserId): Promise<User> {
  return fetch(`/api/users/${id}`).then(r => r.json());
}

function getProduct(id: ProductId): Promise<Product> {
  return fetch(`/api/products/${id}`).then(r => r.json());
}

// Usage
const userId = createUserId('user-123');
const productId = createProductId('prod-456');

getUser(userId); // OK
getUser(productId); // TypeScript error - wrong type!
```

#### **3. Const Assertions for Literal Types**

```tsx
// Infer literal types
const BUTTON_VARIANTS = ['primary', 'secondary', 'danger'] as const;
type ButtonVariant = typeof BUTTON_VARIANTS[number]; // 'primary' | 'secondary' | 'danger'

const ROUTES = {
  HOME: '/',
  ABOUT: '/about',
  DASHBOARD: '/dashboard',
} as const;
type Route = typeof ROUTES[keyof typeof ROUTES]; // '/' | '/about' | '/dashboard'
```

#### **4. Type Guards**

```tsx
// User-defined type guards
function isError(value: unknown): value is Error {
  return value instanceof Error;
}

function isProduct(value: unknown): value is Product {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'name' in value
  );
}

// Usage
try {
  const data = await fetchData();
  if (isProduct(data)) {
    console.log(data.name); // TypeScript knows data is Product
  }
} catch (error) {
  if (isError(error)) {
    console.error(error.message); // TypeScript knows error is Error
  }
}
```

#### **5. Strict Null Checks**

Always enable `strict: true` in tsconfig.json.

```tsx
// Handle nullable values explicitly
interface User {
  name: string;
  email: string | null; // Explicitly nullable
}

function UserProfile({ user }: { user: User | null }) {
  // Must check for null
  if (!user) {
    return <div>No user</div>;
  }

  return (
    <div>
      <h1>{user.name}</h1>
      {/* Must check email nullability */}
      <p>{user.email ?? 'No email'}</p>
    </div>
  );
}
```

#### **6. Zod for Runtime Validation**

TypeScript only provides compile-time checking. Use Zod for runtime validation of external data (APIs, forms).

```bash
pnpm add zod
```

**Example:**
```tsx
import { z } from 'zod';

// Define schema
const ProductSchema = z.object({
  id: z.number(),
  name: z.string().min(1),
  price: z.number().positive(),
  inStock: z.boolean(),
});

// Infer TypeScript type from schema
type Product = z.infer<typeof ProductSchema>;

// Validate API response
async function fetchProducts(): Promise<Product[]> {
  const response = await fetch('/api/products');
  const data = await response.json();

  // Runtime validation
  const productsSchema = z.array(ProductSchema);
  const products = productsSchema.parse(data); // Throws if invalid

  return products;
}
```

### Bundle Optimization

#### **1. Tree Shaking**

Vite automatically tree-shakes unused code when using ES modules.

**Best Practices:**
```tsx
// GOOD: Named imports (tree-shakeable)
import { useState, useEffect } from 'react';
import { debounce } from 'lodash-es';

// AVOID: Default imports of entire libraries
import _ from 'lodash'; // Imports entire lodash
```

#### **2. Import Only What You Need**

```tsx
// GOOD: Specific imports
import debounce from 'lodash-es/debounce';
import { Button } from '@/components/Button';

// AVOID: Barrel imports (may import entire module)
import * as _ from 'lodash-es';
```

#### **3. Use Production Builds**

```bash
# Development (unoptimized)
pnpm dev

# Production (optimized, minified, tree-shaken)
pnpm build
pnpm preview
```

#### **4. Analyze Dependencies**

```bash
# Check bundle size impact before adding
pnpm dlx bundlephobia <package-name>

# Example
pnpm dlx bundlephobia moment
# Consider date-fns (smaller) or native Date APIs
```

#### **5. Lazy Load Third-Party Libraries**

```tsx
// Lazy load heavy libraries
import { lazy, Suspense } from 'react';

const ReactQuill = lazy(() => import('react-quill'));

function Editor() {
  return (
    <Suspense fallback={<div>Loading editor...</div>}>
      <ReactQuill />
    </Suspense>
  );
}
```

#### **6. Asset Optimization**

**vite.config.ts:**
```ts
export default defineConfig({
  build: {
    assetsInlineLimit: 4096, // Inline assets < 4KB as base64
    cssCodeSplit: true, // Split CSS into separate files
    minify: 'esbuild', // Fast minification
  },
});
```

## 5. Current Industry Standards

### What the React Team Recommends (2024-2025)

Based on official React documentation and blog posts:

#### **Build Tools**
- **Recommended**: Vite for SPAs, Next.js for full-stack
- **Deprecated**: Create React App (no longer maintained, last update 2022)
- **Reason**: Vite provides significantly faster development experience and better production builds

#### **Component Style**
- **Recommended**: Function components with hooks
- **Deprecated**: Class components (no new features, maintained for backward compatibility)
- **Note**: "Function components have become the de facto standard for React development"

#### **Refs**
- **React 19**: `ref` as a prop (no forwardRef needed)
- **Deprecated**: `React.forwardRef` (will be removed in future versions)

#### **Type Checking**
- **Recommended**: TypeScript
- **Deprecated**: PropTypes (removed from React package in v19)
- **Migration**: Use TypeScript or external type-checking solution

#### **JSX Transform**
- **Required**: New JSX transform (`jsx: "react-jsx"` in tsconfig.json)
- **Reason**: Enables React 19 features like ref as prop
- **Note**: No need to import React in every file

#### **Context**
- **Recommended**: Use for dependency injection (theme, auth, routing)
- **Not Recommended**: Use for frequently changing state (performance issues)
- **Alternative**: Zustand or state management libraries for state

#### **Server Components**
- **Status**: Stable in React 19 (December 2024)
- **Framework Support**: Next.js 15 (full support), React Router 7 (upcoming), TanStack Start
- **Recommendation**: Consider for new projects, especially with SEO requirements

#### **Data Fetching**
- **Recommended Pattern**: React Server Components for SSR, TanStack Query for client-side
- **Avoid**: useEffect for data fetching (prefer libraries with caching and error handling)

#### **Testing**
- **Recommended**: Vitest + React Testing Library
- **Philosophy**: Test user behavior, not implementation details
- **Accessibility**: Use accessible queries (getByRole, getByLabelText)

### Common Patterns in Modern React Applications (2024-2025)

#### **1. Project Structure**

```
src/
├── components/         # Reusable UI components
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx
│   │   └── index.ts
│   └── ...
├── pages/             # Route components
│   ├── Home.tsx
│   ├── Dashboard.tsx
│   └── ...
├── features/          # Feature-based modules
│   ├── auth/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── store.ts
│   │   └── types.ts
│   └── ...
├── hooks/             # Shared custom hooks
│   ├── useAuth.ts
│   ├── useDebounce.ts
│   └── ...
├── store/             # Global state (Zustand stores)
│   ├── authStore.ts
│   ├── uiStore.ts
│   └── ...
├── lib/               # Utilities and helpers
│   ├── api.ts
│   ├── utils.ts
│   └── ...
├── types/             # Shared TypeScript types
│   └── index.ts
├── App.tsx
└── main.tsx
```

#### **2. Custom Hooks Pattern**

Extract reusable logic into custom hooks.

```tsx
// useDebounce.ts
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}

// useLocalStorage.ts
function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue] as const;
}

// useMedia.ts (responsive design)
function useMedia(query: string): boolean {
  const [matches, setMatches] = useState(() => window.matchMedia(query).matches);

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    const handler = (event: MediaQueryListEvent) => setMatches(event.matches);

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [query]);

  return matches;
}
```

#### **3. Compound Components Pattern**

For flexible, composable component APIs.

```tsx
// Select.tsx
interface SelectContextValue {
  value: string;
  onChange: (value: string) => void;
}

const SelectContext = createContext<SelectContextValue | null>(null);

function Select({
  value,
  onChange,
  children
}: {
  value: string;
  onChange: (value: string) => void;
  children: React.ReactNode;
}) {
  return (
    <SelectContext.Provider value={{ value, onChange }}>
      <div className="select">{children}</div>
    </SelectContext.Provider>
  );
}

function Option({ value, children }: { value: string; children: React.ReactNode }) {
  const context = useContext(SelectContext);
  if (!context) throw new Error('Option must be within Select');

  return (
    <div
      className={`option ${context.value === value ? 'selected' : ''}`}
      onClick={() => context.onChange(value)}
    >
      {children}
    </div>
  );
}

// Export as compound component
Select.Option = Option;

// Usage
function App() {
  const [value, setValue] = useState('');

  return (
    <Select value={value} onChange={setValue}>
      <Select.Option value="red">Red</Select.Option>
      <Select.Option value="blue">Blue</Select.Option>
      <Select.Option value="green">Green</Select.Option>
    </Select>
  );
}
```

#### **4. Render Props Pattern (Less Common in 2024)**

Modern alternative: Custom hooks (preferred in 2024-2025).

```tsx
// OLD: Render props
<DataProvider render={(data) => <Display data={data} />} />

// MODERN: Custom hook
function useData() {
  const [data, setData] = useState(null);
  // ... fetch logic
  return data;
}

function Display() {
  const data = useData();
  return <div>{data}</div>;
}
```

#### **5. Error Boundaries (Class Component - Required)**

Error boundaries must be class components (React 19 doesn't provide hook alternative yet).

```tsx
import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div>
          <h1>Something went wrong</h1>
          <p>{this.state.error?.message}</p>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage
function App() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route path="/" element={<Home />} />
      </Routes>
    </ErrorBoundary>
  );
}
```

#### **6. Environment Variables (Vite)**

```typescript
// vite-env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_API_KEY: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// Usage in code
const apiUrl = import.meta.env.VITE_API_URL;

// .env file
VITE_API_URL=https://api.example.com
VITE_API_KEY=secret-key
```

### Deprecated Practices to Avoid (2024-2025)

#### **1. Create React App**
- **Status**: Unmaintained (last update 2022)
- **Alternative**: Vite, Next.js
- **Reason**: Slow build times, outdated dependencies, no active development

#### **2. Class Components**
- **Status**: Maintained but no new features
- **Alternative**: Function components with hooks
- **Reason**: Hooks provide simpler state management, better code reuse, smaller bundle size

#### **3. PropTypes**
- **Status**: Removed from React package in v19
- **Alternative**: TypeScript
- **Reason**: Runtime checking vs compile-time checking, TypeScript provides better DX

#### **4. React.FC (React.FunctionComponent)**
- **Status**: Not recommended (2024 consensus)
- **Alternative**: Standard function declarations
- **Reason**: Cannot use generics, implicit children type was problematic, removed in React 18

```tsx
// AVOID
const Button: React.FC<ButtonProps> = ({ title }) => {
  return <button>{title}</button>;
};

// RECOMMENDED
function Button({ title }: ButtonProps) {
  return <button>{title}</button>;
}
```

#### **5. forwardRef**
- **Status**: Deprecated in React 19
- **Alternative**: `ref` as a prop
- **Reason**: Simplified API, ref is now a standard prop

```tsx
// OLD (React 18)
const Input = forwardRef<HTMLInputElement, Props>((props, ref) => {
  return <input {...props} ref={ref} />;
});

// NEW (React 19)
function Input({ ref, ...props }: Props & { ref?: React.Ref<HTMLInputElement> }) {
  return <input {...props} ref={ref} />;
}
```

#### **6. String Refs**
- **Status**: Removed in React 19 (deprecated March 2018)
- **Alternative**: useRef hook or callback refs

```tsx
// REMOVED
<input ref="inputRef" />
this.refs.inputRef.focus();

// CORRECT
const inputRef = useRef<HTMLInputElement>(null);
<input ref={inputRef} />
inputRef.current?.focus();
```

#### **7. defaultProps (Function Components)**
- **Status**: Removed from function components in React 19
- **Alternative**: ES6 default parameters
- **Reason**: Simpler, more standard JavaScript

```tsx
// OLD
function Button({ title, variant }: ButtonProps) {
  // ...
}
Button.defaultProps = {
  variant: 'primary',
};

// NEW
function Button({ title, variant = 'primary' }: ButtonProps) {
  // ...
}
```

#### **8. Legacy Context API**
- **Status**: Removed in React 19 (deprecated October 2018)
- **Alternative**: createContext and useContext
- **Reason**: Better TypeScript support, simpler API, better performance

```tsx
// REMOVED
class Component extends React.Component {
  static contextTypes = { theme: PropTypes.string };
  render() {
    return <div>{this.context.theme}</div>;
  }
}

// CORRECT
const ThemeContext = createContext<string>('light');

function Component() {
  const theme = useContext(ThemeContext);
  return <div>{theme}</div>;
}
```

#### **9. Module Pattern Factories**
- **Status**: Removed in React 19 (deprecated August 2019)
- **Alternative**: Function components or class components

#### **10. createFactory**
- **Status**: Removed in React 19
- **Alternative**: JSX

```tsx
// REMOVED
const div = React.createFactory('div');
const element = div({ className: 'foo' }, 'Hello');

// CORRECT
const element = <div className="foo">Hello</div>;
```

#### **11. Data Fetching in useEffect**
- **Status**: Still works but not recommended
- **Alternative**: TanStack Query, React Server Components, SWR
- **Reason**: No caching, no deduplication, more boilerplate, harder error handling

```tsx
// DISCOURAGED (2024-2025)
function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetch('/api/products')
      .then(r => r.json())
      .then(data => setProducts(data))
      .catch(err => setError(err))
      .finally(() => setLoading(false));
  }, []);

  // ...
}

// RECOMMENDED (2024-2025)
import { useQuery } from '@tanstack/react-query';

function Products() {
  const { data: products, isLoading, error } = useQuery({
    queryKey: ['products'],
    queryFn: () => fetch('/api/products').then(r => r.json()),
  });

  // Automatic caching, refetching, error handling
}
```

#### **12. Index as Key in Lists**
- **Status**: Anti-pattern (always has been)
- **Alternative**: Stable unique identifiers
- **Reason**: Causes rendering bugs, lost state, performance issues

```tsx
// AVOID
{items.map((item, index) => (
  <div key={index}>{item.name}</div>
))}

// CORRECT
{items.map((item) => (
  <div key={item.id}>{item.name}</div>
))}
```

#### **13. Mutating State Directly**
- **Status**: Anti-pattern
- **Alternative**: Immutable updates

```tsx
// AVOID
const [items, setItems] = useState([1, 2, 3]);
items.push(4); // Direct mutation
setItems(items);

// CORRECT
setItems([...items, 4]); // New array
// or
setItems(prev => [...prev, 4]);
```

#### **14. Inline Object/Array Props**
- **Status**: Performance anti-pattern
- **Alternative**: useMemo or extracted variables

```tsx
// AVOID (creates new object every render)
<Component style={{ padding: 10 }} />

// CORRECT
const style = { padding: 10 };
<Component style={style} />

// or with useMemo for computed values
const style = useMemo(() => ({ padding: computePadding() }), [dependency]);
<Component style={style} />
```

## Action Items

Based on this research, here are specific steps to implement modern React + TypeScript development:

### 1. Project Initialization
```bash
# Choose based on project type
pnpm create vite my-app --template react-ts    # For SPAs
pnpm create next-app my-app --typescript       # For full-stack/SEO

cd my-app
pnpm install
```

### 2. Configure TypeScript
- Copy recommended `tsconfig.json` from Section 1
- Enable `strict: true` and `noUncheckedIndexedAccess: true`
- Set `jsx: "react-jsx"` for React 19 compatibility

### 3. Set Up Linting and Formatting
```bash
# ESLint + Prettier (recommended)
pnpm add -D eslint @eslint/js @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint-plugin-react eslint-plugin-react-hooks prettier eslint-config-prettier

# or Biome (alternative)
pnpm add -D @biomejs/biome
```

### 4. Configure Testing
```bash
pnpm add -D vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event @vitest/ui @vitest/coverage-v8
```
- Add test configuration to `vite.config.ts`
- Create `src/test/setup.ts` for test utilities

### 5. Add State Management (if needed)
```bash
# For client state
pnpm add zustand

# For server state
pnpm add @tanstack/react-query
```

### 6. Install React 19 Types
```bash
pnpm add --save-exact @types/react@^19.0.0 @types/react-dom@^19.0.0
```

### 7. Set Up Code Splitting
- Implement route-based splitting with React.lazy
- Add Suspense boundaries with fallback UI
- Configure Vite bundle analysis with rollup-plugin-visualizer

### 8. Configure Path Aliases
In `tsconfig.json`:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

In `vite.config.ts`:
```ts
import path from 'path';

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

### 9. Migrate from Legacy Patterns
- Replace `forwardRef` with ref as prop (React 19)
- Convert PropTypes to TypeScript interfaces
- Replace `React.FC` with function declarations
- Replace `defaultProps` with default parameters
- Update data fetching to use TanStack Query or Server Components

### 10. Implement Project Structure
- Organize by features or routes
- Separate components, hooks, and utilities
- Use barrel exports (index.ts) for cleaner imports

## Sources

### Official Documentation
- [React v19 Release Notes](https://react.dev/blog/2024/12/05/react-19) - React team, December 5, 2024
- [React 19 Upgrade Guide](https://react.dev/blog/2024/04/25/react-19-upgrade-guide) - React team, April 25, 2024
- [Using TypeScript with React](https://react.dev/learn/typescript) - Official React documentation
- [TypeScript Handbook: React](https://www.typescriptlang.org/docs/handbook/react.html) - TypeScript official docs
- [Vite Documentation](https://vite.dev/guide/) - Vite official guide (2024)
- [React Server Components Reference](https://react.dev/reference/rsc/server-components) - React official docs

### Authoritative Comparisons
- [Vite vs Next.js: 2025 Developer Framework Comparison](https://strapi.io/blog/vite-vs-nextjs-2025-developer-framework-comparison) - Strapi, 2025
- [Next.js vs. Vite: When to Choose Each](https://hygraph.com/blog/vite-vs-nextjs) - Hygraph, 2024
- [pnpm vs npm vs Yarn: Which Should You Choose in 2025?](https://medium.com/@djantchengamo/npm-yarn-or-pnpm-in-2025-which-package-manager-should-you-choose-d1a351810fd4) - Medium, 2025
- [pnpm Benchmarks](https://pnpm.io/benchmarks) - Official pnpm documentation

### State Management
- [React State Management in 2024](https://dev.to/nguyenhongphat0/react-state-management-in-2024-5e7l) - DEV Community, 2024
- [State Management in 2025: Context, Redux, Zustand, or Jotai](https://dev.to/hijazi313/state-management-in-2025-when-to-use-context-redux-zustand-or-jotai-2d2k) - DEV Community, 2025
- [Zustand Official Documentation](https://zustand.docs.pmnd.rs/) - pmndrs
- [Zustand and React Context](https://tkdodo.eu/blog/zustand-and-react-context) - TkDodo's blog (React Query maintainer)

### Tooling and Testing
- [Biome.js: Frontend Code Standards Revolution 2025](https://markaicode.com/biome-js-frontend-code-standards-revolution-2025/) - Markaicode, 2025
- [Migrate from ESLint and Prettier](https://biomejs.dev/guides/migrate-eslint-prettier/) - Biome official docs
- [Vitest with React Testing Library](https://blog.incubyte.co/blog/vitest-react-testing-library-guide/) - Incubyte, 2024
- [React Component Testing: Best Practices with Vitest (2025 Guide)](https://www.codingeasypeasy.com/blog/react-component-testing-best-practices-with-vitest-and-jest-2025-guide) - CodingEasyPeasy, 2025

### Patterns and Best Practices
- [React Design Patterns and Best Practices for 2025](https://www.telerik.com/blogs/react-design-patterns-best-practices) - Telerik, 2025
- [React and TypeScript Trends in 2024](https://thiraphat-ps-dev.medium.com/react-and-typescript-trends-in-2024-what-to-expect-df32a5d9bd6f) - Medium, 2024
- [React Trends in 2025](https://www.robinwieruch.de/react-trends/) - Robin Wieruch, 2025
- [TypeScript in React: Advancements and Best Practices in 2025](https://medium.com/@theNewGenCoder/typescript-in-react-advancements-and-best-practices-in-2025-c856f1564935) - Medium, 2025

### Performance
- [Optimizing React Apps with Code Splitting and Lazy Loading](https://medium.com/@ignatovich.dm/optimizing-react-apps-with-code-splitting-and-lazy-loading-e8c8791006e3) - Medium, 2024
- [Implementing Code Splitting and Lazy Loading in React](https://www.greatfrontend.com/blog/code-splitting-and-lazy-loading-in-react) - GreatFrontend, 2024
- [Making Sense of React Server Components](https://www.joshwcomeau.com/react/server-components/) - Josh W. Comeau, 2024

## Caveats

1. **React Server Components**: While stable in React 19 (December 2024), framework support varies. Next.js 15 has full support, but other frameworks are still adopting. Evaluate framework maturity before committing to RSC-heavy architecture.

2. **Biome vs ESLint**: Biome is significantly faster but covers only 64 of 200+ typescript-eslint rules. For production applications requiring comprehensive type-aware linting, ESLint + typescript-eslint remains the safer choice as of 2024-2025.

3. **Migration Complexity**: React 19's deprecations (forwardRef, PropTypes, defaultProps) require codemod usage for large codebases. The `types-react-codemod` tool helps, but manual verification is essential.

4. **Bundle Size Trade-offs**: Over-aggressive code splitting can increase the number of HTTP requests and degrade performance. Benchmark your specific application to find the optimal split strategy.

5. **pnpm Adoption**: While pnpm offers clear performance advantages, some legacy tooling and CI/CD pipelines may require adjustments. Verify compatibility with your existing infrastructure before migration.

6. **TypeScript Strict Mode**: Enabling `strict: true` on existing codebases can surface hundreds of type errors. Plan for gradual migration by enabling strict checks incrementally.

7. **Hook Dependencies**: React's exhaustive-deps ESLint rule can be overly aggressive. Understanding when to suppress warnings vs fixing dependency arrays requires experience.

8. **Version Currency**: This research reflects the landscape as of October 2025. React 19 was released December 2024, making some patterns still stabilizing. Monitor official React documentation for updates beyond this date.
