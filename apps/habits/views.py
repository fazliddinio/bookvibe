from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
from .models import ReadingHabit
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import calendar


class ReadingHabitTrackerView(View):
    def get(self, request):
        today = date.today()
        
        # If user is not authenticated, show empty page with login prompt
        if not request.user.is_authenticated:
            return render(request, 'habits/tracker.html', {
                'today_habit': None,
                'total_days': 0,
                'current_streak': 0,
                'total_pages': 0,
                'total_minutes': 0,
                'heatmap_data': json.dumps({}),
                'today': today,
                'require_login': True,
            })
        
        # Get or create today's habit
        habit, created = ReadingHabit.objects.get_or_create(
            user=request.user,
            date=today
        )
        
        # Get last 365 days of habits for the heatmap
        year_ago = today - timedelta(days=365)
        habits = ReadingHabit.objects.filter(
            user=request.user,
            date__gte=year_ago
        ).order_by('date')
        
        # Calculate stats
        total_days = habits.filter(completed=True).count()
        current_streak = self.calculate_streak(request.user)
        total_pages = habits.aggregate(total=models.Sum('pages_read'))['total'] or 0
        total_minutes = habits.aggregate(total=models.Sum('minutes_read'))['total'] or 0
        
        # Prepare heatmap data
        heatmap_data = {}
        for habit in habits:
            heatmap_data[str(habit.date)] = {
                'completed': habit.completed,
                'pages': habit.pages_read,
                'minutes': habit.minutes_read
            }
        
        return render(request, 'habits/tracker.html', {
            'today_habit': habit,
            'total_days': total_days,
            'current_streak': current_streak,
            'total_pages': total_pages,
            'total_minutes': total_minutes,
            'heatmap_data': json.dumps(heatmap_data),
            'today': today,
            'require_login': False,
        })
    
    def post(self, request):
        today = date.today()
        habit, created = ReadingHabit.objects.get_or_create(
            user=request.user,
            date=today
        )
        
        # Toggle completion status
        habit.completed = not habit.completed
        habit.save()
        
        messages.success(request, 'O\'qish faoliyatingiz yangilandi!')
        return redirect('habits:tracker')
    
    def calculate_streak(self, user):
        """Calculate the current streak of consecutive reading days"""
        today = date.today()
        streak = 0
        current_date = today
        
        while True:
            try:
                habit = ReadingHabit.objects.get(user=user, date=current_date)
                if habit.completed:
                    streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break
            except ReadingHabit.DoesNotExist:
                break
        
        return streak


@login_required
def toggle_reading_day(request):
    """API endpoint to toggle reading completion for a specific day"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        date_str = data.get('date')
        
        if not date_str:
            return JsonResponse({'success': False, 'error': 'Sana talab qilinadi'}, status=400)
        
        habit_date = date.fromisoformat(date_str)
        
        # Check if date is in the future
        if habit_date > date.today():
            return JsonResponse({'success': False, 'error': 'Kelajak kunlarini belgilab bo\'lmaydi'}, status=400)
        
        habit, created = ReadingHabit.objects.get_or_create(
            user=request.user,
            date=habit_date
        )
        
        # Toggle completion status
        habit.completed = not habit.completed
        habit.save()
        
        return JsonResponse({
            'success': True,
            'completed': habit.completed,
            'date': str(habit.date),
            'pages': habit.pages_read,
            'minutes': habit.minutes_read
        })
    except ValueError as e:
        return JsonResponse({'success': False, 'error': 'Noto\'g\'ri sana formati'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Xatolik: {str(e)}'}, status=500)


@login_required
def update_reading_details(request):
    """API endpoint to update reading details (pages/minutes) for a specific day"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        date_str = data.get('date')
        pages = data.get('pages', 0)
        minutes = data.get('minutes', 0)
        
        if not date_str:
            return JsonResponse({'success': False, 'error': 'Sana talab qilinadi'}, status=400)
        
        habit_date = date.fromisoformat(date_str)
        
        habit, created = ReadingHabit.objects.get_or_create(
            user=request.user,
            date=habit_date
        )
        
        # Update pages and minutes
        habit.pages_read = int(pages) if pages else 0
        habit.minutes_read = int(minutes) if minutes else 0
        
        # Automatically mark as completed if pages or minutes > 0
        if habit.pages_read > 0 or habit.minutes_read > 0:
            habit.completed = True
        
        habit.save()
        
        return JsonResponse({
            'success': True,
            'completed': habit.completed,
            'pages': habit.pages_read,
            'minutes': habit.minutes_read,
            'date': str(habit.date)
        })
    except ValueError as e:
        return JsonResponse({'success': False, 'error': 'Noto\'g\'ri ma\'lumot formati'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Xatolik: {str(e)}'}, status=500)


from django.db import models

