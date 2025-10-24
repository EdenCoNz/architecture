# Frontend Configuration Quick Start

## 🚀 5-Minute Setup

### Local Development

```bash
# 1. Copy the local environment template
cp .env.local.example .env.local

# 2. Update VITE_API_URL in .env.local (if needed)
# Default: http://localhost:8000

# 3. Start development server
npm run dev

# 4. Access at http://localhost:5173
```

### Docker Development

```bash
# 1. Start Docker containers
docker compose up

# 2. Access at http://localhost:5173

# Configuration is in .env.docker (already set up)
```

## 📋 Required Configuration

**Only one required variable:**

- `VITE_API_URL` - Backend API URL (e.g., `http://localhost:8000`)

All other variables have sensible defaults.

## 📁 Configuration Files

| File | Use Case | Committed? |
|------|----------|-----------|
| `.env.example` | Template with all options | ✅ Yes |
| `.env.local.example` | Local dev template | ✅ Yes |
| `.env.local` | Your local config | ❌ No |
| `.env.docker` | Docker development | ✅ Yes |

## 🔑 Key Variables

```bash
# API Configuration
VITE_API_URL=http://localhost:8000        # Required
VITE_API_TIMEOUT=30000                    # Optional (milliseconds)

# Application Settings
VITE_APP_NAME=Frontend Application        # Optional
VITE_DEBUG=true                           # Optional (true/false)

# Feature Flags
VITE_ENABLE_ANALYTICS=false               # Optional (true/false)
VITE_ENABLE_ERROR_REPORTING=false         # Optional (true/false)
```

## 🏗️ Production Build

### Option 1: Environment File

```bash
# 1. Create production config
cp .env.production.example .env.production

# 2. Update production values
# Edit VITE_API_URL, etc.

# 3. Build Docker image
export $(cat .env.production | xargs)
docker compose -f docker-compose.prod.yml build
```

### Option 2: Build Arguments

```bash
docker build \
  --target production \
  --build-arg VITE_API_URL=https://api.example.com \
  -t frontend:prod .
```

## 🐛 Troubleshooting

**Configuration not loading?**
- Restart dev server after changing `.env` files
- Ensure variables start with `VITE_` prefix
- Check browser console for validation errors

**Missing API URL error?**
- Add `VITE_API_URL=http://localhost:8000` to `.env.local`

**Docker issues?**
- Rebuild: `docker compose up --build`
- Check `.env.docker` exists and has VITE_API_URL

## 📖 Full Documentation

See [docs/FRONTEND_CONFIGURATION.md](docs/FRONTEND_CONFIGURATION.md) for:
- Complete configuration reference
- Security best practices
- CI/CD integration
- Advanced usage examples

## 🆘 Quick Help

```bash
# View current configuration
npm run dev
# Check browser console for configuration summary

# Test configuration loading
npm run test src/config/index.test.ts

# Validate Docker configuration
docker compose config
```
