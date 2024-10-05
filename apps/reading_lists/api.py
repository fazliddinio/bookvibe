"""
Simplified API endpoints for reading lists functionality.
Only essential internal APIs are kept for clean architecture.
"""

import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Count
from apps.books.models import Book
from .models import ReadingShelf

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def book_search_api(request):
    """
    Simple API for searching books with basic filters
    """
    query = request.GET.get("q", "")
    genre = request.GET.get("genre", "")

    if not query:
        return JsonResponse(
            {"error": "Query parameter is required", "status": "error"}, status=400
        )

    # Build query
    books = Book.objects.filter(title__icontains=query)

    if genre:
        books = books.filter(genre__name__icontains=genre)

    # Limit results
    books = books[:20]

    # Format response
    books_data = []
    for book in books:
        books_data.append(
            {
                "id": book.id,
                "title": book.title,
                "author": (
                    book.get_primary_author().full_name()
                    if book.get_primary_author()
                    else "Unknown"
                ),
                "genre": book.genre.name if book.genre else "Unknown",
                "isbn": book.isbn,
                "page_count": book.page_count,
                "detail_url": f"/{book.id}/",
            }
        )

    return JsonResponse(
        {
            "status": "success",
            "query": query,
            "total_results": len(books_data),
            "books": books_data,
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_book_to_shelf_api(request):
    """
    Add a book to a reading shelf via API
    """
    try:
        import json

        data = json.loads(request.body)
        book_id = data.get("book_id")
        shelf_name = data.get("shelf_name")

        if not book_id or not shelf_name:
            return JsonResponse(
                {"status": "error", "error": "book_id and shelf_name are required"},
                status=400,
            )

        book = get_object_or_404(Book, id=book_id)
        shelf, created = ReadingShelf.objects.get_or_create(
            name=shelf_name, user=request.user
        )

        success = shelf.add_book(book)

        if success:
            return JsonResponse(
                {"status": "success", "message": f"Book added to {shelf_name}"}
            )
        else:
            return JsonResponse(
                {"status": "error", "error": "Book already in shelf"}, status=400
            )

    except Exception as e:
        logger.error(f"Error adding book to shelf: {e}")
        return JsonResponse(
            {"status": "error", "error": "Internal server error"}, status=500
        )


@csrf_exempt
@require_http_methods(["GET"])
def trending_books_api(request):
    """
    Get trending books based on recent reviews
    """
    # Get books with most recent reviews
    trending_books = (
        Book.objects.annotate(review_count=Count("bookreview"))
        .filter(review_count__gt=0)
        .order_by("-bookreview__created_at")[:10]
    )

    books_data = []
    for book in trending_books:
        books_data.append(
            {
                "id": book.id,
                "title": book.title,
                "author": (
                    book.get_primary_author().full_name()
                    if book.get_primary_author()
                    else "Unknown"
                ),
                "genre": book.genre.name if book.genre else "Unknown",
                "review_count": book.review_count,
                "detail_url": f"/{book.id}/",
            }
        )

    return JsonResponse({"status": "success", "trending_books": books_data})


@csrf_exempt
@require_http_methods(["GET"])
def api_health_check(request):
    """
    Simple health check for API endpoints
    """
    return JsonResponse({"status": "healthy", "api": "reading_lists", "version": "1.0"})
