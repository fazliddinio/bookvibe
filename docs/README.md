# BookVibe

A book review and discovery platform built with Django. Track your reading habits, write reviews, and find new books.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- Browse and search books by title, author, or genre
- Organize books into personal reading shelves (Reading, To Read, Read)
- Write reviews with 5-star ratings, comment on others' reviews
- Activity feed to see what others are reading
- Reading habits tracker with calendar view
- RESTful API with JWT auth (Django REST Framework)
- Google OAuth login via django-allauth
- Background tasks with Celery + Redis
- Book data from Google Books and OpenLibrary APIs
- AI-powered recommendations (OpenAI/Cohere, optional)

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (or SQLite for development)
- Redis (optional, for caching and Celery)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/bookvibe.git
   cd bookvibe
   ```

2. **Run the setup script**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

3. **Start the development server**
   ```bash
   source venv/bin/activate
   python manage.py runserver
   ```

4. **Access the application**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin/
   - API docs: http://localhost:8000/api/v1/docs/

### Docker Setup

1. **Copy environment template**
   ```bash
   cp env_template.md .env
   # Edit .env with your configuration
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## Project Structure

```
bookvibe/
├── apps/
│   ├── books/          # Book models, views, API, services
│   ├── users/          # Auth, profiles, email verification
│   ├── reading_lists/  # Personal reading shelves
│   ├── feed/           # Activity feed
│   ├── habits/         # Reading tracker & calendar
│   └── feedback/       # User feedback
├── bookvibe/           # Django settings, URLs, Celery config
├── templates/          # HTML templates
├── static/             # CSS, images
├── scripts/            # Setup & deploy scripts
├── nginx/              # Nginx config
└── docker-compose.yml
```

## Tech Stack

- **Backend:** Django 4.2, DRF, Celery
- **Database:** PostgreSQL 15, Redis
- **Auth:** Django Allauth (Google OAuth) + JWT
- **Frontend:** Bootstrap 5, Font Awesome
- **Deploy:** Docker, Nginx, Gunicorn, GitHub Actions

## Configuration

Key environment variables (see `env_template.md` for full list):

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

# Database
DB_NAME=bookvibe_db
DB_USER=bookvibe_user
DB_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## API

Main endpoints:
- `GET /api/v1/books/` — list/search books
- `POST /api/v1/books/{id}/reviews/` — add review
- `GET /api/v1/users/profile/` — current user profile
- `POST /api/v1/auth/token/` — get JWT token

## Tests

```bash
python manage.py test
python manage.py test apps.books  # single app
```

## Deployment

```bash
# Docker
./scripts/deploy.sh production
docker-compose logs -f web
```

Or manually:
```bash
python manage.py migrate
python manage.py collectstatic
gunicorn bookvibe.wsgi:application
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for full instructions.

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Development Guidelines:**
- Follow PEP 8 style guide
- Write tests for new features
- Update documentation as needed
- Keep commits atomic and well-described

## License

MIT — see [LICENSE](LICENSE) for details.

---

Built by Fazliddin

