# Changelog

## [1.1.0] - 2026-03-04

### Changed
- Simplified auth: direct signup/login with email + password (no email verification)
- Registration rejects duplicate emails instead of updating passwords

### Security
- Fixed critical account takeover vulnerability in registration
- `DEBUG` defaults to `False` — production safe without `.env`
- App crashes on startup if `SECRET_KEY` uses insecure default in production
- Added HSTS, secure cookies, proxy SSL header when `DEBUG=False`
- Rate limiting on login and registration (10 requests/minute per IP)
- Fixed open redirect in login `?next=` parameter
- Removed BrowsableAPIRenderer in production
- Changed Docker to use `expose` instead of `ports` for PostgreSQL and Redis
- Removed internal error details from health check endpoint

### Removed
- Email verification flow (views, URLs, templates, forms)
- Dead code across 12+ files
- `verify_email_code.html` template
- `PendingRegistration` admin registration

## [1.0.0] - 2024-10-07

### Added
- Book browsing, search, and discovery by title/author/genre
- Personal reading shelves (Reading, To Read, Read)
- Review system with 5-star ratings and comments
- Activity feed
- Reading habits tracker with calendar view
- REST API with JWT authentication
- Google OAuth login via django-allauth
- Background tasks with Celery + Redis
- Google Books and OpenLibrary API integration
- Docker deployment with PostgreSQL, Redis, Nginx
- GitHub Actions CI/CD pipeline
- Responsive UI with Bootstrap 5
