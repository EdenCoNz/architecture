/**
 * Runtime Configuration Loader
 *
 * This module provides runtime configuration loading from the backend API,
 * allowing the same frontend image to be deployed across different environments
 * without rebuilding.
 *
 * Configuration loading strategy:
 * 1. Attempt to fetch configuration from backend API endpoint
 * 2. Fall back to build-time environment variables if fetch fails
 * 3. Cache the loaded configuration for subsequent access
 */

import type { AppConfig, Environment } from './index';

/**
 * Backend API Configuration Response
 */
interface BackendConfigResponse {
  api: {
    url: string;
    timeout: number;
    enableLogging: boolean;
  };
  app: {
    name: string;
    title: string;
    version: string;
    environment: string;
  };
  features: {
    enableAnalytics: boolean;
    enableDebugMode: boolean;
  };
}

/**
 * Runtime configuration state
 */
let runtimeConfig: AppConfig | null = null;
let configPromise: Promise<AppConfig> | null = null;

/**
 * Fetch configuration from backend API
 *
 * @param apiUrl - Base URL of the backend API
 * @param timeout - Request timeout in milliseconds
 * @returns Backend configuration response
 * @throws Error if fetch fails
 */
async function fetchConfigFromBackend(
  apiUrl: string,
  timeout = 5000
): Promise<BackendConfigResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(`${apiUrl}/api/v1/config/frontend/`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
}

/**
 * Get fallback configuration from build-time environment variables
 *
 * This is used when the backend API is not available or returns an error.
 *
 * @returns Fallback configuration
 */
function getFallbackConfig(): AppConfig {
  // Get environment
  const mode = import.meta.env.MODE;
  const environment: Environment =
    mode === 'production' ? 'production' : mode === 'test' ? 'test' : 'development';
  const isProduction = environment === 'production';
  const isDevelopment = environment === 'development';
  const isTest = environment === 'test';

  return {
    environment,
    isProduction,
    isDevelopment,
    isTest,

    api: {
      baseUrl: (import.meta.env.VITE_API_URL as string) || 'http://localhost:8000',
      timeout: Number(import.meta.env.VITE_API_TIMEOUT) || 30000,
      enableLogging:
        (import.meta.env.VITE_API_ENABLE_LOGGING as string) === 'true' || !isProduction,
    },

    app: {
      name: (import.meta.env.VITE_APP_NAME as string) || 'Frontend Application',
      version: (import.meta.env.VITE_APP_VERSION as string) || '1.0.0',
      title: (import.meta.env.VITE_APP_TITLE as string) || 'Frontend Application',
      debug: (import.meta.env.VITE_DEBUG as string) === 'true' || isDevelopment,
    },

    features: {
      enableAnalytics: (import.meta.env.VITE_ENABLE_ANALYTICS as string) === 'true' || isProduction,
      enableErrorReporting:
        (import.meta.env.VITE_ENABLE_ERROR_REPORTING as string) === 'true' || isProduction,
      enableServiceWorker:
        (import.meta.env.VITE_ENABLE_SERVICE_WORKER as string) === 'true' || false,
    },

    security: {
      enableCSP: (import.meta.env.VITE_SECURITY_ENABLE_CSP as string) === 'true' || isProduction,
      maxLoginAttempts: Number(import.meta.env.VITE_SECURITY_MAX_LOGIN_ATTEMPTS) || 5,
    },
  };
}

/**
 * Transform backend configuration response to AppConfig format
 *
 * @param backendConfig - Configuration from backend API
 * @returns Transformed AppConfig
 */
function transformBackendConfig(backendConfig: BackendConfigResponse): AppConfig {
  const environment = (backendConfig.app.environment as Environment) || 'production';
  const isProduction = environment === 'production';
  const isDevelopment = environment === 'development';
  const isTest = environment === 'test';

  return {
    environment,
    isProduction,
    isDevelopment,
    isTest,

    api: {
      baseUrl: backendConfig.api.url,
      timeout: backendConfig.api.timeout,
      enableLogging: backendConfig.api.enableLogging,
    },

    app: {
      name: backendConfig.app.name,
      version: backendConfig.app.version,
      title: backendConfig.app.title,
      debug: backendConfig.features.enableDebugMode,
    },

    features: {
      enableAnalytics: backendConfig.features.enableAnalytics,
      enableErrorReporting: isProduction,
      enableServiceWorker: false,
    },

    security: {
      enableCSP: isProduction,
      maxLoginAttempts: 5,
    },
  };
}

/**
 * Load runtime configuration
 *
 * Attempts to fetch configuration from the backend API. If the fetch fails
 * (e.g., network error, API not available), falls back to build-time
 * environment variables.
 *
 * This function is idempotent - subsequent calls return the same promise
 * and cached configuration.
 *
 * @returns Promise resolving to application configuration
 *
 * @example
 * ```typescript
 * // Load config at app startup
 * const config = await loadRuntimeConfig();
 * console.log('API URL:', config.api.baseUrl);
 * ```
 */
export async function loadRuntimeConfig(): Promise<AppConfig> {
  // Return cached config if available
  if (runtimeConfig) {
    return runtimeConfig;
  }

  // Return existing promise if load is in progress
  if (configPromise) {
    return configPromise;
  }

  // Start loading configuration
  configPromise = (async () => {
    try {
      // First, get fallback config to know the API URL
      const fallback = getFallbackConfig();

      // Try to fetch from backend
      const backendConfig = await fetchConfigFromBackend(fallback.api.baseUrl);

      // Transform and cache the configuration
      runtimeConfig = transformBackendConfig(backendConfig);

      return runtimeConfig;
    } catch (error) {
      console.warn('[Config] Failed to load runtime configuration from backend:', error);

      // Use fallback configuration
      runtimeConfig = getFallbackConfig();

      return runtimeConfig;
    }
  })();

  return configPromise;
}

/**
 * Get current runtime configuration (synchronous)
 *
 * Returns the cached runtime configuration. Throws an error if configuration
 * has not been loaded yet. Use loadRuntimeConfig() first to load configuration.
 *
 * @returns Current application configuration
 * @throws Error if configuration has not been loaded
 *
 * @example
 * ```typescript
 * // After loadRuntimeConfig() has been called
 * const config = getRuntimeConfig();
 * console.log('API URL:', config.api.baseUrl);
 * ```
 */
export function getRuntimeConfig(): AppConfig {
  if (!runtimeConfig) {
    throw new Error(
      'Runtime configuration not loaded. ' +
        'Call loadRuntimeConfig() and await its completion before accessing configuration.'
    );
  }
  return runtimeConfig;
}

/**
 * Check if runtime configuration has been loaded
 *
 * @returns true if configuration is loaded, false otherwise
 */
export function isConfigLoaded(): boolean {
  return runtimeConfig !== null;
}

/**
 * Reset runtime configuration (for testing)
 *
 * Clears the cached configuration and loading promise, forcing a fresh
 * load on the next call to loadRuntimeConfig().
 */
export function resetRuntimeConfig(): void {
  runtimeConfig = null;
  configPromise = null;
}
