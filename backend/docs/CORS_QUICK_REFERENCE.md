# CORS Quick Reference

## TL;DR

✅ **CORS is already configured and tested**
- Development: Allows all origins
- Production: Configurable via `CORS_ALLOWED_ORIGINS` environment variable
- All 17 CORS tests passing

## Quick Commands

```bash
# Run CORS tests
cd backend
poetry run pytest tests/integration/test_cors_configuration.py -v

# Start development server (CORS enabled)
make dev

# Check CORS configuration
poetry run python manage.py shell
>>> from django.conf import settings
>>> print(settings.CORS_ALLOWED_ORIGINS)
>>> print(settings.CORS_ALLOW_CREDENTIALS)
```

## Environment Variables

### Development
```bash
DJANGO_SETTINGS_MODULE=backend.settings.development
# CORS_ALLOWED_ORIGINS not needed - allows all origins
```

### Production
```bash
DJANGO_SETTINGS_MODULE=backend.settings.production
CORS_ALLOWED_ORIGINS=https://app.example.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Default Allowed Origins

- `http://localhost:5173` (Vite dev server)
- `http://127.0.0.1:5173` (Vite dev server)

## Testing CORS from Browser

```javascript
// Run this from frontend (http://localhost:5173)
fetch('http://localhost:8000/health/')
  .then(r => r.json())
  .then(data => console.log('✅ CORS working:', data))
  .catch(err => console.error('❌ CORS error:', err));
```

## Key Settings

| Setting | Development | Production |
|---------|-------------|------------|
| `CORS_ALLOW_ALL_ORIGINS` | `True` | `False` |
| `CORS_ALLOWED_ORIGINS` | N/A | From env var |
| `CORS_ALLOW_CREDENTIALS` | `True` | `True` |
| `SESSION_COOKIE_SECURE` | `False` | `True` |
| `CSRF_COOKIE_SECURE` | `False` | `True` |

## Troubleshooting

### CORS error in browser?

1. Check origin in error message
2. Add to `CORS_ALLOWED_ORIGINS` environment variable
3. Restart backend server

### Credentials not working?

1. Verify `CORS_ALLOW_CREDENTIALS = True`
2. Ensure origin is explicitly allowed (not `*`)
3. Frontend must send `credentials: 'include'`

## File Locations

- Configuration: `backend/src/backend/settings/base.py`
- Tests: `backend/tests/integration/test_cors_configuration.py`
- Full docs: `backend/docs/CORS_CONFIGURATION.md`
- Summary: `backend/docs/STORY_4_IMPLEMENTATION_SUMMARY.md`

## Response Headers

When CORS is working, you'll see these headers:

```
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: content-type, authorization
```

## Security Checklist (Production)

- [ ] Use HTTPS only
- [ ] Set specific `CORS_ALLOWED_ORIGINS` (no wildcards)
- [ ] Enable `SESSION_COOKIE_SECURE=True`
- [ ] Enable `CSRF_COOKIE_SECURE=True`
- [ ] Enable `SECURE_SSL_REDIRECT=True`
- [ ] Set `SECURE_HSTS_SECONDS=31536000`

## For More Information

See `backend/docs/CORS_CONFIGURATION.md` for complete documentation.
