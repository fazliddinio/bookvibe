from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.users.models import UserProfile
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

    def test_successful_registration(self):
        response = self.client.post(self.register_url, {
            "email": "test@example.com",
            "password": "testpass123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_registration_short_password(self):
        response = self.client.post(self.register_url, {
            "email": "test@example.com",
            "password": "12345",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="test@example.com").exists())

    def test_duplicate_email_rejected(self):
        User.objects.create_user(
            username="test@example.com", email="test@example.com",
            password="oldpass123",
        )
        response = self.client.post(self.register_url, {
            "email": "test@example.com",
            "password": "newpass456",
        })
        self.assertEqual(response.status_code, 200)  # stays on form with error
        user = User.objects.get(email="test@example.com")
        self.assertTrue(user.check_password("oldpass123"))  # password unchanged


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


class UserProfileModelTest(TestCase):

    def test_profile_str(self):
        user = User.objects.create_user(
            username="test@example.com", email="test@example.com",
            password="testpass123",
        )
        profile = UserProfile.objects.create(user=user)
        self.assertIn("test@example.com", str(profile))
