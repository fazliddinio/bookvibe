from django import forms
from .models import BookReview, ReviewComment, Book, Author, BookPurchaseLink


class BookReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = ["stars_given", "comment"]
        widgets = {
            "stars_given": forms.Select(choices=[(i, i) for i in range(1, 6)]),
            "comment": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        }
        labels = {
            "stars_given": "Baholash",
            "comment": "Sizning Sharhingiz",
        }


class ReviewCommentForm(forms.ModelForm):
    class Meta:
        model = ReviewComment
        fields = ["content", "parent_comment"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-control",
                    "placeholder": "Izohingizni yozing...",
                }
            ),
            "parent_comment": forms.HiddenInput(),
        }
        labels = {
            "content": "Izoh",
        }

    def __init__(self, *args, **kwargs):
        self.review = kwargs.pop("review", None)
        self.parent_comment = kwargs.pop("parent_comment", None)
        super().__init__(*args, **kwargs)

        if self.parent_comment:
            self.fields["content"].widget.attrs[
                "placeholder"
            ] = f"{self.parent_comment.user.username}ga javob yozing..."


class AddBookForm(forms.ModelForm):
    author_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Muallifning to'liq ismi"}
        ),
        label="Muallif",
    )
    
    # Optional purchase link fields
    purchase_seller_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Amazon, Kitoblar.uz, va h.k."
            }
        ),
        label="Sotuvchi Nomi (Ixtiyoriy)",
    )
    
    purchase_url = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                "class": "form-control",
                "placeholder": "https://example.com/book-link"
            }
        ),
        label="Xarid Havolasi (Ixtiyoriy)",
    )

    class Meta:
        model = Book
        fields = [
            "title",
            "description",
            "isbn",
            "genre",
            "cover_image",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Kitob nomi"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Kitob tavsifi",
                }
            ),
            "isbn": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "ISBN (13 raqam) - Ixtiyoriy",
                }
            ),
            "genre": forms.Select(attrs={"class": "form-control"}),
            "cover_image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
        }
        labels = {
            "title": "Kitob Nomi",
            "description": "Tavsif",
            "isbn": "ISBN",
            "genre": "Janr",
            "cover_image": "Muqova Rasmi",
        }

    def clean_isbn(self):
        isbn = self.cleaned_data.get("isbn")
        if isbn:
            # Remove any spaces or hyphens from ISBN
            isbn = isbn.replace(" ", "").replace("-", "")

            # Check if ISBN is 13 digits
            if not isbn.isdigit() or len(isbn) != 13:
                raise forms.ValidationError("ISBN aynan 13 raqamdan iborat bo'lishi kerak.")

            # Check if ISBN already exists
            if Book.objects.filter(isbn=isbn).exists():
                raise forms.ValidationError("Bu ISBN raqamli kitob allaqachon mavjud.")

        return isbn if isbn else None

    def save(self, commit=True, user=None):
        book = super().save(commit=False)
        if user:
            book.added_by = user

        if commit:
            book.save()

            # Create or get author
            author_name = self.cleaned_data.get("author_name")
            if author_name:
                # Split the full name into first and last name
                name_parts = author_name.strip().split()
                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = " ".join(name_parts[1:])
                else:
                    first_name = author_name
                    last_name = ""

                author, created = Author.objects.get_or_create(
                    first_name=first_name, last_name=last_name
                )
                # Link author to book
                from .models import BookAuthor

                BookAuthor.objects.get_or_create(book=book, author=author)
            
            # Create purchase link if provided
            purchase_seller = self.cleaned_data.get("purchase_seller_name")
            purchase_url = self.cleaned_data.get("purchase_url")
            
            if purchase_seller and purchase_url and user:
                BookPurchaseLink.objects.create(
                    book=book,
                    seller_name=purchase_seller,
                    url=purchase_url,
                    added_by=user
                )

        return book


class BookPurchaseLinkForm(forms.ModelForm):
    class Meta:
        model = BookPurchaseLink
        fields = ["seller_name", "url"]
        widgets = {
            "seller_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Masalan: Amazon, Kitoblar.uz, Ozon.ru",
                }
            ),
            "url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://example.com/book-link",
                }
            ),
        }
        labels = {
            "seller_name": "Sotuvchi Nomi",
            "url": "Xarid Havolasi",
        }

    def clean_url(self):
        url = self.cleaned_data.get("url")
        if url:
            # Basic URL validation
            if not url.startswith(("http://", "https://")):
                raise forms.ValidationError(
                    "URL http:// yoki https:// bilan boshlanishi kerak."
                )
        return url
