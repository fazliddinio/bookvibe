from django.http import JsonResponse
from django.db import connection
from django.utils import timezone


def health_check(request):
    """
    Health check endpoint for monitoring
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
