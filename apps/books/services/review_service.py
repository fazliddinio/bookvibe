"""
Review Service - Business logic for book reviews, comments, and votes
Follows Single Responsibility Principle
"""
from typing import Optional, List, Dict
from django.db.models import QuerySet, Count, Q
from django.contrib.auth.models import User
from apps.books.models import Book, BookReview, ReviewComment, ReviewVote
import logging

logger = logging.getLogger(__name__)


class ReviewService:
    """Service class for review operations."""
    
    @staticmethod
    def get_reviews_for_book(
        book: Book,
        user: Optional[User] = None
    ) -> QuerySet:
        """
        Get all reviews for a book with vote scores, ordered by popularity.
        
        Args:
            book: Book instance
            user: Optional user to include their vote information
            
        Returns:
            QuerySet of reviews with annotations
        """
        try:
            reviews = book.reviews.all().annotate(
                vote_score=Count("votes", filter=Q(votes__vote_type="like"))
                - Count("votes", filter=Q(votes__vote_type="dislike"))
            ).order_by("-vote_score", "-created_time")
            
            return reviews.prefetch_related("comments__user__profile", "votes")
        except Exception as e:
            logger.error(f"Error fetching reviews for book {book.id}: {str(e)}")
            return BookReview.objects.none()
    
    @staticmethod
    def create_review(
        book: Book,
        user: User,
        stars_given: int,
        comment: str
    ) -> Optional[BookReview]:
        """
        Create a new book review.
        
        Args:
            book: Book to review
            user: User creating the review
            stars_given: Rating (1-5)
            comment: Review text
            
        Returns:
            Created review or None
        """
        try:
            # Check if review already exists
            existing = BookReview.objects.filter(book=book, user=user).first()
            if existing:
                logger.info(f"User {user.username} already reviewed book {book.id}")
                return None
            
            review = BookReview.objects.create(
                book=book,
                user=user,
                stars_given=stars_given,
                comment=comment
            )
            
            logger.info(f"Review created for book {book.id} by {user.username}")
            return review
            
        except Exception as e:
            logger.error(f"Error creating review: {str(e)}")
            return None
    
    @staticmethod
    def update_review(
        review: BookReview,
        stars_given: int,
        comment: str
    ) -> bool:
        """
        Update an existing review.
        
        Args:
            review: Review to update
            stars_given: New rating
            comment: New comment
            
        Returns:
            True if updated, False otherwise
        """
        try:
            review.stars_given = stars_given
            review.comment = comment
            review.save()
            
            logger.info(f"Review {review.id} updated")
            return True
        except Exception as e:
            logger.error(f"Error updating review {review.id}: {str(e)}")
            return False
    
    @staticmethod
    def delete_review(review: BookReview, user: User) -> bool:
        """
        Delete a review (only by owner).
        
        Args:
            review: Review to delete
            user: User attempting to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            if review.user != user:
                logger.warning(f"User {user.username} attempted to delete review {review.id} without permission")
                return False
            
            review.delete()
            logger.info(f"Review {review.id} deleted by {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting review {review.id}: {str(e)}")
            return False
    
    @staticmethod
    def get_user_review_for_book(book: Book, user: User) -> Optional[BookReview]:
        """
        Get a user's review for a specific book.
        
        Args:
            book: Book instance
            user: User instance
            
        Returns:
            Review or None
        """
        try:
            return BookReview.objects.filter(book=book, user=user).first()
        except Exception as e:
            logger.error(f"Error fetching user review: {str(e)}")
            return None


class ReviewCommentService:
    """Service class for review comment operations."""
    
    @staticmethod
    def create_comment(
        review: BookReview,
        user: User,
        content: str,
        parent_comment: Optional[ReviewComment] = None
    ) -> Optional[ReviewComment]:
        """
        Create a comment on a review.
        
        Args:
            review: Review to comment on
            user: User creating the comment
            content: Comment text
            parent_comment: Optional parent comment for replies
            
        Returns:
            Created comment or None
        """
        try:
            # Validate content length
            if not content or len(content) > 500:
                logger.warning(f"Invalid comment length: {len(content) if content else 0}")
                return None
            
            comment = ReviewComment.objects.create(
                review=review,
                user=user,
                content=content,
                parent_comment=parent_comment
            )
            
            logger.info(f"Comment created on review {review.id} by {user.username}")
            return comment
            
        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}")
            return None
    
    @staticmethod
    def get_comments_for_review(review: BookReview) -> QuerySet:
        """
        Get all top-level comments for a review.
        
        Args:
            review: Review instance
            
        Returns:
            QuerySet of comments
        """
        try:
            return review.comments.filter(
                parent_comment__isnull=True
            ).select_related('user').prefetch_related('replies__user').order_by('created_at')
        except Exception as e:
            logger.error(f"Error fetching comments for review {review.id}: {str(e)}")
            return ReviewComment.objects.none()


class ReviewVoteService:
    """Service class for review voting operations."""
    
    @staticmethod
    def vote_on_review(
        review: BookReview,
        user: User,
        vote_type: str
    ) -> Dict:
        """
        Vote on a review (like/dislike).
        
        Args:
            review: Review to vote on
            user: User voting
            vote_type: 'like' or 'dislike'
            
        Returns:
            Dict with success status and message
        """
        try:
            # Validate vote type
            if vote_type not in ['like', 'dislike']:
                return {"success": False, "message": "Invalid vote type"}
            
            # Check if user is voting on their own review
            if review.user == user:
                return {"success": False, "message": "Cannot vote on your own review"}
            
            # Check for existing vote
            existing_vote = ReviewVote.objects.filter(
                review=review, user=user
            ).first()
            
            if existing_vote:
                if existing_vote.vote_type == vote_type:
                    # Remove vote (toggle off)
                    existing_vote.delete()
                    logger.info(f"Vote removed from review {review.id} by {user.username}")
                    return {"success": True, "message": "Vote removed", "action": "removed"}
                else:
                    # Change vote
                    existing_vote.vote_type = vote_type
                    existing_vote.save()
                    logger.info(f"Vote changed on review {review.id} by {user.username}")
                    return {"success": True, "message": "Vote updated", "action": "updated"}
            else:
                # Create new vote
                ReviewVote.objects.create(
                    review=review,
                    user=user,
                    vote_type=vote_type
                )
                logger.info(f"New vote on review {review.id} by {user.username}")
                return {"success": True, "message": "Vote recorded", "action": "created"}
                
        except Exception as e:
            logger.error(f"Error voting on review {review.id}: {str(e)}")
            return {"success": False, "message": "Error processing vote"}
    
    @staticmethod
    def get_vote_counts(review: BookReview) -> Dict:
        """
        Get vote counts for a review.
        
        Args:
            review: Review instance
            
        Returns:
            Dict with like and dislike counts
        """
        try:
            likes = review.votes.filter(vote_type="like").count()
            dislikes = review.votes.filter(vote_type="dislike").count()
            
            return {
                "likes": likes,
                "dislikes": dislikes,
                "score": likes - dislikes
            }
        except Exception as e:
            logger.error(f"Error getting vote counts for review {review.id}: {str(e)}")
            return {"likes": 0, "dislikes": 0, "score": 0}

