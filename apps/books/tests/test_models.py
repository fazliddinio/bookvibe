from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from apps.books.models import (
    Genre, Author, Book, BookAuthor, BookReview,
    ReviewComment, ReviewVote
)


class GenreModelTest(TestCase):

    def setUp(self):
        self.genre = Genre.objects.create(
            name="Science Fiction",
            description="Books about science and future",
            color="#FF5733"
        )

    def test_genre_creation(self):
        self.assertEqual(self.genre.name, "Science Fiction")
        self.assertTrue(self.genre.created_at)

    def test_genre_str(self):
        self.assertEqual(str(self.genre), "Science Fiction")

    def test_genre_ordering(self):
        Genre.objects.create(name="Fantasy")
        Genre.objects.create(name="Mystery")
        names = list(Genre.objects.values_list("name", flat=True))
        self.assertEqual(names, ["Fantasy", "Mystery", "Science Fiction"])

    def test_genre_unique_name(self):
        with self.assertRaises(Exception):
            Genre.objects.create(name="Science Fiction")


class AuthorModelTest(TestCase):

    def setUp(self):
        self.author = Author.objects.create(
            first_name="Isaac",
            last_name="Asimov",
            bio="Famous science fiction writer"
        )

    def test_author_str(self):
        self.assertEqual(str(self.author), "Asimov, Isaac")

    def test_author_full_name(self):
        self.assertEqual(self.author.full_name(), "Isaac Asimov")

    def test_author_unique_together(self):
        with self.assertRaises(Exception):
            Author.objects.create(first_name="Isaac", last_name="Asimov")


class BookModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.genre = Genre.objects.create(name="Science Fiction")
        self.author = Author.objects.create(first_name="Isaac", last_name="Asimov")
        self.book = Book.objects.create(
            title="Foundation",
            description="Epic tale of galactic empire",
            isbn="9780553293357",
            genre=self.genre,
            added_by=self.user,
            page_count=255
        )
        BookAuthor.objects.create(book=self.book, author=self.author, is_primary=True)

    def test_book_creation(self):
        self.assertEqual(self.book.title, "Foundation")
        self.assertEqual(self.book.genre, self.genre)
        self.assertTrue(self.book.is_available)

    def test_book_str(self):
        self.assertEqual(str(self.book), "Foundation")

    def test_get_authors(self):
        authors = self.book.get_authors()
        self.assertEqual(len(authors), 1)
        self.assertEqual(authors[0], self.author)

    def test_average_rating_no_reviews(self):
        self.assertEqual(self.book.get_average_rating(), 0)

    def test_average_rating_with_reviews(self):
        BookReview.objects.create(book=self.book, user=self.user, stars_given=4, comment="Great")
        user2 = User.objects.create_user(username="user2", email="u2@test.com")
        BookReview.objects.create(book=self.book, user=user2, stars_given=5, comment="Excellent")
        self.assertEqual(self.book.get_average_rating(), 4.5)


class BookReviewModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="reviewer", email="rev@test.com", password="pass123"
        )
        self.book = Book.objects.create(title="Test Book", description="Test")
        self.review = BookReview.objects.create(
            book=self.book, user=self.user, stars_given=4,
            comment="Great book with interesting plot!"
        )

    def test_review_creation(self):
        self.assertEqual(self.review.stars_given, 4)
        self.assertTrue(self.review.is_approved)

    def test_review_str(self):
        expected = f"{self.user.username}'s review of {self.book.title}"
        self.assertEqual(str(self.review), expected)

    def test_stars_validation(self):
        review = BookReview(
            book=self.book, user=self.user, stars_given=6, comment="Test"
        )
        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_unique_review_per_user(self):
        with self.assertRaises(Exception):
            BookReview.objects.create(
                book=self.book, user=self.user, stars_given=5, comment="Again"
            )

    def test_likes_count(self):
        self.assertEqual(self.review.get_likes_count(), 0)
        user2 = User.objects.create_user(username="voter", email="v@test.com")
        ReviewVote.objects.create(review=self.review, user=user2, vote_type="like")
        self.assertEqual(self.review.get_likes_count(), 1)

    def test_comments_count(self):
        self.assertEqual(self.review.get_comments_count(), 0)
        user2 = User.objects.create_user(username="commenter", email="c@test.com")
        ReviewComment.objects.create(review=self.review, user=user2, content="Nice!")
        self.assertEqual(self.review.get_comments_count(), 1)
