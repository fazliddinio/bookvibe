#!/bin/bash

# BookVibe Local Development Setup Script
# This script sets up your local development environment

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

echo "======================================"
echo "  BookVibe Development Setup"
echo "======================================"
echo ""

# Check Python version
log_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed!"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
log_success "Python $PYTHON_VERSION found"

# Create virtual environment
if [ ! -d "venv" ]; then
    log_info "Creating virtual environment..."
    python3 -m venv venv
    log_success "Virtual environment created"
else
    log_info "Virtual environment already exists"
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
log_info "Upgrading pip..."
pip install --upgrade pip

# Install requirements
log_info "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    log_info "Creating .env file from template..."
    cat > .env << EOF
# Django Settings
SECRET_KEY=django-insecure-$(openssl rand -base64 32)
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Settings (PostgreSQL)
DB_NAME=bookvibe_db
DB_USER=bookvibe_user
DB_PASSWORD=bookvibe_password
DB_HOST=localhost
DB_PORT=5432

# Email Settings (Console backend for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@bookvibe.com
SITE_URL=http://localhost:8000

# Celery Settings
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=django-db
CELERY_TASK_ALWAYS_EAGER=True

# External API Keys (Optional)
GOOGLE_BOOKS_API_KEY=
OPENAI_API_KEY=
COHERE_API_KEY=
ANTHROPIC_API_KEY=

# Social Auth (Optional - Google OAuth)
# GOOGLE_OAUTH_CLIENT_ID=
# GOOGLE_OAUTH_CLIENT_SECRET=
EOF
    log_success ".env file created"
    log_warning "Please update .env file with your configuration"
else
    log_info ".env file already exists"
fi

# Create logs directory
mkdir -p logs
touch logs/django.log

# Database setup prompt
echo ""
log_info "Database Setup Options:"
echo "1. Use SQLite (Simple, no setup required)"
echo "2. Use PostgreSQL (Recommended for production-like environment)"
read -p "Choose option (1 or 2): " db_choice

if [ "$db_choice" == "1" ]; then
    log_info "Configuring SQLite..."
    # Update settings for SQLite
    cat >> .env << EOF

# Using SQLite for development
DATABASE_ENGINE=django.db.backends.sqlite3
EOF
    log_success "SQLite configured"
elif [ "$db_choice" == "2" ]; then
    log_info "PostgreSQL selected. Make sure PostgreSQL is installed and running."
    log_info "Creating database..."
    
    # Try to create database
    psql -U postgres -c "CREATE DATABASE bookvibe_db;" 2>/dev/null || log_warning "Database might already exist"
    psql -U postgres -c "CREATE USER bookvibe_user WITH PASSWORD 'bookvibe_password';" 2>/dev/null || log_warning "User might already exist"
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE bookvibe_db TO bookvibe_user;" 2>/dev/null || true
    
    log_info "PostgreSQL database setup attempted"
fi

# Run migrations
log_info "Running database migrations..."
python manage.py migrate

# Create superuser
log_info "Creating superuser..."
echo "You'll be prompted to create an admin user."
python manage.py createsuperuser

# Collect static files
log_info "Collecting static files..."
python manage.py collectstatic --noinput

# Load sample data (optional)
read -p "Would you like to load sample data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Loading sample genres..."
    python manage.py shell << EOF
from apps.books.models import Genre

genres = [
    'Fiction', 'Non-Fiction', 'Mystery', 'Thriller', 'Romance',
    'Science Fiction', 'Fantasy', 'Biography', 'History', 'Self-Help',
    'Poetry', 'Horror', 'Adventure', 'Young Adult', 'Children'
]

for genre_name in genres:
    Genre.objects.get_or_create(name=genre_name, defaults={'description': f'{genre_name} books'})

print(f"Created {len(genres)} genres")
EOF
    log_success "Sample data loaded"
fi

echo ""
log_success "Setup completed successfully!"
echo ""
echo "======================================"
echo "  Next Steps:"
echo "======================================"
echo "1. Review and update .env file if needed"
echo "2. Start the development server:"
echo "   python manage.py runserver"
echo ""
echo "3. Access the application:"
echo "   - Main site: http://localhost:8000"
echo "   - Admin panel: http://localhost:8000/admin/"
echo "   - API docs: http://localhost:8000/api/v1/docs/"
echo ""
echo "4. For background tasks, run Celery worker (optional):"
echo "   celery -A bookvibe worker -l info"
echo "======================================"

