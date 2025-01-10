# 🚀 BookVibe VPS Deployment Guide

Complete guide for deploying BookVibe to your VPS alongside your tech blog project.

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Initial VPS Setup](#initial-vps-setup)
4. [Nginx Configuration](#nginx-configuration)
5. [Deploy BookVibe](#deploy-bookvibe)
6. [GitHub Actions CI/CD](#github-actions-cicd)
7. [SSL Certificate Setup](#ssl-certificate-setup)
8. [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture Overview

Your VPS hosts **TWO projects**:

### Tech Blog (fazliddin.com)
- **Port**: 8000
- **Containers**: `web`, `db`, `redis`, `nginx`
- **Domains**: fazliddin.com, fazliddin.org
- **Network**: vps-network

### BookVibe (bookvibe.org)
- **Port**: 8080
- **Containers**: `bookvibe_web`, `bookvibe_celery`, `bookvibe_celery_beat`
- **Domain**: bookvibe.org
- **Network**: vps-network (shared)
- **Shared Services**: PostgreSQL, Redis (from tech blog)

### Shared Resources
- **PostgreSQL**: Used by both projects (different databases)
- **Redis**: Used by both projects (different DB numbers)
  - Tech Blog: Redis DB 0-1
  - BookVibe: Redis DB 2-3
- **Nginx**: Main reverse proxy (in tech blog project)
- **Network**: `vps-network` (external Docker network)

---

## ✅ Prerequisites

Before starting, ensure you have:

- [ ] VPS with tech blog already running
- [ ] Root or sudo access to VPS
- [ ] Docker and Docker Compose installed on VPS
- [ ] Domain `bookvibe.org` pointing to your VPS IP
- [ ] SSH access configured
- [ ] GitHub account with repository access

---

## 🔧 Initial VPS Setup

### 1. Create VPS Network (if not exists)

```bash
# SSH into your VPS
ssh user@45.80.181.236

# Check if vps-network exists
docker network ls | grep vps-network

# If not exists, create it
docker network create vps-network

# Verify tech blog is using this network
docker network inspect vps-network
```

### 2. Connect Tech Blog to VPS Network

If your tech blog isn't using the `vps-network` yet:

```bash
cd /path/to/tech-blog

# Update tech blog's docker-compose.yml
# Change network section to:
networks:
  vps-network:
    external: true

# Restart tech blog
docker-compose down
docker-compose up -d
```

### 3. Clone BookVibe Repository

```bash
cd /home/your-username
git clone https://github.com/your-username/bookvibe.git
cd bookvibe
```

### 4. Create Production Environment File

```bash
# Copy the production template
cp env.production .env

# Edit with your values
nano .env
```

**Important values to change:**
```bash
# MUST CHANGE
SECRET_KEY=<generate-new-one>
DB_PASSWORD=<same-as-tech-blog>
REDIS_PASSWORD=<same-as-tech-blog>
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<your-app-password>

# VPS specific
MOUNT_CODE=
WEB_PORT=8080
NETWORK_EXTERNAL=true
NETWORK_NAME=vps-network
DEBUG=False

# Database - use shared postgres
DB_NAME=bookvibe_prod
DB_USER=postgres
DB_PASSWORD=<tech-blog-db-password>
DB_HOST=db
DB_PORT=5432

# Redis - use shared redis (different DB numbers)
REDIS_URL=redis://:your-redis-password@redis:6379/2
CELERY_BROKER_URL=redis://:your-redis-password@redis:6379/2
CELERY_RESULT_BACKEND=redis://:your-redis-password@redis:6379/3

# Security
ALLOWED_HOSTS=localhost,127.0.0.1,bookvibe.org,www.bookvibe.org,45.80.181.236
CSRF_TRUSTED_ORIGINS=https://bookvibe.org,https://www.bookvibe.org
SITE_URL=https://bookvibe.org
```

---

## 🌐 Nginx Configuration

Update your **main nginx configuration** in the tech blog project.

### Location: `/path/to/tech-blog/nginx/nginx.conf`

Add this server block for BookVibe:

```nginx
# ========================================
# HTTP to HTTPS redirect for BookVibe
# ========================================
server {
    listen 80;
    server_name bookvibe.org www.bookvibe.org;
    return 301 https://$server_name$request_uri;
}

# ========================================
# HTTPS server block for BookVibe
# ========================================
server {
    listen 443 ssl http2;
    server_name bookvibe.org www.bookvibe.org;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/bookvibe.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bookvibe.org/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Static files (from BookVibe volumes)
    location /static/ {
        alias /var/lib/docker/volumes/bookvibe_static_volume/_data/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/lib/docker/volumes/bookvibe_media_volume/_data/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Main application (BookVibe on port 8080)
    location / {
        proxy_pass http://bookvibe_web:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Rate limiting
        limit_req zone=api burst=20 nodelay;
    }

    # Admin area
    location /admin/ {
        proxy_pass http://bookvibe_web:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Rate limiting for admin
        limit_req zone=login burst=5 nodelay;
    }

    # Health check endpoint
    location /health/ {
        proxy_pass http://bookvibe_web:8080;
        access_log off;
    }
}
```

### Reload Nginx

```bash
cd /path/to/tech-blog
docker-compose restart nginx

# Or if nginx is running directly on host:
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🚀 Deploy BookVibe

### 1. Create Database in Shared PostgreSQL

```bash
# Connect to postgres container
docker exec -it tech_blog_db psql -U postgres

# Create database for BookVibe
CREATE DATABASE bookvibe_prod;

# Grant permissions (if using same user)
GRANT ALL PRIVILEGES ON DATABASE bookvibe_prod TO postgres;

# Exit
\q
```

### 2. Build and Start BookVibe

```bash
cd /home/your-username/bookvibe

# Build the image
docker-compose build

# Start containers (without db/redis - using shared)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f bookvibe_web
```

### 3. Run Database Migrations

```bash
# Run migrations
docker-compose exec bookvibe_web python manage.py migrate

# Create superuser
docker-compose exec bookvibe_web python manage.py createsuperuser

# Collect static files (if not done)
docker-compose exec bookvibe_web python manage.py collectstatic --noinput
```

### 4. Verify Deployment

```bash
# Check all containers
docker ps

# Test health endpoint
curl http://localhost:8080/health/

# Check from outside
curl https://bookvibe.org/health/
```

---

## 🔄 GitHub Actions CI/CD

### 1. Add GitHub Secrets

Go to your repository: `Settings` → `Secrets and variables` → `Actions`

Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `VPS_HOST` | `45.80.181.236` | Your VPS IP address |
| `VPS_USERNAME` | `your-username` | SSH username |
| `VPS_SSH_KEY` | `<private-key>` | Your private SSH key |
| `VPS_PORT` | `22` | SSH port (default 22) |

### 2. Generate SSH Key (if needed)

On your local machine:

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions

# Copy public key to VPS
ssh-copy-id -i ~/.ssh/github_actions.pub user@45.80.181.236

# Copy private key for GitHub secret
cat ~/.ssh/github_actions
```

### 3. Configure GitHub Actions

The workflow file is already created at `.github/workflows/deploy.yml`.

It will automatically:
1. Run tests on every push to `main`
2. Build Docker image
3. Push to GitHub Container Registry
4. Deploy to VPS
5. Run health check

### 4. Trigger Deployment

```bash
# Push to main branch
git add .
git commit -m "Deploy to production"
git push origin main

# Or manually trigger from GitHub Actions tab
```

---

## 🔐 SSL Certificate Setup

### Get SSL Certificate for bookvibe.org

```bash
# Stop nginx temporarily
cd /path/to/tech-blog
docker-compose stop nginx

# Get certificate (on host or in certbot container)
sudo certbot certonly --standalone \
  -d bookvibe.org \
  -d www.bookvibe.org \
  --email your-email@example.com \
  --agree-tos

# Restart nginx
docker-compose start nginx

# Test auto-renewal
sudo certbot renew --dry-run
```

### Auto-Renewal with Cron

```bash
# Add to crontab
sudo crontab -e

# Add this line (runs daily at 3am)
0 3 * * * certbot renew --quiet && docker-compose -f /path/to/tech-blog/docker-compose.yml restart nginx
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs bookvibe_web

# Check if port is already in use
sudo lsof -i :8080

# Verify environment variables
docker-compose config
```

### Can't Connect to Database

```bash
# Check if postgres is running
docker ps | grep postgres

# Test connection
docker exec -it bookvibe_web python manage.py dbshell

# Check network connectivity
docker exec bookvibe_web ping db
```

### Can't Connect to Redis

```bash
# Check redis is running
docker ps | grep redis

# Test redis connection
docker exec -it bookvibe_web python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')
```

### Nginx Can't Reach BookVibe

```bash
# Check if containers are on same network
docker network inspect vps-network

# Verify bookvibe_web is listed

# Test from nginx container
docker exec -it nginx_container curl http://bookvibe_web:8080/health/
```

### Static Files Not Loading

```bash
# Collect static files again
docker-compose exec bookvibe_web python manage.py collectstatic --noinput --clear

# Check volume mount
docker volume ls
docker volume inspect bookvibe_static_volume

# Check nginx static alias path
docker exec nginx ls -la /var/lib/docker/volumes/bookvibe_static_volume/_data/
```

### GitHub Actions Failing

```bash
# Check secrets are set correctly
# Go to: Settings → Secrets and variables → Actions

# Test SSH connection locally
ssh -i ~/.ssh/github_actions user@45.80.181.236

# Check workflow logs in GitHub Actions tab
```

---

## 📊 Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f bookvibe_web

# Last 100 lines
docker-compose logs --tail=100 bookvibe_web
```

### Container Stats

```bash
# Real-time stats
docker stats

# Check disk usage
docker system df

# Clean up
docker system prune -a
```

---

## 🎉 Success Checklist

- [ ] VPS network created and shared
- [ ] BookVibe containers running
- [ ] Database migrations complete
- [ ] Admin user created
- [ ] HTTPS working (https://bookvibe.org)
- [ ] Health endpoint responding
- [ ] GitHub Actions deploying successfully
- [ ] Celery workers running
- [ ] Static files loading correctly
- [ ] Email sending working (test registration)

---

## 📞 Need Help?

- Check logs first: `docker-compose logs -f`
- Verify network: `docker network inspect vps-network`
- Test endpoints: `curl http://localhost:8080/health/`
- Review nginx config: `docker exec nginx nginx -t`

---

**Last Updated**: October 2025  
**Version**: 1.0

