from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Book, BookReview
from apps.feed.models import Activity


@receiver(post_save, sender=BookReview)
def create_review_activity(sender, instance, created, **kwargs):
    """Create an activity when a user posts a review"""
    if created:
        Activity.objects.create(
            user=instance.user,
            activity_type='review',
            book=instance.book,
            review=instance,
            description=f"{instance.stars_given}/5 yulduz baho berdi"
        )


@receiver(post_save, sender=Book)
def create_book_activity(sender, instance, created, **kwargs):
    """Create an activity when a user adds a new book"""
    if created and instance.added_by:
        Activity.objects.create(
            user=instance.added_by,
            activity_type='book_add',
            book=instance,
            description=f"To'plamga yangi kitob qo'shdi"
        )

