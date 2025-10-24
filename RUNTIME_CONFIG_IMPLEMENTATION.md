# Runtime Configuration Implementation Guide

## Overview

The frontend and backend applications now support **runtime configuration**, allowing the same container image to be deployed across multiple environments (dev, staging, production) without rebuilding.

**Key Achievement**: TRUE deployment flexibility - **Build Once, Deploy Everywhere**

## Architecture

### Before (Build-time Configuration)
```
Build Time:  Frontend → [Embed API URL] → Docker Image → Different image per environment
Deploy Time: Use environment-specific image
```
**Problem**: Need separate images for dev/staging/prod

### After (Runtime Configuration)
```
Build Time:  Frontend → [Minimal defaults] → Single Docker Image
Deploy Time: Image → Fetch config from /api/v1/config/frontend/ → Start app
```
**Solution**: One image works everywhere

## Implementation Details

### Backend Changes

#### 1. Configuration API Endpoint
**File**: `backend/apps/api/config_views.py`

```python
@api_view(["GET"])
@permission_classes([AllowAny])  # Public endpoint
def frontend_config(request):
    """
    Returns runtime configuration for frontend based on environment variables.

    Response format:
    {
        "api": {
            "url": "https://api.example.com",
            "timeout": 30000,
            "enableLogging": false
        },
        "app": {
            "name": "Frontend Application",
            "title": "Frontend Application",
            "version": "1.0.0",
            "environment": "production"
        },
        "features": {
            "enableAnalytics": false,
            "enableDebugMode": false
        }
    }
    """
```

**URL**: `/api/v1/config/frontend/`
**Method**: `GET`
**Authentication**: None (public endpoint)

####  2. Environment Variables (Backend)

Configure these environment variables to control frontend behavior:

| Variable | Description | Default |
|----------|-------------|---------|
| `FRONTEND_API_URL` | Backend API base URL | `http://localhost:8000` |
| `FRONTEND_API_TIMEOUT` | API request timeout (ms) | `30000` |
| `FRONTEND_API_ENABLE_LOGGING` | Enable API logging | `false` |
| `FRONTEND_APP_NAME` | Application name | `Frontend Application` |
| `FRONTEND_APP_TITLE` | Application title | `Frontend Application` |
| `FRONTEND_APP_VERSION` | Application version | `1.0.0` |
| `FRONTEND_ENABLE_ANALYTICS` | Enable analytics | `false` |
| `FRONTEND_ENABLE_DEBUG` | Enable debug mode | `false` |

### Frontend Changes

#### 1. Runtime Config Loader
**File**: `frontend/src/config/runtimeConfig.ts`

```typescript
// Load config at app startup
const config = await loadRuntimeConfig();

// Access config anywhere
import { getRuntimeConfig } from '@/config';
const config = getRuntimeConfig();
console.log('API URL:', config.api.baseUrl);
```

**Features**:
- Fetches configuration from `/api/v1/config/frontend/` on startup
- Falls back to build-time defaults if API unavailable
- Caches configuration for performance
- Type-safe configuration access

#### 2. App Initialization
**File**: `frontend/src/main.tsx`

```typescript
// Load runtime config before rendering app
loadRuntimeConfig()
  .then((config) => {
    // Render app with loaded configuration
    createRoot(root).render(<App />);
  })
  .catch((error) => {
    // Show error state with retry button
  });
```

**User Experience**:
- Shows "Loading..." while fetching config
- Shows error screen with retry button if config fetch fails
- Logs configuration details to console

#### 3. Dockerfile Updates
**File**: `frontend/Dockerfile`

**Before**:
```dockerfile
ARG VITE_API_URL           # Required
ARG VITE_APP_NAME          # Required
ARG VITE_APP_VERSION       # Required
# ... 10+ more args
RUN if [ -z "$VITE_API_URL" ]; then exit 1; fi  # Validation
```

**After**:
```dockerfile
ARG VITE_API_URL=http://localhost:8000  # Minimal fallback only
ARG VITE_APP_NAME="Frontend Application"
ARG VITE_APP_VERSION=1.0.0
# Only 3 minimal defaults for local development
```

#### 4. CI/CD Workflow Updates
**File**: `.github/workflows/frontend-ci.yml`

**Removed**:
```yaml
build-args: |
  VITE_API_URL=https://api.example.com
  VITE_APP_NAME=Frontend Application
  VITE_APP_VERSION=${{ steps.meta.outputs.version }}
```

**Added**:
```yaml
# Runtime config: no build-args needed
# Configuration loaded at runtime from backend API
```

## Deployment Guide

### Development Environment

```bash
# Backend
docker run -d \
  -e FRONTEND_API_URL=http://localhost:8000 \
  -e FRONTEND_ENABLE_DEBUG=true \
  -e DJANGO_ENV=development \
  -p 8000:8000 \
  ghcr.io/<owner>/backend:latest

# Frontend
docker run -d \
  -p 80:80 \
  ghcr.io/<owner>/frontend:latest
```

### Staging Environment

