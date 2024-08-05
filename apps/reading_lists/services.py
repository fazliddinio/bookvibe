"""
Reading List Service - Business logic for reading shelves
Follows Single Responsibility Principle
"""
from typing import Optional, List
from django.db.models import QuerySet
from django.contrib.auth.models import User
from apps.reading_lists.models import ReadingShelf, ShelfBook
from apps.books.models import Book
import logging

logger = logging.getLogger(__name__)


class ReadingShelfService:
    """Service class for reading shelf operations."""
    
    @staticmethod
    def get_user_shelves(user: User, include_private: bool = True) -> QuerySet:
        """
        Get all shelves for a user.
        
        Args:
            user: User instance
            include_private: Whether to include private shelves
            
        Returns:
            QuerySet of shelves
        """
        try:
            shelves = ReadingShelf.objects.filter(user=user)
            if not include_private:
                shelves = shelves.filter(is_public=True)
            return shelves.order_by('-updated_at')
        except Exception as e:
            logger.error(f"Error fetching user shelves: {str(e)}")
            return ReadingShelf.objects.none()
    
    @staticmethod
    def get_shelf_by_name(user: User, shelf_name: str) -> Optional[ReadingShelf]:
        """
        Get a specific shelf by name for a user.
        
        Args:
            user: User instance
            shelf_name: Name of the shelf
            
        Returns:
            ReadingShelf instance or None
        """
        try:
            return ReadingShelf.objects.filter(user=user, name=shelf_name).first()
        except Exception as e:
            logger.error(f"Error fetching shelf: {str(e)}")
            return None
    
    @staticmethod
    def create_shelf(user: User, name: str, is_public: bool = True) -> Optional[ReadingShelf]:
        """
        Create a new reading shelf.
        
        Args:
            user: User creating the shelf
            name: Shelf name
            is_public: Whether shelf is public
            
        Returns:
            Created shelf or None
        """
        try:
            shelf = ReadingShelf.objects.create(
                user=user,
                name=name,
                is_public=is_public
            )
            logger.info(f"Shelf '{name}' created for user {user.username}")
            return shelf
        except Exception as e:
            logger.error(f"Error creating shelf: {str(e)}")
            return None
    
    @staticmethod
    def delete_shelf(shelf: ReadingShelf, user: User) -> bool:
        """
        Delete a shelf (only by owner).
        
        Args:
            shelf: Shelf to delete
            user: User attempting to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            if shelf.user != user:
                logger.warning(f"User {user.username} attempted to delete shelf {shelf.id} without permission")
                return False
            
            shelf.delete()
            logger.info(f"Shelf {shelf.id} deleted by {user.username}")
            return True
        except Exception as e:
            logger.error(f"Error deleting shelf: {str(e)}")
            return False
    
    @staticmethod
    def add_book_to_shelf(shelf: ReadingShelf, book: Book) -> bool:
        """
        Add a book to a shelf.
        
        Args:
            shelf: ReadingShelf instance
            book: Book to add
            
        Returns:
            True if added, False if already exists
        """
        try:
            return shelf.add_book(book)
        except Exception as e:
            logger.error(f"Error adding book to shelf: {str(e)}")
            return False
    
    @staticmethod
    def remove_book_from_shelf(shelf: ReadingShelf, book: Book) -> bool:
        """
        Remove a book from a shelf.
        
        Args:
            shelf: ReadingShelf instance
            book: Book to remove
            
        Returns:
            True if removed, False otherwise
        """
        try:
            return shelf.remove_book(book)
        except Exception as e:
            logger.error(f"Error removing book from shelf: {str(e)}")
            return False
    
    @staticmethod
    def get_or_create_default_shelves(user: User) -> dict:
        """
        Get or create default shelves (Reading Now, To Read, Read).
        
        Args:
            user: User instance
            
        Returns:
            Dict with shelf names as keys
        """
        try:
            default_names = ["Reading Now", "To Read", "Read"]
            shelves = {}
            
            for name in default_names:
                shelf, created = ReadingShelf.objects.get_or_create(
                    user=user,
                    name=name,
                    defaults={"is_public": True}
                )
                shelves[name] = shelf
                if created:
                    logger.info(f"Default shelf '{name}' created for {user.username}")
            
            return shelves
        except Exception as e:
            logger.error(f"Error creating default shelves: {str(e)}")
            return {}
    
    @staticmethod
    def get_public_shelves(exclude_user: Optional[User] = None, limit: int = 20) -> QuerySet:
        """
        Get public shelves from other users.
        
        Args:
            exclude_user: User to exclude from results
            limit: Maximum number of shelves
            
        Returns:
            QuerySet of public shelves
        """
        try:
            shelves = ReadingShelf.objects.filter(is_public=True)
            if exclude_user:
                shelves = shelves.exclude(user=exclude_user)
            
            return shelves.select_related('user').prefetch_related('books')[:limit]
        except Exception as e:
            logger.error(f"Error fetching public shelves: {str(e)}")
            return ReadingShelf.objects.none()
    
    @staticmethod
    def get_books_in_shelf(shelf: ReadingShelf) -> List[Book]:
        """
        Get all books in a shelf.
        
        Args:
            shelf: ReadingShelf instance
            
        Returns:
            List of books
        """
        try:
            return shelf.get_books()
        except Exception as e:
            logger.error(f"Error fetching books in shelf: {str(e)}")
            return []
    
    @staticmethod
    def is_book_in_shelf(shelf: ReadingShelf, book: Book) -> bool:
        """
        Check if a book is in a shelf.
        
        Args:
            shelf: ReadingShelf instance
            book: Book to check
            
        Returns:
            True if book is in shelf, False otherwise
        """
        try:
            return shelf.books.filter(id=book.id).exists()
        except Exception as e:
            logger.error(f"Error checking book in shelf: {str(e)}")
            return False

