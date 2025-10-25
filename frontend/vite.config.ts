/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

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
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'json-summary', 'html', 'lcov'],
      exclude: ['node_modules/', 'tests/', '**/*.config.{js,ts}', '**/dist/**', '**/*.d.ts'],
    },
    // Ensure test environment variables are loaded
    env: {
      VITE_API_URL: 'http://localhost:8000',
    },
  },
});
