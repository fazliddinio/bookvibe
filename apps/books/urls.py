from django.urls import path
from . import views

app_name = "books"

urlpatterns = [
    path("", views.BooksView.as_view(), name="list"),
    path("<int:id>/", views.BookDetailView.as_view(), name="detail"),
    path("<int:id>/reviews/", views.AddReviewView.as_view(), name="reviews"),
    path(
        "<int:book_id>/reviews/<int:review_id>/delete/",
        views.DeleteReviewView.as_view(),
        name="delete-review",
    ),
    # URLs for comments
    path(
        "<int:book_id>/reviews/<int:review_id>/comment/",
        views.AddCommentView.as_view(),
        name="add-comment",
    ),
    path(
        "<int:book_id>/reviews/<int:review_id>/comments/<int:comment_id>/reply/",
        views.ReplyToCommentView.as_view(),
        name="reply-comment",
    ),
    # Book management
    path("add/", views.AddBookView.as_view(), name="add-book"),
    path("<int:book_id>/delete/", views.DeleteBookView.as_view(), name="delete-book"),
    # Review voting
    path(
        "<int:book_id>/reviews/<int:review_id>/vote/",
        views.VoteReviewView.as_view(),
        name="vote-review",
    ),
    # Purchase links management
    path(
        "<int:book_id>/purchase-links/add/",
        views.AddPurchaseLinkView.as_view(),
        name="add-purchase-link",
    ),
    path(
        "<int:book_id>/purchase-links/<int:link_id>/edit/",
        views.EditPurchaseLinkView.as_view(),
        name="edit-purchase-link",
    ),
    path(
        "<int:book_id>/purchase-links/<int:link_id>/delete/",
        views.DeletePurchaseLinkView.as_view(),
        name="delete-purchase-link",
    ),
]
