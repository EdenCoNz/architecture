/**
 * TypeScript Type Definitions for Basic Login API
 *
 * Feature: 20 - Basic Login Functionality
 * Contract Version: 1.0
 * Last Updated: 2025-11-02
 *
 * This file contains all TypeScript interfaces and types for the basic login API.
 * Both frontend and backend (if using TypeScript) should use these types to ensure
 * type safety and consistency with the API contract.
 */

// ============================================================================
// Request Types
// ============================================================================

/**
 * Request payload for basic login/registration
 */
export interface BasicLoginRequest {
  /** User's full name (first and last name) */
  name: string;
  /** User's email address (unique identifier) */
  email: string;
}

/**
 * Request payload for token refresh
 */
export interface TokenRefreshRequest {
  /** Valid refresh token from login response */
  refresh: string;
}

/**
 * Request payload for logout
 */
export interface LogoutRequest {
  /** Refresh token to blacklist */
  refresh: string;
}

// ============================================================================
// Response Types
// ============================================================================

/**
 * User profile information
 */
export interface UserProfile {
  /** User's database ID */
  id: number;
  /** User's email address */
  email: string;
  /** User's first name */
  first_name: string;
  /** User's last name */
  last_name: string;
  /** Whether the account is active */
  is_active: boolean;
  /** ISO 8601 datetime when the account was created */
  date_joined: string;
}

/**
 * JWT token pair returned from authentication
 */
export interface JWTTokens {
  /** Access token (valid for 15 minutes) */
  access: string;
  /** Refresh token (valid for 7 days) */
  refresh: string;
}

/**
 * Response from successful basic login (existing user)
 */
export interface BasicLoginSuccessResponse {
  /** Success message */
  message: string;
  /** User profile information */
  user: UserProfile;
  /** JWT access token */
  access: string;
  /** JWT refresh token */
  refresh: string;
  /** Indicates if this is a new user (false for existing) */
  is_new_user: boolean;
}

/**
 * Response from successful basic login (new user)
 */
export interface BasicLoginCreatedResponse {
  /** Success message */
  message: string;
  /** User profile information */
  user: UserProfile;
  /** JWT access token */
  access: string;
  /** JWT refresh token */
  refresh: string;
  /** Indicates if this is a new user (true for new) */
  is_new_user: boolean;
}

/**
 * Union type for basic login responses
 * Use this type when handling login responses to cover both status codes (200 and 201)
 */
export type BasicLoginResponse = BasicLoginSuccessResponse | BasicLoginCreatedResponse;

/**
 * Response from token refresh
 */
export interface TokenRefreshResponse {
  /** New access token */
  access: string;
  /** New refresh token (if rotation enabled) */
  refresh: string;
}

/**
 * Response from successful logout
 */
export interface LogoutResponse {
  /** Success message */
  message: string;
}

/**
 * Response from get current user endpoint
 */
export type CurrentUserResponse = UserProfile;

// ============================================================================
// Error Types
// ============================================================================

/**
 * Validation error response with field-specific errors
 * Used for 400 Bad Request responses
 */
export interface ValidationErrorResponse {
  /** Field name mapped to array of error messages */
  [field: string]: string[];
}

/**
 * Generic error response
 * Used for various error status codes (403, 429, 500, 503)
 */
export interface ErrorResponse {
  /** Error message */
  error: string;
  /** Optional error details */
  details?: string;
}

/**
 * JWT token error response
 * Used for 401 Unauthorized responses
 */
export interface TokenErrorResponse {
  /** Error description */
  detail: string;
  /** Error code */
  code: string;
  /** Additional error messages */
  messages?: Array<{
    token_class: string;
    token_type: string;
    message: string;
  }>;
}

/**
 * Union type for all possible error responses
 */
export type ApiErrorResponse = ValidationErrorResponse | ErrorResponse | TokenErrorResponse;

// ============================================================================
// Enums and Constants
// ============================================================================

/**
 * HTTP status codes used in the API
 */
export const HttpStatus = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
} as const;

/**
 * API endpoints
 */
export const API_ENDPOINTS = {
  BASIC_LOGIN: '/api/v1/auth/basic/',
  CURRENT_USER: '/api/v1/auth/me/',
  TOKEN_REFRESH: '/api/v1/auth/token/refresh/',
  LOGOUT: '/api/v1/auth/logout/',
} as const;

/**
 * Token expiration times
 */
export const TOKEN_EXPIRY = {
  /** Access token validity in minutes */
  ACCESS_TOKEN_MINUTES: 15,
  /** Refresh token validity in days */
  REFRESH_TOKEN_DAYS: 7,
} as const;

/**
 * Field validation constraints
 */
export const VALIDATION_CONSTRAINTS = {
  /** Maximum length for name field */
  NAME_MAX_LENGTH: 255,
  /** Maximum length for email field */
  EMAIL_MAX_LENGTH: 254,
} as const;

/**
 * Rate limits
 */
export const RATE_LIMITS = {
  /** Basic login requests per minute */
  BASIC_LOGIN_PER_MINUTE: 10,
} as const;

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Type guard to check if response is a validation error
 */
export function isValidationError(error: unknown): error is ValidationErrorResponse {
  return (
    typeof error === 'object' &&
    error !== null &&
    Object.values(error).every((val) => Array.isArray(val))
  );
}

/**
 * Type guard to check if response is a token error
 */
export function isTokenError(error: unknown): error is TokenErrorResponse {
  return (
    typeof error === 'object' &&
    error !== null &&
    'detail' in error &&
    'code' in error
  );
}

/**
 * Type guard to check if response is a generic error
 */
