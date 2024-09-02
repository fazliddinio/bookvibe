from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import date


class ReadingHabit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reading_habits'
    )
    date = models.DateField(default=date.today)
    pages_read = models.PositiveIntegerField(default=0)
    minutes_read = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        db_table = 'reading_habits'
        indexes = [
            models.Index(fields=['user', '-date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {'✓' if self.completed else '✗'}"


class UserInterest(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interests'
    )
    preferred_genres = models.JSONField(default=list, blank=True)
    preferred_authors = models.JSONField(default=list, blank=True)
    reading_preferences = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_interests'
    
    def __str__(self):
        return f"{self.user.username}'s interests"

