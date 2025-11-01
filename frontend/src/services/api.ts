/**
 * API Service
 *
 * Centralized API client for making HTTP requests to the backend.
 * Handles request configuration, error handling, and response parsing.
 *
 * Story-10.3: API Call Functionality
 *
 * Uses runtime configuration loaded from backend API endpoint to ensure
 * the same frontend image works across all environments without rebuilding.
 */

import { getRuntimeConfig } from '../config/runtimeConfig';

/**
 * API Response from backend test endpoint
 */
export interface ApiTestResponse {
  /** Success message from backend */
  message: string;
  /** Timestamp when response was generated (ISO 8601 format) */
  timestamp: string;
}

/**
 * Assessment form data structure for submission
 */
export interface AssessmentData {
  sport: string | null;
  age: number | null;
  experienceLevel: string | null;
  trainingDays: string | null;
  injuries: string | null;
  equipment: string[];
}

/**
 * API Response from assessment submission endpoint
 */
export interface AssessmentResponse {
  /** Success indicator */
  success: boolean;
  /** Assessment ID if successfully created */
  id?: string;
  /** Response message */
  message?: string;
}

/**
 * API Error with user-friendly message
 */
export class ApiError extends Error {
  status?: number;
  statusText?: string;

  constructor(message: string, status?: number, statusText?: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.statusText = statusText;
  }
}

/**
 * Test backend connection
 *
 * Calls the backend test endpoint to verify connectivity and data exchange.
 *
 * @returns Promise resolving to test response data
 * @throws ApiError if request fails or backend is unreachable
 */
export async function testBackendConnection(): Promise<ApiTestResponse> {
  const config = getRuntimeConfig();
  const apiUrl = config.api.baseUrl;
  const endpoint = `${apiUrl}/api/v1/test/`;

  try {
    // Make HTTP request with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), config.api.timeout);

    const response = await fetch(endpoint, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Check if response is ok (status 200-299)
    if (!response.ok) {
      throw new ApiError(
        `Backend returned error: ${response.status} ${response.statusText}`,
        response.status,
        response.statusText
      );
    }

    // Parse JSON response
    const data = await response.json();

    // Validate response structure
    if (!data.message || !data.timestamp) {
      throw new ApiError('Invalid response format from backend');
    }

    return data as ApiTestResponse;
  } catch (error) {
    // Handle different error types
    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof Error) {
      // Handle abort/timeout errors
      if (error.name === 'AbortError') {
        throw new ApiError('Request timeout - backend took too long to respond');
      }

      // Handle network errors
      if (error.message.includes('fetch')) {
        throw new ApiError('Connection failed - unable to reach backend server');
      }

      // Handle JSON parsing errors
      if (error.message.includes('JSON')) {
        throw new ApiError('Invalid response format from backend');
      }

      // Generic error
      throw new ApiError(`Connection failed: ${error.message}`);
    }

    // Unknown error type
    throw new ApiError('An unexpected error occurred');
  }
}

/**
 * Basic Login Request data structure
 */
export interface BasicLoginRequest {
  name: string;
  email: string;
}

/**
 * Basic Login Response data structure
 */
export interface BasicLoginResponse {
  message: string;
  user: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    is_active: boolean;
    date_joined: string;
  };
  access: string;
  refresh: string;
  is_new_user: boolean;
}

/**
 * Submit basic login credentials
 *
 * Authenticates or registers a user using only their name and email address.
 * If the email exists, the user's name is updated. If the email is new, a new
 * user account is created.
 *
 * @param name - User's full name
 * @param email - User's email address
 * @returns Promise resolving to login response with JWT tokens and user data
 * @throws ApiError if request fails or validation errors occur
 *
 * Story 20.5: Submit login information
 * Story 20.9: Handle login errors gracefully
 */
