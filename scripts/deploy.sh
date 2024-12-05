#!/bin/bash

# BookVibe Production Deployment Script
# Usage: ./scripts/deploy.sh [environment]

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if environment argument is provided
ENV=${1:-production}

log_info "Starting deployment for environment: $ENV"

# Check if .env file exists
if [ ! -f .env ]; then
    log_error ".env file not found!"
    log_info "Creating .env from template..."
    cp env_template.md .env
    log_warning "Please update .env file with your configuration before proceeding."
    exit 1
fi

# Pull latest changes
log_info "Pulling latest changes from Git..."
git pull origin main

# Build and start containers
log_info "Building Docker containers..."
docker-compose build --no-cache

log_info "Starting containers..."
docker-compose down
docker-compose up -d

# Wait for services to be healthy
log_info "Waiting for services to be ready..."
sleep 10

# Run migrations
log_info "Running database migrations..."
docker-compose exec -T web python manage.py migrate

# Collect static files
log_info "Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Create superuser if needed (skip if exists)
log_info "Checking for superuser..."
docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(is_superuser=True).exists():
    print('No superuser found. Please create one manually.');
else:
    print('Superuser exists.');
" || log_warning "Could not check superuser status"

# Health check
log_info "Performing health check..."
if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    log_success "Health check passed!"
else
    log_error "Health check failed!"
    log_info "Checking container logs..."
    docker-compose logs --tail=50 web
    exit 1
fi

# Show running containers
log_info "Running containers:"
docker-compose ps

log_success "Deployment completed successfully!"
log_info "Application is running at http://localhost:8000"
log_info "Admin panel: http://localhost:8000/admin/"
log_info "API documentation: http://localhost:8000/api/v1/docs/"

# Optional: Show logs
read -p "Would you like to view application logs? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose logs -f web
fi

