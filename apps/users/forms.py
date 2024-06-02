from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import UserProfile


class UserRegistrationForm(UserCreationForm):
    # Redefine username field without unique constraint to allow unverified re-registration
    username = forms.CharField(
        max_length=150,
        required=True,
        error_messages={
            'required': "Bu maydon to'ldirilishi shart.",
        }
    )
    
    email = forms.EmailField(
        required=True,
        help_text="Talab qilinadi. To'g'ri email manzilini kiriting.",
        widget=forms.EmailInput(attrs={"placeholder": "Email manzilingizni kiriting"}),
        error_messages={
            'required': "Bu maydon to'ldirilishi shart.",
            'invalid': "To'g'ri email manzilini kiriting.",
        }
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override widgets to add placeholders
        self.fields["username"].widget.attrs.update(
            {"placeholder": "Email manzilingizni kiriting"}
        )
        self.fields["password1"].widget.attrs.update(
            {"placeholder": "Parolni kiriting (kamida 6 ta belgi)"}
        )
        self.fields["password2"].widget.attrs.update(
            {"placeholder": "Parolni tasdiqlang"}
        )
        
        # Add Uzbek error messages
        self.fields["username"].error_messages = {
            'required': "Bu maydon to'ldirilishi shart.",
        }
        self.fields["password1"].error_messages = {
            'required': "Bu maydon to'ldirilishi shart.",
        }
        self.fields["password2"].error_messages = {
            'required': "Bu maydon to'ldirilishi shart.",
        }
        
        # Set Uzbek labels
        self.fields["username"].label = "Email"
        self.fields["password1"].label = "Parol"
        self.fields["password2"].label = "Parolni tasdiqlang"

        # Customize password validation
        self.fields["password1"].help_text = "Kamida 6 ta belgi talab qilinadi."
        self.fields["password2"].help_text = "Yuqoridagi parol bilan bir xil parolni kiriting."
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Ikki parol maydoni mos kelmadi.")
        return password2

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if len(password1) < 6:
            raise forms.ValidationError("Parol kamida 6 ta belgidan iborat bo'lishi kerak.")
        return password1

    def clean_email(self):
        from apps.users.models import PendingRegistration
        
        email = self.cleaned_data.get("email")
        
        # Check if email already exists in User table (fully registered)
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email manzil allaqachon ro'yxatdan o'tgan.")
        
        # Check if email has a pending registration
        pending = PendingRegistration.objects.filter(email=email).first()
        if pending:
            # Mark that we need to resend verification code for this pending registration
            self.pending_registration = pending
        
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        email = self.cleaned_data.get("email")
        if email:
            # Use email as username
            # Check if username (email) already exists
            if User.objects.filter(username=email).exists():
                raise forms.ValidationError("Bu email manzil allaqachon ro'yxatdan o'tgan.")
            return email
        return username

    def save(self, commit=True):
        """
        This method is NOT used anymore. Registration creates PendingRegistration, not User.
        Keeping it for compatibility but it should not be called.
        """
        raise NotImplementedError("Use PendingRegistration.create_pending() instead")


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Email manzilingizni kiriting"}),
        error_messages={
            'required': "Bu maydon to'ldirilishi shart.",
            'invalid': "To'g'ri email manzilini kiriting.",
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Parolni kiriting"}),
        error_messages={
            'required': "Bu maydon to'ldirilishi shart.",
        }
    )

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email and password:
            # Try to authenticate with email as username
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError("Email yoki parol noto'g'ri.")
            else:
                profile, created = UserProfile.objects.get_or_create(user=user)
        return self.cleaned_data


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Email manzilingizni kiriting"}),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email bilan foydalanuvchi topilmadi.")
        return email


class PasswordResetForm(forms.Form):
    password1 = forms.CharField(
        label="Yangi Parol",
        widget=forms.PasswordInput(attrs={"placeholder": "Yangi parolni kiriting"}),
    )
    password2 = forms.CharField(
        label="Parolni Tasdiqlang",
        widget=forms.PasswordInput(attrs={"placeholder": "Parolni qayta kiriting"}),
    )

    def clean(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Parollar mos kelmadi.")
        return self.cleaned_data


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Ismingizni kiriting", "class": "form-control"}
        ),
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Familiyangizni kiriting", "class": "form-control"}
        ),
    )

    class Meta:
        model = UserProfile
        fields = [
            "bio",
            "profile_picture",
        ]
        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "placeholder": "O'zingiz haqingizda yozing...",
                    "rows": 3,
                    "class": "form-control",
                }
            ),
            "profile_picture": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Update user fields
            profile.user.first_name = self.cleaned_data.get("first_name", "")
            profile.user.last_name = self.cleaned_data.get("last_name", "")
            profile.user.save()
            profile.save()
        return profile


class EmailVerificationCodeForm(forms.Form):
    verification_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "placeholder": "6 raqamli kodni kiriting",
                "maxlength": "6",
                "pattern": "[0-9]{6}",
                "inputmode": "numeric",
            }
        ),
        help_text="Emailingizga yuborilgan 6 raqamli kodni kiriting",
        error_messages={
            'required': "Bu maydon to'ldirilishi shart.",
            'min_length': "Tasdiqlash kodi 6 raqamdan iborat bo'lishi kerak.",
            'max_length': "Tasdiqlash kodi 6 raqamdan iborat bo'lishi kerak.",
            'invalid': "Faqat raqamlar kiritishingiz mumkin.",
        }
    )
    
    def clean_verification_code(self):
        code = self.cleaned_data.get('verification_code')
        if code and not code.isdigit():
            raise forms.ValidationError("Tasdiqlash kodi faqat raqamlardan iborat bo'lishi kerak.")
        if code and len(code) != 6:
            raise forms.ValidationError("Tasdiqlash kodi 6 raqamdan iborat bo'lishi kerak.")
        return code


class UsernameChangeForm(forms.Form):
    """Form for changing username"""

    new_username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Yangi foydalanuvchi nomini kiriting"}),
        help_text="Talab qilinadi. 150 ta belgi yoki undan kam. Faqat harflar, raqamlar va @/./+/-/_ belgilar.",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Joriy parolingizni kiriting"}
        ),
        help_text="O'zgarishni tasdiqlash uchun joriy parolingizni kiriting.",
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_username(self):
        new_username = self.cleaned_data.get("new_username")
        if User.objects.filter(username=new_username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Bu foydalanuvchi nomi allaqachon mavjud.")
        return new_username

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not self.user.check_password(password):
            raise forms.ValidationError("Parolingiz noto'g'ri kiritildi.")
        return password

    def save(self):
        self.user.username = self.cleaned_data["new_username"]
        self.user.save()
        return self.user


class PasswordChangeForm(forms.Form):
    """Form for changing password"""

    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Joriy parolni kiriting"}),
        help_text="Joriy parolingizni kiriting.",
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Yangi parolni kiriting"}),
        help_text="Kamida 6 ta belgi talab qilinadi.",
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Parolni qayta kiriting"}),
        help_text="Yuqoridagi parol bilan bir xil parolni kiriting.",
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Eski parol noto'g'ri kiritildi.")
        return old_password

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get("new_password1")
        if len(new_password1) < 6:
            raise forms.ValidationError("Parol kamida 6 ta belgidan iborat bo'lishi kerak.")
        return new_password1

    def clean(self):
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError("Ikki parol maydoni mos kelmadi.")
        return self.cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save()
        return self.user
