from django.test import TestCase
from django.contrib.auth.models import User
from apps.feed.models import Activity
from apps.books.models import Book, Genre


class ActivityModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.genre = Genre.objects.create(name="Fiction")
        self.book = Book.objects.create(
            title="Test Book", description="Test", genre=self.genre, added_by=self.user
        )

    def test_create_activity(self):
        activity = Activity.objects.create(
            user=self.user, activity_type="book_add",
            book=self.book, description="Added a new book"
        )
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.activity_type, "book_add")

    def test_activity_str(self):
        activity = Activity.objects.create(
            user=self.user, activity_type="reading_start", book=self.book
        )
        self.assertIn(self.user.username, str(activity))

    def test_activity_ordering(self):
        a1 = Activity.objects.create(
            user=self.user, activity_type="book_add", book=self.book
        )
        a2 = Activity.objects.create(
            user=self.user, activity_type="reading_start", book=self.book
        )
        activities = list(Activity.objects.all())
        self.assertEqual(activities[0], a2)
        self.assertEqual(activities[1], a1)
