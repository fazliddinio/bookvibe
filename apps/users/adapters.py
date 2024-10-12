"""
Custom adapters for django-allauth
"""
from django.contrib import messages
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom account adapter for regular signups"""
    
    def get_login_redirect_url(self, request):
        """Redirect to home page after login"""
        return "/"
    
    def add_message(self, request, level, message_tag, message, *args, **kwargs):
        """Override to translate messages to Uzbek"""
        message_str = str(message).lower()
        
        # Translate common allauth messages (case-insensitive)
        if 'successfully signed in' in message_str or 'successfully sign in' in message_str:
            # Extract username/email if present
            parts = str(message).split(' as ')
            if len(parts) > 1:
                message = f"Muvaffaqiyatli kirdingiz: {parts[1]}"
            else:
                message = "Muvaffaqiyatli tizimga kirdingiz!"
        elif 'you have signed out' in message_str or 'signed out' in message_str:
            message = 'Tizimdan chiqdingiz.'
        elif 'password successfully changed' in message_str:
            message = 'Parol muvaffaqiyatli o\'zgartirildi.'
        elif 'password successfully set' in message_str:
            message = 'Parol muvaffaqiyatli o\'rnatildi.'
        elif 'email address confirmed' in message_str:
            message = 'Email manzil tasdiqlandi.'
        elif 'email confirmation sent' in message_str:
            message = 'Email tasdiqlash xabari yuborildi'
        elif 'account inactive' in message_str:
            message = 'Hisobingiz faol emas.'
        elif 'email address already verified' in message_str:
            message = 'Email manzil allaqachon tasdiqlangan.'
        
        return super().add_message(request, level, message_tag, message, *args, **kwargs)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter for OAuth signups"""
    
    def add_message(self, request, level, message_tag, message, *args, **kwargs):
        """Override to translate messages to Uzbek"""
        message_str = str(message).lower()
        
        # Translate common allauth social messages (case-insensitive)
        if 'successfully signed in' in message_str or 'successfully sign in' in message_str:
            # Extract username/email if present
            parts = str(message).split(' as ')
            if len(parts) > 1:
                message = f"Muvaffaqiyatli kirdingiz: {parts[1]}"
            else:
                message = "Muvaffaqiyatli tizimga kirdingiz!"
        elif 'social account has been connected' in message_str:
            message = 'Ijtimoiy tarmoq hisobi bog\'landi.'
        elif 'social account has been disconnected' in message_str:
            message = 'Ijtimoiy tarmoq hisobi uzildi.'
        elif 'account has no password' in message_str:
            message = 'Hisobingizda parol o\'rnatilmagan.'
        elif 'you have signed out' in message_str or 'signed out' in message_str:
            message = 'Tizimdan chiqdingiz.'
        elif 'account inactive' in message_str:
            message = 'Hisobingiz faol emas.'
        elif 'email address already verified' in message_str:
            message = 'Email manzil allaqachon tasdiqlangan.'
        
        return super().add_message(request, level, message_tag, message, *args, **kwargs)
    
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a social provider,
        but before the login is actually processed.
        
        This handles linking social accounts to existing email accounts and
        automatically activates inactive accounts that sign in via Google.
        """
        # If the social account is already connected to a user, just proceed
        if sociallogin.is_existing:
            # But make sure the user is active and verified
            user = sociallogin.user
            if not user.is_active:
                user.is_active = True
                user.save()
            
            # Ensure profile is verified
            try:
                from .models import UserProfile
                profile = UserProfile.objects.get(user=user)
                if not profile.is_email_verified:
                    profile.is_email_verified = True
                    profile.save()
            except:
                pass
            return
        
        # Try to connect social account to existing user with same email
        try:
            from django.contrib.auth import get_user_model
            from .models import UserProfile
            User = get_user_model()
            
            # Get the email from the social account
            email = sociallogin.account.extra_data.get('email')
            if email:
                # Check if a user with this email already exists
                try:
                    user = User.objects.get(email=email)
                    
                    # Activate the user if inactive (e.g., unverified email account)
                    if not user.is_active:
                        user.is_active = True
                        user.save()
                    
                    # Connect the social account to the existing user
                    sociallogin.connect(request, user)
                    
                    # Mark the email as verified and update profile
                    profile, created = UserProfile.objects.get_or_create(user=user)
                    profile.is_email_verified = True
                    profile.email_verification_code = None  # Clear any pending code
                    profile.save()
                    
                except User.DoesNotExist:
                    # No existing user, will create new one
                    pass
        except Exception as e:
            # Log error but don't break the flow
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error in pre_social_login: {e}")
        
        # Mark the email as verified since it comes from a trusted provider
        if sociallogin.account.provider == 'google':
            sociallogin.email_addresses = sociallogin.email_addresses or []
            for email in sociallogin.email_addresses:
                email.verified = True
    
    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social login user.
        Override to mark email as verified and activate account.
        """
        user = super().save_user(request, sociallogin, form)
        
        # Make sure user is active
        if not user.is_active:
            user.is_active = True
            user.save()
        
        # Automatically verify the email for social accounts
        try:
            from .models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.is_email_verified = True
            profile.email_verification_code = None  # Clear any pending code
            profile.save()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error updating profile in save_user: {e}")
        
        return user
    
    def get_connect_redirect_url(self, request, socialaccount):
        """Redirect after connecting a social account"""
        return "/"

