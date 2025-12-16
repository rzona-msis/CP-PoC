# Docker Deployment Guide - Campus Resource Hub

This guide explains how to deploy the Campus Resource Hub using Docker.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development Deployment](#development-deployment)
- [Production Deployment](#production-deployment)
- [Environment Variables](#environment-variables)
- [Docker Commands Reference](#docker-commands-reference)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

1. **Docker** installed on your system
   - Download from: https://www.docker.com/get-started
   - Verify installation: `docker --version`

2. **Docker Compose** (included with Docker Desktop)
   - Verify: `docker-compose --version`

---

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd AIDD-Final

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
# Open browser to http://localhost:5000
```

### Option 2: Using Docker CLI

```bash
# Build the image
docker build -t campus-resource-hub .

# Run the container
docker run -d \
  --name campus-hub \
  -p 5000:5000 \
  -e SECRET_KEY="your-secret-key" \
  campus-resource-hub

# View logs
docker logs -f campus-hub

# Access the application
# Open browser to http://localhost:5000
```

---

## Development Deployment

For development with hot reload:

```bash
# Use the development docker-compose file
docker-compose -f docker-compose.dev.yml up

# Or with rebuild
docker-compose -f docker-compose.dev.yml up --build
```

**Features:**
- Hot reload on code changes
- Debug mode enabled
- Source code mounted as volume
- Database persisted locally

---

## Production Deployment

### Step 1: Configure Environment

```bash
# Create .env file from example
cp .env.example .env

# Edit .env with production values
nano .env  # or vim, code, etc.
```

**Important:** Set these variables:
- `SECRET_KEY` - Use a strong random key
- `FLASK_ENV=production`
- Configure email settings if using notifications
- Add API keys for optional features

### Step 2: Build and Deploy

```bash
# Build the production image
docker-compose build

# Start the service
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
```

### Step 3: Verify Deployment

```bash
# Check health endpoint
curl http://localhost:5000/health

# Should return:
# {"app": "Campus Resource Hub", "status": "healthy"}
```

### Step 4: Access the Application

Open your browser to:
- **Application**: http://localhost:5000
- **Admin Login**: admin@university.edu / admin123
- **Staff Login**: sjohnson@university.edu / staff123
- **Student Login**: asmith@university.edu / student123

---

## Environment Variables

### Required Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for sessions | `dev-secret-key-change-in-production` |
| `FLASK_ENV` | Environment (development/production) | `production` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MAIL_SERVER` | SMTP server for emails | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USE_TLS` | Use TLS for email | `true` |
| `MAIL_USERNAME` | Email account username | - |
| `MAIL_PASSWORD` | Email account password | - |
| `MAIL_SUPPRESS_SEND` | Suppress email sending (dev) | `true` |
| `GEMINI_API_KEY` | Google Gemini API key for AI | - |
| `GA_MEASUREMENT_ID` | Google Analytics ID | - |

### Setting Environment Variables

**Method 1: .env file (Recommended)**
```bash
# Create .env in project root
SECRET_KEY=my-super-secret-key-here
FLASK_ENV=production
GEMINI_API_KEY=your-api-key
```

**Method 2: Docker Compose Override**
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  web:
    environment:
      - SECRET_KEY=my-secret-key
      - GEMINI_API_KEY=my-api-key
```

**Method 3: Command Line**
```bash
docker run -e SECRET_KEY=my-key -e FLASK_ENV=production ...
```

---

## Docker Commands Reference

### Container Management

```bash
# Start containers
docker-compose up -d

# Stop containers
docker-compose down

# Restart containers
docker-compose restart

# View running containers
docker-compose ps

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f web

# Execute command in container
docker-compose exec web bash

# Execute Python command
docker-compose exec web python -c "from src.models.database import *; print('DB OK')"
```

### Building and Cleaning

```bash
# Build/rebuild images
docker-compose build
docker-compose build --no-cache  # Fresh build

# Remove containers and volumes
docker-compose down -v

# Clean up unused images
docker image prune

# Clean up everything
docker system prune -a
```

### Database Management

```bash
# Access database in running container
docker-compose exec web python

# In Python shell:
from src.models.database import get_db_connection
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM users")
print(cursor.fetchone())
conn.close()

# Backup database
docker cp campus-resource-hub:/app/src/campus_hub.db ./backup_$(date +%Y%m%d).db

# Restore database
docker cp ./backup.db campus-resource-hub:/app/src/campus_hub.db
docker-compose restart
```

### Monitoring

```bash
# Resource usage
docker stats campus-resource-hub

# Inspect container
docker inspect campus-resource-hub

# Health check status
docker inspect --format='{{.State.Health.Status}}' campus-resource-hub
```

---

## Advanced Configuration

### Using a Reverse Proxy (nginx)

Create `nginx.conf`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://web:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Add to `docker-compose.yml`:

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - web
    networks:
      - campus-hub-network
```

### SSL/TLS with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Update nginx config to use SSL
# Add certificate paths to nginx.conf
```

### Scaling Horizontally

```bash
# Run multiple instances
docker-compose up -d --scale web=3

# Use nginx as load balancer
# Update nginx config with upstream servers
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker-compose logs web

# Check if port is already in use
netstat -tulpn | grep 5000  # Linux
netstat -ano | findstr :5000  # Windows

# Remove old containers and restart
docker-compose down
docker-compose up -d
```

### Database Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d

# Or manually:
docker-compose exec web rm /app/src/campus_hub.db
docker-compose exec web python -c "from src.models.database import init_database, seed_sample_data; init_database(); seed_sample_data()"
docker-compose restart
```

### Permission Errors

```bash
# If database permission errors occur
chmod 666 src/campus_hub.db

# If directory permission errors
sudo chown -R $USER:$USER .
```

### Health Check Failing

```bash
# Check if app is responding
docker-compose exec web curl http://localhost:5000/health

# Check Python errors
docker-compose exec web python run.py
```

### Memory/Performance Issues

```bash
# Check resource usage
docker stats campus-resource-hub

# Limit container resources in docker-compose.yml:
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

---

## Production Best Practices

### 1. Security

```yaml
# Use secrets for sensitive data
secrets:
  db_password:
    file: ./secrets/db_password.txt

services:
  web:
    secrets:
      - db_password
```

### 2. Logging

```yaml
services:
  web:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 3. Health Checks

Already configured in docker-compose.yml:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### 4. Backups

```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker cp campus-resource-hub:/app/src/campus_hub.db ./backups/db_$DATE.db
# Keep only last 7 days
find ./backups -name "db_*.db" -mtime +7 -delete
```

### 5. Monitoring

Consider adding:
- Prometheus for metrics
- Grafana for visualization
- Sentry for error tracking

---

## Multi-Stage Build (Optional)

For smaller production images:

```dockerfile
# Builder stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "run.py"]
```

---

## Kubernetes Deployment (Advanced)

For Kubernetes deployment, see:
- `k8s/deployment.yaml`
- `k8s/service.yaml`
- `k8s/ingress.yaml`

(Create these files based on your cluster requirements)

---

## Support and Resources

- **Docker Documentation**: https://docs.docker.com
- **Docker Compose**: https://docs.docker.com/compose
- **Flask Docker**: https://flask.palletsprojects.com/en/latest/deploying/docker/
- **Project Repository**: https://github.com/your-repo

---

## Quick Reference Card

```bash
# Start application
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f

# Rebuild after code changes
docker-compose up -d --build

# Access shell in container
docker-compose exec web bash

# Backup database
docker cp campus-resource-hub:/app/src/campus_hub.db ./backup.db

# Check health
curl http://localhost:5000/health

# Clean everything and restart fresh
docker-compose down -v && docker-compose up -d --build
```

---

**Document Version**: 1.0  
**Last Updated**: November 14, 2025  
**Docker Version**: 24.0+  
**Docker Compose Version**: 2.0+

