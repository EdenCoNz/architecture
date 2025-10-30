/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { readFileSync } from 'fs';
import { resolve } from 'path';

// Read version from package.json
const packageJson = JSON.parse(readFileSync(resolve(__dirname, 'package.json'), 'utf-8'));
const appVersion = packageJson.version;

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

  // Inject version from package.json into the app
  define: {
    __APP_VERSION__: JSON.stringify(appVersion),
  },

  // Development server configuration optimized for Docker
  server: {
    host: '0.0.0.0', // Required for Docker - allows external connections
    port: 5173,
    strictPort: true, // Fail if port is already in use

    // Hot Module Replacement (HMR) configuration for Docker
    hmr: {
      // Use host networking for WebSocket connections
      // This ensures HMR works correctly when accessing via localhost
      clientPort: 5173,
    },

    // Watch configuration for better file change detection
    watch: {
      // Enable polling for file systems that don't support native file watching
      // (common in Docker bind mounts, especially on Windows/Mac)
      usePolling: true,
      interval: 100, // Check for changes every 100ms
    },

    // CORS configuration for API requests during development
    cors: true,
  },

  // Build configuration
  build: {
    // Source maps for better debugging in production
    sourcemap: true,

    // Optimize chunk splitting for better caching
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
        },
      },
    },
  },

  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.ts',
    css: true,
    testTimeout: 15000, // 15 seconds - allows async operations and complex component testing
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'json-summary', 'html', 'lcov'],
      exclude: ['node_modules/', 'tests/', '**/*.config.{js,ts}', '**/dist/**', '**/*.d.ts'],
    },
    // Ensure test environment variables are loaded
    env: {
      VITE_API_URL: 'http://localhost:8000',
      VITE_APP_VERSION: `${appVersion}-test`, // Add test suffix to distinguish test runs
    },
  },
});
