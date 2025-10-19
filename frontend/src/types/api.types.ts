/**
 * API Type Definitions
 *
 * TypeScript types for API requests and responses.
 * These types ensure type safety when communicating with the backend.
 */

/**
 * Health Check Response
 * Matches the backend /health/ endpoint response structure
 */
export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  version: string;
  service: string;
  database: {
    status: 'healthy' | 'unhealthy';
    connected: boolean;
    engine: string;
  };
  debug_mode: boolean;
}

/**
 * Generic API Response wrapper for successful responses
 */
export interface ApiResponse<T> {
  data: T;
  status: number;
}

/**
 * API Error Response
 * Standardized error structure for all API errors
 */
export interface ApiError {
  message: string;
  status: number;
  details?: Record<string, unknown>;
}

/**
 * API Request State
 * Discriminated union for tracking API request states
 */
export type ApiRequestState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: ApiError };
