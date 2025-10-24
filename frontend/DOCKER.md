# Frontend Development Container

This guide explains how to run the frontend application in a containerized development environment.

## Prerequisites

- **Docker Engine**: 23.0+ (with BuildKit support)
- **Docker Compose**: 2.0+ (comes with Docker Desktop)

Verify installation:
```bash
docker --version
docker compose version
```

## Quick Start

### Start Development Container

From the `frontend` directory:

```bash
# Start the development container
docker compose up

# Or start in detached mode (background)
docker compose up -d
```

The application will be available at:
- **http://localhost:5173**

### Stop Development Container

```bash
# Stop the container
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

## Development Workflow

### Hot Module Replacement (HMR)

The development container is configured with hot module replacement:

1. Start the container: `docker compose up`
2. Edit files in `src/` directory
3. Save changes
4. Browser automatically reloads with your changes

**Note**: Changes to these files trigger automatic reload:
- All files in `src/`
- `index.html`
- `vite.config.ts`
- Configuration files (tsconfig.json, etc.)

### Installing New Dependencies

You can install dependencies without rebuilding the container:

```bash
# Execute npm install inside the running container
docker compose exec frontend npm install <package-name>

# Example: Install axios
docker compose exec frontend npm install axios

# Install dev dependencies
docker compose exec frontend npm install -D <package-name>
```

Changes to `package.json` and `package-lock.json` are automatically synced due to volume mounts.

**Dependency Persistence**: Installed dependencies are stored in a Docker volume (`node_modules`) and persist between container restarts.

### Running Commands in Container

```bash
# Run any npm script
docker compose exec frontend npm run <script>

# Examples:
docker compose exec frontend npm run lint
docker compose exec frontend npm run test
docker compose exec frontend npm run format

# Open shell in container
docker compose exec frontend sh
```

### View Logs

```bash
# Follow logs (Ctrl+C to exit)
docker compose logs -f frontend

# View last 100 lines
docker compose logs --tail=100 frontend
```

## Container Management

### Rebuild Container

When you change Dockerfile or need a fresh build:

```bash
# Rebuild and restart
docker compose up --build

# Force rebuild (ignore cache)
docker compose build --no-cache
docker compose up
```

### Check Container Status

```bash
# View running containers
docker compose ps

# View container health
docker inspect frontend-dev --format='{{.State.Health.Status}}'
```

### Clean Up

```bash
# Stop and remove containers, networks
docker compose down

# Remove containers, networks, and volumes
docker compose down -v

# Remove all (including images)
docker compose down -v --rmi all
```

## Troubleshooting

### Port Already in Use

If port 5173 is already in use:

1. **Option 1**: Stop the process using the port
   ```bash
   lsof -ti:5173 | xargs kill -9
   ```

2. **Option 2**: Change the port in `docker-compose.yml`
   ```yaml
   ports:
     - "3000:5173"  # Access at http://localhost:3000
   ```

### Dependencies Not Installing

If `npm install` fails inside the container:

```bash
# Remove the node_modules volume and rebuild
docker compose down -v
docker compose up --build
```

### Container Not Responding

If the container starts but application doesn't load:

```bash
# Check container logs
docker compose logs -f frontend

# Restart the container
docker compose restart frontend

# Full rebuild
docker compose down
docker compose up --build
```

### Changes Not Reflecting

If file changes aren't being picked up:

1. Verify volume mounts in `docker-compose.yml`
2. Check file permissions (container runs as non-root user)
3. Restart the container: `docker compose restart frontend`
4. Try hard refresh in browser: `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)

### Permission Errors

The container runs as a non-root user (UID 1001). If you encounter permission issues:

```bash
# Check file ownership in container
docker compose exec frontend ls -la /app

# If needed, fix permissions on host
sudo chown -R $USER:$USER .
```

## Advanced Usage

### Environment Variables

Configure environment variables in `docker-compose.yml`:

```yaml
environment:
  - NODE_ENV=development
  - VITE_API_URL=http://localhost:8000
  - VITE_CUSTOM_VAR=value
```

Or create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:8000
VITE_CUSTOM_VAR=value
```

Docker Compose will automatically load `.env` files.

### Resource Limits

Resource limits are configured in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'        # Maximum 2 CPU cores
      memory: 2G       # Maximum 2GB RAM
    reservations:
      cpus: '1'        # Reserve 1 CPU core
      memory: 512M     # Reserve 512MB RAM
```

Adjust these based on your system resources.

### Multiple Environments

To run different configurations:

1. Create environment-specific compose files:
   - `docker-compose.yml` (base configuration)
   - `docker-compose.staging.yml` (staging overrides)
   - `docker-compose.production.yml` (production overrides)

2. Run with specific configuration:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.staging.yml up
   ```

## Development vs Production

### Development Container

**Purpose**: Local development with hot module replacement

**Features**:
- Volume mounts for live code editing
- Development dependencies included
- Vite dev server with HMR
- Source maps enabled
- Debugging tools available

**Start**: `docker compose up`

### Production Container

**Purpose**: Optimized deployment

**Features**:
- Minimal image size (~15-20MB)
- Only production dependencies
- Nginx static file server
- Gzip compression enabled
- Cache headers configured
- Non-root user execution

**Build**:
```bash
docker build --target production -t frontend:prod .
```

**Run**:
```bash
docker run -p 80:80 frontend:prod
```

**Access**: http://localhost

## Best Practices

1. **Don't commit node_modules**: The `.dockerignore` file excludes it
2. **Use named volumes**: Persist dependencies between rebuilds
3. **Clean up regularly**: Remove unused containers and volumes
4. **Monitor resource usage**: `docker stats frontend-dev`
5. **Check logs frequently**: `docker compose logs -f frontend`
6. **Keep base image updated**: Regularly rebuild with latest Node.js patches

## Integration with Backend

When running full stack locally, see the root-level `docker-compose.yml` for orchestrating frontend + backend + database together.

Example multi-service setup:
```bash
# From project root
docker compose up frontend backend database
```

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Vite Documentation](https://vitejs.dev/)
- [Node.js Docker Best Practices](https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md)
