from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.db import transaction
from .models import ReadingShelf
from apps.books.models import Book


def reading_lists_view(request):
    """View for managing reading lists"""
    # If user is not authenticated, show empty page with login prompt
    if not request.user.is_authenticated:
        context = {
            "currently_reading": [],
            "want_to_read": [],
            "already_read": [],
            "require_login": True,
        }
        return render(request, "reading_lists/lists.html", context)
    
    user = request.user

    # Get books from the three fixed categories
    reading_now_shelf = ReadingShelf.objects.filter(
        user=user, name="Reading Now"
    ).first()
    to_read_shelf = ReadingShelf.objects.filter(user=user, name="To Read").first()
    read_shelf = ReadingShelf.objects.filter(user=user, name="Read").first()

    # Get books for each category
    currently_reading = reading_now_shelf.get_books() if reading_now_shelf else []
    want_to_read = to_read_shelf.get_books() if to_read_shelf else []
    already_read = read_shelf.get_books() if read_shelf else []

    context = {
        "currently_reading": currently_reading,
        "want_to_read": want_to_read,
        "already_read": already_read,
        "require_login": False,
    }

    return render(request, "reading_lists/lists.html", context)


@login_required
def shelf_detail_view(request, shelf_id):
    """View for individual shelf details"""
    shelf = get_object_or_404(ReadingShelf, id=shelf_id, user=request.user)
    books = shelf.get_books()

    context = {
        "shelf": shelf,
        "books": books,
    }

    return render(request, "reading_lists/shelf_detail.html", context)


@login_required
def add_to_shelf_view(request, book_id):
    """Add a book to a shelf"""
    book = get_object_or_404(Book, id=book_id)
    shelf_name = request.POST.get("shelf_name", "Reading Now")

    shelf, created = ReadingShelf.objects.get_or_create(
        name=shelf_name, user=request.user
    )

    if shelf.add_book(book):
        messages.success(request, f'"{book.title}" {shelf_name}ga qo\'shildi')
    else:
        messages.info(request, f'"{book.title}" allaqachon {shelf_name}da')

    return redirect("reading_lists:lists")


@login_required
def remove_book_from_category(request, book_id, category_name):
    """Remove a book from a specific category"""
    book = get_object_or_404(Book, id=book_id)

    # Find the shelf for this category
    shelf = ReadingShelf.objects.filter(user=request.user, name=category_name).first()

    if shelf and shelf.remove_book(book):
        messages.success(request, f'"{book.title}" {category_name}dan o\'chirildi')
    else:
        messages.error(request, f"Kitob {category_name}da topilmadi")

    return redirect("reading_lists:lists")


@require_http_methods(["POST"])
@login_required
def create_shelf_view(request):
    """Create new reading shelf"""
    shelf_name = request.POST.get("shelf_name")
    # Checkbox sends "on" when checked, nothing when unchecked
    is_public = "is_public" in request.POST

    if not shelf_name:
        messages.error(request, "Javon nomi kiritilishi shart")
        return redirect("reading_lists:lists")

    with transaction.atomic():
        ReadingShelf.objects.create(
            name=shelf_name, user=request.user, is_public=is_public
        )
        messages.success(request, f'"{shelf_name}" javoni yaratildi')

    return redirect("reading_lists:lists")


@require_http_methods(["POST"])
@login_required
def delete_shelf_view(request, shelf_id):
    """Delete reading shelf"""
    shelf = get_object_or_404(ReadingShelf, id=shelf_id, user=request.user)
    shelf_name = shelf.name

    with transaction.atomic():
        shelf.delete()
        messages.success(request, f'"{shelf_name}" javoni o\'chirildi')

    return redirect("reading_lists:lists")


@login_required
def public_shelves_view(request):
    """View public shelves from other users"""
    shelves = (
        ReadingShelf.objects.filter(is_public=True)
        .exclude(user=request.user)
        .select_related("user")
        .prefetch_related("books")
    )

    # Paginate results
    paginator = Paginator(shelves, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
    }

    return render(request, "reading_lists/public_shelves.html", context)