export function isGenericError(error: unknown): error is ErrorResponse {
  return (
    typeof error === 'object' &&
    error !== null &&
    'error' in error &&
    typeof (error as ErrorResponse).error === 'string'
  );
}

/**
 * Type guard to check if login response indicates a new user
 */
export function isNewUser(response: BasicLoginResponse): response is BasicLoginCreatedResponse {
  return response.is_new_user === true;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * API response wrapper that includes status code
 */
export interface ApiResponse<T> {
  /** HTTP status code */
  status: number;
  /** Response data */
  data: T;
}

/**
 * API error wrapper
 */
export interface ApiError {
  /** HTTP status code */
  status: number;
  /** Error response */
  error: ApiErrorResponse;
}

/**
 * Result type for API calls (either success or error)
 */
export type ApiResult<T> = ApiResponse<T> | ApiError;

// ============================================================================
// Helper Functions Types
// ============================================================================

/**
 * Function signature for basic login
 */
export type BasicLoginFunction = (
  request: BasicLoginRequest
) => Promise<BasicLoginResponse>;

/**
 * Function signature for getting current user
 */
export type GetCurrentUserFunction = () => Promise<CurrentUserResponse>;

/**
 * Function signature for refreshing token
 */
export type RefreshTokenFunction = (
  request: TokenRefreshRequest
) => Promise<TokenRefreshResponse>;

/**
 * Function signature for logout
 */
export type LogoutFunction = (request: LogoutRequest) => Promise<LogoutResponse>;

// ============================================================================
// Token Storage Interface
// ============================================================================

/**
 * Interface for token storage operations
 */
export interface TokenStorage {
  /** Store access and refresh tokens */
  storeTokens(access: string, refresh: string): void;

  /** Retrieve access token */
  getAccessToken(): string | null;

  /** Retrieve refresh token */
  getRefreshToken(): string | null;

  /** Clear all tokens */
  clearTokens(): void;

  /** Check if user is authenticated (has valid tokens) */
  isAuthenticated(): boolean;
}

// ============================================================================
// Auth Context Types
// ============================================================================

/**
 * Authentication state
 */
export interface AuthState {
  /** Current authenticated user (null if not authenticated) */
  user: UserProfile | null;
  /** Whether authentication is in progress */
  isLoading: boolean;
  /** Whether user is authenticated */
  isAuthenticated: boolean;
  /** Authentication error (if any) */
  error: string | null;
}

/**
 * Authentication context actions
 */
export interface AuthActions {
  /** Login with name and email */
  login: (name: string, email: string) => Promise<void>;

  /** Logout current user */
  logout: () => Promise<void>;

  /** Refresh access token */
  refreshToken: () => Promise<boolean>;

  /** Get current user profile */
  getCurrentUser: () => Promise<void>;

  /** Clear authentication error */
  clearError: () => void;
}

/**
 * Complete authentication context
 */
export interface AuthContext extends AuthState, AuthActions {}

// ============================================================================
// Form Validation Types
// ============================================================================

/**
 * Form field errors
 */
export interface FormErrors {
  name?: string;
  email?: string;
  general?: string;
}

/**
 * Form state
 */
export interface LoginFormState {
  /** Form values */
  values: {
    name: string;
    email: string;
  };
  /** Form errors */
  errors: FormErrors;
  /** Whether form is submitting */
  isSubmitting: boolean;
  /** Whether form has been touched */
  touched: {
    name: boolean;
    email: boolean;
  };
}

// ============================================================================
// Example Usage (commented out for documentation purposes)
// ============================================================================

/*
// Example: Basic Login
const loginUser = async (name: string, email: string): Promise<BasicLoginResponse> => {
  const response = await fetch(API_ENDPOINTS.BASIC_LOGIN, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name, email } as BasicLoginRequest),
  });

  if (!response.ok) {
    const error: ApiErrorResponse = await response.json();
    throw new Error(JSON.stringify(error));
  }

  const data: BasicLoginResponse = await response.json();
  return data;
};

// Example: Get Current User
const getCurrentUser = async (accessToken: string): Promise<CurrentUserResponse> => {
  const response = await fetch(API_ENDPOINTS.CURRENT_USER, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to get current user');
  }

  const data: CurrentUserResponse = await response.json();
  return data;
};

// Example: Token Refresh
const refreshAccessToken = async (refreshToken: string): Promise<TokenRefreshResponse> => {
  const response = await fetch(API_ENDPOINTS.TOKEN_REFRESH, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh: refreshToken } as TokenRefreshRequest),
  });

  if (!response.ok) {
    throw new Error('Failed to refresh token');
  }

  const data: TokenRefreshResponse = await response.json();
  return data;
};

// Example: Error Handling
const handleLoginError = (error: unknown) => {
  if (isValidationError(error)) {
    // Handle validation errors (400)
    console.error('Validation errors:', error);
    if (error.email) {
      console.error('Email errors:', error.email);
    }
    if (error.name) {
      console.error('Name errors:', error.name);
    }
  } else if (isTokenError(error)) {
    // Handle token errors (401)
    console.error('Token error:', error.detail);
  } else if (isGenericError(error)) {
    // Handle generic errors (403, 429, 500, 503)
    console.error('Error:', error.error);
  } else {
    // Handle unknown errors
    console.error('Unknown error:', error);
  }
};

// Example: Type Guard Usage
const processLoginResponse = (response: BasicLoginResponse) => {
  if (isNewUser(response)) {
    console.log('Welcome new user!', response.user);
  } else {
    console.log('Welcome back!', response.user);
  }
};
*/
