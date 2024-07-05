"""
Book Service - Business logic for book operations
Follows Single Responsibility Principle and separates business logic from views
"""
from typing import List, Optional, Dict
from django.db.models import Q, Count, Avg, QuerySet
from django.core.paginator import Paginator, Page
from django.contrib.auth.models import User
from apps.books.models import Book, Genre, Author, BookAuthor
import logging

logger = logging.getLogger(__name__)


class BookService:
    """
    Service class for book-related business logic.
    Centralizes all book operations following SOLID principles.
    """
    
    @staticmethod
    def get_all_books(
        search_query: str = "",
        genre_filter: str = "",
        page_number: int = 1,
        page_size: int = 14
    ) -> Dict:
        """
        Get paginated list of books with optional filtering.
        
        Args:
            search_query: Search term for title, description, or ISBN
            genre_filter: Genre ID to filter by
            page_number: Page number for pagination
            page_size: Number of items per page
            
        Returns:
            Dictionary with paginated books and metadata
        """
        try:
            books = Book.objects.select_related("genre").all()
            
            # Apply search filter
            if search_query:
                books = books.filter(
                    Q(title__icontains=search_query)
                    | Q(description__icontains=search_query)
                    | Q(isbn__icontains=search_query)
                )
            
            # Apply genre filter
            if genre_filter:
                books = books.filter(genre_id=genre_filter)
            
            # Paginate
            paginator = Paginator(books, page_size)
            page_obj = paginator.get_page(page_number)
            
            return {
                "page_obj": page_obj,
                "total_count": paginator.count,
                "total_pages": paginator.num_pages,
            }
        except Exception as e:
            logger.error(f"Error fetching books: {str(e)}")
            return {
                "page_obj": None,
                "total_count": 0,
                "total_pages": 0,
            }
    
    @staticmethod
    def get_book_by_id(book_id: int) -> Optional[Book]:
        """
        Get a single book by ID with related data.
        
        Args:
            book_id: Book ID
            
        Returns:
            Book instance or None
        """
        try:
            return Book.objects.select_related("genre", "added_by").prefetch_related(
                "book_authors__author", "reviews__user", "purchase_links"
            ).get(id=book_id)
        except Book.DoesNotExist:
            logger.warning(f"Book with ID {book_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error fetching book {book_id}: {str(e)}")
            return None
    
    @staticmethod
    def create_book(
        title: str,
        description: str,
        genre_id: Optional[int],
        isbn: Optional[str],
        cover_image,
        added_by: User,
        author_name: str
    ) -> Optional[Book]:
        """
        Create a new book with author.
        
        Args:
            title: Book title
            description: Book description
            genre_id: Genre ID
            isbn: ISBN number
            cover_image: Cover image file
            added_by: User who added the book
            author_name: Full name of the author
            
        Returns:
            Created Book instance or None
        """
        try:
            # Create book
            book = Book.objects.create(
                title=title,
                description=description,
                genre_id=genre_id,
                isbn=isbn,
                cover_image=cover_image,
                added_by=added_by
            )
            
            # Create or get author
            if author_name:
                author = BookService._create_or_get_author(author_name)
                if author:
                    BookAuthor.objects.create(
                        book=book,
                        author=author,
                        is_primary=True
                    )
            
            logger.info(f"Book '{title}' created successfully by {added_by.username}")
            return book
            
        except Exception as e:
            logger.error(f"Error creating book: {str(e)}")
            return None
    
    @staticmethod
    def delete_book(book_id: int, user: User) -> bool:
        """
        Delete a book (only by owner or staff).
        
        Args:
            book_id: Book ID
            user: User attempting to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            book = Book.objects.get(id=book_id)
            
            # Check permissions
            if book.added_by != user and not user.is_staff:
                logger.warning(f"User {user.username} attempted to delete book {book_id} without permission")
                return False
            
            book.delete()
            logger.info(f"Book {book_id} deleted by {user.username}")
            return True
            
        except Book.DoesNotExist:
            logger.warning(f"Book {book_id} not found for deletion")
            return False
        except Exception as e:
            logger.error(f"Error deleting book {book_id}: {str(e)}")
            return False
    
    @staticmethod
    def search_books_by_query(query: str, limit: int = 20) -> QuerySet:
        """
        Search books by title, author, or ISBN.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            QuerySet of matching books
        """
        try:
            books = Book.objects.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(isbn__icontains=query)
                | Q(book_authors__author__first_name__icontains=query)
                | Q(book_authors__author__last_name__icontains=query)
            ).distinct()[:limit]
            
            return books
        except Exception as e:
            logger.error(f"Error searching books: {str(e)}")
            return Book.objects.none()
    
    @staticmethod
    def get_book_statistics() -> Dict:
        """
        Get overall book statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            total_books = Book.objects.count()
            books_with_reviews = Book.objects.annotate(
                review_count=Count('reviews')
            ).filter(review_count__gt=0).count()
            
            avg_pages = Book.objects.filter(
                page_count__isnull=False
            ).aggregate(
                avg_pages=Avg('page_count')
            )['avg_pages'] or 0
            
            return {
                "total_books": total_books,
                "books_with_reviews": books_with_reviews,
                "average_pages": round(avg_pages, 0),
            }
        except Exception as e:
            logger.error(f"Error fetching book statistics: {str(e)}")
            return {
                "total_books": 0,
                "books_with_reviews": 0,
                "average_pages": 0,
            }
    
    @staticmethod
    def _create_or_get_author(full_name: str) -> Optional[Author]:
        """
        Create or get author from full name.
        
        Args:
            full_name: Author's full name
            
        Returns:
            Author instance or None
        """
        try:
            name_parts = full_name.strip().split()
            if len(name_parts) >= 2:
                first_name = name_parts[0]
                last_name = " ".join(name_parts[1:])
            else:
                first_name = full_name
                last_name = ""
            
            author, created = Author.objects.get_or_create(
                first_name=first_name,
                last_name=last_name
            )
            
            return author
        except Exception as e:
            logger.error(f"Error creating/getting author: {str(e)}")
            return None


class GenreService:
    """Service class for genre operations."""
    
    @staticmethod
    def get_all_genres() -> QuerySet:
        """Get all genres ordered by name."""
        return Genre.objects.all().order_by('name')
    
    @staticmethod
    def get_genre_by_id(genre_id: int) -> Optional[Genre]:
        """Get genre by ID."""
        try:
            return Genre.objects.get(id=genre_id)
        except Genre.DoesNotExist:
            return None
    
    @staticmethod
    def get_books_by_genre(genre_id: int, limit: int = 10) -> QuerySet:
        """Get books for a specific genre."""
        return Book.objects.filter(genre_id=genre_id).select_related('genre')[:limit]

