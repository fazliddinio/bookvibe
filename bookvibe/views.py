from django.http import JsonResponse
from django.db import connection
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def health_check(request):
    """
    Health check endpoint for monitoring.
    Exempt from SSL redirect via SECURE_REDIRECT_EXEMPT in settings.
    """
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return JsonResponse(
            {
                "status": "healthy",
                "database": "connected",
                "timestamp": timezone.now().isoformat(),
            }
        )
    except Exception:
        return JsonResponse(
            {
                "status": "unhealthy",
                "database": "disconnected",
                "timestamp": timezone.now().isoformat(),
            },
            status=500,
        )
