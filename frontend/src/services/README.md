# API Service Layer

This directory contains the service layer for backend communication.

## Overview

The API service layer provides a consistent interface for making HTTP requests to the backend API. It handles:

- Network errors and timeouts
- HTTP error responses
- Response formatting
- Type safety with TypeScript

## Usage

### Basic Health Check

```typescript
import { apiService } from '@/services';

// Check backend health
try {
  const response = await apiService.getHealth();
  console.log('Backend status:', response.data.status);
  console.log('Database connected:', response.data.database.connected);
} catch (error) {
  if (error instanceof ApiError) {
    console.error('API Error:', error.message, 'Status:', error.status);
  }
}
```

### Using in React Components

```typescript
import { useState } from 'react';
import { apiService, ApiError } from '@/services';
import type { HealthCheckResponse } from '@/types';

function HealthStatus() {
  const [health, setHealth] = useState<HealthCheckResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.getHealth();
      setHealth(response.data);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={checkHealth} disabled={loading}>
        {loading ? 'Checking...' : 'Check Health'}
      </button>
      {error && <p>Error: {error}</p>}
      {health && <p>Status: {health.status}</p>}
    </div>
  );
}
```

## Configuration

The API service uses environment variables for configuration:

- `VITE_API_URL`: Base URL for the backend API (default: `http://localhost:8000`)

Set these in your `.env.development` or `.env.production` files.

## Error Handling

All API methods throw `ApiError` instances on failure. The error includes:

- `message`: Human-readable error description
- `status`: HTTP status code (0 for network errors)
- `details`: Optional additional error information

## Available Methods

### `getHealth()`

Checks the health status of the backend API and database.

**Returns:** `Promise<ApiResponse<HealthCheckResponse>>`

**Throws:** `ApiError`

### `getBaseUrl()`

Returns the configured base API URL. Useful for debugging.

**Returns:** `string`

## Testing

Comprehensive test coverage is provided in `tests/unit/services/api.test.ts`.

Run tests with:

```bash
npm test -- tests/unit/services/api.test.ts
```

## Architecture

The service layer follows these principles:

1. **Consistent Response Format**: All methods return `ApiResponse<T>` with `data` and `status`
2. **Graceful Error Handling**: Network errors, timeouts, and HTTP errors are caught and thrown as `ApiError`
3. **Type Safety**: Full TypeScript support with proper type definitions
4. **Testability**: Easy to mock and test with dependency injection
5. **Timeout Protection**: 10-second default timeout prevents hanging requests
