# Contributing to BookVibe

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to BookVibe. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if relevant**
- **Include your environment details** (OS, Python version, Django version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Explain why this enhancement would be useful**
- **List some examples of how it would be used**

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Make your changes** following the coding standards below
3. **Add tests** if you've added code that should be tested
4. **Ensure the test suite passes** (`python manage.py test`)
5. **Make sure your code lints** (`flake8`, `black`, `isort`)
6. **Update documentation** if needed
7. **Write a good commit message**

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/bookvibe.git
   cd bookvibe
   ```

2. Set up development environment:
   ```bash
   ./scripts/setup.sh
   ```

3. Create a branch:
   ```bash
   git checkout -b feature/my-new-feature
   ```

## Coding Standards

### Python Style Guide

We follow PEP 8 with some specific preferences:

- **Line length**: Maximum 100 characters
- **Imports**: Organized using `isort`
- **Formatting**: Use `black` for automatic formatting
- **Docstrings**: Google style

Example:
```python
def calculate_average_rating(reviews: list) -> float:
    """Calculate the average rating from a list of reviews.
    
    Args:
        reviews: List of review objects containing star ratings.
        
    Returns:
        The average rating as a float, or 0 if no reviews.
        
    Example:
        >>> reviews = [Review(stars_given=5), Review(stars_given=4)]
        >>> calculate_average_rating(reviews)
        4.5
    """
    if not reviews:
        return 0.0
    return sum(r.stars_given for r in reviews) / len(reviews)
```

### Django Best Practices

- **Models**: Keep business logic in models when possible
- **Views**: Keep views thin, move logic to services or utils
- **Templates**: Use template inheritance, avoid logic in templates
- **URLs**: Use meaningful URL names
- **Forms**: Use Django forms for validation

### Commit Messages

Follow the conventional commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(books): add book recommendation algorithm

Implemented collaborative filtering to suggest books based on
user reading history and ratings.

Closes #123
```

```
fix(auth): resolve login redirect issue

Fixed bug where users were redirected to wrong page after login
when accessing protected pages.

Fixes #456
```

## Testing

### Running Tests

```bash
# All tests
python manage.py test

# Specific app
python manage.py test apps.books

# With coverage
coverage run --source='.' manage.py test
coverage report
```

### Writing Tests

- Write tests for all new features
- Update tests when modifying existing features
- Aim for >80% code coverage
- Use descriptive test names

Example:
```python
class BookModelTest(TestCase):
    def test_average_rating_with_multiple_reviews(self):
        """Test that average rating is calculated correctly with multiple reviews."""
        book = Book.objects.create(title="Test Book")
        BookReview.objects.create(book=book, user=self.user1, stars_given=5)
        BookReview.objects.create(book=book, user=self.user2, stars_given=3)
        
        self.assertEqual(book.get_average_rating(), 4.0)
```

## Code Review Process

1. **Automated checks**: CI runs linting, tests, and security checks
2. **Peer review**: At least one maintainer reviews your PR
3. **Address feedback**: Make requested changes
4. **Approval & merge**: Once approved, your PR will be merged

## Documentation

- **Code comments**: Explain why, not what
- **Docstrings**: All public functions and classes
- **README**: Update if adding new features
- **LEARNING_GUIDE**: Add explanations for complex implementations

## Community

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on what's best for the community
- Show empathy towards others

### Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Discord**: (Coming soon) For real-time chat

## Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes
- Project documentation

Thank you for contributing to BookVibe! 🚀

