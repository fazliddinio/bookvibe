from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile_view, name="edit_profile"),
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
