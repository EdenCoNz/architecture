/**
 * API Service Layer
 *
 * Handles HTTP communication with the backend API.
 * Provides methods for all API endpoints with consistent error handling.
 */

import type {
  HealthCheckResponse,
  ApiResponse,
  ApiError,
  ThemePreferenceResponse,
  ThemePreferenceRequest,
} from '@/types';

/**
 * Base API configuration
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const DEFAULT_TIMEOUT = 10000; // 10 seconds

/**
 * Custom error class for API errors
 */
class ApiErrorClass extends Error implements ApiError {
  status: number;
  details?: Record<string, unknown>;

  constructor(message: string, status: number, details?: Record<string, unknown>) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

/**
 * Make HTTP request with timeout and error handling
 */
async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeout: number = DEFAULT_TIMEOUT
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);

    // Handle abort/timeout
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiErrorClass('Request timeout', 0);
    }

    // Re-throw as ApiError
    if (error instanceof Error) {
      throw new ApiErrorClass(error.message, 0);
    }

    // Fallback for unknown errors
    throw new ApiErrorClass('An unknown error occurred', 0);
  }
}

/**
 * Handle API response and errors
 */
async function handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
  if (!response.ok) {
    throw new ApiErrorClass(
      `HTTP error: ${response.status} ${response.statusText}`,
      response.status
    );
  }

  try {
    const data = await response.json();
    return {
      data,
      status: response.status,
    };
  } catch (error) {
    if (error instanceof SyntaxError) {
      throw new ApiErrorClass('Invalid JSON response', response.status);
    }
    throw error;
  }
}

/**
 * API Service
 * Provides methods for all backend API endpoints
 */
export const apiService = {
  /**
   * Health Check
   * GET /health/
   *
   * Checks the health status of the backend API and database.
   *
   * @returns Promise<ApiResponse<HealthCheckResponse>>
   * @throws ApiError
   */
  async getHealth(): Promise<ApiResponse<HealthCheckResponse>> {
    const url = `${API_BASE_URL}/health/`;

    const response = await fetchWithTimeout(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    return handleResponse<HealthCheckResponse>(response);
  },

  /**
   * Get the base API URL
   * Useful for debugging and testing
   */
  getBaseUrl(): string {
    return API_BASE_URL;
  },

  /**
   * Get Theme Preference
   * GET /api/preferences/theme/
   *
   * Retrieves the user's theme preference from the backend.
   * Requires authentication.
   *
   * @returns Promise<ApiResponse<ThemePreferenceResponse>>
   * @throws ApiError
   */
  async getThemePreference(): Promise<ApiResponse<ThemePreferenceResponse>> {
    const url = `${API_BASE_URL}/api/preferences/theme/`;

    const response = await fetchWithTimeout(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Include cookies for authentication
    });

    return handleResponse<ThemePreferenceResponse>(response);
  },

  /**
   * Update Theme Preference
   * PATCH /api/preferences/theme/
   *
   * Updates the user's theme preference on the backend.
   * Requires authentication.
   *
   * @param theme - Theme mode to set ('light', 'dark', or 'auto')
   * @returns Promise<ApiResponse<ThemePreferenceResponse>>
   * @throws ApiError
   */
  async updateThemePreference(
    theme: ThemePreferenceRequest['theme']
  ): Promise<ApiResponse<ThemePreferenceResponse>> {
    const url = `${API_BASE_URL}/api/preferences/theme/`;

    const response = await fetchWithTimeout(url, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Include cookies for authentication
      body: JSON.stringify({ theme }),
    });

    return handleResponse<ThemePreferenceResponse>(response);
  },
};

/**
 * Export API error class for use in error boundaries and catch blocks
 */
export { ApiErrorClass as ApiError };

/**
 * Default export
 */
export default apiService;
