from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.views.static import serve
from . import views


def about_view(request):
    return render(request, "about.html")


# CRITICAL: Media files pattern MUST come FIRST
urlpatterns = [
    # Media files - MUST be first to avoid conflicts
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

# Add all other patterns AFTER media
urlpatterns += [
    path("donut1024/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    # REST API endpoints
    path("api/v1/", include("bookvibe.api_urls")),
    # Web app URLs
    path("", include("apps.feed.urls")),  # Feed is now the home page
    path("books/", include("apps.books.urls")),  # Books moved to /books/
    path("users/", include("apps.users.urls")),
    path("reading-lists/", include("apps.reading_lists.urls")),
    path("feedback/", include("apps.feedback.urls")),
    path("habits/", include("apps.habits.urls")),
    path("about/", about_view, name="about"),
    path("health/", views.health_check, name="health_check"),
]
