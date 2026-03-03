# Deployment Guide

How BookVibe is deployed to a VPS with Docker and GitHub Actions CI/CD.

## Architecture

BookVibe runs on a VPS alongside a separate tech blog project. They share PostgreSQL and Redis but have independent Docker containers.

| Service | Container | Port |
|---------|-----------|------|
| Django (Gunicorn) | `bookvibe_web` | 8080 |
| Celery Worker | `bookvibe_celery` | — |
| Celery Beat | `bookvibe_celery_beat` | — |
| PostgreSQL | shared from host | 5432 |
| Redis | shared from host | 6379 |

Nginx runs on the host and reverse-proxies to the Docker container. SSL is handled by Let's Encrypt (certbot).

## Prerequisites

- VPS with Docker and Docker Compose v2
- Domain pointing to your VPS IP
- SSH access
- GitHub repository with Actions enabled

## Initial Setup

### 1. Clone on VPS

```bash
cd /var/www
git clone https://github.com/fazliddinio/bookvibe.git
cd bookvibe
```

### 2. Create `.env`

```bash
cp .env.example .env
nano .env
```

Set production values:

```bash
SECRET_KEY=<generate-a-random-50-char-string>
DEBUG=False
ALLOWED_HOSTS=bookvibe.org,www.bookvibe.org

DB_NAME=bookvibe_prod
DB_USER=postgres
DB_PASSWORD=<your-db-password>
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/2
CELERY_BROKER_URL=redis://redis:6379/2
CELERY_RESULT_BACKEND=redis://redis:6379/3

CSRF_TRUSTED_ORIGINS=https://bookvibe.org,https://www.bookvibe.org
CORS_ALLOWED_ORIGINS=https://bookvibe.org
SITE_URL=https://bookvibe.org
SECURE_SSL_REDIRECT=True

MOUNT_CODE=
WEB_PORT=8080
NETWORK_EXTERNAL=true
NETWORK_NAME=vps-network
```

### 3. Create shared Docker network (if not exists)

```bash
docker network create vps-network
```

### 4. Create database

```bash
docker exec -it <postgres-container> psql -U postgres -c "CREATE DATABASE bookvibe_prod;"
```

### 5. Build and start

```bash
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py collectstatic --noinput
```

### 6. Verify

```bash
curl http://localhost:8080/health/
```

## Nginx Configuration

Add a server block for bookvibe.org in your main nginx config:

```nginx
server {
    listen 80;
    server_name bookvibe.org www.bookvibe.org;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bookvibe.org www.bookvibe.org;

    ssl_certificate /etc/letsencrypt/live/bookvibe.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bookvibe.org/privkey.pem;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    location /static/ {
        alias /var/lib/docker/volumes/bookvibe_static_volume/_data/;
        expires 30d;
    }

    location /media/ {
        alias /var/lib/docker/volumes/bookvibe_media_volume/_data/;
        expires 7d;
    }

    location / {
        proxy_pass http://bookvibe_web:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## SSL Certificate

```bash
sudo certbot certonly --standalone -d bookvibe.org -d www.bookvibe.org
```

Auto-renewal via cron:

```bash
0 3 * * * certbot renew --quiet && systemctl reload nginx
```

## CI/CD (GitHub Actions)

The pipeline is at `.github/workflows/deploy.yml`. On push to `main`:

1. **Test job** — runs Django tests with PostgreSQL and Redis
2. **Deploy job** — SSHs into VPS, pulls code, rebuilds Docker, runs migrations

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `VPS_HOST` | VPS IP address |
| `VPS_USERNAME` | SSH user (e.g. `root`) |
| `VPS_SSH_KEY` | Private SSH key (ed25519) |

### Manual deploy

```bash
ssh root@<your-vps> "cd /var/www/bookvibe && git pull && docker compose up -d --build && docker compose exec web python manage.py migrate && docker compose exec web python manage.py collectstatic --noinput"
```

## Troubleshooting

**Container won't start:**
```bash
docker compose logs web
```

**Static files returning 403:**
```bash
chmod o+x /var/lib/docker/ /var/lib/docker/volumes/
```

**Database connection refused:**
```bash
docker network inspect vps-network   # verify containers are on same network
```

**Health check:**
```bash
curl https://bookvibe.org/health/
```
