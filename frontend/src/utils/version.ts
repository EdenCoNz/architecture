/**
 * Frontend Version Information Utility
 *
 * Provides runtime access to the frontend application version for support engineers,
 * administrators, and monitoring tools.
 *
 * This module exposes version information through multiple channels:
 * - Console logging for troubleshooting
 * - Window object for browser dev tools access
 * - Programmatic API for components
 *
 * The version is automatically sourced from package.json at build time via Vite,
 * ensuring it stays in sync with the version defined in Story 16.1.
 *
 * Feature #16 Story 16.6: Expose Frontend Version at Runtime
 */

/**
 * Application version information
 */
export interface VersionInfo {
  /** Application version (semantic versioning format: MAJOR.MINOR.PATCH) */
  version: string;

  /** Application name */
  name: string;

  /** Build timestamp (if available) */
  buildDate?: string;

  /** Environment (development, staging, production) */
  environment?: string;
}

/**
 * Global type declarations
 */
declare global {
  /**
   * Window interface extension for version information
   *
   * This allows TypeScript to recognize version properties on the window object
   */
  interface Window {
    /** Application version information object */
    __APP_INFO__?: VersionInfo;

    /** Quick access to version string */
    APP_VERSION?: string;
  }

  /**
   * Version injected by Vite at build time from package.json
   */
  const __APP_VERSION__: string;
}

/**
 * Get application version from package.json
 *
 * The version is injected at build time by Vite, which automatically
 * exposes package.json fields. This ensures the version stays in sync
 * with the source of truth (package.json) from Story 16.1.
 *
 * @returns Application version string (e.g., "1.0.0")
 *
 * @example
 * ```typescript
 * const version = getVersion();
 * console.log('Current version:', version); // "1.0.0"
 * ```
 */
export function getVersion(): string {
  // Priority order for version resolution:
  // 1. VITE_APP_VERSION environment variable (allows runtime override)
  // 2. __APP_VERSION__ injected by Vite define plugin from package.json
  // 3. Fallback to 1.0.0 (should never be reached in normal operation)

  // Try VITE_APP_VERSION first (from environment variables)
  const envVersion = import.meta.env.VITE_APP_VERSION as string | undefined;
  if (envVersion) {
    return envVersion;
  }

  // Use version injected by Vite from package.json (configured in vite.config.ts)
  // This is the primary method - version is baked into the build at compile time
  // eslint-disable-next-line no-restricted-globals
  if (typeof __APP_VERSION__ !== 'undefined') {
    return __APP_VERSION__;
  }

  // Ultimate fallback - this should match package.json
  // This fallback ensures the code doesn't break if the define plugin fails
  return '1.0.0';
}

/**
 * Get comprehensive application information
 *
 * Returns detailed version information including version number,
 * application name, build date, and environment.
 *
 * @param environment - Optional environment override
 * @returns Complete version information object
 *
 * @example
 * ```typescript
 * const info = getVersionInfo('production');
 * console.log(info.version);     // "1.0.0"
 * console.log(info.name);        // "Frontend Application"
 * console.log(info.environment); // "production"
 * ```
 */
export function getVersionInfo(environment?: string): VersionInfo {
  return {
    version: getVersion(),
    name: (import.meta.env.VITE_APP_NAME as string) || 'Frontend Application',
    buildDate: (import.meta.env.VITE_BUILD_DATE as string) || undefined,
    environment: environment || (import.meta.env.MODE as string) || 'development',
  };
}

/**
 * Log version information to console
 *
 * Logs application version info in a formatted, easily readable way.
 * This is useful for troubleshooting and verifying deployments.
 *
 * Support engineers can:
 * 1. Open browser dev tools (F12)
 * 2. Check console output
 * 3. See version information immediately
 *
 * @param environment - Optional environment override for display
 *
 * @example
 * ```typescript
 * // At application startup
 * logVersionInfo('production');
 * // Console output:
 * // Frontend Application v1.0.0
 * // Environment: production
 * ```
 */
export function logVersionInfo(environment?: string): void {
  const info = getVersionInfo(environment);

  // Create a visually distinct log group for easy identification
  console.log(
    `%c🚀 ${info.name} v${info.version}`,
    'color: #1976d2; font-weight: bold; font-size: 14px;'
  );

  console.log(`%cEnvironment: ${info.environment}`, 'color: #666; font-size: 12px;');

  if (info.buildDate) {
    console.log(`%cBuild Date: ${info.buildDate}`, 'color: #666; font-size: 12px;');
  }

  // Add helpful message for support engineers
  console.log(
    '%cℹ️ Access version programmatically: window.__APP_INFO__ or window.APP_VERSION',
    'color: #888; font-style: italic; font-size: 11px;'
  );
}

/**
 * Expose version information to window object
 *
 * Makes version information accessible via browser dev tools for
 * support engineers and administrators who need to verify deployed versions.
 *
 * Usage in browser dev tools console:
 * - Quick access: `window.APP_VERSION` or just `APP_VERSION`
 * - Full info: `window.__APP_INFO__`
 *
 * @param environment - Optional environment override
 *
 * @example
 * ```typescript
 * // At application startup
 * exposeVersionToWindow('production');
 *
 * // In browser dev tools console:
 * APP_VERSION              // "1.0.0"
 * __APP_INFO__             // { version: "1.0.0", name: "...", ... }
 * __APP_INFO__.version     // "1.0.0"
 * ```
 */
export function exposeVersionToWindow(environment?: string): void {
  const info = getVersionInfo(environment);

  // Check if properties already exist and remove them for re-configuration
  // This allows the function to be idempotent (can be called multiple times)
  if ('__APP_INFO__' in window) {
    delete (window as { __APP_INFO__?: unknown }).__APP_INFO__;
  }
  if ('APP_VERSION' in window) {
    delete (window as { APP_VERSION?: unknown }).APP_VERSION;
  }

  // Define properties with proper descriptors
  // configurable: true allows the property to be deleted and re-defined
  // writable: false prevents accidental modification
  Object.defineProperty(window, '__APP_INFO__', {
    value: info,
    writable: false,
    configurable: true,
    enumerable: true,
  });

  Object.defineProperty(window, 'APP_VERSION', {
    value: info.version,
    writable: false,
    configurable: true,
    enumerable: true,
  });
}

/**
 * Initialize version information at application startup
 *
 * This is a convenience function that combines logging and window exposure.
 * Call this once at application startup to make version information
 * available through all channels.
 *
 * @param environment - Optional environment override
 *
 * @example
 * ```typescript
 * // In main.tsx, before rendering the app
 * import { initializeVersionInfo } from './utils/version';
 *
 * initializeVersionInfo('production');
 *
 * // Now version is available in:
 * // - Browser console (logged)
 * // - Dev tools (window.APP_VERSION)
 * // - Programmatically (getVersion())
 * ```
 */
export function initializeVersionInfo(environment?: string): void {
  logVersionInfo(environment);
  exposeVersionToWindow(environment);
}
