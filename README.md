# BookVibe

A book review and discovery platform built with Django. Track your reading habits, write reviews, and find new books.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- Browse and search books by title, author, or genre
- Organize books into personal reading shelves (Reading, To Read, Read)
- Write reviews with 5-star ratings, comment on others' reviews
- Activity feed showing what others are reading
- Reading habits tracker with calendar view
- REST API with JWT authentication
- Google OAuth login via django-allauth
- Background tasks with Celery + Redis

## Quick Start

```bash
git clone https://github.com/fazliddinio/bookvibe.git
cd bookvibe
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit with your values
python manage.py migrate
python manage.py runserver
```

Access at http://localhost:8000

## Docker

```bash
cp .env.example .env  # edit with your values
docker compose --profile full up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## Tech Stack

- **Backend:** Django 5.2, Django REST Framework, Celery
- **Database:** PostgreSQL 15, Redis 7
- **Auth:** django-allauth (Google OAuth) + JWT
- **Frontend:** Bootstrap 5, Font Awesome
- **Deploy:** Docker, Nginx, Gunicorn, GitHub Actions CI/CD

## Project Structure

```
bookvibe/
├── apps/
│   ├── books/          # Book models, views, API, search
│   ├── users/          # Auth, profiles
│   ├── reading_lists/  # Personal reading shelves
│   ├── feed/           # Activity feed (home page)
│   ├── habits/         # Reading tracker & calendar
│   └── feedback/       # User feedback
├── bookvibe/           # Settings, URLs, Celery config
├── templates/          # HTML templates
├── static/             # CSS, images
├── nginx/              # Nginx config
└── docker-compose.yml
```

## API

Endpoints at `/api/v1/`:
- `GET /api/v1/books/` — list/search books
- `POST /api/v1/books/{id}/add_review/` — add review
- `GET /api/v1/users/me/` — current user profile
- `POST /api/v1/token/` — get JWT token
- `GET /api/v1/schema/swagger-ui/` — interactive API docs

## Tests

```bash
python manage.py test              # all tests
python manage.py test apps.books   # single app
```

## Docs

See the [docs/](docs/) folder for:
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)
- [Google OAuth Setup](docs/GOOGLE_OAUTH_SETUP.md)
- [Contributing](docs/CONTRIBUTING.md)

## License

MIT — see [docs/LICENSE](docs/LICENSE)

---

Built by [Fazliddin](https://github.com/fazliddinio)
