"""
API URL Configuration for BookVibe REST API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from apps.books.api_views import BookViewSet, GenreViewSet, AuthorViewSet, BookReviewViewSet
from apps.users.api_views import UserViewSet
from apps.books import async_views

# Create router and register viewsets
router = DefaultRouter()
router.register(r"books", BookViewSet, basename="book")
router.register(r"genres", GenreViewSet, basename="genre")
router.register(r"authors", AuthorViewSet, basename="author")
router.register(r"reviews", BookReviewViewSet, basename="review")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    # Async external API endpoints
    path("external/search/", async_views.search_external_books, name="external-search"),
    path("external/isbn/<str:isbn>/", async_views.get_book_enrichment, name="book-enrichment"),
    
    # AI-powered endpoints
    path("ai/recommendations/", async_views.get_ai_recommendations, name="ai-recommendations"),
    path("ai/summary/<int:book_id>/", async_views.get_book_ai_summary, name="ai-summary"),
    path("ai/analyze-reviews/<int:book_id>/", async_views.analyze_book_reviews, name="analyze-reviews"),
    
    # JWT Authentication endpoints
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    
    # API Documentation
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    
    # Include router URLs
    path("", include(router.urls)),
]

