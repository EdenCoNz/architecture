# Persistent Data Management (Story 12.6)

**Feature ID**: 12
**Story**: 12.6
**Status**: ✅ Completed
**Date**: 2025-10-25

## Overview

This document describes the persistent data management strategy for the unified multi-service orchestration platform. All application data persists between service restarts using Docker named volumes, with comprehensive backup, restore, and cleanup utilities.

## Table of Contents

- [Data Persistence Architecture](#data-persistence-architecture)
- [Named Volumes](#named-volumes)
- [Data Management Commands](#data-management-commands)
- [Backup Strategy](#backup-strategy)
- [Restore Procedures](#restore-procedures)
- [Cleanup Operations](#cleanup-operations)
- [Acceptance Criteria Validation](#acceptance-criteria-validation)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Data Persistence Architecture

### Overview

The application uses Docker named volumes to ensure all critical data persists between container restarts, rebuilds, and deployments. Named volumes are Docker-managed storage units that exist independently of container lifecycles.

### Benefits of Named Volumes

1. **Persistence**: Data survives container removal and recreation
2. **Performance**: Better I/O performance than bind mounts on Docker Desktop
3. **Portability**: Can be backed up, migrated, and shared between containers
4. **Management**: Docker handles volume lifecycle and storage drivers
5. **Security**: Isolated from host filesystem, reducing attack surface

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Docker Host                                 │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  PostgreSQL  │  │   Backend    │  │   Frontend   │         │
│  │  Container   │  │  Container   │  │  Container   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                  │                  │
│         │                 │                  │                  │
│  ┌──────▼────────────────▼──────────────────▼─────────┐        │
│  │           Docker Named Volumes Layer               │        │
│  │                                                     │        │
│  │  📊 app-postgres-data      (Database records)     │        │
│  │  📊 app-redis-data         (Cache/queue data)     │        │
│  │  📁 app-backend-media      (User uploads)         │        │
│  │  📁 app-backend-static     (Static files)         │        │
│  │  📦 app-frontend-node-modules (Dependencies)      │        │
│  │  📝 app-proxy-logs         (Nginx logs)           │        │
│  └─────────────────────────────────────────────────────┘        │
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────┐        │
│  │          Host Filesystem Storage                    │        │
│  │  /var/lib/docker/volumes/app-*                      │        │
│  └─────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Named Volumes

### Volume Inventory

| Volume Name | Purpose | Container Path | Typical Size | Critical |
|-------------|---------|----------------|--------------|----------|
| `app-postgres-data` | PostgreSQL database | `/var/lib/postgresql/data` | 100MB-10GB | ✅ Critical |
| `app-redis-data` | Redis persistence | `/data` | 10MB-1GB | ⚠️ Important |
| `app-backend-media` | User uploads | `/app/media` | Varies | ✅ Critical |
| `app-backend-static` | Static files | `/app/staticfiles` | 10MB-100MB | ℹ️ Regenerable |
| `app-frontend-node-modules` | NPM packages | `/app/node_modules` | 200MB-500MB | ℹ️ Regenerable |
| `app-proxy-logs` | Nginx logs | `/var/log/nginx` | 10MB-1GB | ℹ️ Optional |

### Volume Details

#### 1. app-postgres-data (Critical)

**Purpose**: Stores all PostgreSQL database data including tables, indexes, and transaction logs.

**Data Included**:
- User accounts and authentication data
- Application records and business data
- Database schema and migrations history
- PostgreSQL system catalogs

**Persistence Guarantees**:
- ✅ Survives container restarts
- ✅ Survives container rebuilds
- ✅ Survives `docker compose down`
- ❌ Removed by `docker compose down -v`
- ❌ Removed by `./docker-dev.sh clean-all`

**Backup Priority**: HIGHEST - Daily backups recommended

#### 2. app-redis-data (Important)

**Purpose**: Redis AOF (Append-Only File) persistence for cache and queue data.

**Data Included**:
- Session data
- Cached query results
- Celery task queue
- Rate limiting counters

**Persistence Guarantees**:
- ✅ Survives container restarts
- ✅ Survives container rebuilds
- ⚠️ Can be regenerated but may impact performance

**Backup Priority**: MEDIUM - Can be rebuilt, but backup recommended for production

#### 3. app-backend-media (Critical)

**Purpose**: User-uploaded files and generated media.

**Data Included**:
- Profile images
- Document uploads
- Generated reports
- Any user-submitted content

**Persistence Guarantees**:
- ✅ Survives container restarts
- ✅ Survives container rebuilds
- ⚠️ Cannot be regenerated - permanent data loss if deleted

**Backup Priority**: HIGHEST - Must be backed up before any destructive operations

#### 4. app-backend-static (Regenerable)

**Purpose**: Collected Django static files (CSS, JavaScript, images).

**Data Included**:
- Django admin CSS/JS
- Third-party library assets
- Application static files

**Persistence Guarantees**:
- ✅ Survives container restarts
- ✅ Can be regenerated with `python manage.py collectstatic`

**Backup Priority**: LOW - Can be regenerated, backup optional

#### 5. app-frontend-node-modules (Regenerable)

**Purpose**: Installed NPM dependencies for frontend development.

**Data Included**:
- React, Vite, and development dependencies
- TypeScript compiler and tools
- Build tools and utilities

**Persistence Guarantees**:
- ✅ Survives container restarts
- ✅ Can be regenerated with `npm install`

**Backup Priority**: NONE - Always regenerated from package-lock.json

#### 6. app-proxy-logs (Optional)

**Purpose**: Nginx access and error logs.

**Data Included**:
- HTTP request logs
- Error logs
- Access patterns

**Persistence Guarantees**:
- ✅ Survives container restarts
- ℹ️ Typically rotated and archived separately

**Backup Priority**: LOW - Logs are typically sent to external aggregation systems

---

## Data Management Commands

All data management is handled through the enhanced `./docker-dev.sh` helper script.

### Volume Inspection

```bash
# Show all volumes and disk usage
./docker-dev.sh volumes
```

**Output Example**:
```
=== Volume information and disk usage ===

INFO: Persistent volumes:
VOLUME NAME                    DRIVER    MOUNTPOINT
app-postgres-data             local     /var/lib/docker/volumes/app-postgres-data/_data
app-redis-data                local     /var/lib/docker/volumes/app-redis-data/_data
app-backend-media             local     /var/lib/docker/volumes/app-backend-media/_data
app-backend-static            local     /var/lib/docker/volumes/app-backend-static/_data
app-frontend-node-modules     local     /var/lib/docker/volumes/app-frontend-node-modules/_data
app-proxy-logs                local     /var/lib/docker/volumes/app-proxy-logs/_data

INFO: Volume sizes:
  app-postgres-data: 42M
  app-redis-data: 8.0K
  app-backend-media: 256K
  app-backend-static: 12M
  app-frontend-node-modules: 387M
  app-proxy-logs: 128K

INFO: Volume details:
  📊 app-postgres-data     - Database records (PostgreSQL data)
  📊 app-redis-data        - Cache and queue data (Redis persistence)
  📁 app-backend-media     - User uploaded files and media
  📁 app-backend-static    - Collected static files (CSS, JS, images)
  📦 app-frontend-node-modules - Frontend dependencies (npm packages)
  📝 app-proxy-logs        - Nginx access and error logs
```

### Service Status

```bash
# View detailed service and volume status
./docker-dev.sh status
```

---

## Backup Strategy

### Full Backup

Creates a complete backup of all critical data (database, media files, static files).

```bash
./docker-dev.sh backup
```

**What Gets Backed Up**:
1. PostgreSQL database (SQL dump)
2. Backend media files (tar.gz archive)
3. Backend static files (tar.gz archive)

**Backup Location**: `./backups/full_backup_YYYYMMDD_HHMMSS.tar.gz`

**Backup Contents**:
```
full_backup_20251025_143022.tar.gz
├── db_backup_20251025_143022.sql
├── media_backup_20251025_143022.tar.gz
└── static_backup_20251025_143022.tar.gz
```

**Process**:
1. Export PostgreSQL database using `pg_dump`
2. Archive media volume using `tar`
3. Archive static volume using `tar`
4. Combine all into single compressed archive
5. Remove temporary individual backups

**Time Estimate**: 10 seconds - 5 minutes (depends on data size)

### Database-Only Backup

For quick database snapshots:

```bash
./docker-dev.sh backup-db
```

**Backup Location**: `./backups/db_backup_YYYYMMDD_HHMMSS.sql`

**Use Cases**:
- Before running migrations
- Before schema changes
- Quick development snapshots
- CI/CD pipeline testing

**Time Estimate**: 5-30 seconds

### Automated Backup Schedule (Production)

For production environments, implement automated backups:

```bash
# Add to crontab for daily backups at 2 AM
0 2 * * * cd /path/to/project && ./docker-dev.sh backup >> /var/log/backup.log 2>&1

# Weekly full backups with rotation (keep 4 weeks)
0 3 * * 0 cd /path/to/project && ./docker-dev.sh backup && find ./backups -name "full_backup_*.tar.gz" -mtime +28 -delete
```

### Backup Retention Policy

**Recommended Retention**:
- Development: 7 days (weekly rotation)
- Staging: 14 days (bi-weekly rotation)
- Production: 30 days local + 90 days offsite

**Storage Recommendations**:
- Keep local backups in `./backups/`
- Copy critical backups to remote storage (S3, Azure Blob, etc.)
- Use versioning on remote storage
- Test restore procedures quarterly

---

## Restore Procedures

### Full Restore

Restore from a complete backup archive:

```bash
./docker-dev.sh restore ./backups/full_backup_20251025_143022.tar.gz
```

**Process**:
1. Confirms destructive operation (user must type "yes")
2. Extracts backup archive to temporary directory
3. Restores database from SQL dump
4. Restores media files to volume
5. Restores static files to volume
6. Cleans up temporary files
7. Prompts to restart services

**Safety Features**:
- Requires explicit confirmation
- Shows backup filename before proceeding
- Validates backup file exists
- Lists available backups if file not specified

**Post-Restore Steps**:
```bash
# Restart services to apply changes
./docker-dev.sh restart

# Verify data integrity
./docker-dev.sh backend-shell
# In Django shell:
# User.objects.count()  # Verify users restored
```

### Database-Only Restore

Restore database from SQL dump:

```bash
# Stop backend to prevent conflicts
docker compose stop backend

# Restore database
docker compose exec -T db psql -U postgres backend_db < ./backups/db_backup_20251025_143022.sql

# Restart backend
docker compose start backend
```

### Partial Restore

Restore specific volumes manually:

```bash
# Restore media files only
docker run --rm \
  -v app-backend-media:/data \
  -v "$(pwd)/backups:/backup" \
  alpine \
  sh -c "rm -rf /data/* && tar xzf /backup/media_backup_20251025_143022.tar.gz -C /data"
```

---

## Cleanup Operations

### Safe Cleanup (Preserve Data)

Remove containers but keep all data:

```bash
./docker-dev.sh clean
```

**What's Removed**:
- All running containers
- Container networks

**What's Preserved**:
- All named volumes
- All persistent data
- Configuration files

**Use Cases**:
- Daily development cleanup
- Switching branches
- Rebuilding containers

### Selective Cleanup

#### Clean Containers Only

```bash
./docker-dev.sh clean-containers
```

Identical to `clean` - removes containers, preserves volumes.

#### Clean Log Files

```bash
./docker-dev.sh clean-logs
```

**What's Removed**:
- `./backend/logs/*` (bind-mounted logs)
- `app-proxy-logs` volume

**What's Preserved**:
- All other data volumes

**Use Cases**:
- Disk space recovery
- Log rotation
- Development cleanup

#### Clean Redis Cache

```bash
./docker-dev.sh clean-cache
```

**What's Removed**:
- `app-redis-data` volume (cache/queue data)

**What's Preserved**:
- Database, media, static files
- All other volumes

**Use Cases**:
- Clear corrupted cache
- Reset session data
- Testing fresh cache behavior

**Note**: Run `./docker-dev.sh start` after cleanup to recreate Redis with empty cache.

### Complete Cleanup (DESTRUCTIVE)

Remove everything including all persistent data:

```bash
./docker-dev.sh clean-all
```

**⚠️ DESTRUCTIVE OPERATION - REQUIRES CONFIRMATION**

**What's Removed**:
- All containers
- All volumes (database, media, cache, logs)
- All persistent data

**Confirmation Required**:
```
Type 'DELETE EVERYTHING' to confirm:
```

**Use Cases**:
- Reset development environment
- Remove all test data
- Fresh start after major changes
- Corrupted data recovery

**Safety Features**:
1. Shows detailed warning banner
2. Lists all data that will be lost
3. Suggests backup first
4. Requires exact phrase "DELETE EVERYTHING"
5. Cancels if phrase doesn't match exactly

**Pre-Cleanup Checklist**:
```bash
# 1. Create backup
./docker-dev.sh backup

# 2. Verify backup created
ls -lh ./backups/

# 3. Only then proceed with cleanup
./docker-dev.sh clean-all
```

---

## Acceptance Criteria Validation

### ✅ AC1: Data Persists Between Restarts

**Requirement**: Given I create data in the application, when I stop and restart services, then my data should still be present.

**Implementation**:
- All critical data stored in named Docker volumes
- Volumes persist independently of container lifecycle
- `docker compose down` preserves volumes by default
- `docker compose up` reattaches existing volumes

**Validation Test**:
```bash
# 1. Start services and create data
./docker-dev.sh start
./docker-dev.sh backend-shell
# In Django shell: User.objects.create_user('test', 'test@example.com', 'password')

# 2. Stop services
./docker-dev.sh stop

# 3. Restart services
./docker-dev.sh start

# 4. Verify data persists
./docker-dev.sh backend-shell
# In Django shell: User.objects.filter(username='test').exists()  # Should return True
```

**Status**: ✅ PASS

---

### ✅ AC2: Schema Changes Persist

**Requirement**: Given I update database schema, when I restart services, then schema changes should be preserved.

**Implementation**:
- PostgreSQL stores schema in `app-postgres-data` volume
- Migration history stored in `django_migrations` table
- Volume persists across container restarts and rebuilds

**Validation Test**:
```bash
# 1. Create and run migration
./docker-dev.sh backend-makemigrations
./docker-dev.sh backend-migrate

# 2. Rebuild backend container
docker compose up -d --build backend

# 3. Verify migrations still applied
./docker-dev.sh exec backend python manage.py showmigrations
# Should show all migrations as [X] applied
```

**Status**: ✅ PASS

---

### ✅ AC3: Uploaded Files Persist

**Requirement**: Given I upload files or create content, when services restart, then that content should remain available.

**Implementation**:
- User uploads stored in `app-backend-media` volume
- Volume mounted at `/app/media` in backend container
- Django MEDIA_ROOT configured to use persistent volume

**Validation Test**:
```bash
# 1. Upload file through Django admin or API
# 2. Verify file in media volume
docker run --rm -v app-backend-media:/data alpine ls -la /data

# 3. Restart services
./docker-dev.sh restart

# 4. Verify file still exists
docker run --rm -v app-backend-media:/data alpine ls -la /data
```

**Status**: ✅ PASS

---

### ✅ AC4: Cleanup Command Available

**Requirement**: Given I need to reset my environment, when I run the cleanup command, then I should be able to remove all persistent data.

**Implementation**:
- `./docker-dev.sh clean-all` removes all volumes
- Requires explicit confirmation ("DELETE EVERYTHING")
- Shows warning and lists data that will be lost
- Multiple selective cleanup options available

**Available Cleanup Commands**:
1. `clean` - Remove containers, preserve data
2. `clean-containers` - Remove containers only
3. `clean-logs` - Remove log files only
4. `clean-cache` - Remove Redis cache only
5. `clean-all` - Remove everything (destructive)

**Validation Test**:
```bash
# 1. Create backup first
./docker-dev.sh backup

# 2. Run complete cleanup
./docker-dev.sh clean-all
# Type: DELETE EVERYTHING

# 3. Verify volumes removed
docker volume ls --filter "name=app-"
# Should show no volumes

# 4. Restore from backup if needed
./docker-dev.sh restore ./backups/full_backup_*.tar.gz
```

**Status**: ✅ PASS

---

## Best Practices

### Development Environment

1. **Regular Backups**: Create backups before major changes
   ```bash
   ./docker-dev.sh backup
   ```

2. **Clean Logs Periodically**: Prevent disk space issues
   ```bash
   ./docker-dev.sh clean-logs
   ```

3. **Use Selective Cleanup**: Don't use `clean-all` unless necessary
   ```bash
   ./docker-dev.sh clean  # Preserves data
   ```

4. **Monitor Disk Usage**: Check volume sizes regularly
   ```bash
   ./docker-dev.sh volumes
   ```

### Production Environment

1. **Automated Backups**: Implement daily backup schedule
   ```bash
   # Daily backup at 2 AM
   0 2 * * * cd /path/to/project && ./docker-dev.sh backup
   ```

2. **Offsite Storage**: Copy backups to remote storage
   ```bash
   # After backup, sync to S3
   aws s3 sync ./backups/ s3://my-bucket/backups/
   ```

3. **Test Restores**: Verify backups work quarterly
   ```bash
   # Test restore in staging environment
   ./docker-dev.sh restore ./backups/latest.tar.gz
   ```

4. **Volume Monitoring**: Monitor volume sizes and growth
   ```bash
   # Alert if volumes exceed threshold
   docker system df -v
   ```

5. **Backup Retention**: Implement rotation policy
   ```bash
   # Keep 30 days, delete older
   find ./backups -name "*.tar.gz" -mtime +30 -delete
   ```

### Security

1. **Encrypt Backups**: Use encryption for sensitive data
   ```bash
   # Encrypt backup
   gpg --encrypt --recipient admin@example.com full_backup.tar.gz
   ```

2. **Secure Storage**: Limit backup directory permissions
   ```bash
   chmod 700 ./backups
   ```

3. **Access Control**: Restrict who can run cleanup commands
   ```bash
   # Only allow specific users to run docker commands
   sudo usermod -aG docker username
   ```

### Data Integrity

1. **Verify Backups**: Test backup integrity after creation
   ```bash
   tar -tzf ./backups/full_backup_*.tar.gz > /dev/null
   echo $?  # Should be 0
   ```

2. **Database Integrity**: Run integrity checks
   ```bash
   ./docker-dev.sh db-shell
   # In psql: \dt  -- List tables
   ```

3. **Volume Health**: Check volume consistency
   ```bash
   docker volume inspect app-postgres-data
   ```

---

## Troubleshooting

### Issue: Backup Fails with "Database Not Running"

**Symptom**: `./docker-dev.sh backup` fails with connection error

**Solution**:
```bash
# Ensure services are running
./docker-dev.sh start

# Wait for database to be healthy
docker compose ps db

# Retry backup
./docker-dev.sh backup
```

---

### Issue: Restore Doesn't Apply Changes

**Symptom**: Data restored but not visible in application

**Solution**:
```bash
# Restart all services after restore
./docker-dev.sh restart

# If issue persists, rebuild containers
./docker-dev.sh rebuild
```

---

### Issue: Volume Disk Space Full

**Symptom**: Error creating volume or writing data

**Solution**:
```bash
# Check volume sizes
./docker-dev.sh volumes

# Clean logs
./docker-dev.sh clean-logs

# Clean Redis cache if not needed
./docker-dev.sh clean-cache

# Remove unused Docker resources
docker system prune -a --volumes
```

---

### Issue: Can't Delete Volume (In Use)

**Symptom**: `docker volume rm` fails with "volume is in use"

**Solution**:
```bash
# Stop all services first
./docker-dev.sh stop

# Remove containers
docker compose down

# Now remove volume
docker volume rm app-volume-name
```

---

### Issue: Backup Directory Not Found

**Symptom**: `./docker-dev.sh backup` fails to create directory

**Solution**:
```bash
# Create backup directory manually
mkdir -p ./backups

# Set permissions
chmod 755 ./backups

# Retry backup
./docker-dev.sh backup
```

---

### Issue: PostgreSQL Won't Start After Restore

**Symptom**: Database container crashes after restore

**Solution**:
```bash
# Check logs
docker compose logs db

# If corruption detected:
# 1. Stop database
docker compose stop db

# 2. Remove corrupted volume
docker volume rm app-postgres-data

# 3. Restore from backup
./docker-dev.sh restore ./backups/good_backup.tar.gz

# 4. Restart services
./docker-dev.sh start
```

---

### Issue: Lost Data After `docker compose down -v`

**Symptom**: All data disappeared after running command

**Solution**:
```bash
# Restore from backup
./docker-dev.sh restore ./backups/latest.tar.gz

# Prevention: Never use -v flag unless intentional
# Use ./docker-dev.sh clean instead (preserves volumes)
./docker-dev.sh clean
```

---

## Summary

### Key Capabilities

✅ **Data Persistence**: All critical data persists across restarts
✅ **Backup/Restore**: Full and partial backup/restore capabilities
✅ **Selective Cleanup**: Multiple cleanup options for different scenarios
✅ **Volume Management**: Comprehensive volume inspection and monitoring
✅ **Safety Features**: Confirmations and warnings for destructive operations

### Data Protection Guarantees

| Operation | Database | Media | Static | Cache | Logs |
|-----------|----------|-------|--------|-------|------|
| `docker compose down` | ✅ Preserved | ✅ Preserved | ✅ Preserved | ✅ Preserved | ✅ Preserved |
| `docker compose up --build` | ✅ Preserved | ✅ Preserved | ✅ Preserved | ✅ Preserved | ✅ Preserved |
| `./docker-dev.sh clean` | ✅ Preserved | ✅ Preserved | ✅ Preserved | ✅ Preserved | ✅ Preserved |
| `./docker-dev.sh clean-logs` | ✅ Preserved | ✅ Preserved | ✅ Preserved | ✅ Preserved | ❌ Removed |
| `./docker-dev.sh clean-cache` | ✅ Preserved | ✅ Preserved | ✅ Preserved | ❌ Removed | ✅ Preserved |
| `./docker-dev.sh clean-all` | ❌ Removed | ❌ Removed | ❌ Removed | ❌ Removed | ❌ Removed |
| `docker compose down -v` | ❌ Removed | ❌ Removed | ❌ Removed | ❌ Removed | ❌ Removed |

### Quick Reference

```bash
# View volumes
./docker-dev.sh volumes

# Create backup
./docker-dev.sh backup

# Restore backup
./docker-dev.sh restore ./backups/full_backup_*.tar.gz

# Clean containers (safe)
./docker-dev.sh clean

# Reset everything (destructive)
./docker-dev.sh clean-all
```

---

**Documentation Status**: Complete
**Last Updated**: 2025-10-25
**Story Status**: ✅ All acceptance criteria met
