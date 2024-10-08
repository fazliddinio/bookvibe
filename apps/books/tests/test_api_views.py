from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from apps.books.models import Genre, Book, BookReview


class BookAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.genre = Genre.objects.create(name="Science Fiction")
        self.book = Book.objects.create(
            title="Test Book", description="Test description",
            genre=self.genre, added_by=self.user
        )

    def test_list_books(self):
        response = self.client.get("/api/v1/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)

    def test_book_detail(self):
        response = self.client.get(f"/api/v1/books/{self.book.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Book")

    def test_create_book_requires_auth(self):
        response = self.client.post("/api/v1/books/", {
            "title": "New Book", "description": "Desc", "genre": self.genre.id
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_book_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/v1/books/", {
            "title": "New Book", "description": "Desc",
            "genre": self.genre.id, "language": "English", "is_available": True
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_search_books(self):
        response = self.client.get("/api/v1/books/?search=Test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BookReviewAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="reviewer", email="rev@test.com", password="testpass123"
        )
        self.book = Book.objects.create(title="Test Book", description="Test")
        self.review = BookReview.objects.create(
            book=self.book, user=self.user, stars_given=4, comment="Great book!"
        )

    def test_list_reviews(self):
        response = self.client.get("/api/v1/reviews/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_review_requires_auth(self):
        response = self.client.post(
            f"/api/v1/books/{self.book.id}/add_review/",
            {"stars_given": 5, "comment": "Excellent!"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
