from django.urls import path
from . import views, api

app_name = "reading_lists"

urlpatterns = [
    path("", views.reading_lists_view, name="lists"),
    path("shelf/<int:shelf_id>/", views.shelf_detail_view, name="shelf_detail"),
    path("add/<int:book_id>/", views.add_to_shelf_view, name="add_to_shelf"),
    path(
        "remove-book/<int:book_id>/<str:category_name>/",
        views.remove_book_from_category,
        name="remove_book_from_category",
    ),
    path("create/", views.create_shelf_view, name="create_shelf"),
    path("delete/<int:shelf_id>/", views.delete_shelf_view, name="delete_shelf"),
    path("public/", views.public_shelves_view, name="public_shelves"),
    # Essential APIs only
    path("api/search/", api.book_search_api, name="api_search"),
    path("api/add-to-shelf/", api.add_book_to_shelf_api, name="api_add_to_shelf"),
    path("api/trending/", api.trending_books_api, name="api_trending"),
    path("api/health/", api.api_health_check, name="api_health"),
]
