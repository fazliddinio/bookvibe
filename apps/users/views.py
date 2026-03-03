from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    UserProfileForm,
    UsernameChangeForm,
    PasswordChangeForm,
)
from .models import UserProfile


def register_view(request):
    """
    Simple registration: email + password.
    If email already exists, update the password.
    """
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.filter(email=email).first()
            if user:
                # Email exists — update password
                user.set_password(password)
                user.save()
            else:
                # Create new user
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                )
                UserProfile.objects.get_or_create(user=user)

            # Log in and redirect
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                messages.success(request, "Xush kelibsiz!")
                return redirect('feed:home')
    else:
        form = UserRegistrationForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    """
    User login view with comprehensive error handling and session management.
    Handles both verified and unverified accounts appropriately.
    """
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            
            try:
                # Try to authenticate
                user = authenticate(request, username=email, password=password)
                
                if user is not None:
                    # User authenticated successfully (all users in DB are verified)
                    profile, created = UserProfile.objects.get_or_create(user=user)

                    # Log user in
                    login(request, user)
                    
                    messages.success(request, f"Xush kelibsiz!")
                    
                    # Redirect to 'next' parameter or home
                    next_url = request.GET.get('next', '')
                    if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                        return redirect(next_url)
                    return redirect('feed:home')
                else:
                    # Authentication failed - wrong password or user doesn't exist
                    messages.error(request, "Email yoki parol noto'g'ri.")
                    
            except Exception as e:
                # Log the error
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Login error for {email}: {str(e)}")
                messages.error(request, "Tizimga kirishda xatolik yuz berdi. Qaytadan urinib ko'ring.")
        else:
            # Form is not valid
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)
    else:
        form = UserLoginForm()

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    """
    User logout view with session cleanup and proper redirect.
    """
    # Clear any verification email from session
    if 'verification_email' in request.session:
        del request.session['verification_email']
    
    # Get username before logout for personalized message
    username = None
    if request.user.is_authenticated:
        username = request.user.username[:20] if hasattr(request.user, 'username') else None
    
    # Logout user
    logout(request)
    
    # Show personalized message if possible
    if username:
        messages.success(request, f"Xayr, {username}! Tez orada ko'rishguncha.")
    else:
        messages.success(request, "Siz muvaffaqiyatli tizimdan chiqdingiz.")
    
    return redirect("feed:home")


@login_required
def profile_view(request):
    """Display user profile with option to edit"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Get user's reviews for display
    from apps.books.models import BookReview

    reviews = BookReview.objects.filter(user=request.user).order_by("-created_time")
    total_reviews = reviews.count()

    context = {
        "profile": profile,
        "reviews": reviews,
        "total_reviews": total_reviews,
    }

    return render(request, "users/profile_display.html", context)


@login_required
def edit_profile_view(request):
    """Edit user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil muvaffaqiyatli yangilandi!")
            return redirect("users:profile")
    else:
        form = UserProfileForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
    }

    return render(request, "users/profile_edit.html", context)


@login_required
def change_username_view(request):
    """View for changing username"""
    if request.method == "POST":
        form = UsernameChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Foydalanuvchi nomi muvaffaqiyatli o'zgartirildi!")
            return redirect("users:profile")
    else:
        form = UsernameChangeForm(request.user)

    return render(request, "users/change_username.html", {"form": form})


@login_required
def change_password_view(request):
    """View for changing password"""
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Parol muvaffaqiyatli o'zgartirildi!")
            return redirect("users:profile")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "users/change_password.html", {"form": form})


@login_required
def delete_review_view(request, review_id):
    """Delete a user's review"""
    try:
        from apps.books.models import BookReview

        review = BookReview.objects.get(id=review_id, user=request.user)
        book_title = review.book.title
        review.delete()
        messages.success(request, f"'{book_title}' uchun sharhingiz o'chirildi.")
    except BookReview.DoesNotExist:
        messages.error(
            request, "Sharh topilmadi yoki uni o'chirish huquqingiz yo'q."
        )
    except Exception:
        messages.error(request, "Sharhni o'chirishda xatolik yuz berdi.")

    return redirect("users:profile")


def view_user_profile(request, user_id):
    """View another user's profile"""
    try:
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        from apps.books.models import BookReview

        # Get the user whose profile we're viewing
        profile_user = User.objects.get(id=user_id)
        profile, created = UserProfile.objects.get_or_create(user=profile_user)

        # Get user's reviews for display
        all_reviews = BookReview.objects.filter(user=profile_user).order_by(
            "-created_time"
        )
        
        total_reviews = all_reviews.count()

        # Paginate reviews - 10 per page
        paginator = Paginator(all_reviews, 10)
        page = request.GET.get('page', 1)
        
        try:
            reviews = paginator.page(page)
        except PageNotAnInteger:
            reviews = paginator.page(1)
        except EmptyPage:
            reviews = paginator.page(paginator.num_pages)

        # Calculate user stats from ALL reviews, not just the displayed ones
        total_likes_received = 0
        for review in all_reviews:
            total_likes_received += review.get_likes_count()

        context = {
            "profile_user": profile_user,
            "profile": profile,
            "reviews": reviews,
            "total_reviews": total_reviews,
            "total_likes_received": total_likes_received,
        }

        return render(request, "users/view_profile.html", context)

    except User.DoesNotExist:
        messages.error(request, "Foydalanuvchi topilmadi.")
        return redirect("books:list")
