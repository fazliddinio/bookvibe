from django.contrib import admin
from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'book', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__username', 'book__title', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']

