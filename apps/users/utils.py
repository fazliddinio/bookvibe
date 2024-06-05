"""
Utility functions for user-related operations.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def send_email_with_fallback(
    subject: str,
    plain_message: str,
    html_message: str,
    recipient_email: str,
    celery_task_func: Optional[callable] = None,
    celery_task_args: Optional[tuple] = None,
) -> bool:
    """
    Send email with Celery fallback to direct sending.

    Args:
        subject: Email subject
        plain_message: Plain text message
        html_message: HTML message
        recipient_email: Recipient email address
        celery_task_func: Celery task function to try first
        celery_task_args: Arguments for the Celery task

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Try Celery first if task function is provided
    if celery_task_func and celery_task_args:
        try:
            task = celery_task_func.delay(*celery_task_args)
            logger.info(f"Email queued for {recipient_email}, task ID: {task.id}")
            return True
        except Exception as e:
            logger.warning(f"Celery failed, trying direct email: {e}")

    # Fallback to direct email sending
    try:
        from django.core.mail import send_mail
        from django.conf import settings

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email sent directly to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Direct email also failed: {e}")
        return False


def create_verification_email_content(verification_code: str) -> tuple[str, str]:
    """
    Create verification email content.

    Args:
        verification_code: The verification code to include

    Returns:
        tuple: (plain_message, html_message)
    """
    plain_message = f"Bookvibe tasdiqlash kodingiz: {verification_code}. Bu kod 10 daqiqadan keyin amal qilmay qoladi."

    html_message = f"""
    <html>
    <body>
        <h2>Bookvibe'ga xush kelibsiz!</h2>
        <p>Tasdiqlash kodingiz: <strong>{verification_code}</strong></p>
        <p>Bu kod 10 daqiqadan keyin amal qilmay qoladi.</p>
        <p>Agar siz bu kodni so'ramagan bo'lsangiz, iltimos bu emailni e'tiborsiz qoldiring.</p>
        <br>
        <p>Hurmat bilan,<br>Bookvibe jamoasi</p>
    </body>
    </html>
    """

    return plain_message, html_message


def create_password_reset_email_content(
    username: str, reset_url: str
) -> tuple[str, str]:
    """
    Create password reset email content.

    Args:
        username: User's username or email
        reset_url: Password reset URL

    Returns:
        tuple: (plain_message, html_message)
    """
    plain_message = f"Bookvibe parolingizni tiklash uchun: {reset_url}\nBu havola 1 soatdan keyin amal qilmay qoladi."

    html_message = f"""
    <html>
    <body>
        <h2>Parolni Tiklash So'rovi</h2>
        <p>Salom {username},</p>
        <p>Siz Bookvibe hisobingiz uchun parolni tiklashni so'radingiz.</p>
        <p>Parolni tiklash uchun quyidagi tugmani bosing:</p>
        <p><a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Parolni Tiklash</a></p>
        <p>Yoki ushbu URL'ni nusxalab, brauzeringizga qo'ying: {reset_url}</p>
        <p>Bu havola 1 soatdan keyin amal qilmay qoladi.</p>
        <p>Agar siz bu tiklashni so'ramagan bo'lsangiz, iltimos bu emailni e'tiborsiz qoldiring.</p>
        <br>
        <p>Hurmat bilan,<br>Bookvibe jamoasi</p>
    </body>
    </html>
    """

    return plain_message, html_message


def create_welcome_email_content(username: str, site_url: str) -> tuple[str, str]:
    """
    Create welcome email content.

    Args:
        username: User's username or email
        site_url: Site URL

    Returns:
        tuple: (plain_message, html_message)
    """
    plain_message = f"Bookvibe'ga xush kelibsiz! Emailingiz tasdiqlandi. Kashf qilishni boshlang: {site_url}"

    html_message = f"""
    <html>
    <body>
        <h2>Bookvibe'ga xush kelibsiz!</h2>
        <p>Salom {username},</p>
        <p>Bookvibe'ga xush kelibsiz! Emailingiz muvaffaqiyatli tasdiqlandi.</p>
        <p>Endi siz:</p>
        <ul>
            <li>Kitoblarni ko'rib chiqishingiz va qidirishingiz</li>
            <li>Sharhlar yozishingiz va kitoblarga baho berishingiz</li>
            <li>O'qish ro'yxatlarini yaratishingiz</li>
            <li>Boshqa kitobxonlar bilan bog'lanishingiz mumkin</li>
        </ul>
        <p>Kashf qilishni boshlang: <a href="{site_url}">{site_url}</a></p>
        <br>
        <p>Yoqimli o'qishlar!<br>Bookvibe jamoasi</p>
    </body>
    </html>
    """

    return plain_message, html_message
