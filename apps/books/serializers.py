"""
DRF Serializers for Books API
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from apps.books.models import Book, Genre, Author, BookAuthor, BookReview, ReviewComment, ReviewVote


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "color", "created_at"]


class AuthorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Author
        fields = ["id", "first_name", "last_name", "full_name", "email", "nationality", "bio", "created_at"]


class BookAuthorSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    
    class Meta:
        model = BookAuthor
        fields = ["author", "is_primary"]


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for nested serialization"""
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class ReviewCommentSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = ReviewComment
        fields = ["id", "user", "content", "parent_comment", "replies", "is_approved", "created_at"]
        read_only_fields = ["user", "is_approved", "created_at"]
    
    def get_replies(self, obj):
        if obj.parent_comment is None:
            replies = obj.get_replies()
            return ReviewCommentSerializer(replies, many=True).data
        return []


class ReviewVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewVote
        fields = ["id", "vote_type", "created_at"]


class BookReviewSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    comments = ReviewCommentSerializer(many=True, read_only=True)
    upvotes_count = serializers.IntegerField(read_only=True)
    downvotes_count = serializers.IntegerField(read_only=True)
    user_vote = serializers.SerializerMethodField()
    
    class Meta:
        model = BookReview
        fields = [
            "id", "user", "book", "stars_given", "comment", 
            "upvotes_count", "downvotes_count", "user_vote",
            "comments", "is_approved", "created_time", "updated_time"
        ]
        read_only_fields = ["user", "book", "is_approved", "created_time", "updated_time"]
    
    def get_user_vote(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            vote = ReviewVote.objects.filter(review=obj, user=request.user).first()
            return vote.vote_type if vote else None
        return None


class BookListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for book lists"""
    genre = GenreSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    primary_author = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            "id", "title", "genre", "primary_author", "cover_image",
            "publication_date", "average_rating", "review_count", "is_available"
        ]
    
    def get_average_rating(self, obj):
        return obj.get_average_rating()
    
    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()
    
    def get_primary_author(self, obj):
        author = obj.get_primary_author()
        return AuthorSerializer(author).data if author else None


class BookDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single book view"""
    genre = GenreSerializer(read_only=True)
    authors = BookAuthorSerializer(many=True, read_only=True, source="book_authors")
    reviews = BookReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    added_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Book
        fields = [
            "id", "title", "description", "genre", "authors", "isbn",
            "publication_date", "cover_image", "page_count", "language",
            "is_available", "average_rating", "review_count", "reviews",
            "added_by", "created_at", "updated_at"
        ]
        read_only_fields = ["added_by", "created_at", "updated_at"]
    
    def get_average_rating(self, obj):
        return obj.get_average_rating()
    
    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()


class BookCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating books"""
    
    class Meta:
        model = Book
        fields = [
            "title", "description", "genre", "isbn", "publication_date",
            "cover_image", "page_count", "language", "is_available"
        ]
    
    def create(self, validated_data):
        validated_data["added_by"] = self.context["request"].user
        return super().create(validated_data)

