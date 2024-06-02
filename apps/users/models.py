from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
import string


class PendingRegistration(models.Model):
    """
    Temporary storage for user registrations pending email verification.
    User is NOT created in database until email is verified.
    """
    email = models.EmailField(unique=True, db_index=True)
    password_hash = models.CharField(max_length=255)  # Hashed password
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'pending_registrations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'verification_code']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Pending: {self.email}"
    
    def is_expired(self):
        """Check if verification code has expired (10 minutes)"""
        return timezone.now() > self.expires_at
    
    def generate_new_code(self):
        """Generate a new verification code and extend expiry"""
        self.verification_code = ''.join(random.choices(string.digits, k=6))
        self.expires_at = timezone.now() + timedelta(minutes=10)
        self.save()
        return self.verification_code
    
    @classmethod
    def create_pending(cls, email, raw_password):
        """Create a pending registration with hashed password"""
        from django.contrib.auth.hashers import make_password
        
        # Delete any existing pending registration for this email
        cls.objects.filter(email=email).delete()
        
        # Create new pending registration
        verification_code = ''.join(random.choices(string.digits, k=6))
        return cls.objects.create(
            email=email,
            password_hash=make_password(raw_password),
            verification_code=verification_code,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
    
    @classmethod
    def cleanup_expired(cls):
        """Remove expired pending registrations (called by scheduled task)"""
        expired = cls.objects.filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.delete()
        return count


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", unique=True
    )
    bio = models.TextField(max_length=500, blank=True, default="")
    location = models.CharField(max_length=100, blank=True, default="")
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", null=True, blank=True
    )
    
    # Email verification (for social logins)
    is_email_verified = models.BooleanField(default=True)  # True by default since regular registration requires verification
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profiles"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username}'s profile"

    def send_welcome_email(self):
        """Send welcome email after successful registration"""
        from .utils import send_email_with_fallback, create_welcome_email_content

        plain_message, html_message = create_welcome_email_content(
            self.user.username,
            "http://localhost:8008"  # Replace with your actual site URL
        )

        return send_email_with_fallback(
            subject="Bookvibe'ga xush kelibsiz!",
            plain_message=plain_message,
            html_message=html_message,
            recipient_email=self.user.email,
        )
