from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.contrib.auth import get_user_model


from .models import Book, Genre, BookReview, ReviewComment, ReviewVote, BookPurchaseLink
from .forms import BookReviewForm, ReviewCommentForm, AddBookForm, BookPurchaseLinkForm

User = get_user_model()


class BooksView(View):
    def get(self, request):
        books = Book.objects.select_related("genre").all()
        search_query = request.GET.get("q", "")
        genre_filter = request.GET.get("genre", "")

        if search_query:
            books = books.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(isbn__icontains=search_query)
            )

        if genre_filter:
            books = books.filter(genre_id=genre_filter)

        # Pagination with 14 books per page
        page_size = 14
        paginator = Paginator(books, page_size)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # Get all genres for the filter
        genres = Genre.objects.all()
        
        # Get real-time database stats
        total_books = Book.objects.count()
        total_readers = User.objects.filter(is_active=True).count()
        total_reviews = BookReview.objects.count()

        return render(
            request,
            "books/list.html",
            {
                "page_obj": page_obj,
                "search_query": search_query,
                "genre_filter": genre_filter,
                "genres": genres,
                "total_books": total_books,
                "total_readers": total_readers,
                "total_reviews": total_reviews,
            },
        )


class BookDetailView(View):
    def get(self, request, id):
        try:
            book = Book.objects.get(id=id)
            review_form = BookReviewForm()
            comment_form = ReviewCommentForm()

            # Get all reviews for this book, ordered by vote score (likes - dislikes) then by creation time
            reviews = (
                book.reviews.all()
                .annotate(
                    vote_score=Count("votes", filter=Q(votes__vote_type="like"))
                    - Count("votes", filter=Q(votes__vote_type="dislike"))
                )
                .order_by("-vote_score", "-created_time")
            )

            # Get user's existing review if any
            user_review = None
            if hasattr(request, "user") and request.user.is_authenticated:
                try:
                    user_review = book.reviews.filter(user=request.user).first()
                except Exception:
                    pass

            # Calculate additional context variables before evaluating queryset
            total_reviews = reviews.count()
            avg_rating = (
                reviews.aggregate(avg_rating=Avg("stars_given"))["avg_rating"] or 0
            )
            
            # Now evaluate the queryset and add user vote information
            reviews = reviews.prefetch_related("comments__user__profile")
            if hasattr(request, "user") and request.user.is_authenticated:
                for review in reviews:
                    try:
                        review.user_vote = review.get_user_vote(request.user)
                    except Exception:
                        review.user_vote = None

            # Get related/recommended books using the recommendation service
            from .services.recommendations import RecommendationService
            
            related_books = RecommendationService.get_related_books(book, limit=6)
            personalized_recommendations = []
            
            if hasattr(request, "user") and request.user.is_authenticated:
                personalized_recommendations = RecommendationService.get_personalized_recommendations(
                    request.user, limit=4
                )

            # Get purchase links for this book
            purchase_links = book.purchase_links.select_related("added_by").all()
            purchase_link_form = BookPurchaseLinkForm()
            
            return render(
                request,
                "books/detail.html",
                {
                    "book": book,
                    "review_form": review_form,
                    "comment_form": comment_form,
                    "reviews": reviews,
                    "user_review": user_review,
                    "total_reviews": total_reviews,
                    "avg_rating": round(avg_rating, 1),
                    "related_books": related_books,
                    "personalized_recommendations": personalized_recommendations,
                    "purchase_links": purchase_links,
                    "purchase_link_form": purchase_link_form,
                },
            )
        except Book.DoesNotExist:
            messages.error(request, "Kitob topilmadi.")
            return redirect("books:list")


class AddReviewView(LoginRequiredMixin, View):
    def post(self, request, id):
        try:
            book = Book.objects.get(id=id)
            review_form = BookReviewForm(data=request.POST)

            if review_form.is_valid():
                # Check if user already reviewed this book
                existing_review = BookReview.objects.filter(
                    book=book, user=request.user
                ).first()
                if existing_review:
                    # Update existing review
                    existing_review.stars_given = review_form.cleaned_data[
                        "stars_given"
                    ]
                    existing_review.comment = review_form.cleaned_data["comment"]
                    existing_review.save()
                    messages.success(
                        request, "Sharhingiz muvaffaqiyatli yangilandi!"
                    )
                else:
                    # Create new review
                    BookReview.objects.create(
                        book=book,
                        user=request.user,
                        stars_given=review_form.cleaned_data["stars_given"],
                        comment=review_form.cleaned_data["comment"],
                    )
                    messages.success(
                        request, "Sharhingiz muvaffaqiyatli qo'shildi!"
                    )

                return redirect(reverse("books:detail", kwargs={"id": book.id}) + "#reviews-section")
            else:
                messages.error(request, "Iltimos, sharhdagi xatolarni to'g'rilang.")
                return redirect(reverse("books:detail", kwargs={"id": book.id}) + "#reviews-section")

        except Book.DoesNotExist:
            messages.error(request, "Kitob topilmadi.")
            return redirect("books:list")


