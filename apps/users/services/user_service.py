"""
User Service - Business logic for user operations
Follows Single Responsibility Principle
"""
from typing import Optional, Dict
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from apps.users.models import UserProfile, PendingRegistration
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user-related operations."""
    
    @staticmethod
    def create_pending_registration(email: str, password: str) -> Optional[PendingRegistration]:
        """
        Create a pending registration for email verification.
        
        Args:
            email: User's email
            password: Raw password
            
        Returns:
            PendingRegistration instance or None
        """
        try:
            pending = PendingRegistration.create_pending(email, password)
            logger.info(f"Pending registration created for {email}")
            return pending
        except Exception as e:
            logger.error(f"Error creating pending registration: {str(e)}")
            return None
    
    @staticmethod
    def verify_and_create_user(verification_code: str) -> Optional[User]:
        """
        Verify email code and create user account.
        
        Args:
            verification_code: 6-digit verification code
            
        Returns:
            Created User instance or None
        """
        try:
            # Find pending registration
            pending = PendingRegistration.objects.filter(
                verification_code=verification_code
            ).first()
            
            if not pending:
                logger.warning(f"No pending registration found for code {verification_code}")
                return None
            
            # Check expiration
            if pending.is_expired():
                logger.warning(f"Verification code expired for {pending.email}")
                return None
            
            # Create user
            user = User.objects.create_user(
                username=pending.email,
                email=pending.email,
                password=None  # Will be set from hash
            )
            user.password = pending.password_hash
            user.is_active = True
            user.save()
            
            # Create profile
            UserProfile.objects.create(
                user=user,
                is_email_verified=True
            )
            
            # Delete pending registration
            pending.delete()
            
            logger.info(f"User created successfully: {user.username}")
            return user
            
        except Exception as e:
            logger.error(f"Error verifying and creating user: {str(e)}")
            return None
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Authenticated user or None
        """
        try:
            user = authenticate(username=email, password=password)
            if user:
                logger.info(f"User authenticated: {user.username}")
            else:
                logger.warning(f"Authentication failed for email: {email}")
            return user
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return None
    
    @staticmethod
    def get_user_profile(user: User) -> UserProfile:
        """
        Get or create user profile.
        
        Args:
            user: User instance
            
        Returns:
            UserProfile instance
        """
        try:
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                logger.info(f"Profile created for user {user.username}")
            return profile
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            # Return a temporary profile object
            return UserProfile(user=user)
    
    @staticmethod
    def update_profile(
        profile: UserProfile,
        bio: Optional[str] = None,
        location: Optional[str] = None,
        birth_date = None,
        profile_picture = None
    ) -> bool:
        """
        Update user profile.
        
        Args:
            profile: UserProfile instance
            bio: Biography text
            location: User location
            birth_date: Birth date
            profile_picture: Profile picture file
            
        Returns:
            True if updated, False otherwise
        """
        try:
            if bio is not None:
                profile.bio = bio
            if location is not None:
                profile.location = location
            if birth_date is not None:
                profile.birth_date = birth_date
            if profile_picture is not None:
                profile.profile_picture = profile_picture
            
            profile.save()
            logger.info(f"Profile updated for user {profile.user.username}")
            return True
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            return False
    
    @staticmethod
    def change_password(user: User, old_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            user: User instance
            old_password: Current password
            new_password: New password
            
        Returns:
            True if changed, False otherwise
        """
        try:
            if not user.check_password(old_password):
                logger.warning(f"Incorrect old password for user {user.username}")
                return False
            
            user.set_password(new_password)
            user.save()
            logger.info(f"Password changed for user {user.username}")
            return True
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            return False
    
    @staticmethod
    def get_user_statistics(user: User) -> Dict:
        """
        Get user statistics (reviews, books read, etc.).
        
        Args:
            user: User instance
            
        Returns:
            Dictionary with statistics
        """
        try:
            from apps.books.models import BookReview
            from apps.reading_lists.models import ShelfBook
            
            total_reviews = BookReview.objects.filter(user=user, is_approved=True).count()
            
            books_read = ShelfBook.objects.filter(
                shelf__user=user,
                shelf__name__iexact="read"
            ).count()
            
            # Calculate total likes received on reviews
            reviews = BookReview.objects.filter(user=user)
            total_likes = sum(review.get_likes_count() for review in reviews)
            
            return {
                "total_reviews": total_reviews,
                "books_read": books_read,
                "total_likes_received": total_likes,
            }
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            return {
                "total_reviews": 0,
                "books_read": 0,
                "total_likes_received": 0,
            }
    
    @staticmethod
    def cleanup_expired_pending_registrations() -> int:
        """
        Clean up expired pending registrations.
        This should be called periodically (e.g., via Celery task).
        
        Returns:
            Number of deleted registrations
        """
        try:
            count = PendingRegistration.cleanup_expired()
            logger.info(f"Cleaned up {count} expired pending registrations")
            return count
        except Exception as e:
            logger.error(f"Error cleaning up pending registrations: {str(e)}")
            return 0


class RegistrationService:
    """Service class for user registration operations."""
    
    @staticmethod
    def is_email_available(email: str) -> bool:
        """
        Check if email is available for registration.
        
        Args:
            email: Email to check
            
        Returns:
            True if available, False otherwise
        """
        # Check if email exists in User table
        if User.objects.filter(email=email).exists():
            return False
        
        # Check if email has a non-expired pending registration
        pending = PendingRegistration.objects.filter(email=email).first()
        if pending and not pending.is_expired():
            return False
        
        return True
    
    @staticmethod
    def resend_verification_code(email: str) -> Optional[str]:
        """
        Resend verification code for pending registration.
        
        Args:
            email: Email address
            
        Returns:
            New verification code or None
        """
        try:
            pending = PendingRegistration.objects.filter(email=email).first()
            if not pending:
                logger.warning(f"No pending registration found for {email}")
                return None
            
            # Check rate limiting (1 minute)
            time_since_created = timezone.now() - pending.created_at
            if time_since_created < timedelta(minutes=1):
                logger.warning(f"Rate limit exceeded for resend: {email}")
                return None
            
            new_code = pending.generate_new_code()
            logger.info(f"Verification code regenerated for {email}")
            return new_code
        except Exception as e:
            logger.error(f"Error resending verification code: {str(e)}")
            return None

