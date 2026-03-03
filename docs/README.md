# BookVibe — Detailed Documentation

Extended docs for the BookVibe project. For a quick overview, see the root [README.md](../README.md).

## Local Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis (optional — for Celery and caching)

### Steps

```bash
git clone https://github.com/fazliddinio/bookvibe.git
cd bookvibe
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set DEBUG=True
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Access:
- Site: http://localhost:8000
- Admin: http://localhost:8000/donut1024/
- API docs: http://localhost:8000/api/v1/schema/swagger-ui/

### Celery (optional)

```bash
celery -A bookvibe worker -l info
celery -A bookvibe beat -l info
```

## Docker Setup

```bash
cp .env.example .env   # edit values
docker compose --profile full up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py collectstatic --noinput
```

The `--profile full` flag starts PostgreSQL and Redis containers alongside the app. Without it, only the web, celery, and celery-beat containers start (useful when sharing a database from another project on the same VPS).

## Configuration

All config is via environment variables. See [`.env.example`](../.env.example) for the full list.

Key variables:

| Variable | Required in Prod | Description |
|----------|-----------------|-------------|
| `SECRET_KEY` | Yes | Django secret key. App refuses to start with the default in production. |
| `DEBUG` | No | Defaults to `False`. Set `True` for local dev. |
| `DB_PASSWORD` | Yes | PostgreSQL password. |
| `ALLOWED_HOSTS` | Yes | Comma-separated hostnames. |
| `CSRF_TRUSTED_ORIGINS` | Yes | Full URLs with scheme, e.g. `https://bookvibe.org` |

## API Reference

Base URL: `/api/v1/`

### Auth
- `POST /api/v1/token/` — JWT access + refresh tokens
- `POST /api/v1/token/refresh/` — refresh access token
- `POST /api/v1/token/verify/` — verify a token

### Books
- `GET /api/v1/books/` — list (search via `?search=`, filter via `?genre=`)
- `GET /api/v1/books/{id}/` — detail
- `POST /api/v1/books/{id}/add_review/` — submit review (authenticated)
- `GET /api/v1/books/{id}/reviews/` — list reviews for a book

### Genres / Authors
- `GET /api/v1/genres/` — all genres
- `GET /api/v1/authors/` — all authors
- `GET /api/v1/authors/{id}/books/` — books by author

### Users
- `GET /api/v1/users/me/` — current user profile
- `GET /api/v1/users/{id}/reviews/` — user's reviews

### Docs
- `GET /api/v1/schema/swagger-ui/` — Swagger UI
- `GET /api/v1/schema/redoc/` — ReDoc

Rate limits: 100 req/hour (anonymous), 1000 req/hour (authenticated).

## Testing

```bash
python manage.py test                # all (66 tests)
python manage.py test apps.books     # single app
python manage.py test apps.users     # auth tests

# with coverage
coverage run manage.py test && coverage report
```

## Project Structure

```
bookvibe/
├── apps/
│   ├── books/          # Book CRUD, reviews, search, external APIs
│   ├── users/          # Registration, login, profiles
│   ├── reading_lists/  # Reading shelves (Reading, To Read, Read)
│   ├── feed/           # Activity feed (home page)
│   ├── habits/         # Reading tracker with calendar
│   └── feedback/       # Feedback form
├── bookvibe/
│   ├── settings.py     # All config (reads .env)
│   ├── urls.py         # Root URLs
│   ├── api_urls.py     # REST API router
│   ├── celery.py       # Celery config
│   └── views.py        # Health check
├── templates/          # Base templates, allauth overrides
├── static/css/         # Stylesheets
├── nginx/              # Nginx reverse proxy config
├── scripts/            # setup.sh, deploy.sh
├── .github/workflows/  # CI/CD pipeline
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Other Docs

- [Deployment Guide](DEPLOYMENT_GUIDE.md) — VPS + Docker + CI/CD
- [Google OAuth Setup](GOOGLE_OAUTH_SETUP.md) — Google login configuration
- [Contributing](CONTRIBUTING.md) — How to contribute
- [License](LICENSE) — MIT

