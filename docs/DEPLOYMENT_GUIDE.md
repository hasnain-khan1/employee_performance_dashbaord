# Deployment Guide

This guide covers deploying the EPMS application to production environments.

## Prerequisites

- Docker and Docker Compose
- Domain name (optional)
- SSL certificate (for HTTPS)
- Database backup strategy
- Monitoring setup

## Production Deployment

### 1. Environment Configuration

Create production environment files:

**Backend (.env)**
```env
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_NAME=epms_prod
DB_USER=epms_user
DB_PASSWORD=your-db-password
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/1

# Email configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Static files
STATIC_URL=/static/
STATIC_ROOT=/var/www/static/
MEDIA_URL=/media/
MEDIA_ROOT=/var/www/media/
```

**Frontend (.env.production)**
```env
VITE_API_BASE_URL=https://yourdomain.com/api
VITE_APP_TITLE=EPMS - Employee Performance Management
```

### 2. Docker Compose Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: epms_prod
      POSTGRES_USER: epms_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U epms_user"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile.prod
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - DB_NAME=epms_prod
      - DB_USER=epms_user
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/1
    volumes:
      - backend_static:/app/staticfiles
      - backend_media:/app/media
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn epms.wsgi:application --bind 0.0.0.0:8000 --workers 3"

  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile.prod
    environment:
      - VITE_API_BASE_URL=https://yourdomain.com/api
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf
      - backend_static:/var/www/static
      - backend_media:/var/www/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  backend_static:
  backend_media:
```

### 3. Production Dockerfiles

**Backend Dockerfile.prod**
```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "epms.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

**Frontend Dockerfile.prod**
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 4. Nginx Configuration

**nginx.prod.conf**
```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    # HTTP redirect to HTTPS
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Admin routes
        location /admin/ {
            limit_req zone=api burst=10 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files
        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Media files
        location /media/ {
            alias /var/www/media/;
            expires 1y;
            add_header Cache-Control "public";
        }

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 5. Deployment Steps

1. **Prepare the server**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Deploy the application**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd epms-mvp
   
   # Create environment files
   cp .env.example .env
   # Edit .env with production values
   
   # Start services
   docker-compose -f docker-compose.prod.yml up -d
   
   # Run initial setup
   docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
   docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
   ```

3. **Setup SSL certificates**
   ```bash
   # Using Let's Encrypt
   sudo apt install certbot
   sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
   
   # Copy certificates
   sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./ssl/cert.pem
   sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./ssl/key.pem
   sudo chown $USER:$USER ./ssl/*
   ```

4. **Setup monitoring**
   ```bash
   # Install monitoring tools
   docker run -d --name=prometheus -p 9090:9090 prom/prometheus
   docker run -d --name=grafana -p 3000:3000 grafana/grafana
   ```

## Database Management

### Backup
```bash
# Create backup
docker-compose exec db pg_dump -U epms_user epms_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose exec -T db psql -U epms_user epms_prod < backup_file.sql
```

### Migration
```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create migration
docker-compose exec backend python manage.py makemigrations
```

## Monitoring and Logs

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Health checks
```bash
# Check service status
docker-compose ps

# Check API health
curl -f http://localhost/api/health
```

## Security Considerations

1. **Environment Variables**: Never commit sensitive data to version control
2. **Database Security**: Use strong passwords and limit access
3. **SSL/TLS**: Always use HTTPS in production
4. **Firewall**: Restrict access to necessary ports only
5. **Updates**: Regularly update dependencies and base images
6. **Backups**: Implement automated backup strategy
7. **Monitoring**: Set up alerts for system issues

## Scaling

### Horizontal Scaling
```yaml
# Scale backend services
docker-compose up -d --scale backend=3

# Use load balancer
# Configure nginx upstream with multiple backend instances
```

### Database Scaling
- Use read replicas for read-heavy operations
- Implement connection pooling
- Consider database sharding for large datasets

## Troubleshooting

### Common Issues

1. **Database connection errors**
   - Check database credentials
   - Verify database is running
   - Check network connectivity

2. **Static files not loading**
   - Run `collectstatic` command
   - Check nginx configuration
   - Verify file permissions

3. **API errors**
   - Check backend logs
   - Verify environment variables
   - Check database migrations

4. **Frontend not loading**
   - Check build process
   - Verify nginx configuration
   - Check browser console for errors

### Debug Commands
```bash
# Check container logs
docker-compose logs service_name

# Access container shell
docker-compose exec service_name sh

# Check resource usage
docker stats

# Restart services
docker-compose restart service_name
```