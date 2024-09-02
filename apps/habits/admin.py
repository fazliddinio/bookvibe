from django.contrib import admin
from .models import ReadingHabit, UserInterest


@admin.register(ReadingHabit)
class ReadingHabitAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'pages_read', 'minutes_read', 'completed']
    list_filter = ['completed', 'date']
    search_fields = ['user__username']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserInterest)
class UserInterestAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']

