from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.books.models import Book, BookReview


class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('review', 'Review'),
        ('book_add', 'Book Added'),
        ('shelf_add', 'Added to Shelf'),
        ('reading_start', 'Started Reading'),
        ('reading_complete', 'Completed Reading'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True
    )
    review = models.ForeignKey(
        BookReview,
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Activities'
        db_table = 'feed_activities'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.created_at}"

