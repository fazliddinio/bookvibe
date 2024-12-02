# ========================================
# Multi-stage Production Dockerfile for BookVibe
# Optimized for VPS deployment
# ========================================

# Builder stage - compile dependencies
FROM python:3.11-slim as builder

# Set build-time environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ========================================
# Production stage - minimal runtime image
# ========================================
FROM python:3.11-slim

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=bookvibe.settings \
    PORT=8080

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R appuser:appuser /app

# Copy application code with proper ownership
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Collect static files (fails gracefully if settings aren't ready)
RUN python manage.py collectstatic --noinput --clear || true

# Expose port 8080 (BookVibe's designated port on VPS)
EXPOSE 8080

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health/ || exit 1

# Production startup command
CMD ["sh", "-c", "\
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput --clear && \
    gunicorn bookvibe.wsgi:application \
        --bind 0.0.0.0:8080 \
        --workers 3 \
        --threads 2 \
        --worker-class sync \
        --worker-tmp-dir /dev/shm \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --timeout 120 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
    "]