```bash
# Backend
docker run -d \
  -e FRONTEND_API_URL=https://staging-api.example.com \
  -e FRONTEND_APP_NAME="My App (Staging)" \
  -e FRONTEND_ENABLE_ANALYTICS=false \
  -e DJANGO_ENV=staging \
  -p 8000:8000 \
  ghcr.io/<owner>/backend:latest

# Frontend  (same image as dev!)
docker run -d \
  -p 80:80 \
  ghcr.io/<owner>/frontend:latest
```

### Production Environment

```bash
# Backend
docker run -d \
  -e FRONTEND_API_URL=https://api.example.com \
  -e FRONTEND_APP_NAME="My App" \
  -e FRONTEND_ENABLE_ANALYTICS=true \
  -e DJANGO_ENV=production \
  -p 8000:8000 \
  ghcr.io/<owner>/backend:latest

# Frontend (same image as dev & staging!)
docker run -d \
  -p 80:80 \
  ghcr.io/<owner>/frontend:latest
```

## Testing

### 1. Test Configuration Endpoint

```bash
# Test backend endpoint
curl http://localhost:8000/api/v1/config/frontend/ | jq

# Expected response:
{
  "api": {
    "url": "http://localhost:8000",
    "timeout": 30000,
    "enableLogging": true
  },
  "app": {
    "name": "Frontend Application",
    "title": "Frontend Application",
    "version": "1.0.0",
    "environment": "development"
  },
  "features": {
    "enableAnalytics": false,
    "enableDebugMode": true
  }
}
```

### 2. Test Frontend Loading

1. Open browser to `http://localhost`
2. Open browser console (F12)
3. Look for log messages:
   ```
   [Config] Loading runtime configuration from backend...
   [Config] API URL: http://localhost:8000
   [Config] Successfully loaded runtime configuration from backend
   [Config] Environment: development
   [App] Configuration loaded, rendering application
   [App] Environment: development
   ```

### 3. Test Fallback Mechanism

1. Stop backend container
2. Reload frontend
3. Should see fallback config being used:
   ```
   [Config] Loading runtime configuration from backend...
   [Config] Failed to load runtime configuration from backend: TypeError: Failed to fetch
   [Config] Using fallback configuration from build-time environment variables
   [Config] Fallback configuration loaded
   ```

## Migration from Build-time to Runtime Config

If you have existing code using the old `config` object:

### Before
```typescript
import { config } from '@/config';
const apiUrl = config.api.baseUrl;  // Works immediately
```

### After
```typescript
import { getRuntimeConfig } from '@/config';
const config = getRuntimeConfig();  // Must be called after loadRuntimeConfig()
const apiUrl = config.api.baseUrl;
```

**Note**: The old `config` export still works for backward compatibility, but uses build-time values.

## Benefits

### 1. Deployment Flexibility
- ✅ Build once, deploy to dev/staging/prod without rebuilding
- ✅ No separate images per environment
- ✅ Faster deployments (no rebuild required)

### 2. Configuration Management
- ✅ Centralized configuration in backend
- ✅ Environment-specific settings via env vars
- ✅ No secrets embedded in frontend code

### 3. Developer Experience
- ✅ Test configuration changes without rebuilding
- ✅ Clearer separation of concerns
- ✅ Better debugging (config logged to console)

### 4. CI/CD Efficiency
- ✅ Faster builds (no build args to inject)
- ✅ Simpler workflows
- ✅ Better cache utilization

## Troubleshooting

### Frontend shows "Failed to Initialize"

**Cause**: Backend API not accessible or not returning config

**Solution**:
1. Check backend is running: `curl http://localhost:8000/api/v1/health/`
2. Check config endpoint: `curl http://localhost:8000/api/v1/config/frontend/`
3. Check CORS settings if frontend and backend on different domains
4. Check browser console for detailed error

### Configuration not updating after environment variable change

**Cause**: Configuration is cached in browser

**Solution**:
1. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
2. Clear browser cache
3. Restart frontend container

### Frontend using fallback configuration

**Cause**: Cannot reach backend config endpoint

**Solution**:
1. Check `VITE_API_URL` matches your backend URL
2. Verify backend config endpoint is accessible
3. Check network connectivity
4. Review browser console logs

## Files Changed

### Backend
- ✅ `backend/apps/api/config_views.py` - New configuration endpoint
- ✅ `backend/apps/api/urls.py` - Added route for config endpoint

### Frontend
- ✅ `frontend/src/config/runtimeConfig.ts` - New runtime config loader
- ✅ `frontend/src/config/index.ts` - Re-export runtime functions
- ✅ `frontend/src/main.tsx` - Load config at app startup
- ✅ `frontend/Dockerfile` - Removed build-time args
- ✅ `.github/workflows/frontend-ci.yml` - Removed build args from CI/CD

## Next Steps

1. **Test the implementation** in local development
2. **Deploy to staging** and verify configuration loads correctly
3. **Test environment variable changes** work without rebuilding
4. **Document environment-specific settings** for your team
5. **Update deployment documentation** with new environment variables

## Support

For issues or questions:
1. Check browser console for config loading logs
2. Verify backend `/api/v1/config/frontend/` endpoint is accessible
3. Review this guide's troubleshooting section
4. Check environment variables are set correctly
