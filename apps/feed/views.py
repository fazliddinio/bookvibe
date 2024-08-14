from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
from .models import Activity
from apps.books.models import Book
from django.db.models import Count
from django.contrib.auth import get_user_model

User = get_user_model()


class FeedView(View):
    def get(self, request):
        # Get all activities ordered by creation time (LIFO - last in, first out)
        activities = Activity.objects.select_related('user', 'book', 'review').all()
        
        # Pagination
        paginator = Paginator(activities, 20)  # Show 20 activities per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get stats for the feed
        total_users = User.objects.filter(is_active=True).count()
        total_books = Book.objects.count()
        recent_reviews = Activity.objects.filter(activity_type='review').count()
        
        # Get trending books (most activities in last 7 days)
        from datetime import timedelta
        from django.utils import timezone
        
        week_ago = timezone.now() - timedelta(days=7)
        trending_books = (
            Book.objects.filter(activities__created_at__gte=week_ago)
            .annotate(activity_count=Count('activities'))
            .order_by('-activity_count')[:6]
        )
        
        return render(request, 'feed/home.html', {
            'page_obj': page_obj,
            'total_users': total_users,
            'total_books': total_books,
            'recent_reviews': recent_reviews,
            'trending_books': trending_books,
        })

