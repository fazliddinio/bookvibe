from django.contrib import admin
from .models import ReadingShelf, ShelfBook


@admin.register(ReadingShelf)
class ReadingShelfAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "get_book_count", "is_public", "created_at"]
    list_filter = ["is_public", "created_at"]
    search_fields = ["name", "user__username"]
    ordering = ["-created_at"]

    def get_book_count(self, obj):
        return obj.get_book_count()

    get_book_count.short_description = "Books"


@admin.register(ShelfBook)
class ShelfBookAdmin(admin.ModelAdmin):
    list_display = ["shelf", "book", "added_at"]
    list_filter = ["added_at"]
    search_fields = ["shelf__name", "book__title"]
    ordering = ["-added_at"]
