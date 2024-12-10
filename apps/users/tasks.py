"""
Celery tasks for BookVibe email operations.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_verification_code_email_task(self, email, verification_code):
    """
    Send verification code email asynchronously.

    Args:
        email (str): User's email address
        verification_code (str): 6-digit verification code
    """
    try:
        subject = "Your Bookvibe verification code"

        # HTML content
        html_message = render_to_string(
            "users/verification_code_email.html",
            {
                "verification_code": verification_code,
                "site_name": "Bookvibe",
                "email": email,
                "user": {"username": email.split("@")[0], "email": email},
            },
        )

        # Plain text content
        plain_message = strip_tags(html_message)

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Verification code email sent successfully to {email}")
        return f"Verification code email sent to {email}"

    except Exception as exc:
        logger.error(f"Failed to send verification code email to {email}: {exc}")
        # Retry the task with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_password_reset_email_task(self, user_id, reset_token):
    """
    Send password reset email asynchronously.

    Args:
        user_id (int): User's ID
        reset_token (str): Password reset token
    """
    try:
        user = User.objects.get(id=user_id)

        # Create reset URL
        reset_url = f"{settings.SITE_URL}/users/reset-password/{reset_token}/"

        # Email subject and content
        subject = "Reset your Bookvibe password"

        # HTML content
        html_message = render_to_string(
            "users/password_reset_email.html",
            {"user": user, "reset_url": reset_url, "site_name": "Bookvibe"},
        )

        # Plain text content
        plain_message = strip_tags(html_message)

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Password reset email sent successfully to {user.email}")
        return f"Password reset email sent to {user.email}"

    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        return f"User with ID {user_id} not found"
    except Exception as exc:
        logger.error(f"Failed to send password reset email to user {user_id}: {exc}")
        # Retry the task with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_welcome_email_task(self, user_id):
    """
    Send welcome email asynchronously after successful verification.

    Args:
        user_id (int): User's ID
    """
    try:
        user = User.objects.get(id=user_id)

        # Email subject and content
        subject = "Welcome to Bookvibe!"

        # HTML content
        html_message = render_to_string(
            "users/welcome_email.html",
            {"user": user, "site_name": "Bookvibe"},
        )

        # Plain text content
        plain_message = strip_tags(html_message)

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Welcome email sent successfully to {user.email}")
        return f"Welcome email sent to {user.email}"

    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        return f"User with ID {user_id} not found"
    except Exception as exc:
        logger.error(f"Failed to send welcome email to user {user_id}: {exc}")
        # Retry the task with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_verification_code_session_email_task(self, email, verification_code):
    """
    Send verification code email for EmailVerificationSession asynchronously.

    Args:
        email (str): User's email address
        verification_code (str): 6-digit verification code
    """
    try:
        subject = "Your Bookvibe verification code"

        # HTML content
        html_message = render_to_string(
            "users/verification_code_email.html",
            {
                "verification_code": verification_code,
                "site_name": "Bookvibe",
                "email": email,
                "user": {"username": email.split("@")[0], "email": email},
            },
        )

        # Plain text content
        plain_message = strip_tags(html_message)

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Verification code session email sent successfully to {email}")
        return f"Verification code session email sent to {email}"

    except Exception as exc:
        logger.error(
            f"Failed to send verification code session email to {email}: {exc}"
        )
        # Retry the task with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))
