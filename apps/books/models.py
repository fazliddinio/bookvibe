from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#28a745")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        db_table = "genres"

    def __str__(self):
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        db_table = "authors"
        unique_together = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Book(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField()
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    publication_date = models.DateField(blank=True, null=True)
    publisher = models.CharField(max_length=200, blank=True, null=True)
    page_count = models.PositiveIntegerField(blank=True, null=True)
    language = models.CharField(max_length=50, default="English")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cover_image = models.ImageField(upload_to="book_covers/", blank=True, null=True)
    is_available = models.BooleanField(default=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="added_books",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        db_table = "books"
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["isbn"]),
            models.Index(fields=["genre"]),
            models.Index(fields=["publication_date"]),
        ]

    def __str__(self):
        return self.title

    def get_authors(self):
        """Get all authors for this book"""
        return [author.author for author in self.book_authors.all()]

    def get_primary_author(self):
        """Get the first author for this book"""
        authors = self.get_authors()
        if authors:
            return authors[0]
        return None

    def get_average_rating(self):
        """Get the average rating for this book"""
        reviews = self.reviews.all()
        if reviews:
            return round(
                sum(review.stars_given for review in reviews) / len(reviews), 1
            )
        return 0

    def get_total_reviews(self):
        """Get the total number of reviews for this book"""
        return self.reviews.count()


class BookAuthor(models.Model):
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="book_authors"
    )
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="author_books"
    )
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ["book", "author"]
        db_table = "book_authors"

    def __str__(self):
        return f"{self.book.title} by {self.author.full_name()}"


class BookReview(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="book_reviews"
    )
    comment = models.TextField(max_length=1000)
    stars_given = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        unique_together = ["book", "user"]
        ordering = ["-created_time"]
        db_table = "book_reviews"

    def __str__(self):
        return f"{self.user.username}'s review of {self.book.title}"

    def get_likes_count(self):
        """Get the total number of likes for this review"""
        return self.votes.filter(vote_type="like").count()

    def get_comments_count(self):
        """Get the total number of comments for this review"""
        return self.comments.count()

    def get_dislikes_count(self):
        """Get the total number of dislikes for this review"""
        return self.votes.filter(vote_type="dislike").count()

    def get_vote_score(self):
        """Get the vote score (likes - dislikes) for this review"""
        return self.get_likes_count() - self.get_dislikes_count()

    def get_user_vote(self, user):
        """Get the user's vote for this review"""
        if user is None or not user.is_authenticated:
            return None
        # Check if user has an ID (is saved to database)
        if not hasattr(user, "id") or user.id is None:
            return None
        try:
            vote = self.votes.get(user=user)
            return vote.vote_type
        except ReviewVote.DoesNotExist:
            return None


class ReviewVote(models.Model):
    VOTE_CHOICES = [
        ("like", "Like"),
        ("dislike", "Dislike"),
    ]

    review = models.ForeignKey(
        BookReview, on_delete=models.CASCADE, related_name="votes"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="review_votes"
    )
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["review", "user"]
        db_table = "review_votes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} {self.vote_type}s {self.review.user.username}'s review"


class ReviewComment(models.Model):
    review = models.ForeignKey(
        BookReview, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="review_comments",
    )
    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ["created_at"]
        db_table = "review_comments"

    def __str__(self):
        return f"{self.user.username}'s comment on {self.review.user.username}'s review"

    def get_replies(self):
        """Get all replies to this comment"""
        return self.replies.all()

    def get_replies_count(self):
        """Get the total number of replies to this comment"""
        return self.replies.count()


class BookPurchaseLink(models.Model):
    """Model for storing purchase links for books (e.g., Amazon, local bookstores, etc.)"""
    book = models.ForeignKey(
        Book, 
        on_delete=models.CASCADE, 
        related_name="purchase_links"
    )
    seller_name = models.CharField(
        max_length=100,
        help_text="Name of the seller (e.g., Amazon, Kitoblar.uz, etc.)"
    )
    url = models.URLField(
        max_length=500,
        help_text="Direct link to purchase the book"
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="added_purchase_links"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether this link has been verified by moderators"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_verified", "-created_at"]
        db_table = "book_purchase_links"
        indexes = [
            models.Index(fields=["book"]),
            models.Index(fields=["added_by"]),
        ]
    
    def __str__(self):
        return f"{self.seller_name} - {self.book.title}"
