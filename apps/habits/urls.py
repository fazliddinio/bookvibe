from django.urls import path
from . import views

app_name = 'habits'

urlpatterns = [
    path('', views.ReadingHabitTrackerView.as_view(), name='tracker'),
    path('api/toggle/', views.toggle_reading_day, name='toggle_day'),
    path('api/update-details/', views.update_reading_details, name='update_details'),
]

