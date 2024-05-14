from django.contrib import admin
from .models import (
    Genre,
    Author,
    Book,
    BookAuthor,
    BookReview,
    ReviewVote,
    ReviewComment,
    BookPurchaseLink,
)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ["name", "color", "created_at"]
    search_fields = ["name"]
    list_filter = ["created_at"]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email", "nationality", "created_at"]
    search_fields = ["first_name", "last_name", "email"]
    list_filter = ["nationality", "created_at"]
    ordering = ["last_name", "first_name"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "genre",
        "isbn",
        "publication_date",
        "is_available",
        "created_at",
    ]
    search_fields = ["title", "isbn", "description"]
    list_filter = ["genre", "is_available", "publication_date", "created_at"]
    ordering = ["title"]


@admin.register(BookAuthor)
class BookAuthorAdmin(admin.ModelAdmin):
    list_display = ["book", "author", "is_primary", "created_at"]
    list_filter = ["is_primary", "created_at"]
    search_fields = ["book__title", "author__first_name", "author__last_name"]


@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    list_display = ["book", "user", "stars_given", "is_approved", "created_time"]
    list_filter = ["stars_given", "is_approved", "created_time"]
    search_fields = ["book__title", "user__username", "comment"]
    ordering = ["-created_time"]


@admin.register(ReviewVote)
class ReviewVoteAdmin(admin.ModelAdmin):
    list_display = ["review", "user", "vote_type", "created_at"]
    list_filter = ["vote_type", "created_at"]
    search_fields = ["review__book__title", "user__username"]
    ordering = ["-created_at"]


@admin.register(ReviewComment)
class ReviewCommentAdmin(admin.ModelAdmin):
    list_display = ["review", "user", "parent_comment", "is_approved", "created_at"]
    list_filter = ["is_approved", "created_at"]
    search_fields = ["content", "review__book__title", "user__username"]
    ordering = ["-created_at"]


@admin.register(BookPurchaseLink)
class BookPurchaseLinkAdmin(admin.ModelAdmin):
    list_display = ["book", "seller_name", "added_by", "is_verified", "created_at"]
    list_filter = ["is_verified", "created_at"]
    search_fields = ["book__title", "seller_name", "url", "added_by__username"]
    ordering = ["-is_verified", "-created_at"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        ("Kitob Ma'lumotlari", {
            "fields": ("book", "seller_name", "url")
        }),
        ("Qo'shimcha", {
            "fields": ("added_by", "is_verified", "created_at", "updated_at")
        }),
    )
