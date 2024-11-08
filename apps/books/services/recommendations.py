"""
Recommendation service for personalized book suggestions
"""
from django.db.models import Count, Q, Avg
from apps.books.models import Book, BookReview
from apps.reading_lists.models import ShelfBook
from apps.habits.models import UserInterest
import random


class RecommendationService:
    """Service for generating personalized book recommendations"""
    
    @staticmethod
    def get_personalized_recommendations(user, limit=6):
        """
        Get personalized recommendations for a user based on their reading history
        and interests
        """
        if not user.is_authenticated:
            return RecommendationService.get_popular_books(limit)
        
        # Get user's interests
        try:
            interests = UserInterest.objects.get(user=user)
            preferred_genres = interests.preferred_genres
        except UserInterest.DoesNotExist:
            preferred_genres = []
        
        # Get books from user's shelves
        user_books = ShelfBook.objects.filter(shelf__user=user).values_list('book_id', flat=True)
        
        # Get user's reviewed books
        reviewed_books = BookReview.objects.filter(user=user).values_list('book_id', flat=True)
        
        # Combine all books user has interacted with
        excluded_books = set(list(user_books) + list(reviewed_books))
        
        # Start with genre-based recommendations
        recommendations = set()
        
        if preferred_genres:
            genre_books = Book.objects.filter(
                genre__name__in=preferred_genres
            ).exclude(
                id__in=excluded_books
            ).annotate(
                avg_rating=Avg('reviews__stars_given'),
                review_count=Count('reviews')
            ).filter(
                review_count__gte=1
            ).order_by('-avg_rating', '-review_count')[:limit]
            
            recommendations.update(genre_books)
        
        # If not enough recommendations, add popular books
        if len(recommendations) < limit:
            popular = RecommendationService.get_popular_books(
                limit - len(recommendations),
                exclude_ids=excluded_books.union(set(b.id for b in recommendations))
            )
            recommendations.update(popular)
        
        # Convert to list and shuffle for variety
        result = list(recommendations)[:limit]
        random.shuffle(result)
        
        return result
    
    @staticmethod
    def get_related_books(book, limit=6):
        """
        Get books related to a given book based on:
        - Same genre
        - Similar authors
        - Similar ratings
        """
        related = set()
        
        # Books in the same genre
        if book.genre:
            genre_books = Book.objects.filter(
                genre=book.genre
            ).exclude(
                id=book.id
            ).annotate(
                avg_rating=Avg('reviews__stars_given')
            ).order_by('-avg_rating')[:limit * 2]
            
            related.update(genre_books)
        
        # Books by same authors
        book_authors = book.get_authors()
        if book_authors:
            for author in book_authors:
                author_books = Book.objects.filter(
                    book_authors__author=author
                ).exclude(
                    id=book.id
                ).annotate(
                    avg_rating=Avg('reviews__stars_given')
                ).order_by('-avg_rating')[:3]
                
                related.update(author_books)
        
        # Convert to list and sort by rating
        result = list(related)
        result.sort(key=lambda x: x.get_average_rating(), reverse=True)
        
        return result[:limit]
    
    @staticmethod
    def get_popular_books(limit=6, exclude_ids=None):
        """Get popular books based on reviews and ratings"""
        queryset = Book.objects.annotate(
            avg_rating=Avg('reviews__stars_given'),
            review_count=Count('reviews')
        ).filter(
            review_count__gte=1
        ).order_by('-review_count', '-avg_rating')
        
        if exclude_ids:
            queryset = queryset.exclude(id__in=exclude_ids)
        
        return list(queryset[:limit])
    
    @staticmethod
    def get_trending_books(days=7, limit=6):
        """Get trending books based on recent activity"""
        from datetime import timedelta
        from django.utils import timezone
        from apps.feed.models import Activity
        
        week_ago = timezone.now() - timedelta(days=days)
        
        trending = Book.objects.filter(
            activities__created_at__gte=week_ago
        ).annotate(
            activity_count=Count('activities')
        ).order_by('-activity_count')[:limit]
        
        return list(trending)

