/**
 * API Service
 *
 * Centralized API client for making HTTP requests to the backend.
 * Handles request configuration, error handling, and response parsing.
 *
 * Story-10.3: API Call Functionality
 */

import { config } from '../config';

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
