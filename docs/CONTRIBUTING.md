# Contributing

## Setup

```bash
git clone https://github.com/fazliddinio/bookvibe.git
cd bookvibe
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set DEBUG=True
python manage.py migrate
python manage.py test   # verify everything works
```

## Workflow

1. Create a branch: `git checkout -b feature/my-change`
2. Make changes
3. Run tests: `python manage.py test`
4. Commit with a clear message
5. Push and open a Pull Request

## Code Style

- Follow PEP 8
- Use Django ORM — no raw SQL
- Keep views thin, put logic in models or services
- Write tests for new features
- Use Django forms for all user input validation

## Commit Messages

Use clear, descriptive messages:

```
Add book search by ISBN
Fix login redirect for unauthenticated users
Remove unused email verification flow
```

## Tests

```bash
python manage.py test              # all
python manage.py test apps.books   # single app
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