class DeleteReviewView(LoginRequiredMixin, View):
    def post(self, request, book_id, review_id):
        try:
            book = Book.objects.get(id=book_id)
            review = book.reviews.get(id=review_id)

            # Check if user owns this review
            if review.user != request.user:
                messages.error(request, "Siz faqat o'z sharhlaringizni o'chirishingiz mumkin.")
                return redirect(reverse("books:detail", kwargs={"id": book_id}))

            review.delete()
            messages.success(request, "Sharhingiz muvaffaqiyatli o'chirildi!")
            return redirect(reverse("books:detail", kwargs={"id": book_id}))

        except (Book.DoesNotExist, BookReview.DoesNotExist):
            messages.error(request, "Sharh topilmadi.")
            return redirect("books:list")


class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, book_id, review_id):
        try:
            book = Book.objects.get(id=book_id)
            review = book.reviews.get(id=review_id)

            # Get the content directly from POST data
            content = request.POST.get("content", "").strip()

            if not content:
                messages.error(request, "Iltimos, izoh kiriting.")
                return redirect(reverse("books:detail", kwargs={"id": book_id}) + f"#review-{review_id}")

            if len(content) > 500:
                messages.error(request, "Izoh juda uzun. Maksimal 500 belgi.")
                return redirect(reverse("books:detail", kwargs={"id": book_id}) + f"#review-{review_id}")

            # Create comment directly
            ReviewComment.objects.create(
                review=review, user=request.user, content=content
            )

            messages.success(request, "Izohingiz qo'shildi!")
            return redirect(reverse("books:detail", kwargs={"id": book_id}) + f"#review-{review_id}")

        except (Book.DoesNotExist, BookReview.DoesNotExist):
            messages.error(request, "Sharh topilmadi.")
            return redirect("books:list")


class ReplyToCommentView(LoginRequiredMixin, View):
    def get(self, request, book_id, review_id, comment_id):
        """Redirect GET requests to the book detail page"""
        return redirect("books:detail", id=book_id)
    
    def post(self, request, book_id, review_id, comment_id):
        try:
            book = Book.objects.get(id=book_id)
            review = BookReview.objects.get(id=review_id, book=book)
            parent_comment = ReviewComment.objects.get(id=comment_id, review=review)

            # Get the content directly from POST data
            content = request.POST.get("content", "").strip()

            if not content:
                messages.error(request, "Iltimos, javob kiriting.")
                return redirect(reverse("books:detail", kwargs={"id": book_id}) + f"#comment-{comment_id}")

            if len(content) > 500:
                messages.error(request, "Javob juda uzun. Maksimal 500 belgi.")
                return redirect(reverse("books:detail", kwargs={"id": book_id}) + f"#comment-{comment_id}")

            # Create reply
            ReviewComment.objects.create(
                review=review,
                user=request.user,
                parent_comment=parent_comment,
                content=content,
            )

            messages.success(request, "Javobingiz qo'shildi!")
            return redirect(reverse("books:detail", kwargs={"id": book_id}) + f"#comment-{comment_id}")

        except Book.DoesNotExist:
            messages.error(request, "Kitob topilmadi.")
            return redirect("books:list")
        except BookReview.DoesNotExist:
            messages.error(request, "Sharh topilmadi.")
            return redirect("books:detail", id=book_id)
        except ReviewComment.DoesNotExist:
            messages.error(request, "Izoh topilmadi.")
            return redirect("books:detail", id=book_id)
        except Exception as e:
            messages.error(request, f"Javobingizni qo'shishda xatolik yuz berdi: {str(e)}")
            return redirect("books:detail", id=book_id)


class AddBookView(LoginRequiredMixin, View):
    def get(self, request):
        form = AddBookForm()
        genres = Genre.objects.all()
        return render(request, "books/add_book.html", {"form": form, "genres": genres})

    def post(self, request):
        form = AddBookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(user=request.user)
            messages.success(
                request, f"'{book.title}' kitobi muvaffaqiyatli qo'shildi!"
            )
            return redirect(reverse("books:detail", kwargs={"id": book.id}))
        else:
            genres = Genre.objects.all()
            return render(
                request, "books/add_book.html", {"form": form, "genres": genres}
            )


class DeleteBookView(LoginRequiredMixin, View):
    def post(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)

            # Check if user can delete this book
            if not (book.added_by == request.user or request.user.is_staff):
                messages.error(request, "Siz faqat o'zingiz qo'shgan kitoblarni o'chirishingiz mumkin.")
                return redirect(reverse("books:detail", kwargs={"id": book_id}))

            book_title = book.title
            book.delete()
            messages.success(
                request, f"'{book_title}' kitobi muvaffaqiyatli o'chirildi!"
            )
            return redirect("books:list")

        except Book.DoesNotExist:
            messages.error(request, "Kitob topilmadi.")
            return redirect("books:list")