export async function submitBasicLogin(name: string, email: string): Promise<BasicLoginResponse> {
  const config = getRuntimeConfig();
  const apiUrl = config.api.baseUrl;
  const endpoint = `${apiUrl}/api/v1/auth/basic/`;

  try {
    // Prepare request payload
    const requestData: BasicLoginRequest = {
      name,
      email,
    };

    // Make HTTP request with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), config.api.timeout);

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Check if response is ok (status 200-299)
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));

      // Handle validation errors (400)
      // AC: Clear feedback when validation fails
      if (response.status === 400 && errorData && typeof errorData === 'object') {
        // Combine validation errors into readable message
        const errorMessages: string[] = [];
        Object.entries(errorData).forEach(([field, messages]) => {
          if (Array.isArray(messages)) {
            errorMessages.push(`${field}: ${messages.join(', ')}`);
          }
        });
        throw new ApiError(
          errorMessages.length > 0
            ? errorMessages.join('; ')
            : 'Please check your name and email and try again.',
          response.status,
          response.statusText
        );
      }

      // Handle rate limiting (429)
      // AC: Clear feedback when rate limit is exceeded
      if (response.status === 429) {
        const errorMessage =
          errorData && typeof errorData === 'object' && 'error' in errorData
            ? (errorData.error as string)
            : 'Too many login attempts. Please wait a moment and try again.';
        throw new ApiError(errorMessage, response.status, response.statusText);
      }

      // Handle service unavailable (503)
      // AC: When system is unavailable, show message indicating service is temporarily unavailable
      if (response.status === 503) {
        const errorMessage =
          errorData && typeof errorData === 'object' && 'error' in errorData
            ? (errorData.error as string)
            : 'The service is temporarily unavailable. Please try again in a few moments.';
        throw new ApiError(errorMessage, response.status, response.statusText);
      }

      // Handle internal server error (500)
      // AC: When system returns an error, provide clear feedback
      if (response.status === 500) {
        const errorMessage =
          errorData && typeof errorData === 'object' && 'error' in errorData
            ? (errorData.error as string)
            : 'Something went wrong on our end. Please try again in a few moments.';
        throw new ApiError(errorMessage, response.status, response.statusText);
      }

      // Handle other errors (403, etc.)
      if (errorData && typeof errorData === 'object' && 'error' in errorData) {
        throw new ApiError(errorData.error as string, response.status, response.statusText);
      }

      // Fallback error message
      throw new ApiError(
        `Unable to complete login. Please try again.`,
        response.status,
        response.statusText
      );
    }

    // Parse JSON response
    const data = await response.json();

    return data as BasicLoginResponse;
  } catch (error) {
    // Handle different error types
    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof Error) {
      // Handle abort/timeout errors
      // AC: When request times out, show message explaining the connection issue
      if (error.name === 'AbortError') {
        throw new ApiError(
          'The connection is taking too long. Please check your internet connection and try again.'
        );
      }

      // Handle network errors
      // AC: When there's a network error, show message explaining the connection issue
      if (
        error.message.includes('fetch') ||
        error.message.includes('NetworkError') ||
        error.message.includes('Failed to fetch')
      ) {
        throw new ApiError(
          'Unable to connect to the server. Please check your internet connection and try again.'
        );
      }

      // Handle JSON parsing errors
      if (error.message.includes('JSON')) {
        throw new ApiError('Received an unexpected response from the server. Please try again.');
      }

      // Generic error
      throw new ApiError(`Unable to complete login: ${error.message}. Please try again.`);
    }

    // Unknown error type
    throw new ApiError('An unexpected error occurred. Please try again.');
  }
}

/**
 * Submit user assessment data
 *
 * Sends user onboarding assessment information to the backend for storage
 * and program generation.
 *
 * @param data - Assessment form data
 * @returns Promise resolving to submission response
 * @throws ApiError if request fails or validation errors occur
 *
 * Story 11.7: Complete Assessment Form
 */
export async function submitAssessment(data: AssessmentData): Promise<AssessmentResponse> {
  const config = getRuntimeConfig();
  const apiUrl = config.api.baseUrl;
  const endpoint = `${apiUrl}/api/v1/assessments/`;

  try {
    // Make HTTP request with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), config.api.timeout);

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Check if response is ok (status 200-299)
    if (!response.ok) {
      throw new ApiError(
        `Failed to submit assessment: ${response.status} ${response.statusText}`,
        response.status,
        response.statusText
      );
    }

    // Parse JSON response
    const responseData = await response.json();

    return {
      success: true,
      id: responseData.id,
      message: responseData.message,
    };
  } catch (error) {
    // Handle different error types
    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof Error) {
      // Handle abort/timeout errors
      if (error.name === 'AbortError') {
        throw new ApiError('Request timeout - submission took too long');
      }

      // Handle network errors
      if (error.message.includes('fetch')) {
        throw new ApiError('Connection failed - unable to reach backend server');
      }

      // Handle JSON parsing errors
      if (error.message.includes('JSON')) {
        throw new ApiError('Invalid response format from backend');
      }

      // Generic error
      throw new ApiError(`Submission failed: ${error.message}`);
    }

    // Unknown error type
    throw new ApiError('An unexpected error occurred during submission');
  }
}
