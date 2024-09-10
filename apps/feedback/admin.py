from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = [
        "get_sender",
        "feedback_type",
        "get_short_message",
        "created_at",
        "is_read",
        "is_responded",
    ]
    list_filter = ["feedback_type", "is_read", "is_responded", "created_at"]
    search_fields = ["name", "email", "message", "user__username"]
    readonly_fields = ["created_at"]
    list_editable = ["is_read", "is_responded"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Sender Information", {"fields": ("name", "email", "user")}),
        ("Feedback Content", {"fields": ("feedback_type", "message")}),
        (
            "Status",
            {
                "fields": ("is_read", "is_responded", "created_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_sender(self, obj):
        if obj.user:
            return f"{obj.user.username} (User)"
        elif obj.name:
            return f"{obj.name} (Guest)"
        else:
            return "Anonymous"

    get_sender.short_description = "Sender"

    def get_short_message(self, obj):
        return obj.get_short_message()

    get_short_message.short_description = "Message"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")
