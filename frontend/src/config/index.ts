/**
 * Frontend Application Configuration
 *
 * This module provides a centralized, type-safe configuration system that:
 * - Loads environment-specific settings from Vite's env variables
 * - Validates required configuration at application startup
 * - Provides secure access to configuration without exposing sensitive values
 * - Supports multiple environments (local, staging, production)
 *
 * Configuration values are injected at build time via Vite and should never
 * be hardcoded. Sensitive values should not be exposed in client-side code.
 *
 * @see https://vitejs.dev/guide/env-and-mode.html
 */

/**
 * Application Environment Type
 */
export type Environment = 'development' | 'staging' | 'production' | 'test';

/**
 * Application Configuration Interface
 *
 * All configuration values that the application needs should be defined here.
 * This provides type safety and autocomplete for configuration access.
 */
export interface AppConfig {
  /** Current environment */
  environment: Environment;

  /** Is the application running in production mode */
  isProduction: boolean;

  /** Is the application running in development mode */
  isDevelopment: boolean;

  /** Is the application running in test mode */
  isTest: boolean;

  /** API Configuration */
  api: {
    /** Base URL for backend API */
    baseUrl: string;

    /** API request timeout in milliseconds */
    timeout: number;

    /** Enable request/response logging */
    enableLogging: boolean;
  };

  /** Application Settings */
  app: {
    /** Application name */
    name: string;

    /** Application version */
    version: string;

    /** Application title (for browser tab) */
    title: string;

    /** Enable debug mode features */
    debug: boolean;
  };

  /** Feature Flags */
  features: {
    /** Enable analytics tracking */
    enableAnalytics: boolean;

    /** Enable error reporting (e.g., Sentry) */
    enableErrorReporting: boolean;

    /** Enable service worker for offline support */
    enableServiceWorker: boolean;
  };

  /** Security Settings */
  security: {
    /** Enable Content Security Policy headers */
    enableCSP: boolean;

    /** Maximum login attempts before lockout */
    maxLoginAttempts: number;
  };
}

/**
 * Configuration Validation Error
 *
 * Thrown when required configuration is missing or invalid
 */
export class ConfigValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ConfigValidationError';
  }
}

/**
 * Get environment variable with validation
 *
 * @param key - Environment variable key (without VITE_ prefix)
 * @param defaultValue - Default value if not set
 * @param required - Whether this variable is required
 * @returns Environment variable value
 * @throws ConfigValidationError if required variable is missing
 */
function getEnv(key: string, defaultValue?: string, required = false): string {
  const fullKey = `VITE_${key}`;
  const value = import.meta.env[fullKey] as string | undefined;

  if (!value && required) {
    throw new ConfigValidationError(
      `Missing required environment variable: ${fullKey}. ` +
        `Please check your .env file or build configuration.`
    );
  }

  return value || defaultValue || '';
}

/**
 * Get boolean environment variable
 *
 * @param key - Environment variable key (without VITE_ prefix)
 * @param defaultValue - Default value if not set
 * @returns Boolean value
 */
function getBooleanEnv(key: string, defaultValue = false): boolean {
  const value = getEnv(key, String(defaultValue));
  return value === 'true' || value === '1';
}

/**
 * Get number environment variable
 *
 * @param key - Environment variable key (without VITE_ prefix)
 * @param defaultValue - Default value if not set
 * @param min - Minimum allowed value
 * @param max - Maximum allowed value
 * @returns Number value
 * @throws ConfigValidationError if value is not a valid number or out of range
 */
function getNumberEnv(key: string, defaultValue: number, min?: number, max?: number): number {
  const value = getEnv(key, String(defaultValue));
  const numValue = Number(value);

  if (isNaN(numValue)) {
    throw new ConfigValidationError(
      `Environment variable VITE_${key} must be a valid number, got: ${value}`
    );
  }

  if (min !== undefined && numValue < min) {
    throw new ConfigValidationError(
      `Environment variable VITE_${key} must be >= ${min}, got: ${numValue}`
    );
  }

  if (max !== undefined && numValue > max) {
    throw new ConfigValidationError(
      `Environment variable VITE_${key} must be <= ${max}, got: ${numValue}`
    );
  }

  return numValue;
}

