from django.contrib import admin
from apps.users.models import UserProfile, PendingRegistration


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "updated_at"]
    search_fields = ["user__username", "user__first_name", "user__last_name"]
    list_filter = ["created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(PendingRegistration)
class PendingRegistrationAdmin(admin.ModelAdmin):
    list_display = ["email", "verification_code", "created_at", "expires_at", "is_expired"]
    search_fields = ["email", "verification_code"]
    list_filter = ["created_at", "expires_at"]
    readonly_fields = ["created_at", "password_hash"]
    actions = ['cleanup_expired']
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = "Expired?"
    
    def cleanup_expired(self, request, queryset):
        """Admin action to cleanup expired registrations"""
        count = PendingRegistration.cleanup_expired()
        self.message_user(request, f"{count} expired registration(s) deleted.")
    cleanup_expired.short_description = "Delete expired registrations"
