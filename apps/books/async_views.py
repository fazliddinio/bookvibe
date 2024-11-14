"""
Async views for external API calls and database operations
Django 4.1+ supports async views natively
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from asgiref.sync import sync_to_async
import asyncio

from apps.books.services.external_apis import google_books_api, openlibrary_api
from apps.books.services.ai_services import recommendation_ai, summary_ai, review_analysis_ai
from apps.books.models import Book, BookReview
from apps.users.models import UserProfile


@require_http_methods(["GET"])
async def search_external_books(request):
    """
    Async view to search books from Google Books and OpenLibrary simultaneously
    """
    query = request.GET.get("q", "")
    if not query:
        return JsonResponse({"error": "Query parameter 'q' is required"}, status=400)
    
    # Run both API calls concurrently
    google_task = asyncio.create_task(
        asyncio.to_thread(google_books_api.search_books, query, 5)
    )
    openlibrary_task = asyncio.create_task(
        openlibrary_api.search_books_async(query, 5)
    )
    
    # Wait for both to complete
    google_results, openlibrary_results = await asyncio.gather(
        google_task, openlibrary_task
    )
    
    return JsonResponse({
        "query": query,
        "google_books": google_results,
        "open_library": openlibrary_results,
        "total_results": len(google_results) + len(openlibrary_results)
    })


@require_http_methods(["GET"])
async def get_book_enrichment(request, isbn):
    """
    Get enriched book data from multiple sources asynchronously
    """
    cache_key = f"enriched_book:{isbn}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return JsonResponse(cached_data)
    
    # Fetch from both APIs concurrently
    google_task = asyncio.create_task(
        asyncio.to_thread(google_books_api.get_book_by_isbn, isbn)
    )
    openlibrary_task = asyncio.create_task(
        asyncio.to_thread(openlibrary_api.get_book_by_isbn, isbn)
    )
    
    google_data, openlibrary_data = await asyncio.gather(
        google_task, openlibrary_task
    )
    
    enriched_data = {
        "isbn": isbn,
        "google_books": google_data,
        "open_library": openlibrary_data,
        "merged_data": _merge_book_data(google_data, openlibrary_data)
    }
    
    # Cache for 24 hours
    cache.set(cache_key, enriched_data, 86400)
    
    return JsonResponse(enriched_data)


@require_http_methods(["GET"])
async def get_ai_recommendations(request):
    """
    Get AI-powered book recommendations for authenticated user
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    # Get user data asynchronously
    user_profile = await sync_to_async(
        lambda: UserProfile.objects.select_related("user").get(user=request.user)
    )()
    
    # Get user's read books
    read_books = await sync_to_async(
        lambda: list(
            Book.objects.filter(
                shelfbook__shelf__user=request.user,
                shelfbook__shelf__name__iexact="read"
            ).values_list("title", flat=True)[:20]
        )
    )()
    
    # Get AI recommendations (run in thread pool)
    recommendations = await asyncio.to_thread(
        recommendation_ai.get_recommendations,
        {
            "favorite_genres": user_profile.favorite_genres,
            "reading_goal": user_profile.reading_goal
        },
        list(read_books),
        5
    )
    
    return JsonResponse({
        "user": request.user.username,
        "recommendations": recommendations
    })


@require_http_methods(["GET"])
async def get_book_ai_summary(request, book_id):
    """
    Generate AI summary for a book
    """
    try:
        # Get book asynchronously
        book = await sync_to_async(
            lambda: Book.objects.get(id=book_id)
        )()
        
        # Generate summary (run in thread pool)
        summary = await asyncio.to_thread(
            summary_ai.generate_summary,
            book.title,
            book.description or "No description available"
        )
        
        return JsonResponse({
            "book_id": book_id,
            "title": book.title,
            "ai_summary": summary or "Xulosa yaratib bo'lmadi"
        })
        
    except Book.DoesNotExist:
        return JsonResponse({"error": "Kitob topilmadi"}, status=404)


@require_http_methods(["GET"])
async def analyze_book_reviews(request, book_id):
    """
    Analyze all reviews for a book using AI
    """
    try:
        # Get book
        book = await sync_to_async(
            lambda: Book.objects.get(id=book_id)
        )()
        
        # Get reviews
        reviews = await sync_to_async(
            lambda: list(
                BookReview.objects.filter(
                    book=book,
                    is_approved=True
                ).values_list("comment", flat=True)[:50]
            )
        )()
        
        if not reviews:
            return JsonResponse({
                "book_id": book_id,
                "message": "Tahlil qilish uchun sharhlar mavjud emas"
            })
        
        # Analyze reviews (run in thread pool)
        analysis = await asyncio.to_thread(
            review_analysis_ai.analyze_reviews,
            list(reviews)
        )
        
        return JsonResponse({
            "book_id": book_id,
            "title": book.title,
            "review_count": len(reviews),
            "analysis": analysis
        })
        
    except Book.DoesNotExist:
        return JsonResponse({"error": "Kitob topilmadi"}, status=404)


def _merge_book_data(google_data, openlibrary_data):
    """
    Merge book data from multiple sources, preferring more complete information
    """
    if not google_data and not openlibrary_data:
        return None
    
    if not google_data:
        return openlibrary_data
    
    if not openlibrary_data:
        return google_data
    
    # Merge both datasets, preferring Google Books for most fields
    merged = {
        "title": google_data.get("title") or openlibrary_data.get("title"),
        "authors": google_data.get("authors") or openlibrary_data.get("authors"),
        "description": google_data.get("description") or openlibrary_data.get("description"),
        "published_date": google_data.get("published_date") or openlibrary_data.get("publish_date"),
        "isbn": google_data.get("isbn_13") or google_data.get("isbn_10") or (openlibrary_data.get("isbn_13", [None])[0]),
        "page_count": google_data.get("page_count") or openlibrary_data.get("number_of_pages"),
        "cover_image": google_data.get("cover_image") or openlibrary_data.get("cover_url"),
        "categories": google_data.get("categories") or openlibrary_data.get("subjects", []),
        "language": google_data.get("language") or "en",
        "average_rating": google_data.get("average_rating"),
        "ratings_count": google_data.get("ratings_count"),
        "sources": ["google_books", "openlibrary"]
    }
    
    return merged

