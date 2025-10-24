# Frontend Application Configuration Guide

## Overview

The frontend application uses a centralized, type-safe configuration system that supports multiple environments (local, staging, production) and provides secure access to configuration values without exposing sensitive data.

**Key Features:**
- Environment-specific configuration files
- Type-safe configuration access with TypeScript
- Validation of required configuration at startup
- Secure handling of environment variables
- Support for local, staging, and production environments
- Docker-friendly configuration management

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration Files](#configuration-files)
3. [Available Configuration Options](#available-configuration-options)
4. [Environment Setup](#environment-setup)
5. [Docker Configuration](#docker-configuration)
6. [Production Deployment](#production-deployment)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Local Development Setup

1. **Copy the example environment file:**
   ```bash
   cp .env.local.example .env.local
   ```

2. **Update the configuration:**
   Edit `.env.local` and set your values (especially `VITE_API_URL`):
   ```bash
   VITE_API_URL=http://localhost:8000
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

The application will automatically load `.env.local` and validate the configuration.

### Verify Configuration

When the application starts, you'll see a configuration summary in the browser console:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Application Configuration Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Environment:           development
Application Name:      Frontend Application (Local)
API Base URL:          http://localhost:8000
Debug Mode:            true
...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Configuration Files

### File Priority (Vite Loading Order)

Vite loads environment files in the following order (later files override earlier ones):

1. `.env` - Base configuration for all environments
2. `.env.local` - Local overrides (not committed to git)
3. `.env.[mode]` - Mode-specific configuration (e.g., `.env.production`)
4. `.env.[mode].local` - Mode-specific local overrides (not committed to git)

### File Descriptions

| File | Purpose | Committed to Git | Used In |
|------|---------|------------------|---------|
| `.env.example` | Template with all available options | ✅ Yes | Documentation |
| `.env.local.example` | Local development template | ✅ Yes | Documentation |
| `.env.staging.example` | Staging environment template | ✅ Yes | Documentation |
| `.env.production.example` | Production environment template | ✅ Yes | Documentation |
| `.env.local` | Your local development config | ❌ No | Local development |
| `.env.staging` | Staging environment config | ❌ No | Staging builds |
| `.env.production` | Production environment config | ❌ No | Production builds |
| `.env.docker` | Docker development config | ✅ Yes | Docker development |

### Security Notes

**IMPORTANT:**
- Files ending in `.local`, `.staging`, or `.production` are automatically ignored by git
- Never commit actual environment values to version control
- All frontend environment variables must be prefixed with `VITE_`
- Frontend env variables are embedded in the build and **visible in client-side code**
- Never store sensitive secrets (API keys, passwords) in frontend environment variables
- Use backend API endpoints to securely access sensitive data

---

## Available Configuration Options

### Required Configuration

#### `VITE_API_URL` (REQUIRED)
- **Description:** Base URL for the backend API
- **Format:** Valid HTTP/HTTPS URL
- **Examples:**
  - Development: `http://localhost:8000`
  - Staging: `https://api-staging.example.com`
  - Production: `https://api.example.com`
- **Validation:** Must be a valid URL; HTTPS enforced in production builds

### API Configuration

#### `VITE_API_TIMEOUT`
- **Description:** API request timeout in milliseconds
- **Default:** `30000` (30 seconds)
- **Valid Range:** 1000-120000 (1 second to 2 minutes)
- **Example:** `VITE_API_TIMEOUT=45000`

#### `VITE_API_ENABLE_LOGGING`
- **Description:** Enable detailed logging of API requests/responses
- **Default:** `true` in development, `false` in production
- **Values:** `true` or `false`
- **Example:** `VITE_API_ENABLE_LOGGING=true`

### Application Settings

#### `VITE_APP_NAME`
- **Description:** Application name used in UI and logging
- **Default:** `Frontend Application`
- **Example:** `VITE_APP_NAME=My Awesome App`

#### `VITE_APP_VERSION`
- **Description:** Application version (typically set by CI/CD)
- **Default:** `1.0.0`
- **Example:** `VITE_APP_VERSION=2.1.3`

#### `VITE_APP_TITLE`
- **Description:** Browser tab title
- **Default:** `Frontend Application`
- **Example:** `VITE_APP_TITLE=My App - Dashboard`

#### `VITE_DEBUG`
- **Description:** Enable debug mode features
- **Default:** `true` in development, `false` in production
- **Values:** `true` or `false`
- **Example:** `VITE_DEBUG=false`

### Feature Flags

#### `VITE_ENABLE_ANALYTICS`
- **Description:** Enable analytics tracking
- **Default:** `false` in development, `true` in production
- **Values:** `true` or `false`
- **Example:** `VITE_ENABLE_ANALYTICS=true`
- **Note:** Keep false in development to avoid polluting analytics data

#### `VITE_ENABLE_ERROR_REPORTING`
- **Description:** Enable error reporting service (Sentry, etc.)
- **Default:** `false` in development, `true` in production
- **Values:** `true` or `false`
- **Example:** `VITE_ENABLE_ERROR_REPORTING=true`

#### `VITE_ENABLE_SERVICE_WORKER`
- **Description:** Enable service worker for offline support
- **Default:** `false`
- **Values:** `true` or `false`
- **Example:** `VITE_ENABLE_SERVICE_WORKER=true`
- **Note:** Only enable if you have implemented a service worker

### Security Settings

#### `VITE_SECURITY_ENABLE_CSP`
- **Description:** Enable Content Security Policy headers
- **Default:** `false` in development, `true` in production
- **Values:** `true` or `false`
- **Example:** `VITE_SECURITY_ENABLE_CSP=true`

#### `VITE_SECURITY_MAX_LOGIN_ATTEMPTS`
- **Description:** Maximum login attempts before lockout
- **Default:** `5`
- **Valid Range:** 1-20
- **Example:** `VITE_SECURITY_MAX_LOGIN_ATTEMPTS=3`

---

## Environment Setup

### Local Development

1. **Create your local environment file:**
   ```bash
   cp .env.local.example .env.local
   ```

2. **Edit `.env.local` with your settings:**
   ```bash
   # Essential settings
   VITE_API_URL=http://localhost:8000

   # Optional: Customize app settings
   VITE_APP_NAME=Frontend Application (Local)
   VITE_DEBUG=true
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

### Staging Environment

1. **Create staging environment file:**
   ```bash
   cp .env.staging.example .env.staging
   ```

2. **Update staging values:**
   ```bash
   VITE_API_URL=https://api-staging.example.com
   VITE_ENABLE_ANALYTICS=true
   VITE_ENABLE_ERROR_REPORTING=true
   ```

3. **Build for staging:**
   ```bash
   npm run build -- --mode staging
   ```

### Production Environment

1. **Create production environment file:**
   ```bash
   cp .env.production.example .env.production
   ```

2. **Update production values:**
   ```bash
   VITE_API_URL=https://api.example.com
   VITE_DEBUG=false
   VITE_ENABLE_ANALYTICS=true
   VITE_ENABLE_ERROR_REPORTING=true
   VITE_SECURITY_ENABLE_CSP=true
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

---

## Docker Configuration

### Development with Docker

The Docker development environment uses `.env.docker` for configuration.

1. **Review Docker configuration:**
   ```bash
   cat .env.docker
   ```

2. **Start Docker development environment:**
   ```bash
   docker compose up
   ```

3. **Override Docker settings (optional):**
   Create `.env.local` to override Docker defaults:
   ```bash
   VITE_API_URL=http://custom-backend:8000
   ```

### Production Docker Build

Production Docker builds use build arguments to inject configuration:

1. **Set environment variables:**
   ```bash
   export VITE_API_URL=https://api.example.com
   export VITE_APP_VERSION=1.2.3
   ```

2. **Build production image:**
   ```bash
   docker compose -f docker-compose.prod.yml build
   ```

3. **Or pass build arguments directly:**
   ```bash
   docker build \
     --target production \
     --build-arg VITE_API_URL=https://api.example.com \
     --build-arg VITE_APP_VERSION=1.2.3 \
     -t frontend:prod .
   ```

---

## Production Deployment

### CI/CD Pipeline Configuration

In CI/CD pipelines, set environment variables as secrets or environment-specific variables:

**GitHub Actions Example:**
```yaml
- name: Build production image
  uses: docker/build-push-action@v5
  with:
    context: ./frontend
    target: production
    build-args: |
      VITE_API_URL=${{ secrets.PRODUCTION_API_URL }}
      VITE_APP_VERSION=${{ github.ref_name }}
      VITE_ENABLE_ANALYTICS=true
      VITE_ENABLE_ERROR_REPORTING=true
    push: true
    tags: myregistry/frontend:${{ github.sha }}
```

### Environment Variable Sources

**Recommended approach for production:**

1. **Store in CI/CD secrets management:**
   - GitHub Actions Secrets
   - GitLab CI/CD Variables
   - AWS Secrets Manager
   - Azure Key Vault

2. **Load from environment file in CI/CD:**
   ```bash
   # In CI/CD script
   export $(cat .env.production | xargs)
   docker compose -f docker-compose.prod.yml build
   ```

3. **Pass as build arguments:**
   ```bash
   docker build --build-arg VITE_API_URL=$API_URL ...
   ```

---

## Best Practices

### Security

1. **Never commit sensitive values**
   - Use `.env.local`, `.env.staging`, `.env.production` (all git-ignored)
   - Store production secrets in CI/CD secrets management
   - Never hardcode values in source code

2. **Frontend vs Backend secrets**
   - Frontend env variables are visible in client code
   - Store API keys, credentials in backend
   - Frontend only stores public configuration

3. **Use HTTPS in production**
   - Always use `https://` URLs for production API endpoints
   - Configuration validation warns if using HTTP in production

### Configuration Management

1. **Use environment-specific files**
   - `.env.local` for local development
   - `.env.staging` for staging builds
   - `.env.production` for production builds

2. **Document all variables**
   - Keep `.env.example` updated with all available options
   - Add comments explaining each variable's purpose
   - Document valid values and ranges

3. **Validate configuration**
   - The app validates configuration at startup
   - Missing required variables throw errors
   - Invalid values are caught before runtime

### Development Workflow

1. **Start with examples**
   - Copy `.env.local.example` to `.env.local`
   - Update values for your environment
   - Never commit `.env.local`

2. **Team consistency**
   - Keep example files updated
   - Document any new configuration in this guide
   - Share configuration changes in pull requests

3. **Test configuration changes**
   - Verify configuration loads correctly
   - Check browser console for configuration summary
   - Test in Docker to ensure consistency

---

## Troubleshooting

### Configuration Validation Errors

**Error: "Missing required environment variable: VITE_API_URL"**
- **Cause:** Required API URL not set
- **Solution:** Add `VITE_API_URL=http://localhost:8000` to `.env.local`

**Error: "Invalid API URL format"**
- **Cause:** API URL is not a valid URL
- **Solution:** Ensure URL includes protocol: `http://` or `https://`

**Error: "VITE_API_TIMEOUT must be a valid number"**
- **Cause:** Timeout value is not a number
- **Solution:** Use numeric value: `VITE_API_TIMEOUT=30000`

### Environment Variables Not Loading

**Problem:** Changes to `.env` files not reflected in app

**Solutions:**
1. **Restart dev server:** Environment variables are loaded at startup
   ```bash
   # Stop server (Ctrl+C)
   npm run dev
   ```

2. **Clear Vite cache:**
   ```bash
   rm -rf node_modules/.vite
   npm run dev
   ```

3. **Check file naming:** Must be exactly `.env.local` (not `.env.development`)

4. **Verify VITE_ prefix:** All variables must start with `VITE_`

### Docker Configuration Issues

**Problem:** Docker container using wrong API URL

**Solutions:**
1. **Check `.env.docker` file exists and has correct values**

2. **Verify docker-compose.yml loads env_file:**
   ```yaml
   env_file:
     - .env.docker
   ```

3. **Override with `.env.local` for custom values**

4. **Rebuild container after changes:**
   ```bash
   docker compose down
   docker compose up --build
   ```

### Production Build Issues

**Problem:** Production build missing configuration

**Solutions:**
1. **Pass build arguments explicitly:**
   ```bash
   docker build --build-arg VITE_API_URL=https://api.example.com ...
   ```

2. **Check environment variables are exported:**
   ```bash
   export VITE_API_URL=https://api.example.com
   echo $VITE_API_URL  # Should print the URL
   ```

3. **Verify docker-compose.prod.yml has correct args:**
   ```yaml
   args:
     VITE_API_URL: ${VITE_API_URL}
   ```

---

## Code Usage Examples

### Accessing Configuration in Code

```typescript
import { config } from '@/config';

// Access API configuration
const apiUrl = config.api.baseUrl;
const timeout = config.api.timeout;

// Check environment
if (config.isDevelopment) {
  console.log('Running in development mode');
}

// Feature flags
if (config.features.enableAnalytics) {
  // Initialize analytics
}

// Security settings
const maxAttempts = config.security.maxLoginAttempts;
```

### Type-Safe Configuration

```typescript
import { AppConfig, config } from '@/config';

// TypeScript provides autocomplete and type checking
const apiConfig: AppConfig['api'] = config.api;

// Access with full type safety
const baseUrl: string = config.api.baseUrl;
const isProduction: boolean = config.isProduction;
```

### Print Configuration Summary

```typescript
import { printConfigSummary } from '@/config';

// In development, print configuration for debugging
if (import.meta.env.DEV) {
  printConfigSummary();
}
```

---

## Additional Resources

- [Vite Environment Variables Documentation](https://vitejs.dev/guide/env-and-mode.html)
- [Docker Build Arguments](https://docs.docker.com/engine/reference/builder/#arg)
- [Docker Compose Build Args](https://docs.docker.com/compose/compose-file/build/#args)
- Project Backend Configuration: `backend/.env.example`

---

## Support

For configuration issues or questions:
1. Check this documentation
2. Review `.env.example` for all available options
3. Check browser console for configuration validation errors
4. Review Docker logs: `docker compose logs frontend`
