from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from apps.habits.models import ReadingHabit, UserInterest


class ReadingHabitModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_create_habit(self):
        habit = ReadingHabit.objects.create(
            user=self.user, date=date.today(),
            pages_read=50, minutes_read=60, completed=True
        )
        self.assertEqual(habit.pages_read, 50)
        self.assertTrue(habit.completed)

    def test_habit_str(self):
        habit = ReadingHabit.objects.create(
            user=self.user, date=date.today(), completed=True
        )
        self.assertIn(self.user.username, str(habit))

    def test_unique_per_date(self):
        ReadingHabit.objects.create(user=self.user, date=date.today())
        with self.assertRaises(Exception):
            ReadingHabit.objects.create(user=self.user, date=date.today())

    def test_default_values(self):
        habit = ReadingHabit.objects.create(user=self.user)
        self.assertEqual(habit.pages_read, 0)
        self.assertFalse(habit.completed)


class UserInterestModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_create_interest(self):
        interest = UserInterest.objects.create(
            user=self.user,
            preferred_genres=["Fiction", "Mystery"],
            reading_preferences="I like fast-paced books"
        )
        self.assertEqual(len(interest.preferred_genres), 2)

    def test_one_to_one(self):
        UserInterest.objects.create(user=self.user)
        with self.assertRaises(Exception):
            UserInterest.objects.create(user=self.user)
