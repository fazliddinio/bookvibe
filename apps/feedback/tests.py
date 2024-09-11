from django.test import TestCase
from django.contrib.auth.models import User
from apps.feedback.models import Feedback


class FeedbackModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_create_feedback(self):
        feedback = Feedback.objects.create(
            user=self.user, feedback_type="bug",
            message="This is a test bug report"
        )
        self.assertEqual(feedback.feedback_type, "bug")
        self.assertFalse(feedback.is_read)

    def test_anonymous_feedback(self):
        feedback = Feedback.objects.create(
            name="Anonymous", email="anon@example.com",
            feedback_type="feature", message="I would like a new feature"
        )
        self.assertIsNone(feedback.user)

    def test_feedback_str(self):
        feedback = Feedback.objects.create(
            user=self.user, feedback_type="general", message="Test"
        )
        self.assertIn(self.user.username, str(feedback))

    def test_short_message(self):
        feedback = Feedback.objects.create(user=self.user, message="x" * 150)
        self.assertTrue(feedback.get_short_message().endswith("..."))
        self.assertEqual(len(feedback.get_short_message()), 103)
