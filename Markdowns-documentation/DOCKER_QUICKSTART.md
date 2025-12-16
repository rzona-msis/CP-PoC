# Docker Quick Start Guide

Get Campus Resource Hub running with Docker in 5 minutes!

## Prerequisites

- Docker Desktop installed ([Download here](https://www.docker.com/get-started))
- Git (to clone the repository)

## Quick Start (3 Commands)

```bash
# 1. Copy environment file
cp env.example .env

# 2. Build and start the container
docker-compose up -d

# 3. Open your browser
# Navigate to: http://localhost:5000
```

That's it! 🎉

## Default Login Accounts

- **Admin**: admin@university.edu / admin123
- **Staff**: sjohnson@university.edu / staff123  
- **Student**: asmith@university.edu / student123

## Common Commands

```bash
# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Restart after code changes
docker-compose up -d --build

# Access container shell
docker-compose exec web bash
```

## Troubleshooting

### Port already in use?
```bash
# Change port in docker-compose.yml
ports:
  - "8080:5000"  # Use 8080 instead of 5000
```

### Container won't start?
```bash
# Check logs
docker-compose logs web

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

## Next Steps

- See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for detailed configuration
- Configure environment variables in `.env`
- Set up Google Gemini API for AI features
- Configure email settings for notifications

## Development Mode

For development with hot reload:

```bash
docker-compose -f docker-compose.dev.yml up
```

---

**Need help?** See the full [Docker Deployment Guide](DOCKER_DEPLOYMENT.md)

