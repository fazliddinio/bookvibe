# 📚 BookVibe

A modern book review and discovery platform built with Django. Track your reading, share reviews, and discover your next favorite book.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📖 Complete Tutorial Available!

**Want to learn how everything works?** Check out our comprehensive 3-part tutorial:

👉 **[Start Learning: Tutorial Index](./TUTORIAL_INDEX.md)** 👈

This isn't just documentation—it's a complete book that teaches you:
- ✅ Django from basics to advanced
- ✅ Building production-ready applications
- ✅ Testing, deployment, and best practices
- ✅ **200+ pages** of detailed explanations with code examples

Perfect for beginners and experienced developers alike!

## ✨ Features

### Core Functionality
- **Book Discovery**: Browse and search thousands of books by title, author, or genre
- **Personal Library**: Organize books into Reading, To Read, and Read shelves
- **Reviews & Ratings**: Share your thoughts with 5-star ratings and detailed reviews
- **Social Features**: Comment on reviews, vote helpful, and engage with the community
- **User Profiles**: Customize your profile with bio and reading stats

### Technical Features
- **RESTful API**: Full API support with JWT authentication
- **Real-time Search**: Fast book search with PostgreSQL full-text search
- **Async Operations**: Celery for background tasks and email notifications
- **Caching**: Redis-based caching for improved performance
- **External APIs**: Integration with Google Books and OpenLibrary
- **AI Features**: Book recommendations and review analysis (optional)

## 🚀 Quick Start

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

### Docker Setup (Recommended for Production)

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

## 📋 Project Structure

```
bookvibe/
├── apps/
│   ├── books/          # Book management and reviews
│   ├── users/          # User authentication and profiles
│   ├── reading_lists/  # Personal reading shelves
│   └── feedback/       # User feedback system
├── bookvibe/           # Project settings
├── static/             # Static files (CSS, JS, images)
├── templates/          # HTML templates
├── scripts/            # Deployment and setup scripts
├── nginx/              # Nginx configuration
└── requirements.txt    # Python dependencies
```

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 4.2
- **Database**: PostgreSQL 15
- **Cache**: Redis
- **Task Queue**: Celery + Redis
- **API**: Django REST Framework
- **Authentication**: Django Allauth + JWT

### Frontend
- **CSS Framework**: Bootstrap 5
- **Icons**: Font Awesome
- **Fonts**: Inter, Playfair Display

### DevOps
- **Containerization**: Docker
- **Web Server**: Nginx
- **WSGI Server**: Gunicorn
- **CI/CD**: GitHub Actions

## 🔧 Configuration

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

## 📚 API Documentation

The project includes a full RESTful API with Swagger documentation.

**Endpoints:**
- `/api/v1/books/` - Book CRUD operations
- `/api/v1/reviews/` - Review management
- `/api/v1/users/` - User profiles
- `/api/v1/auth/token/` - JWT authentication

**API Docs:** http://localhost:8000/api/v1/docs/

## 🧪 Testing

Run tests with coverage:
```bash
python manage.py test
```

Run specific app tests:
```bash
python manage.py test apps.books
```

## 🚢 Deployment

### Using Docker (Recommended)

```bash
# Production deployment
./scripts/deploy.sh production

# Check logs
docker-compose logs -f web
```

### Manual Deployment

1. Set up PostgreSQL and Redis
2. Configure environment variables
3. Run migrations: `python manage.py migrate`
4. Collect static files: `python manage.py collectstatic`
5. Start with Gunicorn: `gunicorn bookvibe.wsgi:application`

### Environment-Specific Guides
- See `QUICKSTART.md` for detailed local setup
- See `DEPLOYMENT.md` for production deployment (coming soon)

## 🤝 Contributing

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

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django community for the amazing framework
- Google Books API for book data
- OpenLibrary for additional book information
- All contributors who have helped shape this project

## 📧 Contact

**Fazliddin** - Project Maintainer

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

## 🗺️ Roadmap

- [ ] Mobile app (React Native)
- [ ] Book clubs and group reading lists
- [ ] Reading challenges and achievements
- [ ] Integration with Goodreads
- [ ] Advanced recommendation engine
- [ ] Multi-language support

---

**Built with ❤️ by Fazliddin**

*Happy Reading!* 📖

