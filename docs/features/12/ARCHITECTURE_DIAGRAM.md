# Story 12.1 - Architecture Diagrams

## Network Flow Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│                        External Network (Host)                         │
│                                                                        │
└────────────────────────────────┬───────────────────────────────────────┘
                                 │
                                 │  Port 80 (HTTP)
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         Docker Bridge Network                           │
│                            (app-network)                                │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                                                                  │  │
│  │  Nginx Reverse Proxy (app-proxy)                                │  │
│  │  Container: nginx:1.27-alpine                                   │  │
│  │  Port: 80 → 80                                                  │  │
│  │                                                                  │  │
│  │  Health: wget http://localhost/health                           │  │
│  │  Resources: 0.5 CPU, 256MB RAM                                  │  │
│  │                                                                  │  │
│  │  Routes:                                                         │  │
│  │    /           → frontend:5173                                  │  │
│  │    /api/*      → backend:8000                                   │  │
│  │    /admin/*    → backend:8000                                   │  │
│  │    /static/*   → backend:8000                                   │  │
│  │    /media/*    → backend:8000                                   │  │
│  │    /ws         → frontend:5173 (WebSocket)                      │  │
│  │    /@vite/*    → frontend:5173 (Dev assets)                     │  │
│  │                                                                  │  │
│  └────┬─────────────────────────────────────────────────┬─────────┘  │
│       │                                                   │            │
│       │ HTTP Proxy                                        │ HTTP Proxy │
│       │                                                   │            │
│       ▼                                                   ▼            │
│  ┌─────────────────────────┐              ┌──────────────────────┐   │
│  │                         │              │                      │   │
│  │  Frontend               │              │  Backend             │   │
│  │  (app-frontend)         │              │  (app-backend)       │   │
│  │                         │              │                      │   │
│  │  Image: frontend-dev    │              │  Image: backend-dev  │   │
│  │  Port: 5173             │              │  Port: 8000          │   │
│  │                         │              │                      │   │
│  │  Tech: React/Vite       │              │  Tech: Django/DRF    │   │
│  │  Node: 20-alpine        │              │  Python: 3.12-slim   │   │
│  │                         │              │                      │   │
│  │  Health: wget :5173     │              │  Health: curl :8000  │   │
│  │  Resources: 2CPU, 2GB   │              │  Resources: 2CPU, 1GB│   │
│  │                         │              │                      │   │
│  │  Features:              │              │  Features:           │   │
│  │  - Hot Module Reload    │              │  - Auto migrations   │   │
│  │  - Live code editing    │              │  - Auto reload       │   │
│  │  - Runtime config       │              │  - Config API        │   │
│  │                         │              │  - REST API          │   │
│  │  Volumes:               │              │                      │   │
│  │  - src/ (bind mount)    │              │  Volumes:            │   │
│  │  - node_modules (named) │              │  - code (bind mount) │   │
│  │                         │              │  - media (named)     │   │
│  │                         │              │  - static (named)    │   │
│  │                         │              │  - logs (bind mount) │   │
│  │                         │              │                      │   │
│  └─────────────────────────┘              └───────┬──────────────┘   │
│                                                    │                  │
│                                     ┌──────────────┴────────────┐     │
│                                     │                           │     │
│                                     ▼                           ▼     │
│                        ┌─────────────────────┐   ┌──────────────────┐│
│                        │                     │   │                  ││
│                        │  PostgreSQL         │   │  Redis           ││
│                        │  (app-db)           │   │  (app-redis)     ││
│                        │                     │   │                  ││
│                        │  Image: postgres:15 │   │  Image: redis:7  ││
│                        │  Port: 5432         │   │  Port: 6379      ││
│                        │                     │   │                  ││
│                        │  Health: pg_isready │   │  Health: ping    ││
│                        │  Resources:         │   │  Resources:      ││
│                        │    1CPU, 512MB      │   │    0.5CPU, 256MB ││
│                        │                     │   │                  ││
│                        │  Volume:            │   │  Volume:         ││
│                        │  - postgres_data    │   │  - redis_data    ││
│                        │                     │   │                  ││
│                        └─────────────────────┘   └──────────────────┘│
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

## Service Startup Sequence

```
Time    Service          Status              Action
──────  ────────────────  ──────────────────  ────────────────────────────────
T+0s    db               starting            PostgreSQL initializing
        redis            starting            Redis initializing

T+5s    db               healthy             pg_isready returns OK
        redis            healthy             redis-cli ping returns PONG

T+10s   backend          starting            Waiting for db/redis health checks
                                            Running migrations
                                            Starting Django dev server

T+40s   backend          healthy             Health endpoint responds 200

T+45s   frontend         starting            Waiting for backend health check
                                            npm run dev starting
                                            Vite dev server initializing

T+75s   frontend         healthy             Vite responds to health check

T+80s   proxy            starting            Waiting for frontend/backend health
                                            nginx starting

T+90s   proxy            healthy             All services ready!
                                            Application accessible at http://localhost/
```

## Data Flow - API Request

```
┌─────────────────────────────────────────────────────────────────┐
│  User Browser                                                   │
│  http://localhost/api/v1/users/                                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ GET /api/v1/users/
                     │ Host: localhost
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│  Nginx Reverse Proxy (app-proxy)                               │
│  - Receives request on port 80                                 │
│  - Matches location /api/                                      │
│  - Proxies to upstream backend                                 │
│  - Adds headers: X-Real-IP, X-Forwarded-For, etc.             │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     │ proxy_pass http://backend:8000/api/v1/users/
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│  Django Backend (app-backend)                                  │
│  - Receives request on port 8000                               │
│  - Django routing matches /api/v1/users/                       │
│  - DRF view processes request                                  │
│  - Queries database if needed                                  │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     │ SQL Query (if needed)
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│  PostgreSQL Database (app-db)                                  │
│  - Executes query                                              │
│  - Returns results                                             │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     │ JSON Response
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│  Django Backend (app-backend)                                  │
│  - Serializes data to JSON                                     │
│  - Adds response headers                                       │
│  - Returns HTTP 200 response                                   │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     │ HTTP 200 + JSON
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│  Nginx Reverse Proxy (app-proxy)                               │
│  - Receives backend response                                   │
│  - Adds security headers                                       │
│  - Applies gzip compression                                    │
│  - Forwards to browser                                         │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     │ HTTP 200 + JSON (compressed)
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│  User Browser                                                  │
│  - Receives response                                           │
│  - Updates UI                                                  │
└────────────────────────────────────────────────────────────────┘
```

## Data Flow - Frontend Access

```
┌─────────────────────────────────────────────────────────────────┐
│  User Browser                                                   │
│  http://localhost/                                              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ GET /
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│  Nginx Reverse Proxy (app-proxy)                               │
│  - Matches location / (catch-all)                              │
│  - Proxies to upstream frontend                                │
│  - Supports WebSocket upgrade for HMR                          │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     │ proxy_pass http://frontend:5173/
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│  Vite Dev Server (app-frontend)                                │
│  - Serves index.html                                           │
│  - Serves bundled JavaScript                                   │
│  - Establishes WebSocket for HMR                               │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     │ HTML + JS + WebSocket
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│  User Browser                                                  │
│  - Renders React application                                   │
│  - React Router displays onboarding page at root URL (/)       │
│    (Feature #14: Onboarding is the main page)                  │
│  - Connects WebSocket for HMR                                  │
│  - Fetches runtime config from /api/v1/config/frontend/       │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     │ GET /api/v1/config/frontend/
                     │ (goes through proxy to backend)
                     │
                     ▼
                [Runtime config loaded, app ready]
```

## Volume Mounting Strategy

```
┌──────────────────────────────────────────────────────────────────┐
│                      Docker Volumes                              │
│                                                                  │
│  Named Volumes (Docker-managed, portable)                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                                                            │ │
│  │  app-postgres-data     → /var/lib/postgresql/data (db)    │ │
│  │  app-redis-data        → /data (redis)                    │ │
│  │  app-backend-media     → /app/media (backend)             │ │
│  │  app-backend-static    → /app/staticfiles (backend)       │ │
│  │  app-frontend-node-modules → /app/node_modules (frontend) │ │
│  │  app-proxy-logs        → /var/log/nginx (proxy)           │ │
│  │                                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Bind Mounts (Host filesystem, for live editing)                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                                                            │ │
│  │  ./backend             → /app (backend)                   │ │
│  │  ./backend/logs        → /app/logs (backend)              │ │
│  │  ./frontend/src        → /app/src (frontend)              │ │
│  │  ./frontend/public     → /app/public (frontend)           │ │
│  │  ./nginx/nginx.conf    → /etc/nginx/nginx.conf (proxy)    │ │
│  │                                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

Benefits:
  ✅ Named volumes persist data across container restarts
  ✅ Bind mounts enable live code editing without rebuilds
  ✅ Separate volumes prevent data loss when rebuilding containers
```

## Resource Allocation

```
┌──────────────────────────────────────────────────────────────────┐
│                   Resource Limits & Reservations                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Service     │  CPU Limit  │  CPU Reserve  │  Mem Limit  │ Mem Reserve │
│  ───────────────────────────────────────────────────────────────│
│  proxy       │  0.5 CPU    │  0.25 CPU     │  256 MB     │  128 MB     │
│  frontend    │  2.0 CPUs   │  1.0 CPU      │  2048 MB    │  512 MB     │
│  backend     │  2.0 CPUs   │  0.5 CPU      │  1024 MB    │  512 MB     │
│  db          │  1.0 CPU    │  0.5 CPU      │  512 MB     │  256 MB     │
│  redis       │  0.5 CPU    │  0.25 CPU     │  256 MB     │  128 MB     │
│  celery*     │  1.0 CPU    │  0.25 CPU     │  512 MB     │  256 MB     │
│  ───────────────────────────────────────────────────────────────│
│  TOTAL       │  7.0 CPUs   │  2.75 CPUs    │  4608 MB    │  1792 MB    │
│                                                                  │
│  * celery is optional (profile: with-celery)                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

Typical Resource Usage (Development):
  CPU: 15-25% (idle: <10%)
  Memory: 2-3 GB (idle: ~1.5 GB)

Resource Strategy:
  - Limits prevent runaway processes
  - Reservations ensure minimum allocation
  - Frontend gets most memory (Vite compilation)
  - Backend gets most CPU (Django processing)
```

## Health Check Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                      Health Check System                         │
└──────────────────────────────────────────────────────────────────┘

Every 10-30 seconds (depending on service):

  Docker Engine
       │
       ├─→ db:           pg_isready -U postgres -d backend_db
       │                 └─→ Returns: healthy/unhealthy
       │
       ├─→ redis:        redis-cli ping
       │                 └─→ Returns: healthy/unhealthy
       │
       ├─→ backend:      curl -f http://localhost:8000/api/v1/health/
       │                 └─→ Checks: Database connectivity, Redis, etc.
       │                 └─→ Returns: healthy/unhealthy
       │
       ├─→ frontend:     wget --spider http://localhost:5173
       │                 └─→ Returns: healthy/unhealthy
       │
       └─→ proxy:        wget --spider http://localhost/health
                         └─→ Returns: healthy/unhealthy

If unhealthy for 3 consecutive checks → Container restarts automatically

Service Dependencies:
  - backend waits for db + redis to be healthy
  - frontend waits for backend to be healthy
  - proxy waits for frontend + backend to be healthy
```

## Network Isolation

```
┌────────────────────────────────────────────────────────────────┐
│                         Host Network                           │
│                                                                │
│  Exposed Ports (accessible from host):                         │
│    - 80:80         (proxy - UNIFIED ENTRY POINT)              │
│    - 5432:5432     (db - for pgAdmin, etc.)                   │
│    - 6379:6379     (redis - for Redis Desktop Manager, etc.)  │
│    - 5173:5173     (frontend - direct access for debugging)   │
│    - 8000:8000     (backend - direct access for debugging)    │
│                                                                │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     │ Port mapping
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│              Docker Bridge Network (app-network)               │
│                                                                │
│  Internal Communication (DNS-based):                           │
│    - proxy can reach:    frontend:5173, backend:8000          │
│    - frontend can reach: backend:8000 (if needed)             │
│    - backend can reach:  db:5432, redis:6379                  │
│    - celery can reach:   db:5432, redis:6379                  │
│                                                                │
│  Network Features:                                             │
│    ✅ Automatic DNS resolution (service name → IP)            │
│    ✅ Network isolation from other Docker networks            │
│    ✅ Can't access other containers outside this network      │
│                                                                │
└────────────────────────────────────────────────────────────────┘

Production Note:
  In production (Story 12.5), only port 80/443 should be exposed.
  Database and Redis should NOT be accessible from outside.
```

---

**Visual Architecture Summary**

This architecture provides:
- ✅ **Unified entry point** via nginx reverse proxy
- ✅ **Automatic service discovery** via Docker DNS
- ✅ **Health-based dependency management**
- ✅ **Data persistence** via named volumes
- ✅ **Live development** via bind mounts
- ✅ **Resource management** via limits/reservations
- ✅ **Network isolation** via bridge network

All accessible with a single command: `./docker-dev.sh start` 🚀
