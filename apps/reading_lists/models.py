from django.db import models
from django.conf import settings
from apps.books.models import Book
from collections import defaultdict
from typing import List, Dict


class ReadingShelf(models.Model):
    """Reading shelf model"""

    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reading_shelves",
    )
    books = models.ManyToManyField(Book, through="ShelfBook", related_name="shelves")
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["name", "user"]
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username}'s {self.name}"

    def add_book(self, book: Book) -> bool:
        """Add a book to the shelf"""
        if not self.books.filter(id=book.id).exists():
            ShelfBook.objects.create(shelf=self, book=book)
            return True
        return False

    def remove_book(self, book: Book) -> bool:
        """Remove a book from the shelf"""
        if self.books.filter(id=book.id).exists():
            ShelfBook.objects.filter(shelf=self, book=book).delete()
            return True
        return False

    def get_books(self) -> List[Book]:
        """Get all books in the shelf"""
        return list(self.books.all())

    def get_book_count(self) -> int:
        """Get the number of books in the shelf"""
        return self.books.count()

    def get_books_by_genre(self) -> Dict[str, List[Book]]:
        """Group books by genre using collections.defaultdict"""
        genre_books = defaultdict(list)
        for book in self.books.all():
            genre_books[book.genre.name].append(book)
        return dict(genre_books)


class ShelfBook(models.Model):
    """Through model for ReadingShelf and Book relationship"""

    shelf = models.ForeignKey(ReadingShelf, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ["shelf", "book"]
        ordering = ["-added_at"]