class VoteReviewView(LoginRequiredMixin, View):
    def post(self, request, book_id, review_id):
        try:
            book = Book.objects.get(id=book_id)
            review = book.reviews.get(id=review_id)
            vote_type = request.POST.get("vote_type")  # "like" or "dislike"

            if vote_type not in ["like", "dislike"]:
                messages.error(request, "Noto'g'ri ovoz turi.")
                return redirect(reverse("books:detail", kwargs={"id": book_id}) + f"#review-{review_id}")

            # Check if user is voting on their own review
            if review.user == request.user:
                messages.error(request, "O'z sharhingizga ovoz bera olmaysiz.")
                return redirect(reverse("books:detail", kwargs={"id": book_id}) + f"#review-{review_id}")

            # Check if user already voted
            existing_vote = ReviewVote.objects.filter(
                review=review, user=request.user
            ).first()

            if existing_vote:
                if existing_vote.vote_type == vote_type:
                    # User is trying to vote the same way, so remove the vote
                    existing_vote.delete()
                    messages.success(request, f"Sizning ovozingiz o'chirildi.")
                else:
                    # User is changing their vote
                    existing_vote.vote_type = vote_type
                    existing_vote.save()
                    messages.success(
                        request, f"Sizning ovozingiz o'zgartirildi."
                    )
            else:
                # Create new vote
                ReviewVote.objects.create(
                    review=review, user=request.user, vote_type=vote_type
                )
                messages.success(request, f"Sizning ovozingiz qabul qilindi!")

            return redirect(reverse("books:detail", kwargs={"id": book_id}) + f"#review-{review_id}")

        except (Book.DoesNotExist, BookReview.DoesNotExist):
            messages.error(request, "Sharh topilmadi.")
            return redirect("books:list")


class AddPurchaseLinkView(LoginRequiredMixin, View):
    """Add a purchase link to a book (only for registered users)"""
    def post(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
            form = BookPurchaseLinkForm(data=request.POST)
            
            if form.is_valid():
                purchase_link = form.save(commit=False)
                purchase_link.book = book
                purchase_link.added_by = request.user
                purchase_link.save()
                
                messages.success(
                    request,
                    f"Xarid havolasi muvaffaqiyatli qo'shildi! ({purchase_link.seller_name})"
                )
            else:
                # Display form errors
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
            
            return redirect(reverse("books:detail", kwargs={"id": book_id}))
        
        except Book.DoesNotExist:
            messages.error(request, "Kitob topilmadi.")
            return redirect("books:list")


class EditPurchaseLinkView(LoginRequiredMixin, View):
    """Edit a purchase link (only by the user who added it)"""
    def post(self, request, book_id, link_id):
        try:
            book = Book.objects.get(id=book_id)
            purchase_link = book.purchase_links.get(id=link_id)
            
            # Only the user who added the link can edit it
            if purchase_link.added_by != request.user:
                messages.error(request, "Siz faqat o'zingiz qo'shgan havolalarni tahrirlashingiz mumkin.")
                return redirect(reverse("books:detail", kwargs={"id": book_id}))
            
            form = BookPurchaseLinkForm(data=request.POST, instance=purchase_link)
            
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    f"Xarid havolasi muvaffaqiyatli yangilandi! ({purchase_link.seller_name})"
                )
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
            
            return redirect(reverse("books:detail", kwargs={"id": book_id}))
        
        except (Book.DoesNotExist, BookPurchaseLink.DoesNotExist):
            messages.error(request, "Havola topilmadi.")
            return redirect("books:list")


class DeletePurchaseLinkView(LoginRequiredMixin, View):
    """Delete a purchase link (only by the user who added it)"""
    def post(self, request, book_id, link_id):
        try:
            book = Book.objects.get(id=book_id)
            purchase_link = book.purchase_links.get(id=link_id)
            
            # Only the user who added the link can delete it
            if purchase_link.added_by != request.user:
                messages.error(request, "Siz faqat o'zingiz qo'shgan havolalarni o'chirishingiz mumkin.")
                return redirect(reverse("books:detail", kwargs={"id": book_id}))
            
            seller_name = purchase_link.seller_name
            purchase_link.delete()
            messages.success(
                request,
                f"Xarid havolasi o'chirildi ({seller_name})."
            )
            
            return redirect(reverse("books:detail", kwargs={"id": book_id}))
        
        except (Book.DoesNotExist, BookPurchaseLink.DoesNotExist):
            messages.error(request, "Havola topilmadi.")
            return redirect("books:list")
