from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile_view, name="edit_profile"),
    # Email verification
    path("verify-email/<uuid:token>/", views.verify_email_view, name="verify_email"),
    path("verify-email-code/", views.verify_email_code_view, name="verify_email_code"),
    path(
        "resend-verification/",
        views.resend_verification_email_view,
        name="resend_verification",
    ),
    # Password reset
    path(
        "password-reset/",
        views.password_reset_request_view,
        name="password_reset_request",
    ),
    path(
        "reset-password/<uuid:token>/", views.password_reset_view, name="password_reset"
    ),
    # API endpoints
    # Username and password change
    path("change-username/", views.change_username_view, name="change_username"),
    path("change-password/", views.change_password_view, name="change_password"),
    # Review management
    path(
        "delete-review/<int:review_id>/", views.delete_review_view, name="delete_review"
    ),
    # User profile viewing
    path("profile/<int:user_id>/", views.view_user_profile, name="view_profile"),
]
