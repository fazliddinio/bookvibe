from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ShelfBook
from apps.feed.models import Activity


@receiver(post_save, sender=ShelfBook)
def create_shelf_activity(sender, instance, created, **kwargs):
    """Create an activity when a user adds a book to a shelf"""
    if created:
        # Translate shelf names to Uzbek
        shelf_translations = {
            'Reading Now': "O'qiyapman",
            'To Read': "O'qimoqchiman",
            'Read': "O'qilgan",
            'Already Read': "O'qilgan"
        }
        
        shelf_name_uz = shelf_translations.get(instance.shelf.name, instance.shelf.name)
        
        Activity.objects.create(
            user=instance.shelf.user,
            activity_type='shelf_add',
            book=instance.book,
            description=f"{shelf_name_uz} javoniga qo'shildi"
        )

