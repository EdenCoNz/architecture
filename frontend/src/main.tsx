/**
 * Application Entry Point
 *
 * Bootstraps the React application with proper providers and strict mode.
 * Loads runtime configuration from the backend before rendering the app.
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import { loadRuntimeConfig } from './config/runtimeConfig';

const root = document.getElementById('root');

if (!root) {
  throw new Error('Root element not found. Ensure index.html contains <div id="root"></div>');
}

// Show loading state while config is being fetched
root.innerHTML = `
  <div style="display: flex; align-items: center; justify-content: center; height: 100vh; font-family: system-ui, -apple-system, sans-serif;">
    <div style="text-align: center;">
      <div style="font-size: 24px; margin-bottom: 16px;">Loading...</div>
      <div style="color: #666;">Initializing application configuration</div>
    </div>
  </div>
`;

// Load runtime configuration and then render app
loadRuntimeConfig()
  .then((config) => {
    console.log('[App] Configuration loaded, rendering application');
    console.log('[App] Environment:', config.environment);

    // Render the application
    createRoot(root).render(
      <StrictMode>
        <App />
      </StrictMode>
    );
  })
  .catch((error) => {
    console.error('[App] Failed to initialize application:', error);

    // Show error state
    root.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: center; height: 100vh; font-family: system-ui, -apple-system, sans-serif;">
        <div style="text-align: center; max-width: 600px; padding: 32px;">
          <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
          <div style="font-size: 24px; margin-bottom: 16px; color: #d32f2f;">Failed to Initialize</div>
          <div style="color: #666; margin-bottom: 24px;">
            The application failed to load its configuration. Please check your network connection and try again.
          </div>
          <div style="background: #f5f5f5; padding: 16px; border-radius: 8px; text-align: left; font-family: monospace; font-size: 14px;">
            ${error instanceof Error ? error.message : String(error)}
          </div>
          <button
            onclick="window.location.reload()"
            style="margin-top: 24px; padding: 12px 24px; background: #1976d2; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer;"
          >
            Retry
          </button>
        </div>
      </div>
    `;
  });
