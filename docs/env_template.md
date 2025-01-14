# Environment Variables Template

Copy this file to `.env` in your project root and fill in the values.

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database (PostgreSQL)
DB_NAME=bookvibe_db
DB_USER=bookvibe_user
DB_PASSWORD=bookvibe_password
DB_HOST=localhost
DB_PORT=5432

# Redis (for caching and Celery)
REDIS_URL=redis://127.0.0.1:6379/1

# Celery
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=django-db
CELERY_TASK_ALWAYS_EAGER=False

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@bookvibe.com

# Site Configuration
SITE_URL=http://localhost:8000

# Django Allauth
ACCOUNT_EMAIL_VERIFICATION=optional

# Google OAuth (optional)
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret

# External APIs
# Google Books API (FREE - Get key: https://console.cloud.google.com/apis/credentials)
GOOGLE_BOOKS_API_KEY=your-google-books-api-key

# AI APIs (All have FREE tiers)
# OpenAI (GPT-3.5/GPT-4) - Get key: https://platform.openai.com/api-keys
OPENAI_API_KEY=your-openai-api-key

# Cohere AI (FREE tier) - Get key: https://dashboard.cohere.com/api-keys
COHERE_API_KEY=your-cohere-api-key

# Anthropic Claude (FREE tier) - Get key: https://console.anthropic.com/
ANTHROPIC_API_KEY=your-anthropic-api-key

# Monitoring & Error Tracking
# Sentry (optional, for production) - Get DSN: https://sentry.io/
SENTRY_DSN=your-sentry-dsn
```

