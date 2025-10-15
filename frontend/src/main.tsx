/**
 * Application Entry Point
 *
 * Bootstraps the React application with proper providers and strict mode.
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

const root = document.getElementById('root');

if (!root) {
  throw new Error('Root element not found. Ensure index.html contains <div id="root"></div>');
}

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>
);