/**
 * Determine current environment
 *
 * @returns Current environment
 */
function getEnvironment(): Environment {
  const mode = import.meta.env.MODE;
  const nodeEnv = import.meta.env.VITE_NODE_ENV as string | undefined;

  // Map Vite modes to our environment types
  if (mode === 'test' || nodeEnv === 'test') {
    return 'test';
  }

  if (mode === 'production') {
    // Allow overriding production to staging via env variable
    return (nodeEnv as Environment) || 'production';
  }

  // Default to development for all other modes
  return 'development';
}

/**
 * Validate API URL format
 *
 * @param url - URL to validate
 * @throws ConfigValidationError if URL is invalid
 */
function validateApiUrl(url: string): void {
  if (!url) {
    throw new ConfigValidationError('API URL cannot be empty');
  }

  try {
    const parsed = new URL(url);

    // Ensure protocol is http or https
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      throw new ConfigValidationError(
        `API URL must use http:// or https:// protocol, got: ${parsed.protocol}`
      );
    }

    // In production, enforce HTTPS
    if (import.meta.env.PROD && parsed.protocol !== 'https:') {
      console.warn(
        'WARNING: Using non-HTTPS API URL in production. This is insecure and should be fixed.'
      );
    }
  } catch (error) {
    if (error instanceof ConfigValidationError) {
      throw error;
    }
    throw new ConfigValidationError(`Invalid API URL format: ${url}`);
  }
}

/**
 * Load and validate application configuration
 *
 * This function is called once at application startup to load and validate
 * all configuration values. It will throw an error if required configuration
 * is missing or invalid, preventing the application from starting in an
 * invalid state.
 *
 * @returns Validated application configuration
 * @throws ConfigValidationError if configuration is invalid
 */
function loadConfig(): AppConfig {
  const environment = getEnvironment();
  const isProduction = environment === 'production';
  const isDevelopment = environment === 'development';
  const isTest = environment === 'test';

  // Load API configuration
  const apiBaseUrl = getEnv('API_URL', 'http://localhost:8000', true);
  validateApiUrl(apiBaseUrl);

  const config: AppConfig = {
    environment,
    isProduction,
    isDevelopment,
    isTest,

    api: {
      baseUrl: apiBaseUrl,
      timeout: getNumberEnv('API_TIMEOUT', 30000, 1000, 120000),
      enableLogging: getBooleanEnv('API_ENABLE_LOGGING', !isProduction),
    },

    app: {
      name: getEnv('APP_NAME', 'Frontend Application'),
      version: getEnv('APP_VERSION', '1.0.0'),
      title: getEnv('APP_TITLE', 'Frontend Application'),
      debug: getBooleanEnv('DEBUG', isDevelopment),
    },

    features: {
      enableAnalytics: getBooleanEnv('ENABLE_ANALYTICS', isProduction),
      enableErrorReporting: getBooleanEnv('ENABLE_ERROR_REPORTING', isProduction),
      enableServiceWorker: getBooleanEnv('ENABLE_SERVICE_WORKER', false),
    },

    security: {
      enableCSP: getBooleanEnv('SECURITY_ENABLE_CSP', isProduction),
      maxLoginAttempts: getNumberEnv('SECURITY_MAX_LOGIN_ATTEMPTS', 5, 1, 20),
    },
  };

  return config;
}

/**
 * Application Configuration Instance
 *
 * DEPRECATED: Use getRuntimeConfig() from './runtimeConfig' instead.
 *
 * This build-time configuration is kept for backward compatibility and testing,
 * but the runtime configuration system should be used in production.
 *
 * @example
 * ```typescript
 * import { getRuntimeConfig } from '@/config';
 *
 * // Access configuration values (after loadRuntimeConfig() has been called)
 * const config = getRuntimeConfig();
 * const apiUrl = config.api.baseUrl;
 * const isDebug = config.app.debug;
 * ```
 */
export const config = loadConfig();

// Export everything for testing
export { getEnv, getBooleanEnv, getNumberEnv, getEnvironment, validateApiUrl };

// Re-export runtime configuration functions for convenient access
export {
  loadRuntimeConfig,
  getRuntimeConfig,
  isConfigLoaded,
  resetRuntimeConfig,
} from './runtimeConfig';
