from django.contrib import admin
from apps.users.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "updated_at"]
    search_fields = ["user__username", "user__first_name", "user__last_name"]
    list_filter = ["created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at"]
