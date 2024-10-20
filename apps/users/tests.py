from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from apps.users.models import UserProfile, PendingRegistration
from unittest.mock import patch
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


class BaseAuthTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.site = Site.objects.get_or_create(
            id=1, defaults={"domain": "testserver", "name": "Test Server"}
        )[0]
        cls.google_app = SocialApp.objects.create(
            provider="google", name="Google",
            client_id="test-client-id", secret="test-secret",
        )
        cls.google_app.sites.add(cls.site)


class RegistrationTestCase(BaseAuthTestCase):

    def setUp(self):
        self.client = Client()
        self.register_url = reverse("users:register")

    def test_registration_page_loads(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)

    @patch("apps.users.utils.send_email_with_fallback")
    def test_successful_registration(self, mock_send_email):
        mock_send_email.return_value = True
        response = self.client.post(self.register_url, {
            "username": "test@example.com",
            "email": "test@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
        })
        self.assertEqual(response.status_code, 302)
        pending = PendingRegistration.objects.filter(email="test@example.com").first()
        self.assertIsNotNone(pending)
        self.assertFalse(User.objects.filter(email="test@example.com").exists())

    def test_registration_password_mismatch(self):
        response = self.client.post(self.register_url, {
            "username": "test@example.com",
            "email": "test@example.com",
            "password1": "testpass123",
            "password2": "differentpassword",
        })
        self.assertEqual(response.status_code, 200)


class EmailVerificationTestCase(BaseAuthTestCase):

    def setUp(self):
        self.client = Client()
        self.verify_url = reverse("users:verify_email_code")

    def test_successful_verification(self):
        pending = PendingRegistration.create_pending("test@example.com", "testpass123")
        response = self.client.post(self.verify_url, {
            "verification_code": pending.verification_code,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())
        self.assertFalse(
            PendingRegistration.objects.filter(email="test@example.com").exists()
        )

    def test_wrong_code(self):
        PendingRegistration.create_pending("test@example.com", "testpass123")
        response = self.client.post(self.verify_url, {
            "verification_code": "999999",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="test@example.com").exists())

    def test_expired_code(self):
        pending = PendingRegistration.create_pending("test@example.com", "testpass123")
        pending.expires_at = timezone.now() - timedelta(minutes=11)
        pending.save()
        response = self.client.post(self.verify_url, {
            "verification_code": pending.verification_code,
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(email="test@example.com").exists())


class LoginTestCase(BaseAuthTestCase):

    def setUp(self):
        self.client = Client()
        self.login_url = reverse("users:login")
        self.user = User.objects.create_user(
            username="test@example.com", email="test@example.com",
            password="testpass123",
        )
        UserProfile.objects.create(user=self.user, is_email_verified=True)

    def test_login_page_loads(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_successful_login(self):
        response = self.client.post(self.login_url, {
            "email": "test@example.com", "password": "testpass123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_wrong_password(self):
        response = self.client.post(self.login_url, {
            "email": "test@example.com", "password": "wrongpass",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class LogoutTestCase(BaseAuthTestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test@example.com", email="test@example.com",
            password="testpass123",
        )
        UserProfile.objects.create(user=self.user, is_email_verified=True)
        self.client.login(username="test@example.com", password="testpass123")

    def test_logout(self):
        response = self.client.get(reverse("users:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class ProfileTestCase(BaseAuthTestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test@example.com", email="test@example.com",
            password="testpass123",
        )
        self.profile = UserProfile.objects.create(user=self.user, is_email_verified=True)
        self.client.login(username="test@example.com", password="testpass123")

    def test_profile_page_loads(self):
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)

    def test_profile_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 302)

    def test_profile_update(self):
        response = self.client.post(reverse("users:edit_profile"), {
            "bio": "This is my bio", "first_name": "Test", "last_name": "User",
        })
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "This is my bio")


class PendingRegistrationModelTest(TestCase):

    def test_create_pending(self):
        pending = PendingRegistration.create_pending("test@example.com", "testpass123")
        self.assertEqual(pending.email, "test@example.com")
        self.assertEqual(len(pending.verification_code), 6)

    def test_is_expired(self):
        pending = PendingRegistration.create_pending("test@example.com", "testpass123")
        self.assertFalse(pending.is_expired())
        pending.expires_at = timezone.now() - timedelta(minutes=11)
        pending.save()
        self.assertTrue(pending.is_expired())

    def test_cleanup_expired(self):
        PendingRegistration.create_pending("test1@example.com", "pass")
        p2 = PendingRegistration.create_pending("test2@example.com", "pass")
        p2.expires_at = timezone.now() - timedelta(minutes=11)
        p2.save()
        count = PendingRegistration.cleanup_expired()
        self.assertEqual(count, 1)
        self.assertTrue(PendingRegistration.objects.filter(email="test1@example.com").exists())
        self.assertFalse(PendingRegistration.objects.filter(email="test2@example.com").exists())
