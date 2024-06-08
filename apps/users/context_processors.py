from django.conf import settings

def feature_flags(request):
    """
    Expose feature flags to templates.
    """
    return {
        'ENABLE_GOOGLE_LOGIN': getattr(settings, 'ENABLE_GOOGLE_LOGIN', False),
        'ENABLE_EMAIL_SENDING': getattr(settings, 'ENABLE_EMAIL_SENDING', False),
    }
