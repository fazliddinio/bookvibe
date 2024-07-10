from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.books.models import Genre, Book, BookReview


class BooksListViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.genre = Genre.objects.create(name="Science Fiction")
        self.book = Book.objects.create(
            title="Test Book", description="Test description", genre=self.genre
        )

    def test_books_list_get(self):
        response = self.client.get(reverse("books:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Book")

    def test_books_list_search(self):
        response = self.client.get(reverse("books:list"), {"q": "Test"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Book")

    def test_books_list_genre_filter(self):
        response = self.client.get(
            reverse("books:list"), {"genre": str(self.genre.id)}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Book")


class BookDetailViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.book = Book.objects.create(title="Test Book", description="Test")

    def test_detail_view(self):
        response = self.client.get(
            reverse("books:detail", kwargs={"id": self.book.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Book")

    def test_nonexistent_book(self):
        response = self.client.get(
            reverse("books:detail", kwargs={"id": 99999})
        )
        self.assertEqual(response.status_code, 302)


class AddReviewViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.book = Book.objects.create(title="Test Book", description="Test")

    def test_add_review_requires_login(self):
        response = self.client.post(
            reverse("books:reviews", kwargs={"id": self.book.id}),
            {"stars_given": 4, "comment": "Great book!"}
        )
        self.assertEqual(response.status_code, 302)

    def test_add_review_authenticated(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("books:reviews", kwargs={"id": self.book.id}),
            {"stars_given": 4, "comment": "Great book!"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            BookReview.objects.filter(book=self.book, user=self.user).exists()
        )


class AddBookViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.genre = Genre.objects.create(name="Science Fiction")

    def test_add_book_requires_login(self):
        response = self.client.get(reverse("books:add-book"))
        self.assertEqual(response.status_code, 302)

    def test_add_book_post(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(reverse("books:add-book"), {
            "title": "New Book",
            "description": "New description",
            "genre": self.genre.id,
            "author_name": "John Doe",
            "isbn": "9781234567890"
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Book.objects.filter(title="New Book").exists())
