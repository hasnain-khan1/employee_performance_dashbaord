# EPMS Docker Configuration

This directory contains Docker Compose configuration for the Employee Performance Management System (EPMS).

## Quick Start

### Development Environment

```bash
# Start development environment
make dev

# Or manually
docker-compose --env-file env.development up -d
```

### Production Environment

```bash
# Start production environment
make prod

# Or manually
docker-compose --env-file env.production --profile production up -d
```

## Available Commands

| Command | Description |
|---------|-------------|
| `make dev` | Start development environment |
| `make prod` | Start production environment |
| `make build` | Build all images |
| `make up` | Start all services |
| `make down` | Stop all services |
| `make logs` | Show logs for all services |
| `make clean` | Clean up containers, volumes, and images |
| `make seed` | Run database seeding |
| `make test` | Run tests |
| `make shell-backend` | Open shell in backend container |
| `make shell-db` | Open shell in database container |
| `make status` | Show service status |
| `make restart-<service>` | Restart specific service |
| `make logs-<service>` | View logs for specific service |

## Services

### Database (PostgreSQL)
- **Port**: 5432
- **Database**: epms_db
- **User**: postgres
- **Password**: postgres (development)

### Redis Cache
- **Port**: 6379
- **Password**: (empty in development)

### Backend (Django)
- **Port**: 8000
- **URL**: http://localhost:8000
- **API**: http://localhost:8000/api

### Frontend (Vue.js)
- **Port**: 5173
- **URL**: http://localhost:5173

### Nginx (Production only)
- **Port**: 80 (HTTP), 443 (HTTPS)
- **URL**: http://localhost

## Environment Configuration

### Development (`env.development`)
- Debug mode enabled
- Development database
- Hot reloading enabled
- Detailed logging

### Production (`env.production`)
- Debug mode disabled
- Production database
- Optimized builds
- Security headers

## Database Seeding

The system includes automatic database seeding for development:

```bash
# Run seeding manually
make seed

# Or run specific seeding commands
docker-compose exec backend python manage.py seed_data
docker-compose exec backend python manage.py create_review_cycles
```

## Health Checks

All services include health checks:

- **Database**: PostgreSQL connection test
- **Redis**: Redis ping test
- **Backend**: API health endpoint
- **Frontend**: HTTP response test
- **Nginx**: Health endpoint test

## Volumes

| Volume | Description |
|--------|-------------|
| `postgres_data` | PostgreSQL data persistence |
| `redis_data` | Redis data persistence |
| `backend_static` | Django static files |
| `backend_media` | Django media files |
| `backend_logs` | Backend application logs |
| `frontend_dist` | Frontend build artifacts |
| `nginx_logs` | Nginx access and error logs |

## Networks

- **epms_network**: Bridge network connecting all services

## Security Considerations

### Development
- Debug mode enabled
- Default passwords
- CORS allows localhost origins
- No SSL/TLS

### Production
- Debug mode disabled
- Secure passwords required
- CORS restricted to production domains
- SSL/TLS recommended
- Security headers enabled

## Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in environment files
2. **Permission issues**: Check file ownership
3. **Database connection**: Ensure PostgreSQL is healthy
4. **Frontend not loading**: Check Vite configuration

### Logs

```bash
# View all logs
make logs

# View specific service logs
make logs-backend
make logs-frontend
make logs-db
```

### Clean Reset

```bash
# Stop and remove everything
make clean

# Start fresh
make dev
```

## Customization

### Environment Variables

Edit the environment files to customize:
- Database credentials
- Port mappings
- API URLs
- Security settings

### Docker Compose Override

Create `docker-compose.override.yml` for local customizations:

```yaml
version: '3.8'
services:
  backend:
    environment:
      - DEBUG=True
      - LOG_LEVEL=DEBUG
```

## Monitoring

### Service Status
```bash
make status
```

### Health Checks
```bash
# Check backend health
curl http://localhost:8000/api/health/

# Check frontend
curl http://localhost:5173

# Check database
docker-compose exec db pg_isready -U postgres
```

## Backup and Restore

### Database Backup
```bash
docker-compose exec db pg_dump -U postgres epms_db > backup.sql
```

### Database Restore
```bash
docker-compose exec -T db psql -U postgres epms_db < backup.sql
```

## Performance Optimization

### Production Optimizations
- Multi-stage Docker builds
- Optimized base images
- Gunicorn with multiple workers
- Nginx caching
- Redis session storage
- Static file serving

### Resource Limits
Add resource limits in production:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```
