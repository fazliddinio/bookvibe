"""
REST API ViewSets for Books
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.core.cache import cache
from django.db.models import Count, Q, Avg
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from apps.books.models import Book, Genre, Author, BookReview, ReviewComment, ReviewVote
from apps.books.serializers import (
    BookListSerializer, BookDetailSerializer, BookCreateUpdateSerializer,
    GenreSerializer, AuthorSerializer, BookReviewSerializer, ReviewCommentSerializer
)


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing genres.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    
    def list(self, request, *args, **kwargs):
        # Cache genres for 1 hour
        cache_key = "api:genres:list"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 3600)
        return response


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing authors.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "nationality"]
    ordering_fields = ["last_name", "first_name", "created_at"]
    
    @action(detail=True, methods=["get"])
    def books(self, request, pk=None):
        """Get all books by this author"""
        author = self.get_object()
        books = Book.objects.filter(bookauthor__author=author)
        serializer = BookListSerializer(books, many=True, context={"request": request})
        return Response(serializer.data)


class BookViewSet(viewsets.ModelViewSet):
    """
    API endpoint for books CRUD operations.
    
    list: Get all books
    retrieve: Get a single book
    create: Create a new book (authenticated users only)
    update: Update a book (authenticated users only)
    partial_update: Partially update a book
    destroy: Delete a book (authenticated users only)
    """
    queryset = Book.objects.select_related("genre", "added_by").prefetch_related("book_authors__author")
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "isbn"]
    ordering_fields = ["title", "publication_date", "created_at"]
    ordering = ["-created_at"]
    
    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return BookCreateUpdateSerializer
        return BookDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by genre
        genre_id = self.request.query_params.get("genre", None)
        if genre_id:
            queryset = queryset.filter(genre_id=genre_id)
        
        # Filter by availability
        available = self.request.query_params.get("available", None)
        if available is not None:
            queryset = queryset.filter(is_available=available.lower() == "true")
        
        # Filter by rating
        min_rating = self.request.query_params.get("min_rating", None)
        if min_rating:
            queryset = queryset.annotate(
                avg_rating=Avg("bookreview__stars_given")
            ).filter(avg_rating__gte=float(min_rating))
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        # Cache individual book details for 10 minutes
        cache_key = f"api:book:{kwargs.get('pk')}"
        cached_data = cache.get(cache_key)
        
        if cached_data and not request.user.is_authenticated:
            return Response(cached_data)
        
        response = super().retrieve(request, *args, **kwargs)
        if not request.user.is_authenticated:
            cache.set(cache_key, response.data, 600)
        return response
    
    @action(detail=True, methods=["get"])
    def reviews(self, request, pk=None):
        """Get all reviews for a book"""
        book = self.get_object()
        reviews = book.reviews.filter(is_approved=True).select_related("user")
        serializer = BookReviewSerializer(reviews, many=True, context={"request": request})
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key="user", rate="5/h", method="POST"))
    def add_review(self, request, pk=None):
        """Add a review to a book"""
        book = self.get_object()
        
        # Check if user already reviewed this book
        existing_review = BookReview.objects.filter(book=book, user=request.user).first()
        if existing_review:
            return Response(
                {"error": "You have already reviewed this book"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = BookReviewSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user, book=book)
            # Invalidate cache
            cache.delete(f"api:book:{pk}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=["get"])
    def trending(self, request):
        """Get trending books based on recent reviews and ratings"""
        cache_key = "api:books:trending"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Books with most reviews in last 30 days
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        trending_books = Book.objects.annotate(
            recent_reviews=Count("bookreview", filter=Q(bookreview__created_time__gte=thirty_days_ago)),
            avg_rating=Avg("bookreview__stars_given")
        ).filter(recent_reviews__gt=0).order_by("-recent_reviews", "-avg_rating")[:10]
        
        serializer = BookListSerializer(trending_books, many=True, context={"request": request})
        cache.set(cache_key, serializer.data, 1800)  # Cache for 30 minutes
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def top_rated(self, request):
        """Get top rated books"""
        cache_key = "api:books:top_rated"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        top_books = Book.objects.annotate(
            avg_rating=Avg("bookreview__stars_given"),
            review_count=Count("bookreview")
        ).filter(review_count__gte=3).order_by("-avg_rating")[:20]
        
        serializer = BookListSerializer(top_books, many=True, context={"request": request})
        cache.set(cache_key, serializer.data, 3600)  # Cache for 1 hour
        return Response(serializer.data)


class BookReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for book reviews.
    """
    queryset = BookReview.objects.select_related("user", "book").filter(is_approved=True)
    serializer_class = BookReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def vote(self, request, pk=None):
        """Vote on a review (upvote/downvote)"""
        review = self.get_object()
        vote_type = request.data.get("vote_type")
        
        if vote_type not in ["upvote", "downvote"]:
            return Response(
                {"error": "Noto'g'ri ovoz turi. 'upvote' yoki 'downvote' bo'lishi kerak"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create vote
        vote, created = ReviewVote.objects.get_or_create(
            review=review,
            user=request.user,
            defaults={"vote_type": vote_type}
        )
        
        if not created:
            # Update existing vote
            if vote.vote_type == vote_type:
                # Remove vote if same type
                vote.delete()
                return Response({"message": "Ovoz o'chirildi"})
            else:
                # Change vote type
                vote.vote_type = vote_type
                vote.save()
                return Response({"message": "Ovoz yangilandi"})
        
        return Response({"message": "Ovoz qo'shildi"}, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key="user", rate="20/h", method="POST"))
    def add_comment(self, request, pk=None):
        """Add a comment to a review"""
        review = self.get_object()
        
        serializer = ReviewCommentSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user, review=review)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

